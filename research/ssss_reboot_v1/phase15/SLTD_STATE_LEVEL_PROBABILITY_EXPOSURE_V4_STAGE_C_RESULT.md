# SLTD State Level -> Probability Exposure v4 — Stage C Result

Status: **REJECTED_NOT_ADMITTED**

Momentum: **NOT USED**
Chan/缠论: **NOT USED**
Fresh OOS consumed: **NO**

## Discovery calibration

- Stable states: **82**
- Discovery labeled rows: **77894**
- Discovery favorable rate: **51.50%**
- Isotonic pooled blocks / knots: **14**

## Temporal validation

- Temporal rows: **52851**
- Constant-probability Brier: **0.249738**
- Isotonic Brier: **0.250434**
- Relative Brier improvement: **-0.279%**
- Rank corr(probability, forward utility): **0.03653**
- Mean target exposure: **50.10%**

## Target buckets

| Target | Count | Mean calibrated p | Favorable rate | Median forward utility |
|---:|---:|---:|---:|---:|
| 50% | 52650 | 51.48% | 51.60% | 0.07224 |
| 75% | 201 | 62.69% | 58.21% | 0.30598 |

## Gates

- temporal_brier_improves: **FAIL**
- temporal_probability_utility_rank_corr_positive: **PASS**
- highest_bucket_utility_gt_lowest: **PASS**
- at_least_three_buckets_used: **FAIL**
- extreme_bucket_support: **FAIL**

Temporal is validation/consistency only; it is not the final independent Fresh OOS.

`SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4_STAGE_C = REJECTED_NOT_ADMITTED`
