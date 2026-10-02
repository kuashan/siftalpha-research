# SLTD V6 Position Policy — Validation Batch 5

Status: **COMPLETE**

Mode: **FROZEN SHORTLIST VALIDATION ONLY**

No discovery reranking or parameter retuning is performed in this batch.

Symbols: IBM, CSCO, CRM, ADBE, TXN, DIS, NKE, SBUX, TGT, LOW

Window: 2020-01-02 through 2026-09-30

Representation: FIRST_OBSERVED

Execution: signal close -> next available open

Candidates evaluated: **5 frozen candidates**

## Frozen-order results

| Slot | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |
|---|---|---:|---:|---:|---:|---:|---:|
| PRIMARY | \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.123 | 4.09% | -33.18% | 31.03% | 0.122 | 5.61 |
| BACKUP_1 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.123 | 4.09% | -33.18% | 31.03% | 0.122 | 5.61 |
| BACKUP_2 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST\` | 0.139 | 3.28% | -23.57% | 24.30% | 0.135 | 10.12 |
| BACKUP_3 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RNO_CHANGE_MIXED\` | 0.139 | 3.28% | -23.57% | 24.30% | 0.135 | 10.12 |
| BACKUP_4 | \`I25_AADD_25_TO_CAP_S75_WTRIM_25_RSELL_FIRST\` | 0.133 | 3.01% | -22.52% | 22.10% | 0.129 | 10.61 |

Validation order remains the frozen discovery order:
PRIMARY -> BACKUP_1 -> BACKUP_2 -> BACKUP_3 -> BACKUP_4.

Final validation gates are evaluated only after Batches 5-8 are complete.

`SLTD_V6_POSITION_POLICY_VALIDATION_BATCH_05 = COMPLETE`
