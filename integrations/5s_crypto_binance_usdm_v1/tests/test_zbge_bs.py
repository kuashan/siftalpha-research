from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import tempfile
import unittest

from engine.execution import M3Executor
from storage import StateStore
from strategy.registry import (
    STRATEGY_ZBGE, RETIRED_MFRA_ID, StrategyDecision, StrategyStep,
    decide, decide_zbge, get_spec, strategy_ids,
)
from strategy.zbge_strategy import ZBGEPoint, evaluate_zbge


def point(*, close=120, buy=False, sell_a=False, sell_b=False):
    return ZBGEPoint(
        open_time=1710000000000, close=close, trend=10 if buy else 90,
        absorption=30, yellow=buy, smile=sell_b, smile_count=3 if sell_b else 0,
        follow_main=sell_a, buy=buy, sell_a=sell_a, sell_b=sell_b,
    )


class ZBGERuleTests(unittest.TestCase):
    def test_replaces_pai_without_silently_enabling_old_configuration(self):
        self.assertIn(STRATEGY_ZBGE, strategy_ids())
        self.assertNotIn(RETIRED_MFRA_ID, strategy_ids())
        self.assertEqual(get_spec(STRATEGY_ZBGE).order_prefix, "zbge")
        with self.assertRaises(ValueError):
            decide(RETIRED_MFRA_ID, [], {}, "4h")

    @patch("strategy.registry.zbge_strategy.evaluate_zbge")
    def test_every_b_is_fixed_25pct_of_initial_budget(self, mock_eval):
        mock_eval.return_value = [point(buy=True)] * 180
        for before in (0, .25, .50, .75):
            result = decide_zbge([], {
                "current_fraction": before, "strategy_state": {"sell_stage": 1},
            }, "4h")
            self.assertEqual(len(result.steps), 1)
            self.assertAlmostEqual(result.steps[0].target_fraction - before, .25)
            self.assertEqual(result.steps[0].state_after["sell_stage"], 1)
        result = decide_zbge([], {"current_fraction": .80}, "4h")
        self.assertEqual(result.steps, ())  # no partial purchase <25%

    @patch("strategy.registry.zbge_strategy.evaluate_zbge")
    def test_first_sell_75pct_second_sell_all_even_after_rebuy(self, mock_eval):
        mock_eval.return_value = [point(close=105, sell_a=True)] * 180
        first = decide_zbge([], {
            "current_fraction": .80, "position_entry_price": 100,
            "strategy_state": {"sell_stage": 0},
        }, "4h")
        self.assertEqual(first.steps[0].code, "ZBGE_SELL_75")
        self.assertAlmostEqual(first.steps[0].target_fraction, .20)
        self.assertEqual(first.steps[0].state_after["sell_stage"], 1)

        mock_eval.return_value = [point(buy=True)] * 180
        rebuy = decide_zbge([], {
            "current_fraction": .20, "strategy_state": {"sell_stage": 1},
        }, "4h")
        self.assertAlmostEqual(rebuy.steps[0].target_fraction, .45)
        self.assertEqual(rebuy.steps[0].state_after["sell_stage"], 1)

        mock_eval.return_value = [point(close=106, sell_b=True)] * 180
        second = decide_zbge([], {
            "current_fraction": .45, "position_entry_price": 100,
            "strategy_state": {"sell_stage": 1},
        }, "4h")
        self.assertEqual(second.steps[0].code, "ZBGE_SELL_ALL")
        self.assertEqual(second.steps[0].target_fraction, 0)
        self.assertEqual(second.steps[0].state_after, {})

    @patch("strategy.registry.zbge_strategy.evaluate_zbge")
    def test_below_cost_s_skips_without_advancing_sell_stage(self, mock_eval):
        mock_eval.return_value = [point(close=98, sell_b=True)] * 180
        state = {"current_fraction": .5, "position_entry_price": 100,
                 "strategy_state": {"sell_stage": 1}}
        decision = decide_zbge([], state, "4h")
        self.assertEqual(decision.signal, "ZBGE_S_BELOW_COST")
        self.assertFalse(decision.steps)
        self.assertEqual(decision.state_after["sell_stage"], 1)
        state["position_entry_price"] = None
        self.assertEqual(decide_zbge([], state, "4h").signal,
                         "ZBGE_S_COST_UNAVAILABLE")

    def test_indicator_is_causal_prefix_stable_and_smiles_only_third(self):
        rows = []
        for i in range(250):
            c = 100 + i * .31 + (i % 17) * .27
            rows.append([1700000000000 + i * 14400000, c - .1, c + .5, c - .5, c, 1])
        points = evaluate_zbge(rows)
        self.assertEqual(len(points), len(rows))
        for j in (180, 220):
            self.assertEqual(evaluate_zbge(rows[:j]), points[:j])
        for i, item in enumerate(points):
            if item.sell_b:
                self.assertEqual(item.smile_count, 3)
                if i + 1 < len(points) and points[i + 1].smile:
                    self.assertFalse(points[i + 1].sell_b)


class FakePositionAdapter:
    def __init__(self):
        self.position = Decimal(".1000")
        self.avg = 100.0
        self.sells = 0

    def position_amount(self, symbol):
        return float(self.position)

    def position_metrics(self, symbol):
        return {"entry_price": self.avg}

    def query_order(self, *args, **kwargs):
        raise RuntimeError("-2013 Order does not exist")

    def symbol_rules(self, symbol):
        return SimpleNamespace(step_size=Decimal(".0001"))

    def submit_market_sell_reduce_only(self, symbol, *, quantity, client_order_id):
        self.sells += 1
        self.position -= quantity
        return {"orderId": self.sells, "status": "FILLED",
                "executedQty": str(quantity), "avgPrice": "105"}


class ZBGEExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.temp.name) / "db.sqlite")
        self.store.seed(("BTCUSDT",), 1, 10000, "4h")
        self.store.set_symbol_strategy("BTCUSDT", STRATEGY_ZBGE, "4h")
        self.store.set_symbol_enabled("BTCUSDT", True)
        self.store.set_strategy_execution_state(
            "BTCUSDT", current_fraction=.5, strategy_state={"sell_stage": 0},
        )
        self.executor = M3Executor(self.store)
        self.adapter = FakePositionAdapter()

    def tearDown(self):
        self.temp.cleanup()

    def execute(self, next_open):
        decision = StrategyDecision(
            strategy_id=STRATEGY_ZBGE, signal="ZBGE_SELL_A",
            steps=(StrategyStep(
                code="ZBGE_SELL_75", order_code="S75",
                target_fraction=.125,
                rule_ids=("FOLLOW_MAIN_TREND_GT75",),
                state_after={"sell_stage": 1},
            ),),
            bar_open_time=1700000000000,
            metadata={"signal_close": 105},
        )
        with patch.object(self.executor, "refresh_accounting"):
            return self.executor.execute(
                "BTCUSDT", decision,
                self.store.get_symbol_configs()["BTCUSDT"],
                self.store.get_runtime_states()["BTCUSDT"],
                self.adapter,
                {"signal_bar_open_time": decision.bar_open_time,
                 "execution_bar_open_time": 1700014400000,
                 "reference_price": next_open, "timeframe": "4h"},
            )

    def test_next_open_below_cost_skips_without_consume(self):
        outcome = self.execute(99)
        self.assertEqual(outcome.actions, ())
        self.assertEqual(self.adapter.sells, 0)
        runtime = self.store.get_runtime_states()["BTCUSDT"]
        self.assertAlmostEqual(runtime["current_fraction"], .5)
        self.assertEqual(runtime["strategy_state"]["sell_stage"], 0)

    def test_sell_above_cost_executes_and_increments_only_on_fill(self):
        outcome = self.execute(105)
        self.assertEqual(outcome.actions, ("ZBGE_SELL_75",))
        self.assertEqual(self.adapter.sells, 1)
        runtime = self.store.get_runtime_states()["BTCUSDT"]
        self.assertAlmostEqual(runtime["current_fraction"], .125)
        self.assertEqual(runtime["strategy_state"]["sell_stage"], 1)


if __name__ == "__main__":
    unittest.main()
