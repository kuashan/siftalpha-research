import pathlib
import unittest

from config import Settings


class TimeframeExtensionTests(unittest.TestCase):
    def test_three_and_five_minute_intervals_are_available_as_experimental(self):
        settings = Settings()
        self.assertEqual(settings.allowed_timeframes[:3], ("3m", "5m", "15m"))
        self.assertNotIn("3m", settings.validated_timeframes)
        self.assertNotIn("5m", settings.validated_timeframes)

    def test_ui_has_chinese_labels_for_new_intervals(self):
        text = (pathlib.Path(__file__).parents[1] / "app.py").read_text(encoding="utf-8")
        self.assertIn('"3m": "3 分钟"', text)
        self.assertIn('"5m": "5 分钟"', text)


if __name__ == "__main__":
    unittest.main()
