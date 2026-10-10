"""SSSS causal signal timing, capital policy, cost guard, and repaint ledger."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.execution import M3Executor
from storage import StateStore
from strategy.registry import (
    STRATEGY_SSSS, StrategyDecision, StrategyStep, decide_ssss,
)
from test_multistrategy_ssss import FakeAdapter, fake_bar


class CausalSignalRules(unittest.TestCase):
    @patch("strategy.registry.ssss_strategy.evaluate_ssss")
    def test_old_repainted_buy_and_exit_are_never_actionable(self, mocked):
        for old_buy, old_exit in ((True, False), (False, True)):
            mocked.return_value = [
                fake_bar(buy=old_buy, exit_=old_exit, open_time=1800000000000),
                fake_bar(open_time=1800000900000),
            ]
            decision = decide_ssss([], {"current_fraction": .5}, "15m")
            self.assertEqual(decision.signal, "HOLD")
            self.assertEqual(decision.steps, ())
            self.assertEqual(decision.metadata["late_event_count"], 1)
            self.assertEqual(decision.metadata["new_buy_count"], 0)
            self.assertEqual(decision.metadata["new_exit_count"], 0)
            self.assertEqual(decision.bar_open_time, 1800000900000)

    @patch("strategy.registry.ssss_strategy.evaluate_ssss")
    def test_b_after_first_s_preserves_second_sell_stage(self, mocked):
        mocked.return_value = [fake_bar(buy=True)]
        decision = decide_ssss([], {
            "current_fraction": .25, "strategy_state": {"sell_stage": 1},
        }, "15m")
        self.assertEqual(decision.steps[0].code, "SSSS_BUY_25")
        self.assertAlmostEqual(decision.steps[0].target_fraction, .50)
        self.assertEqual(decision.steps[0].state_after["sell_stage"], 1)
        mocked.return_value = [fake_bar(exit_=True)]
        decision = decide_ssss([], {
            "current_fraction": .50, "strategy_state": {"sell_stage": 1},
            "position_entry_price": 90,
        }, "15m")
        self.assertEqual(decision.steps[0].code, "SSSS_EXIT_ALL")
        self.assertEqual(decision.steps[0].target_fraction, 0)
        self.assertEqual(decision.steps[0].state_after["sell_stage"], 0)

    @patch("strategy.registry.ssss_strategy.evaluate_ssss")
    def test_below_average_cost_and_missing_cost_never_advance_stage(self, mocked):
        mocked.return_value = [fake_bar(exit_=True)]
        for entry in (100, 105, None):
            result = decide_ssss([], {
                "current_fraction": .5,
                "strategy_state": {"sell_stage": 1},
                "position_entry_price": entry,
            }, "15m")
            self.assertFalse(result.steps)
            self.assertEqual(result.state_after["sell_stage"], 1)
            self.assertEqual(
                result.signal,
                "SSSS_EXIT_COST_UNAVAILABLE" if entry is None
                else "SSSS_EXIT_BELOW_COST",
            )


class CostSafeExecution(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.folder.name) / "positions.db")
        self.store.seed(("BTCUSDT",), 2, 1000, "15m")
        self.store.set_symbol_strategy("BTCUSDT", STRATEGY_SSSS, "15m")
        self.store.set_symbol_enabled("BTCUSDT", True)
        self.store.set_strategy_execution_state(
            "BTCUSDT", current_fraction=.50, strategy_state={"sell_stage": 0},
        )
        self.adapter = FakeAdapter()
        self.adapter.position = Decimal("1.000")
        self.adapter.avg_entry = 95
        self.executor = M3Executor(self.store)

    def tearDown(self):
        self.folder.cleanup()

    def test_gap_down_at_next_open_skips_first_s_and_keeps_stage(self):
        decision = StrategyDecision(
            strategy_id=STRATEGY_SSSS,
            signal="SSSS_EXIT_15",
            steps=(StrategyStep(
                code="SSSS_SELL_75", order_code="S75",
                target_fraction=.125, rule_ids=("DRAWICON_15",),
                state_after={"sell_stage": 1},
            ),),
            bar_open_time=1800000000000,
            metadata={"signal_close": 105},
        )
        with patch.object(self.executor, "refresh_accounting"):
            outcome = self.executor.execute(
                "BTCUSDT", decision,
                self.store.get_symbol_configs()["BTCUSDT"],
                self.store.get_runtime_states()["BTCUSDT"],
                self.adapter,
                {
                    "signal_bar_open_time": decision.bar_open_time,
                    "execution_bar_open_time": 1800000900000,
                    "reference_price": 94, "timeframe": "15m",
                },
            )
        self.assertEqual(outcome.actions, ())
        self.assertEqual(self.adapter.submits, 0)
        self.assertEqual(self.store.get_runtime_states()["BTCUSDT"]["strategy_state"]["sell_stage"], 0)
        self.assertAlmostEqual(
            self.store.get_runtime_states()["BTCUSDT"]["current_fraction"], .5,
        )


class RecordedRepaintLedger(unittest.TestCase):
    def test_first_detection_is_persisted_and_retrievable_for_chart(self):
        with tempfile.TemporaryDirectory() as folder:
            store = StateStore(Path(folder) / "events.db")
            store.seed(("BTCUSDT",), 1, 1000, "15m")
            signal_time = 1800000000000
            store.record_ssss_signal_detection(
                "BTCUSDT", timeframe="15m",
                signal_bar_open_time=signal_time, icon_id=9,
                detection_bar_open_time=signal_time + 2 * 900000,
                status="LATE_REPAINT_IGNORED",
            )
            store.record_ssss_signal_detection(
                "BTCUSDT", timeframe="15m",
                signal_bar_open_time=signal_time + 900000, icon_id=15,
                detection_bar_open_time=signal_time + 900000,
            )
            store.mark_ssss_signal_result(
                "BTCUSDT", timeframe="15m", signal_bar_open_time=signal_time + 900000,
                icon_id=15, status="SKIPPED_BELOW_COST",
            )
            visible = store.chart_ssss_signal_events(
                "BTCUSDT", timeframe="15m",
                first_open_time=signal_time, last_open_time=signal_time + 900000,
            )
            self.assertEqual(len(visible), 2)
            self.assertEqual(
                [v["status"] for v in visible],
                ["LATE_REPAINT_IGNORED", "SKIPPED_BELOW_COST"],
            )
            src = (Path(__file__).parents[1] / "templates/index.html").read_text(encoding="utf-8")
            self.assertIn("SSSS_RECORDED_BUY_9", src)
            self.assertIn("记录💰", src)


if __name__ == "__main__":
    unittest.main()
