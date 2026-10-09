"""ZBGE drawings and historical signal markers are not trades."""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from strategy.zbge_strategy import ZBGEPoint, evaluate_zbge


class ZBGEVisualTests(unittest.TestCase):
    def _rows(self, count=260):
        rows = []
        for i in range(count):
            center = 90000 + i * 6 + (i % 19 - 9) * 100
            rows.append([1700000000000 + i * 14400000,
                         center - 40, center + 190,
                         center - 180, center + 20, 1234])
        return rows

    def test_plot_values_are_causal_and_do_not_modify_signals(self):
        full = evaluate_zbge(self._rows())
        for size in (180, 230):
            self.assertEqual(evaluate_zbge(self._rows(size)), full[:size])
        self.assertTrue(any(p.cyan is not None or p.red is not None or
                            p.gray is not None for p in full))
        for p in full:
            self.assertEqual(p.sell, p.sell_a or p.sell_b)
            if p.rush_red:
                self.assertIsNotNone(p.rush)

    def test_stopped_strategy_renders_unexecuted_B_and_S(self):
        import app
        rows = self._rows(6)
        # Separate synthetic signals prove that no order or RUNNING state is needed.
        b = ZBGEPoint(
            open_time=rows[2][0], close=rows[2][4], trend=14,
            absorption=22, yellow=True, smile=False, smile_count=0,
            follow_main=False, buy=True, sell_a=False, sell_b=False,
            cyan=12, red=22, gray=17,
        )
        s = ZBGEPoint(
            open_time=rows[3][0], close=rows[3][4], trend=90,
            absorption=10, yellow=False, smile=True, smile_count=3,
            follow_main=False, buy=False, sell_a=False, sell_b=True,
            pink=True, rush=10,
        )
        with (
            patch.object(app.store, "get_symbol_configs",
                         return_value={"BTCUSDT":{"strategy_id":"zbge_bs","timeframe":"4h"}}),
            patch.object(app.store, "get_runtime_states",
                         return_value={"BTCUSDT":{"run_state":"STOPPED", "current_fraction":0}}),
            patch.object(app.store, "list_trade_markers", return_value=[]),
            patch.object(app.testnet_session, "credentials", return_value=(None, None)),
            patch.object(app.probe, "klines", return_value=rows),
            patch.object(app, "evaluate_zbge", return_value=[b,s]) as evaluate,
            patch.object(app, "zbge_chart_snapshot", return_value={"trend":90}),
        ):
            data = app.chart_payload("BTCUSDT")
        self.assertEqual(data["runtime_state"], "STOPPED")
        self.assertEqual(data["markers"], [])  # no FILLED trades
        self.assertEqual(
            [x["kind"] for x in data["strategy_indicator_markers"]],
            ["ZBGE_BUY_B", "ZBGE_SELL_S"],
        )
        self.assertEqual([x["text"] for x in data["strategy_indicator_markers"]], ["B","S"])
        self.assertEqual(data["strategy_overlay"][0]["CYAN"], 12)
        self.assertEqual(data["strategy_overlay"][0]["RED"], 22)
        self.assertEqual(data["strategy_overlay"][1]["PINK"], None)
        self.assertEqual(data["strategy_overlay"][1]["SMILE"], True)
        # The current unfinished candle must not be analyzed.
        self.assertEqual(len(evaluate.call_args.args[0]), len(rows) - 1)

    def test_visual_template_renders_all_components_separately(self):
        base = Path(__file__).parents[1]
        page = (base / "templates/index.html").read_text(encoding="utf-8")
        app_source = (base / "app.py").read_text(encoding="utf-8")
        for key in ("CYAN","RED","GRAY","YELLOW","PINK","RUSH",
                    "FOLLOW","BULL","TREND","SMILE"):
            self.assertIn('"' + key + '"', app_source)
            self.assertIn(key, page)
        self.assertIn("ZBGE_BUY_B", page)
        self.assertIn("ZBGE_SELL_S", page)
        self.assertIn("strategy_indicator_markers", app_source)
        self.assertIn("未交易也显示", page)
        self.assertIn("setHeight(245)", page)


if __name__ == "__main__":
    unittest.main()
