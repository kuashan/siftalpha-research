# Falsification v1 — State Density Audit

Status: COMPLETE FOR PERSISTED THREE-STATE ENGINE / VALIDATION B COVERAGE QUALIFIED  
Date: 2026-09-28

## Method

Daily exclusive state is reconstructed from the persisted as-of transition sequence in TRANS_MID_CHUNK1/2/3.

The stored transition idx aligns with the SPY trading-date index used by the persisted validation sample.

A transition bar belongs to its new current state.

For symbols with no transition inside the reconstructed Validation B interval, the persisted event stream shows a single constant state across that reconstructed interval.

No market data are re-downloaded and XMA is not recalculated.

Important limitation:
the persisted falsification transition engine contains UP / RANGE / DOWN only.
EXPANSION is not present in this artifact and is not retro-inferred here.

## Post-closure coverage qualification

The JSON artifact records Validation B as:

- start: 2025-07-01
- end: 2025-12-30
- 127 trading bars
- 39 symbols
- 4,953 state bars

But the frozen Validation B protocol ends on **2025-12-31**, and persisted transition/midpoint artifacts contain 2025-12-31 records.

Therefore this audit is **one trading day short of the frozen Validation B window**.

The Validation B occupancy shares and eligible-state event densities below are preserved as the result of the persisted 127-bar reconstruction, but they must not be described as complete 2025-07-01..2025-12-31 full-window occupancy.

No final-day state is guessed or retro-inferred in this correction.

See:
`POST_CLOSURE_INTEGRITY_AUDIT_v1.md`.

## Aggregate state occupancy

| Window | State bars | UP | RANGE | DOWN |
| --- | ---: | ---: | ---: | ---: |
| Validation A | 49062 | 51.0% | 25.8% | 23.2% |
| Validation B persisted reconstruction | 4953 | 59.9% | 26.4% | 13.7% |

Validation A:
- 1258 trading bars x 39 symbols.

Validation B persisted reconstruction:
- 127 trading bars x 39 symbols;
- through 2025-12-30 only.

## Event density within eligible state

| Window | Upper events / 1000 UP bars | Lower events / 1000 DOWN bars |
| --- | ---: | ---: |
| Validation A | 15.67 | 28.59 |
| Validation B persisted reconstruction | 15.49 | 29.50 |

Within the persisted 127-bar B reconstruction, conditional event density is very similar to Validation A even though state occupancy changes materially.

This suggests that, within the reconstructed interval:
- B contains more UP exposure than A;
- B contains much less DOWN exposure than A;
- strict confluence frequency conditional on its required state is similar.

However, because the final frozen Validation B trading day is absent from this density reconstruction, this observation is descriptive and qualified.

It does not establish an edge and does not create a Regime explanation.

## Per-symbol state-density dispersion

Validation A median symbol shares:
- UP: 51.0%
- RANGE: 26.5%
- DOWN: 23.2%

Validation B persisted-reconstruction median symbol shares:
- UP: 60.6%
- RANGE: 22.8%
- DOWN: 0.0%

Validation B is more heterogeneous across symbols; several symbols spend the entire reconstructed short window in one state.

## Decision

State density is retained as descriptive context.

It does not alter:
- Upper general-top rule = REJECT;
- Lower incremental-buy rule = REJECT.

No state-density threshold is promoted.
No Regime split is created.

Validation B density carries the explicit coverage label:
**PARTIAL-WINDOW RECONSTRUCTION THROUGH 2025-12-30.**
