# SLTD V6 Hard Exit Study v1 — 79 Stocks

Status: **COMPLETE**

Ordinary policy held fixed: `I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

Hard Exit executes at the next available open and overrides ordinary actions.

## 5 bps — all 79 equal-weight portfolio

| Variant | Return | CAGR | MaxDD | Calmar | Turnover | Time in market | Hard exits |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASELINE | 190.06% | 17.11% | -24.56% | 0.697 | 6.19 | 98.12% | 0 |
| H1_GREEN_LOWER_FULL_BELOW | 167.86% | 15.73% | -23.34% | 0.674 | 7.10 | 93.32% | 73 |
| H2_GREEN_TWO_CLOSES_BELOW_ZD1 | 72.04% | 8.38% | -15.52% | 0.540 | 12.16 | 62.61% | 557 |
| H3_H1_OR_H2 | 72.24% | 8.40% | -15.41% | 0.545 | 12.16 | 62.57% | 558 |

## 5 bps — batch Calmar

| Variant | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | Median |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASELINE | 0.935 | 0.360 | 0.573 | 0.659 | 0.123 | 0.567 | 0.490 | 0.323 | 0.528 |
| H1_GREEN_LOWER_FULL_BELOW | 0.937 | 0.341 | 0.488 | 0.602 | 0.146 | 0.547 | 0.492 | 0.276 | 0.490 |
| H2_GREEN_TWO_CLOSES_BELOW_ZD1 | 1.077 | 0.191 | 0.166 | 0.305 | 0.044 | 0.058 | 0.524 | 0.029 | 0.179 |
| H3_H1_OR_H2 | 1.076 | 0.193 | 0.166 | 0.311 | 0.053 | 0.065 | 0.523 | 0.028 | 0.180 |

## 5 bps — batch CAGR

| Variant | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | Median |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASELINE | 38.66% | 12.02% | 10.94% | 13.29% | 4.09% | 8.94% | 17.10% | 7.35% | 11.48% |
| H1_GREEN_LOWER_FULL_BELOW | 36.66% | 10.44% | 9.34% | 11.01% | 4.32% | 7.87% | 16.64% | 6.44% | 9.89% |
| H2_GREEN_TWO_CLOSES_BELOW_ZD1 | 25.03% | 5.47% | 1.97% | 4.56% | 1.04% | 0.97% | 11.69% | 0.66% | 3.27% |
| H3_H1_OR_H2 | 24.99% | 5.52% | 1.98% | 4.62% | 1.18% | 1.09% | 11.69% | 0.62% | 3.30% |

## 5 bps — batch MaxDD

| Variant | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | Median |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASELINE | -41.32% | -33.42% | -19.11% | -20.17% | -33.18% | -15.77% | -34.91% | -22.74% | -27.96% |
| H1_GREEN_LOWER_FULL_BELOW | -39.11% | -30.59% | -19.11% | -18.29% | -29.61% | -14.39% | -33.84% | -23.32% | -26.46% |
| H2_GREEN_TWO_CLOSES_BELOW_ZD1 | -23.23% | -28.58% | -11.89% | -14.97% | -23.60% | -16.63% | -22.33% | -22.50% | -22.42% |
| H3_H1_OR_H2 | -23.23% | -28.58% | -11.89% | -14.82% | -22.44% | -16.75% | -22.33% | -22.50% | -22.39% |

## Comparison versus BASELINE

| Hard Exit | Calmar improved batches | CAGR improved batches | MaxDD improved batches | Median Calmar | Median CAGR | Median MaxDD | Median 10bps Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|
| H1_GREEN_LOWER_FULL_BELOW | 3/8 | 1/8 | 6/8 | 0.490 | 9.89% | -26.46% | 0.487 |
| H2_GREEN_TWO_CLOSES_BELOW_ZD1 | 2/8 | 0/8 | 7/8 | 0.179 | 3.27% | -22.42% | 0.172 |
| H3_H1_OR_H2 | 2/8 | 0/8 | 7/8 | 0.180 | 3.30% | -22.39% | 0.173 |

This is a fixed-hypothesis comparison. No Hard Exit threshold was tuned after seeing results.

`SLTD_V6_HARD_EXIT_STUDY_V1 = COMPLETE`
