import unittest

from strategy.frozen_signal_engine import normalize_candles, evaluate_candles


class FrozenSignalEngineTests(unittest.TestCase):
    def test_normalize_sorts_by_open_time(self):
        rows = [
            [2, "2", "3", "1", "2.5", "20"],
            [1, "1", "2", "0.5", "1.5", "10"],
        ]
        out = normalize_candles(rows)
        self.assertEqual([x.open_time for x in out], [1, 2])

    def test_short_history_is_safe_and_has_no_signals(self):
        rows = [
            [i, 100 + i, 101 + i, 99 + i, 100.5 + i, 1000 + i]
            for i in range(5)
        ]
        out = evaluate_candles(rows)
        self.assertEqual(len(out), 5)
        self.assertTrue(all(not x.buy_onsets and not x.sell_onsets for x in out))


if __name__ == "__main__":
    unittest.main()
