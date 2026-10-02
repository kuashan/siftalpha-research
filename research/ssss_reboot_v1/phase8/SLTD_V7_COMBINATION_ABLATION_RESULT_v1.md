# SLTD V7 Combination Ablation Study v1

Status: **COMPLETE**

Research status: **EXPLORATORY — reused 79-stock universe**

Frozen V6 baseline remains unchanged.

Baseline reproduction against frozen C2 result: **PASS (5 bps and 10 bps)**.

## All-79 portfolio — 5 bps

| Variant | Return | CAGR | MaxDD | Calmar | Turnover | C2 exits |
|---|---:|---:|---:|---:|---:|---:|
| BASELINE_ALL_15 | 153.45% | 14.79% | -18.30% | 0.808 | 9.09 | 305 |
| DROP_B3 | 152.10% | 14.70% | -18.19% | 0.808 | 9.01 | 305 |
| DROP_S1 | 179.68% | 16.48% | -20.12% | 0.819 | 6.82 | 243 |
| DROP_S3 | 167.57% | 15.71% | -19.18% | 0.820 | 8.34 | 251 |
| DROP_B3_S1 | 178.81% | 16.42% | -20.02% | 0.820 | 6.77 | 243 |
| DROP_B3_S3 | 166.28% | 15.63% | -18.99% | 0.823 | 8.29 | 251 |
| DROP_S1_S3 | 199.26% | 17.65% | -21.07% | 0.838 | 5.71 | 179 |
| DROP_B3_S1_S3 | 198.58% | 17.61% | -20.91% | 0.842 | 5.69 | 179 |

## Delta vs frozen baseline — 5 bps

| Variant | ΔCAGR | ΔMaxDD | ΔCalmar | Calmar better batches | Calmar worse batches |
|---|---:|---:|---:|---:|---:|
| DROP_B3 | -0.09% | 0.11% | -0.000 | 2/8 | 6/8 |
| DROP_S1 | 1.69% | -1.82% | +0.011 | 4/8 | 4/8 |
| DROP_S3 | 0.93% | -0.88% | +0.011 | 5/8 | 3/8 |
| DROP_B3_S1 | 1.64% | -1.73% | +0.012 | 4/8 | 4/8 |
| DROP_B3_S3 | 0.84% | -0.69% | +0.015 | 4/8 | 4/8 |
| DROP_S1_S3 | 2.86% | -2.77% | +0.030 | 6/8 | 2/8 |
| DROP_B3_S1_S3 | 2.82% | -2.61% | +0.034 | 6/8 | 2/8 |

## Combination interaction — 5 bps

| Combo | Interaction ΔCAGR | CAGR label | Interaction ΔCalmar | Calmar label |
|---|---:|---|---:|---|
| DROP_B3_S1 | 0.04% | APPROX_ADDITIVE | +0.002 | APPROX_ADDITIVE |
| DROP_B3_S3 | 0.01% | APPROX_ADDITIVE | +0.004 | APPROX_ADDITIVE |
| DROP_S1_S3 | 0.25% | BETTER_THAN_ADDITIVE | +0.008 | APPROX_ADDITIVE |
| DROP_B3_S1_S3 | 0.30% | BETTER_THAN_ADDITIVE | +0.012 | BETTER_THAN_ADDITIVE |

This study does not change the frozen V6 baseline. Any candidate must receive fresh OOS validation before replacement.

`SLTD_V7_COMBINATION_ABLATION_STUDY_V1 = COMPLETE`
