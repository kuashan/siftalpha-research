from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
import hashlib
import json
import math
import tempfile
import unittest

from engine.execution import M3Executor
from engine.scheduler import StrategyScheduler
from exchange.binance_usdm_testnet import SymbolRules
from storage import StateStore
from strategy.registry import (
    STRATEGY_5S,
    STRATEGY_SSSS,
    StrategyDecision,
    StrategyStep,
    decide_ssss,
    get_spec,
    strategy_ids,
    strategy_signal_label,
)
from strategy.ssss_strategy import (
    SSSSBar,
    SSSS_SOURCE_SHA256,
    evaluate_ssss,
    load_formula_source,
    source_sha256,
)


class FakeAdapter:
    def __init__(self):
        self.position = Decimal("0")
        self.available = 1000.0
        self.orders = {}
        self.submits = 0

    def ensure_one_way(self): return {"changed": False}
    def ensure_isolated(self, symbol): return {"changed": False}
    def max_allowed_leverage(self, symbol): return 20
    def set_leverage(self, symbol, leverage): return {"leverage": leverage}
    def available_usdt(self): return self.available

    def symbol_rules(self, symbol):
        return SymbolRules(
            symbol, "TRADING", "PERPETUAL", "USDT",
            Decimal("0.1"), Decimal("0.001"), Decimal("0.001"),
            Decimal("1000"), Decimal("5"),
        )

    def position_amount(self, symbol): return float(self.position)

    def submit_market_buy(self, symbol, *, quantity, client_order_id):
        self.submits += 1
        self.position += quantity
        row = {
            "symbol": symbol, "orderId": self.submits, "status": "FILLED",
            "executedQty": str(quantity), "avgPrice": "100",
        }
        self.orders[client_order_id] = row
        return row

    def submit_market_sell_reduce_only(self, symbol, *, quantity, client_order_id):
        self.submits += 1
        self.position = max(Decimal("0"), self.position - quantity)
        row = {
            "symbol": symbol, "orderId": self.submits, "status": "FILLED",
            "executedQty": str(quantity), "avgPrice": "100",
        }
        self.orders[client_order_id] = row
        return row

    def query_order(self, symbol, *, client_order_id=None, order_id=None):
        if client_order_id in self.orders:
            return self.orders[client_order_id]
        raise RuntimeError("-2013 Order does not exist")

    def positions(self, symbol=None):
        return [{
            "symbol": symbol or "BTCUSDT",
            "positionAmt": str(self.position),
            "unRealizedProfit": "0",
        }]

    def income_history(self, symbol, *, start_time=None, end_time=None, limit=1000):
        return []


def fake_bar(*, buy=False, exit_=False, open_time=1700000000000):
    return SSSSBar(
        open_time=open_time,
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.0,
        volume=1.0,
        values={
            "GZB3": 100.0, "GZB4": 99.0,
            "GZB10": 100.0, "GZB11": 99.0,
            "GZB12": 1.0, "GZB13": 0.0, "GZB14": 0.0,
            "ZK1": 101.0, "ZD1": 99.0, "BS": 102.0, "BD": 98.0,
        },
        buy_icon_9=buy,
        exit_icon_15=exit_,
    )


class SSSSFormulaTests(unittest.TestCase):
    def test_original_ftindex_bytes_are_locked_by_sha256(self):
        self.assertEqual(
            SSSS_SOURCE_SHA256,
            "25f8c56075c0021dd2d0567401d37def25d6a9b895f139b3a8a9abc376fecaa7",
        )
        self.assertEqual(source_sha256(), SSSS_SOURCE_SHA256)

    def test_original_four_drawicon_rules_are_read_from_ftindex(self):
        source = load_formula_source()
        expected = [
            "DRAWICON(GZB36=1,L,9);",
            "DRAWICON(GZB34=1,H,15);",
            "DRAWICON(GZB33=1 OR GZB37=1,L,9);",
            "DRAWICON(GZB35=1 OR GZB38=1,H,15);",
        ]
        for statement in expected:
            self.assertIn(statement, source)

    def test_original_formula_executes_on_synthetic_bars(self):
        rows = []
        base = 1700000000000
        for i in range(360):
            center = 100.0 + math.sin(i / 12.0) * 8.0 + math.sin(i / 37.0) * 5.0
            close = center + math.sin(i / 3.0) * 1.3
            open_ = center - math.cos(i / 5.0) * 0.8
            high = max(open_, close) + 1.5
            low = min(open_, close) - 1.5
            rows.append([base + i * 900000, open_, high, low, close, 1000 + i])
        result = evaluate_ssss(rows)
        self.assertEqual(len(result), len(rows))
        self.assertTrue(all("ZK1" in bar.values and "ZD1" in bar.values for bar in result[-20:]))

        from strategy.ssss_strategy import chart_overlay
        overlay = chart_overlay(rows)
        encoded = json.dumps(overlay, allow_nan=False)
        self.assertIn("null", encoded)


class SSSSTradingRuleTests(unittest.TestCase):
    def test_latest_signal_label_is_action_advice_only(self):
        self.assertEqual(strategy_signal_label(STRATEGY_SSSS, "SSSS_BUY_9"), "买入 25%")
        self.assertEqual(strategy_signal_label(STRATEGY_SSSS, "SSSS_EXIT_15"), "全部清仓")
        self.assertEqual(strategy_signal_label(STRATEGY_SSSS, "HOLD"), "观望")
        self.assertEqual(strategy_signal_label(STRATEGY_SSSS, None), "观望")
        self.assertNotIn("💰", strategy_signal_label(STRATEGY_SSSS, "SSSS_BUY_9"))
        self.assertNotIn("💥", strategy_signal_label(STRATEGY_SSSS, "SSSS_EXIT_15"))
        self.assertNotIn("图标", strategy_signal_label(STRATEGY_SSSS, "SSSS_EXIT_15"))

    def test_registered_strategies_are_only_5s_and_ssss(self):
        self.assertEqual(strategy_ids(), (STRATEGY_5S, STRATEGY_SSSS))
        spec = get_spec(STRATEGY_SSSS)
        self.assertEqual(spec.max_fraction, 1.0)
        self.assertEqual(spec.order_prefix, "ssss")
        self.assertEqual(
            spec.supported_timeframes,
            ("3m", "5m", "15m", "1h", "2h", "4h", "6h", "12h", "1d"),
        )

    @patch("strategy.registry.ssss_strategy.evaluate_ssss")
    def test_money_icon_adds_exactly_25_percentage_points(self, mocked):
        mocked.return_value = [fake_bar(buy=True)]
        for current, target in [(0.0, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 1.0)]:
            decision = decide_ssss([], {"current_fraction": current}, "15m")
            self.assertEqual(decision.signal, "SSSS_BUY_9")
            self.assertEqual(len(decision.steps), 1)
            self.assertAlmostEqual(decision.steps[0].target_fraction, target)
            self.assertEqual(decision.steps[0].order_code, "B25")

    @patch("strategy.registry.ssss_strategy.evaluate_ssss")
    def test_money_icon_at_full_position_does_not_overbuy(self, mocked):
        mocked.return_value = [fake_bar(buy=True)]
        decision = decide_ssss([], {"current_fraction": 1.0}, "15m")
        self.assertEqual(decision.signal, "SSSS_BUY_9")
        self.assertEqual(decision.steps, ())

    @patch("strategy.registry.ssss_strategy.evaluate_ssss")
    def test_explosion_icon_full_exit_has_same_bar_priority(self, mocked):
        mocked.return_value = [fake_bar(buy=True, exit_=True)]
        decision = decide_ssss([], {"current_fraction": 0.75}, "15m")
        self.assertEqual(decision.signal, "SSSS_EXIT_15")
        self.assertEqual(len(decision.steps), 1)
        self.assertEqual(decision.steps[0].order_code, "X100")
        self.assertEqual(decision.steps[0].target_fraction, 0.0)


class SSSSExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.tmp.name) / "state.db")
        self.store.seed(("BTCUSDT",), 2, 100, "15m")
        self.store.set_symbol_strategy("BTCUSDT", STRATEGY_SSSS, "15m")
        self.store.set_symbol_enabled("BTCUSDT", True)
        self.adapter = FakeAdapter()
        self.executor = M3Executor(self.store, pnl_refresh_seconds=10)

    def tearDown(self):
        self.tmp.cleanup()

    def _execute(self, decision, execution_bar):
        self.executor.execute(
            "BTCUSDT",
            decision,
            self.store.get_symbol_configs()["BTCUSDT"],
            self.store.get_runtime_states()["BTCUSDT"],
            self.adapter,
            {
                "signal_bar_open_time": decision.bar_open_time,
                "execution_bar_open_time": execution_bar,
                "reference_price": 100.0,
                "timeframe": "15m",
            },
        )

    def test_filled_money_buy_and_explosion_exit_leave_b_and_x(self):
        buy = StrategyDecision(
            strategy_id=STRATEGY_SSSS,
            signal="SSSS_BUY_9",
            steps=(StrategyStep(
                code="SSSS_BUY_25",
                order_code="B25",
                target_fraction=0.25,
                rule_ids=("DRAWICON_9",),
                state_after={"last_icon": 9},
            ),),
            bar_open_time=1700000000000,
        )
        self._execute(buy, 1700000900000)

        self.assertEqual(self.adapter.position, Decimal("0.500"))
        runtime = self.store.get_runtime_states()["BTCUSDT"]
        self.assertAlmostEqual(float(runtime["current_fraction"]), 0.25)

        markers = self.store.list_trade_markers("BTCUSDT", STRATEGY_SSSS)
        self.assertEqual([m["side"] for m in markers], ["B"])
        self.assertEqual(markers[0]["open_time"], 1700000900000)

        exit_decision = StrategyDecision(
            strategy_id=STRATEGY_SSSS,
            signal="SSSS_EXIT_15",
            steps=(StrategyStep(
                code="SSSS_EXIT_ALL",
                order_code="X100",
                target_fraction=0.0,
                rule_ids=("DRAWICON_15",),
                state_after={},
            ),),
            bar_open_time=1700001800000,
        )
        self._execute(exit_decision, 1700002700000)

        self.assertEqual(self.adapter.position, Decimal("0"))
        runtime = self.store.get_runtime_states()["BTCUSDT"]
        self.assertAlmostEqual(float(runtime["current_fraction"]), 0.0)
        markers = self.store.list_trade_markers("BTCUSDT", STRATEGY_SSSS)
        self.assertEqual([m["side"] for m in markers], ["B", "X"])
        self.assertEqual(markers[-1]["open_time"], 1700002700000)

        orders = self.store.list_orders("BTCUSDT")
        self.assertTrue(all(x["strategy_id"] == STRATEGY_SSSS for x in orders))
        self.assertTrue(all(str(x["client_order_id"]).startswith("ssss-BTC-") for x in orders))
        self.assertTrue(all(str(x["status"]).upper() == "FILLED" for x in orders))



class _SchedulerSession:
    def credentials(self):
        return "demo-key", "demo-secret"

    def recovery_ready(self, symbol):
        return True


class _SchedulerAdapter(FakeAdapter):
    def __init__(self):
        super().__init__()
        self.generation = 0

    def klines(self, symbol, timeframe, limit):
        base = 1700000000000
        rows = []
        # 180 closed bars are enough for the SSSS registry minimum.
        for i in range(180 + self.generation):
            t = base + i * 900000
            rows.append([t, 100.0, 101.0, 99.0, 100.0, 1000.0])
        # Current open bar; scheduler excludes this from signal calculation and
        # uses its open as the execution reference.
        i = 180 + self.generation
        t = base + i * 900000
        rows.append([t, 100.0, 101.0, 99.0, 100.0, 1000.0])
        return rows


class SSSSEndToEndAutomationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.tmp.name) / "state.db")
        self.store.seed(("BTCUSDT",), 2, 100, "15m")
        self.store.set_symbol_strategy("BTCUSDT", STRATEGY_SSSS, "15m")
        self.store.set_symbol_enabled("BTCUSDT", True)
        self.adapter = _SchedulerAdapter()
        self.executor = M3Executor(self.store, pnl_refresh_seconds=10)
        self.scheduler = StrategyScheduler(
            store=self.store,
            session=_SchedulerSession(),
            symbols=("BTCUSDT",),
            allowed_timeframes=("15m",),
            adapter_factory=lambda **kwargs: self.adapter,
            minimum_closed_bars=64,
            on_decision=self.executor.execute,
        )

    def tearDown(self):
        self.tmp.cleanup()

    @patch("strategy.registry.ssss_strategy.evaluate_ssss")
    def test_money_signal_buys_and_explosion_signal_fully_exits(self, mocked):
        base = 1700000000000

        def evaluate(rows):
            latest = int(rows[-1][0])
            buy_time = base + 180 * 900000
            exit_time = base + 181 * 900000
            return [fake_bar(
                buy=latest == buy_time,
                exit_=latest == exit_time,
                open_time=latest,
            )]

        mocked.side_effect = evaluate

        # First poll establishes the baseline and must never replay old history.
        first = self.scheduler.run_once()
        self.assertEqual(first["BTCUSDT"]["state"], "MONITORING")
        self.assertEqual(self.adapter.submits, 0)

        # Next closed bar shows 💰: scheduler must reach the Binance adapter BUY.
        self.adapter.generation = 1
        second = self.scheduler.run_once()
        self.assertEqual(second["BTCUSDT"]["signal"], "SSSS_BUY_9")
        self.assertEqual(second["BTCUSDT"]["actions"], ["SSSS_BUY_25"])
        self.assertEqual(self.adapter.submits, 1)
        self.assertGreater(self.adapter.position, Decimal("0"))
        self.assertAlmostEqual(
            float(self.store.get_runtime_states()["BTCUSDT"]["current_fraction"]),
            0.25,
        )

        # Following closed bar shows 💥: scheduler must issue reduce-only full exit.
        self.adapter.generation = 2
        third = self.scheduler.run_once()
        self.assertEqual(third["BTCUSDT"]["signal"], "SSSS_EXIT_15")
        self.assertEqual(third["BTCUSDT"]["actions"], ["SSSS_EXIT_ALL"])
        self.assertEqual(self.adapter.submits, 2)
        self.assertEqual(self.adapter.position, Decimal("0"))
        self.assertAlmostEqual(
            float(self.store.get_runtime_states()["BTCUSDT"]["current_fraction"]),
            0.0,
        )

        orders = self.store.list_orders("BTCUSDT")
        self.assertEqual([str(x["status"]).upper() for x in orders], ["FILLED", "FILLED"])
        self.assertEqual([x["side"] for x in orders], ["BUY", "SELL"])
        markers = self.store.list_trade_markers("BTCUSDT", STRATEGY_SSSS)
        self.assertEqual([x["side"] for x in markers], ["B", "X"])



if __name__ == "__main__":
    unittest.main()
