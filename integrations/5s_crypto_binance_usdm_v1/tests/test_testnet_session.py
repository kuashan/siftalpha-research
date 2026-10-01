import unittest

from runtime_testnet_session import TestnetSession


class FakeAdapter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def balances(self):
        return [{"asset": "USDT", "balance": "10000.50", "availableBalance": "8765.25"}]

    def positions(self):
        return [
            {"symbol": "BTCUSDT", "positionAmt": "0.001"},
            {"symbol": "ETHUSDT", "positionAmt": "0"},
            {"symbol": "XRPUSDT", "positionAmt": "5"},
        ]

    def is_one_way(self):
        return True


class FailingAdapter(FakeAdapter):
    def balances(self):
        raise RuntimeError("invalid testnet credentials")


class TestnetSessionTests(unittest.TestCase):
    def session(self, factory=FakeAdapter):
        return TestnetSession(
            allowed_symbols=("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"),
            allowed_timeframes=("15m", "1h", "1d"),
            adapter_factory=factory,
        )

    def test_successful_connection_exposes_only_safe_status(self):
        s = self.session()
        snap = s.connect_and_test("abcdefgh12345678", "super-secret")
        self.assertEqual(snap.environment, "TESTNET")
        self.assertEqual(snap.usdt_balance, 10000.50)
        self.assertEqual(snap.usdt_available_balance, 8765.25)
        self.assertEqual(snap.nonzero_position_count, 1)
        self.assertTrue(snap.one_way)

        status = s.public_status()
        self.assertTrue(status["connected"])
        self.assertEqual(status["masked_api_key"], "abcd••••5678")
        self.assertNotIn("super-secret", repr(status))

    def test_failed_connection_does_not_retain_secret(self):
        s = self.session(FailingAdapter)
        with self.assertRaises(RuntimeError):
            s.connect_and_test("bad-key", "bad-secret")
        self.assertFalse(s.public_status()["credentials_present"])
        self.assertNotIn("bad-secret", repr(s.public_status()))

    def test_disconnect_clears_memory_credentials(self):
        s = self.session()
        s.connect_and_test("abcdefgh12345678", "secret")
        s.disconnect()
        status = s.public_status()
        self.assertFalse(status["connected"])
        self.assertFalse(status["credentials_present"])


if __name__ == "__main__":
    unittest.main()
