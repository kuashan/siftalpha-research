from __future__ import annotations

import unittest

from market_data import (
    BinancePublicMarketDataProvider,
    CN_A_SHARE,
    CRYPTO_24_7,
    MarketDataRouter,
    US_EQUITY,
)


class FakeProbe:
    def __init__(self, rows=None, error=None):
        self.rows = rows or []
        self.error = error
        self.calls = []

    def klines(self, symbol, timeframe, limit=300):
        self.calls.append((symbol, timeframe, limit))
        if self.error:
            raise self.error
        return list(self.rows)


class FakeProvider:
    def __init__(self, provider_id, rows=None, error=None):
        self.provider_id = provider_id
        self.provider_label_zh = provider_id
        self.profile = CRYPTO_24_7
        self.rows = rows or []
        self.error = error
        self.calls = []

    def klines(self, symbol, timeframe, limit=300):
        self.calls.append((symbol, timeframe, limit))
        if self.error:
            raise self.error
        return list(self.rows)

    def stream_url(self, symbol):
        return f"wss://example.invalid/{self.provider_id}/{symbol}"


class MarketDataBoundaryTests(unittest.TestCase):
    def test_market_profiles_are_separate_from_provider(self):
        self.assertTrue(CRYPTO_24_7.continuous)
        self.assertFalse(US_EQUITY.continuous)
        self.assertEqual(CN_A_SHARE.sessions, (("09:30", "11:30"), ("13:00", "15:00")))

    def test_binance_provider_wraps_public_probe_without_credentials(self):
        probe = FakeProbe([[1, 2, 3]])
        provider = BinancePublicMarketDataProvider(probe)
        self.assertEqual(provider.klines("BTCUSDT", "1h", 220), [[1, 2, 3]])
        self.assertEqual(probe.calls, [("BTCUSDT", "1h", 220)])
        self.assertIn("btcusdt@ticker", provider.stream_url("BTCUSDT"))

    def test_router_fails_over_by_refetching_whole_window(self):
        first = FakeProvider("P1", error=RuntimeError("down"))
        second = FakeProvider("P2", rows=[[10], [20], [30]])
        router = MarketDataRouter()
        router.register(first)
        router.register(second)

        result = router.fetch("CRYPTO", "BTCUSDT", "15m", limit=300)
        self.assertEqual(result.provider_id, "P2")
        self.assertEqual(result.rows, [[10], [20], [30]])
        self.assertEqual(first.calls, [("BTCUSDT", "15m", 300)])
        self.assertEqual(second.calls, [("BTCUSDT", "15m", 300)])
        self.assertIn("/P2/BTCUSDT", result.stream_url)


if __name__ == "__main__":
    unittest.main()
