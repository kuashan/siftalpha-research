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


def U(direction: str, a: float, b: float, i: int) -> chan_strategy.StructUnit:
    return chan_strategy.StructUnit(
        direction=direction,
        from_index=i * 10,
        from_price=a,
        to_index=i * 10 + 9,
        to_price=b,
        high=max(a, b),
        low=min(a, b),
        start_index=i * 10,
        end_index=i * 10 + 9,
        confirm_index=i * 10 + 9,
        pending=False,
        count=1,
        kind="TEST",
        source_start=i,
        source_end=i,
    )


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
        self.assertEqual(
            6,
            sum(len(x) for x in chan_strategy.CHAN_RULES.values()),
        )

    def test_chan_payload_is_fully_independent(self) -> None:
        p = self.payload
        self.assertEqual("chan", p["strategy"]["id"])
        self.assertEqual("缠论", p["strategy"]["selector_label"])
        self.assertEqual("独立缠论 v2.2", p["strategy"]["version"])
        self.assertEqual(6, p["strategy"]["active_rule_count"])
        self.assertEqual(
            "CHAN_SIGNAL_ONLY_V2",
            p["strategy"]["position_policy"],
        )
        self.assertEqual(0.0, p["snapshot"]["position_fraction"])
        self.assertIn("完全隔离", p["snapshot"]["risk_sub_zh"])
        self.assertLessEqual(len(p["chart"]), 300)

        # No SLTD/XMA rail is emitted by the independent Chan chart rows.
        for row in p["chart"]:
            self.assertNotIn("ZD1", row)
            self.assertNotIn("ZK1", row)
            self.assertNotIn("BS", row)
            self.assertNotIn("GZB4", row)

    def test_multilevel_objects_exist(self) -> None:
        chan = self.payload["chan"]
        self.assertIn("endpoints", chan)
        self.assertIn("bis", chan)
        self.assertIn("segments", chan)
        self.assertIn("zhongshus", chan)
        self.assertIn("trends", chan)
        self.assertIn("signals", chan)
        self.assertIn("levels", chan)
        self.assertGreaterEqual(len(chan["levels"]), 1)
        self.assertEqual(0, chan["levels"][0]["level"])

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
            self.assertGreaterEqual(
                date_pos[event["date"]],
                date_pos[anchor],
                event,
            )
            if event["execution_date"]:
                self.assertGreater(
                    date_pos[event["execution_date"]],
                    date_pos[event["date"]],
                    event,
                )

    def test_default_top_bottom_are_only_valid_bi_endpoints(self) -> None:
        chan = self.payload["chan"]
        self.assertEqual(
            chan["counts"]["bi_endpoints"],
            len(chan_strategy.select_bi_points(
                chan_strategy.merge_inclusion(
                    chan_strategy._slice_analysis_window(
                        chan_strategy._validate_candles(self.candles)
                    )[0]
                ),
                chan_strategy.find_fractals(
                    chan_strategy.merge_inclusion(
                        chan_strategy._slice_analysis_window(
                            chan_strategy._validate_candles(self.candles)
                        )[0]
                    )
                ),
            )),
        )
        self.assertLessEqual(
            len(chan["endpoints"]),
            chan["counts"]["bi_endpoints"],
        )

    def test_zhongshu_clips_into_visible_window(self) -> None:
        visible = {x["date"] for x in self.payload["chart"]}
        for zs in self.payload["chan"]["zhongshus"]:
            self.assertIn(zs["start_date"], visible)
            self.assertIn(zs["end_date"], visible)
            self.assertGreater(float(zs["ZG"]), float(zs["ZD"]))

    def test_recursive_trend_types_shrink(self) -> None:
        units = [
            U("up", 5, 20, 0), U("down", 20, 10, 1),
            U("up", 10, 20, 2), U("down", 20, 10, 3),
            U("up", 10, 40, 4), U("down", 40, 35, 5),
            U("up", 35, 45, 6), U("down", 45, 35, 7),
            U("up", 35, 70, 8), U("down", 70, 65, 9),
            U("up", 65, 75, 10), U("down", 75, 65, 11),
            U("up", 65, 100, 12),
        ]
        zss = chan_strategy.build_zhongshus(
            units,
            level=1,
            unit_kind="TEST",
        )
        trends = chan_strategy.build_trend_types(
            units,
            zss,
            level=1,
        )
        self.assertGreaterEqual(len(zss), 2)
        self.assertLess(len(trends), len(units))
        self.assertTrue(
            any("TREND" in x.kind for x in trends),
            [x.kind for x in trends],
        )

    def test_third_class_buy_is_structural_not_macd_only(self) -> None:
        units = [
            U("down", 12, 8, 0),   # entering movement
            U("up", 8, 12, 1),
            U("down", 12, 9, 2),
            U("up", 9, 13, 3),     # center [9,12]
            U("down", 13, 10, 4),  # still touching
            U("up", 10, 16, 5),    # departure
            U("down", 16, 13, 6),  # first return, low >= ZG
            U("up", 13, 18, 7),
        ]
        zss = chan_strategy.build_zhongshus(
            units,
            level=0,
            unit_kind="TEST",
        )
        self.assertTrue(zss)

        bars = [
            chan_strategy.RawBar(
                date=f"2026-01-{(i % 28) + 1:02d}",
                open=10,
                high=11,
                low=9,
                close=10,
                volume=1,
                index=i,
            )
            for i in range(100)
        ]
        macd = {
            "dif": [0.0] * 100,
            "dea": [0.0] * 100,
            "hist": [0.0] * 100,
        }
        level = {
            "level": 0,
            "label": "L0 测试",
            "units": units,
            "zss": zss,
            "links": chan_strategy.link_zhongshus(zss),
        }
        sig = chan_strategy.compute_level_signals(
            bars,
            level,
            macd,
        )
        self.assertTrue(
            any(x["kind"] == "B3" for x in sig),
            sig,
        )


    def _signal_fixture_bars(self, n: int = 140):
        return [
            chan_strategy.RawBar(
                date=f"{2020 + i // 360:04d}-{(i // 30) % 12 + 1:02d}-{i % 28 + 1:02d}",
                open=10.0,
                high=11.0,
                low=9.0,
                close=10.0,
                volume=1.0,
                index=i,
            )
            for i in range(n)
        ]

    def test_standard_uptrend_divergence_emits_s1(self) -> None:
        units = [
            U("up", 5, 20, 0),
            U("down", 20, 12, 1),
            U("up", 12, 22, 2),
            U("down", 22, 14, 3),
            U("up", 14, 45, 4),   # b: enter second center
            U("down", 45, 34, 5),
            U("up", 34, 44, 6),
            U("down", 44, 36, 7),
            U("up", 36, 50, 8),   # c: new high, weaker
        ]
        z0 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=1, end_sub=3,
            zg=18, zd=14, gg=22, dd=12,
            start_index=10, end_index=39, confirm_index=39,
            count=3, pending=False, upgraded=False,
        )
        z1 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=5, end_sub=7,
            zg=40, zd=36, gg=44, dd=34,
            start_index=50, end_index=79, confirm_index=79,
            count=3, pending=False, upgraded=False,
        )
        hist = [0.0] * 140
        dif = [0.0] * 140
        for i in range(units[4].start_index, units[4].end_index + 1):
            hist[i] = 2.0
            dif[i] = 2.0
        for i in range(units[8].start_index, units[8].end_index + 1):
            hist[i] = 0.5
            dif[i] = 0.8
        level = {
            "level": 0,
            "label": "L0 测试",
            "units": units,
            "zss": [z0, z1],
            "links": [None, "up"],
            "parent_turns": [],
        }
        sig = chan_strategy.compute_level_signals(
            self._signal_fixture_bars(),
            level,
            {"dif": dif, "dea": [0.0] * 140, "hist": hist},
        )
        self.assertTrue(any(x["kind"] == "S1" for x in sig), sig)

    def test_standard_downtrend_divergence_emits_b1(self) -> None:
        units = [
            U("down", 60, 45, 0),
            U("up", 45, 53, 1),
            U("down", 53, 43, 2),
            U("up", 43, 51, 3),
            U("down", 51, 20, 4),  # b
            U("up", 20, 31, 5),
            U("down", 31, 21, 6),
            U("up", 21, 29, 7),
            U("down", 29, 15, 8),  # c: new low, weaker
        ]
        z0 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=1, end_sub=3,
            zg=51, zd=45, gg=53, dd=43,
            start_index=10, end_index=39, confirm_index=39,
            count=3, pending=False, upgraded=False,
        )
        z1 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=5, end_sub=7,
            zg=29, zd=25, gg=31, dd=20,
            start_index=50, end_index=79, confirm_index=79,
            count=3, pending=False, upgraded=False,
        )
        hist = [0.0] * 140
        dif = [0.0] * 140
        for i in range(units[4].start_index, units[4].end_index + 1):
            hist[i] = -2.0
            dif[i] = -2.0
        for i in range(units[8].start_index, units[8].end_index + 1):
            hist[i] = -0.5
            dif[i] = -0.8
        level = {
            "level": 0,
            "label": "L0 测试",
            "units": units,
            "zss": [z0, z1],
            "links": [None, "down"],
            "parent_turns": [],
        }
        sig = chan_strategy.compute_level_signals(
            self._signal_fixture_bars(),
            level,
            {"dif": dif, "dea": [0.0] * 140, "hist": hist},
        )
        self.assertTrue(any(x["kind"] == "B1" for x in sig), sig)


    def test_s1_requires_new_high_in_standard_trend_divergence(self) -> None:
        units = [
            U("up", 5, 20, 0),
            U("down", 20, 12, 1),
            U("up", 12, 22, 2),
            U("down", 22, 14, 3),
            U("up", 14, 45, 4),
            U("down", 45, 34, 5),
            U("up", 34, 44, 6),
            U("down", 44, 36, 7),
            U("up", 36, 43, 8),  # leaves ZG but does not exceed b high
        ]
        z0 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=1, end_sub=3,
            zg=18, zd=14, gg=22, dd=12,
            start_index=10, end_index=39, confirm_index=39,
            count=3, pending=False, upgraded=False,
        )
        z1 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=5, end_sub=7,
            zg=40, zd=36, gg=44, dd=34,
            start_index=50, end_index=79, confirm_index=79,
            count=3, pending=False, upgraded=False,
        )
        level = {
            "level": 0, "label": "L0 测试", "units": units,
            "zss": [z0, z1], "links": [None, "up"], "parent_turns": [],
        }
        sig = chan_strategy.compute_level_signals(
            self._signal_fixture_bars(),
            level,
            {"dif": [2.0] * 140, "dea": [0.0] * 140, "hist": [2.0] * 140},
        )
        self.assertFalse(any(x["kind"] == "S1" for x in sig), sig)

    def test_b1_requires_new_low_in_standard_trend_divergence(self) -> None:
        units = [
            U("down", 60, 45, 0),
            U("up", 45, 53, 1),
            U("down", 53, 43, 2),
            U("up", 43, 51, 3),
            U("down", 51, 20, 4),
            U("up", 20, 31, 5),
            U("down", 31, 25, 6),
            U("up", 25, 29, 7),
            U("down", 29, 22, 8),  # below ZD=25, but above b low=20
        ]
        z0 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=1, end_sub=3,
            zg=51, zd=45, gg=53, dd=43,
            start_index=10, end_index=39, confirm_index=39,
            count=3, pending=False, upgraded=False,
        )
        z1 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=5, end_sub=7,
            zg=29, zd=25, gg=31, dd=20,
            start_index=50, end_index=79, confirm_index=79,
            count=3, pending=False, upgraded=False,
        )
        level = {
            "level": 0, "label": "L0 测试", "units": units,
            "zss": [z0, z1], "links": [None, "down"], "parent_turns": [],
        }
        sig = chan_strategy.compute_level_signals(
            self._signal_fixture_bars(),
            level,
            {"dif": [-2.0] * 140, "dea": [0.0] * 140, "hist": [-2.0] * 140},
        )
        self.assertFalse(any(x["kind"] == "B1" for x in sig), sig)

    def test_lesson38_does_not_override_lesson37_new_high_requirement(self) -> None:
        # Lesson 37 requires c to make a new high/low in standard trend
        # divergence.  Lesson 38 same-level decomposition must not be used to
        # loosen that B1/S1 definition.
        units = [
            U("up", 5, 20, 0),
            U("down", 20, 12, 1),
            U("up", 12, 22, 2),
            U("down", 22, 14, 3),
            U("up", 14, 45, 4),
            U("down", 45, 34, 5),
            U("up", 34, 44, 6),
            U("down", 44, 36, 7),
            U("up", 36, 43, 8),   # leaves ZG=40, but no new trend high
        ]
        z0 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=1, end_sub=3,
            zg=18, zd=14, gg=22, dd=12,
            start_index=10, end_index=39, confirm_index=39,
            count=3, pending=False, upgraded=False,
        )
        z1 = chan_strategy.Zhongshu(
            level=0, unit_kind="TEST", start_sub=5, end_sub=7,
            zg=40, zd=36, gg=44, dd=34,
            start_index=50, end_index=79, confirm_index=79,
            count=3, pending=False, upgraded=False,
        )
        level = {
            "level": 0,
            "label": "L0 测试",
            "units": units,
            "zss": [z0, z1],
            "links": [None, "up"],
            "parent_turns": [],
        }
        sig = chan_strategy.compute_level_signals(
            self._signal_fixture_bars(),
            level,
            {
                "dif": [2.0] * 140,
                "dea": [0.0] * 140,
                "hist": [2.0] * 140,
            },
        )
        self.assertFalse(any(x["kind"] == "S1" for x in sig), sig)

    def test_b2_accepts_consolidation_divergence_new_low(self) -> None:
        units = [
            U("up", 20, 30, 0),
            U("down", 30, 18, 1),
            U("down", 18, 10, 2),  # parent structural low
            U("up", 10, 22, 3),
            U("down", 22, 9, 4),   # new low, but much weaker down force
            U("up", 9, 25, 5),
        ]
        turn = chan_strategy.StructUnit(
            direction="down",
            from_index=units[0].from_index,
            from_price=30,
            to_index=units[2].to_index,
            to_price=10,
            high=30,
            low=10,
            start_index=units[0].start_index,
            end_index=units[2].end_index,
            confirm_index=units[2].confirm_index,
            pending=False,
            count=3,
            kind="SEGMENT",
            source_start=0,
            source_end=2,
        )
        hist = [0.0] * 140
        dif = [0.0] * 140
        for i in range(units[2].start_index, units[2].end_index + 1):
            hist[i] = -2.0
            dif[i] = -2.0
        for i in range(units[4].start_index, units[4].end_index + 1):
            hist[i] = -0.25
            dif[i] = -0.5
        level = {
            "level": 0,
            "label": "L0 测试",
            "units": units,
            "zss": [],
            "links": [],
            "parent_turns": [turn],
        }
        sig = chan_strategy.compute_level_signals(
            self._signal_fixture_bars(),
            level,
            {"dif": dif, "dea": [0.0] * 140, "hist": hist},
        )
        b2 = [x for x in sig if x["kind"] == "B2"]
        self.assertTrue(b2, sig)
        self.assertIn("盘整背驰", b2[0]["note"])

    def test_b2_does_not_require_a_b1(self) -> None:
        units = [
            U("up", 20, 30, 0),
            U("down", 30, 18, 1),
            U("down", 18, 10, 2),  # parent low endpoint
            U("up", 10, 22, 3),
            U("down", 22, 13, 4),  # first return, no new low
            U("up", 13, 25, 5),
        ]
        turn = chan_strategy.StructUnit(
            direction="down",
            from_index=units[0].from_index,
            from_price=30,
            to_index=units[2].to_index,
            to_price=10,
            high=30,
            low=10,
            start_index=units[0].start_index,
            end_index=units[2].end_index,
            confirm_index=units[2].confirm_index,
            pending=False,
            count=3,
            kind="SEGMENT",
            source_start=0,
            source_end=2,
        )
        level = {
            "level": 0,
            "label": "L0 测试",
            "units": units,
            "zss": [],
            "links": [],
            "parent_turns": [turn],
        }
        sig = chan_strategy.compute_level_signals(
            self._signal_fixture_bars(),
            level,
            {"dif": [0.0] * 140, "dea": [0.0] * 140, "hist": [0.0] * 140},
        )
        self.assertTrue(any(x["kind"] == "B2" for x in sig), sig)
        self.assertFalse(any(x["kind"] == "B1" for x in sig), sig)

    def test_s2_does_not_require_an_s1(self) -> None:
        units = [
            U("down", 30, 20, 0),
            U("up", 20, 32, 1),
            U("up", 32, 40, 2),    # parent high endpoint
            U("down", 40, 28, 3),
            U("up", 28, 37, 4),    # first return, no new high
            U("down", 37, 24, 5),
        ]
        turn = chan_strategy.StructUnit(
            direction="up",
            from_index=units[0].from_index,
            from_price=20,
            to_index=units[2].to_index,
            to_price=40,
            high=40,
            low=20,
            start_index=units[0].start_index,
            end_index=units[2].end_index,
            confirm_index=units[2].confirm_index,
            pending=False,
            count=3,
            kind="SEGMENT",
            source_start=0,
            source_end=2,
        )
        level = {
            "level": 0,
            "label": "L0 测试",
            "units": units,
            "zss": [],
            "links": [],
            "parent_turns": [turn],
        }
        sig = chan_strategy.compute_level_signals(
            self._signal_fixture_bars(),
            level,
            {"dif": [0.0] * 140, "dea": [0.0] * 140, "hist": [0.0] * 140},
        )
        self.assertTrue(any(x["kind"] == "S2" for x in sig), sig)
        self.assertFalse(any(x["kind"] == "S1" for x in sig), sig)

    def test_app_selector_accepts_chan(self) -> None:
        self.assertEqual("chan", app.normalize_strategy("chan"))
        self.assertIn("chan", app.AVAILABLE_STRATEGIES)

    def test_page_has_independent_chan_visual_layers(self) -> None:
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn('data-strategy="chan"', page)
        self.assertIn("独立缠论", page)
        self.assertIn("一/二/三买", page)
        self.assertIn("一/二/三卖", page)
        self.assertIn("chan.zhongshus", page)
        self.assertIn("chan.segments", page)
        self.assertIn("chan.signals", page)
        self.assertIn("chan.endpoints", page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
