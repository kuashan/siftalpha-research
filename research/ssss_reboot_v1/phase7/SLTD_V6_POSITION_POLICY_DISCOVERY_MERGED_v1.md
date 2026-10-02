# SLTD V6 Position Policy — Discovery Merge B1-B4

Status: **COMPLETE**

This is the mechanical merge/ranking of the four frozen discovery batches.
No Stage A parameters were changed.

Candidates merged: **1,152**

Primary + four Backups are **not frozen by this merge step**.

## Ranking semantics

1. higher median batch Calmar
2. higher worst-batch Calmar
3. higher median batch CAGR
4. lower median batch Max Drawdown magnitude
5. lower between-batch Calmar dispersion (population standard deviation)
6. lower median batch turnover

## Top 20 merged discovery ranking

| Rank | Policy | Median Calmar | Worst Calmar | Median CAGR | Median MaxDD | Calmar Disp. | Median Turnover | Median 10bps Calmar |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.616 | 0.360 | 12.65% | -26.80% | 0.206 | 6.424 | 0.612 |
| 2 | \`I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.616 | 0.360 | 12.65% | -26.80% | 0.206 | 6.424 | 0.612 |
| 3 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.616 | 0.363 | 12.70% | -26.78% | 0.205 | 6.453 | 0.612 |
| 4 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RWAIT_FIRST\` | 0.616 | 0.363 | 12.70% | -26.78% | 0.205 | 6.453 | 0.612 |
| 5 | \`I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.616 | 0.363 | 12.70% | -26.78% | 0.205 | 6.453 | 0.612 |
| 6 | \`I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RWAIT_FIRST\` | 0.616 | 0.363 | 12.70% | -26.78% | 0.205 | 6.453 | 0.612 |
| 7 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST\` | 0.581 | 0.307 | 9.71% | -19.49% | 0.341 | 11.690 | 0.574 |
| 8 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RWAIT_FIRST\` | 0.581 | 0.307 | 9.71% | -19.49% | 0.341 | 11.690 | 0.574 |
| 9 | \`I25_AADD_ENTRY_TO_CAP_S75_WHOLD_RSELL_FIRST\` | 0.581 | 0.307 | 9.71% | -19.49% | 0.341 | 11.690 | 0.574 |
| 10 | \`I25_AADD_ENTRY_TO_CAP_S75_WHOLD_RWAIT_FIRST\` | 0.581 | 0.307 | 9.71% | -19.49% | 0.341 | 11.690 | 0.574 |
| 11 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RNO_CHANGE_MIXED\` | 0.573 | 0.307 | 9.58% | -19.56% | 0.343 | 11.682 | 0.565 |
| 12 | \`I25_AADD_ENTRY_TO_CAP_S75_WHOLD_RNO_CHANGE_MIXED\` | 0.573 | 0.307 | 9.58% | -19.56% | 0.343 | 11.682 | 0.565 |
| 13 | \`I25_AADD_25_TO_CAP_S75_WTRIM_25_RSELL_FIRST\` | 0.562 | 0.275 | 9.34% | -19.43% | 0.381 | 12.165 | 0.554 |
| 14 | \`I25_AADD_25_TO_CAP_S75_WTRIM_25_RWAIT_FIRST\` | 0.562 | 0.275 | 9.34% | -19.43% | 0.381 | 12.165 | 0.554 |
| 15 | \`I25_AADD_ENTRY_TO_CAP_S75_WTRIM_25_RSELL_FIRST\` | 0.562 | 0.275 | 9.34% | -19.43% | 0.381 | 12.165 | 0.554 |
| 16 | \`I25_AADD_ENTRY_TO_CAP_S75_WTRIM_25_RWAIT_FIRST\` | 0.562 | 0.275 | 9.34% | -19.43% | 0.381 | 12.165 | 0.554 |
| 17 | \`I40_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.559 | 0.366 | 12.89% | -28.93% | 0.217 | 6.500 | 0.556 |
| 18 | \`I40_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.559 | 0.369 | 12.94% | -28.91% | 0.216 | 6.529 | 0.555 |
| 19 | \`I40_AADD_25_TO_CAP_S25_WHOLD_RWAIT_FIRST\` | 0.559 | 0.369 | 12.94% | -28.91% | 0.216 | 6.529 | 0.555 |
| 20 | \`I25_AADD_25_TO_CAP_S25_WTRIM_25_RNO_CHANGE_MIXED\` | 0.557 | 0.364 | 11.86% | -25.66% | 0.253 | 7.610 | 0.553 |

## Top 5 batch-by-batch Calmar

| Rank | Policy | B1 | B2 | B3 | B4 |
|---:|---|---:|---:|---:|---:|
| 1 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.935 | 0.360 | 0.573 | 0.659 |
| 2 | \`I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.935 | 0.360 | 0.573 | 0.659 |
| 3 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.935 | 0.363 | 0.572 | 0.659 |
| 4 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RWAIT_FIRST\` | 0.935 | 0.363 | 0.572 | 0.659 |
| 5 | \`I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.935 | 0.363 | 0.572 | 0.659 |

`SLTD_V6_POSITION_POLICY_DISCOVERY_MERGE_B1_B4 = COMPLETE`
