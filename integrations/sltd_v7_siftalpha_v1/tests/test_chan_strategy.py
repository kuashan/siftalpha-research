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

DATA = REPO / "research" / "ssss_reboot_v1" / "phase7" / "data_snapshot" / "batch_01_stocks" / "AAPL.csv.gz"
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


class UpstreamChanStrategyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = chan_strategy.analyze_chan(
            "AAPL",
            load_candles(),
            display_limit=300,
            timeframe="1d",
        )

    def test_upstream_is_pinned(self) -> None:
        self.assertEqual(
            "429d6ed3043e27c93a003ba2b10e70a05575e1f5",
            chan_strategy.CHAN_UPSTREAM_COMMIT,
        )
        self.assertIn("chan.py upstream", chan_strategy.CHAN_STRATEGY_VERSION)
        self.assertTrue((PROJECT / "vendor" / "chanpy" / "LICENSE").exists())
        self.assertTrue((PROJECT / "vendor" / "chanpy" / "Chan.py").exists())

    def test_all_upstream_bsp_classes_are_exposed(self) -> None:
        kinds = set(chan_strategy.CHAN_RULES["BUY"] + chan_strategy.CHAN_RULES["SELL"])
        for rule in (
            "CHAN_B1", "CHAN_B1P", "CHAN_B2", "CHAN_B2S", "CHAN_B3A", "CHAN_B3B",
            "CHAN_S1", "CHAN_S1P", "CHAN_S2", "CHAN_S2S", "CHAN_S3A", "CHAN_S3B",
        ):
            self.assertIn(rule, kinds)
        self.assertEqual(12, sum(len(x) for x in chan_strategy.CHAN_RULES.values()))

    def test_payload_uses_upstream_core(self) -> None:
        p = self.payload
        self.assertEqual("chan", p["strategy"]["id"])
        self.assertEqual("缠论", p["strategy"]["selector_label"])
        self.assertEqual(
            chan_strategy.CHAN_UPSTREAM_COMMIT,
            p["chan"]["upstream_commit"],
        )
        self.assertGreater(p["chan"]["counts"]["bis"], 0)
        self.assertGreater(p["chan"]["counts"]["segments"], 0)
        self.assertGreater(p["chan"]["counts"]["zhongshus"], 0)
        self.assertGreater(p["chan"]["counts"]["bsp_points"], 0)
        self.assertGreater(p["chan"]["counts"]["segment_bsp_points"], 0)
        self.assertLessEqual(len(p["chart"]), 300)

    def test_current_frame_signals_have_valid_upstream_types(self) -> None:
        allowed = {
            "B1", "B1P", "B2", "B2S", "B3A", "B3B",
            "S1", "S1P", "S2", "S2S", "S3A", "S3B",
        }
        for sig in self.payload["chan"]["signals"]:
            self.assertIn(sig["kind"], allowed)
            self.assertIn(sig["level"], (0, 1))
            self.assertIsInstance(sig["sure_structure"], bool)

    def test_virtual_and_confirmed_structure_contract_is_exposed(self) -> None:
        counts = self.payload["chan"]["counts"]
        self.assertEqual(
            counts["segments"],
            counts["sure_segments"] + counts["virtual_segments"],
        )
        for seg in self.payload["chan"]["segments"]:
            self.assertIn("pending", seg)
            self.assertIsInstance(seg["pending"], bool)

    def test_zhongshu_is_well_formed(self) -> None:
        visible = {x["date"] for x in self.payload["chart"]}
        for zs in self.payload["chan"]["zhongshus"]:
            self.assertIn(zs["start_date"], visible)
            self.assertIn(zs["end_date"], visible)
            self.assertGreater(float(zs["ZG"]), float(zs["ZD"]))

    def test_app_selector_accepts_chan(self) -> None:
        self.assertEqual("chan", app.normalize_strategy("chan"))
        self.assertEqual(
            chan_strategy.CHAN_STRATEGY_VERSION,
            app.AVAILABLE_STRATEGIES["chan"],
        )

    def test_page_preserves_shunshi_width_one(self) -> None:
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("drawLine('sr_short_pressure','#52d49a',[5,4],1)", page)
        self.assertIn("drawLine('sr_short_support','#ff7b82',[5,4],1)", page)
        self.assertIn("drawLine('sr_long_pressure','#52d49a',[],1)", page)
        self.assertIn("drawLine('sr_long_support','#ff7b82',[],1)", page)

    def test_page_keeps_chan_visual_layers(self) -> None:
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn('data-strategy="chan"', page)
        self.assertIn("chan.zhongshus", page)
        self.assertIn("chan.segments", page)
        self.assertIn("chan.signals", page)
        self.assertIn("chan.endpoints", page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
