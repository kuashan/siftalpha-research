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


class ChanStandaloneStrategyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candles = load_candles()
        cls.payload = chan_strategy.analyze_chan(
            "AAPL",
            cls.candles,
            display_limit=300,
            timeframe="1d",
        )

    def test_chan_is_six_bsp_classes(self) -> None:
        self.assertEqual(
            ("CHAN_B1", "CHAN_B2", "CHAN_B3"),
            chan_strategy.CHAN_RULES["BUY"],
        )
        self.assertEqual(
            ("CHAN_S1", "CHAN_S2", "CHAN_S3"),
            chan_strategy.CHAN_RULES["SELL"],
        )
        self.assertEqual(6, sum(len(x) for x in chan_strategy.CHAN_RULES.values()))

    def test_chan_payload_is_independent_structure_mode(self) -> None:
        p = self.payload
        self.assertEqual("chan", p["strategy"]["id"])
        self.assertEqual("缠论", p["strategy"]["selector_label"])
        self.assertEqual(6, p["strategy"]["active_rule_count"])
        self.assertEqual("STRUCTURE_ONLY_NO_POSITION", p["strategy"]["position_policy"])
        self.assertEqual(0.0, p["snapshot"]["position_fraction"])
        self.assertLessEqual(len(p["chart"]), 300)
        self.assertIn("chan", p)
        self.assertIn("bis", p["chan"])
        self.assertIn("segments", p["chan"])
        self.assertIn("zhongshus", p["chan"])
        self.assertIn("signals", p["chan"])

    def test_signal_confirmation_never_precedes_anchor(self) -> None:
        date_pos = {row["date"]: i for i, row in enumerate(self.candles)}
        for sig in self.payload["chan"]["signals"]:
            self.assertIn(sig["anchor_date"], date_pos)
            self.assertIn(sig["confirm_date"], date_pos)
            self.assertGreaterEqual(
                date_pos[sig["confirm_date"]],
                date_pos[sig["anchor_date"]],
                sig,
            )

    def test_event_time_is_confirmation_time(self) -> None:
        date_pos = {row["date"]: i for i, row in enumerate(self.candles)}
        for event in self.payload["events"]:
            self.assertIn(event["date"], date_pos)
            anchor = str(event["age"]).replace("锚点 ", "", 1)
            self.assertIn(anchor, date_pos)
            self.assertGreaterEqual(date_pos[event["date"]], date_pos[anchor], event)

    def test_overlay_geometry_has_valid_dates_and_prices(self) -> None:
        visible = {x["date"] for x in self.payload["chart"]}
        for bi in self.payload["chan"]["bis"]:
            self.assertTrue(
                bi["start_date"] in visible or bi["end_date"] in visible
            )
            self.assertIsInstance(float(bi["start_price"]), float)
            self.assertIsInstance(float(bi["end_price"]), float)

        for zs in self.payload["chan"]["zhongshus"]:
            self.assertGreater(float(zs["ZG"]), float(zs["ZD"]))

    def test_app_selector_accepts_chan(self) -> None:
        self.assertEqual("chan", app.normalize_strategy("chan"))
        self.assertIn("chan", app.AVAILABLE_STRATEGIES)

    def test_page_has_chan_selector_and_visual_layers(self) -> None:
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn('data-strategy="chan"', page)
        self.assertIn("一/二/三买", page)
        self.assertIn("一/二/三卖", page)
        self.assertIn("chan.zhongshus", page)
        self.assertIn("chan.segments", page)
        self.assertIn("chan.signals", page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
