# Pure SLTD V8 Probability-Map Candidate R3 — Result

Status: **COMPLETE**

Decision: **REJECTED_NOT_ADMITTED**

## Equal-weight portfolio — 5 bps

| System | Return | CAGR | MaxDD | Calmar | Turnover | Exposure |
|---|---:|---:|---:|---:|---:|---:|
| V7_BASE | 70.89% | 8.27% | -18.82% | 0.439 | 7.17 | 86.52% |
| PMAP_14 | 68.06% | 8.00% | -17.49% | 0.457 | 12.06 | 89.92% |
| BUY_HOLD | 93.72% | 10.30% | -40.16% | 0.257 | 1.00 | 100.00% |
| SMA200_TREND | 16.75% | 2.32% | -15.23% | 0.153 | 73.38 | 61.30% |

## Breadth

- Return better than V7: **12/20**
- Calmar better than V7: **15/20**

## Drift-adjusted event validation

- PM_BUY_1: n=86, symbols=20, 10d excess=1.20%, breadth=70.00%; 20d excess=0.36%, breadth=55.00%
- PM_SELL_1: n=276, symbols=20, 10d excess=0.37%, negative breadth=30.00%; 20d excess=-1.11%, negative breadth=60.00%

## Gates

- portfolio_5bps_return_gt_v7: **FAIL**
- portfolio_5bps_calmar_gt_v7: **PASS**
- portfolio_5bps_maxdd_not_worse_gt_1pp: **PASS**
- symbol_return_breadth_ge_11: **PASS**
- symbol_calmar_breadth_ge_11: **PASS**
- portfolio_10bps_return_gt_v7: **FAIL**
- portfolio_10bps_calmar_gt_v7: **PASS**
- buy_support: **PASS**
- buy_excess_10_positive: **PASS**
- buy_excess_20_positive: **PASS**
- buy_breadth_10_ge_60: **PASS**
- buy_breadth_20_ge_60: **FAIL**
- sell_support: **PASS**
- sell_excess_10_negative: **FAIL**
- sell_excess_20_negative: **PASS**
- sell_breadth_10_ge_60: **FAIL**
- sell_breadth_20_ge_60: **PASS**
- simple_baseline_guard: **PASS**

Existing V7 remains unchanged unless R3 is promoted and separately engineered.

PURE_SLTD_V8_PROBABILITY_MAP_R3 = REJECTED_NOT_ADMITTED
