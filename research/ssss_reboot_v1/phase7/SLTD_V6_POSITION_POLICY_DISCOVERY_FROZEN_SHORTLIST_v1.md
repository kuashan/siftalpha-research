# SLTD V6 Position Policy — Frozen Discovery Shortlist v1

Status: **FROZEN BEFORE VALIDATION**

Source: Batches 1-4 merged discovery ranking.

Raw Stage A candidates: **1152**
Unique discovery-observed outcome groups: **688**

## Deduplication rule

Two policies are treated as discovery-observed equivalents only when their complete
B1-B4 baseline 5 bps and stress 10 bps aggregate metric dictionaries are exactly identical.
Within each equivalence group, the earliest policy in the frozen discovery ranking is the representative.
Deduplication never reorders non-equivalent policies.

This is a user-directed pre-validation procedural amendment made before inspecting any
Batch 5-8 validation outcome. Its only purpose is to prevent Backup slots from being
consumed by policies that produced exactly the same observed discovery outcomes.

## Frozen Primary + Backups

| Slot | Discovery Rank | Policy | Median Calmar | Worst Calmar | Median CAGR | Median MaxDD | Median 10bps Calmar | Equivalent Count |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| PRIMARY | 1 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED\` | 0.616 | 0.360 | 12.65% | -26.80% | 0.612 | 2 |
| BACKUP_1 | 3 | \`I25_AADD_25_TO_CAP_S25_WHOLD_RSELL_FIRST\` | 0.616 | 0.363 | 12.70% | -26.78% | 0.612 | 4 |
| BACKUP_2 | 7 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RSELL_FIRST\` | 0.581 | 0.307 | 9.71% | -19.49% | 0.574 | 4 |
| BACKUP_3 | 11 | \`I25_AADD_25_TO_CAP_S75_WHOLD_RNO_CHANGE_MIXED\` | 0.573 | 0.307 | 9.58% | -19.56% | 0.565 | 2 |
| BACKUP_4 | 13 | \`I25_AADD_25_TO_CAP_S75_WTRIM_25_RSELL_FIRST\` | 0.562 | 0.275 | 9.34% | -19.43% | 0.554 | 4 |

## Frozen execution semantics

- **PRIMARY**: initial=25%, add=ADD_25_TO_CAP, sell_reduction=25%, wait=HOLD, mixed=NO_CHANGE_MIXED.
- **BACKUP_1**: initial=25%, add=ADD_25_TO_CAP, sell_reduction=25%, wait=HOLD, mixed=SELL_FIRST.
- **BACKUP_2**: initial=25%, add=ADD_25_TO_CAP, sell_reduction=75%, wait=HOLD, mixed=SELL_FIRST.
- **BACKUP_3**: initial=25%, add=ADD_25_TO_CAP, sell_reduction=75%, wait=HOLD, mixed=NO_CHANGE_MIXED.
- **BACKUP_4**: initial=25%, add=ADD_25_TO_CAP, sell_reduction=75%, wait=TRIM_25, mixed=SELL_FIRST.

These five representatives are frozen in this order for Batch 5-8 validation.
No later batch may retune or reorder them.

`SLTD_V6_POSITION_POLICY_DISCOVERY_SHORTLIST = FROZEN_BEFORE_VALIDATION`
