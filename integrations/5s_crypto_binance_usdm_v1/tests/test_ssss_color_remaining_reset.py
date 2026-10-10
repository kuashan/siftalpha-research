"""SSSS color-filtered entry policy and resettable two-stage cost-aware exits.

These tests use synthetic closed candles and never change the original
SSSS.ftindex formula or ZBGE/5s signals.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
import tempfile
from unittest.mock import patch
from engine.execution import M3Executor
from storage import StateStore
from strategy.registry import StrategyDecision, StrategyStep
from test_multistrategy_ssss import FakeAdapter
from pathlib import Path
from unittest.mock import patch
import unittest

from strategy.registry import decide_ssss, STRATEGY_SSSS
from strategy.ssss_strategy import SSSSAnalysis, band_state
from test_multistrategy_ssss import fake_bar


def bar(t: int, *, color: str = "BLUE", buy: bool = False,
        exit_: bool = False):
    values = dict(fake_bar().values)
    values.update({
        "GZB12": 1.0 if color == "BLUE" else 0.0,
        "GZB13": 1.0 if color == "GREEN" else 0.0,
        "GZB14": 1.0 if color == "GRAY" else 0.0,
    })
    return replace(fake_bar(buy=buy, exit_=exit_, open_time=t), values=values)


def decision(bars, fraction=0.0, stage=0, cost=None):
    runtime = {
        "current_fraction": fraction,
        "strategy_state": {"sell_stage": stage},
    }
    if cost is not None:
        runtime["position_entry_price"] = cost
    with patch("strategy.registry.ssss_strategy.evaluate_ssss", return_value=bars):
        return decide_ssss([], runtime, "15m")


class ColorFilterTests(unittest.TestCase):
    def test_original_state_mapping_blue_green_gray(self):
        self.assertEqual(band_state(bar(1,color="BLUE").values), "BLUE")
        self.assertEqual(band_state(bar(1,color="GREEN").values), "GREEN")
        self.assertEqual(band_state(bar(1,color="GRAY").values), "GRAY")
        analysis = SSSSAnalysis((
            bar(1,color="BLUE"),
            bar(2,color="GREEN"),
            bar(3,color="GRAY"),
        ))
        self.assertEqual(
            [r["state"] for r in analysis.overlay()],
            ["BLUE", "GREEN", "GRAY"],
        )

    def test_blue_band_buy_allowed(self):
        d = decision([bar(1000,color="BLUE",buy=True)])
        self.assertEqual(d.signal, "SSSS_BUY_9")
        self.assertAlmostEqual(d.steps[0].target_fraction, .25)

    def test_green_band_buy_prohibited_but_original_icon_remains(self):
        d = decision([bar(1000,color="GREEN",buy=True)])
        self.assertEqual(d.signal, "SSSS_BUY_COLOR_BLOCKED")
        self.assertEqual(d.steps, ())
        self.assertTrue(d.metadata["buy_icon_9"])
        self.assertEqual(d.metadata["new_buy_count"], 1)
        self.assertFalse(d.metadata["buy_color_allowed"])

    def test_gray_after_blue_or_green(self):
        def d(color):
            bars = [
                bar(1000,color=color),
                bar(2000,color="GRAY"),
                bar(3000,color="GRAY",buy=True),
            ]
            return decision(bars)
        blue = d("BLUE")
        green = d("GREEN")
        self.assertEqual(blue.signal, "SSSS_BUY_COLOR_BLOCKED")
        self.assertFalse(blue.steps)
        self.assertEqual(blue.metadata["preceding_non_gray_band"], "BLUE")
        self.assertEqual(green.signal, "SSSS_BUY_9")
        self.assertEqual(green.metadata["preceding_non_gray_band"], "GREEN")
        self.assertAlmostEqual(green.steps[0].target_fraction, .25)

    def test_gray_with_no_known_previous_color_cannot_buy(self):
        d = decision([bar(1000,color="GRAY",buy=True)])
        self.assertFalse(d.steps)
        self.assertEqual(d.signal, "SSSS_BUY_COLOR_BLOCKED")

    def test_sells_allowed_in_all_three_bands(self):
        for color in ("BLUE","GREEN","GRAY"):
            with self.subTest(color=color):
                d = decision([bar(1000,color=color,exit_=True)],
                             fraction=.8,cost=95)
                self.assertEqual(d.steps[0].code, "SSSS_SELL_75")
                self.assertAlmostEqual(d.steps[0].target_fraction, .2)


class CapitalAndResetTests(unittest.TestCase):
    def test_first_buy_initial_then_quarter_of_remaining(self):
        cases=[(0.0,.25),(.25,.4375),(.4375,.578125),(.75,.8125),(.99,.9925)]
        for before,expected in cases:
            with self.subTest(before=before):
                d = decision([bar(1000,buy=True)],fraction=before)
                self.assertEqual(d.signal,"SSSS_BUY_9")
                self.assertAlmostEqual(d.steps[0].target_fraction,expected)
                self.assertEqual(d.steps[0].state_after["sell_stage"],0)
        self.assertFalse(decision([bar(1000,buy=True)],fraction=1.0).steps)

    def test_after_first_sell_new_successful_buy_uses_initial_25_and_resets_stage(self):
        d=decision([bar(1000,buy=True)],fraction=.125,stage=1)
        self.assertAlmostEqual(d.steps[0].target_fraction,.375)
        self.assertEqual(d.steps[0].state_after["sell_stage"],0)
        after_buy=decision([bar(2000,exit_=True)],fraction=.375,stage=0,cost=90)
        self.assertEqual(after_buy.steps[0].code,"SSSS_SELL_75")
        self.assertAlmostEqual(after_buy.steps[0].target_fraction,.09375)

    def test_without_intervening_buy_next_sell_clears_all(self):
        d=decision([bar(2000,exit_=True)],fraction=.125,stage=1,cost=90)
        self.assertEqual(d.steps[0].code,"SSSS_EXIT_ALL")
        self.assertEqual(d.steps[0].target_fraction,0)

    def test_blocked_rebuy_does_not_reset_sell_stage(self):
        d=decision([bar(1000,color="GREEN",buy=True)],fraction=.125,stage=1)
        self.assertFalse(d.steps)
        self.assertEqual(d.state_after["sell_stage"],1)

    def test_full_initial_quarter_if_room_not_available_is_skipped(self):
        d=decision([bar(1000,buy=True)],fraction=.80,stage=1)
        self.assertEqual(d.signal,"SSSS_BUY_BUDGET_EXHAUSTED")
        self.assertEqual(d.steps, ())
        self.assertEqual(d.state_after["sell_stage"],1)

    def test_cost_guard_skips_without_advancing(self):
        for color in ("BLUE","GREEN","GRAY"):
            for stage in (0,1):
                d=decision([bar(1000,color=color,exit_=True)],
                           fraction=.5,stage=stage,cost=110)
                self.assertFalse(d.steps)
                self.assertEqual(d.signal,"SSSS_EXIT_BELOW_COST")
                self.assertEqual(d.state_after["sell_stage"],stage)

    def test_visual_changes_leave_user_formula_unchanged(self):
        source = (Path(__file__).parents[1] / "strategy/ssss_strategy.py").read_text(encoding="utf-8")
        ui = (Path(__file__).parents[1] / "templates/index.html").read_text(encoding="utf-8")
        self.assertIn("SSSS_SOURCE_SHA256", source)
        self.assertIn("GREEN:'#22b573'", ui)
        self.assertIn("蓝带或绿转灰允许买", ui)


class SSSSActualFillStateTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.folder.name) / "ssss-policy.sqlite")
        self.store.seed(("BTCUSDT",), 1, 1000, "15m")
        self.store.set_symbol_strategy("BTCUSDT", STRATEGY_SSSS, "15m")
        self.store.set_symbol_enabled("BTCUSDT", True)
        self.adapter = FakeAdapter()
        self.engine = M3Executor(self.store)

    def tearDown(self):
        self.folder.cleanup()

    def run_buy(self, target, existing_fraction, stage):
        self.store.set_strategy_execution_state(
            "BTCUSDT", current_fraction=existing_fraction,
            strategy_state={"sell_stage":stage, "tracker_timeframe":"15m"},
        )
        self.adapter.position = Decimal("0") if existing_fraction == 0 else Decimal("0.500")
        entry = StrategyDecision(
            strategy_id=STRATEGY_SSSS, signal="SSSS_BUY_9",
            bar_open_time=1700000000000,
            steps=(StrategyStep(
                code="SSSS_BUY_25", order_code="B25",
                target_fraction=target, rule_ids=("DRAWICON_9",),
                state_after={"sell_stage":0 if stage==1 else stage, "tracker_timeframe":"15m"},
            ),), metadata={"signal_close":100},
        )
        with patch.object(self.engine, "refresh_accounting"):
            result = self.engine.execute(
                "BTCUSDT", entry,
                self.store.get_symbol_configs()["BTCUSDT"],
                self.store.get_runtime_states()["BTCUSDT"],
                self.adapter,
                {
                    "signal_bar_open_time":1700000000000,
                    "execution_bar_open_time":1700000900000,
                    "reference_price":100, "timeframe":"15m",
                },
            )
        return result, self.store.get_runtime_states()["BTCUSDT"]

    def test_successful_post_first_s_buy_resets_stage(self):
        outcome,state=self.run_buy(.375,.125,1)
        self.assertEqual(outcome.actions,("SSSS_BUY_25",))
        self.assertAlmostEqual(state["current_fraction"],.375)
        self.assertEqual(state["strategy_state"]["sell_stage"],0)

    def test_dust_purchase_skips_without_resetting_sell_stage(self):
        outcome,state=self.run_buy(.999925,.9999,1)
        self.assertEqual(outcome.actions,())
        self.assertEqual(self.adapter.submits,0)
        self.assertAlmostEqual(state["current_fraction"],.9999)
        self.assertEqual(state["strategy_state"]["sell_stage"],1)

    def test_insufficient_free_margin_skips_without_b(self):
        self.adapter.available=10.0
        outcome,state=self.run_buy(.25,0.0,0)
        self.assertEqual(outcome.actions,())
        self.assertEqual(self.adapter.submits,0)
        self.assertAlmostEqual(state["current_fraction"],0)


if __name__ == "__main__":
    unittest.main()
