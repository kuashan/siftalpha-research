# SLTD State Level -> Probability Exposure v4 — Closeout

Status: **CLOSED / REJECTED_NOT_ADMITTED**

Branch: `research/sltd-state-level-probability-exposure-v4`

Result commit before closeout:
`ee6014c6d8557c792661af44e3ffef872aadb249`

## 1. Frozen research interpretation

v4 tested the preregistered architecture:

`SLTD state -> risk-adjusted LEVEL -> calibrated favorable probability -> target exposure`

The mapping was learned on Discovery only by monotone isotonic calibration (PAVA).

Score Momentum was not used.
Chan/缠论 was not used.
V7 was not used as a signal source.

The Stage C Temporal validation failed its preregistered admission gates.

Therefore:

- Stage D Fresh OOS portfolio testing is **NOT ALLOWED** for v4.
- The frozen Fresh30 universe remains **UNCONSUMED**.
- No threshold, probability grid, bucket rule, or calibration method may be altered inside v4 to rescue the result.
- v4 must not be presented as a trading strategy candidate.

## 2. Stage C evidence

Discovery:
- stable states: 82
- labeled rows: 77,894
- favorable rate: 51.50%
- isotonic pooled blocks / knots: 14

Temporal:
- rows: 52,851
- constant-probability Brier: 0.249738
- isotonic Brier: 0.250434
- relative Brier improvement: -0.279%
- rank corr(probability, forward utility): 0.03653
- mean target exposure: 50.10%

Used target buckets:
- 50%: 52,650 observations, median forward utility 0.07224
- 75%: 201 observations, median forward utility 0.30598

Gate outcome:
- Temporal Brier improves: FAIL
- probability/utility rank correlation positive: PASS
- highest bucket utility > lowest: PASS
- at least three buckets used: FAIL
- extreme bucket support: FAIL

Final Stage C decision:
`REJECTED_NOT_ADMITTED`

## 3. What the failure means

The failure does **not** invalidate the v3 Stage-A Score Level.

The surviving conclusion remains:

- SLTD Score Level contains weak but directionally ordered state information.
- Converting that LEVEL into a calibrated binary favorable probability does not add enough separation to support a useful 0/25/50/75/100 exposure ladder.
- The isotonic probability mapping collapsed almost the entire Temporal sample into the 50% bucket.
- Therefore the main weakness is the **LEVEL -> probability/exposure translation**, not a newly discovered failure of the underlying state taxonomy.

This distinction must be preserved.

## 4. Research boundary after v4

Frozen statuses:

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_A = IMPLEMENTED_AND_VERIFIED`

`SLTD_STATE_SCORE_MOMENTUM = REJECTED_NOT_ADMITTED`

`SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4_STAGE_C = REJECTED_NOT_ADMITTED`

`SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4 = CLOSED`

Fresh OOS consumed by v4: **NO**

V7: **UNCHANGED / BENCHMARK-ONLY**

Chan/缠论: **EXCLUDED**

## 5. Next admissible question

Any next study must be separately preregistered.

It may reuse the frozen v3 Score Level, but it must not:
- reopen v4,
- tune v4 thresholds after seeing Stage C,
- add Score Momentum,
- import V7 decision rules,
- consume the reserved Fresh OOS before its own development gates pass.

The next study should first ask whether the Score Level is more useful as a **relative risk/ranking variable** than as an absolute binary favorable-probability estimator.

No further development is authorized by this closeout itself.
