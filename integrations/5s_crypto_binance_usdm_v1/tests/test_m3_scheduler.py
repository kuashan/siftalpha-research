from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from engine.scheduler import BAR_CLOSE_CONTRACT, StrategyScheduler, decide_actions
from storage import StateStore
from strategy.frozen_signal_engine import BarEvaluation


def evaluation(open_time: int, *, buy=(), sell=()):
    return BarEvaluation(
        index=100,
        open_time=open_time,
        states={"trend": "GRAY", "capital": "GRAY", "momentum": "GRAY", "accel": "GRAY", "anomaly": "GRAY"},
        buy_active=tuple(buy),
        sell_active=tuple(sell),
        buy_onsets=tuple(buy),
        sell_onsets=tuple(sell),
        features={},
    )


class FakeSession:
    def __init__(self, key="k", secret="s"):
        self.key = key
        self.secret = secret

    def credentials(self):
        return self.key, self.secret


class FakeAdapter:
    calls = []
    generation = 0

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def klines(self, symbol, timeframe, limit):
        FakeAdapter.calls.append((symbol, timeframe, limit))
        base = 100 if symbol == "BTCUSDT" else 200
        rows = []
        for i in range(90):
            t = i + FakeAdapter.generation
            rows.append([t, base, base + 1, base - 1, base + 0.5, 1000])
        rows.append([90 + FakeAdapter.generation, base, base + 1, base - 1, base + 0.5, 1000])
        return rows


def fake_evaluator(rows):
    marker = int(float(rows[-1][1]))
    buy = ("A",) if marker == 100 else ()
    return [
        evaluation(int(r[0]), buy=buy if i == len(rows) - 1 else ())
        for i, r in enumerate(rows)
    ]


class SchedulerDecisionTests(unittest.TestCase):
    def test_flat_a_signal_targets_60(self):
        d = decide_actions(
            {"current_fraction": 0, "c_confirmed": 0},
            evaluation(10, buy=("A",)),
            [1, 2, 10],
        )
        self.assertEqual(d.signal, "BUY_A")
        self.assertEqual(d.actions, ("BUY_60",))

    def test_sell_is_full_for_any_family(self):
        d = decide_actions(
            {"current_fraction": 0.6, "c_confirmed": 0},
            evaluation(10, sell=("C",)),
            [1, 2, 10],
        )
        self.assertEqual(d.actions, ("SELL_ALL",))
        self.assertEqual(d.signal, "SELL_C")

    def test_c_topup_requires_w3(self):
        runtime = {"current_fraction": 0.6, "c_confirmed": 0, "entry_signal_open_time": 20}
        d = decide_actions(runtime, evaluation(23, buy=("C",)), [20, 21, 22, 23])
        self.assertEqual(d.actions, ("TOPUP_TO_100",))
        self.assertTrue(d.c_eligible)
        d2 = decide_actions(runtime, evaluation(24, buy=("C",)), [20, 21, 22, 23, 24])
        self.assertEqual(d2.actions, ())

    def test_c_then_sell_preserves_frozen_order(self):
        runtime = {"current_fraction": 0.6, "c_confirmed": 0, "entry_signal_open_time": 20}
        d = decide_actions(runtime, evaluation(22, buy=("C",), sell=("A",)), [20, 21, 22])
        self.assertEqual(d.actions, ("TOPUP_TO_100", "SELL_ALL"))


class SchedulerLoopTests(unittest.TestCase):
    def setUp(self):
        FakeAdapter.calls = []
        FakeAdapter.generation = 0
        self.tmp = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.tmp.name) / "state.db")
        self.symbols = ("BTCUSDT", "ETHUSDT")
        self.store.seed(self.symbols, 1, 1000, "1d")
        self.store.set_symbol_config("BTCUSDT", capital_budget_usdt=100, leverage=2, timeframe="15m")
        self.store.set_symbol_config("ETHUSDT", capital_budget_usdt=200, leverage=3, timeframe="1h")
        self.store.set_symbol_enabled("BTCUSDT", True)
        self.store.set_symbol_enabled("ETHUSDT", True)

    def tearDown(self):
        self.tmp.cleanup()

    def scheduler(self, session=None):
        return StrategyScheduler(
            store=self.store,
            session=session or FakeSession(),
            symbols=self.symbols,
            allowed_timeframes=("15m", "1h", "1d"),
            adapter_factory=FakeAdapter,
            evaluator=fake_evaluator,
            minimum_closed_bars=64,
        )

    def test_forming_bar_is_never_part_of_confirmed_signal_window(self):
        rows = [[1, 100], [2, 101], [3, 102]]
        self.assertEqual(StrategyScheduler._closed_rows(rows), rows[:-1])
        self.assertEqual(BAR_CLOSE_CONTRACT, "SELECTED_TIMEFRAME_BAR_CLOSE_TO_NEXT_SELECTED_BAR_OPEN")

    def test_each_enabled_slot_uses_its_own_timeframe_and_bootstraps(self):
        out = self.scheduler().run_once()
        self.assertEqual([x[:2] for x in FakeAdapter.calls], [
            ("BTCUSDT", "15m"),
            ("ETHUSDT", "1h"),
        ])
        self.assertEqual(out["BTCUSDT"]["state"], "MONITORING")
        self.assertEqual(out["ETHUSDT"]["state"], "MONITORING")

    def test_new_bar_is_processed_once_per_symbol(self):
        s = self.scheduler()
        s.run_once()
        FakeAdapter.generation = 1
        out = s.run_once()
        self.assertEqual(out["BTCUSDT"]["actions"], ["BUY_60"])
        self.assertEqual(out["ETHUSDT"]["actions"], [])
        rt = self.store.get_runtime_states()
        self.assertEqual(rt["BTCUSDT"]["pending_action"], "BUY_60")
        self.assertEqual(rt["BTCUSDT"]["last_signal"], "BUY_A")
        again = s.run_once()
        self.assertFalse(again["BTCUSDT"]["new_bar"])

    def test_missing_demo_credentials_waits_without_crashing(self):
        out = self.scheduler(FakeSession("", "")).run_once()
        self.assertEqual(out["BTCUSDT"]["state"], "WAITING_DEMO")
        self.assertEqual(out["ETHUSDT"]["state"], "WAITING_DEMO")


if __name__ == "__main__":
    unittest.main()
