# SLTD V6 Position Policy v1 — Stock Batch 4

Status: **COMPLETE**

Symbols: MA, CAT, BA, GE, XOM, CVX, LIN, NEE, PLD

Window: 2020-01-02 through 2026-09-30

Representation: FIRST_OBSERVED

Execution: signal close -> next available open

Candidates evaluated: 1152

## Top 20 — 5 bps baseline

| Rank | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `I25_ATOPUP_TO_100_S25_WHOLD_RNO_CHANGE_MIXED` | 0.669 | 14.18% | -21.19% | 144.51% | 0.666 | 6.89 |
| 2 | `I25_ATOPUP_TO_100_S25_WHOLD_RSELL_FIRST` | 0.669 | 14.18% | -21.19% | 144.51% | 0.666 | 6.89 |
| 3 | `I25_ATOPUP_TO_100_S25_WHOLD_RWAIT_FIRST` | 0.669 | 14.18% | -21.19% | 144.51% | 0.666 | 6.89 |
| 4 | `I40_AADD_ENTRY_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED` | 0.669 | 13.90% | -20.78% | 140.47% | 0.665 | 6.83 |
| 5 | `I40_AADD_ENTRY_TO_CAP_S25_WHOLD_RSELL_FIRST` | 0.669 | 13.90% | -20.78% | 140.47% | 0.665 | 6.83 |
| 6 | `I40_AADD_ENTRY_TO_CAP_S25_WHOLD_RWAIT_FIRST` | 0.669 | 13.90% | -20.78% | 140.47% | 0.665 | 6.83 |
| 7 | `I40_ATOPUP_TO_100_S25_WHOLD_RNO_CHANGE_MIXED` | 0.665 | 14.05% | -21.12% | 142.70% | 0.662 | 6.92 |
| 8 | `I40_ATOPUP_TO_100_S25_WHOLD_RSELL_FIRST` | 0.665 | 14.05% | -21.12% | 142.70% | 0.662 | 6.92 |
| 9 | `I40_ATOPUP_TO_100_S25_WHOLD_RWAIT_FIRST` | 0.665 | 14.05% | -21.12% | 142.70% | 0.662 | 6.92 |
| 10 | `I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED` | 0.659 | 13.29% | -20.17% | 131.93% | 0.655 | 6.62 |
| 11 | `I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST` | 0.659 | 13.29% | -20.17% | 131.93% | 0.655 | 6.62 |
| 12 | `I25_AADD_25_TO_CAP_S25_WHOLD_RWAIT_FIRST` | 0.659 | 13.29% | -20.17% | 131.93% | 0.655 | 6.62 |
| 13 | `I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED` | 0.659 | 13.29% | -20.17% | 131.93% | 0.655 | 6.62 |
| 14 | `I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RSELL_FIRST` | 0.659 | 13.29% | -20.17% | 131.93% | 0.655 | 6.62 |
| 15 | `I25_AADD_ENTRY_TO_CAP_S25_WHOLD_RWAIT_FIRST` | 0.659 | 13.29% | -20.17% | 131.93% | 0.655 | 6.62 |
| 16 | `I40_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED` | 0.653 | 13.22% | -20.25% | 131.07% | 0.650 | 6.70 |
| 17 | `I40_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST` | 0.653 | 13.22% | -20.25% | 131.07% | 0.650 | 6.70 |
| 18 | `I40_AADD_25_TO_CAP_S25_WHOLD_RWAIT_FIRST` | 0.653 | 13.22% | -20.25% | 131.07% | 0.650 | 6.70 |
| 19 | `I50_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED` | 0.650 | 13.19% | -20.29% | 130.55% | 0.646 | 6.75 |
| 20 | `I50_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST` | 0.650 | 13.19% | -20.29% | 130.55% | 0.646 | 6.75 |

## Batch rule

This batch is recorded independently. No parameter is changed from its
results before the next batch. Discovery ranking across Batches 1-4 is
performed only after Batch 4 is complete.

`SLTD_V6_POSITION_POLICY_BATCH_04 = COMPLETE`
