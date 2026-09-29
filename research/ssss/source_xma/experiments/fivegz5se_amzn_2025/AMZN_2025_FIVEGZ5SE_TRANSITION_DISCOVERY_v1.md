# AMZN 2025 FIVEGZ5SE Transition Discovery v1

Status: **EXPLORATORY_CANDIDATE_LOGIC_IDENTIFIED**

Date: 2026-09-29

Branch start HEAD:
`66db535f33eb393c99668e365a67ae1b514ffb14`

Universe:
- AMZN
- 2025-01-02 through 2025-12-31
- 250 sessions
- FIVEGZ5SE with `SCTYPE=1`
- original author action labels ignored for decision discovery

## 1. Research discipline

This analysis does **not** use formula-native OPEN/CLEAR/REDUCE/RISK labels as
trading rules.

Signals are discovered only from:
- t-1 -> t five-dimension state transitions;
- underlying continuous calculations;
- next-session-open forward outcomes;
- event de-duplication;
- H1/H2 stability checks.

Repeated consecutive qualifying days are collapsed into one event.

## 2. Unconditional AMZN 2025 baseline

From next-session open:

- 5-day mean: +0.08%
- 5-day median: +0.10%
- 5-day positive rate: 51.7%
- 10-day mean: +0.22%
- 10-day positive rate: 54.3%
- 20-day mean: +0.27%
- 20-day positive rate: 51.3%

These are the reference levels.

## 3. Important rejected simplification

The hypothesis "more dimensions turn bullish simultaneously = better buy" does
not hold in this sample.

Event:
- Trend state score improves
- Capital state score improves
- Momentum state score improves
- Acceleration state score improves
all on the same bar.

De-duplicated n = 9.

Forward result:
- 5-day mean: **-1.84%**
- 5-day median: **-2.33%**
- 5-day positive rate: **22.2%**
- 5-day MFE: +1.86%
- 5-day MAE: -4.50%
- 20-day mean: -2.21%

H1 and H2 both had negative 5-day means.

Interpretation:
this pattern is an **anti-chase warning candidate**, not a buy rule.

## 4. Preliminary buy candidate B5

Event is the first bar in a new qualifying cluster where:

1. previous Trend = LIGHT_LONG
2. current Trend = LIGHT_LONG
3. previous Acceleration = LONG
4. current Acceleration = LONG
5. current RVOL20 is between 0.8 and 1.5

No author signal label is required.

Event dates:
- 2025-01-22
- 2025-05-30
- 2025-06-03
- 2025-06-09
- 2025-06-30
- 2025-07-07
- 2025-07-21
- 2025-08-15
- 2025-10-22
- 2025-10-24

De-duplicated n = 10.

Forward outcomes:

### 3 trading days
- mean +0.76%
- median +1.10%
- positive 70.0%
- MFE +1.95%
- MAE -1.78%

### 5 trading days
- mean **+2.44%**
- median **+1.31%**
- positive **70.0%**
- MFE +3.71%
- MAE -2.00%

### 10 trading days
- mean **+2.53%**
- median **+2.76%**
- positive **70.0%**
- MFE +5.85%
- MAE -2.75%

### 20 trading days
- mean +1.11%
- median +1.24%
- positive 70.0%

H1/H2 split:

H1:
- 5-day mean +2.09%, positive 60%
- 10-day mean +1.93%, positive 80%

H2:
- 5-day mean +2.79%, positive 80%
- 10-day mean +3.12%, positive 60%

Interpretation:
the strongest pilot pattern is not a bottom-picking state. It is a
**controlled continuation entry**:
trend is already mildly positive, acceleration remains strongly positive, but
relative volume is not an extreme spike.

The 20-day edge fades, suggesting this is currently a short-to-medium swing
candidate rather than a long holding signal.

Important:
the 0.8-1.5 RVOL range is exploratory and requires larger-sample validation.

## 5. Preliminary sell/de-risk candidate S0

Event is the first bar in a new qualifying cluster where acceleration remains
inside the bearish zone but changes severity:

- LIGHT_SHORT -> SHORT
or
- SHORT -> LIGHT_SHORT

In this AMZN sample all such events also occur with Trend <= LIGHT_LONG and
Momentum <= GRAY, so adding those restrictions does not change the event set.

De-duplicated n = 13.

Forward outcomes:

### 3 trading days
- mean -1.37%
- median -0.77%
- positive 23.1%
- MFE +1.60%
- MAE -3.09%

### 5 trading days
- mean **-2.37%**
- median **-3.94%**
- positive **30.8%**
- MFE +1.97%
- MAE -4.84%

### 10 trading days
- mean **-3.19%**
- median **-4.75%**
- positive 30.8%
- MFE +2.56%
- MAE -7.22%

### 20 trading days
- mean **-6.02%**
- median **-4.42%**
- positive 23.1%
- MFE +2.56%
- MAE -10.79%

H1:
- 5-day mean -3.77%
- 10-day mean -6.17%

H2:
- 5-day mean -1.17%
- 10-day mean -0.63%

Interpretation:
this pattern is strongest as a **tail-risk / de-risk candidate**, not yet a
universal deterministic full-exit rule. The second-half effect is weaker and
has more positive observations, although average downside remains negative.

## 6. Secondary deterioration candidate

Trend transition:

`LONG -> LIGHT_LONG`

De-duplicated n = 8.

- 5-day mean -2.30%
- 5-day median -1.25%
- positive rate 12.5%
- 5-day MAE -4.06%

This is directionally strong but sample size is very small.

It is therefore retained as a secondary exit-confirmation candidate, not
admitted as a standalone rule.

## 7. Combined de-risk candidate

A broad pilot de-risk event is:

- Trend LONG -> LIGHT_LONG
OR
- bearish-zone acceleration transition S0

De-duplicated n = 21.

- 5-day mean -2.34%
- median -2.09%
- positive 23.8%
- 10-day mean -2.64%
- 20-day mean -4.22%

This has more coverage but H2 is materially weaker than H1.

## 8. Candidate operation logic for the next trading simulation

The next simulation should use a deliberately simple binary position model so
that signal quality is tested before position-sizing optimization.

### ENTRY_CANDIDATE_V0

At close t, open a long at next-session open only when a **new event cluster**
begins and:

```
Trend(t-1) = LIGHT_LONG
Trend(t)   = LIGHT_LONG

Acceleration(t-1) = LONG
Acceleration(t)   = LONG

0.8 <= RVOL20(t) <= 1.5
```

Additional rules:
- do not enter again on each consecutive qualifying day;
- do not require the author formula's OPEN label;
- do not require all five dimensions to be red;
- do not enter when all four core state scores jump upward on the same bar.

### HOLD

Hold after entry while no exit condition fires.

Pilot maximum holding horizon:
**10 trading days**.

Reason:
the observed B5 edge is strongest around 5-10 days and weakens by 20 days.

### EARLY_DE_RISK / EXIT_CANDIDATE_V0

Exit or de-risk at the next-session open if either:

A.
`Trend: LONG -> LIGHT_LONG`

or

B.
Acceleration makes one of the bearish-zone transitions:
`LIGHT_SHORT -> SHORT`
or
`SHORT -> LIGHT_SHORT`

For the first strategy simulation, test:
1. full exit;
2. 50% reduction followed by full exit only if weakness persists.

These are separate variants and must not be optimized after seeing the final
equity curve without a new validation split.

### ANTI_CHASE_VETO_V0

Do not open a fresh position when on the same bar:

```
dTrendState > 0
AND dCapitalState > 0
AND dMomentumState > 0
AND dAccelerationState > 0
```

In AMZN 2025 this looked more like a late over-extension event than an early
entry.

## 9. What is and is not established

Established for this pilot:
- current color snapshot alone is insufficient;
- t-1 -> t transition adds useful structure;
- repeated-state rows must be de-duplicated into events;
- all-dimensions-turn-up is not automatically bullish;
- a mild-positive-trend + persistent-positive-acceleration + normal-RVOL
  continuation structure is the best current entry candidate;
- negative acceleration-zone transitions are the best current de-risk family.

Not established:
- statistical universality;
- optimal RVOL thresholds;
- optimal holding period;
- optimal position size;
- whether full exit or partial reduction is superior;
- cross-stock robustness.

The one-year single-symbol sample is too small for final statistical
admission.

## 10. Next research cycle

Freeze the above candidate logic as V0 and run a **true trading simulation**
on AMZN 2025:
- signal at close t;
- execution at t+1 open;
- no look-ahead;
- no duplicate same-cluster entries;
- binary long/cash first;
- compare 5-day, 10-day, and early-exit variants;
- calculate total return, drawdown, Sharpe, trade count, hit rate, average
  trade, MFE/MAE and exposure.

Only after that simulation should position sizing be considered.

Research state:

`AMZN_2025_FIVEGZ5SE_CANDIDATE_LOGIC_V0 = EXPLORATORY_CANDIDATE_IDENTIFIED`

Not yet:
`IMPLEMENTED_AND_VERIFIED`
