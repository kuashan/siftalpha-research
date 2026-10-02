from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from engine.scheduler import StrategyScheduler
from storage import StateStore


class GateSession:
    def credentials(self):
        return "k", "s"

    def recovery_ready(self, symbol=None):
        if symbol is None:
            return False
        return symbol == "BTCUSDT"


class GateAdapter:
    def __init__(self, **kwargs):
        pass


class PublicMarket:
    calls = []

    def klines(self, symbol, timeframe, limit):
        self.calls.append(symbol)
        rows = [[i,100,101,99,100,1000] for i in range(90)]
        rows.append([90,100,101,99,100,1000])
        return rows


class M4SchedulerGateTests(unittest.TestCase):
    def test_recovery_gate_is_per_symbol(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp) / "state.db")
            symbols = ("BTCUSDT", "ETHUSDT")
            store.seed(symbols, 1, 100, "1d")
            store.set_symbol_enabled("BTCUSDT", True)
            store.set_symbol_enabled("ETHUSDT", True)
            PublicMarket.calls = []

            scheduler = StrategyScheduler(
                store=store,
                session=GateSession(),
                symbols=symbols,
                allowed_timeframes=("1d",),
                adapter_factory=GateAdapter,
                market_data_provider=PublicMarket(),
                minimum_closed_bars=64,
            )
            result = scheduler.run_once()

            # Recovery gates execution only; public signal monitoring still reads
            # both symbols from the market-data layer.
            self.assertEqual(PublicMarket.calls, ["BTCUSDT", "ETHUSDT"])
            self.assertEqual(result["ETHUSDT"]["state"], "WAITING_RECONCILE")
            self.assertEqual(result["BTCUSDT"]["state"], "MONITORING")


if __name__ == "__main__":
    unittest.main()
