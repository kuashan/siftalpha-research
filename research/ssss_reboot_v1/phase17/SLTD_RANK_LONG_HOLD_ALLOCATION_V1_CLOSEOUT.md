# SLTD Rank -> Long-Hold Allocation v1 — Closeout

Status: **CLOSED / REJECTED_NOT_ADMITTED**

Branch:
`research/sltd-rank-long-hold-allocation-v1`

Protocol commit:
`357a22372daa172ad439005b30cb984b66be9c3b`

Stage A archive:
`9542310902f3c11e15cab935bf3a15b2d0adcb38`

## 1. Frozen conclusion

Phase17 tested whether the frozen SLTD cross-sectional rank could improve **initial capital allocation**
for a long holding period without any rank-driven rebalance or sell action after entry.

Architecture:

`frozen SLTD LEVEL -> one-time cross-sectional rank -> one-time static allocation -> long hold`

No Chan/缠论.
No V7 signal input.
No Score Momentum.
No v4 probability calibration.
No rank-based rebalance after entry.
Fresh OOS was not consumed.

Decision:

`SLTD_RANK_LONG_HOLD_ALLOCATION_V1_STAGE_A = REJECTED_NOT_ADMITTED`

The study is CLOSED.

## 2. Important positive diagnostic

A single full-window static portfolio formed at the final 2019 close and bought at the
2020-01-02 open looked favorable.

At 5 bps:

- RANK_STATIC total return: +244.11%
- EQUAL_STATIC total return: +235.14%
- return advantage: +8.97 percentage points
- RANK_STATIC MaxDD: -32.80%
- EQUAL_STATIC MaxDD: -33.95%
- RANK_STATIC Calmar: 0.613
- EQUAL_STATIC Calmar: 0.579

This single start-date result is descriptive only.

It cannot be used as admission evidence because the preregistered monthly-cohort robustness test
did not confirm that the advantage repeats across formation dates.

## 3. Monthly-cohort evidence

### 252-bar (~1 trading year), 5 bps

Early formations, 2020-2023:
- cohorts: 48
- median excess return: -0.043%
- mean excess return: +0.213%
- positive fraction: 47.9%
- median MaxDD difference: -0.478%
- median Calmar difference: +0.011

Late formations, 2024 onward:
- cohorts: 21
- median excess return: +0.497%
- mean excess return: -0.454%
- positive fraction: 52.4%
- median MaxDD difference: +0.367%
- median Calmar difference: +0.033

All 252-bar cohorts:
- cohorts: 69
- median excess return: -0.009%
- mean excess return: +0.010%
- positive fraction: 49.3%

This is effectively no stable long-hold allocation edge.

### 126-bar, late formations

- median excess return: -0.845%
- mean excess return: -1.336%
- positive fraction: 32.1%

### 504-bar (~2 trading years)

Early:
- median excess return: +1.596%
- positive fraction: 60.4%

Late:
- cohorts: 9
- median excess return: -6.433%
- positive fraction: 22.2%

The long-horizon result is regime/start-date sensitive and not stable enough for admission.

## 4. Gate outcome

PASS:
- late 252 median excess > 0
- late 252 positive fraction > 50%
- late 252 median Calmar difference > 0
- late 252 MaxDD guard
- late 252 at 20 bps median excess > 0

FAIL:
- early 252 median excess > 0
- early 252 positive fraction > 50%
- late 126 median excess > 0

Final:
`REJECTED_NOT_ADMITTED`

## 5. Correct interpretation

This result rejects a mistaken conclusion:

> "Because long holding is strong, SLTD Rank should improve returns simply by being used less often."

The data do not support that.

The stronger conclusion is:

1. **Long holding itself is the dominant return engine** in these tests.
2. SLTD relative rank contains some cross-sectional information, but the information is too weak /
   unstable to reliably improve one-time long-hold capital allocation across formation dates.
3. The favorable 2020 full-window start is not robust enough to treat as a rule.
4. Lower turnover is not itself an alpha source.
5. More frequent trading destroyed value through turnover, but eliminating trading did not
   automatically turn the rank signal into a robust excess-return allocator.

## 6. What remains valid

- SLTD risk-adjusted Score Level remains an interpretable state/ranking variable.
- Phase16 Stage A relative-ordering evidence remains valid as descriptive/predictive information.
- Phase16 daily allocation is rejected.
- Phase17 static long-hold rank allocation is rejected.
- V7 remains unchanged and benchmark-only.
- Fresh OOS remains untouched.

Frozen statuses:

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_A = IMPLEMENTED_AND_VERIFIED`

`SLTD_STATE_SCORE_MOMENTUM = REJECTED_NOT_ADMITTED`

`SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4 = CLOSED / REJECTED_NOT_ADMITTED`

`SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1 = CLOSED / REJECTED_NOT_ADMITTED`

`SLTD_RANK_LONG_HOLD_ALLOCATION_V1 = CLOSED / REJECTED_NOT_ADMITTED`

## 7. Next admissible research direction

The next study should not ask how to trade Rank more often or less often.

The more economically coherent question is:

> Can SLTD improve the **risk side** of an otherwise long-hold portfolio while preserving most of
> the long-hold return?

That means long holding remains the return engine.
SLTD would be tested only as a risk overlay, with a preregistered requirement that any protection
must preserve a high fraction of buy-and-hold return while materially improving drawdown / Calmar.

No next risk-overlay rule is authorized by this closeout itself.
