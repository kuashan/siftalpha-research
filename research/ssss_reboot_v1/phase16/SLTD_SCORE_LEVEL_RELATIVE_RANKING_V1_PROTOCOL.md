# SLTD Score Level -> Relative Ranking v1 — Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

Branch:
`research/sltd-score-level-relative-ranking-v1`

Parent closeout:
`research/sltd-state-level-probability-exposure-v4@47f81af4e86e667cfbf84471013fd403a05cce69`

## 1. Why Phase16 exists

v3 Stage A established that the richer risk-adjusted SLTD Score Level contains temporally stable
state information.

v3 Stage B rejected Score Momentum.

v4 then tested:

`LEVEL -> absolute favorable probability -> target exposure`

and failed Stage C because:

- calibrated probability did not improve Temporal Brier score;
- almost the entire Temporal sample collapsed into the 50% target bucket;
- only 50% and 75% target buckets were used;
- the preregistered support gates failed.

Therefore Phase16 asks a different question:

> Is the frozen SLTD Score Level useful as a **relative risk-ranking variable across assets at the same date**, even though it is not useful as an absolute favorable-probability estimator?

This is not a rescue of v4. v4 remains CLOSED.

## 2. Frozen boundaries

- no Chan/缠论
- no V7 BUY/HOLD/WAIT/SELL input
- no V7 C2 input
- no Score Momentum
- no v4 probability calibration
- no fitted probability thresholds
- no stop loss / take profit / cooldown / hysteresis
- FIRST_OBSERVED / causal semantics
- state observed at close t can affect allocation only from open t+1
- Stage-A Discovery utilities are the only live state weights
- Temporal utilities are never used as live state weights
- Fresh OOS is not consumed in Stage A

Frozen score source:
`research/sltd-state-score-risk-exposure-v3@e996e4344e5c40425bc93253d2e00501bacb3eb8`

Frozen v3 closeout:
`acf88b42ff9c80834423d228b21e13ecd0fbb9e9`

## 3. Frozen LEVEL construction

Use exactly the v3 live LEVEL construction:

- REGIME: stable F2 overrides F1
- INNER: stable F3
- SLOW: median stable F4/F5
- EVENT: stable F7 overrides corresponding F6; median independent events
- TRANSITION: median stable F8 matches
- LEVEL = median(non-zero matched components)
- LEVEL = 0 if nothing stable matches

Only the 82 Stage-A temporally stable states may contribute.
Each state uses its **Discovery utility** as its weight.

## 4. Development data

Original 79-stock universe.

Discovery:
- 2020-01-02 .. 2023-12-31

Temporal consistency:
- 2024-01-01 .. 2026-09-30

For every labeled row, the entire 20-bar forward outcome must end inside its own segment.
No label may cross the Discovery/Temporal boundary.

Important:
Stage-A state selection already used Temporal.
Therefore Temporal here is a consistency set, not a final independent Fresh OOS.

## 5. Daily cross-sectional rank

For each date independently:

1. collect all available original-79 symbols with finite LEVEL and valid forward labels;
2. require at least **60** symbols on that date;
3. rank LEVEL ascending using average rank for ties;
4. convert rank to [0,1]:

`RANK = (average_rank - 1) / (N - 1)`

Thus:
- 0 = lowest LEVEL on that date
- 1 = highest LEVEL on that date

No fitted cut point is used.

## 6. Fixed diagnostic quintiles

For diagnostics only, use deterministic equal-width rank buckets:

- Q1: [0.0, 0.2)
- Q2: [0.2, 0.4)
- Q3: [0.4, 0.6)
- Q4: [0.6, 0.8)
- Q5: [0.8, 1.0]

These are not trading thresholds and are not optimized.

## 7. Forward labels

Primary label:
the same v3 risk-adjusted FORWARD_UTILITY constructed from horizons {5,10,20}
using Discovery-only symbol baselines and Discovery-only normalization scales.

For each date define:

`XS_UTILITY = FORWARD_UTILITY - median_date(FORWARD_UTILITY)`

Also define same-date cross-sectional excess:

- XS_RET_5
- XS_RET_10
- XS_RET_20

where:

`XS_RET_h = RET_h - median_date(RET_h)`

Risk diagnostic:

`XS_MAE_SAFETY_h = MAE_h - median_date(MAE_h)`

Higher is safer because less-negative MAE is better.

The primary research question is whether RANK orders **relative future quality**, not whether it predicts an absolute market direction.

## 8. Required Stage A diagnostics

For Discovery and Temporal separately report:

- valid dates
- valid observations
- mean daily cross-section size
- Spearman rank correlation: RANK vs XS_UTILITY
- Q1..Q5 count
- Q1..Q5 median XS_UTILITY
- Q1..Q5 median XS_RET_5/10/20
- Q1..Q5 median XS_MAE_SAFETY_10/20
- Q5-Q1 spread for all above metrics
- number of adjacent increases in quintile median XS_UTILITY (0..4)
- fraction of dates where daily median(Q5 XS_UTILITY) > daily median(Q1 XS_UTILITY)

No portfolio return is used in Stage A.

## 9. Stage A gates

All must pass:

1. Discovery corr(RANK, XS_UTILITY) > 0
2. Temporal corr(RANK, XS_UTILITY) > 0
3. Discovery Q5-Q1 median XS_UTILITY > 0
4. Temporal Q5-Q1 median XS_UTILITY > 0
5. Temporal Q5-Q1 XS_RET_10 > 0
6. Temporal Q5-Q1 XS_RET_20 > 0
7. Temporal quintile median XS_UTILITY has at least **3 of 4** adjacent increases
8. Temporal daily Q5>Q1 XS_UTILITY spread is positive on **more than 50%** of valid dates
9. Temporal Q1 and Q5 each contain at least **5,000** observations

All pass:
`PROMOTED_TO_ALLOCATION_TEST`

Otherwise:
`REJECTED_NOT_ADMITTED`

A failed gate may not be rescued by changing quintiles, minimum cross-section size, horizons,
or by adding momentum/probability calibration.

## 10. Stage B architecture if Stage A passes

Stage B is allowed only after Stage A = PROMOTED_TO_ALLOCATION_TEST.

The only admissible first allocation rule is a deterministic fully-invested long-only
cross-sectional rank tilt:

`RAW_WEIGHT_i = RANK_i`

`TARGET_WEIGHT_i = RAW_WEIGHT_i / sum_j(RAW_WEIGHT_j)`

If all RAW_WEIGHT values are zero on a date, use equal weights.

Properties:

- no probability translation
- no threshold tuning
- no leverage
- no shorting
- total target portfolio weight = 100%
- close t rank becomes target at open t+1
- transaction costs charged on absolute portfolio-weight turnover

This rule is frozen now so Stage-A results cannot be used to choose a prettier mapping.

Stage B must compare at minimum:

1. SLTD_RANK_LINEAR
2. EQUAL_WEIGHT_BUY_HOLD
3. V7_BASE aggregate benchmark
4. SMA200 aggregate benchmark

Primary friction:
- 5 bps

Sensitivity:
- 10 bps
- 20 bps

Required metrics:
- Total Return
- CAGR
- MaxDD
- Calmar
- turnover
- position changes / rebalance count
- tail daily loss
- annual return consistency

Stage-B exact portfolio admission gates must be frozen in a separate amendment
**before Stage B is run**. Stage A alone cannot authorize engineering use.

## 11. Reserved Fresh OOS

The v4 Fresh30 list was preregistered but never consumed.
It remains untouched.

Phase16 may use it only after:
- Stage A passes;
- Stage B protocol/amendment is frozen;
- development-stage allocation evidence passes its preregistered gates.

No Fresh symbol result may be inspected before those conditions.

## 12. Freeze

`SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_PROTOCOL = FROZEN`
