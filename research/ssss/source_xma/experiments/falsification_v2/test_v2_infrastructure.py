#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from market_data_panel import (
    EQUITIES,
    REQUIRED_STOCK_PANEL,
    build_panel,
)
from v2_feature_definitions import breadth_risk_off


def write_twelve_csv(path: Path, start: str = "2025-01-02", n: int = 40) -> None:
    dates = pd.bdate_range(start, periods=n)
    rows = ["datetime;open;high;low;close;volume"]
    for i, d in enumerate(dates):
        c = 100.0 + i
        rows.append(
            f"{d.date()};{c-1:.2f};{c+1:.2f};{c-2:.2f};{c:.2f};{1000000+i}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


class MarketDataPanelTests(unittest.TestCase):
    def test_32_of_39_is_breadth_capable_but_not_freeze_ready(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "raw"
            out = root / "panel"
            for symbol in EQUITIES[:32]:
                write_twelve_csv(raw / f"{symbol}.csv")

            manifest = build_panel(
                raw_dir=raw,
                output_dir=out,
                provider="TEST",
                adjustment_mode="TEST_RAW",
                timezone="America/New_York",
                retrieved_at="2026-09-28T00:00:00+00:00",
            )

            self.assertEqual(manifest["breadth_members_cached"], 32)
            self.assertTrue(manifest["breadth_80pct_path_available"])
            self.assertFalse(manifest["official_freeze_ready"])
            self.assertGreater(len(manifest["missing_raw_symbols"]), 0)

    def test_all_51_stock_etf_series_are_required_for_freeze_ready(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "raw"
            out = root / "panel"
            for symbol in REQUIRED_STOCK_PANEL:
                write_twelve_csv(raw / f"{symbol}.csv")

            manifest = build_panel(
                raw_dir=raw,
                output_dir=out,
                provider="TEST",
                adjustment_mode="TEST_RAW",
                timezone="America/New_York",
                retrieved_at="2026-09-28T00:00:00+00:00",
            )

            self.assertEqual(len(REQUIRED_STOCK_PANEL), 51)
            self.assertEqual(manifest["missing_raw_symbols"], [])
            self.assertEqual(manifest["breadth_members_cached"], 39)
            self.assertTrue(manifest["official_freeze_ready"])

    def test_normalized_manifest_contains_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "raw"
            out = root / "panel"
            write_twelve_csv(raw / "AAPL.csv")

            manifest = build_panel(
                raw_dir=raw,
                output_dir=out,
                provider="TEST",
                adjustment_mode="TEST_RAW",
                timezone="America/New_York",
                retrieved_at="2026-09-28T00:00:00+00:00",
                symbols=("AAPL",),
            )

            item = manifest["symbols"][0]
            self.assertEqual(item["symbol"], "AAPL")
            self.assertEqual(len(item["raw_sha256"]), 64)
            self.assertEqual(len(item["normalized_sha256"]), 64)
            self.assertEqual(item["duplicate_dates"], 0)
            self.assertEqual(item["missing_ohlcv_rows"], 0)


class FeatureDefinitionTests(unittest.TestCase):
    def test_breadth_q10_uses_prior_20_valid_observations_not_rows(self) -> None:
        idx = pd.bdate_range("2025-01-02", periods=30)
        values = pd.Series(np.arange(30, dtype=float), index=idx)

        # Put NaNs inside the most recent 20 calendar rows.
        values.iloc[12] = np.nan
        values.iloc[17] = np.nan
        values.iloc[21] = np.nan

        result = breadth_risk_off(values)

        # There are still 20 valid historical observations by the last date,
        # so the last date must be classifiable.
        self.assertFalse(pd.isna(result.iloc[-1]))

        prior_valid = values.iloc[:-1].dropna().iloc[-20:]
        expected_q10 = prior_valid.quantile(0.10, interpolation="linear")
        expected = bool(values.iloc[-1] < expected_q10)
        self.assertEqual(bool(result.iloc[-1]), expected)


if __name__ == "__main__":
    unittest.main()
