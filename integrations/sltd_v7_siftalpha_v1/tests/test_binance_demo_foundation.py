from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from binance_demo_executor import DemoExecutor
from binance_demo_store import DemoStore
from data_provider import _market_id_for_symbol
from providers.binance_usdm import BinanceUsdMProvider


class BinanceDemoFoundationTests(unittest.TestCase):
    def test_crypto_routes_to_binance_market(self):
        self.assertEqual(_market_id_for_symbol("BTCUSDT"), "CRYPTO")
        self.assertEqual(_market_id_for_symbol("AAPL"), "US_EQUITY")

    def test_store_rejects_display_only_strategy(self):
        with tempfile.TemporaryDirectory() as td:
            store=DemoStore(Path(td)/"x.db")
            with self.assertRaises(ValueError):
                store.set_config("BTCUSDT",strategy_id="chan",timeframe="1h",leverage=1,budget=1000)

    def test_fraction_semantics_are_preserved(self):
        self.assertAlmostEqual(DemoExecutor._next_fraction("SLTD_BUY25",0.50),0.75)
        self.assertAlmostEqual(DemoExecutor._next_fraction("SLTD_SELL25_CURRENT",0.80),0.60)
        self.assertAlmostEqual(DemoExecutor._next_fraction("E_BUY50",0.25),0.75)
        self.assertAlmostEqual(DemoExecutor._next_fraction("E_SELL50PP",0.75),0.25)
        self.assertAlmostEqual(DemoExecutor._next_fraction("5S_BUY60",0.0),0.60)
        self.assertAlmostEqual(DemoExecutor._next_fraction("5S_HALF_EXIT",1.0),0.50)

    def test_client_id_is_bar_unique(self):
        a=DemoExecutor.client_id("BTCUSDT",1700000000,"SLTD_BUY25",0)
        b=DemoExecutor.client_id("BTCUSDT",1700000300,"SLTD_BUY25",0)
        self.assertNotEqual(a,b)
        self.assertLessEqual(len(a),36)

    def test_binance_provider_converts_milliseconds_to_seconds(self):
        row=[1700000000000,"1","2","0.5","1.5","10",1700000299999]
        out=BinanceUsdMProvider._normalize_row(row,complete=True)
        self.assertEqual(out["open_time"],1700000000)
        self.assertEqual(out["close_time"],1700000299)


if __name__=="__main__":
    unittest.main()
