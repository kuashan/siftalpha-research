# Falsification v1 — Closure Report

Status: **CLOSED WITH INTEGRITY QUALIFICATIONS**  
Date: 2026-09-28  
Branch: research/source-xma-walkforward

## Closure decision

Falsification v1 is terminally closed for hypothesis testing, with post-closure integrity qualifications documented in:

- `POST_CLOSURE_INTEGRITY_AUDIT_v1.md`
- `POST_CLOSURE_INTEGRITY_AUDIT_v1.json`

The purpose of v1 was not to find a profitable rule.
It was to test whether the strong Jan–Jun 2025 Source-XMA effects generalized under broader holdouts and stronger controls.

They did not.

The integrity audit does not reopen, repair, or rescue any failed hypothesis.

## Final core decisions

### Upper strict confluence

Registered proposition:
general top / decline rule.

Final status:
**REJECT**

Reason:
Validation A and B do not have consistent direction, and the combined matched/sector-relative effects are near zero.

The post-closure boundary audit does not change that decision:
removing the one Validation B Upper event whose own 5-bar outcome falls in 2026 changes the raw 5-bar mean from about -0.63% (n=46) to about -0.72% (n=45).

Current permitted interpretation:
a structural high-side geometry descriptor with no validated general directional edge.

No Regime-dependent explanation is assigned.

### Lower strict confluence

Registered proposition:
incremental buy / rebound information.

Final status:
**REJECT**

Reason:
positive raw rebound in Validation A is weaker than comparable same-DOWN / overextension-matched controls.

The post-closure boundary audit also does not rescue Validation B:
- 10-bar raw remains about -0.97% after excluding the one event whose own 10-bar horizon enters 2026;
- 20-bar raw remains about -1.75% after restricting to events whose own 20-bar horizon remains in 2025.

Current permitted interpretation:
Extreme / Dislocation Context only.

## Independence correction

Raw episodes are not treated as independent market contexts.

Combined equities:
- Upper: 438 episodes -> 192 frozen ±2-day market-wave clusters.
- Lower: 345 episodes -> 130 frozen ±2-day market-wave clusters.

±5-day linkage sensitivity:
- Upper -> 72 waves.
- Lower -> 60 waves.

Wave count is not called ESS.

Approximate ICC-based ESS is reported separately in INDEPENDENCE_AUDIT_v1 and is metric-specific.

## Matching correction and boundary qualification

Validation A frozen matching coverage:
- Upper 392/392
- Lower 325/325

Validation B:
- Upper 39/46; all 7 missing events are PLD / Real Estate.
- Lower 12/20; missingness is systematic and higher-ATR events are overrepresented among the unmatchable group.

Therefore B Lower matched results remain:
**CONDITIONAL ON MATCHABILITY.**

The v1 repository did not persist selected control identities, dates, and control-level covariate snapshots.

Consequences:
1. true event-vs-control pre/post balance SMD cannot be reconstructed;
2. after discovering the Validation B / 2026 boundary issue, it is also impossible to verify that every selected control's own forward-return horizon stayed inside 2025.

The post-closure event-horizon-only sensitivity remains negative:
- Upper B 5-bar matched excess: about -1.67% on n=39 originally; about -1.88% on the 38 matchable events whose own event horizon stays in 2025;
- Lower B 10-bar: about -1.39% on n=12 originally; about -1.53% on 11 event-horizon-safe matchable events;
- Lower B 20-bar: about -2.76% on n=12 originally; about -4.24% on 11 event-horizon-safe matchable events.

These are not relabeled as fully boundary-corrected matched estimates because the selected controls' dates were not persisted.

Required provenance label:
**NOT CLEANLY AUDITABLE FROM PERSISTED CONTROL-LEVEL DATA.**

This is a documented reproducibility limitation, not a post-hoc repair.

## State / lifecycle findings

The originally reported State Density values are:

- Validation A: UP 51.0%, RANGE 25.8%, DOWN 23.2%
- persisted Validation B reconstruction: UP 59.9%, RANGE 26.4%, DOWN 13.7%

But the State Density artifact itself ends Validation B on 2025-12-30 and uses 127 trading bars, while the frozen Validation B window ends 2025-12-31 and other persisted transition/midpoint artifacts contain 2025-12-31 records.

Therefore the Validation B density values are retained only as a **partial-window descriptive reconstruction**, one trading day short of the frozen window.
They must not be represented as full 2025-07-01..2025-12-31 occupancy.

The originally reported conditional event densities remain descriptive:
- Upper: ~15.7 vs 15.5 events / 1000 UP bars
- Lower: ~28.6 vs 29.5 / 1000 DOWN bars

They do not establish an edge or a Regime explanation.

FAST_MID_ANALYTIC changes earlier than formal state departure, but crossing direction is not independently predictive.

No time stop is promoted.

### Transition-path integrity qualification

The transition-path result remains:
**OBSERVE / NOT PROMOTED.**

However, the path protocol was materially modified after the earlier artifact at commit `a827b995f4325263a47c74f00beb81b9d1eb9160` was already labeled frozen.

Later changes include:
- changing random-control timing to 60 bars per transition step;
- excluding any transition bar from controls rather than only the anchor transition;
- adding NO_RANGE_ENTRY_60 and DIRECT_EXIT_NO_RANGE categories;
- adding unconditional and RANGE-entry-conditional random baselines.

No preserved numbered amendment proves these changes were frozen before path outcomes were computed.

Therefore the path study carries:
**PROTOCOL-INTEGRITY CAVEAT / OBSERVE / NOT PROMOTED.**

No deeper path subdivision or same-window rerun is opened.

## Auxiliary features

Expanded holdout auxiliary features were not preserved.

Terminal classifications:
- BELOW_VAL: INCONCLUSIVE / DATA NOT AVAILABLE
- HYS2 interaction: INCONCLUSIVE / DATA NOT AVAILABLE
- Volume: INCONCLUSIVE / DATA NOT AVAILABLE
- Breadth: INCONCLUSIVE / DATA NOT AVAILABLE
- VIX: INCONCLUSIVE / DATA NOT AVAILABLE

HYS2 fire-bottom/top:
**REDUNDANT WITHIN STRICT XMA EVENT SAMPLE**
only.

## Crypto

Crypto is separated from equities from the data/report level.

No pooled stock+crypto model is used.

Upper crypto means are highly extreme-value sensitive:
the BNB 2021-02-01 event returned about +473.6% over 20 bars and contributes ~39.8% of absolute Upper-A 20-bar movement.

Crypto does not rescue either general confluence proposition.

## Multiple testing

The frozen protocol required the primary family to be controlled with Benjamini-Hochberg FDR q=0.10.

A complete BH-adjusted vector cannot be produced as preregistered because:
- some expanded-holdout feature tests lack preserved Validation A/B feature data;
- some registered family items do not have one uniquely frozen scalar p-like statistic.

Choosing those missing scalar tests after seeing outcomes would be a post-hoc specification change.

Terminal integrity classification:
**BH-FDR FAMILY: INCONCLUSIVE / NOT FULLY COMPUTABLE AS PREREGISTERED.**

No positive result is promoted and no FDR-based alpha claim is made.

This limitation must be fixed prospectively in v2.

## 2026H1 boundary correction

The previous closure statement that "2026H1 remains sealed and unused" is retracted.

The event-date-only check was insufficient.

The frozen protocol says 2026-01-01 through 2026-06-30 is not used in Validation A/B, but persisted Validation B forward outcomes include January 2026 dates.

Confirmed examples include:
- BAC Upper event 2025-12-29 -> 5-bar outcome 2026-01-06;
- COST Lower event 2025-12-17 -> 10-bar outcome 2026-01-02;
- four Lower 20-bar outcomes extending into January 2026;
- transition/midpoint records with 2026 forward outcomes, including PLD MID_DOWN on 2025-12-31 -> 5-bar 2026-01-08 and 10-bar 2026-01-15.

Therefore:
**2026H1 is contaminated and is no longer eligible as an untouched v2 holdout.**

This boundary correction does not reverse any v1 REJECT decision.

## CLOSED criteria — corrected

- [x] frozen geometry tests completed
- [x] same-state / matched controls completed
- [x] MFE/MAE and extreme robustness completed
- [x] independence / market-wave audit completed
- [x] state transition study completed
- [x] midpoint study completed
- [x] survival/time-to-confirm study completed with validation-window right-censoring
- [x] transition-path study completed, with post-freeze protocol-integrity caveat documented
- [x] crypto robustness completed
- [x] unavailable auxiliary tests terminally classified
- [x] no Regime rescue
- [x] no post-hoc matching expansion
- [x] Hypothesis Ledger completed
- [!] complete BH-FDR vector was not computable as preregistered
- [!] State Density Validation B reconstruction is one trading day short
- [!] 2026H1 seal was breached by persisted Validation B forward outcomes

The terminal status is therefore:

**FALSIFICATION v1 = CLOSED WITH INTEGRITY QUALIFICATIONS**

## Next

No v2 is opened automatically.

2026H1 must not be used as an untouched future validation window.

Any v2 must begin with a new preregistration file before the new independent outcome window is inspected.

A future v2 must use either:
- a new prospectively protected independent time window; or
- a new frozen universe with independently protected outcomes.

Prospective protocol improvements include:
- persist every matched control row, date, covariate snapshot, and forward-outcome date;
- enforce outcome-horizon censoring at the validation-window boundary;
- freeze expanded matching variables prospectively;
- freeze exactly one scalar primary statistic per FDR-family item;
- persist full point-in-time HYS2/Volume/Profile/Breadth/VIX feature panels;
- optionally include repaint-consistency diagnostics;
- record any protocol amendment as a separate immutable pre-outcome artifact.

None of these are active hypotheses yet.
