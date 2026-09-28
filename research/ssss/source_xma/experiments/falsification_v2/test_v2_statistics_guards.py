#!/usr/bin/env python3
from __future__ import annotations

import unittest
import numpy as np
import pandas as pd

from v2_guards import (
    SEEDS,
    deterministic_rejection_permutation,
    guard_f3_sector_rs,
    guard_f5_riskoff_dates,
)
from v2_statistics import (
    km_median_wait,
    partial_spearman,
    rank_biserial_from_binary,
    residualize,
)


class GuardTests(unittest.TestCase):
    def test_f3_permutation_is_deterministic_and_group_local(self) -> None:
        df = pd.DataFrame({
            "date":["2025-01-02"]*4 + ["2025-01-03"]*4,
            "xma_state":["UP_STATE"]*8,
            "sector_rs":[1.,2.,3.,4.,5.,6.,7.,8.],
        })
        a = guard_f3_sector_rs(df)
        b = guard_f3_sector_rs(df)
        self.assertTrue(a.equals(b))
        self.assertEqual(sorted(a.iloc[:4].tolist()), [1.,2.,3.,4.])
        self.assertEqual(sorted(a.iloc[4:].tolist()), [5.,6.,7.,8.])

    def test_f5_date_labels_stay_market_wide(self) -> None:
        df = pd.DataFrame({
            "date":["2025-01-02"]*2+["2025-01-03"]*2+["2025-01-06"]*2,
            "symbol":["A","B"]*3,
            "risk_off":[True,True,False,False,True,True],
        })
        out = guard_f5_riskoff_dates(df)
        by_date = pd.DataFrame({"date":df["date"],"v":out}).groupby("date")["v"].nunique()
        self.assertTrue((by_date == 1).all())

    def test_rejection_sampling_uses_one_seed_stream(self) -> None:
        vals=np.array([0,1,2,3])
        accepted, attempts = deterministic_rejection_permutation(
            vals, SEEDS["G-F1"], lambda x: x[0] == 2
        )
        self.assertEqual(int(accepted[0]),2)
        self.assertGreaterEqual(attempts,1)


class StatisticsTests(unittest.TestCase):
    def test_km_median(self) -> None:
        times=np.array([1,2,2,4,4,4])
        obs=np.array([1,1,1,1,1,1],dtype=bool)
        self.assertEqual(km_median_wait(times,obs,20),2.0)

    def test_rank_biserial_positive(self) -> None:
        g=np.array([0,0,1,1],dtype=bool)
        y=np.array([1.,2.,3.,4.])
        self.assertGreater(rank_biserial_from_binary(g,y),0)

    def test_partial_spearman_finite(self) -> None:
        x=np.array([1.,2.,3.,4.,5.,6.])
        y=np.array([1.,2.,2.5,4.,5.2,5.8])
        controls=np.column_stack([np.array([3.,1.,4.,2.,6.,5.])])
        r=partial_spearman(x,y,controls)
        self.assertTrue(np.isfinite(r))

    def test_residualize_rejects_rank_deficiency(self) -> None:
        y=np.array([1.,2.,3.,4.])
        x=np.column_stack([np.ones(4)])
        with self.assertRaisesRegex(ValueError,"CONTROL_MATRIX_RANK_DEFICIENT"):
            residualize(y,x)


if __name__ == "__main__":
    unittest.main()
