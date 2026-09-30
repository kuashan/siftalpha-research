# Canonical XMA Geometry Event Study Protocol v1

Status: FROZEN BEFORE RUN  
Date: 2026-09-28

## Purpose

Test the user's observed XMA geometry hypotheses after formula correction, without using HYS2, FIVEGZ, Volume, VIX, Breadth, or Volume Profile to define the original event.

This is a Discovery event study, not OOS validation.

## Chronology

For every date t:
1. use only data available through t;
2. calculate right-edge XMA25 and XMA60 point-in-time;
3. calculate corrected W20/EMA90 slow structure;
4. save first-observed rails and state;
5. classify the current candle/rail geometry;
6. only after saving t, advance to t+1.

No later XMA repaint may overwrite t.

## Universe

Equities:
ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM

Crypto:
BTC, ETH, BNB, SOL

ARM remains pending verified daily OHLCV.

## Evaluation window

Primary discovery window:
2025-01-02 through 2025-06-30 for equities where data exist.

Crypto:
2025-01-01 through 2025-06-30.

Older data are warm-up only.

## Formula ids

Fast:
- ZK1 = fast upper
- ZD1 = fast lower
- GZB18 = fast midpoint analytical line

Outer:
- BS = outer upper 60-XMA rail
- BD = outer lower 60-XMA rail

Slow:
- GZB8 = slow outer upper structure
- GZB9 = slow outer lower structure

## Exclusive band state

```text
UP_STATE:
ZD1 >= GZB9 AND ZK1 > GZB8

DOWN_STATE:
ZD1 < GZB9 AND ZK1 <= GZB8

RANGE_STATE:
ZD1 >= GZB9 AND ZK1 <= GZB8

EXPANSION_STRADDLE:
ZD1 < GZB9 AND ZK1 > GZB8
```

Also preserve original GZB12/13/14 booleans.

## Geometry distances

Normalize rail distances by ATR14.

```text
lower_gap_atr = abs(ZD1-BD)/ATR14
upper_gap_atr = abs(ZK1-BS)/ATR14
```

Study bins:
- 0 to 0.25 ATR
- >0.25 to 0.50
- >0.50 to 1.00
- >1.00 to 2.00
- >2.00

No one bin is pre-declared a buy/sell threshold.

## Rail crossing events

Lower rail-cross:
```text
(ZD1-BD) changes sign between t-1 and t
```

Upper rail-cross:
```text
(ZK1-BS) changes sign between t-1 and t
```

## Candle interaction events

For each pair of rails, classify:

- TOUCH_PAIR:
  current [low,high] overlaps both rail levels
- PIERCE_FAST:
  wick crosses fast rail
- PIERCE_OUTER:
  wick crosses outer rail
- CLOSE_OUTSIDE:
  close finishes outside the outer rail
- RECLAIM_FAST:
  price traded outside/below-above fast rail and close returns inside
- FULL_BAR_OUTSIDE:
  full candle range is outside fast rail

Lower pair:
- ZD1 + BD

Upper pair:
- ZK1 + BS

## Core hypotheses

H1 Lower pair:
When lower_gap_atr is small and the candle overlaps both ZD1/BD, future returns differ by state.

H2 Lower transition:
DOWN->RANGE or RANGE->UP near lower confluence should outperform static DOWN_STATE lower confluence.

H3 Upper pair:
Upper overlap/exceed is not universally bearish.

H4 Upper exhaustion:
UP->RANGE near upper confluence should have weaker forward return / larger downside excursion than persistent UP_STATE rail-ride.

H5 Rail ride:
Repeated upper interaction while state remains UP and fast/outer slopes stay positive should be continuation, not an automatic top.

H6 Compression:
RANGE_STATE plus narrowing fast/slow widths may precede expansion; direction must be measured rather than assumed.

## Event outcomes

For every event date measure from event close:

Forward close return:
- +1 bar
- +3
- +5
- +10
- +20

MFE:
maximum high return during next N bars.

MAE:
minimum low return during next N bars.

Use N:
- 3
- 5
- 10
- 20

Also record:
- event count
- positive-return rate
- median
- trimmed mean
- average MFE
- average MAE
- MFE/abs(MAE) ratio

## State transition fields

For each event:
- state_t
- state_t-1
- transition
- days_in_state
- fast_lower_slope
- fast_upper_slope
- outer_lower_slope
- outer_upper_slope
- fast_width_change
- slow_width_change

## No trading optimization in Phase 1

This phase does NOT choose:
- entry percentage
- stop
- take profit
- short rule

It only discovers whether pure-XMA geometry/state events have repeatable conditional behavior.

Position sizing is Phase 3+ only.

## Closure

Phase 1 closes when:
- all 15 symbols processed;
- event tables generated;
- minimum sample counts reported;
- hypotheses H1-H6 classified KEEP / DROP / OBSERVE / INCONCLUSIVE;
- no thresholds tuned after result within the same window.
