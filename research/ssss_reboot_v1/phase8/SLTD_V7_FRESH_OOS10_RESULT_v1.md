# SLTD V7 Fresh 10-Stock OOS Validation v1

Status: **COMPLETE**

Research status: **FRESH STOCK OOS**

Frozen universe: **WFC, LMT, PM, ADP, WM, UNP, SO, VZ, PANW, CVS**

No symbol overlaps the prior 79-stock universe.

## Equal-weight 10-stock portfolio — 5 bps

| System | Return | CAGR | MaxDD | Calmar | Turnover | C2 exits |
|---|---:|---:|---:|---:|---:|---:|
| BASELINE_ALL_15 | 64.43% | 7.65% | -16.34% | 0.468 | 11.18 | 47 |
| CANDIDATE_A_DROP_S1_S3 | 85.92% | 9.63% | -16.43% | 0.586 | 7.07 | 25 |
| CANDIDATE_B_DROP_B3_S1_S3 | 87.73% | 9.79% | -16.43% | 0.596 | 7.11 | 26 |

## Breadth vs baseline — 5 bps

| Candidate | Better return | Better CAGR | Better MaxDD | Better Calmar | Median ΔReturn | Median ΔCAGR | Median ΔMaxDD | Median ΔCalmar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CANDIDATE_A_DROP_S1_S3 | 7/10 | 7/10 | 5/10 | 7/10 | 9.54% | 1.24% | -0.24% | +0.043 |
| CANDIDATE_B_DROP_B3_S1_S3 | 7/10 | 7/10 | 5/10 | 7/10 | 11.85% | 1.77% | 0.42% | +0.071 |

## Per-symbol 5 bps total return / Calmar

| Symbol | Baseline Return | A Return | B Return | Baseline Calmar | A Calmar | B Calmar |
|---|---:|---:|---:|---:|---:|---:|
| WFC | -16.06% | -12.36% | -12.36% | -0.056 | -0.041 | -0.041 |
| LMT | -36.15% | 4.60% | 3.64% | -0.162 | 0.020 | 0.016 |
| PM | 62.77% | 100.26% | 100.26% | 0.293 | 0.416 | 0.416 |
| ADP | 10.17% | 23.42% | 37.58% | 0.035 | 0.076 | 0.215 |
| WM | 15.14% | 20.97% | 20.97% | 0.100 | 0.145 | 0.145 |
| UNP | 28.91% | 16.91% | 16.91% | 0.123 | 0.056 | 0.056 |
| SO | -14.58% | 7.91% | 3.28% | -0.078 | 0.044 | 0.018 |
| VZ | -6.74% | -14.20% | -14.20% | -0.035 | -0.063 | -0.063 |
| PANW | 557.40% | 681.20% | 681.20% | 0.851 | 1.164 | 1.164 |
| CVS | 43.41% | 30.49% | 40.06% | 0.177 | 0.108 | 0.157 |

No candidate is auto-promoted by this run.

`SLTD_V7_FRESH_OOS10_VALIDATION_V1 = COMPLETE`
