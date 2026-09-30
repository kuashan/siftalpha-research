# Research Checkpoint — 2026-09-19 — E038 BTC 15m Tactical Tranche

## Status
NO_TACTICAL_REDUCE_CANDIDATE

## Architecture tested

30% core
+ 10% first ADD
-> temporary tactical 10% REDUCE
-> optional tactical 10% RE-ADD
-> unchanged reference CLOSE

Eligible first-ADD lifecycles:
32.

## REDUCE

### GREEN->GRAY after ADD
32 events.

Failure paths:
strongly benefited from tactical reduction.

Mature paths:
large continuation winners made the average incremental value strongly negative.

Conclusion:
risk checkpoint, not unconditional REDUCE.

### Post-Red MFE>=4 + giveback>=0.5 ATR
18 events.

Typical event sometimes benefited, but mean incremental value was -1.95%.

Reject.

### RTE after MFE>=2 ATR
12 events.

Too sparse and negative median incremental value.

Reject.

## RE-ADD

Exact first-ADD reuse:
- 5/32 after GREEN->GRAY
- 0/18 after mature giveback
- 0/12 after RTE

Reason:
RunningMFE<1 ATR is cumulative and does not reset later in the lifecycle.

Alternative GREEN / dsep / FastMid recovery rules also failed the pair-level economics.

## CLOSE

No tested REDUCE checkpoint showed stable evidence supporting full close earlier than the existing reference close.

## Core lesson

The next problem is classification, not another blunt threshold.

At GREEN->GRAY after early ADD, distinguish:
- temporary weakening inside a future Mature path
from
- true Failure risk.

A future RE-ADD rule should use local post-reduction state rather than original-starter cumulative MFE.
