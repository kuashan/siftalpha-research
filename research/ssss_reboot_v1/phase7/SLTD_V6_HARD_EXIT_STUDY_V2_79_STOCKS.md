# SLTD V6 Hard Exit Study v2 — 79 Stocks

Status: **COMPLETE**

Ordinary policy fixed: `I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

## All-79 equal-weight portfolio — 5 bps

| Variant | Return | CAGR | MaxDD | Calmar | Turnover | Time in market | Hard exits |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASELINE | 190.06% | 17.11% | -24.56% | 0.697 | 6.19 | 98.12% | 0 |
| A_SELL_ARMED_THEN_GREEN_FULL_BELOW | 183.10% | 16.69% | -23.94% | 0.697 | 6.47 | 95.95% | 31 |
| B_GREEN_FULL_BELOW_THEN_NO_RECLAIM | 171.34% | 15.95% | -23.45% | 0.680 | 6.95 | 93.97% | 62 |
| C_SELL_ARMED_GREEN_CLOSE_BELOW_SLOW_BAND | 152.34% | 14.71% | -18.24% | 0.806 | 9.30 | 80.57% | 330 |
| D_SELL_ARMED_GREEN_ZD1_MINUS_1ATR | 170.03% | 15.87% | -22.24% | 0.714 | 7.50 | 88.84% | 135 |

## Batch-level comparison versus BASELINE — 5 bps

| Variant | Calmar improved | CAGR improved | MaxDD improved | Median Calmar | Median CAGR | Median MaxDD | Median 10bps Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|
| A_SELL_ARMED_THEN_GREEN_FULL_BELOW | 3/8 | 1/8 | 5/8 | 0.487 | 10.77% | -25.79% | 0.483 |
| B_GREEN_FULL_BELOW_THEN_NO_RECLAIM | 4/8 | 1/8 | 6/8 | 0.494 | 10.08% | -26.53% | 0.492 |
| C_SELL_ARMED_GREEN_CLOSE_BELOW_SLOW_BAND | 3/8 | 1/8 | 6/8 | 0.409 | 7.96% | -21.91% | 0.405 |
| D_SELL_ARMED_GREEN_ZD1_MINUS_1ATR | 4/8 | 1/8 | 7/8 | 0.421 | 9.10% | -25.02% | 0.418 |

## What happened after Hard Exit? — 5 bps event set

| Variant | Exits | +5d median | +5d positive | +10d median | +10d positive | +20d median | +20d positive |
|---|---:|---:|---:|---:|---:|---:|---:|
| A_SELL_ARMED_THEN_GREEN_FULL_BELOW | 31 | 2.31% | 77.42% | 2.43% | 67.74% | 3.99% | 80.65% |
| B_GREEN_FULL_BELOW_THEN_NO_RECLAIM | 62 | 1.15% | 66.13% | 1.70% | 62.90% | 3.36% | 60.66% |
| C_SELL_ARMED_GREEN_CLOSE_BELOW_SLOW_BAND | 330 | -0.19% | 49.54% | 0.15% | 51.53% | 0.82% | 54.18% |
| D_SELL_ARMED_GREEN_ZD1_MINUS_1ATR | 135 | 1.63% | 63.70% | 1.44% | 61.65% | 2.60% | 64.12% |

Positive post-exit return means the stock had rebounded above the exit open by that horizon;
negative return means it was still below the exit open.

The four candidates were frozen before this run. No threshold was tuned after seeing results.

`SLTD_V6_HARD_EXIT_STUDY_V2 = COMPLETE`
