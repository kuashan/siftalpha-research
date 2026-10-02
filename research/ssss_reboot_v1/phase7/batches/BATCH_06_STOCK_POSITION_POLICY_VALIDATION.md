# SLTD V6 Position Policy — Validation Batch 6

Status: **COMPLETE**

Mode: **FROZEN SHORTLIST VALIDATION ONLY**

No discovery reranking or parameter retuning is performed in this batch.

Symbols: MRK, PFE, ABBV, AMGN, GILD, C, MS, BLK, COP, UPS

Window: 2020-01-02 through 2026-09-30

Representation: FIRST_OBSERVED

Execution: signal close -> next available open

Candidates evaluated: **5 frozen candidates**

## Frozen-order results

| Slot | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |
|---|---|---:|---:|---:|---:|---:|---:|
| PRIMARY | \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.567 | 8.94% | -15.77% | 78.15% | 0.561 | 7.29 |
| BACKUP_1 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.566 | 8.93% | -15.77% | 78.06% | 0.561 | 7.31 |
| BACKUP_2 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST\` | 0.312 | 4.51% | -14.44% | 34.66% | 0.305 | 12.98 |
| BACKUP_3 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RNO_CHANGE_MIXED\` | 0.313 | 4.53% | -14.44% | 34.79% | 0.306 | 12.94 |
| BACKUP_4 | \`I25_AADD_25_TO_CAP_S75_WTRIM_25_RSELL_FIRST\` | 0.293 | 4.01% | -13.68% | 30.37% | 0.285 | 13.54 |

Validation order remains the frozen discovery order:
PRIMARY -> BACKUP_1 -> BACKUP_2 -> BACKUP_3 -> BACKUP_4.

Final validation gates are evaluated only after Batches 5-8 are complete.

`SLTD_V6_POSITION_POLICY_VALIDATION_BATCH_06 = COMPLETE`
