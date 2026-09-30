# AMZN 2023-2025 FIVEGZ5SE Combination Search Cycle 2 — Statistical Pruning

Status: **PRUNING_COMPLETE / SHORTLIST_NOT_FINAL**

Date: 2026-09-29

Development scope:
- AMZN only
- 2023-2025
- SCTYPE=1
- combination-first five-dimension research
- W1/W3/W5 are supporting temporal features

## 1. Purpose

Cycle 1 deliberately searched a broad interpretable combination space.

Cycle 2 does the opposite:
- stop adding new combinations;
- collapse near-duplicate rules;
- compare complex children with simpler parents;
- compare candidate events against year/current-state matched controls;
- use year-stratified bootstrap and permutation checks;
- apply BH-FDR inside the retained pruning family;
- keep the simplest rule when an added condition does not add demonstrable information.

The goal is to reduce the search space before a new trading simulation.

## 2. Fifth-dimension note

The fifth Anomaly dimension is included in this cycle.

A source-logic issue was also confirmed:

`异动浅绿 := CORE_SELL AND HELP_SELL AND VAR4 AND NOT(趋势偏空)`

while

`异动空 := CORE_SELL AND HELP_SELL AND VAR4`

Therefore every bar satisfying `异动浅绿` also satisfies `异动空`.
Because the plotting code draws the green `异动空` layer after light-green,
light-green is not a unique mutually exclusive visual state.

The source formula is **not changed** in this cycle.
The issue is recorded for later formula-governance review.

## 3. Statistical pruning methods

Primary outcome:
- next-session-open to 10-trading-day close return.

Secondary outcomes from Cycle 1:
- 5-day return;
- 20-day return;
- MFE;
- MAE.

Event handling:
- consecutive qualifying bars are de-duplicated into one first-event cluster.

Minimum development candidate requirement:
- n >= 15;
- at least 3 events in each of 2023, 2024, 2025.

### 3.1 Year-stratified bootstrap

Candidate events are resampled within each year.

Report:
- 95% confidence interval of mean 10-day return.

### 3.2 Year-stratified permutation baseline

For each candidate, random dates are sampled while preserving the candidate's
per-year event counts.

This tests whether the event is better/worse than a generic day in the same
calendar-year mixture.

### 3.3 Current-five-state matched control

For each candidate event, controls are drawn from the same:
- year;
- current exact five-dimension state tuple.

This asks a key question:

**Does the path/history condition add information beyond the current colors?**

### 3.4 BH-FDR

BH-FDR is applied across the retained pruning-family tests.

Important limitation:
this does **not** erase the winner's-curse from Cycle 1's thousands of searched
combinations.

A crude 4,110-comparison Bonferroni stress test would not admit any current
candidate at 5%.

Therefore all Cycle-2 survivors remain development candidates, not final
statistically proven signals.

## 4. Redundancy clustering

Near-duplicate event families (Jaccard event overlap >= 0.80) were found.

### B1 cluster

Core B1 plus:
- B1 + bear_now>=2
- B1 + Anomaly=GRAY
- B1 + Acceleration negative >=2/3
- B1 + Acceleration negative >=3/5

These mostly select the same events.

Examples:
- B1 vs +bear_now>=2: Jaccard 0.85
- B1 vs +Anomaly=GRAY: 0.952
- B1 vs +Acceleration negative>=2/3: 0.85
- B1 vs +Acceleration negative>=3/5: 0.95

The added conditions are **not retained in the core rule**.

### B2 cluster

B2 vs B2 + Anomaly=GRAY:
- Jaccard 0.941

The Anomaly=GRAY addition is dropped.

### S1 cluster

S1 vs S1 + 5-bar bullish persistence:
- Jaccard 1.000
- exact same event set

Extra predicate is dropped.

### S2 cluster

S2 + 3-bar bullish persistence and
S2 + 5-bar bullish persistence both reproduce the same event set as S2.

Both are dropped.

### S3 cluster

Adding:
- Anomaly W3 slope >0
- current bullish-dimension count >=3

produces the same event set as S3.

Both are dropped.

## 5. PRUNED BUY FAMILY A — B1

Keep:

```
Trend W3 slope > 0
AND
Momentum = SHORT
AND
Momentum W5 slope < 0
```

Interpretation:

- the short-term Trend path has started improving;
- Momentum is still at the deepest bearish color;
- the five-bar Momentum path has not yet turned upward.

This is an **early-transition / reversal family**.

### Development statistics

n = 20

10-day:
- mean +5.00%
- median +4.85%
- positive 90.0%
- bootstrap 95% mean CI: **+2.90% to +7.18%**

Per-year 10-day mean:
- 2023: +4.89% (n=7)
- 2024: +5.04% (n=5)
- 2025: +5.06% (n=8)

Current-five-state matched test:
- matchable events n=13
- signal minus matched-control mean: **+3.59 pp**
- p = 0.0006
- pruning-family BH q = 0.0016

Year-stratified random-date test:
- excess mean: +3.70 pp
- p = 0.0010

### Why the third condition is retained

Simpler parents:

1. Trend W3 slope>0 + Momentum SHORT
   - n=29
   - mean +3.91%
   - matched p 0.0759

2. Momentum SHORT + Momentum W5 slope<0
   - n=50
   - mean +2.11%
   - matched p 0.9337

3. Trend W3 slope>0 + Momentum W5 slope<0
   - n=51
   - mean +1.64%
   - matched p 0.2147

The three-condition B1 is materially cleaner than any two-condition parent.

### Pruning decision

`B1 = RETAIN_CORE_BUY_FAMILY`

Drop all fourth-condition decorations from the core definition.

## 6. PRUNED BUY FAMILY B — B2

Keep:

```
Capital = GRAY
AND
Capital W1 net change < 0
AND
Acceleration W3 slope > 0
```

Interpretation:

- Capital state is neutral;
- Capital has just deteriorated on W1;
- but Acceleration has been turning upward over W3.

This is a distinct **cooling-capital / improving-acceleration** family.

### Development statistics

n = 17

10-day:
- mean +4.91%
- median +5.06%
- positive 88.2%
- bootstrap 95% mean CI: **+2.48% to +7.14%**

Per-year:
- 2023: +4.69% (n=3)
- 2024: +6.49% (n=3)
- 2025: +4.54% (n=11)

Current-five-state matched:
- matchable n=10
- signal minus control: **+6.71 pp**
- p = 0.0001
- pruning-family BH q = 0.0008

Year-stratified random-date:
- +4.00 pp
- p = 0.0018

### Parent comparison

Two-condition parents:

- Capital GRAY + Capital W1 down:
  n=55, mean +2.44%, matched p=0.0048

- Capital GRAY + Acceleration W3 up:
  n=52, mean +2.06%, matched p=0.0124

- Capital W1 down + Acceleration W3 up:
  n=69, mean +2.50%, matched p=0.0024

All three parents have useful information, but B2 selects a materially stronger
subset.

Adding `Anomaly=GRAY` is unnecessary:
event overlap with B2 is 0.941 and adds too little independent information.

### Pruning decision

`B2 = RETAIN_CORE_BUY_FAMILY`

## 7. PRUNED SELL FAMILY A — S1

Keep:

```
Trend = GRAY
AND
Acceleration positive on >=3 of last 5 bars
AND
>=3 bullish dimensions on >=2 of last 3 bars
```

Interpretation:

the system was recently broadly bullish and acceleration remained positive,
but Trend has fallen back to neutral.

This behaves like a **failed-continuation / exhaustion** state.

### Development statistics

n = 15

10-day:
- mean -2.07%
- median -3.91%
- positive only 40.0%
- bootstrap 95% mean CI: -4.78% to +0.65%

Per-year:
- 2023: -4.01%
- 2024: -1.82%
- 2025: -1.50%

Matched exact-current-state:
- matchable n=8
- difference **-5.80 pp**
- p=0.0016
- BH q=0.0036

Year-stratified random-date:
- difference -3.03 pp
- p=0.0175

The unconditional bootstrap CI crosses zero, so this is retained as a
**de-risk / exit family**, not as proof of a deterministic short signal.

Adding 5-bar bullish-persistence is exactly redundant.

### Pruning decision

`S1 = RETAIN_PRIMARY_DE_RISK_FAMILY`

## 8. PRUNED SELL FAMILY B — S2

Keep:

```
Capital W5 slope < 0
AND
Momentum >= LIGHT_LONG
AND
Anomaly W1 net change < 0
```

Interpretation:

- Momentum still looks bullish;
- Capital has been deteriorating for several bars;
- Anomaly state has just moved downward.

This is a **bullish-surface / internal-deterioration divergence** family.

### Development statistics

n = 15

10-day:
- mean -1.97%
- median -1.75%
- positive only 26.7%
- bootstrap 95% mean CI: **-3.88% to -0.04%**

Per-year:
- 2023: -1.30%
- 2024: -1.92%
- 2025: -2.82%

Year-stratified random-date:
- difference about -3.33 pp
- p=0.0083

Exact five-state matching has only 6 usable events, so a matched-control p-value
is not reported.

The extra `bullbars3` and `bullbars5` conditions are exactly redundant.

### Pruning decision

`S2 = RETAIN_SECONDARY_DE_RISK_FAMILY`

Reason for "secondary":
matched-control sample is too sparse.

## 9. PRUNED SELL FAMILY C — S3

Keep:

```
Momentum = LONG
AND
Anomaly W3 net change > 0
AND
>=3 bullish dimensions on >=2 of last 3 bars
```

Interpretation:

Momentum is maximally bullish and broad bullish persistence already exists,
while the Anomaly dimension has recently jumped upward.

In the AMZN development sample this behaves more like **late-stage
over-extension** than a fresh entry.

### Development statistics

n = 20

10-day:
- mean -2.22%
- median -1.61%
- positive 35.0%
- bootstrap 95% mean CI: -4.64% to +0.17%

Per-year:
- 2023: -1.43%
- 2024: -1.25%
- 2025: -6.98%

Matched:
- n=11
- difference -1.96 pp
- p=0.0233
- BH q=0.0352

Year-stratified random-date:
- difference -3.94 pp
- p=0.0003

However Cycle 1 showed the 20-day mean returns to approximately +0.33%.

Therefore this is not retained as a long-horizon bearish thesis.

### Pruning decision

`S3 = RETAIN_SHORT_HORIZON_DE_RISK_ONLY`

## 10. Rules removed by pruning

### Remove B1 fourth-condition refinements

Drop from core rule:
- bear_now>=2
- Anomaly=GRAY
- Acceleration negative >=2/3
- Acceleration SHORT/LIGHT_SHORT
- Acceleration negative >=3/5

Reason:
high event overlap and no demonstrated independent incremental value.

### Remove B2 Anomaly=GRAY

Reason:
94.1% event overlap; does not justify extra complexity.

### Remove S1 5-bar bullish persistence child

Reason:
identical event set.

### Remove S2 bullish-persistence children

Reason:
identical event set.

### Remove S3 Anomaly-slope and bullish-count children

Reason:
identical event set.

## 11. Search-selection stress test

The within-pruning-family BH q-values are useful for pruning.

They are **not final statistical admission** because Cycle 1 searched thousands
of combinations.

Using a deliberately harsh 4,110-test Bonferroni stress calculation:

- even the strongest matched p-values would not pass 0.05 after multiplying by
  4,110.

This is expected for a development-stage combinatorial search with only three
years of one stock.

Therefore:
- use the statistics to simplify and rank candidate families;
- do not claim final universal significance;
- freeze the shortlist before later overall validation.

## 12. Final Cycle-2 shortlist

### Buy

**BUY-A / B1 — early transition**
```
Trend W3 slope > 0
AND Momentum = SHORT
AND Momentum W5 slope < 0
```

**BUY-B / B2 — capital cooling + acceleration recovery**
```
Capital = GRAY
AND Capital W1 net change < 0
AND Acceleration W3 slope > 0
```

### Sell / de-risk

**SELL-A / S1 — failed bullish continuation**
```
Trend = GRAY
AND Acceleration positive >=3/5
AND >=3 bullish dimensions on >=2/3 recent bars
```

**SELL-B / S2 — internal deterioration while Momentum stays bullish**
```
Capital W5 slope < 0
AND Momentum >= LIGHT_LONG
AND Anomaly W1 net change < 0
```

**SELL-C / S3 — short-horizon over-extension**
```
Momentum = LONG
AND Anomaly W3 net change > 0
AND >=3 bullish dimensions on >=2/3 recent bars
```

## 13. Next step

Do **not** add more predicates yet.

Cycle 3 should use only this pruned shortlist and answer:

1. How should BUY-A and BUY-B interact?
   - union;
   - priority;
   - require confirmation;
   - separate setup types.

2. How should SELL-A/B/C interact with an open position?
   - full exit;
   - partial reduction;
   - priority hierarchy;
   - time stop.

3. What happens when a buy and sell family occur close together?

4. Which combination produces the best complete trading path under:
   - next-open execution;
   - 5 bps slippage;
   - AMZN 2023-2025 only.

Only after Cycle 3 should a new trading logic version be frozen.

Closure:

`AMZN_2023_2025_FIVEGZ5SE_COMBINATION_PRUNING_CYCLE2 = COMPLETE`
