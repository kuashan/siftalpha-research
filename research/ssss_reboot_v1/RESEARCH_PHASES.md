# SSSS Reboot v1 — Research Phases

Status: **PRE-REGISTERED SEQUENCE**

## Phase 0 — Source reconstruction

Goal:
- decode and parse the original SSSS source;
- enumerate every computed series and displayed object;
- identify XMA use and any non-causal/repainting behavior;
- reproduce the ABT 2025-01-15 calibration anchor.

Closure:
`PHASE0_SOURCE_RECONSTRUCTION = PASS / FAIL`

No market-outcome statistics before Phase 0 closes.

## Phase 1 — Structural inventory

Goal:
Describe the source without trading semantics.

For each observable component:
- mathematical definition;
- point-in-time reproducibility;
- lag / responsiveness;
- relationship to price;
- relationship to other source components;
- frequency and persistence.

No BUY / SELL rules.

Closure:
`PHASE1_STRUCTURE_INVENTORY = CLOSED`

## Phase 2 — Event atlas

Freeze a finite event vocabulary from source geometry/state only.

For every event:
- exact definition;
- detection time;
- sample count;
- symbol/time coverage.

Still no rule promotion.

Closure:
`PHASE2_EVENT_VOCABULARY = FROZEN`

## Phase 3 — Forward-behavior study

For the frozen event vocabulary measure:
- 1/3/5/10/20/40-bar forward returns as appropriate;
- mean and median;
- p10/p25/p50/p75/p90;
- MFE / MAE;
- positive rate;
- time-block stability;
- cross-symbol breadth;
- concentration;
- leave-one-symbol-out stability.

This phase asks what tends to happen, not what to trade.

Closure:
`PHASE3_EVENT_BEHAVIOR = COMPLETE`

## Phase 4 — Actionability audit

For effects requiring confirmation or later state information:
- recompute from detection time;
- use next-open execution diagnostic;
- reject any apparent edge that disappears after realistic detection.

Closure:
`PHASE4_ACTIONABILITY = COMPLETE`

## Phase 5 — Strategy formation

Only surviving, executable effects may be assembled into a lifecycle:

`WATCH -> ENTRY -> ADD/HOLD -> REDUCE -> EXIT/INVALIDATE`

The exact vocabulary is not predetermined.

Freeze:
- signal definitions;
- execution semantics;
- position sizing;
- costs;
- risk controls.

No tuning after freeze on the same development sample.

## Phase 6 — Untouched validation

Run the frozen candidate on genuinely untouched data:
- forward OOS and/or
- separately frozen untouched symbols / periods.

Only this phase can support production promotion.
