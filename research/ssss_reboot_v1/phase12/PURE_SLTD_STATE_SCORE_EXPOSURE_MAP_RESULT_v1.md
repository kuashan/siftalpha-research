# Pure SLTD State Score -> Exposure Map v1 — Result

Status: **COMPLETE**

Decision: **REJECTED_NOT_ADMITTED**

Chan/缠论: **NOT USED**

## Frozen calibration

- Positive scale: **0.012623**
- Negative scale: **0.004775**
- Calibration nonzero states: **40907**

## Equal-weight Fresh24 portfolio — 5 bps

| System | Return | CAGR | MaxDD | Calmar | Turnover mean | Invested bars |
|---|---:|---:|---:|---:|---:|---:|
| SCORE_EXPOSURE | 63.12% | 7.53% | -28.39% | 0.265 | 33.63 | 100.00% |
| V7_BASE | 77.26% | 8.86% | -16.42% | 0.540 | 5.23 | 87.84% |
| FIXED_75_LONG | 58.08% | 7.03% | -27.35% | 0.257 | 0.75 | 100.00% |
| BUY_HOLD | 77.36% | 8.87% | -36.24% | 0.245 | 1.00 | 100.00% |
| SMA200_TREND | 46.82% | 5.86% | -10.75% | 0.545 | 60.90 | 60.55% |

## Fresh24 state buckets

| Target | Count | Stocks | 10d excess | 20d excess |
|---:|---:|---:|---:|---:|
| 25% | 8033 | 24 | -0.17% | -0.53% |
| 50% | 5367 | 24 | -0.15% | -0.33% |
| 75% | 19374 | 24 | -0.10% | -0.18% |
| 100% | 7426 | 24 | 1.06% | 1.97% |

## Gates

- calmar_gt_v7_5bps: **FAIL**
- calmar_gt_fixed75_5bps: **PASS**
- return_gt_fixed75_5bps: **PASS**
- return_ge_95pct_v7_5bps: **FAIL**
- maxdd_not_worse_v7_5bps: **FAIL**
- calmar_breadth_ge_13: **PASS**
- calmar_gt_v7_10bps: **FAIL**
- return_ge_95pct_v7_10bps: **FAIL**
- low_bucket_support: **PASS**
- high_bucket_support: **PASS**
- high_10d_positive: **PASS**
- high_20d_positive: **PASS**
- low_10d_negative: **PASS**
- low_20d_negative: **PASS**
- high_gt_low_10d: **PASS**
- high_gt_low_20d: **PASS**

No production V7 rule is changed by this run.

PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_V1 = REJECTED_NOT_ADMITTED
