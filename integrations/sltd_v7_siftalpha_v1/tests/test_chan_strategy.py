from __future__ import annotations

import csv
import gzip
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROJECT = REPO / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))

import app  # noqa: E402
import chan_strategy  # noqa: E402


DATA = (
    REPO
    / "research"
    / "ssss_reboot_v1"
    / "phase7"
    / "data_snapshot"
    / "batch_01_stocks"
    / "AAPL.csv.gz"
)
PAGE = PROJECT / "templates" / "index.html"


def load_candles() -> list[dict]:
    out = []
    with gzip.open(DATA, "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out.append(
                {
                    "date": row["Date"][:10],
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row.get("Volume") or 0.0),
                }
            )
    return out


class ChanUpstreamAdapterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candles = load_candles()
        cls.payload = chan_strategy.analyze_chan(
            "AAPL",
            cls.candles,
            display_limit=300,
            timeframe="1d",
        )

    def test_pinned_upstream_identity(self) -> None:
        self.assertEqual(
            "429d6ed3043e27c93a003ba2b10e70a05575e1f5",
            chan_strategy.CHANPY_UPSTREAM_SHA,
        )
        self.assertIn("chan.py", chan_strategy.CHAN_STRATEGY_VERSION)

    def test_all_upstream_bsp_classes_exposed(self) -> None:
        buy = chan_strategy.CHAN_RULES["BUY"]
        sell = chan_strategy.CHAN_RULES["SELL"]
        for suffix in ("1", "1P", "2", "2S", "3A", "3B"):
            self.assertIn(f"CHAN_B{suffix}", buy)
            self.assertIn(f"CHAN_S{suffix}", sell)
        self.assertEqual(12, sum(len(x) for x in chan_strategy.CHAN_RULES.values()))

    def test_payload_is_powered_by_upstream(self) -> None:
        p = self.payload
        self.assertEqual("chan", p["strategy"]["id"])
        self.assertEqual("缠论", p["strategy"]["selector_label"])
        self.assertEqual(
            chan_strategy.CHANPY_UPSTREAM_SHA,
            p["strategy"]["upstream_sha"],
        )
        self.assertEqual("Vespa314/chan.py", p["chan"]["engine"])
        self.assertEqual(
            chan_strategy.CHANPY_UPSTREAM_SHA,
            p["chan"]["upstream_sha"],
        )
        self.assertLessEqual(len(p["chart"]), 300)

    def test_upstream_structure_and_bsp_are_present(self) -> None:
        counts = self.payload["chan"]["counts"]
        self.assertGreater(counts["bis"], 0)
        self.assertGreater(counts["segments"], 0)
        self.assertGreater(counts["zhongshus"], 0)
        self.assertGreater(counts["bi_level_bsp"], 0)
        self.assertGreater(len(self.payload["chan"]["signals"]), 0)

    def test_sure_and_virtual_state_are_preserved(self) -> None:
        for seg in self.payload["chan"]["segments"]:
            self.assertIn("pending", seg)
            self.assertEqual(seg["pending"], seg["confirm_date"] is None)
        for sig in self.payload["chan"]["signals"]:
            self.assertIn(sig["status"], {"SURE", "VIRTUAL_CURRENT_FRAME"})
            self.assertIn(sig["level"], {0, 1})

    def test_signal_types_are_upstream_types(self) -> None:
        allowed = {
            "B1", "B1P", "B2", "B2S", "B3A", "B3B",
            "S1", "S1P", "S2", "S2S", "S3A", "S3B",
        }
        for sig in self.payload["chan"]["signals"]:
            self.assertIn(sig["kind"], allowed, sig)

    def test_app_selector_accepts_chan(self) -> None:
        self.assertEqual("chan", app.normalize_strategy("chan"))
        self.assertEqual(
            chan_strategy.CHAN_STRATEGY_VERSION,
            app.AVAILABLE_STRATEGIES["chan"],
        )

    def test_page_has_independent_chan_visual_layers(self) -> None:
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn('data-strategy="chan"', page)
        self.assertIn("chan.zhongshus", page)
        self.assertIn("chan.segments", page)
        self.assertIn("chan.signals", page)
        self.assertIn("chan.endpoints", page)

    def test_shunshi_long_lines_remain_width_one(self) -> None:
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("drawLine('sr_long_pressure','#52d49a',[],1)", page)
        self.assertIn("drawLine('sr_long_support','#ff7b82',[],1)", page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
