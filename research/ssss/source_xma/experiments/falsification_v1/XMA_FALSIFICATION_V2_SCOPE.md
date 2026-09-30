# XMA Falsification v2 Scope

Status: SCOPE ONLY / NO EXPERIMENT AUTHORIZED
Date: 2026-09-28

## 0. Why v2 Exists

v2 does not exist because v1 failed to find a signal and needs another search.

v1 already demonstrated that XMA geometry alone does not constitute a validated directional trading signal under independent validation.

Therefore v2 studies a different question:

> Whether XMA geometry, as a condition variable, provides incremental information inside other defined contexts.

v2 does NOT study:

- XMA geometry as a standalone entry signal;
- parameter optimization of v1 hypotheses;
- rescue of rejected v1 propositions.

## 1. Forbidden Re-test List

### REJECT class

Includes:

- Upper confluence as a general top/decline signal;
- Lower confluence as a general incremental buy/reversal signal.

Operation rule:

These cannot be retested with the same definition, universe, and window.

A future test requires:

- new asset universe;
- new mathematical definition;
- new preregistered reason why it is not a renamed v1 hypothesis.

### OBSERVE / NOT PROMOTED class

Includes:

- state transition lifecycle effects;
- transition path analysis;
- FAST_MID_ANALYTIC;
- time-to-confirm analysis.

Operation rule:

Retesting is allowed only with:

- new data;
- new preregistration;
- independent validation window;
- explicit comparison against the original definition.

If the original definition fails again under the new protocol, it must receive a terminal classification and cannot remain permanently OBSERVE.

### INCONCLUSIVE / DATA NOT AVAILABLE class

Includes:

- BELOW_VAL;
- HYS2 interaction;
- Volume;
- Breadth;
- VIX expanded dimensions.

Operation rule:

These may be revisited only after solving the data availability problem.

Repeated inability to obtain required data cannot create permanent INCONCLUSIVE status.

## 2. v1 Lessons — Out-of-sample Decay

v1 showed that discovery-sample effects may decay or reverse outside the discovery period.

Discovery effects must not be treated as expected future effect sizes.

v2 rule:

Any discovery effect size must assume decay before promotion.

A v2 hypothesis must define:

- discovery effect;
- expected decay assumption;
- minimum detectable effect;
- promotion threshold.

Discovery performance cannot be used to estimate strategy capacity.

## 3. XMA as Condition Variable

v1 question:

"Can XMA geometry predict direction?"

v2 question:

"Can XMA geometry provide incremental information when combined with another defined context?"

Research categories:

### Risk Management

Possible statistics:

- MAE distribution;
- drawdown difference;
- holding duration difference.

### Position Lifecycle

Possible statistics:

- conditional transition probability;
- lifecycle outcome distribution.

### Cross-sectional Ranking

Possible statistics:

- relative return ranking;
- cross-sectional information coefficient.

### Conditional Information

Possible statistics:

- interaction effects with other frozen variables.

Each future hypothesis must define:

- one primary statistic;
- minimum detectable effect;
- required data fields.

## 4. Hard Gates Before Any Experiment

Required before data analysis:

1. Match control persistence
- identities;
- dates;
- covariates;
- distances.

2. Primary statistic freeze

Each hypothesis defines exactly one primary statistic before outcome inspection.

3. FDR family freeze

The family and correction method are fixed before testing.

4. Data availability audit

Required fields, coverage, universe, and date range must be recorded before analysis.

5. Sample size floor

Each hypothesis must define minimum:

- raw episodes;
- market-wave clusters;
- symbol clusters;
- ESS reporting method.

## 5. Sealed Window Rules

2026H1 is not an untouched holdout because Validation B forward horizons entered that period.

A v2 sealed window must:

- begin after v2 protocol freeze;
- remain inaccessible before freeze;
- not overlap any previous forward horizon exposure.

No sealed window is selected by this scope document.

## 6. Exit Condition

If all v2 condition-variable hypotheses are rejected under the frozen protocol:

XMA geometry research terminates.

No v3 is automatically opened.

The final conclusion would be that XMA geometry does not provide actionable incremental information at the tested market scale and timeframe.

## 7. What v2 Will NOT Do

v2 will not:

- search for new signals without preregistration;
- optimize v1 parameters;
- perform Regime Mining after observing results;
- convert rejected hypotheses into renamed hypotheses;
- open experiments before protocol freeze.

## Current Status

v2 Scope drafted.

Next steps:

1. Review this scope.
2. Freeze v2 protocol.
3. Commit protocol before selecting sealed window.
4. Only then authorize experiments.
