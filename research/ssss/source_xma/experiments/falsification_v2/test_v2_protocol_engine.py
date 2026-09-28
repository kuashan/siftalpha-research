#!/usr/bin/env python3
from __future__ import annotations

import unittest
import numpy as np
import pandas as pd

from v2_protocol_engine import (
    benjamini_hochberg,
    build_continuous_state_runs,
    build_debounced_episodes,
    design_effect_ess,
    guard_pass,
    market_wave_ids,
    pair_f5_a_to_b,
)


class EpisodeTests(unittest.TestCase):
    def test_debounce_gap_rule(self) -> None:
        dates = pd.bdate_range("2025-01-02", periods=8)
        qualifying = [1, 0, 1, 0, 0, 1, 0, 1]
        arm = ["A"] * 8
        eps = build_debounced_episodes("X", dates, qualifying, arm)
        # q idx: 0,2 => same episode (gap=2); 5,7 => same second episode.
        self.assertEqual(len(eps), 2)
        self.assertEqual((eps[0].anchor_idx, eps[0].last_qualifying_idx), (0,2))
        self.assertEqual((eps[1].anchor_idx, eps[1].last_qualifying_idx), (5,7))

    def test_f1_continuous_state_runs_do_not_bridge_interruptions(self) -> None:
        dates = pd.bdate_range("2025-01-02", periods=6)
        states = ["DOWN_STATE","DOWN_STATE","RANGE","DOWN_STATE","UP_STATE","UP_STATE"]
        eps = build_continuous_state_runs("X", dates, states)
        self.assertEqual([e.arm for e in eps], ["DOWN_STATE","DOWN_STATE","UP_STATE"])
        self.assertEqual([e.anchor_idx for e in eps], [0,3,4])


class WaveTests(unittest.TestCase):
    def test_exact_session_distance(self) -> None:
        wave = market_wave_ids([10,12,15,16,30], max_gap_sessions=2)
        self.assertEqual(wave.tolist(), [1,1,2,2,3])


class ESSTests(unittest.TestCase):
    def test_independent_clusters_deff_not_below_one(self) -> None:
        y = [0,1,0,1,0,1,0,1]
        g = [1,1,2,2,3,3,4,4]
        r = design_effect_ess(y,g)
        self.assertGreaterEqual(r["deff"], 1.0)
        self.assertLessEqual(r["ess"], r["n"])


class FDRTests(unittest.TestCase):
    def test_bh_known_case(self) -> None:
        q = benjamini_hochberg([0.01,0.04,1.0,0.02])
        self.assertTrue(np.all((q >= 0) & (q <= 1)))
        self.assertAlmostEqual(float(q[0]), 0.04, places=12)
        self.assertAlmostEqual(float(q[3]), 0.04, places=12)
        self.assertAlmostEqual(float(q[2]), 1.0, places=12)


class F5PairingTests(unittest.TestCase):
    def test_deterministic_same_quarter_session_pairing_without_reuse(self) -> None:
        a = pd.DataFrame([
            {"event_id":"A1","symbol":"X","date":"2025-01-10","session_idx":10},
            {"event_id":"A2","symbol":"X","date":"2025-01-20","session_idx":16},
        ])
        b = pd.DataFrame([
            {"event_id":"B1","symbol":"X","date":"2025-01-09","session_idx":9},
            {"event_id":"B2","symbol":"X","date":"2025-01-21","session_idx":17},
        ])
        p = pair_f5_a_to_b(a,b)
        self.assertEqual(p["b_event_id"].tolist(), ["B1","B2"])
        self.assertEqual(p["status"].tolist(), ["MATCHED","MATCHED"])


class GuardTests(unittest.TestCase):
    def test_guard_gate(self) -> None:
        self.assertEqual(guard_pass(0.1,0.5,True), "PASS")
        self.assertEqual(guard_pass(0.5,0.5,True), "FAIL")
        self.assertEqual(guard_pass(0.0,0.5,False), "INSUFFICIENT")


if __name__ == "__main__":
    unittest.main()
