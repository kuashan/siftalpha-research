# Falsification v1 — State Density Audit

Status: COMPLETE FOR PERSISTED THREE-STATE VALIDATION ENGINE  
Date: 2026-09-28

## Method

Daily exclusive state is reconstructed from the persisted as-of transition sequence in TRANS_MID_CHUNK1/2/3.

The stored transition idx aligns exactly with the SPY trading-date index for the validation sample.

A transition bar belongs to its new current state.

For symbols with no transition inside Validation B, the persisted event stream shows a single constant state across the window.

No market data are re-downloaded and XMA is not recalculated.

Important limitation:
the persisted falsification transition engine contains UP / RANGE / DOWN only.
EXPANSION is not present in this artifact and is not retro-inferred here.

## Aggregate state occupancy

| Window | State bars | UP | RANGE | DOWN |
| --- | ---: | ---: | ---: | ---: |
| Validation A | 49062 | 51.0% | 25.8% | 23.2% |
| Validation B | 4953 | 59.9% | 26.4% | 13.7% |

Validation A:
- 1258 trading bars x 39 symbols.

Validation B:
- 127 available trading bars x 39 symbols.

## Event density within eligible state

| Window | Upper events / 1000 UP bars | Lower events / 1000 DOWN bars |
| --- | ---: | ---: |
| Validation A | 15.67 | 28.59 |
| Validation B | 15.49 | 29.50 |

The conditional event density is remarkably similar across A and B even though state occupancy changes materially.

This matters because:
- B contains more UP exposure than A;
- B contains much less DOWN exposure than A;
- but strict confluence frequency conditional on its required state is similar.

Therefore the A/B outcome difference cannot be explained simply by saying the confluence event became rare inside its own state.

This does not establish an edge and does not create a Regime explanation.

## Per-symbol state-density dispersion

Validation A median symbol shares:
- UP: 51.0%
- RANGE: 26.5%
- DOWN: 23.2%

Validation B median symbol shares:
- UP: 60.6%
- RANGE: 22.8%
- DOWN: 0.0%

Validation B is more heterogeneous across symbols; several symbols spend the entire short window in one state.

## Decision

State density is retained as descriptive context.

It does not alter:
- Upper general-top rule = REJECT;
- Lower incremental-buy rule = REJECT.

No state-density threshold is promoted.
No Regime split is created.
