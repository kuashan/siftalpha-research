from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import support_resistance_strategy as sr  # noqa: E402


def _candles(n: int = 220) -> list[dict]:
    out: list[dict] = []
    for i in range(n):
        base = 100.0 + 10.0 * math.sin(2.0 * math.pi * i / 30.0) + 0.03 * i
        out.append(
            {
                "date": f"2025-{i:04d}",
                "open": base - 0.2,
                "high": base + 1.0,
                "low": base - 1.0,
                "close": base + 0.2,
                "volume": 1000.0 + i,
            }
        )
    return out


class TongDaXinPrimitiveTests(unittest.TestCase):
    def test_filter_matches_tdx_following_n_bar_suppression(self) -> None:
        self.assertEqual(
            [True, False, False, True, False, False, True],
            sr._filter([True] * 7, 2),
        )

    def test_backset_sets_current_plus_previous_n_minus_one(self) -> None:
        self.assertEqual(
            [False, True, True, False],
            sr._backset([False, False, True, False], 2),
        )

    def test_periods_are_frozen_to_short_3_long_7(self) -> None:
        self.assertEqual(3, sr.SHORT_PERIOD)
        self.assertEqual(7, sr.LONG_PERIOD)


class SupportResistanceStrategyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candles = _candles()
        cls.calc = sr.compute_support_resistance(cls.candles)
        cls.payload = sr.analyze_support_resistance(
            "TEST",
            cls.candles,
            timeframe="1d",
            display_limit=300,
        )

    def test_both_periods_produce_two_pressure_support_anchors(self) -> None:
        for key in ("short", "long"):
            layer = self.calc[key]
            self.assertIsNotNone(layer["pressure_anchor"], key)
            self.assertIsNotNone(layer["support_anchor"], key)
            self.assertGreaterEqual(len(layer["high_pivots"]), 2, key)
            self.assertGreaterEqual(len(layer["low_pivots"]), 2, key)

    def test_drawline_values_extend_to_latest_bar(self) -> None:
        for key in ("short", "long"):
            layer = self.calc[key]
            self.assertIsNotNone(layer["pressure"][-1], key)
            self.assertIsNotNone(layer["support"][-1], key)
            self.assertTrue(math.isfinite(float(layer["pressure"][-1])))
            self.assertTrue(math.isfinite(float(layer["support"][-1])))

    def test_payload_is_display_only_and_contains_exact_four_lines(self) -> None:
        payload = self.payload
        self.assertEqual("support_resistance", payload["strategy"]["id"])
        self.assertEqual(3, payload["strategy"]["short_period"])
        self.assertEqual(7, payload["strategy"]["long_period"])
        self.assertTrue(payload["strategy"]["repainting"])
        self.assertEqual([], payload["markers"])
        self.assertEqual([], payload["events"])
        self.assertEqual("NONE", payload["snapshot"]["resolved_action"])
        self.assertEqual(0, payload["strategy"]["active_rule_count"])

        row = payload["chart"][-1]
        line_keys = {
            "sr_short_pressure",
            "sr_short_support",
            "sr_long_pressure",
            "sr_long_support",
        }
        self.assertTrue(line_keys.issubset(row))
        for key in line_keys:
            self.assertIsNotNone(row[key], key)

    def test_display_limit_does_not_limit_formula_history(self) -> None:
        payload = sr.analyze_support_resistance(
            "TEST",
            self.candles,
            timeframe="1d",
            display_limit=80,
        )
        self.assertEqual(80, len(payload["chart"]))
        # Anchors are calculated on the full history, then only the chart is clipped.
        self.assertIsNotNone(payload["support_resistance"]["long_pressure_anchor"])
        self.assertIsNotNone(payload["support_resistance"]["long_support_anchor"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
