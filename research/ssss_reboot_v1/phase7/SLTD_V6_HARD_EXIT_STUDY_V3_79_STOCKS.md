# SLTD V6 Hard Exit Study v3 — C Confirmation — 79 Stocks

Status: **COMPLETE**

Ordinary policy fixed: `I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

## All-79 equal-weight portfolio — 5 bps

| Variant | Return | CAGR | MaxDD | Calmar | Turnover | Time in market | Hard exits |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASELINE | 190.06% | 17.11% | -24.56% | 0.697 | 6.19 | 98.12% | 0 |
| C0_IMMEDIATE | 152.34% | 14.71% | -18.24% | 0.806 | 9.30 | 80.57% | 330 |
| C1_ONE_BAR_NO_RECLAIM | 151.72% | 14.67% | -18.64% | 0.787 | 9.19 | 81.02% | 319 |
| C2_FULL_CANDLE_BELOW_SLOW_BAND | 153.45% | 14.79% | -18.30% | 0.808 | 9.09 | 81.42% | 305 |
| C3_FALLING_SLOW_BAND_CONFIRM | 152.34% | 14.71% | -18.24% | 0.806 | 9.30 | 80.57% | 330 |

## Batch-level comparison versus BASELINE — 5 bps

| Variant | Calmar improved | CAGR improved | MaxDD improved | Median Calmar | Median CAGR | Median MaxDD | Median 10bps Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0_IMMEDIATE | 3/8 | 1/8 | 6/8 | 0.409 | 7.96% | -21.91% | 0.405 |
| C1_ONE_BAR_NO_RECLAIM | 3/8 | 1/8 | 7/8 | 0.389 | 7.75% | -23.09% | 0.385 |
| C2_FULL_CANDLE_BELOW_SLOW_BAND | 3/8 | 1/8 | 6/8 | 0.405 | 7.85% | -21.94% | 0.401 |
| C3_FALLING_SLOW_BAND_CONFIRM | 3/8 | 1/8 | 6/8 | 0.409 | 7.96% | -21.91% | 0.405 |

## What happened after Hard Exit? — 5 bps event set

| Variant | Exits | +5d median | +5d positive | +10d median | +10d positive | +20d median | +20d positive |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0_IMMEDIATE | 330 | -0.19% | 49.54% | 0.15% | 51.53% | 0.82% | 54.18% |
| C1_ONE_BAR_NO_RECLAIM | 319 | 0.02% | 50.16% | 0.65% | 55.73% | 1.00% | 56.09% |
| C2_FULL_CANDLE_BELOW_SLOW_BAND | 305 | -0.27% | 48.68% | 0.27% | 52.16% | 0.83% | 54.36% |
| C3_FALLING_SLOW_BAND_CONFIRM | 330 | -0.19% | 49.54% | 0.15% | 51.53% | 0.82% | 54.18% |

Positive post-exit return means the stock had rebounded above the exit open by that horizon;
negative return means it was still below the exit open.

The C-family confirmation candidates were frozen before this run. No threshold was tuned after seeing results.

`SLTD_V6_HARD_EXIT_STUDY_V3 = COMPLETE`
