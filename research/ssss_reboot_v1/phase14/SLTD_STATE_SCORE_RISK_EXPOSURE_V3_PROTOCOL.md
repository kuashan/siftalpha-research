# SLTD State Score Risk-Exposure v3 — Master Protocol

Status: **PRE-REGISTERED / STAGE A NOT YET RUN**

## 0. Repository audit basis

This protocol starts only after auditing the real remote history.

Audited predecessors:

- Phase11 closeout: `94fb2b3101b4415aa0dc9fb1b02bcc17598b4f04`
- Phase12 standalone continuous exposure-map closeout:
  `research/sltd-state-score-exposure-map-v1@29ceeeb73328e0f1b1108f01ab14179e858c7e5e`
- Duplicate state-score branch invalidation:
  `research/sltd-state-score-mode-v1@5455d4981ff3ae678758b9f57a11273e0644c892`
- Phase13 standalone score-regime v2 closeout:
  `research/sltd-state-score-regime-v2@a7b10493450867960e9bdd8ff05f9e3905e854a6`

Frozen interpretation of those results:

1. Pure SLTD state information has repeatable predictive content.
2. Phase12 proved score-bucket separation on Fresh24, but direct continuous rebalancing had
   too much turnover and much worse drawdown than V7.
3. Phase13 proved that extreme score buckets still had correct directional meaning on a
   separate Fresh30, but a binary LONG/CASH hysteresis system still failed to beat V7 or
   Buy & Hold on return.
4. Therefore v3 must not tune Phase12/13 thresholds on their consumed Fresh24/Fresh30.
5. V7 remains comparison-only. No V7 BUY/HOLD/WAIT/SELL rule or C2 rule may enter v3.
6. Chan/缠论 remains excluded.

## 1. Research question

Build a standalone architecture:

`SLTD current state -> risk-adjusted state score -> score level + score momentum -> data-derived target exposure`

The question is not "is this bar BUY or SELL?"

The question is:

> Given all causally observable SLTD state information at this close, what target long
> exposure is justified at the next bar open?

## 2. Non-negotiable boundaries

- Pure SLTD only.
- No Chan/缠论.
- V7 is a benchmark only.
- FIRST_OBSERVED / causal state semantics only.
- State observed at close t may change exposure only at open t+1.
- No future backfill.
- No parameter may be changed after its declared validation or Fresh OOS result is seen.
- Every stage ends with one of:
  `IMPLEMENTED_AND_VERIFIED`, `PROMOTED`, `REJECTED_NOT_ADMITTED`, `CLOSED`.

## 3. Why v3 is materially different from Phase12 and Phase13

Phase12 used only the 20 previously OOS-confirmed states and a manually specified
75%-centered 25/50/75/100 exposure ladder.

Phase13 kept that frozen score and manually mapped only the 100% bucket to entry and
25% bucket to exit.

v3 changes the research object itself:

- estimate state value using return, probability, MFE, MAE and risk/reward together;
- include transition information as an explicit independent component;
- control nested state overlap before aggregation;
- do not dilute missing components by averaging them as zeros;
- explicitly study Score Level and Score Momentum;
- allow positive and negative score changes to have different fitted responses;
- derive exposure cut points from Discovery data rather than hard-coding score thresholds.

## 4. Data partitions

### Development universe

Use the frozen original 79-stock SLTD dataset already archived in Phase7.

### Discovery

- 79 stocks
- 2020-01-02 .. 2023-12-31

Used for:
- state metric estimation;
- robust normalization;
- candidate score construction;
- later Stage B/C model fitting.

### Temporal validation

- same 79 stocks
- 2024-01-01 .. 2026-09-30

Used only after a Stage-A candidate score definition is frozen.

### Fresh OOS

Not consumed in Stage A.

A future Stage D Fresh OOS universe must have zero overlap with every prior universe:
- original 79;
- Phase11 OOS10;
- R2 Fresh20;
- R3 Fresh20;
- Phase12 Fresh24;
- Phase13 Fresh30.

Fresh OOS symbols may not be selected using v3 outcome data.

## 5. Horizons and executable outcome convention

Primary horizons:

- 5 bars
- 10 bars
- 20 bars

For a state observed at close t:

- executable entry reference = open t+1;
- return_h = close(t+h) / open(t+1) - 1;
- MFE_h = max(high[t+1:t+h]) / open(t+1) - 1;
- MAE_h = min(low[t+1:t+h]) / open(t+1) - 1.

These are outcome labels only. They are never inputs to the same bar's score.

## 6. State families

All state families from the pure SLTD probability study remain eligible:

- F1 COLOR + AGE
- F2 COLOR + AGE + ORIGIN
- F3 COLOR + AGE + INNER POSITION
- F4 COLOR + AGE + SLOW POSITION
- F5 COLOR + AGE + SLOW TREND
- F6 COLOR + AGE + EVENT
- F7 COLOR + AGE + EVENT SUBTYPE
- F8 TRANSITION + EVENT

No family is promoted merely because it worked in an earlier phase.

## 7. State-level predictive vector

For each supported state and each horizon h in {5,10,20}, compute cross-symbol medians
of five signed predictive dimensions relative to each symbol's unconditional baseline:

1. Return excess:
   `state median return_h - symbol baseline median return_h`

2. Up-probability lift:
   `P(return_h > 0 | state) - P(return_h > 0 | symbol)`

3. MFE excess:
   `state median MFE_h - symbol baseline median MFE_h`

4. MAE safety lift:
   `state median MAE_h - symbol baseline median MAE_h`

   MAE is negative, so a positive lift means less adverse excursion.

5. Risk/reward lift:

   Per symbol:
   `RR = median(MFE_h) / max(abs(median(MAE_h)), 1e-6)`

   State lift is:
   `log(RR_state) - log(RR_symbol_baseline)`.

For each dimension, collapse 5/10/20 with the median.

The Stage-A state vector is therefore:

`[RETURN, UP_PROB, MFE, MAE_SAFETY, RR]`

## 8. Support gates

Dense families F1-F5:

- total observations >= 500
- symbols >= 30

Event families F6-F8:

- total observations >= 80
- symbols >= 15

Unsupported states receive no weight.

## 9. Robust normalization and composite state utility

Within the Discovery split, for each of the five dimensions:

- center = median across all supported states;
- scale = MAD across all supported states;
- if MAD is effectively zero, use IQR/1.349;
- if both are effectively zero, that dimension is declared non-informative and omitted.

Each raw dimension is transformed to a robust z-score using only Discovery statistics.

The state composite utility is:

`STATE_UTILITY = median(non-missing robust-z dimensions)`

No manually chosen return/MFE/MAE coefficient is allowed.

For auditability report:
- all five raw dimension signals;
- all five normalized signals;
- composite utility;
- support.

## 10. Temporal stability gate

A Discovery-supported state is `TEMPORAL_STABLE` only if on 2024-2026Q3:

- composite utility has the same non-zero sign as Discovery;
- at least 3 of the 5 raw dimensions have the same sign as Discovery;
- 10d return-excess sign agrees with Discovery;
- symbol coverage still satisfies at least 50% of the Discovery family support-symbol gate.

States failing this gate remain archived but receive zero live score weight.

## 11. Redundancy / nesting control

The live score may contain at most five independent components.

### REGIME
- F2 overrides F1 when a stable F2 state matches.
- otherwise use stable F1.

### INNER
- F3 only.

### SLOW
- F4 and F5 are related.
- if both match, use their median utility as one SLOW component.

### EVENT
- F7 overrides its corresponding F6 event.
- if multiple independent events occur on the same bar, use their median utility as one EVENT component.

### TRANSITION
- F8 is a separate component.
- it is included only if the matching F8 state is TEMPORAL_STABLE.

Current score level:

`LEVEL_t = median(non-zero matched component utilities)`

If no stable component matches:
`LEVEL_t = 0`.

This avoids counting nested descriptions as independent votes and avoids diluting sparse
evidence by averaging missing components as zeros.

## 12. Score momentum study — Stage B only

Stage A does not choose a momentum window.

Stage B will compare exactly these pre-declared momentum definitions on Discovery only:

- M1: `LEVEL_t - LEVEL_(t-1)`
- M3: `LEVEL_t - median(LEVEL_(t-3:t-1))`
- M5: `LEVEL_t - median(LEVEL_(t-5:t-1))`

Positive and negative momentum are separate predictors:

- `MOM_UP = max(momentum, 0)`
- `MOM_DOWN = min(momentum, 0)`

This allows asymmetric response without assuming symmetry in advance.

The winning momentum definition must be selected using Discovery-only blocked
time cross-validation and then frozen before Temporal evaluation.

## 13. Exposure mapping — Stage C only

Exposure thresholds may not be manually chosen from Phase12/13 results.

Stage C must derive the mapping from Discovery data only.

Allowed target exposures are fixed for interpretability:

- 0%
- 25%
- 50%
- 75%
- 100%

But the score cut points that map policy score to those exposures must be learned from
Discovery only using a monotone mapping.

The mapping must use:
- Score Level;
- selected Score Momentum;
- separate positive and negative momentum terms.

No Fresh OOS observation may affect a threshold.

## 14. Portfolio comparison — Stage D

Only after the score and exposure mapping are frozen.

Required comparators:

1. v3 risk-adjusted State Score exposure
2. V7_BASE
3. BUY_HOLD
4. SMA200_TREND
5. FIXED_EXPOSURE baseline matched to v3 average exposure

Required metrics:

- Total Return
- CAGR
- MaxDD
- Calmar
- time in market
- turnover
- position changes
- win rate
- tail loss / worst trade or equivalent position-period tail statistic
- per-symbol return breadth
- per-symbol Calmar breadth

Primary friction:
- 5 bps

Sensitivity:
- 10 bps
- 20 bps

## 15. Stage A output contract

Stage A must archive:

- full Discovery state metric table;
- full Temporal state metric table;
- robust normalization constants;
- TEMPORAL_STABLE state table;
- family funnel;
- example nested-state audits;
- machine-readable JSON;
- concise Markdown summary.

Stage A must not output a trading admission decision.

Its only allowed terminal statuses are:

- `IMPLEMENTED_AND_VERIFIED`
- `REJECTED_NOT_ADMITTED` if the risk-adjusted state layer fails temporal stability.

## 16. Freeze

This file is frozen before Stage A runs.

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_MASTER_PROTOCOL = FROZEN`
