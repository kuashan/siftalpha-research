# FIVEGZ5SE Five-Dimension Signal Discovery Audit & Research Protocol v1

Status: **PROTOCOL_FROZEN_BEFORE_LARGE_SAMPLE_REPLAY**

Date: 2026-09-29

Repository branch:
`research/source-xma-walkforward`

Protocol start HEAD:
`eab1d1e26592673fb6cd2af260c05b6dd250b6c0`

Source:
- user-supplied `FIVEGZ5SE.txt`
- SHA-256: `61bc9f7cad7a2efb6374a187c680fa75789b2468824885e5127c5f70333400c9`
- size: 93,201 bytes

Market mode for this research:
`SCTYPE = 1` (HK/US mode)

---

## 1. Research objective

The purpose of this project is **not** to validate the indicator author's
display labels such as "清仓", "抄底", "主升", "逃顶", or to assume that
five red states are automatically a buy and five green states are
automatically a sell.

The objective is to discover, from large historical samples, which
five-dimension state transitions and which changes in the underlying numerical
calculations carry the strongest repeatable information about subsequent price
behavior.

The core observation unit is:

`previous bar (t-1) -> current bar (t)`

For each of the five dimensions:
1. Trend
2. Capital/volume
3. Momentum
4. Acceleration
5. Anomaly/candlestick

we record:
- previous discrete state/color;
- current discrete state/color;
- underlying numerical calculation at t-1;
- underlying numerical calculation at t;
- first difference;
- where meaningful, second difference / acceleration;
- distance from the thresholds that separate state categories.

The primary research question is therefore not:

`What color is the current bar?`

but:

`How did each dimension move from t-1 to t, how large was the move, and what happened after t?`

---

## 2. Formula-governance rules

### 2.1 Freeze the original indicator first

The original FIVEGZ5SE formula is frozen for the first research pass.

No threshold is changed after seeing a backtest result.

No author label is promoted into trading truth.

Any possible formula defect is documented separately and tested with a
sensitivity analysis before a corrected variant is allowed.

The original and any corrected variants must always remain separately named.

### 2.2 SCTYPE is fixed

All US-stock research in this protocol uses:

`SCTYPE = 1`

Important SCTYPE=1 values include:
- ATR_FILTER_LIMIT = 0.35
- HSL_LOCK_RATIO = 0.65
- relative-volume healthy range = 0.4 to 12
- VOL_BUY_MIN = 1.0
- VOL_SELL_BURST = 1.2
- SLOPE_BUY_STRONG = 2.0
- MOM_STD_RATIO = 0.35
- US-market high-position multipliers from the original source

No SCTYPE=0 or SCTYPE=2 observation is pooled into the primary US result.

### 2.3 Point-in-time rule

For bar t:
- only data available through the close of t may be used;
- the t state is compared with t-1;
- no t+1 or later price is allowed into the state calculation;
- a tradable signal formed at the close of t can first execute at the open of
  t+1.

This rule applies even where the formula itself does not appear to repaint.

---

## 3. Future-function audit

Current source audit found no use of the usual forward-looking structures:
- ZIG
- BACKSET
- REFX
- negative REF(...,-N)
- PEAK
- TROUGH
- DYNAINFO
- CURRBARSCOUNT

The formula does use:

`FORCAST(X,N)`

The research implementation treats this as a rolling historical linear
regression evaluated at the current endpoint, using only the latest N
available historical observations.

`ISLASTBAR` occurs extensively in display-text logic, but is not treated as a
historical state input.

Current status:

`FUTURE_FUNCTION_AUDIT = PROVISIONAL_PASS`

Final engine parity still requires spot-checking selected Futu dates after the
reproduction engine is built.

---

## 4. Known formula issues that must not be silently repaired

### 4.1 Momentum continuity is effectively disabled

The source contains:

`MOM_CONTINUOUS_DAYS := 0`

therefore:

`BARSLASTCOUNT(condition) >= 0`

does not impose a meaningful persistence requirement.

This is retained in the original-source replay.

A later sensitivity test may compare it with positive continuity values, but
that is a different variant.

### 4.2 Several COUNT annotations overstate the implemented logic

Patterns such as:

`COUNT(A OR B OR C, N)`

count the number of bars within the lookback on which at least one of
A/B/C was true.

They do not count how many independent dimensions are simultaneously true.

Therefore labels such as "multi-dimension synchronous turn" or "three
dimensions weaken" cannot be accepted at face value.

### 4.3 Display labels are hypotheses, not targets

For example:
- "清仓" is a rule-defined state, not proof that immediate full liquidation is
  optimal;
- "底部双重背离" is not automatically a mathematical divergence;
- "主力资金" is an interpretation of price/volume conditions, not direct
  observation of institutional flow.

The research uses the actual numerical conditions, not the wording.

---

## 5. Five-dimensional observation schema

Every eligible symbol-date creates one observation row.

### 5.1 Discrete color/state encoding

For each dimension:

- deep green / 空 = -2
- light green / 浅空 = -1
- gray = 0
- light red / 浅多 = +1
- deep red / 多 = +2

Keep the original textual state alongside the numeric encoding.

For each dimension D:

`D_prev = state(t-1)`

`D_now = state(t)`

`D_state_delta = D_now - D_prev`

The signed number is only an ordinal summary. Exact transition labels remain
stored separately, e.g.:

`LIGHT_SHORT -> GRAY`

`GRAY -> LIGHT_LONG`

`LIGHT_LONG -> LONG`

`LONG -> LIGHT_LONG`

### 5.2 Trend dimension

Persist at minimum:
- VAR9
- VAR10
- VAR9 - VAR10
- VAR10 - REF(VAR10,1)
- trend absolute change over SLOPE_CYCLE
- distance to SLOPE_BUY_STRONG
- distance to -SLOPE_SELL_WEAK
- VAR3
- volume / VOL_MA20
- Trend state/color

Derived transition values include:
- delta(VAR9-VAR10)
- delta(trend absolute change)
- threshold crossing direction
- state transition

### 5.3 Momentum dimension

Persist:
- VAR26
- momentum slope
- MOM_STD
- dynamic threshold
- normalized momentum strength:
  `momentum_slope / dynamic_threshold` when defined
- background trend side
- Momentum state/color

Derived:
- delta(VAR26)
- delta(momentum slope)
- delta(normalized momentum strength)
- sign reversal
- weak-to-strong / strong-to-weak transition

### 5.4 Acceleration dimension

Persist:
- VAR15
- VAR18
- J change over ACCEL_CHG_CYCLE
- RSI change over ACCEL_CHG_CYCLE
- trend-vs-range context
- precise range flag
- Acceleration state/color

Derived:
- delta(J change)
- delta(RSI change)
- whether the direction crossed zero
- whether a weak move became a threshold-qualified strong move

### 5.5 Capital/volume dimension

Persist:
- VAR3
- Close vs VAR11
- VAR11 slope
- Volume / VOL_MA5
- Volume / VOL_MA20
- effective relative volume
- HSL_MA5 comparison
- breakout-high flag
- MA20 slope
- suspected-distribution flag
- lock-up confirmation
- violent-sell flag
- first-bear flag
- Capital state/color

Important:
"capital" is treated as a derived price/volume state, not literal observed
institutional money flow.

### 5.6 Anomaly/candlestick dimension

Persist:
- body size
- lower shadow
- upper shadow
- bullish engulfing flag
- hammer flag
- sunrise/breakout-candle flag
- bearish engulfing flag
- hanging-top flag
- dark-cloud flag
- MA20 vs MA60 context
- volume context
- VAR7 position context
- Anomaly state/color

Derived:
- previous pattern -> current pattern
- negative anomaly disappearing
- positive anomaly appearing
- anomaly direction transition

---

## 6. Transition-first analysis

The primary feature object is the **five-dimensional transition vector**:

`T(t) = [Trend(t-1)->Trend(t),
          Capital(t-1)->Capital(t),
          Momentum(t-1)->Momentum(t),
          Accel(t-1)->Accel(t),
          Anomaly(t-1)->Anomaly(t)]`

This is combined with the continuous change vector:

`Delta(t) = [DeltaTrend,
              DeltaCapital,
              DeltaMomentum,
              DeltaAccel,
              DeltaAnomaly]`

and, where meaningful:

`Delta2(t) = Delta(t) - Delta(t-1)`

Therefore a bar that remains five-red but is numerically decelerating is
different from a five-red bar whose underlying values are still strengthening.

Likewise, a bar that is not yet red but has several dimensions turning from
green -> gray -> light red may be a much earlier candidate reversal.

---

## 7. Outcome definitions

Signals are evaluated as probabilities and distributions, not just binary
win/loss labels.

For a signal formed at close t, actionable entry begins at next-session open.

Primary horizons:
- 1 trading day
- 3 trading days
- 5 trading days
- 10 trading days
- 20 trading days

For each horizon record:
- forward return from t+1 open;
- median forward return;
- mean forward return;
- trimmed mean;
- p10 / p25 / p50 / p75 / p90;
- probability return > 0;
- probability return < 0;
- MFE (maximum favorable excursion);
- MAE (maximum adverse excursion);
- MFE/MAE ratio;
- worst intrahorizon drawdown;
- time to MFE;
- time to MAE.

For a candidate **buy** event, the main question is:
does the transition improve the probability and payoff distribution of
subsequent upside relative to an appropriate baseline?

For a candidate **sell/exit** event, the main question is:
does the transition materially increase subsequent downside / drawdown risk,
and would exiting at t+1 open avoid a statistically meaningful loss or
adverse excursion?

A sell signal is not automatically interpreted as a short signal.

---

## 8. Baselines

Every candidate must be compared with multiple baselines.

### B0 — unconditional
All eligible stock-days in the same sample.

### B1 — current state only
Same current five-color state, ignoring the transition path.

This directly tests whether:
`previous -> current`
contains information beyond the current color snapshot.

### B2 — single-dimension transition
Only the relevant dimension transition.

### B3 — formula-native author signal
The source formula's own open/reduce/clear/add/risk flags.

This tells us whether our transition discovery improves on the formula's
existing textual/action layer.

### B4 — matched market context
Match on practical confounders such as:
- recent volatility;
- recent return;
- trend/range background;
- relative volume;
- broad market direction when available.

This prevents a five-dimensional pattern from receiving credit merely because
it usually occurs during a general bull market.

---

## 9. Discovery hierarchy

Do not search all 9.7 million possible exact previous/current combinations and
pick the apparent winner.

Use hierarchical discovery.

### Stage 1 — each dimension independently

For Trend, Capital, Momentum, Acceleration, Anomaly:
- exact t-1 -> t transition;
- continuous delta bins;
- threshold-cross events;
- strengthening vs weakening while state remains unchanged.

Identify which dimension carries useful standalone information.

### Stage 2 — two-dimensional interactions

Only combine dimensions that survived Stage 1.

Examples:
- Trend transition × Momentum transition
- Trend × Capital
- Momentum × Acceleration
- Capital × Anomaly

### Stage 3 — core three-dimensional interactions

Focus first on Trend + Capital + Momentum because the source itself treats
them as core confirmation dimensions, but their usefulness must be verified
rather than assumed.

### Stage 4 — full five-dimensional transition

Only after lower-order effects are understood.

Use hierarchical back-off:
if an exact five-dimensional transition is too rare, fall back to its stable
three- or two-dimensional parent rather than reporting a tiny-sample
"winner".

### Stage 5 — continuous-value refinement

Within a stable color-transition family, test whether raw numerical changes
meaningfully improve discrimination.

Example:
`LIGHT_LONG -> LONG`
may be split by whether the underlying strength margin barely crossed the
threshold or crossed it by a large normalized amount.

---

## 10. Sample-size and anti-overfitting rules

A high win rate with tiny n is not accepted.

Primary candidate reporting requires:
- event count displayed for every result;
- symbol coverage displayed;
- year / fold coverage displayed;
- no hidden filtering after outcomes are viewed.

Rare exact combinations are shrunk or grouped rather than promoted.

As a working rule:
- n < 30: descriptive only;
- 30 <= n < 100: exploratory;
- n >= 100: eligible for candidate testing;
- stronger claims should normally have several hundred events and broad symbol
  coverage.

These are governance thresholds, not guarantees of statistical power.

---

## 11. Statistical tests

For every candidate transition calculate:
- effect size vs baseline;
- confidence interval;
- bootstrap distribution;
- odds/risk difference for directional outcomes;
- return-distribution differences;
- downside-tail differences.

Because thousands of hypotheses can be generated, use:
- Benjamini-Hochberg false discovery rate (BH-FDR);
- primary q threshold = 0.05.

No "best" signal is selected from raw p-values alone.

Economic effect size must also be meaningful.

---

## 12. Dependence and overlapping-event controls

Stock-day observations are not independent.

Controls:
1. block/bootstrap by time rather than naive row bootstrap;
2. evaluate cross-symbol robustness;
3. distinguish a transition event from persistent repeated states;
4. primary transition event is the first day of a state change;
5. persistence-days are a separate study;
6. overlapping forward-return windows are handled separately or with
   dependence-aware inference;
7. same-date market-wide events are not counted as dozens of independent
   confirmations without cluster-aware checks.

---

## 13. Walk-forward / out-of-sample design

No random train/test split.

Use time-ordered expanding-window validation.

Recommended fold structure for available daily US data:
- develop on an earlier block;
- freeze candidate rules;
- test on the next 6-month block;
- expand the history;
- repeat.

The final holdout block is not used for rule design.

The holdout is opened once after candidate rules are frozen.

If a rule works only in the development period and collapses later, it is
rejected.

---

## 14. Cross-symbol robustness

A candidate must not owe its result to one exceptional stock.

Report:
- pooled result;
- per-symbol result;
- median symbol effect;
- fraction of symbols with same-sign effect;
- leave-one-symbol-out sensitivity;
- remove top winner / worst loser;
- sector breakdown when available.

A signal with strong pooled performance but no cross-symbol stability is
classified as concentrated, not universal.

---

## 15. Regime robustness

The same transition may mean different things in different environments.

Stratify at minimum by:
- rising vs falling broader trend;
- high vs low volatility;
- strong vs weak relative volume;
- trend vs range condition;
- large recent gain vs large recent loss.

Do not average together structurally opposite regimes if the effect changes
sign.

---

## 16. Formula-native signal audit

The original formula's existing messages are evaluated as hypotheses.

Examples include:
- 当下开仓
- 当下加仓
- 当下减仓
- 当下清仓
- 风险高抛动作
- 震荡低吸
- 震荡高抛
- 异动关注
- 异动预警

For each one, measure the same forward-return/MFE/MAE statistics.

Then compare:

`author signal`

vs

`five-color snapshot`

vs

`five-dimension transition`

vs

`transition + continuous numerical changes`

This determines where the actual predictive information resides.

---

## 17. First implementation gate — ABT reproduction

Before any large-sample result is accepted, the FIVEGZ5SE engine must
reproduce the already archived ABT January 2025 post-hoc states for the known
dates.

At minimum verify:
- Trend state
- Capital state
- Momentum state
- Acceleration state
- Anomaly state

for the archived January checkpoints.

If parity fails:
`BLOCKED_BY_ENGINE_PARITY`

No large-sample result may be interpreted until parity is repaired.

---

## 18. Large-sample sequence

### Phase A — implementation validation
Use existing known US-stock data and archived ABT checkpoints.

Goal:
prove that the engine reproduces the formula.

### Phase B — existing multi-asset development universe
Run the currently available broad US-stock research universe across the full
available history.

Goal:
discover candidate transition families and eliminate obviously unstable
effects.

### Phase C — expanded universe
After the implementation is frozen, expand to a substantially larger liquid-US
universe and/or longer history as data availability permits.

Goal:
increase rare-transition sample size and test cross-sectional generality.

### Phase D — untouched holdout
Run the frozen candidate rules on data not used to choose them.

Goal:
decide whether they survive out of sample.

---

## 19. Iterative research loop

The requested repeated review process is formalized as:

### Cycle 1
Compute -> summarize -> inspect errors -> audit.

### Cycle 2
Correct implementation errors only -> recompute -> compare with Cycle 1.

### Cycle 3
Test candidate transition hypotheses -> reject weak effects.

### Cycle 4
Run robustness / FDR / cross-symbol / regime checks.

### Cycle 5
Freeze surviving candidates -> run out-of-sample.

### Cycle 6
Translate only surviving probability signals into a trading simulation.

Do not loop indefinitely.

Every hypothesis must end as one of:
- `IMPLEMENTED_AND_VERIFIED`
- `REJECTED_NOT_ADMITTED`
- `BLOCKED_BY_DATA`
- `CLOSED`

---

## 20. Criteria for a statistically supported buy point

A transition can be called a **buy-point candidate** only if it satisfies all
of the following:

1. formed using information available by close t;
2. executes no earlier than t+1 open;
3. adequate sample size and symbol coverage;
4. positive forward-return effect vs relevant baseline;
5. favorable MFE/MAE asymmetry;
6. effect remains after BH-FDR correction;
7. effect persists across multiple time folds;
8. effect is not driven by one or two stocks;
9. direction is stable in final holdout;
10. transaction-cost replay does not erase the benefit.

The final output should be a probability statement, e.g.:

`P(5-day positive return | transition X) = ...`

plus effect size and uncertainty.

Do not label a bar "best buy" merely because it historically preceded the
single largest average return.

---

## 21. Criteria for a statistically supported sell point

A transition can be called a **sell/exit-point candidate** only if:

1. downside probability increases materially;
2. expected forward return deteriorates vs comparable held states;
3. MAE / drawdown risk increases;
4. exit at t+1 open improves outcomes after costs;
5. result survives multiple-testing correction;
6. result is robust across symbols and folds;
7. final holdout confirms the direction.

A sell point means an evidence-supported exit/de-risk event.

It is not automatically a short-entry signal.

---

## 22. Final ranking framework

At the end, do not produce one opaque "score".

For each surviving signal report a structured card:

- exact previous five-dimensional state;
- exact current five-dimensional state;
- key continuous-value changes;
- sample size;
- symbol coverage;
- 1/3/5/10/20-day positive-return probabilities;
- mean and median returns;
- MFE;
- MAE;
- confidence intervals;
- FDR-adjusted q-value;
- fold consistency;
- sector / regime sensitivity;
- transaction-cost result;
- classification:
  - BUY_CANDIDATE
  - HOLD / CONTINUATION
  - REDUCE_CANDIDATE
  - EXIT_CANDIDATE
  - NO_EDGE

This preserves human interpretability.

---

## 23. Relationship with XMA

The five-dimensional study is first completed as an independent signal study.

Do not use XMA to rescue an effect that fails standalone.

After the five-dimensional transition map is frozen, a separate second-stage
study may test:

`XMA geometry/state × FIVEGZ5SE transition`

The interaction study must be named separately and must not rewrite the
standalone five-dimensional result.

---

## 24. Immediate next step

Build a deterministic `SCTYPE=1` FIVEGZ5SE replay engine.

First acceptance test:
reproduce the archived ABT January five-dimensional state table.

Only after parity:
run the first large-sample transition census.

Protocol closure:

`FIVEGZ5SE_SIGNAL_DISCOVERY_PROTOCOL_v1 = FROZEN_BEFORE_LARGE_SAMPLE_REPLAY`
