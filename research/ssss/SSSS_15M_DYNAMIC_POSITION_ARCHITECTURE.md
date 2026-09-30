# SSSS 15m Dynamic Position Architecture

Date: 2026-09-19
Status: ARCHITECTURE DIRECTION — NOT YET A VALIDATED TRADING RULE

## 1. Product intent

For crypto deployment, SSSS should be researched as a 15-minute event-driven dynamic position system.

It is NOT intended to remain a binary:

OPEN -> HOLD -> CLOSE

system.

Target behavior:

FLAT
-> one of several validated OPEN modes
-> HOLD / ADD / REDUCE / RE-ADD as indicator structure changes
-> CLOSE
-> FLAT

Every position action must be causal and driven by changing indicator evidence.

## 2. Current repository reality

The existing state-machine architecture already targets:

FLAT
-> OPEN
-> POSITION
-> ADD / REDUCE / RE-ADD
-> CLOSE
-> FLAT

However, the current executable core only acts on:
- OPEN
- HOLD
- CLOSE

because:
- ADD has no validated trigger
- REDUCE has candidates only
- RE-ADD has no validated trigger

This implementation limitation must not be mistaken for the intended final architecture.

## 3. 15-minute transfer principle

Do NOT simply reuse the daily parameter counts on 15-minute bars.

Example:
- daily EMA90 represents a slow multi-month structure;
- 15m EMA90 covers only about 22.5 hours.

Also do NOT mechanically time-scale every daily parameter.

For 24/7 crypto:
- 96 x 15m bars per day;
- 90 daily periods would correspond to about 8640 x 15m bars.

That would preserve elapsed time but would not necessarily preserve the economic meaning or desired responsiveness.

Therefore the 15m model must be calibrated as a separate native timeframe while preserving the causal design ideas.

Any parameter change requires its own pre-registered experiment.

## 4. Action-engine concept

The future 15m engine should emit an action intent every completed bar:

- NONE
- OPEN
- HOLD
- ADD
- REDUCE
- RE_ADD
- CLOSE

The engine should also emit:
- mode_id
- reason_code
- evidence state
- current exposure state
- desired exposure delta
- next-bar execution flag

The research unit is not only a complete trade.

It is also each causally available position decision.

## 5. Multiple OPEN modes

The architecture must support more than one OPEN mode.

The existing Qualified GRB becomes only one candidate mode:
- OPEN_GRB

Additional OPEN modes are not yet accepted and must be discovered / validated separately.

Potential mode families may be researched from:
- structural breakout
- pullback / reclaim
- early trend transition
- volatility release
- other materially distinct causal structures

These are research families, not accepted formulas.

No new OPEN mode may be added merely to increase trade count.

## 6. Dynamic exposure state

The state machine should model exposure, not only in-position / out-of-position.

Conceptually:

FLAT
-> STARTER
-> PARTIAL
-> FULLER
-> REDUCED
-> REBUILT
-> FLAT

Exact position percentages are intentionally NOT frozen yet.

This preserves the existing rule:
position size is assigned only after the corresponding action trigger has passed validation.

## 7. Action semantics

### OPEN

Starts exposure from zero.

There may eventually be multiple validated OPEN mode IDs.

### ADD

Increases exposure when post-entry evidence improves.

ADD is not required to wait for a late confirmation if the incremental economics show that late chasing is harmful.

### REDUCE

Cuts part of exposure when tactical risk increases while the full thesis is not yet invalidated.

RTE remains a candidate concept only.

### RE-ADD

Restores previously reduced exposure only after a separately validated recovery condition.

### CLOSE

Removes all remaining exposure when the position thesis is invalidated or the mature lifecycle exits.

## 8. 15m execution convention

For research:
- indicators are computed only from completed 15m bars;
- an action becomes known after the 15m close;
- default execution is the next 15m bar open;
- no intra-bar hindsight;
- fees and slippage must be modeled explicitly.

Crypto is 24/7.

Session boundary assumptions must be explicit even though 15m bars are continuous.

## 9. Cost sensitivity

15m trading may create many more actions than daily trading.

Therefore each experiment must report:
- gross return before costs
- exchange fee assumption
- slippage assumption
- turnover
- action count
- net return after costs

A high-frequency action family that disappears after realistic costs is rejected.

## 10. Research ordering

Before any 15m production rule:

1. repository duplication audit
2. freeze venue / pair / bar convention / data snapshot
3. establish 15m baseline transfer
4. measure action-frequency funnel
5. research multiple OPEN modes
6. research ADD / REDUCE / RE-ADD as state transitions
7. assign position-size deltas only after trigger validation
8. OOS
9. Frozen OOS
10. paper/live timestamp parity audit

## 11. First crypto research target

BTC should be the first 15m development asset.

This does NOT consume future multi-asset OOS automatically.

The first 15m round should determine:
- whether the existing structural ideas produce enough events at 15m;
- which daily assumptions fail when moved intraday;
- how many independent action opportunities exist;
- whether the model can support a true dynamic exposure state machine.

The first round must not optimize every action at once.

## 12. Frozen daily core

Do not modify:
models/ssss_core_v0_1.py

The daily frozen core remains a historical benchmark.

The 15m model must be versioned separately.
