# SLTD V6 Position Policy v1 — Stock Batch 3

Status: **COMPLETE**

Symbols: PEP, ABT, LLY, UNH, JNJ, TMO, JPM, BAC, GS, V

Window: 2020-01-02 through 2026-09-30

Representation: FIRST_OBSERVED

Execution: signal close -> next available open

Candidates evaluated: 1152

## Top 20 — 5 bps baseline

| Rank | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED` | 0.573 | 10.94% | -19.11% | 101.44% | 0.569 | 6.72 |
| 2 | `I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED` | 0.573 | 10.94% | -19.11% | 101.44% | 0.569 | 6.72 |
| 3 | `I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST` | 0.572 | 10.94% | -19.11% | 101.42% | 0.569 | 6.74 |
| 4 | `I25_AADD_25_TO_CAP_S25_WHOLD_RWAIT_FIRST` | 0.572 | 10.94% | -19.11% | 101.42% | 0.569 | 6.74 |
| 5 | `I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RSELL_FIRST` | 0.572 | 10.94% | -19.11% | 101.42% | 0.569 | 6.74 |
| 6 | `I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RWAIT_FIRST` | 0.572 | 10.94% | -19.11% | 101.42% | 0.569 | 6.74 |
| 7 | `I25_AADD_25_TO_CAP_S25_WTRIM_25_RNO_CHANGE_MIXED` | 0.496 | 9.45% | -19.05% | 83.81% | 0.492 | 8.07 |
| 8 | `I25_AADD_ENTRY_TO_CAP_S25_WTRIM_25_RNO_CHANGE_MIXED` | 0.496 | 9.45% | -19.05% | 83.81% | 0.492 | 8.07 |
| 9 | `I25_AADD_25_TO_CAP_S25_WTRIM_25_RSELL_FIRST` | 0.496 | 9.45% | -19.05% | 83.80% | 0.492 | 8.09 |
| 10 | `I25_AADD_25_TO_CAP_S25_WTRIM_25_RWAIT_FIRST` | 0.496 | 9.45% | -19.05% | 83.80% | 0.492 | 8.09 |
| 11 | `I25_AADD_ENTRY_TO_CAP_S25_WTRIM_25_RSELL_FIRST` | 0.496 | 9.45% | -19.05% | 83.80% | 0.492 | 8.09 |
| 12 | `I25_AADD_ENTRY_TO_CAP_S25_WTRIM_25_RWAIT_FIRST` | 0.496 | 9.45% | -19.05% | 83.80% | 0.492 | 8.09 |
| 13 | `I40_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED` | 0.464 | 10.90% | -23.49% | 100.89% | 0.461 | 6.79 |
| 14 | `I40_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST` | 0.464 | 10.90% | -23.49% | 100.88% | 0.461 | 6.81 |
| 15 | `I40_AADD_25_TO_CAP_S25_WHOLD_RWAIT_FIRST` | 0.464 | 10.90% | -23.49% | 100.88% | 0.461 | 6.81 |
| 16 | `I25_AADD_25_TO_CAP_S25_WTRIM_50_RNO_CHANGE_MIXED` | 0.436 | 8.29% | -18.99% | 71.05% | 0.432 | 9.02 |
| 17 | `I25_AADD_ENTRY_TO_CAP_S25_WTRIM_50_RNO_CHANGE_MIXED` | 0.436 | 8.29% | -18.99% | 71.05% | 0.432 | 9.02 |
| 18 | `I25_AADD_25_TO_CAP_S25_WTRIM_50_RSELL_FIRST` | 0.436 | 8.28% | -18.99% | 71.03% | 0.432 | 9.04 |
| 19 | `I25_AADD_25_TO_CAP_S25_WTRIM_50_RWAIT_FIRST` | 0.436 | 8.28% | -18.99% | 71.03% | 0.432 | 9.04 |
| 20 | `I25_AADD_ENTRY_TO_CAP_S25_WTRIM_50_RSELL_FIRST` | 0.436 | 8.28% | -18.99% | 71.03% | 0.432 | 9.04 |

## Batch rule

This batch is recorded independently. No parameter is changed from its
results before the next batch. Discovery ranking across Batches 1-4 is
performed only after Batch 4 is complete.

`SLTD_V6_POSITION_POLICY_BATCH_03 = COMPLETE`
