from __future__ import annotations

import csv
import gzip
import json
import math
import sys
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen


REPO = Path(__file__).resolve().parents[4]
PROJECT = REPO / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))

import app  # noqa: E402
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
        payload = strategy.analyze("AAPL", self.candles, display_limit=300)
        self.assertEqual(300, len(payload["chart"]))
        self.assertEqual(12, payload["strategy"]["active_rule_count"])
        self.assertEqual("AAPL", payload["snapshot"]["symbol"])
        self.assertGreater(len(self.actual), len(payload["chart"]))


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
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
