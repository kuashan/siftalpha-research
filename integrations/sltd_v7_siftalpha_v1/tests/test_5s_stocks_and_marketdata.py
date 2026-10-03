from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import os
import tempfile
import unittest
from unittest.mock import patch

import app
import data_provider
import five_s_stocks_strategy
from five_s_signal_engine import BarEvaluation


def _bar_evaluation(i: int, *, buy=(), sell=()) -> BarEvaluation:
    return BarEvaluation(
        index=i,
        open_time=i,
        states={
            "trend": "GRAY",
            "capital": "GRAY",
            "momentum": "GRAY",
            "accel": "GRAY",
            "anomaly": "GRAY",
        },
        buy_active=tuple(buy),
        sell_active=tuple(sell),
        buy_onsets=tuple(buy),
        sell_onsets=tuple(sell),
        features={},
    )


def _candles(n: int = 130) -> list[dict]:
    out = []
    for i in range(n):
        p = 100.0 + i * 0.1
        out.append(
            {
                "date": f"2025-{1 + i // 28:02d}-{1 + i % 28:02d}",
                "open_time": i,
                "open": p,
                "high": p + 1.0,
                "low": p - 1.0,
                "close": p + 0.2,
                "volume": 1000.0 + i,
            }
        )
    return out


class FiveSStocksPolicyTests(unittest.TestCase):
    def test_independent_strategy_is_registered(self) -> None:
        self.assertIn("v7", app.AVAILABLE_STRATEGIES)
        self.assertIn("e", app.AVAILABLE_STRATEGIES)
        self.assertIn("5s_stocks", app.AVAILABLE_STRATEGIES)
        self.assertIn("support_resistance", app.AVAILABLE_STRATEGIES)

    def test_frozen_half_sell_and_later_distinct_full_exit(self) -> None:
        signals = {
            70: (("A",), ()),
            72: (("C",), ()),
            75: ((), ("A",)),
            78: ((), ("A",)),  # same family again: no second sale
            80: ((), ("B",)),  # later distinct family: full exit
            90: (("B",), ()),
            94: ((), ("C",)),  # SELL-C is full exit
            100: (("A",), ()),
            104: ((), ("B",)), # first isolated B: half of current 60% -> 30%
        }

        def fake_evaluator(rows):
            out = []
            for i, _row in enumerate(rows):
                buy, sell = signals.get(i, ((), ()))
                out.append(_bar_evaluation(i, buy=buy, sell=sell))
            return out

        with patch.object(
            five_s_stocks_strategy,
            "evaluate_candles",
            side_effect=fake_evaluator,
        ):
            payload = five_s_stocks_strategy.analyze_5s_stocks(
                "TEST",
                _candles(),
                timeframe="1d",
                display_limit=300,
            )

        markers = payload["markers"]
        by_exec = {(int(m["execution_date"].split("-")[1]), m["execution_date"]): m for m in markers}
        # Use marker sequence because synthetic dates wrap by month.
        seq = [(m["side"], round(float(m["position_after"]), 6)) for m in markers]
        self.assertEqual(
            [
                ("B", 0.6),  # BUY-A
                ("B", 1.0),  # BUY-C +40pp
                ("S", 0.5),  # isolated SELL-A: half current holding
                ("X", 0.0),  # later distinct SELL-B: full exit
                ("B", 0.6),  # BUY-B
                ("X", 0.0),  # SELL-C full exit
                ("B", 0.6),  # BUY-A
                ("S", 0.3),  # first isolated SELL-B: half of 60%
            ],
            seq,
        )
        self.assertFalse(any(m["signal_date"] == _candles()[78]["date"] for m in markers))
        self.assertEqual("5s_stocks", payload["strategy"]["id"])
        self.assertIn("首次半卖", payload["strategy"]["position_policy_zh"])

    def test_selected_timeframe_does_not_change_frozen_signal_equations(self) -> None:
        def fake_evaluator(rows):
            return [_bar_evaluation(i) for i, _ in enumerate(rows)]

        with patch.object(five_s_stocks_strategy, "evaluate_candles", side_effect=fake_evaluator):
            payload = five_s_stocks_strategy.analyze_5s_stocks(
                "TEST", _candles(), timeframe="1h"
            )
        self.assertEqual("1h", payload["strategy"]["timeframe"])
        self.assertIn("实验周期", payload["strategy"]["timeframe_validation_zh"])


class MarketDataBoundaryTests(unittest.TestCase):
    def test_cache_key_is_provider_symbol_and_timeframe_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"SLTD_RUNTIME_DATA_DIR": tmp}
        ):
            a = data_provider._cache_path("AAPL", "1d", "YAHOO_FINANCE_CHART")
            b = data_provider._cache_path("MSFT", "1d", "YAHOO_FINANCE_CHART")
            c = data_provider._cache_path("AAPL", "1h", "YAHOO_FINANCE_CHART")
            d = data_provider._cache_path("AAPL", "1d", "MASSIVE")
            self.assertEqual(4, len({a, b, c, d}))

    def test_router_result_is_exposed_in_market_metadata(self) -> None:
        bars = _candles(130)
        fake = SimpleNamespace(
            provider_id="TEST_PROVIDER",
            provider_label_zh="测试行情",
            market_id="US_EQUITY",
            payload={
                "completed": bars,
                "forming": None,
                "meta": {
                    "exchange_timezone": "America/New_York",
                    "regular_market_start": None,
                    "regular_market_end": None,
                },
            },
        )
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"SLTD_RUNTIME_DATA_DIR": tmp}
        ), patch.object(data_provider._STOCK_MARKET, "fetch", return_value=fake):
            completed, forming, meta = data_provider.fetch_bars(
                "AAPL", "1d", force_refresh=True
            )
        self.assertEqual(130, len(completed))
        self.assertIsNone(forming)
        self.assertEqual("TEST_PROVIDER", meta["provider_id"])
        self.assertEqual("测试行情", meta["provider"])
        self.assertEqual("US_EQUITY", meta["market_id"])

    def test_failed_symbol_never_falls_back_to_another_symbols_stale_cache(self) -> None:
        bars = _candles(130)
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"SLTD_RUNTIME_DATA_DIR": tmp}
        ):
            data_provider._write_cache(
                symbol="AAPL",
                timeframe="1d",
                provider_id="YAHOO_FINANCE_CHART",
                provider_label="雅虎财经",
                market_id="US_EQUITY",
                completed=bars,
                forming=None,
                meta={},
            )
            with patch.object(
                data_provider._STOCK_MARKET,
                "fetch",
                side_effect=RuntimeError("network down"),
            ):
                with self.assertRaises(data_provider.MarketDataError):
                    data_provider.fetch_bars("MSFT", "1d", force_refresh=True)


class WebUiContractTests(unittest.TestCase):
    def test_independent_strategy_tabs_exist(self) -> None:
        page = (Path(__file__).resolve().parents[1] / "templates" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn('data-strategy="v7"', page)
        self.assertIn('data-strategy="e"', page)
        self.assertIn('data-strategy="5s_stocks"', page)
        self.assertIn('data-strategy="support_resistance"', page)
        self.assertIn(">5s Stocks<", page)
        self.assertIn(">顺势<", page)
        self.assertIn("sr_short_pressure", page)
        self.assertIn("sr_long_support", page)

    def test_shunshi_four_line_visual_contract(self) -> None:
        page = (Path(__file__).resolve().parents[1] / "templates" / "index.html").read_text(
            encoding="utf-8"
        )
        # Missing overlay values must break the path instead of Number(null) -> 0,
        # which previously created vertical spikes from the chart floor.
        self.assertIn("raw===null||raw===undefined||raw===''", page)
        self.assertIn("started=false;", page)

        # Pressure is green, support is red. Long lines are solid width 2;
        # short lines are dashed width 1.
        self.assertIn("drawLine('sr_short_pressure','#52d49a',[5,4],1)", page)
        self.assertIn("drawLine('sr_short_support','#ff7b82',[5,4],1)", page)
        self.assertIn("drawLine('sr_long_pressure','#52d49a',[],2)", page)
        self.assertIn("drawLine('sr_long_support','#ff7b82',[],2)", page)
        self.assertIn("短压 · 绿虚线", page)
        self.assertIn("短支 · 红虚线", page)
        self.assertIn("长压 · 绿实线", page)
        self.assertIn("长支 · 红实线", page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
