from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from engine.execution import ExecutionBlocked, M3Executor
from engine.scheduler import M3Decision
from exchange.binance_usdm_testnet import SymbolRules
from storage import StateStore


class FakeAdapter:
    def __init__(self, available=1000.0, max_leverage=20):
        self.available = available
        self.max_leverage_value = max_leverage
        self.position = Decimal("0")
        self.orders = {}
        self.submits = 0
        self.leverage = None

    def ensure_one_way(self): return {"changed": False}
    def ensure_isolated(self, symbol): return {"changed": False}
    def max_allowed_leverage(self, symbol): return self.max_leverage_value
    def set_leverage(self, symbol, leverage): self.leverage = leverage; return {"leverage": leverage}
    def available_usdt(self): return self.available
    def symbol_rules(self, symbol):
        return SymbolRules(symbol, "TRADING", "PERPETUAL", "USDT", Decimal("0.1"), Decimal("0.001"), Decimal("0.001"), Decimal("1000"), Decimal("5"))
    def position_amount(self, symbol): return float(self.position)
    def submit_market_buy(self, symbol, *, quantity, client_order_id):
        self.submits += 1; self.position += quantity
        o={"symbol":symbol,"orderId":1000+self.submits,"status":"FILLED","executedQty":str(quantity),"avgPrice":"100"}
        self.orders[client_order_id]=o; return o
    def submit_market_sell_reduce_only(self, symbol, *, quantity, client_order_id):
        self.submits += 1; self.position=max(Decimal("0"),self.position-quantity)
        o={"symbol":symbol,"orderId":1000+self.submits,"status":"FILLED","executedQty":str(quantity),"avgPrice":"100"}
        self.orders[client_order_id]=o; return o
    def query_order(self, symbol, *, client_order_id=None, order_id=None):
        if client_order_id in self.orders: return self.orders[client_order_id]
        raise RuntimeError("-2013 Order does not exist")
    def positions(self, symbol=None):
        return [{"symbol":symbol or "BTCUSDT","positionAmt":str(self.position),"unRealizedProfit":"3.5" if self.position else "0"}]
    def income_history(self, symbol, *, start_time=None, end_time=None, limit=1000):
        return [
            {"incomeType":"REALIZED_PNL","income":"2.0"},
            {"incomeType":"FUNDING_FEE","income":"-0.2"},
            {"incomeType":"COMMISSION","income":"-0.1"},
        ]


class M3ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=StateStore(Path(self.tmp.name)/"state.db")
        self.store.seed(("BTCUSDT",),2,100,"1d")
        self.store.set_symbol_config("BTCUSDT",capital_budget_usdt=100,leverage=2,timeframe="1d")
        self.store.set_symbol_enabled("BTCUSDT",True)
        self.executor=M3Executor(self.store,pnl_refresh_seconds=10)

    def tearDown(self): self.tmp.cleanup()
    def context(self): return {"signal_bar_open_time":1000,"execution_bar_open_time":2000,"reference_price":100.0,"timeframe":"1d"}
    def runtime(self): return self.store.get_runtime_states()["BTCUSDT"]

    def test_initial_buy_uses_60_percent_margin_budget(self):
        a=FakeAdapter(); d=M3Decision("BUY_A",("BUY_60",),bar_open_time=1000)
        self.executor.execute("BTCUSDT",d,self.store.get_symbol_configs()["BTCUSDT"],self.runtime(),a,self.context())
        self.assertEqual(a.position,Decimal("1.200"))
        self.assertEqual(a.leverage,2)
        rt=self.runtime(); self.assertAlmostEqual(float(rt["current_fraction"]),.6); self.assertEqual(rt["entry_family"],"A")

    def test_c_topup_adds_remaining_40_percent(self):
        a=FakeAdapter(); a.position=Decimal("1.200")
        self.store.set_execution_position_state("BTCUSDT",current_fraction=.6,c_confirmed=False,entry_signal_open_time=900,entry_family="A")
        d=M3Decision("BUY_C",("TOPUP_TO_100",),c_eligible=True,bar_open_time=1000)
        self.executor.execute("BTCUSDT",d,self.store.get_symbol_configs()["BTCUSDT"],self.runtime(),a,self.context())
        self.assertEqual(a.position,Decimal("2.000")); self.assertAlmostEqual(float(self.runtime()["current_fraction"]),1.0)

    def test_sell_closes_full_position(self):
        a=FakeAdapter(); a.position=Decimal("1.234")
        self.store.set_execution_position_state("BTCUSDT",current_fraction=1,c_confirmed=True,entry_signal_open_time=900,entry_family="B")
        d=M3Decision("SELL_C",("SELL_ALL",),bar_open_time=1000)
        self.executor.execute("BTCUSDT",d,self.store.get_symbol_configs()["BTCUSDT"],self.runtime(),a,self.context())
        self.assertEqual(a.position,Decimal("0.000")); self.assertEqual(float(self.runtime()["current_fraction"]),0)

    def test_insufficient_margin_blocks(self):
        a=FakeAdapter(available=20); d=M3Decision("BUY_A",("BUY_60",),bar_open_time=1000)
        with self.assertRaises(ExecutionBlocked):
            self.executor.execute("BTCUSDT",d,self.store.get_symbol_configs()["BTCUSDT"],self.runtime(),a,self.context())
        self.assertEqual(a.submits,0)

    def test_leverage_cap_blocks(self):
        self.store.set_symbol_config("BTCUSDT",capital_budget_usdt=100,leverage=10,timeframe="1d")
        a=FakeAdapter(max_leverage=5); d=M3Decision("BUY_A",("BUY_60",),bar_open_time=1000)
        with self.assertRaises(ExecutionBlocked):
            self.executor.execute("BTCUSDT",d,self.store.get_symbol_configs()["BTCUSDT"],self.runtime(),a,self.context())

    def test_pending_order_recovers_without_duplicate(self):
        a=FakeAdapter(); cid=self.executor._client_order_id("BTCUSDT",1000,"BUY_60")
        self.store.begin_order("BTCUSDT",cid,side="BUY",quantity=1.2,price=100)
        a.position=Decimal("1.200"); a.orders[cid]={"orderId":777,"status":"FILLED","executedQty":"1.2","avgPrice":"100"}
        d=M3Decision("BUY_A",("BUY_60",),bar_open_time=1000)
        self.executor.execute("BTCUSDT",d,self.store.get_symbol_configs()["BTCUSDT"],self.runtime(),a,self.context())
        self.assertEqual(a.submits,0); self.assertAlmostEqual(float(self.runtime()["current_fraction"]),.6)

    def test_accounting(self):
        a=FakeAdapter(); a.position=Decimal("1"); self.store.set_accounting_start_if_missing("BTCUSDT",1000)
        self.executor.refresh_accounting("BTCUSDT",a,force=True)
        p=self.store.get_pnl()["BTCUSDT"]
        self.assertAlmostEqual(p["realized_pnl"],2); self.assertAlmostEqual(p["unrealized_pnl"],3.5)
        self.assertAlmostEqual(p["funding_fee"],-.2); self.assertAlmostEqual(p["trading_fee"],.1); self.assertAlmostEqual(p["total_pnl"],5.2)


if __name__=="__main__": unittest.main()
