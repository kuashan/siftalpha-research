from __future__ import annotations

import csv
from datetime import datetime, timezone
import gzip
import json
import math
import sys
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen


REPO = Path(__file__).resolve().parents[3]
PROJECT = REPO / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))

import app  # noqa: E402
import data_provider  # noqa: E402
import strategy  # noqa: E402


DATA = REPO / "research" / "ssss_reboot_v1" / "phase7" / "data_snapshot" / "batch_01_stocks" / "AAPL.csv.gz"
LEDGER = REPO / "research" / "ssss_reboot_v1" / "phase7" / "signal_ledgers" / "BATCH_01_AAPL_FIRST_OBSERVED.csv.gz"
ROBUSTNESS = REPO / "research" / "ssss_reboot_v1" / "phase8" / "SLTD_V7_79_STOCK_ROBUSTNESS_RESULT_v1.json"


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


def split_rules(value: str | None) -> list[str]:
    return [x for x in str(value or "").split("|") if x]


def load_expected_v6() -> list[dict]:
    with gzip.open(LEDGER, "rt", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class StrategyRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candles = load_candles()
        cls.actual = strategy.build_ledger(cls.candles, "AAPL")
        cls.expected = load_expected_v6()

    def test_v7_has_exactly_12_active_rules(self) -> None:
        active = [r for group in strategy.ACTIVE_RULES.values() for r in group]
        self.assertEqual(12, len(active))
        self.assertEqual(12, len(set(active)))
        for removed in strategy.REMOVED_V6_RULES:
            self.assertNotIn(removed, active)

    def test_signal_math_matches_frozen_v6_ledger_then_applies_only_v7_deletions(self) -> None:
        self.assertEqual(len(self.expected), len(self.actual))
        removed = set(strategy.REMOVED_V6_RULES)

        for i, (exp, act) in enumerate(zip(self.expected, self.actual)):
            self.assertEqual(exp["date"], act["date"], i)
            self.assertEqual(exp["color"], act["color"], i)
            self.assertEqual(int(exp["run_age"]), act["run_age"], i)
            self.assertEqual(exp["age"], act["age"], i)
            self.assertEqual((exp["origin"] or None), act["origin"], i)
            self.assertEqual(exp["lower"] == "True", act["lower"], i)
            self.assertEqual((exp["lower_subtype"] or None), act["lower_subtype"], i)
            self.assertEqual(exp["upper"] == "True", act["upper"], i)
            self.assertEqual((exp["upper_subtype"] or None), act["upper_subtype"], i)
            self.assertEqual(exp["light_support"] == "True", act["light_support"], i)
            self.assertEqual(exp["light_resist"] == "True", act["light_resist"], i)

            for key in ("ZD1", "ZK1", "GZB3", "GZB4"):
                ev = exp[key]
                av = act[key]
                if ev == "" or ev is None:
                    self.assertIsNone(av, (i, key))
                else:
                    self.assertTrue(
                        math.isclose(float(ev), float(av), rel_tol=1e-10, abs_tol=1e-10),
                        (i, key, ev, av),
                    )

            for cls_name in ("BUY", "HOLD", "WAIT", "SELL"):
                filtered = [r for r in split_rules(exp[cls_name]) if r not in removed]
                self.assertEqual(filtered, act[cls_name], (i, cls_name))

    def test_aapl_candidate_b_execution_matches_frozen_79_stock_result(self) -> None:
        sim = strategy.simulate_policy(self.candles, self.actual, friction_bps=5.0)
        frozen = json.loads(ROBUSTNESS.read_text(encoding="utf-8"))
        expected = frozen["per_symbol"]["AAPL"]["5bps"]["CANDIDATE_B_DROP_B3_S1_S3"]

        self.assertTrue(
            math.isclose(sim["final_equity"] - 1.0, expected["total_return"], rel_tol=1e-10, abs_tol=1e-10)
        )
        self.assertEqual(len(sim["markers"]), expected["position_changes"])
        self.assertEqual(sum(1 for m in sim["markers"] if m["side"] == "X"), expected["hard_exit_count"])

    def test_analyze_display_is_capped_at_300_without_limiting_history_math(self) -> None:
        payload = strategy.analyze("AAPL", self.candles, display_limit=300, timeframe="1d")
        self.assertEqual(300, len(payload["chart"]))
        self.assertEqual(12, payload["strategy"]["active_rule_count"])
        self.assertEqual("AAPL", payload["snapshot"]["symbol"])
        self.assertEqual("1d", payload["strategy"]["timeframe"])
        self.assertEqual(
            "CONFIRMED_ON_SELECTED_BAR_CLOSE_EXECUTE_ON_NEXT_SELECTED_BAR_OPEN",
            payload["strategy"]["bar_close_contract"],
        )
        self.assertGreater(len(self.actual), len(payload["chart"]))


class BarCloseContractTest(unittest.TestCase):
    def test_supported_timeframes_are_not_daily_only(self) -> None:
        self.assertEqual({"5m", "15m", "30m", "1h", "4h", "1d"}, set(data_provider.TIMEFRAMES))
        self.assertTrue(data_provider.TIMEFRAMES["1d"]["validated"])
        self.assertFalse(data_provider.TIMEFRAMES["15m"]["validated"])
        self.assertFalse(data_provider.TIMEFRAMES["4h"]["validated"])
        self.assertEqual("1h", data_provider.TIMEFRAMES["4h"]["aggregate_from"])

    def test_four_hour_aggregation_uses_four_hour_then_session_tail(self) -> None:
        rows = []
        base = int(datetime(2023, 11, 14, 9, 30, tzinfo=timezone.utc).timestamp())
        for i in range(7):
            rows.append(
                {
                    "date": str(i),
                    "open_time": base + i * 3600,
                    "open": 100 + i,
                    "high": 101 + i,
                    "low": 99 + i,
                    "close": 100.5 + i,
                    "volume": 10 + i,
                    "complete": True,
                }
            )
        regular_start = base
        regular_end = base + int(6.5 * 3600)
        aggregated = data_provider._aggregate_four_hour_bars(
            rows,
            exchange_timezone="UTC",
            regular_start=regular_start,
            regular_end=regular_end,
            now_ts=regular_end,
        )
        self.assertEqual(2, len(aggregated))
        self.assertEqual(4, aggregated[0]["source_bars"])
        self.assertEqual(3, aggregated[1]["source_bars"])
        self.assertTrue(aggregated[0]["complete"])
        self.assertTrue(aggregated[1]["complete"])
        self.assertEqual(100.0, aggregated[0]["open"])
        self.assertEqual(103.5, aggregated[0]["close"])
        self.assertEqual(104.0, aggregated[1]["open"])
        self.assertEqual(106.5, aggregated[1]["close"])

    def test_short_four_hour_tail_is_forming_until_session_close(self) -> None:
        base = int(datetime(2023, 11, 14, 9, 30, tzinfo=timezone.utc).timestamp())
        rows = [
            {
                "date": str(i),
                "open_time": base + i * 3600,
                "open": 100 + i,
                "high": 101 + i,
                "low": 99 + i,
                "close": 100.5 + i,
                "volume": 10,
                "complete": True,
            }
            for i in range(6)
        ]
        regular_start = base
        regular_end = base + int(6.5 * 3600)
        aggregated = data_provider._aggregate_four_hour_bars(
            rows,
            exchange_timezone="UTC",
            regular_start=regular_start,
            regular_end=regular_end,
            now_ts=regular_end - 60,
        )
        self.assertEqual(2, len(aggregated))
        self.assertTrue(aggregated[0]["complete"])
        self.assertFalse(aggregated[1]["complete"])

    def test_intraday_bar_is_not_confirmed_before_its_selected_close(self) -> None:
        # 5-minute bar opened at t=4700 and regular session ends at t=5000.
        self.assertFalse(
            data_provider._is_complete(
                4700, "5m", 4999, regular_start=1000, regular_end=5000
            )
        )
        self.assertTrue(
            data_provider._is_complete(
                4700, "5m", 5000, regular_start=1000, regular_end=5000
            )
        )

    def test_daily_bar_is_not_confirmed_until_regular_session_close(self) -> None:
        self.assertFalse(
            data_provider._is_complete(
                1000, "1d", 4999, regular_start=1000, regular_end=5000
            )
        )
        self.assertTrue(
            data_provider._is_complete(
                1000, "1d", 5000, regular_start=1000, regular_end=5000
            )
        )


class WebSmokeTest(unittest.TestCase):
    def test_health_endpoint_and_ephemeral_port(self) -> None:
        server = app.create_server("127.0.0.1", 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = int(server.server_address[1])
            self.assertGreater(port, 0)
            with urlopen(f"http://127.0.0.1:{port}/api/health", timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertTrue(payload["ok"])
            self.assertEqual(12, payload["active_rules"])
            self.assertTrue(payload["bar_close_contract"])
            self.assertIn("15m", payload["timeframes"])
            self.assertIn("1h", payload["timeframes"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
