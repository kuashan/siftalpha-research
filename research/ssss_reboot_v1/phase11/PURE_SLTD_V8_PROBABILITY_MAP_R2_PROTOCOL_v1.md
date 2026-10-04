# Pure SLTD V8 Probability-Map Candidate R2 — Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

## Why this round exists

The pure-SLTD probability study completed on:
- 79-stock discovery,
- 79-stock temporal validation,
- fresh 10-stock external OOS,

and produced 20 OOS-confirmed state effects.

The strongest actionable event-specific effects were:

- POSITIVE: `GREEN|21_PLUS|LOWER|CLOSE_BELOW`
- NEGATIVE: `BLUE|21_PLUS|UPPER|WICK_ONLY`

The negative event independently matches the previously completed
`SLTD V8 Universal Sell Study R1` candidate
`S1_MATURE_BLUE_UPPER_WICK`.

This round therefore tests a **minimal two-rule probability map** instead of
adding many correlated state rules.

## Frozen base

Pure SLTD V7:
- 12 active rules
- source: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`
- engineering pure-SLTD boundary: `09cc68d20ba3b1005cc67caa5c459bb5b21c78d9`
- no Chan/缠论 in SLTD
- signal at selected-bar close -> execution next selected-bar open
- first BUY 25%; later BUY +25 percentage points to 100%
- ordinary SELL = 25% of current holding
- NO_CHANGE_MIXED
- existing C2 hard exit remains unchanged
- friction: 5 bps primary, 10 bps sensitivity

## Candidate additions

### PM_BUY_1 — mature GREEN lower close-below

Conditions:
- color = GREEN
- run_age >= 21
- lower = true
- lower_subtype = CLOSE_BELOW

Action:
- BUY class
- next bar open uses the existing +25pp position policy

Evidence source:
`F7_COLOR_AGE_EVENT_SUBTYPE::GREEN|21_PLUS|LOWER|CLOSE_BELOW`

Prior state study:
- discovery 10d symbol-drift-adjusted excess: +2.52%
- temporal validation 10d excess: +1.32%
- fresh OOS10 10d excess: +2.75%
- fresh OOS10 20d excess: +3.25%

### PM_SELL_1 — mature BLUE upper wick-only

Conditions:
- color = BLUE
- run_age >= 21
- upper = true
- upper_subtype = WICK_ONLY

Action:
- SELL class
- next bar open sells 25% of current holding
- executed SELL arms existing C2 exactly like the current V7 SELL rules

Evidence source:
`F7_COLOR_AGE_EVENT_SUBTYPE::BLUE|21_PLUS|UPPER|WICK_ONLY`

Prior state study:
- discovery 10d excess: -0.88%
- temporal validation 10d excess: -0.48%
- fresh OOS10 10d excess: -0.71%
- fresh OOS10 20d excess: -1.09%

Independent prior sell R1:
`S1_MATURE_BLUE_UPPER_WICK` advanced to R2.

## Conflict rule

The new rules join the ordinary BUY/SELL action classes.

If a bar has more than one action class after adding the new rule,
the existing `NO_CHANGE_MIXED` behavior remains in force.

C2 hard exit retains priority over ordinary actions.

## Fresh R2 stock universe

These 20 stocks do not overlap the prior 79-stock universe or the frozen OOS10:

- Financial: AXP, PGR, CB, ICE
- Communication: T, TMUS, CMCSA
- Consumer staples: CL, MDLZ, GIS
- Industrials: MMM, FDX, EMR
- Utilities: DUK, D, EXC
- Energy: SLB, EOG
- Auto: F, GM

All data are fetched only after this protocol is frozen.

## Window

- warm-up fetch: 2010-01-04 onward
- formal evaluation: 2020-01-02 .. 2026-09-30
- daily bars only in this round

The probability study that generated PM_BUY_1 / PM_SELL_1 was daily-bar research.
No claim about 1h/4h is made for PM_BUY_1.

## Systems compared

1. `V7_BASE` — current pure SLTD V7.
2. `PMAP_14` — V7 + PM_BUY_1 + PM_SELL_1.
3. `BUY_HOLD` — 100% long from first formal open.
4. `SMA200_TREND` — 100% long when the previous completed close is above its causal SMA200; 0% otherwise; next-open execution.

No parameter tuning is allowed after seeing Fresh20 results.

## Primary R2 admission gates for PMAP_14

Relative to V7_BASE at 5 bps:

- equal-weight portfolio Total Return must improve;
- equal-weight portfolio Calmar must improve;
- portfolio MaxDD may not worsen by more than 1.0 percentage point;
- per-symbol Total Return better in >= 11/20 stocks;
- per-symbol Calmar better in >= 11/20 stocks.

Event sanity on Fresh20:

- PM_BUY_1 next-open 10d median forward return must be positive;
- PM_BUY_1 next-open 20d median forward return must be positive;
- PM_SELL_1 next-open 10d median forward return must be <= 0;
- PM_SELL_1 next-open 20d median forward return must be <= 0.

Simple-baseline guard:

- PMAP_14 Calmar must be greater than `SMA200_TREND` Calmar,
  OR PMAP_14 must have higher Total Return than SMA200 with no worse MaxDD.

## Interpretation

- If every gate passes: `PROMOTE_TO_ENGINEERING_CANDIDATE`.
- If portfolio improves but one breadth/sanity guard fails:
  `RESEARCH_ONLY_NOT_PROMOTED`.
- If return or Calmar fails versus V7:
  `REJECTED_NOT_ADMITTED`.

This protocol does not permit changing thresholds after observing results.

`PURE_SLTD_V8_PROBABILITY_MAP_R2_PROTOCOL = FROZEN`
