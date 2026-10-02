import unittest

from engine.paper import preview_exposure
from strategy.frozen_contract import FrozenCryptoV1Policy, Signal


class PolicyTests(unittest.TestCase):
    def test_frozen_crypto_policy(self):
        p = FrozenCryptoV1Policy()
        self.assertEqual(p.target_fraction(0, Signal.BUY_A), 0.60)
        self.assertEqual(p.target_fraction(0, Signal.BUY_B), 0.60)
        self.assertEqual(p.target_fraction(0.60, Signal.BUY_C, c_eligible=True), 1.0)
        self.assertEqual(p.target_fraction(0.60, Signal.BUY_C, c_eligible=False), 0.60)
        self.assertEqual(p.target_fraction(1.0, Signal.SELL_C), 0.0)
        self.assertEqual(p.target_fraction(1.0, Signal.SELL_A), 0.0)

    def test_futures_notional_preview(self):
        x = preview_exposure("BTCUSDT", 1000, 0.60, 5)
        self.assertEqual(x.margin_allocated_usdt, 600)
        self.assertEqual(x.target_notional_usdt, 3000)


if __name__ == "__main__":
    unittest.main()
