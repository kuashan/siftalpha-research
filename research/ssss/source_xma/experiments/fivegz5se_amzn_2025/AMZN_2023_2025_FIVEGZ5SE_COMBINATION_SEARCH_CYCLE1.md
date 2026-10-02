# AMZN 2023-2025 FIVEGZ5SE Combination Search Cycle 1

Status: **EXPLORATORY_COMBINATION_SEARCH_COMPLETE**

Date: 2026-09-29

Development scope:
- AMZN only
- 2023-01-01 through 2025-12-31
- SCTYPE=1
- five dimensions: Trend, Capital, Momentum, Acceleration, Anomaly

## 1. Research correction

The research is explicitly **combination-first**.

W1 / W3 / W5 are supporting temporal features and are not treated as the
primary optimization target.

The search objective is to identify repeatable buy/sell structures across
combinations of:
- current five-dimension states;
- cross-dimension interactions;
- W1 / W3 / W5 net changes;
- W3 / W5 slopes;
- positive/negative persistence;
- multi-dimension strengthening / weakening.

## 2. Fifth-dimension correction

The prior frozen V1 replay engine stored only:
- Trend
- Capital
- Momentum
- Acceleration

The current combination search restored the fifth Anomaly dimension from the
original source formula.

Anomaly uses:
- bullish engulfing / hammer / sunrise patterns;
- bearish engulfing / hanging-top / dark-cloud patterns;
- MA20 vs MA60 context;
- VOL vs VOL_MA5 context;
- VAR7 position context;
- trend context for deep/light bullish state.

This means the present search is the first development pass in this sequence
that actually performs full five-dimension combination discovery.

## 3. Search space

Interpretable atomic predicates: **109**

They include:
- current state thresholds for each dimension;
- exact LONG / SHORT / GRAY states;
- W1/W3/W5 net positive/negative changes;
- W3/W5 positive/negative slope;
- W3/W5 persistence counts;
- current number of bullish/bearish dimensions;
- 3-bar / 5-bar multi-dimension bullish/bearish persistence;
- 3-bar / 5-bar multi-dimension improvement/deterioration counts.

Search sequence:
- valid singles: 102
- valid pairs: **4,110**
- retained three-condition buy candidates: 100
- retained three-condition sell candidates: 100
- retained four-condition buy candidates: 80
- retained four-condition sell candidates: 80

Events are de-duplicated:
a consecutive qualifying cluster is counted once at its first qualifying bar.

Minimum candidate gate:
- total event n >= 15
- at least 3 events in each of 2023, 2024 and 2025

Primary ranking horizon:
- 10 trading days

Secondary diagnostics:
- 5-day and 20-day forward return
- win probability
- MFE
- MAE
- per-year 10-day mean

## 4. Important preliminary buy family

A strong recurring family emerged:

```
Trend W3 slope > 0
AND
Momentum = SHORT
AND
Momentum W5 slope < 0
```

De-duplicated events:
- n = 20

10-day mean by year:
- 2023: +4.89%
- 2024: +5.04%
- 2025: +5.06%

Forward distribution:
- 5-day mean +2.57%
- 5-day median +2.32%
- 5-day win rate 75.0%
- 10-day mean +5.00%
- 10-day median +4.85%
- 10-day win rate 90.0%
- 20-day mean +4.75%
- 20-day median +5.33%
- 20-day win rate 75.0%

10-day:
- MFE +7.41%
- MAE -2.84%

Interpretation:
this is **not** a conventional "all dimensions bullish" entry.

It describes a potential early reversal / transition state:
- short-term Trend structure is already improving;
- Momentum is still deeply bearish;
- the five-bar Momentum path is still negative.

The market may therefore be transitioning before Momentum itself changes
color.

This family requires statistical correction because it was discovered after
searching many combinations.

## 5. More selective reversal family

Adding persistent negative Acceleration context:

```
Trend W3 slope > 0
AND
Momentum = SHORT
AND
Momentum W5 slope < 0
AND
Acceleration negative in at least 2 of the last 3 bars
```

n = 17

10-day mean by year:
- 2023: +6.44%
- 2024: +3.88%
- 2025: +5.74%

Forward:
- 5-day mean +2.67%
- 10-day mean +5.55%
- 10-day win rate 94.1%
- 20-day mean +5.76%

This is a stronger-looking but smaller sample.

It is not admitted as the preferred rule yet.

## 6. Alternative buy family

Another distinct family:

```
Capital = GRAY
AND
Capital W1 net change < 0
AND
Acceleration W3 slope > 0
AND
Anomaly = GRAY
```

n = 16

10-day mean by year:
- 2023: +4.69%
- 2024: +6.49%
- 2025: +5.56%

10-day:
- mean +5.57%
- median +5.15%
- win rate 93.8%
- MFE +7.52%
- MAE -3.05%

This is structurally different from the first family and may represent a
"capital cooling while price acceleration turns up" setup.

It must be tested independently rather than merged immediately.

## 7. Preliminary sell / de-risk families

### Sell family A

```
Trend = GRAY
AND
Acceleration positive in at least 3 of the last 5 bars
AND
at least 3 dimensions were bullish on >=2 of the last 3 bars
```

n = 15

10-day mean by year:
- 2023: -4.01%
- 2024: -1.82%
- 2025: -1.50%

Forward:
- 5-day mean -0.76%
- 10-day mean -2.07%
- 10-day median -3.91%
- 10-day positive rate 40.0%
- 20-day mean -2.18%
- 20-day positive rate 33.3%
- 20-day MAE -8.60%

Interpretation:
recent multi-dimension strength combined with Trend falling back to neutral may
be an exhaustion / failed-continuation state.

### Sell family B

```
Capital W5 slope < 0
AND
Momentum >= LIGHT_LONG
AND
Anomaly W1 net change < 0
```

n = 15

10-day mean by year:
- 2023: -1.30%
- 2024: -1.92%
- 2025: -2.82%

10-day:
- mean -1.97%
- median -1.75%
- positive rate 26.7%
- MFE +3.03%
- MAE -6.00%

Interpretation:
Momentum remains bullish while Capital deteriorates and the Anomaly state
turns downward.

This is a possible internal-divergence exit structure.

## 8. What the first search already rejects

The evidence does not support a simple framework such as:
- "more red = better buy";
- "five red = strongest buy";
- "one-bar transition is the whole story";
- "W3 is always better than W1";
- "W5 is always better than W3".

The useful candidates are interaction structures.

For example:
a bearish Momentum color can coexist with an improving Trend path and produce
a strong forward-return candidate.

Therefore color count alone loses important transition information.

## 9. Statistical warning

This cycle searched thousands of combinations.

The top candidate is therefore exposed to:
- multiple-testing bias;
- winner's curse;
- correlated overlapping hypotheses;
- small event counts.

Raw historical performance is not enough.

The next cycle must:
1. cluster near-duplicate logical rules;
2. remove redundant predicates;
3. compare each candidate with matched controls;
4. use year-stratified bootstrap / permutation;
5. perform false-discovery / search-selection adjustment;
6. compare simpler parent rules against more complex child rules;
7. reject extra conditions that do not add statistically meaningful
   incremental information.

No candidate from Cycle 1 is yet called the "best buy" or "best sell".

## 10. Next cycle

Keep the AMZN 2023-2025 scope.

Do not expand to the full universe yet.

The next research cycle is:

`COMBINATION_SEARCH_CYCLE_2_STATISTICAL_PRUNING`

Goal:
reduce the large candidate set into a small number of statistically defensible
buy and sell families before any new trading simulation.

Closure:

`AMZN_2023_2025_FIVEGZ5SE_COMBINATION_SEARCH_CYCLE1 = COMPLETE`
