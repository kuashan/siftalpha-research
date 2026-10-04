# SLTD Score Level -> Relative Ranking v1 — Stage A Result

Status: **PROMOTED_TO_ALLOCATION_TEST**

Chan/缠论: **NOT USED**
V7 as signal: **NOT USED**
Score Momentum: **NOT USED**
v4 probability calibration: **NOT USED**
Fresh OOS consumed: **NO**

## Core question

Does frozen SLTD LEVEL order relative future quality across stocks on the same date?

## Discovery

- Valid dates: **986**
- Valid observations: **77894**
- Mean daily cross-section: **79.00**
- Rank corr(RANK, XS_UTILITY): **0.04850**
- Q5-Q1 XS_UTILITY: **0.11351**
- Q5-Q1 XS_RET_10: **0.333%**
- Q5-Q1 XS_RET_20: **0.314%**
- Adjacent quintile utility increases: **2/4**
- Daily Q5>Q1 utility fraction: **59.73%**

| Bucket | Count | Median XS utility | XS ret 5d | XS ret 10d | XS ret 20d | XS MAE safety 10d | XS MAE safety 20d |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q1 | 16417 | -0.05518 | -0.039% | -0.220% | -0.176% | -0.044% | -0.055% |
| Q2 | 14402 | 0.00000 | 0.000% | 0.005% | 0.000% | 0.014% | 0.085% |
| Q3 | 16129 | 0.00000 | 0.000% | 0.015% | 0.000% | 0.000% | 0.000% |
| Q4 | 14996 | 0.00000 | 0.000% | 0.000% | 0.000% | 0.000% | -0.024% |
| Q5 | 15950 | 0.05833 | 0.019% | 0.114% | 0.139% | 0.000% | 0.036% |

## Temporal

- Valid dates: **669**
- Valid observations: **52851**
- Mean daily cross-section: **79.00**
- Rank corr(RANK, XS_UTILITY): **0.02418**
- Q5-Q1 XS_UTILITY: **0.02169**
- Q5-Q1 XS_RET_10: **0.067%**
- Q5-Q1 XS_RET_20: **0.272%**
- Adjacent quintile utility increases: **3/4**
- Daily Q5>Q1 utility fraction: **53.51%**

| Bucket | Count | Median XS utility | XS ret 5d | XS ret 10d | XS ret 20d | XS MAE safety 10d | XS MAE safety 20d |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q1 | 11221 | -0.01784 | 0.000% | -0.067% | -0.272% | -0.011% | -0.043% |
| Q2 | 10194 | -0.00891 | 0.000% | 0.000% | 0.000% | -0.009% | -0.016% |
| Q3 | 10685 | 0.00000 | 0.000% | 0.025% | 0.120% | 0.022% | 0.000% |
| Q4 | 9892 | 0.01930 | 0.036% | 0.073% | 0.093% | 0.099% | 0.153% |
| Q5 | 10859 | 0.00385 | 0.000% | 0.000% | 0.000% | -0.049% | -0.018% |

## Gates

- discovery_rank_corr_positive: **PASS**
- temporal_rank_corr_positive: **PASS**
- discovery_q5_q1_utility_positive: **PASS**
- temporal_q5_q1_utility_positive: **PASS**
- temporal_q5_q1_ret10_positive: **PASS**
- temporal_q5_q1_ret20_positive: **PASS**
- temporal_utility_monotonicity_3_of_4: **PASS**
- temporal_daily_q5_gt_q1_majority: **PASS**
- temporal_extreme_support: **PASS**

`SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_STAGE_A = PROMOTED_TO_ALLOCATION_TEST`
