#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from provider_parity_audit import DEFAULT_SUBSET, audit_symbol


def write_semicolon(path: Path) -> None:
    path.write_text(
        "datetime;open;high;low;close;volume\n"
        "2025-01-02;100;102;99;101;1000\n"
        "2025-01-03;101;103;100;102;1100\n",
        encoding="utf-8",
    )


def write_yfinance(path: Path, changed: bool = False) -> None:
    c2 = 102.5 if changed else 102.0
    path.write_text(
        "Date,Open,High,Low,Close,Adj Close,Volume,Dividends,Stock Splits\n"
        "2025-01-02,100,102,99,101,100.5,1000,0,0\n"
        f"2025-01-03,101,103,100,{c2},101.5,1100,0.25,2\n",
        encoding="utf-8",
    )


class ProviderParityTests(unittest.TestCase):
    def test_preregistered_subset_is_fixed(self) -> None:
        self.assertEqual(
            DEFAULT_SUBSET,
            ("AAPL", "NVDA", "TSLA", "JPM", "XOM", "NEE", "SPY", "XLK"),
        )

    def test_identical_ohlcv_reports_zero_difference(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            left = root / "left.csv"
            right = root / "right.csv"
            write_semicolon(left)
            write_yfinance(right, changed=False)

            result = audit_symbol(left, right)
            self.assertEqual(result["overlap_rows"], 2)
            self.assertEqual(result["left_only_dates"], [])
            self.assertEqual(result["right_only_dates"], [])
            for field in ("open", "high", "low", "close", "volume"):
                self.assertEqual(
                    result["field_differences"][field]["abs_diff_max"],
                    0.0,
                )

            actions = result["right_corporate_actions"]
            self.assertEqual(actions["dividends"][0]["value"], 0.25)
            self.assertEqual(actions["stock_splits"][0]["value"], 2.0)
            self.assertIn("adj_close_to_close_ratio", actions)

    def test_difference_is_reported_not_auto_classified(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            left = root / "left.csv"
            right = root / "right.csv"
            write_semicolon(left)
            write_yfinance(right, changed=True)

            result = audit_symbol(left, right)
            self.assertGreater(
                result["field_differences"]["close"]["abs_diff_max"],
                0.0,
            )


if __name__ == "__main__":
    unittest.main()
