from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from engine.recovery import M4Recovery
from exchange.binance_usdm_testnet import SymbolRules
from storage import StateStore


class FakeAdapter:
    def __init__(self):
        self.position = Decimal("0")
        self.remote_orders = {}
        self.open = []
        self.canceled = []

    def position_amount(self, symbol): return float(self.position)
    def symbol_rules(self, symbol):
        return SymbolRules(symbol, "TRADING", "PERPETUAL", "USDT", Decimal("0.1"), Decimal("0.001"), Decimal("0.001"), Decimal("1000"), Decimal("5"))
    def klines(self, symbol, timeframe, limit=2):
        return [[1000,100,101,99,100,10],[2000,101,102,100,101,11],[3000,102,103,101,102,12]][-limit:]
    def query_order(self, symbol, *, client_order_id=None, order_id=None):
        if client_order_id in self.remote_orders: return self.remote_orders[client_order_id]
        raise RuntimeError("-2013 Order does not exist")
    def open_orders(self, symbol=None): return list(self.open)
    def cancel_order(self, symbol, *, order_id=None, client_order_id=None):
        self.canceled.append(order_id if order_id is not None else client_order_id)
        self.open = [x for x in self.open if x.get("orderId") != order_id and x.get("clientOrderId") != client_order_id]
        return {"status":"CANCELED"}
    def submit_market_sell_reduce_only(self, symbol, *, quantity, client_order_id):
        self.position -= quantity
        return {"symbol":symbol,"orderId":9001,"clientOrderId":client_order_id,"status":"FILLED","executedQty":str(quantity),"avgPrice":"100"}


class M4RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.tmp.name) / "state.db")
        self.store.seed(("BTCUSDT",), 2, 100, "1d")
        self.store.set_symbol_enabled("BTCUSDT", True)
        self.recovery = M4Recovery(self.store)

    def tearDown(self):
        self.tmp.cleanup()

    def add_filled(self, cid, side, qty, oid="1"):
        self.store.begin_order("BTCUSDT", cid, side=side, quantity=qty, price=100)
        self.store.complete_order("BTCUSDT", cid, binance_order_id=oid, status="FILLED", quantity=qty, price=100)

    def test_matching_position_recovers_and_rebaselines(self):
        self.add_filled("5sv1-BTC-111-B60", "BUY", 1.2)
        a = FakeAdapter(); a.position = Decimal("1.2")
        result = self.recovery.reconcile_all(a, ("BTCUSDT",))
        self.assertEqual(result["status"], "PASS")
        rt = self.store.get_runtime_states()["BTCUSDT"]
        self.assertAlmostEqual(float(rt["current_fraction"]), 0.6)
        self.assertEqual(int(rt["entry_signal_open_time"]), 111)
        self.assertEqual(int(rt["last_closed_bar_open_time"]), 2000)
        self.assertEqual(rt["run_state"], "MONITORING")

    def test_crash_pending_order_is_recovered_from_binance(self):
        cid = "5sv1-BTC-222-B60"
        self.store.begin_order("BTCUSDT", cid, side="BUY", quantity=1.2, price=100)
        a = FakeAdapter(); a.position = Decimal("1.2")
        a.remote_orders[cid] = {"orderId":12,"status":"FILLED","executedQty":"1.2","avgPrice":"100"}
        result = self.recovery.reconcile_all(a, ("BTCUSDT",))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(self.store.get_order("BTCUSDT", cid)["status"], "FILLED")
        self.assertAlmostEqual(float(self.store.get_runtime_states()["BTCUSDT"]["current_fraction"]), 0.6)

    def test_position_mismatch_blocks_automatic_trading(self):
        self.add_filled("5sv1-BTC-111-B60", "BUY", 1.2)
        a = FakeAdapter(); a.position = Decimal("0.7")
        result = self.recovery.reconcile_all(a, ("BTCUSDT",))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(self.store.get_runtime_states()["BTCUSDT"]["run_state"], "RECOVERY_BLOCKED")

    def test_flat_remote_position_reanchors_stale_terminal_ledger(self):
        self.add_filled("5sv1-BTC-444-EMG", "SELL", 0.0029)
        a = FakeAdapter()

        result = self.recovery.reconcile_all(a, ("BTCUSDT",))

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["symbols"]["BTCUSDT"]["ledger_position"], 0.0)
        self.assertEqual(
            self.store.get_reconciliation_baseline("BTCUSDT", "5s_crypto_v1"),
            Decimal("-0.0029"),
        )
        audit = self.store.recent_audit("BTCUSDT", event_types=("M4_AUTO_BASELINE",))
        self.assertEqual(len(audit), 1)

    def test_external_open_order_blocks_without_canceling_it(self):
        a = FakeAdapter()
        a.open = [{"orderId":55,"clientOrderId":"manual-order","status":"NEW"}]
        result = self.recovery.reconcile_all(a, ("BTCUSDT",))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(a.canceled, [])

    def test_strategy_open_order_is_canceled_during_recovery(self):
        a = FakeAdapter()
        a.open = [{"orderId":56,"clientOrderId":"5sv1-BTC-333-B60","status":"NEW"}]
        result = self.recovery.reconcile_all(a, ("BTCUSDT",))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(a.canceled, [56])

    def test_emergency_flatten_stops_symbol_and_closes_demo_position(self):
        self.add_filled("5sv1-BTC-111-B60", "BUY", 1.2)
        a = FakeAdapter(); a.position = Decimal("1.2")
        out = self.recovery.emergency_flatten(a, "BTCUSDT")
        self.assertEqual(out["status"], "FILLED")
        self.assertEqual(a.position, Decimal("0.000"))
        cfg = self.store.get_symbol_configs()["BTCUSDT"]
        rt = self.store.get_runtime_states()["BTCUSDT"]
        self.assertFalse(cfg["enabled"])
        self.assertEqual(float(rt["current_fraction"]), 0.0)
        self.assertEqual(rt["run_state"], "STOPPED")


if __name__ == "__main__":
    unittest.main()
