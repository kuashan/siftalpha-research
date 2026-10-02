# SLTD V6 Position Policy — Stock Validation Decision v1

Status: **COMPLETE**

Validation batches: **5, 6, 7, 8**

Selection rule: use the first candidate in the frozen discovery order that passes all
preregistered validation gates. Validation results are admission gates, not a reranking objective.

## Validation summary

| Frozen slot | Policy | Positive Calmar batches | Median Calmar | Median CAGR | Median 10bps Calmar | Worst MaxDD | Gates |
|---|---|---:|---:|---:|---:|---:|---|
| PRIMARY | \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 4/4 | 0.406 | 8.14% | 0.404 | -34.91% | **PASS** |
| BACKUP_1 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 4/4 | 0.406 | 8.14% | 0.404 | -34.91% | **PASS** |
| BACKUP_2 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST\` | 4/4 | 0.262 | 4.48% | 0.256 | -26.29% | **PASS** |
| BACKUP_3 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RNO_CHANGE_MIXED\` | 4/4 | 0.262 | 4.49% | 0.256 | -26.29% | **PASS** |
| BACKUP_4 | \`I25_AADD_25_TO_CAP_S75_WTRIM_25_RSELL_FIRST\` | 4/4 | 0.232 | 3.80% | 0.226 | -24.49% | **PASS** |

## Gate details

### PRIMARY — \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\`

- PASS — at_least_3_of_4_calmar_gt_0
- PASS — median_validation_calmar_gt_0
- PASS — median_validation_cagr_gt_0
- PASS — median_10bps_validation_calmar_gt_0
- PASS — no_validation_batch_maxdd_worse_than_minus_60pct

### BACKUP_1 — \`I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\`

- PASS — at_least_3_of_4_calmar_gt_0
- PASS — median_validation_calmar_gt_0
- PASS — median_validation_cagr_gt_0
- PASS — median_10bps_validation_calmar_gt_0
- PASS — no_validation_batch_maxdd_worse_than_minus_60pct

### BACKUP_2 — \`I25_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST\`

- PASS — at_least_3_of_4_calmar_gt_0
- PASS — median_validation_calmar_gt_0
- PASS — median_validation_cagr_gt_0
- PASS — median_10bps_validation_calmar_gt_0
- PASS — no_validation_batch_maxdd_worse_than_minus_60pct

### BACKUP_3 — \`I25_AADD_25_TO_CAP_S75_WHOLD_RNO_CHANGE_MIXED\`

- PASS — at_least_3_of_4_calmar_gt_0
- PASS — median_validation_calmar_gt_0
- PASS — median_validation_cagr_gt_0
- PASS — median_10bps_validation_calmar_gt_0
- PASS — no_validation_batch_maxdd_worse_than_minus_60pct

### BACKUP_4 — \`I25_AADD_25_TO_CAP_S75_WTRIM_25_RSELL_FIRST\`

- PASS — at_least_3_of_4_calmar_gt_0
- PASS — median_validation_calmar_gt_0
- PASS — median_validation_cagr_gt_0
- PASS — median_10bps_validation_calmar_gt_0
- PASS — no_validation_batch_maxdd_worse_than_minus_60pct

## Stock policy decision

**PROMOTED:** \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\`

Frozen role: **PRIMARY**

Execution policy: initial=25%, add=ADD_25_TO_CAP, sell_reduction=25%, wait=HOLD, mixed=NO_CHANGE_MIXED.

The policy was selected by frozen order + admission gates, not by validation reranking.

Batch 9 remains a crypto transfer check only and cannot change this stock-selected policy.

\`SLTD_V6_STOCK_POLICY = PROMOTED\`
