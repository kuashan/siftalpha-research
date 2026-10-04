# SLTD State Score Risk-Exposure v3 — Stage B Momentum Result

Status: **REJECTED_NOT_ADMITTED**

Discovery-selected momentum: **M1**
Stable Stage-A state count: **82**
Bars with non-zero LEVEL: **89.42%**

## Discovery blocked walk-forward

| Candidate | Median MAE improvement | Positive folds | Median rank-corr improvement | Selection pass |
|---|---:|---:|---:|---|
| M1 | -0.016% | 0/3 | -0.00070 | FAIL |
| M3 | -0.022% | 0/3 | -0.00070 | FAIL |
| M5 | -0.026% | 0/3 | -0.00265 | FAIL |

## Temporal consistency (2024-2026Q3)

- Baseline LEVEL-only MAE: **1.055399**
- LEVEL + asymmetric momentum MAE: **1.055453**
- MAE improvement: **-0.005%**
- Baseline rank correlation: **0.03653**
- Full rank correlation: **0.03661**
- MOM_UP coefficient: **-0.002855**
- MOM_DOWN coefficient: **-0.001537**
- Bottom prediction quartile median forward utility: **-0.00205**
- Top prediction quartile median forward utility: **0.16243**

## Gates

- discovery_selection_pass: **FAIL**
- temporal_mae_improves: **FAIL**
- temporal_rank_corr_improves: **PASS**
- temporal_top_gt_bottom: **PASS**

Temporal is a consistency check because Stage A already used it for state stability.
No Fresh OOS was consumed.

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_B = REJECTED_NOT_ADMITTED`
