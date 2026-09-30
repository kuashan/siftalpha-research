# XMA Falsification v2 — Protocol Design One-Pager Amendment v2

Status: PRE-PROTOCOL DESIGN AMENDMENT ONLY

No experiment authorized.
No data access authorized.
No sealed window selected.

This amendment supplements the approved One-Pager and supersedes only the conflicting items identified below.

## 1. Hypothesis Budget Supersession

The earlier `V2_PROTOCOL_DESIGN_ONEPAGER_AMENDMENT_v1.md` stated a total-hypothesis maximum of 12.

That limit is superseded.

Final frozen formal hypothesis budget:

- F1 Risk: 2
- F2 Lifecycle: 2
- F3 Cross-sectional: 2
- F4 Conditional: 4
- F5 Risk-Off: 4

Total formal hypotheses: **14 maximum**.

Guard controls G-F1 through G-F5 are separate methodological controls and do not count toward the 14 formal hypotheses.

No candidate variable may be added or replaced.

## 2. F1 / F2 / F4 / F5 Boundary Freeze

F1 Risk:
- condition source: discrete XMA state;
- primary outcomes: absolute risk metrics only;
- no matched-excess-return primary statistic.

F2 Lifecycle:
- condition source: distance to midpoint / XMA lifecycle geometry;
- primary outcomes: path probability or transition timing only;
- no MAE, drawdown, or return primary statistic.

F4 Conditional:
- condition source: external variable × XMA state;
- primary outcome: matched excess return only.

F5 Risk-Off:
- condition source: predefined Breadth or VIX stress × XMA state;
- primary outcome: difference-in-differences effect only;
- may test only whether XMA information weakens under predefined risk stress;
- may not search for the environment where XMA performs best.

## 3. Event Unit Freeze

For v2 Registry purposes, an event is an **Episode** after continuous-event deduplication.

A single qualifying bar is not an independent event.

Market-wave clustering is reported separately using the frozen ±2 trading-day linkage definition.

## 4. Matched-Control Covariates

Matched-control distance variables remain:

- dev20;
- prior 20-bar return;
- ATR14 / close.

Any additional matching covariate requires a later formal Amendment.

Control-pool eligibility is hypothesis-specific and must be explicitly stated in the Registry.

## 5. F2 Midpoint Definitions

Midpoint touch:
- `abs(distance-to-mid) <= 0.25 ATR14`.

H4 distance groups:
- extreme: symbol-level <=P10 or >=P90;
- neutral: symbol-level P40 through P60.

## 6. Sample Floor and MDE Freeze

Default hypothesis sample floor:

- raw Episodes >=100;
- market-wave clusters >=30;
- symbol clusters >=20.

F1 MDE:
- 0.5 ATR.

F2 H3 MDE:
- 10 percentage points absolute probability difference.

F2 H4 MDE:
- 3 bars absolute waiting-time difference.

F3 MDE:
- 0.03 correlation / IC units.

F4 MDE:
- 0.5 percentage points 10-bar matched excess.

F5 MDE:
- -0.5 percentage points or lower for the preregistered DiD direction.

No sample floor may be lowered because a Risk-Off sample is sparse.

## 7. Guard Freeze

Each family has one methodological guard entry:

- G-F1
- G-F2
- G-F3
- G-F4
- G-F5

Each guard must preregister:
- deterministic generation rule;
- random seed where permutation is required;
- sample-matching rule;
- primary statistic;
- MDE;
- sample floor;
- insufficiency handling.

Guard failure or insufficiency blocks family promotion.

## 8. Sealed-Window Unlock

Unlock occurs on the first date when all requirements are simultaneously satisfied:

- duration >=12 months;
- raw Episodes >=100 for every hypothesis;
- market-wave clusters >=30 for every hypothesis;
- symbol clusters >=20 for every hypothesis.

The calendar anniversary alone does not unlock the sealed window.

If any hypothesis remains below floor, continue waiting.

## Status

These constraints are frozen inputs to the v2 Hypothesis Registry Draft and future Protocol.

Experiment remains NOT AUTHORIZED.
