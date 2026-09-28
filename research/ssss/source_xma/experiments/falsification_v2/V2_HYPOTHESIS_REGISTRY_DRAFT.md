# XMA Falsification v2 Hypothesis Registry Draft

Status: PRE-REGISTRY DRAFT ONLY

Experiment authorization: NOT AUTHORIZED
Data access: NOT AUTHORIZED

## Registry Rules

Every hypothesis must contain:

- Title
- Family
- Condition variable
- Condition definition
- Control variables
- Outcome
- Primary statistic
- Horizon
- Direction
- Test type
- MDE
- Sample floor
- Data required
- Guard

No TBD fields are allowed before Protocol freeze.

## Hypothesis Budget

Maximum: 14 hypotheses.

## Frozen Family Allocation

### F1 Risk (2)

Condition:
- XMA internal state

Outcome boundary:
- ATR-normalized absolute risk only
- No relative return statistics

### F2 Lifecycle (2)

Condition:
- Distance to midpoint

Outcome boundary:
- Transition path probability
- Transition timing
- No MAE, drawdown, or return statistics

Midpoint touch definition:
- |distance-to-mid| <= 0.25 ATR

Extreme distance definition:
- Symbol-level 10% / 90% quantiles
- Neutral range: symbol-level 40% / 60% quantiles

### F3 Cross-sectional (2)

Condition:
- Sector relative strength

Control variables:
- Same-day market return
- Same-day industry return
- Same-day volatility level

### F4 Conditional (4)

Condition:
- Volatility z-score
- Volume z-score

Outcome boundary:
- Matched excess return only

### F5 Risk-Off (4)

Condition:
- Market Breadth
- VIX change

Primary statistic:
- Difference-in-differences

Risk-Off definition must be fixed before Protocol freeze.

## Event and Matching Rules

Event means Episode after continuous-event deduplication.

Matched control uses:
- dev20
- prior20
- ATR14/close

## Guard Registry

Guards are separate from the 14 hypothesis budget.

Each family requires a Null Control Event guard.

Guard matching requirements:
- same symbol distribution
- same time range
- same raw event count
- same wave cluster count
- same matching pipeline
- remove only the tested condition

Guard sample insufficiency pauses family promotion.

## Freeze Rule

This registry cannot add new hypotheses after approval. Hypotheses may only be removed or wording clarified before Protocol freeze.
