# Pure SLTD V8 Probability-Map Candidate R2 — Result

Status: **COMPLETE**

Decision: **RESEARCH_ONLY_NOT_PROMOTED**

Fresh universe: **20 previously unused US stocks**.

## Equal-weight portfolio — 5 bps

| System | Return | CAGR | MaxDD | Calmar | Turnover mean | Exposure mean |
|---|---:|---:|---:|---:|---:|---:|
| V7_BASE | 42.95% | 5.44% | -20.85% | 0.261 | 5.71 | 89.39% |
| PMAP_14 | 50.03% | 6.20% | -21.28% | 0.291 | 10.77 | 91.76% |
| BUY_HOLD | 50.47% | 6.25% | -34.90% | 0.179 | 1.00 | 100.00% |
| SMA200_TREND | 11.20% | 1.59% | -17.67% | 0.090 | 68.23 | 58.29% |

## Breadth vs current V7 — 5 bps

- Better Total Return: **13/20**
- Better Calmar: **13/20**

## Fresh20 event sanity

- PM_BUY_1 events: **122**; 10d median 1.44%; 20d median 1.91%
- PM_SELL_1 events: **277**; 10d median 0.09%; 20d median 0.95%

## Admission gates

- portfolio_return_improves_vs_v7: **PASS**
- portfolio_calmar_improves_vs_v7: **PASS**
- portfolio_maxdd_not_worse_by_gt_1pp: **PASS**
- symbol_return_breadth_ge_11: **PASS**
- symbol_calmar_breadth_ge_11: **PASS**
- pm_buy_10d_positive: **PASS**
- pm_buy_20d_positive: **PASS**
- pm_sell_10d_nonpositive: **FAIL**
- pm_sell_20d_nonpositive: **FAIL**
- simple_baseline_guard: **PASS**

## Per-symbol 5 bps return

| Symbol | V7 | PMAP_14 | Delta | PM buy exec | PM sell exec |
|---|---:|---:|---:|---:|---:|
| AXP | 99.91% | 148.25% | 48.35% | 3 | 17 |
| PGR | 71.02% | 64.82% | -6.21% | 0 | 17 |
| CB | 48.93% | 53.76% | 4.83% | 2 | 24 |
| ICE | 67.23% | 72.31% | 5.08% | 1 | 14 |
| T | -14.50% | -13.28% | 1.22% | 1 | 14 |
| TMUS | 113.04% | 83.48% | -29.56% | 3 | 20 |
| CMCSA | -35.68% | -23.33% | 12.35% | 5 | 12 |
| CL | 23.38% | 23.83% | 0.45% | 4 | 10 |
| MDLZ | 0.75% | 4.32% | 3.57% | 3 | 2 |
| GIS | -34.66% | -51.56% | -16.90% | 4 | 12 |
| MMM | 19.21% | 2.03% | -17.18% | 0 | 14 |
| FDX | 70.70% | 156.91% | 86.21% | 4 | 14 |
| EMR | 104.96% | 104.74% | -0.21% | 0 | 14 |
| DUK | 13.63% | 14.76% | 1.13% | 0 | 8 |
| D | -15.01% | -24.32% | -9.31% | 3 | 11 |
| EXC | 34.34% | 46.50% | 12.16% | 1 | 13 |
| SLB | 10.93% | 42.44% | 31.52% | 2 | 12 |
| EOG | 86.23% | 88.15% | 1.92% | 0 | 17 |
| F | 94.20% | 128.73% | 34.53% | 4 | 7 |
| GM | 100.32% | 78.12% | -22.20% | 4 | 16 |

The existing V7 remains unchanged unless this result is explicitly promoted into engineering.

`PURE_SLTD_V8_PROBABILITY_MAP_R2 = RESEARCH_ONLY_NOT_PROMOTED`
