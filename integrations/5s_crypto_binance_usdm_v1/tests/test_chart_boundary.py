import inspect
import unittest

from charting import DISPLAY_KLINE_LIMIT, normalize_chart_klines
from engine.scheduler import StrategyScheduler


class ChartBoundaryTests(unittest.TestCase):
    def test_display_uses_1000_bars_without_changing_strategy_fetch_window(self):
        self.assertEqual(DISPLAY_KLINE_LIMIT, 1000)
        default = inspect.signature(StrategyScheduler.__init__).parameters["fetch_limit"].default
        self.assertEqual(default, 220)
        self.assertNotEqual(DISPLAY_KLINE_LIMIT, default)

    def test_chart_normalizer_keeps_latest_1000_only(self):
        rows = [[i, 1, 2, 0.5, 1.5, 10] for i in range(1200)]
        out = normalize_chart_klines(rows)
        self.assertEqual(len(out), 1000)
        self.assertEqual(out[0]["open_time"], 200)
        self.assertEqual(out[-1]["open_time"], 1199)


if __name__ == "__main__":
    unittest.main()
