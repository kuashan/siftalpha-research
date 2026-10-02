# SLTD V7 79-Stock Robustness Check v1

Status: **COMPLETE**

This is a robustness check on the already-used 79-stock universe, not fresh OOS.

## Full-window all-79 portfolio — 5 bps

| Variant | Return | CAGR | MaxDD | Calmar |
|---|---:|---:|---:|---:|
| BASELINE_ALL_15 | 153.45% | 14.79% | -18.30% | 0.808 |
| CANDIDATE_A_DROP_S1_S3 | 199.26% | 17.65% | -21.07% | 0.838 |
| CANDIDATE_B_DROP_B3_S1_S3 | 198.58% | 17.61% | -20.91% | 0.842 |

## Calendar-year total return — 5 bps

| Year | Baseline | Candidate A | Candidate B |
|---|---:|---:|---:|
| 2020 | 19.29% | 21.65% | 21.66% |
| 2021 | 22.95% | 25.34% | 25.17% |
| 2022 | -10.00% | -9.61% | -9.59% |
| 2023 | 16.41% | 20.01% | 19.96% |
| 2024 | 14.72% | 16.80% | 16.74% |
| 2025 | 10.16% | 14.34% | 14.29% |
| 2026 | 10.17% | 11.54% | 11.54% |

## Era Calmar — 5 bps

| Era | Baseline | Candidate A | Candidate B |
|---|---:|---:|---:|
| EARLY_2020_2021 | 1.333 | 1.475 | 1.490 |
| MIDDLE_2022_2023 | 0.067 | 0.144 | 0.145 |
| LATE_2024_2026Q3 | 1.072 | 1.175 | 1.173 |

## Breadth versus baseline — 5 bps

| Candidate | Symbols better return | Symbols better Calmar | Years better return | Eras better Calmar | Median symbol ΔReturn | Median symbol ΔCalmar |
|---|---:|---:|---:|---:|---:|---:|
| CANDIDATE_A_DROP_S1_S3 | 60/79 | 59/79 | 7/7 | 3/3 | 15.63% | +0.055 |
| CANDIDATE_B_DROP_B3_S1_S3 | 59/79 | 58/79 | 7/7 | 3/3 | 15.40% | +0.057 |

No baseline rule is changed by this run.

`SLTD_V7_79_STOCK_ROBUSTNESS_CHECK_V1 = COMPLETE`
