# Pure SLTD State Score -> Exposure Map v1 — Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

## Purpose

Phase11 established two separate facts:

1. Pure SLTD state variables contain measurable forward-return information.
2. Directly converting one strong positive state into BUY and one strong negative state into SELL was not stable enough to extend V7.

This study therefore changes the architecture:

`SLTD state -> expected excess-return score -> target exposure`

instead of:

`SLTD state -> isolated BUY/SELL rule`.

Chan/缠论 is excluded.

## Frozen source boundary

- Current pure-SLTD engineering base: `09cc68d20ba3b1005cc67caa5c459bb5b21c78d9`
- Frozen SLTD rule source: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`
- Frozen probability evidence: `PURE_SLTD_STATE_PROBABILITY_RESULT_v1.json`
- Phase11 closeout: `94fb2b3101b4415aa0dc9fb1b02bcc17598b4f04`
- Representation: causal / FIRST_OBSERVED semantics
- Signal state is known only after selected-bar close
- Exposure change executes at next selected-bar open

No Phase12 parameter may be changed after Fresh24 results are observed.

## Frozen score dictionary

Only the 20 `OOS_CONFIRMED` states from
`PURE_SLTD_STATE_PROBABILITY_RESULT_v1.json`
are allowed to contribute to the score.

For each confirmed state:

- `e10 = median(discovery_10d_excess, temporal_10d_excess, oos10_10d_excess)`
- `e20 = median(discovery_20d_excess, temporal_20d_excess, oos10_20d_excess)`
- `state_weight = (e10 + e20) / 2`

This deliberately uses the median across the three already-completed validation splits,
rather than the largest observed effect.

## Redundancy control

Confirmed states are grouped into four independent score components.

### REGIME

Families:
- F1_COLOR_AGE
- F2_COLOR_AGE_ORIGIN

If more than one confirmed REGIME state matches the current bar,
use the matched state with the largest absolute `state_weight`.

### INNER

Family:
- F3_COLOR_AGE_INNER

Use at most one matched INNER state.

### SLOW

Families:
- F4_COLOR_AGE_SLOWPOS
- F5_COLOR_AGE_SLOWTREND

If both match, use their arithmetic mean as one SLOW component.

### EVENT

Families:
- F6_COLOR_AGE_EVENT
- F7_COLOR_AGE_EVENT_SUBTYPE

If an F7 subtype state matches, it replaces its corresponding broader F6 state.
If multiple independent event types occur on the same bar,
average their event weights into one EVENT component.

This prevents nested descriptions of the same bar from being counted as independent evidence.

## Raw score

For each bar:

- compute REGIME, INNER, SLOW and EVENT component values;
- a missing component contributes 0;
- `raw_score = mean(REGIME, INNER, SLOW, EVENT)`.

Therefore a bar with no previously confirmed state has `raw_score = 0`.

No forward data from the tested bar are used.

## Exposure calibration

Calibration uses only the original 79-stock **Discovery** period:
2020-01-02 .. 2023-12-31.

From all non-zero raw scores in that period:

- `POS_SCALE = median(raw_score | raw_score > 0)`
- `NEG_SCALE = median(abs(raw_score) | raw_score < 0)`

These two values are frozen before Fresh24 evaluation.

Continuous target exposure:

If score >= 0:

`continuous = 0.75 + 0.25 * min(score / POS_SCALE, 1)`

If score < 0:

`continuous = 0.75 - 0.50 * min(abs(score) / NEG_SCALE, 1)`

Then quantize to the nearest 25 percentage points and clamp to:

- 25%
- 50%
- 75%
- 100%

Interpretation:

- neutral / unclassified state defaults to 75% exposure;
- increasingly positive confirmed state evidence increases exposure toward 100%;
- increasingly negative confirmed state evidence reduces exposure toward 25%.

## Trading mechanics

System name:
`SLTD_SCORE_EXPOSURE_V1`

- long-only
- cash earns 0
- no leverage
- no shorting
- no isolated BUY/SELL rules
- no V7 C2 exit inside this standalone score system
- every close calculates the next target exposure
- next bar open rebalances to that target
- if quantized target is unchanged, no trade
- friction: 5 bps primary, 10 bps sensitivity

This is a separate candidate architecture. It does not mutate V7.

## Fresh24 untouched universe

No symbol may overlap:
- original 79-stock universe,
- Phase11 fresh OOS10,
- R2 Fresh20,
- R3 Fresh20.

Fresh24:

Financial:
- COF, MCO, AJG

Healthcare:
- BSX, EW, ZTS

Industrials:
- GD, NOC, ROK

Materials:
- NEM, ECL, DD

Consumer:
- KR, KHC, DG

Communication:
- EA, TTWO, FOXA

Real estate:
- EQIX, PSA, O

Energy:
- MPC, OXY, VLO

The script must assert zero overlap before any result is accepted.

## Window

- daily bars
- data warm-up from 2010-01-04
- formal evaluation: 2020-01-02 .. 2026-09-30
- raw unadjusted OHLC
- next-open execution

## Comparison systems

1. `SLTD_SCORE_EXPOSURE_V1`
2. `V7_BASE`
3. `FIXED_75_LONG`
4. `BUY_HOLD`
5. `SMA200_TREND`

`FIXED_75_LONG` exists specifically to test whether any advantage comes from
state timing rather than merely carrying less than 100% market exposure.

## Fresh-state diagnostic

For each Fresh24 bar, record its quantized target bucket.

For 10d and 20d next-open forward returns, calculate symbol-drift-adjusted excess:

`bucket_excess = median(bucket forward return) - median(all eligible forward return for that symbol)`.

The score is directionally validated if:

- 100% exposure bucket has positive cross-symbol median excess at 10d and 20d;
- 25% exposure bucket has negative cross-symbol median excess at 10d and 20d;
- 100% bucket excess > 25% bucket excess at both horizons;
- each extreme bucket has >= 200 total observations and occurs in >= 12 Fresh24 stocks.

## Primary admission gates

At 5 bps, `SLTD_SCORE_EXPOSURE_V1` must satisfy all:

- Calmar > V7_BASE Calmar;
- Calmar > FIXED_75_LONG Calmar;
- Total Return > FIXED_75_LONG Total Return;
- Total Return >= 95% of V7_BASE Total Return;
- MaxDD is no worse than V7_BASE;
- per-symbol Calmar better than V7 in >= 13/24 stocks.

At 10 bps:

- Calmar > V7_BASE Calmar;
- Total Return >= 95% of V7_BASE Total Return.

Fresh-state diagnostic must also pass all directional/support gates above.

## Decision

All gates pass:
- `PROMOTE_TO_ENGINEERING_CANDIDATE`

Portfolio gates pass but a state-diagnostic gate fails:
- `RESEARCH_ONLY_NOT_PROMOTED`

Calmar fails versus V7 or return falls below the V7 floor:
- `REJECTED_NOT_ADMITTED`

No production SLTD rule is changed by this study alone.

`PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_V1_PROTOCOL = FROZEN`
