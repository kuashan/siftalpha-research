# SLTD Relative Ranking v1 — Stage B Result

Status: **REJECTED_NOT_ADMITTED**

Development-only: **YES**
Fresh OOS consumed: **NO**
Chan/缠论: **NOT USED**
V7 as signal: **NOT USED**
Score Momentum: **NOT USED**
v4 probability: **NOT USED**

- Symbols: **79**
- Synchronized trading days: **1695**
- 5bps annual wins vs Equal Weight Daily: **4/7**

## 5bps

| System | Total Return | CAGR | MaxDD | Calmar | Turnover | Rebalances | Daily p1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| SLTD_RANK_LINEAR | 186.04% | 16.87% | -35.27% | 0.478 | 281.72 | 1695 | -3.60% |
| EQUAL_WEIGHT_DAILY | 182.41% | 16.64% | -34.17% | 0.487 | 21.75 | 1695 | -3.57% |
| EQUAL_WEIGHT_BUY_HOLD | 235.14% | 19.64% | -33.95% | 0.579 | 1.00 | 1 | -3.96% |
| V7_BASE | 198.58% | 17.61% | -20.91% | 0.842 | 5.69 mean | — | — |
| SMA200_TREND | 116.80% | 12.16% | -17.15% | 0.709 | 57.88 mean | — | — |

## 10bps

| System | Total Return | CAGR | MaxDD | Calmar | Turnover | Rebalances | Daily p1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| SLTD_RANK_LINEAR | 148.45% | 14.45% | -35.42% | 0.408 | 281.72 | 1695 | -3.61% |
| EQUAL_WEIGHT_DAILY | 179.36% | 16.46% | -34.19% | 0.481 | 21.75 | 1695 | -3.57% |
| EQUAL_WEIGHT_BUY_HOLD | 234.97% | 19.63% | -33.95% | 0.578 | 1.00 | 1 | -3.96% |
| V7_BASE | 197.82% | 17.57% | -20.94% | 0.839 | 5.69 mean | — | — |
| SMA200_TREND | 111.69% | 11.76% | -17.50% | 0.672 | 57.87 mean | — | — |

## 20bps

| System | Total Return | CAGR | MaxDD | Calmar | Turnover | Rebalances | Daily p1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| SLTD_RANK_LINEAR | 87.44% | 9.76% | -35.71% | 0.273 | 281.72 | 1695 | -3.63% |
| EQUAL_WEIGHT_DAILY | 173.35% | 16.08% | -34.22% | 0.470 | 21.75 | 1695 | -3.57% |
| EQUAL_WEIGHT_BUY_HOLD | 234.64% | 19.62% | -33.95% | 0.578 | 1.00 | 1 | -3.96% |
| V7_BASE | 196.29% | 17.48% | -21.00% | 0.832 | 5.69 mean | — | — |
| SMA200_TREND | 101.86% | 10.98% | -18.43% | 0.596 | 57.84 mean | — | — |

## 5bps annual returns

| Year | Rank Linear | Equal Weight Daily | Beat? |
|---|---:|---:|---|
| 2020 | 27.83% | 28.33% | NO |
| 2021 | 32.13% | 30.24% | YES |
| 2022 | -13.34% | -14.62% | YES |
| 2023 | 26.96% | 26.81% | YES |
| 2024 | 15.23% | 17.82% | NO |
| 2025 | 21.54% | 18.77% | YES |
| 2026 | 9.91% | 11.52% | NO |

## Gates

- return_gt_equal_daily_5bps: **PASS**
- calmar_gt_equal_daily_5bps: **FAIL**
- return_gt_equal_buyhold_5bps: **FAIL**
- calmar_gt_equal_buyhold_5bps: **FAIL**
- maxdd_no_worse_than_equal_buyhold_5bps: **FAIL**
- return_gt_equal_daily_10bps: **FAIL**
- calmar_gt_equal_daily_20bps: **FAIL**
- annual_beats_equal_daily_ge_4_of_7: **PASS**
- daily_p1_no_worse_than_equal_buyhold_5bps: **PASS**

`SLTD_RELATIVE_RANKING_V1_STAGE_B = REJECTED_NOT_ADMITTED`
