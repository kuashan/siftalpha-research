from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from engine.execution import M3Executor
from exchange.binance_usdm_testnet import SymbolRules
from storage import StateStore
from strategy.registry import (
    STRATEGY_5S,
    STRATEGY_E,
    StrategyDecision,
    StrategyStep,
    get_spec,
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
        return [{"symbol": symbol or "BTCUSDT", "positionAmt": str(self.position), "unRealizedProfit": "0"}]
    def income_history(self, symbol, *, start_time=None, end_time=None, limit=1000):
        return []


class MultiStrategyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.tmp.name) / "state.db")
        self.store.seed(("BTCUSDT",), 2, 100, "1d")

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_is_frozen_5s(self):
        cfg = self.store.get_symbol_configs()["BTCUSDT"]
        self.assertEqual(cfg["strategy_id"], STRATEGY_5S)
        self.assertIn("1d", get_spec(STRATEGY_5S).supported_timeframes)

    def test_strategy_switch_resets_flat_runtime(self):
        self.store.set_execution_position_state(
            "BTCUSDT",
            current_fraction=0.0,
            c_confirmed=False,
            entry_signal_open_time=None,
            entry_family=None,
        )
        self.store.set_symbol_strategy("BTCUSDT", STRATEGY_E, "15m")
        cfg = self.store.get_symbol_configs()["BTCUSDT"]
        rt = self.store.get_runtime_states()["BTCUSDT"]
        self.assertEqual(cfg["strategy_id"], STRATEGY_E)
        self.assertEqual(cfg["timeframe"], "15m")
        self.assertFalse(cfg["enabled"])
        self.assertEqual(float(rt["current_fraction"]), 0.0)
        self.assertEqual(rt["strategy_state"], {})

    def test_e_buy_25_uses_generic_target_delta(self):
        self.store.set_symbol_strategy("BTCUSDT", STRATEGY_E, "15m")
        self.store.set_symbol_enabled("BTCUSDT", True)
        adapter = FakeAdapter()
        executor = M3Executor(self.store, pnl_refresh_seconds=10)
        decision = StrategyDecision(
            strategy_id=STRATEGY_E,
            signal="E_BUY_1",
            steps=(
                StrategyStep(
                    code="E_BUY",
                    order_code="B25",
                    target_fraction=0.25,
                    rule_ids=("E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1",),
                    state_after={"b1_used": True, "b2_used": False, "b3_used": False, "sell_stage": 0},
                ),
            ),
            bar_open_time=1700000000000,
        )
        executor.execute(
            "BTCUSDT",
            decision,
            self.store.get_symbol_configs()["BTCUSDT"],
            self.store.get_runtime_states()["BTCUSDT"],
            adapter,
            {
                "signal_bar_open_time": 1700000000000,
                "execution_bar_open_time": 1700000900000,
                "reference_price": 100.0,
                "timeframe": "15m",
            },
        )
        self.assertEqual(adapter.position, Decimal("0.500"))
        rt = self.store.get_runtime_states()["BTCUSDT"]
        self.assertAlmostEqual(float(rt["current_fraction"]), 0.25)
        self.assertTrue(rt["strategy_state"]["b1_used"])
        orders = self.store.list_orders("BTCUSDT")
        self.assertEqual(orders[-1]["strategy_id"], STRATEGY_E)
        self.assertAlmostEqual(float(orders[-1]["target_fraction_after"]), 0.25)
        self.assertTrue(str(orders[-1]["client_order_id"]).startswith("ev1-BTC-"))

    def test_e_sell_50pp_sells_proportional_actual_position(self):
        self.store.set_symbol_strategy("BTCUSDT", STRATEGY_E, "15m")
        self.store.set_symbol_enabled("BTCUSDT", True)
        self.store.set_strategy_execution_state(
            "BTCUSDT",
            current_fraction=0.75,
            strategy_state={"b1_used": True, "b2_used": True, "b3_used": True, "sell_stage": 0},
        )
        adapter = FakeAdapter()
        adapter.position = Decimal("1.500")
        executor = M3Executor(self.store, pnl_refresh_seconds=10)
        decision = StrategyDecision(
            strategy_id=STRATEGY_E,
            signal="E_SELL_1",
            steps=(
                StrategyStep(
                    code="E_SELL_50PP",
                    order_code="S50",
                    target_fraction=0.25,
                    rule_ids=("E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP",),
                    state_after={"b1_used": True, "b2_used": True, "b3_used": True, "sell_stage": 1},
                ),
            ),
            bar_open_time=1700000000000,
        )
        executor.execute(
            "BTCUSDT",
            decision,
            self.store.get_symbol_configs()["BTCUSDT"],
            self.store.get_runtime_states()["BTCUSDT"],
            adapter,
            {
                "signal_bar_open_time": 1700000000000,
                "execution_bar_open_time": 1700000900000,
                "reference_price": 100.0,
                "timeframe": "15m",
            },
        )
        self.assertEqual(adapter.position, Decimal("0.500"))
        rt = self.store.get_runtime_states()["BTCUSDT"]
        self.assertAlmostEqual(float(rt["current_fraction"]), 0.25)
        self.assertEqual(int(rt["strategy_state"]["sell_stage"]), 1)

    def test_e_timeframes_are_explicit_and_do_not_mutate_5s(self):
        self.assertEqual(
            get_spec(STRATEGY_E).supported_timeframes,
            ("5m", "15m", "1h", "4h"),
        )
        self.assertEqual(
            get_spec(STRATEGY_5S).supported_timeframes,
            ("3m", "5m", "15m", "1h", "2h", "4h", "6h", "12h", "1d"),
        )


if __name__ == "__main__":
    unittest.main()
