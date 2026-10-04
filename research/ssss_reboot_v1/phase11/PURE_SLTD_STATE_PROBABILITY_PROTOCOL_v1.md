# Pure SLTD State Probability Study v1 — Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

## Objective

Test whether the **pure SLTD** visual/state variables themselves contain stable forward-return information, before changing any BUY/SELL rule.

This study deliberately separates:

`SLTD state description -> forward probability -> trading rule`

from the current V7 shortcut:

`SLTD state description -> hand-written BUY/SELL rule`.

No Chan/缠论 data, BSP, Bi, Segment or Zhongshu is allowed in this study.

## Source boundary

- Pure-SLTD engineering base: `09cc68d20ba3b1005cc67caa5c459bb5b21c78d9`
- Frozen SLTD formula source: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`
- XMA representation: FIRST_OBSERVED / causal bar-by-bar
- Formal window: 2020-01-02 .. 2026-09-30
- 79-stock universe: existing frozen phase7 snapshots
- Fresh 10-stock universe: WFC, LMT, PM, ADP, WM, UNP, SO, VZ, PANW, CVS
- No rule mutation during the probability study.

## Data partitions

1. **Discovery** — prior 79 stocks, 2020-01-02 .. 2023-12-29.
2. **Temporal validation** — same 79 stocks, 2024-01-01 .. 2026-09-30.
3. **External stock OOS** — the existing fresh 10 stocks, 2020-01-02 .. 2026-09-30.

Candidate definitions are selected using Discovery only.
Temporal validation may reject candidates but may not redefine them.
External stock OOS is final confirmation and may not redefine candidates.

## Executable forward outcomes

All forward-return outcomes respect the real execution boundary.

For a state observed at close of bar `t`:

- executable entry reference = open of `t+1`
- horizon returns = close of `t+h` / open of `t+1` - 1
- MFE(h) = max high over `t+1 .. t+h` / open of `t+1` - 1
- MAE(h) = min low over `t+1 .. t+h` / open of `t+1` - 1
- horizons = 1, 3, 5, 10, 20 selected bars

No historical anchor is treated as executable before it is known.

## Pure-SLTD state variables

Existing causal ledger fields:

- color: BLUE / GRAY / GREEN / OTHER
- state age: 1_3 / 4_10 / 11_20 / 21_PLUS
- origin
- recent transition
- lower inner-rail event + subtype
- upper inner-rail event + subtype
- light-gray support event
- light-gray resistance event
- ZD1 / ZK1
- GZB3 / GZB4
- BS / BD

Derived from the same bar only:

- inner position:
  - BELOW_ZD1
  - LOWER_HALF
  - UPPER_HALF
  - ABOVE_ZK1
- slow-band position:
  - BELOW_GZB4
  - IN_GZB_BAND
  - ABOVE_GZB3
- five-bar slow-band-midpoint direction:
  - UP
  - DOWN
  - FLAT_OR_NA

## Pre-registered candidate families

Dense families:

- F1 = COLOR|AGE
- F2 = COLOR|AGE|ORIGIN
- F3 = COLOR|AGE|INNER_POSITION
- F4 = COLOR|AGE|SLOW_POSITION
- F5 = COLOR|AGE|SLOW_TREND

Event families:

- F6 = COLOR|AGE|EVENT
- F7 = COLOR|AGE|EVENT|SUBTYPE
- F8 = TRANSITION|EVENT

EVENT is one of LOWER, UPPER, LIGHT_SUPPORT, LIGHT_RESIST.
A bar with multiple events contributes separately to the relevant event-family keys.

No arbitrary higher-order combination is searched in v1.

## Support gates

Dense family candidate:

- Discovery n >= 500 bars
- present in >= 30 of the 79 discovery stocks

Event family candidate:

- Discovery n >= 80 events
- present in >= 15 of the 79 discovery stocks

## Drift-adjusted effect

For each symbol and horizon:

`state_excess = median(state forward return) - median(all eligible bars forward return)`

The cross-symbol median of `state_excess` is the primary effect measure.
This prevents a candidate from being promoted merely because it occurs mostly in strong bull-market stocks.

## Discovery admission gate

A candidate must satisfy all of:

- cross-symbol median excess has the same sign at 5d, 10d and 20d;
- |10d median excess| >= 0.25 percentage points;
- |20d median excess| >= 0.50 percentage points;
- directional symbol breadth >= 60% at 10d;
- directional symbol breadth >= 60% at 20d;
- deterministic symbol bootstrap 90% CI for 10d excess excludes zero.

Positive and negative candidates are both allowed.

## Temporal validation gate

A discovery candidate survives only if, on 2024-2026Q3:

- 10d and 20d excess keep the discovery direction;
- directional symbol breadth >= 55% at 10d;
- directional symbol breadth >= 55% at 20d.

No threshold is loosened after results are seen.

## External OOS confirmation

Surviving candidates are evaluated unchanged on the fresh 10-stock universe.

A candidate is **OOS_CONFIRMED** only if:

- 10d and 20d excess retain the same direction;
- directional breadth >= 6/10 symbols at 10d;
- directional breadth >= 6/10 symbols at 20d.

Otherwise it is **REJECTED_NOT_STABLE**.

## Trading-system boundary

This study does **not** automatically rewrite V7.

Only if at least one positive and one negative state are OOS_CONFIRMED may a separate
`PURE_SLTD_PROBABILITY_MAP_CANDIDATE` be built and backtested.

That candidate must be evaluated against:

- current pure SLTD V7;
- Buy & Hold;
- a simple trend baseline.

No existing V7 rule is deleted or promoted by the probability study alone.

`PURE_SLTD_STATE_PROBABILITY_V1_PROTOCOL = FROZEN`
