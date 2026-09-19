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


## E030 ADD update — 2026-09-19

Rejected at Discovery:
Progress -> Controlled Pullback -> Re-acceleration ADD using the pre-registered six-variant E030 family.

Discovery outcome:
- FastUpper-reset family: only 3 signals across 3 stocks and 0 resolved ADD legs
- FastMid-test/reclaim family: 0 signals

This failed the pre-registered minimum-event gate before any OOS was opened.

State-machine consequence:
- ADD remains RESEARCH / none accepted
- no production transition is added
- do not revive the exact E030 six-variant family under a new name without a materially different hypothesis


## E031 ADD update — 2026-09-19

Rejected at Discovery:
StructuralSep confirmation ADD.

All six pre-registered variants had negative median ADD-leg returns despite several having positive averages and profit factors above 2.

Best-balanced variant S050B still had:
- 34 resolved events
- 25 stocks
- +4.21% average
- -2.90% median

State-machine consequence:
- ADD remains RESEARCH / none accepted
- normalized band separation must not be promoted into a production ADD transition
- the exact E031 family should not be revived without a materially different timing hypothesis


## E032 diagnostic update — 2026-09-19

ADD Opportunity Map found 15 Discovery candidate zones, primarily early/pre-Red and near the original entry.

This does not create an ADD transition.

Interpretation:
- later confirmation has repeatedly produced weak typical incremental returns;
- early marginal economics are materially better;
- the next ADD hypothesis should test a selective early second entry rather than a late confirmation chase.

State-machine status remains:
ADD = RESEARCH / none accepted.


## E033 ADD / sizing update — 2026-09-19

Selective Early Second Entry was rejected at Discovery.

All four candidates had positive per-event economics, but none achieved the required Mature-vs-Failure discrimination.

State-machine consequence:
- ADD remains unvalidated
- no selective early ADD transition is added
- early positive marginal economics should now be studied as a sizing / split-entry problem, not assumed to be a technical confirmation signal


## 15m crypto architecture direction — 2026-09-19

The final state machine is explicitly dynamic and exposure-based.

The current core executes only OPEN / HOLD / CLOSE because intermediate actions are not yet validated.

For the crypto track, research will move toward a native 15-minute model that supports:
- multiple OPEN modes
- ADD
- REDUCE
- RE-ADD
- CLOSE

according to changing causal indicator evidence.

Do not interpret the current single-position daily implementation as the final product design.

The 15m model must be versioned separately; daily parameter counts cannot simply be copied or mechanically rescaled.

Exact exposure percentages remain unfrozen until action triggers are validated.


## E037 BTC 15m dynamic-action update — 2026-09-19

Discovery-only result.

15m role structure is becoming clearer:

STARTER OPEN candidate:
- GREEN_TRANSITION

Direct later confirmation as ADD:
- GRB after starter: reject
- FAST_BREAKOUT after starter: reject
- FASTMID_RECLAIM after starter: reject

ADD opportunity map:
10 candidate cells passed, concentrated early/pre-Red and near/below starter entry.

No REDUCE / RE-ADD / CLOSE map cell passed.

State-machine consequence:
do not add executable actions yet.

The strongest next validation target is an exact early ADD rule derived from the pre-registered opportunity cells, while preserving the current close logic until a superior risk action is independently validated.


## E038 BTC 15m tactical-tranche update — 2026-09-19

No tactical REDUCE / RE-ADD cycle was accepted.

Important role refinement:

GREEN->GRAY after first ADD:
- useful risk checkpoint
- not an unconditional reduce action

It benefited Failure paths but damaged large Mature continuations on average.

RE-ADD:
the first-ADD formula cannot be reused literally because its RunningMFE<1 ATR condition is anchored to the original starter lifecycle and does not reset.

State-machine consequence:
- preserve 30% core exposure through tactical warnings until a full-close condition occurs;
- do not automatically remove the 10% tactical tranche at GREEN->GRAY;
- next research should classify GREEN->GRAY into "temporary weakening" vs "true failure-risk";
- any future RE-ADD rule should use a local post-reduction reset anchor rather than global first-entry MFE.


## E039 probability-sizing update — 2026-09-19

The intended action taxonomy is now explicit:

ADD type 1:
TREND_ADD — high continuation probability while not losing.

ADD type 2:
LOSS_ADD — meaningful current loss but still high continuation probability.

REDUCE type 1:
PROFIT_RISK_REDUCE — profitable position, upside probability still high, but near-term drawdown probability high.

REDUCE type 2:
LOSS_RISK_REDUCE — losing position, upside confidence has weakened into an uncertainty band, and drawdown probability is high.

Sizing intent:
- starter 30%
- each ADD +10 percentage points
- max 50%
- each REDUCE sells 15% of CURRENT position quantity

E039 did not validate these probability actions.

LOSS_ADD provisional research threshold:
-6%, with a -6% to -7% candidate band.

It remains disabled.

Reference CLOSE remains unchanged.


## E040 repeated-pullback update — 2026-09-19

Repeated local pullbacks are now treated separately by action role.

Provisional LOSS_PULLBACK_ADD:
- 1% local pullback
- FastLower must remain intact
- EffectiveState GREEN or RED
- dsep > 0
- current position return < 0
- +10pp exposure
- local anchor resets after action
- max exposure 50%
- Discovery candidate only

Do NOT apply the same rule to profitable positions:
TREND_PULLBACK_ADD at 1% had negative median economics.

Repeated REDUCE:
not accepted.

Risk-state reductions still require a discriminator that avoids cutting Mature continuation winners.

Reference CLOSE remains unchanged.


## E041 loss-add depth update — 2026-09-19

No ADD transition is accepted.

The fixed 1% FastLower LOSS_PULLBACK_ADD was isolated from TREND_ADD and REDUCE.

One-step depth:
- safer path risk;
- but failed concentration and Benchmark-B return gates.

Two-step depth:
- second ADD economics were strong;
- 17 second-add events;
- mean +2.88%;
- median +1.22%;
- stress median +1.16%;
- but portfolio maxDD rose to 11.33% versus the 10.80% frozen ceiling.

State-machine consequence:
- do not activate generic repeated LOSS_ADD;
- do not discard the second LOSS_ADD economics;
- treat the second step as a separate risk-admission problem;
- current reference CLOSE remains unchanged;
- repeated REDUCE remains rejected.

The next useful transition research is:
first LOSS_ADD -> risk-qualified SECOND LOSS_ADD,
not a new pullback-percentage search.
