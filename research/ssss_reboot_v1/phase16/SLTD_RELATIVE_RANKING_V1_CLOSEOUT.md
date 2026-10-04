# SLTD Relative Ranking v1 — Closeout

Status: **CLOSED / REJECTED_NOT_ADMITTED**

Branch:
`research/sltd-score-level-relative-ranking-v1`

Stage A archive:
`beb8f377e25417390ac38c2b2a86fa98ab04e04d`

Stage B archive:
`11d19037213e20af2fe86208d2e32192955f3db6`

## 1. Frozen conclusion

Phase16 v1 tested:

`frozen SLTD LEVEL -> same-date cross-sectional rank -> linear fully-invested portfolio weight`

No Chan/缠论.
No Score Momentum.
No v4 probability mapping.
No V7 signal input.
Fresh OOS was not consumed.

Stage A:
`PROMOTED_TO_ALLOCATION_TEST`

Stage B:
`REJECTED_NOT_ADMITTED`

Therefore the complete v1 study is CLOSED.

## 2. What survived

The relative-ranking hypothesis survived Stage A.

Discovery:
- rank corr(RANK, XS_UTILITY): +0.04850
- Q5-Q1 XS_UTILITY: +0.11351
- Q5-Q1 XS_RET_10: +0.333%
- Q5-Q1 XS_RET_20: +0.314%
- daily Q5>Q1 utility fraction: 59.73%

Temporal:
- rank corr(RANK, XS_UTILITY): +0.02418
- Q5-Q1 XS_UTILITY: +0.02169
- Q5-Q1 XS_RET_10: +0.067%
- Q5-Q1 XS_RET_20: +0.272%
- utility monotonicity: 3/4 adjacent increases
- daily Q5>Q1 utility fraction: 53.51%

All 9 Stage-A gates passed.

Interpretation:
the frozen SLTD LEVEL contains weak but repeatable same-date cross-sectional ordering information.

## 3. What failed

The first frozen allocation translation failed:

`TARGET_WEIGHT_i proportional to RANK_i`

At 5 bps:
- SLTD_RANK_LINEAR: +186.04%, Calmar 0.478, MaxDD -35.27%
- EQUAL_WEIGHT_DAILY: +182.41%, Calmar 0.487, MaxDD -34.17%
- EQUAL_WEIGHT_BUY_HOLD: +235.14%, Calmar 0.579, MaxDD -33.95%
- V7_BASE: +198.58%, Calmar 0.842, MaxDD -20.91%

SLTD_RANK_LINEAR cumulative gross turnover:
- 281.72

EQUAL_WEIGHT_DAILY turnover:
- 21.75

At 10 bps:
- SLTD_RANK_LINEAR: +148.45%
- EQUAL_WEIGHT_DAILY: +179.36%

At 20 bps:
- SLTD_RANK_LINEAR: +87.44%
- EQUAL_WEIGHT_DAILY: +173.35%

The rank portfolio beat Equal Weight Daily in 4/7 years at 5 bps,
but failed the risk-adjusted and cost-durability gates.

## 4. Main interpretation

The evidence does NOT support:

- daily full re-ranking and full rebalancing;
- treating every small rank movement as a trade;
- engineering the v1 allocation rule.

The evidence DOES support preserving:

- frozen SLTD Score Level;
- cross-sectional relative ranking as a research signal.

The dominant v1 failure is implementation friction / turnover amplification:
a weak ranking edge is repeatedly traded at very high turnover.

This does not prove that every lower-turnover rank architecture will work.
It only justifies a separately preregistered test of whether the same frozen ranking information
can survive when allocation changes are deliberately made less frequent / less sensitive.

## 5. Frozen boundaries after v1

`SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_STAGE_A = PROMOTED_TO_ALLOCATION_TEST`

`SLTD_RELATIVE_RANKING_V1_STAGE_B = REJECTED_NOT_ADMITTED`

`SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1 = CLOSED`

Fresh OOS consumed: **NO**

V7: **UNCHANGED / BENCHMARK-ONLY**

Chan/缠论: **EXCLUDED**

Score Momentum: **REJECTED / NOT USED**

v4 probability calibration: **REJECTED / NOT USED**

## 6. Next admissible research question

Any next study must be separate and preregistered.

The most direct admissible question is:

> Can the already-validated relative rank signal retain its cross-sectional edge under a lower-turnover allocation mechanism?

A next study may test a small, preregistered set of turnover-control mechanisms,
but it must not tune them after observing portfolio outcomes and must not consume Fresh OOS
until development gates pass.

No further study is authorized by this closeout itself.
