# SLTD State Score Mode v1 — Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

## Core correction

This is **not** V7 plus new rules.

It is a second, independent operating mode built from the SLTD state layer itself:

`SLTD raw state -> estimated forward edge -> state score -> target exposure`

The existing V7 remains only a benchmark.

No V7 BUY/HOLD/WAIT/SELL rule, no V7 25% add/reduce rule and no C2 hard-exit rule is used inside this mode.

Chan/缠论 is excluded.

## Naming

Research name:

`SLTD_STATE_SCORE_MODE_V1`

Working UI name if this mode later graduates:

`SLTD Score` / `SLTD 状态评分`

No production integration is allowed by this protocol.

## Causal representation

All SLTD state variables use the existing FIRST_OBSERVED / XMA causal representation.

A score is computed only from information available at the close of bar t.

Target exposure derived from that score is executed at the open of bar t+1.

There is no anchor-date backfill and no future information.

## Development universe

The score map is learned only from already-used research data:

### Discovery
- Original 79 stocks
- 2020-01-02 .. 2023-12-31

### Stability filter
- Same 79 stocks
- 2024-01-01 .. 2026-09-30
- existing OOS10:
  WFC, LMT, PM, ADP, WM, UNP, SO, VZ, PANW, CVS

R2 Fresh20 and R3 Fresh20 are **not** used for model fitting or thresholds.

## Fresh final validation universe

A new 30-stock universe, not overlapping the 79, OOS10, R2 Fresh20 or R3 Fresh20:

Financial:
- COF, MMC, AJG

Technology:
- KLAC, SNPS, CDNS

Communication / media:
- EA, TTWO, FOXA

Healthcare:
- EW, BSX, REGN

Industrials:
- FAST, URI, PCAR

Materials:
- NUE, MLM, ECL

Consumer discretionary:
- DG, LULU, AZO

Consumer staples:
- KMB, SYY, HSY

Utilities:
- AEP, XEL, WEC

Energy:
- MPC, OXY, VLO

The workflow must assert zero overlap before downloading formal validation data.

## State families

Use the same pure-SLTD state families frozen in Phase11:

- F1 = COLOR|AGE
- F2 = COLOR|AGE|ORIGIN
- F3 = COLOR|AGE|INNER_POSITION
- F4 = COLOR|AGE|SLOW_POSITION
- F5 = COLOR|AGE|SLOW_TREND
- F6 = COLOR|AGE|EVENT
- F7 = COLOR|AGE|EVENT|SUBTYPE

F8 transition-event is excluded in v1 because Phase11 produced zero admitted candidates and it is too sparse for a continuous score.

## Learning one state effect

For each family/key and each split, calculate per-symbol drift-adjusted forward return:

`effect_h(symbol,key) = median(key forward return_h) - median(all eligible forward return_h)`

where h = 10 and 20 selected bars and forward return uses:

`close[t+h] / open[t+1] - 1`

For each family/key:

Discovery support:
- dense F1-F5: n >= 300 bars and >= 25 stocks
- event F6-F7: n >= 50 events and >= 10 stocks

Discovery direction:
- median cross-symbol excess at 10d and 20d must have the same non-zero sign.

Stability:
- temporal-79 10d and 20d median excess must keep the discovery sign;
- OOS10 10d and 20d median excess must keep the discovery sign;
- OOS10 key must be present in >= 5 stocks.

Only states passing all conditions enter the score map.

Frozen state effect:

`effect = median(discovery10, discovery20, temporal10, temporal20, oos10_10, oos10_20)`

This uses only already-known development data.

## Per-bar score

A bar may map to one key from each dense family and zero or more event-family keys.

For every matching admitted family/key, retrieve its frozen effect.

The bar score is:

`score = median(all matching admitted state effects)`

If no admitted state key matches:

`score = 0`

The effects are **not summed**, to avoid double-counting correlated descriptions of the same market state.

## From score to target exposure

No hand-picked score cutoffs are allowed.

Using Discovery-79 bars only, compute the empirical score distribution and freeze:

- q20
- q40
- q60
- q80

Then map score to exposure:

- score <= q20 -> 0%
- q20 < score <= q40 -> 25%
- q40 < score <= q60 -> 50%
- q60 < score <= q80 -> 75%
- score > q80 -> 100%

If score is exactly zero and zero occupies multiple quantile boundaries, ties use the lower-risk bucket.

This is the complete trading policy.

There is:
- no V7 rule priority,
- no BUY/SELL labels,
- no C2,
- no forced holding period,
- no stop-loss,
- no take-profit,
- no extra trend filter.

## Execution

At each selected daily bar close:
1. calculate SLTD state;
2. calculate state score;
3. map score to target exposure;
4. rebalance to that target at next daily open.

Rebalancing cost is charged on traded notional.

Friction tests:
- 5 bps primary
- 10 bps
- 20 bps stress

## Comparators

On the exact same Fresh30 window:

1. `SLTD_STATE_SCORE_V1`
2. current pure `SLTD_V7`
3. `BUY_HOLD`
4. `SMA200_TREND`

V7 is a comparator only. It is not part of the score mode.

## Formal window

- warm-up data begins 2010-01-04 where available
- formal evaluation: 2020-01-02 .. 2026-09-30
- daily bars
- raw unadjusted Yahoo OHLC to match the existing US-stock research protocol

## Model sanity before portfolio interpretation

On the unseen Fresh30, score buckets must preserve ordering.

For each score-exposure bucket, report:
- count
- 10d median forward return
- 20d median forward return
- 10d win rate
- 20d win rate

Monotonicity gate:

The five exposure buckets must have a non-decreasing cross-bucket median 20d forward return, allowing at most one adjacent inversion smaller than 0.25 percentage points.

If this fails, the score itself is not considered stable enough, regardless of portfolio PnL.

## Fresh30 admission gates

At 5 bps, the new independent score mode must satisfy all:

- equal-weight portfolio Total Return > pure V7;
- equal-weight portfolio Calmar > pure V7;
- equal-weight portfolio Total Return >= Buy & Hold;
- equal-weight portfolio Calmar > Buy & Hold;
- portfolio MaxDD less severe than Buy & Hold;
- per-symbol Total Return > V7 in >= 16/30;
- per-symbol Calmar > V7 in >= 16/30;
- per-symbol Total Return > Buy & Hold in >= 16/30;
- score-bucket monotonicity gate passes.

Friction durability:
- at 10 bps, score-mode Total Return must still exceed V7;
- at 20 bps, score-mode Calmar must still exceed V7.

## Decision

All gates pass:
`PROMOTE_STATE_SCORE_MODE_TO_ENGINEERING_CANDIDATE`

Portfolio beats V7 but fails Buy & Hold or score monotonicity:
`RESEARCH_ONLY_NEEDS_NEW_SCORE_ARCHITECTURE`

Fails to beat V7 return or Calmar at 5 bps:
`REJECTED_STATE_SCORE_V1`

No threshold, universe or mapping may be changed after Fresh30 is observed.

`SLTD_STATE_SCORE_MODE_V1_PROTOCOL = FROZEN`
