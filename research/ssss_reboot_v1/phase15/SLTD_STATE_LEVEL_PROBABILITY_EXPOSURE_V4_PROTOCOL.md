# SLTD State Level -> Probability Exposure v4 — Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

## 1. Why v4 exists

v3 Stage A established a richer risk-adjusted SLTD Score Level:

- 359 state keys examined
- 198 Discovery support-pass
- 82 temporally stable
- 43 positive / 39 negative
- all five components represented: REGIME, INNER, SLOW, EVENT, TRANSITION

v3 Stage B then rejected Score Momentum:

- M1/M3/M5 all worsened Discovery walk-forward MAE in 0/3 folds.

Therefore v4 removes momentum entirely.

Architecture:

`SLTD state -> risk-adjusted LEVEL -> calibrated favorable probability -> target exposure`

This is standalone. V7 is comparison-only.

## 2. Frozen boundaries

- no Chan/缠论
- no V7 BUY/HOLD/WAIT/SELL input
- no V7 C2 input
- FIRST_OBSERVED / causal semantics
- close t determines target for open t+1
- no leverage, no shorting
- no result-driven threshold edits
- Stage-A Discovery utilities are the only state weights
- Temporal utilities are never used as live weights

Score source:

`research/sltd-state-score-risk-exposure-v3@e996e4344e5c40425bc93253d2e00501bacb3eb8`

v3 closeout:

`acf88b42ff9c80834423d228b21e13ecd0fbb9e9`

## 3. LEVEL

Use exactly the v3 frozen live LEVEL construction:

- REGIME: stable F2 overrides F1
- INNER: stable F3
- SLOW: median stable F4/F5
- EVENT: stable F7 overrides corresponding F6; median independent events
- TRANSITION: median stable F8 matches
- LEVEL = median(non-zero matched components)
- LEVEL = 0 if nothing stable matches

No Score Momentum is allowed.

## 4. Forward risk-adjusted utility

Use the same research-only forward utility as v3 Stage B.

For h in {5,10,20} from open t+1:

- return
- up indicator
- MFE
- MAE
- realized RR

Convert to symbol-baseline-relative dimensions:

- RETURN
- UP_PROB
- MFE
- MAE_SAFETY
- RR

Collapse each dimension across 5/10/20 by median.
Normalize with semantic zero preserved using Discovery-only scales.
Forward utility is the median normalized dimension.

Define:

`FAVORABLE = 1(FORWARD_UTILITY > 0)`

## 5. Discovery probability calibration

Development data:

- original 79 stocks
- 2020-01-02 .. 2023-12-31
- last 20 bars of the period are excluded from labels to prevent outcome leakage

Fit a one-dimensional monotone isotonic calibration:

`LEVEL -> P(FAVORABLE=1)`

Implementation is deterministic weighted PAVA:

1. sort rows by LEVEL;
2. aggregate identical LEVEL values into weighted success rates;
3. pool adjacent blocks while probability decreases;
4. use each pooled block's weighted-mean LEVEL and pooled favorable rate as knots;
5. prediction between knots uses monotone linear interpolation;
6. values outside the knot range use the nearest endpoint probability.

No hyperparameter is tuned.

## 6. Probability -> exposure

Allowed target grid:

- 0%
- 25%
- 50%
- 75%
- 100%

Continuous target is the calibrated favorable probability itself.

Quantized target:

`TARGET = nearest_25pct(P_FAVORABLE)`

implemented deterministically as:

`floor(4*p + 0.5) / 4`

clamped to [0,1].

Therefore exposure cut points are mathematical nearest-grid boundaries, not fitted after
seeing portfolio results.

No hysteresis, persistence filter, cooldown, stop loss, take profit, or V7 rule is added.

## 7. Stage C — Temporal validation

The mapping is fitted on Discovery only.

Temporal:
- same original 79 stocks
- 2024-01-01 .. 2026-09-30

Important:
Stage A already used this period for state-stability filtering, so this is a validation /
consistency set, **not** a final independent Fresh OOS.

Required diagnostics:

- Discovery favorable rate
- isotonic knots
- Temporal constant-probability Brier score
- Temporal calibrated Brier score
- Brier improvement
- rank correlation between calibrated probability and continuous forward utility
- exposure-bucket counts
- exposure-bucket favorable rates
- exposure-bucket median forward utility
- mean target exposure

Stage C gates:

1. calibrated Temporal Brier < constant Discovery-rate Brier;
2. rank correlation(probability, forward utility) > 0;
3. highest used exposure bucket median forward utility >
   lowest used exposure bucket median forward utility;
4. at least 3 exposure buckets are used;
5. highest and lowest used buckets each contain >= 500 observations.

All pass:
`PROMOTED_TO_FRESH_OOS`

Otherwise:
`REJECTED_NOT_ADMITTED`

No trading admission occurs at Stage C.

## 8. Frozen Fresh30 final OOS universe

This universe is frozen before Stage C results are observed.

It must be asserted to have zero overlap with:

- original 79
- Phase11 OOS10
- R2 Fresh20
- R3 Fresh20
- Phase12 Fresh24
- Phase13 Fresh30

Fresh30 v4:

Financial:
- ALL, TRV, AFL

Technology:
- KLAC, CDNS, SNPS

Healthcare:
- REGN, ZBH, DXCM

Industrials:
- LHX, FAST, IR

Materials:
- MLM, VMC, PPG

Consumer Discretionary:
- LEN, AZO, GPC

Consumer Staples:
- KMB, SYY, HSY

Utilities:
- AEP, XEL, WEC

Energy:
- BKR, CTRA, WMB

Real Estate:
- WELL, AVB, EQR

Final formal window:
- 2020-01-02 .. 2026-09-30
- raw unadjusted OHLC
- warm-up fetched from 2010-01-04 where available
- next-open execution

If a frozen symbol lacks sufficient pre-2020 warm-up or data through 2026-09-30,
it may be replaced only by a same-sector symbol through a documented
**pre-result data-availability amendment** before any Fresh30 portfolio result exists.

## 9. Stage D — final Fresh OOS portfolio test

Run only if Stage C passes.

Comparators:

1. SLTD_LEVEL_PROB_EXPOSURE_V4
2. V7_BASE
3. BUY_HOLD
4. SMA200_TREND
5. FIXED_LONG_MATCHED_EXPOSURE

The fixed-long baseline uses the v4 Fresh30 average exposure, but does not time exposure.

Primary friction:
- 5 bps

Sensitivity:
- 10 bps
- 20 bps

Required portfolio metrics:

- Total Return
- CAGR
- MaxDD
- Calmar
- time in market
- turnover
- position changes
- tail daily/holding loss diagnostic
- per-symbol return breadth
- per-symbol Calmar breadth

Final admission gates at 5 bps:

- Calmar > V7_BASE
- Total Return >= 95% of V7_BASE
- Calmar > FIXED_LONG_MATCHED_EXPOSURE
- Total Return > FIXED_LONG_MATCHED_EXPOSURE
- MaxDD no worse than V7_BASE
- per-symbol Calmar > V7 in >= 16/30

Durability:

- at 10 bps: Calmar > V7 and Return >= 95% of V7
- at 20 bps: Calmar > V7

Probability sanity on Fresh30 must also hold:

- highest used target bucket has higher 10d and 20d forward excess than lowest used bucket;
- each extreme used bucket occurs in >= 15 stocks.

All final gates pass:
`PROMOTE_TO_ENGINEERING_CANDIDATE`

Otherwise:
`REJECTED_NOT_ADMITTED`

## 10. Freeze

`SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4_PROTOCOL = FROZEN`
