# SLTD V6 Position Policy — Validation Batch 7

Status: **COMPLETE**

Mode: **FROZEN SHORTLIST VALIDATION ONLY**

No discovery reranking or parameter retuning is performed in this batch.

Symbols: ACN, NOW, INTU, AMAT, LRCX, BKNG, TJX, CMG, ROST, MAR

Window: 2020-01-02 through 2026-09-30

Representation: FIRST_OBSERVED

Execution: signal close -> next available open

Candidates evaluated: **5 frozen candidates**

## Frozen-order results

| Slot | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |
|---|---|---:|---:|---:|---:|---:|---:|
| PRIMARY | \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.490 | 17.10% | -34.91% | 189.87% | 0.488 | 5.69 |
| BACKUP_1 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.489 | 17.08% | -34.91% | 189.64% | 0.488 | 5.76 |
| BACKUP_2 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST\` | 0.403 | 10.60% | -26.29% | 97.22% | 0.399 | 10.77 |
| BACKUP_3 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RNO_CHANGE_MIXED\` | 0.406 | 10.67% | -26.29% | 98.08% | 0.402 | 10.68 |
| BACKUP_4 | \`I25_AADD_25_TO_CAP_S75_WTRIM_25_RSELL_FIRST\` | 0.439 | 10.75% | -24.49% | 99.12% | 0.435 | 11.13 |

Validation order remains the frozen discovery order:
PRIMARY -> BACKUP_1 -> BACKUP_2 -> BACKUP_3 -> BACKUP_4.

Final validation gates are evaluated only after Batches 5-8 are complete.

`SLTD_V6_POSITION_POLICY_VALIDATION_BATCH_07 = COMPLETE`
