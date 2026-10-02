from __future__ import annotations

import unittest

from signal_preview import build_strategy_signal_markers
from strategy.frozen_signal_engine import BarEvaluation


def evaluation(open_time: int, *, buy=(), sell=()):
    return BarEvaluation(
        index=open_time,
        open_time=open_time,
        states={"trend":"GRAY","capital":"GRAY","momentum":"GRAY","accel":"GRAY","anomaly":"GRAY"},
        buy_active=tuple(buy),
        sell_active=tuple(sell),
        buy_onsets=tuple(buy),
        sell_onsets=tuple(sell),
        features={},
    )


def fake_evaluator(rows):
    out = []
    for row in rows:
        t = int(row[0])
        buy = ("A",) if t == 2 else ()
        sell = ("A",) if t == 5 else ()
        out.append(evaluation(t, buy=buy, sell=sell))
    return out


class SignalPreviewTests(unittest.TestCase):
    def test_theoretical_bs_markers_do_not_need_account_api(self):
        rows = [[i, 100, 101, 99, 100.5, 10] for i in range(1, 8)]
        rows.append([8, 100, 101, 99, 100.5, 10])  # forming row
        markers = build_strategy_signal_markers(rows, evaluator=fake_evaluator)
        self.assertEqual([(x["open_time"], x["side"]) for x in markers], [(2, "B"), (5, "S")])
        self.assertTrue(all(x["source"] == "STRATEGY_PREVIEW" for x in markers))


if __name__ == "__main__":
    unittest.main()
