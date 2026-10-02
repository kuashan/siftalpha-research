# SLTD V6 Position Policy v1 — Stock Batch 1

Status: **COMPLETE**

Symbols: AAPL, MSFT, NVDA, AMD, AVGO, ORCL, INTC, QCOM, MU, GOOGL

Window: 2020-01-02 through 2026-09-30

Representation: FIRST_OBSERVED

Execution: signal close -> next available open

Candidates evaluated: 1152

## Top 20 — 5 bps baseline

| Rank | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `I25_AADD_25_TO_CAP_S75_WTRIM_50_RNO_CHANGE_MIXED` | 1.362 | 29.90% | -21.96% | 483.61% | 1.353 | 10.39 |
| 2 | `I25_AADD_ENTRY_TO_CAP_S75_WTRIM_50_RNO_CHANGE_MIXED` | 1.362 | 29.90% | -21.96% | 483.61% | 1.353 | 10.39 |
| 3 | `I25_AADD_25_TO_CAP_S75_WTRIM_50_RSELL_FIRST` | 1.361 | 29.89% | -21.96% | 483.26% | 1.352 | 10.40 |
| 4 | `I25_AADD_25_TO_CAP_S75_WTRIM_50_RWAIT_FIRST` | 1.361 | 29.89% | -21.96% | 483.26% | 1.352 | 10.40 |
| 5 | `I25_AADD_ENTRY_TO_CAP_S75_WTRIM_50_RSELL_FIRST` | 1.361 | 29.89% | -21.96% | 483.26% | 1.352 | 10.40 |
| 6 | `I25_AADD_ENTRY_TO_CAP_S75_WTRIM_50_RWAIT_FIRST` | 1.361 | 29.89% | -21.96% | 483.26% | 1.352 | 10.40 |
| 7 | `I40_AADD_25_TO_CAP_S75_WTRIM_50_RNO_CHANGE_MIXED` | 1.354 | 29.78% | -22.00% | 479.88% | 1.345 | 10.52 |
| 8 | `I40_AADD_25_TO_CAP_S75_WTRIM_50_RSELL_FIRST` | 1.353 | 29.77% | -22.00% | 479.53% | 1.344 | 10.53 |
| 9 | `I40_AADD_25_TO_CAP_S75_WTRIM_50_RWAIT_FIRST` | 1.353 | 29.77% | -22.00% | 479.53% | 1.344 | 10.53 |
| 10 | `I25_AADD_25_TO_CAP_S50_WEXIT_100_RNO_CHANGE_MIXED` | 1.350 | 31.08% | -23.02% | 520.42% | 1.342 | 10.05 |
| 11 | `I25_AADD_ENTRY_TO_CAP_S50_WEXIT_100_RNO_CHANGE_MIXED` | 1.350 | 31.08% | -23.02% | 520.42% | 1.342 | 10.05 |
| 12 | `I25_AADD_25_TO_CAP_S50_WEXIT_100_RSELL_FIRST` | 1.350 | 31.06% | -23.02% | 519.80% | 1.341 | 10.08 |
| 13 | `I25_AADD_25_TO_CAP_S50_WEXIT_100_RWAIT_FIRST` | 1.350 | 31.06% | -23.02% | 519.80% | 1.341 | 10.08 |
| 14 | `I25_AADD_ENTRY_TO_CAP_S50_WEXIT_100_RSELL_FIRST` | 1.350 | 31.06% | -23.02% | 519.80% | 1.341 | 10.08 |
| 15 | `I25_AADD_ENTRY_TO_CAP_S50_WEXIT_100_RWAIT_FIRST` | 1.350 | 31.06% | -23.02% | 519.80% | 1.341 | 10.08 |
| 16 | `I40_AADD_25_TO_CAP_S100_WTRIM_50_RNO_CHANGE_MIXED` | 1.321 | 29.31% | -22.18% | 466.00% | 1.311 | 12.44 |
| 17 | `I40_AADD_25_TO_CAP_S100_WTRIM_50_RSELL_FIRST` | 1.321 | 29.31% | -22.18% | 466.00% | 1.311 | 12.44 |
| 18 | `I40_AADD_25_TO_CAP_S100_WTRIM_50_RWAIT_FIRST` | 1.321 | 29.31% | -22.18% | 466.00% | 1.311 | 12.44 |
| 19 | `I50_AADD_25_TO_CAP_S75_WTRIM_50_RNO_CHANGE_MIXED` | 1.310 | 29.68% | -22.65% | 476.82% | 1.305 | 10.61 |
| 20 | `I50_AADD_25_TO_CAP_S75_WTRIM_50_RSELL_FIRST` | 1.309 | 29.66% | -22.65% | 476.47% | 1.304 | 10.62 |

## Batch rule

This batch is recorded independently. No parameter is changed from its
results before the next batch. Discovery ranking across Batches 1-4 is
performed only after Batch 4 is complete.

`SLTD_V6_POSITION_POLICY_BATCH_01 = COMPLETE`
