# Falsification v1 — Closure Report

Status: **CLOSED**  
Date: 2026-09-28  
Branch: research/source-xma-walkforward

## Closure decision

Falsification v1 is formally closed.

The purpose of v1 was not to find a profitable rule.
It was to test whether the strong Jan–Jun 2025 Source-XMA effects generalized under broader holdouts and stronger controls.

They did not.

## Final core decisions

### Upper strict confluence

Registered proposition:
general top / decline rule.

Final status:
**REJECT**

Reason:
Validation A and B do not have consistent direction, and the combined matched/sector-relative effects are near zero.

Current permitted interpretation:
a structural high-side geometry descriptor with no validated general directional edge.

No Regime-dependent explanation is assigned.

### Lower strict confluence

Registered proposition:
incremental buy / rebound information.

Final status:
**REJECT**

Reason:
positive raw rebound is weaker than comparable same-DOWN / overextension-matched controls.

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

## Matching correction

Validation A frozen matching coverage:
- Upper 392/392
- Lower 325/325

Validation B:
- Upper 39/46; all 7 missing events are PLD / Real Estate.
- Lower 12/20; missingness is systematic and higher-ATR events are overrepresented among the unmatchable group.

Therefore B Lower matched results are:
**CONDITIONAL ON MATCHABILITY.**

The v1 repository did not persist selected control-level covariate snapshots, so true pre/post balance SMD cannot be reconstructed.
This is a documented reproducibility limitation, not post-hoc repaired.

## State / lifecycle findings

State density:
- Validation A: UP 51.0%, RANGE 25.8%, DOWN 23.2%
- Validation B: UP 59.9%, RANGE 26.4%, DOWN 13.7%

But confluence density inside the eligible state is stable:
- Upper: ~15.7 vs 15.5 events / 1000 UP bars
- Lower: ~28.6 vs 29.5 / 1000 DOWN bars

Common state transitions and 3-state transition paths do not show material incremental separation from appropriate state/random-path baselines.

FAST_MID_ANALYTIC changes earlier than formal state departure, but crossing direction is not independently predictive.

No time stop is promoted.

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

The registered family is summarized in HYPOTHESIS_LEDGER_v1.md.

A complete BH-FDR vector is not retrofitted because some registered family items lack preserved holdout features or a uniquely frozen scalar test statistic.

No positive result is promoted, so no FDR-based alpha claim is made.

This limitation must be fixed prospectively in v2.

## Sealed future window

Verification across the persisted 873 v1 events:
- earliest event: 2020-02-10
- latest event: 2025-12-29
- any 2026 event: false

Therefore:
**2026H1 remains sealed and unused.**

## CLOSED criteria

- [x] frozen geometry tests completed
- [x] same-state / matched controls completed
- [x] MFE/MAE and extreme robustness completed
- [x] independence / market-wave audit completed
- [x] state transition study completed
- [x] midpoint study completed
- [x] survival/time-to-confirm study completed
- [x] transition-path study completed
- [x] crypto robustness completed
- [x] unavailable auxiliary tests terminally classified
- [x] no Regime rescue
- [x] no post-hoc matching expansion
- [x] Hypothesis Ledger completed
- [x] 2026H1 remains sealed

## Next

No v2 is opened automatically.

Any v2 must begin with a new preregistration file before any sealed-window outcome is inspected.

Candidate v2 protocol improvements may include:
- persist every matched control row and covariate snapshot;
- freeze expanded matching variables prospectively;
- freeze one scalar primary statistic per FDR-family item;
- persist full point-in-time HYS2/Volume/Profile/Breadth/VIX feature panels;
- optionally include repaint-consistency diagnostics;
- define any Regime hypothesis before opening 2026H1.

None of these are active hypotheses yet.
