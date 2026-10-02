# SSSS Reboot — ABT Three-Color Bidirectional Rail Matrix v2.3 Protocol

Status: **FROZEN BEFORE OUTCOME RUN**
Date: 2026-10-02

## Goal

Measure BUY-side and SELL-side rail behavior **simultaneously** for all three
SSSS color states, with the true visual light-gray band integrated into the
same path analysis.

This round is explicitly intended to identify statistically defensible future
BUY / SELL points, but it does not pre-label any event as a final trade.

## Data

- Symbol: ABT
- Interval: daily
- Main statistical window: 2018-01-02 through 2025-12-31 where data exist
- Earlier history: warm-up only
- Historical representation: FIRST_OBSERVED, bar-by-bar
- Original XMA25 / XMA60: unchanged

## Color-state names

Use Chinese presentation labels:
- BLUE = source GZB12 / COLOR000066
- GREEN = source GZB13 / COLOR003300
- GRAY = source GZB14 / COLOR555555

The true light-gray band is independent:
- upper = GZB3
- lower = GZB4

GZB8/GZB9 remain state-classification thresholds and are not the light-gray band.

## A. Lower inner-rail break — BUY-side study

A new event starts when:
- current Low < current ZD1;
- prior bar was not already below its own FIRST_OBSERVED ZD1.

For BLUE / GREEN / GRAY separately, record within 5 / 10 / 20 bars:

1. return inside the inner lower rail:
   - future High >= future ZD1
2. touch true light-gray band:
   - future Low <= future GZB3 AND future High >= future GZB4
3. hit MID
4. hit inner upper rail ZK1
5. hit outer lower rail BD
6. MFE / MAE / close return

Primary path races:
- MID vs BD
- ZK1 vs BD
- true light-gray touch vs BD
- true light-gray touch vs MID

These races answer whether a lower-rail break is:
- a clean rebound,
- a deeper move toward BD before rebound,
- or a move that interacts with the slow light-gray structure first.

## B. Upper inner-rail break — SELL-side study

A new event starts when:
- current High > current ZK1;
- prior bar was not already above its own FIRST_OBSERVED ZK1.

For BLUE / GREEN / GRAY separately, record within 5 / 10 / 20 bars:

1. return inside the inner upper rail:
   - future Low <= future ZK1
2. touch true light-gray band
3. hit MID
4. hit inner lower rail ZD1
5. hit outer upper rail BS
6. MFE / MAE / close return

Primary path races:
- MID vs BS
- ZD1 vs BS
- true light-gray touch vs BS
- true light-gray touch vs MID

These races answer whether an upper-rail break is:
- a clean mean-reversion / sell candidate,
- or continuation toward BS before decline.

## C. True light-gray band — direct support / resistance study

### Support from above
New episode:
- prior Close > prior GZB3;
- current bar intersects [GZB4,GZB3];
- de-cluster consecutive contacts.

Primary response:
- SUPPORT_HOLD if price first closes back above GZB3 before closing below GZB4;
- SUPPORT_BREAK if price first closes below GZB4;
- unresolved otherwise.

### Resistance from below
New episode:
- prior Close < prior GZB4;
- current bar intersects [GZB4,GZB3];
- de-cluster consecutive contacts.

Primary response:
- RESIST_HOLD if price first closes back below GZB4 before closing above GZB3;
- RESIST_BREAK if price first closes above GZB3.

Both are broken down by BLUE / GREEN / GRAY.

## D. State relationship metadata

Keep, but do not use as the first headline split:
- previous state / origin state
- current state run age
- age bucket
  - 1-3
  - 4-10
  - 11-20
  - 21+

This lets the study later refine candidate BUY / SELL points without obscuring
the primary BLUE / GREEN / GRAY comparison.

## Minimum sample rule

- n >= 5: may be discussed as a candidate context
- n < 5: insufficient, descriptive only

## Reporting order

1. BLUE / GREEN / GRAY lower-break matrix
2. BLUE / GREEN / GRAY upper-break matrix
3. BLUE / GREEN / GRAY light-gray support/resistance
4. only then state-age refinements if they materially explain the first three tables

No candlestick UI color is used.
