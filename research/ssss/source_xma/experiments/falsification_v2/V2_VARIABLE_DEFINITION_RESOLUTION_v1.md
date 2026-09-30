# XMA Falsification v2 — Variable Definition Resolution v1

Status: **DEFINITIONS SELECTED / IMPLEMENTATION TEST REQUIRED**

Date: 2026-09-28

This file resolves only the six definition gaps identified in `V2_PROTOCOL_INPUT_GAP_AUDIT_v1.md`.

No v2 outcome was inspected to choose these definitions.

No hypothesis, candidate variable, horizon, primary statistic, direction, MDE, sample floor, or family is changed.

---

# 1. Volatility z-score — H7/H8

## Raw return

`r_t = ln(CLOSE_t / CLOSE_{t-1})`

## Realized volatility

`RV20_t = sample_std(r_{t-19}, ..., r_t)`

Requirements:
- exactly 20 valid daily log returns;
- `ddof = 1`;
- no annualization.

## Point-in-time z-score

Reference window is the **60 prior RV20 observations**, excluding current `RV20_t`:

`VOL_Z_t = (RV20_t - mean(RV20_{t-60:t-1})) / sample_std(RV20_{t-60:t-1})`

Rules:
- 60 valid prior RV20 observations required;
- sample standard deviation, `ddof = 1`;
- if reference std = 0, value is missing;
- no winsorization;
- no clipping;
- no forward fill;
- current RV20 is not included in its own z-score reference moments.

Registered condition remains:

`VOL_Z_t > +1`

This variable is return-realized volatility and is not ATR-based.

---

# 2. Volume z-score — H9/H10

## Raw activity field

Use dollar volume:

`DOLLAR_VOLUME_t = CLOSE_t * VOLUME_t`

Transform:

`LDV_t = ln(1 + DOLLAR_VOLUME_t)`

Rationale fixed before testing:
- dollar volume avoids direct dependence on nominal share count;
- log transform reduces scale/skew sensitivity;
- no signed-volume construction is used because the registered variable is Volume z-score, not Volume Structure.

## Point-in-time z-score

Use the 60 prior LDV observations, excluding current LDV:

`VOLUME_Z_t = (LDV_t - mean(LDV_{t-60:t-1})) / sample_std(LDV_{t-60:t-1})`

Rules:
- 60 valid prior observations required;
- `ddof = 1`;
- zero reference std => missing;
- volume < 0 => invalid;
- volume = 0 is retained through `ln(1+x)`;
- no winsorization;
- no clipping;
- no forward fill.

Registered condition remains:

`VOLUME_Z_t > +1`

---

# 3. Sector Relative Strength — H5/H6

Use the repository's frozen 11-sector ETF mapping:

- Technology -> XLK
- Communication Services -> XLC
- Consumer Discretionary -> XLY
- Consumer Staples -> XLP
- Health Care -> XLV
- Financials -> XLF
- Industrials -> XLI
- Energy -> XLE
- Materials -> XLB
- Utilities -> XLU
- Real Estate -> XLRE

Market benchmark:

`SPY`

## Sector raw RS

For mapped sector ETF `S`:

`SECTOR_RET20_t = S_t / S_{t-20} - 1`

`SPY_RET20_t = SPY_t / SPY_{t-20} - 1`

`SECTOR_RS20_t = SECTOR_RET20_t - SPY_RET20_t`

Rules:
- simple returns, not log returns;
- 20 trading bars;
- no substitute ETF;
- if either endpoint for sector ETF or SPY is missing, Sector RS is missing.

## Cross-sectional rank

On each date, rank the available 11 `SECTOR_RS20` values from weak to strong.

Use deterministic percentile rank:

`RS_PCT = (rank_average - 1) / (N - 1)`

where:
- rank 1 = weakest;
- `rank_average` is average rank for ties;
- `N` is number of available sector ETFs that date.

Eligibility:
- all 11 sector ETFs must be available for H5/H6 on that date;
- otherwise the date is ineligible.

H5 buckets:
- Low: `RS_PCT <= 0.20`
- High: `RS_PCT >= 0.80`

H6:
- continuous `RS_PCT`.

This is the unique v2 Sector RS definition.

---

# 4. Market Breadth level — H11/H12

v2 uses a fixed, reproducible breadth proxy rather than claiming official S&P 500 breadth.

## Breadth universe

Use the frozen 39-equity Falsification v1 universe from `UNIVERSE_FROZEN_v1.md`.

Universe membership is static for the entire v2 computation.

No constituent is added or removed based on later availability or outcome.

## Per-symbol breadth indicator

For symbol `i`:

`ABOVE20_{i,t} = 1(CLOSE_{i,t} > SMA20(CLOSE_i)_t)`

SMA20:
- arithmetic mean;
- 20 valid closes required.

## Scalar Market Breadth level

`BREADTH20_t = 100 * mean_i(ABOVE20_{i,t})`

Eligibility:
- at least 80% of the 39 symbols must have a valid ABOVE20 value on date t;
- otherwise Breadth is missing;
- available constituents are equal-weighted;
- no forward fill;
- no market-cap weighting.

This breadth proxy includes the focal symbol when present; the membership rule is identical for every event and therefore produces one market-wide scalar series.

## Risk-Off threshold

For each date t, compute the 10th percentile from the **20 prior valid BREADTH20 observations**, excluding current t:

`BREADTH_Q10_t = quantile(BREADTH20_{t-20:t-1}, 0.10, method="linear")`

Risk-Off:

`BREADTH20_t < BREADTH_Q10_t`

Normal:

`BREADTH20_t >= BREADTH_Q10_t`

Rules:
- 20 valid prior Breadth observations required;
- current day excluded from threshold estimation;
- strict `<` defines Risk-Off;
- no alternate breadth component is combined into the scalar.

---

# 5. F3 same-day volatility control — H5/H6

Use the already canonical XMA risk scale:

`VOL_LEVEL_t = ATR14_t / CLOSE_t`

ATR14:
- True Range;
- arithmetic rolling mean over 14 valid TR observations;
- no Wilder RMA substitution.

No z-score is applied to this F3 control.

This control is distinct from F4 `VOL_Z`.

---

# 6. H4 symbol-level quantile reference population and estimator

H4 quantile thresholds are calibration constants computed only from a pre-sealed historical reference period.

## Reference period

`2020-01-02 through 2025-12-31`, inclusive.

No 2026 date may be used to estimate H4 reference quantiles.

## Input variable

`DIST_MID_ATR_t = (CLOSE_t - FAST_MID_ANALYTIC_t) / ATR14_t`

with:

`FAST_MID_ANALYTIC_t = (ZK1_t + ZD1_t) / 2`

## Per-symbol quantiles

For each symbol separately, compute:

- P10
- P40
- P60
- P90

using all valid `DIST_MID_ATR` observations in the reference period.

Estimator:
- linear quantile interpolation;
- missing observations excluded;
- minimum valid observations per symbol = 252.

If a symbol has <252 valid observations:
- H4 for that symbol is ineligible;
- no pooled/global quantile substitutes for it.

Arm definitions:
- Extreme: `DIST <= P10` OR `DIST >= P90`
- Neutral: `P40 <= DIST <= P60`

Boundary ties are included.

These quantiles are frozen calibration constants for the future sealed window and are not recomputed using sealed data.

---

# 7. Missing-data and point-in-time rules

Across all six resolved definitions:

- no backward fill;
- no forward fill unless a later Data Freeze explicitly documents an exchange-calendar alignment rule for a benchmark series;
- no interpolation of price/volume values;
- a feature requiring unavailable endpoints is missing;
- current-bar data may be used only when the registered event is defined at current-bar close;
- future data are never used in a current feature;
- missingness cannot be repaired after outcome inspection with a new vendor.

---

# 8. Trading-service mapping

These definitions remain research variables until sealed validation.

If eventually validated:

- VOL_Z / VOLUME_Z -> Conditional Information gate;
- Sector RS -> cross-sectional ranking input;
- BREADTH20 / VIX change -> Risk-Off suppression context;
- DIST_MID_ATR -> position-lifecycle timing/context;
- ATR14/close -> risk normalization/control.

No order-generation rule is authorized here.

---

# 9. Stage closure criteria

This definition stage closes only if one implementation can reproduce every formula above on non-sealed development data and produce the required fields without hidden choices.

Next step:

**IMPLEMENTATION SANITY TEST**

The test may check:
- computability;
- coverage;
- missingness;
- deterministic repeatability;
- event/control construction compatibility.

The test may not inspect or optimize trading performance.

If a definition cannot be implemented reproducibly, its linked hypothesis is `REJECTED_NOT_ADMITTED`; no replacement variable is allowed.
