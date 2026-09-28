# Falsification v1 — Transition Path Protocol

Status: FROZEN BEFORE PATH OUTCOME ANALYSIS  
Date: 2026-09-28

## Purpose

Study whether already-registered as-of XMA state transitions have reproducible path structure.

This protocol is not allowed to rescue failed Upper/Lower confluence hypotheses.

No confluence, HYS2, volume, breadth, VIX, or Regime subgroup is introduced in this v1 path study.

## Anchor transitions

Two anchor families:

1. DOWN -> RANGE
2. UP -> RANGE

They are generated independently from confluence.

## Maximum path length

Maximum state-sequence length:
**3 states / 2 transitions.**

Primary path families:

From DOWN -> RANGE:
- DOWN -> RANGE -> UP
- DOWN -> RANGE -> DOWN
- DOWN -> RANGE -> STALLED_60
- DOWN -> RANGE -> WINDOW_CENSORED

From UP -> RANGE:
- UP -> RANGE -> DOWN
- UP -> RANGE -> UP
- UP -> RANGE -> STALLED_60
- UP -> RANGE -> WINDOW_CENSORED

No fourth state is added in v1.

## Waiting window

Maximum waiting time from the anchor transition to the next transition out of RANGE:
**60 trading bars.**

The first transition out of RANGE determines the completed path.

No alternative 20/30/40/90-bar threshold is searched after outcomes are inspected.

## Stalling and right-censoring

A sample is:
- STALLED_60 only if a full 60 future trading bars are observed and RANGE is not exited;
- WINDOW_CENSORED if the frozen validation window ends before 60 bars and no RANGE exit has yet been observed.

WINDOW_CENSORED samples remain in the dataset and are never silently dropped.

This intentionally distinguishes genuine observed stalling from insufficient follow-up.

## Random-path baseline

For every anchor transition, sample same-origin-state control anchors:

- same symbol;
- same validation window;
- same exclusive starting state:
  - DOWN for DOWN -> RANGE anchors;
  - UP for UP -> RANGE anchors;
- control bar is not itself the anchor transition;
- exclude +/-20 bars around the same anchor-transition family;
- deterministic seed: 20260928;
- sample up to 20 eligible control anchors.

Each control anchor is followed for the same 60-bar maximum observation window.

Because an ordinary DOWN/UP control bar has not yet entered RANGE, random controls add one explicit category:
- NO_RANGE_ENTRY_60: no transition from the origin state into RANGE is observed within 60 bars.

If RANGE is entered, the control is then classified using the same maximum 3-state sequence:
- origin -> RANGE -> target;
- origin -> RANGE -> origin;
- origin -> RANGE -> STALLED_60;
- WINDOW_CENSORED where follow-up is insufficient.

Report random-path comparisons in two ways:
1. unconditional across all same-origin-state control anchors;
2. conditional on controls that actually enter RANGE within the observation window.

The baseline comparison is path-distribution versus same-origin-state random paths, not path return versus zero.

## Outputs

For each anchor family and validation window report:

- raw anchor n;
- market-wave cluster n;
- completed target-path n/rate;
- reversal-back path n/rate;
- STALLED_60 n/rate;
- WINDOW_CENSORED n/rate;
- random-control NO_RANGE_ENTRY_60 n/rate;
- unconditional random-path rates;
- RANGE-entry-conditional random-path rates;
- time-to-next-transition p25/p50/p75/p90;
- same-origin-state random-path distribution;
- difference versus random baseline;
- symbol/month clustered uncertainty where sample size permits.

Forward returns may be reported descriptively but do not define path success.

## Minimum interpretation rule

- path n <20: hypothesis only;
- n 20-29: OBSERVE;
- n >=30: eligible for interpretation.

No path becomes a trading rule in v1.

## As-of requirement

All transition labels use first-observed point-in-time XMA state.

Final-history repainted states are not substituted into trading-path definitions.

A separate repaint-consistency audit may compare first-observed and final-history states, but it cannot rewrite v1 paths.

## Governance

- no path extension beyond 3 states;
- no waiting-window tuning;
- no Regime split;
- no auxiliary-factor split;
- no confluence-conditioned path rescue;
- no portfolio or position-sizing inference.

Any additional path structure becomes a preregistered v2 hypothesis.
