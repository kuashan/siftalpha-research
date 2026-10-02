# SLTD V6 Position Policy — Validation Batch 8

Status: **COMPLETE**

Mode: **FROZEN SHORTLIST VALIDATION ONLY**

No discovery reranking or parameter retuning is performed in this batch.

Symbols: DHR, SYK, MDT, BMY, ISRG, SCHW, SPGI, DE, HON, RTX

Window: 2020-01-02 through 2026-09-30

Representation: FIRST_OBSERVED

Execution: signal close -> next available open

Candidates evaluated: **5 frozen candidates**

## Frozen-order results

| Slot | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |
|---|---|---:|---:|---:|---:|---:|---:|
| PRIMARY | \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.323 | 7.35% | -22.74% | 61.30% | 0.320 | 6.10 |
| BACKUP_1 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.323 | 7.35% | -22.74% | 61.34% | 0.320 | 6.11 |
| BACKUP_2 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST\` | 0.211 | 4.45% | -21.09% | 34.12% | 0.207 | 10.97 |
| BACKUP_3 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RNO_CHANGE_MIXED\` | 0.211 | 4.45% | -21.09% | 34.12% | 0.207 | 10.97 |
| BACKUP_4 | \`I25_AADD_25_TO_CAP_S75_WTRIM_25_RSELL_FIRST\` | 0.171 | 3.60% | -21.09% | 26.92% | 0.166 | 11.75 |

Validation order remains the frozen discovery order:
PRIMARY -> BACKUP_1 -> BACKUP_2 -> BACKUP_3 -> BACKUP_4.

Final validation gates are evaluated only after Batches 5-8 are complete.

`SLTD_V6_POSITION_POLICY_VALIDATION_BATCH_08 = COMPLETE`
