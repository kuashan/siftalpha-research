# SLTD Rank -> Long-Hold Allocation v1 — Stage A Result

Status: **REJECTED_NOT_ADMITTED**

Interpretation: ranking is used only at initial formation; positions are not rebalanced because rank changes.

Chan/缠论: **NOT USED**
V7 as signal: **NOT USED**
Score Momentum: **NOT USED**
v4 probability: **NOT USED**
Fresh OOS consumed: **NO**

- Symbols: **79**
- Monthly formation pairs available: **81**

## Aggregate cohort results — 5 bps

| Horizon | Segment | Cohorts | Median excess | Mean excess | Positive fraction | Median MaxDD diff | Median Calmar diff |
|---:|---|---:|---:|---:|---:|---:|---:|
| 126 | EARLY | 48 | 0.139% | 0.284% | 52.1% | -0.197% | -0.042 |
| 126 | LATE | 28 | -0.845% | -1.336% | 32.1% | 0.248% | -0.108 |
| 126 | ALL | 76 | -0.590% | -0.313% | 44.7% | -0.123% | -0.083 |
| 252 | EARLY | 48 | -0.043% | 0.213% | 47.9% | -0.478% | 0.011 |
| 252 | LATE | 21 | 0.497% | -0.454% | 52.4% | 0.367% | 0.033 |
| 252 | ALL | 69 | -0.009% | 0.010% | 49.3% | -0.118% | 0.014 |
| 504 | EARLY | 48 | 1.596% | 0.750% | 60.4% | 0.192% | 0.023 |
| 504 | LATE | 9 | -6.433% | -2.435% | 22.2% | 0.601% | -0.101 |
| 504 | ALL | 57 | 0.353% | 0.247% | 54.4% | 0.310% | 0.017 |

## Full-window static diagnostic — 5 bps

- RANK_STATIC: Return **244.11%**, CAGR **20.11%**, MaxDD **-32.80%**, Calmar **0.613**
- EQUAL_STATIC: Return **235.14%**, CAGR **19.64%**, MaxDD **-33.95%**, Calmar **0.579**
- Rank minus Equal full-window return: **8.97%**

## Gates

- early_252_median_excess_positive: **FAIL**
- late_252_median_excess_positive: **PASS**
- early_252_positive_fraction_gt_50: **FAIL**
- late_252_positive_fraction_gt_50: **PASS**
- late_252_median_calmar_difference_positive: **PASS**
- late_252_median_maxdd_difference_ge_minus_1pp: **PASS**
- late_126_median_excess_positive: **FAIL**
- late_252_20bps_median_excess_positive: **PASS**

`SLTD_RANK_LONG_HOLD_ALLOCATION_V1_STAGE_A = REJECTED_NOT_ADMITTED`
