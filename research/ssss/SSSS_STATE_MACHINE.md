# SSSS Position State Machine

Version: v0.1.0

## Target architecture

```
FLAT
  |
  | Qualified GRB
  v
OPEN
  |
  v
POSITION
  |---- ADD ----------> POSITION
  |---- REDUCE -------> REDUCED
  |                       |
  |                       | RE-ADD
  |                       v
  |                    POSITION
  |
  |---- Failure Gray->Green ---> CLOSE ---> FLAT
  |
  |---- Mature Red->Gray ------> CLOSE ---> FLAT
```

## Current maturity

| Action | Status | Current trigger |
|---|---|---|
| OPEN | VALIDATED RESEARCH | Qualified GRB |
| HOLD | ACTIVE | default while position remains valid |
| ADD | RESEARCH | none accepted |
| REDUCE | CANDIDATE | RTE |
| RE-ADD | RESEARCH | none accepted |
| CLOSE (failure) | VALIDATED RESEARCH | Gray -> Green |
| CLOSE (mature) | VALIDATED RESEARCH | Red -> Gray |

## Rejected direct ADD triggers

Do not revive without new evidence:

- Bullish Gray alone
- Effective Red alone
- +1 ATR profit progress alone
- +2 ATR profit progress alone
- Bullish Gray + 1 ATR
- Red + 1 ATR

Reason: averages were often lifted by rare large trends while hit rate / median outcome was weak or reversed out of sample.

## Rejected RE-ADD trigger

```
RTE
-> reduce
-> dsep becomes positive again
-> RE-ADD
```

Observed re-add leg was weak:
- win rate about 30%
- average about -2.34%
- median about -4.86%

## REDUCE candidate

RTE remains the leading candidate for partial de-risking.

Across the currently observed RTE events, RTE pricing was on average above the later final close price, but event count is still small. It is not yet a validated mandatory REDUCE action.

## Design rule

A position percentage is not assigned until the corresponding action trigger has passed validation.

The final model should eventually define:
- initial OPEN allocation
- one or more ADD increments
- one or more REDUCE increments
- RE-ADD logic
- maximum total exposure
- CLOSE of all remaining exposure


## Action Discovery Update — 2026-09-19

The position-state-machine architecture remains unchanged, but several candidate actions were rejected.

### Newly rejected ADD triggers

- repeated Qualified GRB inside the same effective Green episode
- Red-confirmed breakout above the highest price formed between OPEN and Red confirmation

The repeated-GRB candidate failed new out-of-sample validation:
- 5 OOS events
- 20% winning add legs
- average add leg -5.22%
- median add leg -2.44%

The Red-confirmed breakout candidate also had a negative median add leg (-2.63%).

### Newly rejected REDUCE triggers

- No-Progress Gray:
  - first Green->Gray before Red
  - running MFE < 1 entry ATR
  - current close <= original entry price
- Profit-Giveback Raw Gray:
  - effective Red
  - prior MFE >= 2 entry ATR
  - giveback >= 1 entry ATR
  - raw state Gray

Neither showed stable positive economic value out of sample.

### RTE status

RTE remains a candidate REDUCE event only.

Do not convert it into mandatory REDUCE until more independent RTE events are observed.

### Newly rejected RE-ADD trigger

After RTE:
- remain in effective Red
- close above the RTE event-day high
- RE-ADD

This produced weak subsequent legs and typically bought back above the earlier reduction price.


## Tail-risk action update — 2026-09-19

No mandatory tail-loss REDUCE rule has been added to the state machine.

Rejected:
- No-Progress + FastMid
- no-progress drawdown thresholds of 1 / 1.5 / 2 entry ATR
- profit round-trip after prior +2 / +3 ATR MFE
- replacing a full OPEN exposure unit with an Effective-Red delayed unit

Warning-only:
- No-Progress + WhiteLower may be retained as a diagnostic / possible second-stage de-risk signal, but it is not a validated action.

Design implication:
- avoid solving tail risk with blunt early exits
- preserve the early Qualified GRB starter
- discover a non-chasing confirmation point for ADD
- use partial-risk architecture only after the ADD/REDUCE frontier is validated
