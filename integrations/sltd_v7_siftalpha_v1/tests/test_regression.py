from __future__ import annotations

import csv
from datetime import datetime, timezone
import gzip
import json
import math
import sys
import threading
import unittest
from unittest.mock import patch
from pathlib import Path
from urllib.request import urlopen


REPO = Path(__file__).resolve().parents[3]
PROJECT = REPO / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))

import app  # noqa: E402
import data_provider  # noqa: E402
import e_strategy  # noqa: E402
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

    def test_all_12_rules_have_chinese_display_names(self) -> None:
        active = [r for group in strategy.ACTIVE_RULES.values() for r in group]
        self.assertEqual(12, len(active))
        self.assertEqual(12, len(strategy.RULE_NAMES_ZH))
        for rule_id in active:
            name = strategy.RULE_NAMES_ZH.get(rule_id)
            self.assertIsNotNone(name, rule_id)
            self.assertRegex(name, r"[\u4e00-\u9fff]")
            self.assertNotEqual(rule_id, name)

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
        self.assertEqual(12, sum(len(v) for v in payload["strategy"]["active_rules_zh"].values()))
        self.assertRegex(payload["snapshot"]["resolved_action_zh"], r"[\u4e00-\u9fff]")
        self.assertRegex(payload["snapshot"]["state_zh"], r"[\u4e00-\u9fff]")
        self.assertGreater(len(self.actual), len(payload["chart"]))


class BarCloseContractTest(unittest.TestCase):
    def test_supported_timeframes_are_not_daily_only(self) -> None:
        self.assertEqual({"5m", "15m", "30m", "1h", "4h", "1d", "5d"}, set(data_provider.TIMEFRAMES))
        self.assertTrue(data_provider.TIMEFRAMES["1d"]["validated"])
        self.assertFalse(data_provider.TIMEFRAMES["15m"]["validated"])
        self.assertFalse(data_provider.TIMEFRAMES["4h"]["validated"])
        self.assertEqual("1h", data_provider.TIMEFRAMES["4h"]["aggregate_from"])
        self.assertEqual("1d", data_provider.TIMEFRAMES["5d"]["aggregate_from"])

    def test_market_data_windows_cover_all_selected_timeframes(self) -> None:
        now = 2_000_000_000
        expected = {
            "5m": ("5m", 30),
            "15m": ("15m", 55),
            "30m": ("30m", 55),
            "1h": ("60m", 365),
            "4h": ("60m", 365),
        }
        for timeframe, (interval, days) in expected.items():
            params = data_provider._request_params(
                timeframe, "2010-01-04", now_ts=now
            )
            self.assertEqual(interval, params["interval"], timeframe)
            self.assertNotIn("range", params, timeframe)
            self.assertEqual(now - days * 86400, params["period1"], timeframe)
            self.assertEqual(now + 60, params["period2"], timeframe)

        daily = data_provider._request_params("1d", "2010-01-04", now_ts=now)
        self.assertEqual("1d", daily["interval"])
        self.assertNotIn("range", daily)
        self.assertEqual(
            data_provider._utc_timestamp("2010-01-04"),
            daily["period1"],
        )
        self.assertGreater(daily["period2"], now)

        five_day = data_provider._request_params("5d", "2010-01-04", now_ts=now)
        self.assertEqual("1d", five_day["interval"])
        self.assertEqual(data_provider._utc_timestamp("2010-01-04"), five_day["period1"])
        self.assertGreater(five_day["period2"], now)

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



class EStrategyTest(unittest.TestCase):
    def test_higher_timeframe_mapping_is_exactly_user_confirmed(self) -> None:
        self.assertEqual(
            {
                "5m": "20m",
                "15m": "1h",
                "30m": "2h",
                "1h": "4h",
                "4h": "1d",
                "1d": "5d",
                "5d": "20d",
            },
            e_strategy.HIGHER_TIMEFRAME_MAP,
        )

    def test_daily_aggregation_requires_complete_five_bar_block(self) -> None:
        rows = []
        base = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())
        for i in range(12):
            rows.append(
                {
                    "date": f"2024-01-{i+1:02d}",
                    "open_time": base + i * 86400,
                    "open": 100 + i,
                    "high": 101 + i,
                    "low": 99 + i,
                    "close": 100.5 + i,
                    "volume": 10,
                    "complete": True,
                }
            )
        out = data_provider._aggregate_daily_bars(rows, 5)
        self.assertEqual(2, len(out))
        self.assertEqual(5, out[0]["source_bars"])
        self.assertEqual(5, out[1]["source_bars"])
        self.assertEqual(100.0, out[0]["open"])
        self.assertEqual(104.5, out[0]["close"])

    def test_e_position_points_same_bar_priority_and_reversal_exit(self) -> None:
        base = datetime(2020, 1, 1, tzinfo=timezone.utc)
        candles = []
        for i in range(625):
            dt = base.timestamp() + i * 86400
            close = 110.0
            high = 115.0
            low = 105.0
            if i in (600, 610):
                close = 95.0
                high = 108.0
                low = 94.0
            if i in (602, 612):
                close = 85.0
                high = 90.0
                low = 78.0
            if i == 604:
                close = 121.0
                high = 125.0
                low = 115.0
            if i == 605:
                close = 123.0
                high = 126.0
                low = 121.0
            if i == 606:
                close = 125.0
                high = 131.0
                low = 121.0
            if i == 614:
                close = 121.0
                high = 131.0
                low = 116.0
            if i == 615:
                close = 123.0
                high = 126.0
                low = 121.0
            if i == 616:
                close = 119.0
                high = 122.0
                low = 117.0
            candles.append(
                {
                    "date": datetime.fromtimestamp(dt, tz=timezone.utc).strftime("%Y-%m-%d"),
                    "open_time": int(dt),
                    "open": close,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": 1000.0,
                }
            )

        def fake_ledger(rows, symbol):
            data = list(rows)
            is_higher = ":" in symbol
            out = []
            for i, bar in enumerate(data):
                close = 90.0 if is_higher else float(bar["close"])
                out.append(
                    {
                        "symbol": symbol,
                        "date": bar["date"],
                        "open": float(bar["open"]),
                        "high": float(bar["high"]),
                        "low": float(bar["low"]),
                        "close": close,
                        "volume": float(bar.get("volume") or 0.0),
                        "ZD1": 100.0,
                        "ZK1": 120.0,
                        "GZB3": 80.0,
                        "GZB4": 75.0,
                        "BS": 130.0,
                        "BD": 60.0,
                        "color": "BLUE",
                        "run_age": i + 1,
                        "age": "21_PLUS",
                        "origin": None,
                    }
                )
            return out

        with patch.object(e_strategy, "build_ledger", side_effect=fake_ledger):
            payload = e_strategy.analyze_e(
                "TEST",
                candles,
                timeframe="1d",
                market_meta={},
                display_limit=300,
            )

        events = payload["events"]
        by_date = {e["date"]: e for e in events}

        # 条件1 + 条件2 同根确认：下一根执行 +50pp。
        first_buy = by_date[candles[600]["date"]]
        self.assertEqual("BUY", first_buy["action"])
        self.assertEqual(
            {
                "E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1",
                "E_BUY_2_HIGHER_CLOSE_BELOW_ZD1",
            },
            set(first_buy["rule_ids"]),
        )
        self.assertAlmostEqual(0.50, first_buy["position_after"])

        # 条件3后达到 75%。
        third_buy = by_date[candles[602]["date"]]
        self.assertEqual(["E_BUY_3_TOUCH_GZB_BAND"], third_buy["rule_ids"])
        self.assertAlmostEqual(0.75, third_buy["position_after"])

        # 收盘突破 ZK1：减 50 个百分点，75% -> 25%。
        sell1 = by_date[candles[604]["date"]]
        self.assertEqual(["E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP"], sell1["rule_ids"])
        self.assertAlmostEqual(0.25, sell1["position_after"])

        # 后续触碰 BS：再减 25 个百分点，25% -> 0%。
        sell2 = by_date[candles[606]["date"]]
        self.assertEqual(["E_SELL_2_TOUCH_BS_MINUS_25PP"], sell2["rule_ids"])
        self.assertAlmostEqual(0.0, sell2["position_after"])

        # 第二轮：同一根同时 ZK1 突破 + BS 触碰，只执行最高级别 BS -25pp，
        # 不再同根累计 -50pp；因此 75% -> 50%。
        same_bar = by_date[candles[614]["date"]]
        self.assertEqual(["E_SELL_2_TOUCH_BS_MINUS_25PP"], same_bar["rule_ids"])
        self.assertAlmostEqual(0.50, same_bar["position_after"])

        # 没到灰带就掉头，收盘跌回 ZK1 下方，剩余全部清仓。
        reversal = by_date[candles[616]["date"]]
        self.assertEqual(["E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT"], reversal["rule_ids"])
        self.assertEqual("HARD_EXIT", reversal["action"])
        self.assertAlmostEqual(0.0, reversal["position_after"])


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
