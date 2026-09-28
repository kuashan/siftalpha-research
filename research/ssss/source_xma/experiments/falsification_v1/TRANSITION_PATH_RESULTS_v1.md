# Falsification v1 — Transition Path Study

Status: COMPLETE UNDER FROZEN PATH PROTOCOL  
Date: 2026-09-28

## Scope

Anchors are independent as-of state transitions, not confluence-conditioned events.

Frozen paths:
- DOWN -> RANGE -> UP / DOWN / STALLED
- UP -> RANGE -> DOWN / UP / STALLED

Maximum:
- 3 states / 2 transitions;
- 60 bars per transition step.

Random baseline:
same symbol, same validation window, same origin state, ordinary non-transition bars, deterministic seed 20260928.

No confluence, HYS2, Volume, VIX, Breadth or Regime split is used.

## Validation A — DOWN -> RANGE

Anchors:
- raw n = 284
- frozen ±2-day market waves = 104
- TARGET path DOWN->RANGE->UP = 177 (62.3%)
- RETURN path DOWN->RANGE->DOWN = 95 (33.5%)
- STALLED_60 = 12 (4.2%)
- median time from RANGE entry to next transition = 13 bars

Same-origin random controls:
- 5680 control draws
- 3659 unique control bars
- 2588 unique controls enter RANGE and are eligible for like-for-like second-step comparison

Conditional on entering RANGE:
- TARGET UP = 1595 (61.6%)
- RETURN DOWN = 906 (35.0%)
- STALLED = 87 (3.4%)

Completed-direction comparison:
- anchor target share among completed UP/DOWN paths: 65.1%
- random RANGE-entry controls target share among completed paths: 63.8%

Difference is small.
DOWN->RANGE does not show a large incremental path-probability separation versus same-origin random paths once RANGE entry is conditioned on.

## Validation A — UP -> RANGE

Anchors:
- raw n = 338
- frozen ±2-day market waves = 143
- TARGET path UP->RANGE->DOWN = 168 (49.7%)
- RETURN path UP->RANGE->UP = 156 (46.2%)
- STALLED_60 = 10
- WINDOW_CENSORED = 4
- median time from RANGE entry to next transition = 13 bars

Conditional same-origin random controls:
- unique RANGE-entry controls = 2522
- TARGET DOWN = 1204 (47.7%)
- RETURN UP = 1184 (46.9%)

Completed-direction comparison:
- anchor target share: 51.9%
- random conditional target share: 50.4%

Again, separation is small.

## Validation B

DOWN -> RANGE:
- anchor n = 17
- wave n = 14
- TARGET = 8
- RETURN = 3
- STALLED = 1
- WINDOW_CENSORED = 5

UP -> RANGE:
- anchor n = 33
- wave n = 17
- TARGET = 10
- RETURN = 14
- STALLED = 2
- WINDOW_CENSORED = 7

Validation B is too small and too censored for a strong path claim, especially DOWN->RANGE n=17.

## Interpretation

The path study does not reveal a large incremental state-path edge.

In Validation A:
- DOWN->RANGE is followed by UP more often than DOWN, but same-origin random controls that later enter RANGE show almost the same conditional split.
- UP->RANGE is approximately balanced between DOWN and return-to-UP, again close to the random conditional baseline.

Therefore common state transitions remain:
**DESCRIPTIVE LIFECYCLE CONTEXT / NOT PROMOTED.**

They are not upgraded into directional signals.

No path subdivision is added after seeing this result.
