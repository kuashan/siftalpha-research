# SLTD State Score Regime Mode v2 — Result

Status: **COMPLETE**

Decision: **REJECTED_SCORE_REGIME_V2**

Standalone mode: **YES**
Uses V7 trade rules: **NO**
Uses V7 C2: **NO**
Uses Chan/缠论: **NO**

## Equal-weight Fresh30 portfolio — 5 bps

| System | Return | CAGR | MaxDD | Calmar | Turnover | Exposure |
|---|---:|---:|---:|---:|---:|---:|
| SCORE_REGIME_V2 | 81.82% | 9.27% | -21.11% | 0.439 | 8.43 | 42.14% |
| SCORE_EXPOSURE_V1 | 96.99% | 10.58% | -35.70% | 0.296 | 34.88 | 100.00% |
| V7_BASE | 126.14% | 12.86% | -17.01% | 0.756 | 5.21 | 88.62% |
| BUY_HOLD | 141.40% | 13.96% | -44.13% | 0.316 | 1.00 | 100.00% |
| SMA200_TREND | 43.15% | 5.46% | -15.81% | 0.345 | 61.85 | 61.95% |

## Fresh30 breadth — 5 bps

- Return > V7: **11/30**
- Calmar > V7: **13/30**
- Return > Buy & Hold: **14/30**

## Trigger diagnostics

- ENTRY_100: 10d excess 1.20%, 20d excess 2.16%
- EXIT_25: 10d excess -0.52%, 20d excess -0.96%

## Admission gates

- return_gt_score_exposure_v1_5bps: **FAIL**
- calmar_gt_score_exposure_v1_5bps: **PASS**
- turnover_lt_score_exposure_v1_5bps: **PASS**
- return_gt_v7_5bps: **FAIL**
- calmar_gt_v7_5bps: **FAIL**
- return_ge_buyhold_5bps: **FAIL**
- calmar_gt_buyhold_5bps: **PASS**
- maxdd_better_than_buyhold: **PASS**
- symbol_return_gt_v7_ge_16: **FAIL**
- symbol_return_gt_buyhold_ge_16: **FAIL**
- entry_100_excess_10_positive: **PASS**
- entry_100_excess_20_positive: **PASS**
- exit_25_excess_10_negative: **PASS**
- exit_25_excess_20_negative: **PASS**
- return_gt_v7_10bps: **FAIL**
- calmar_gt_v7_20bps: **FAIL**

This result governs only the standalone score-regime mode. Production V7 is unchanged.

SLTD_STATE_SCORE_REGIME_MODE_V2 = REJECTED_SCORE_REGIME_V2
