import inspect
import unittest

from charting import DISPLAY_KLINE_LIMIT, normalize_chart_klines
from engine.scheduler import StrategyScheduler
from signal_preview import SIGNAL_HISTORY_LIMIT


class ChartBoundaryTests(unittest.TestCase):
    def test_display_uses_300_bars_without_changing_strategy_fetch_window(self):
        self.assertEqual(DISPLAY_KLINE_LIMIT, 300)
        default = inspect.signature(StrategyScheduler.__init__).parameters["fetch_limit"].default
        self.assertEqual(default, 220)
        self.assertNotEqual(DISPLAY_KLINE_LIMIT, default)
        self.assertGreater(SIGNAL_HISTORY_LIMIT, DISPLAY_KLINE_LIMIT)

    def test_chart_normalizer_keeps_latest_300_only(self):
        rows = [[i, 1, 2, 0.5, 1.5, 10] for i in range(350)]
        out = normalize_chart_klines(rows)
        self.assertEqual(len(out), 300)
        self.assertEqual(out[0]["open_time"], 50)
        self.assertEqual(out[-1]["open_time"], 349)


if __name__ == "__main__":
    unittest.main()
