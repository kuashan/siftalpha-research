# SLTD V6 Position Policy v1 — Stock Batch 2

Status: **COMPLETE**

Symbols: META, NFLX, AMZN, TSLA, HD, MCD, WMT, COST, PG, KO

Window: 2020-01-02 through 2026-09-30

Representation: FIRST_OBSERVED

Execution: signal close -> next available open

Candidates evaluated: 1152

## Top 20 — 5 bps baseline

| Rank | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `I100_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST` | 0.540 | 11.20% | -20.75% | 104.63% | 0.536 | 11.60 |
| 2 | `I100_AADD_25_TO_CAP_S75_WHOLD_RWAIT_FIRST` | 0.540 | 11.20% | -20.75% | 104.63% | 0.536 | 11.60 |
| 3 | `I25_AADD_25_TO_CAP_S100_WHOLD_RSELL_FIRST` | 0.539 | 9.33% | -17.30% | 82.49% | 0.532 | 12.19 |
| 4 | `I25_AADD_25_TO_CAP_S100_WHOLD_RWAIT_FIRST` | 0.539 | 9.33% | -17.30% | 82.49% | 0.532 | 12.19 |
| 5 | `I25_AADD_ENTRY_TO_CAP_S100_WHOLD_RSELL_FIRST` | 0.539 | 9.33% | -17.30% | 82.49% | 0.532 | 12.19 |
| 6 | `I25_AADD_ENTRY_TO_CAP_S100_WHOLD_RWAIT_FIRST` | 0.539 | 9.33% | -17.30% | 82.49% | 0.532 | 12.19 |
| 7 | `I70_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST` | 0.539 | 11.08% | -20.54% | 103.07% | 0.533 | 11.46 |
| 8 | `I70_AADD_25_TO_CAP_S75_WHOLD_RWAIT_FIRST` | 0.539 | 11.08% | -20.54% | 103.07% | 0.533 | 11.46 |
| 9 | `I60_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST` | 0.539 | 10.97% | -20.36% | 101.78% | 0.533 | 11.37 |
| 10 | `I60_AADD_25_TO_CAP_S75_WHOLD_RWAIT_FIRST` | 0.539 | 10.97% | -20.36% | 101.78% | 0.533 | 11.37 |
| 11 | `I50_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST` | 0.539 | 10.87% | -20.17% | 100.49% | 0.532 | 11.29 |
| 12 | `I50_AADD_25_TO_CAP_S75_WHOLD_RWAIT_FIRST` | 0.539 | 10.87% | -20.17% | 100.49% | 0.532 | 11.29 |
| 13 | `I40_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST` | 0.536 | 10.74% | -20.04% | 98.91% | 0.530 | 11.18 |
| 14 | `I40_AADD_25_TO_CAP_S75_WHOLD_RWAIT_FIRST` | 0.536 | 10.74% | -20.04% | 98.91% | 0.530 | 11.18 |
| 15 | `I25_AADD_25_TO_CAP_S100_WTRIM_25_RSELL_FIRST` | 0.534 | 9.19% | -17.21% | 80.93% | 0.526 | 12.43 |
| 16 | `I25_AADD_25_TO_CAP_S100_WTRIM_25_RWAIT_FIRST` | 0.534 | 9.19% | -17.21% | 80.93% | 0.526 | 12.43 |
| 17 | `I25_AADD_ENTRY_TO_CAP_S100_WTRIM_25_RSELL_FIRST` | 0.534 | 9.19% | -17.21% | 80.93% | 0.526 | 12.43 |
| 18 | `I25_AADD_ENTRY_TO_CAP_S100_WTRIM_25_RWAIT_FIRST` | 0.534 | 9.19% | -17.21% | 80.93% | 0.526 | 12.43 |
| 19 | `I25_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST` | 0.529 | 10.52% | -19.87% | 96.33% | 0.523 | 11.01 |
| 20 | `I25_AADD_25_TO_CAP_S75_WHOLD_RWAIT_FIRST` | 0.529 | 10.52% | -19.87% | 96.33% | 0.523 | 11.01 |

## Batch rule

This batch is recorded independently. No parameter is changed from its
results before the next batch. Discovery ranking across Batches 1-4 is
performed only after Batch 4 is complete.

`SLTD_V6_POSITION_POLICY_BATCH_02 = COMPLETE`
