# SSSS Reboot — AAPL Cross-Symbol Validation v2.5 Protocol

Status: **FROZEN BEFORE AAPL OUTCOME RUN**
Date: 2026-10-02

## Purpose

Validate, without modification, the candidate BUY / SELL structures discovered
on ABT in v2.3-v2.4.

AAPL is the second symbol and serves as a cross-symbol validation sample.

## Non-negotiable rule

No event definition, color-state definition, state-age bucket, transition rule,
light-gray-band definition, or XMA formula may be changed because of AAPL
results.

If AAPL disagrees with ABT, record the disagreement.

## Data

- Symbol: AAPL
- Interval: daily
- Main statistical window: 2018-01-02 through 2025-12-31 where provider data exist
- Earlier history: warm-up only
- Historical representation: FIRST_OBSERVED bar-by-bar
- XMA25/XMA60: unchanged

## Frozen states

- BLUE = GZB12 / COLOR000066
- GREEN = GZB13 / COLOR003300
- GRAY = GZB14 / COLOR555555

True light-gray band:
- upper = GZB3
- lower = GZB4

State age:
- 1-3
- 4-10
- 11-20
- 21+

Recent transition:
- current state age <= 5

## Frozen events

### BUY-side
New inner-lower break:
- Low < ZD1
- previous bar was not already below prior FIRST_OBSERVED ZD1

Measure:
- MID hit
- ZK1 hit
- BD hit
- MID before BD
- BD before MID
- true light-gray-band touch
- 20-bar MFE / MAE / close return

### SELL-side
New inner-upper break:
- High > ZK1
- previous bar was not already above prior FIRST_OBSERVED ZK1

Measure:
- MID hit
- ZD1 hit
- BS hit
- MID before BS
- BS before MID
- true light-gray-band touch
- 20-bar MFE / MAE / close return

### True light-gray support / resistance

Support from above:
- prior Close > prior GZB3
- current bar intersects [GZB4,GZB3]
- de-cluster consecutive contacts
- HOLD if close back above GZB3 before close below GZB4
- BREAK otherwise first decisive opposite close

Resistance from below:
- prior Close < prior GZB4
- current bar intersects [GZB4,GZB3]
- HOLD if close back below GZB4 before close above GZB3
- BREAK otherwise first decisive opposite close

## Candidate structures to validate

### BUY-side
1. Recent GRAY->GREEN + inner-lower break is an avoid-first-entry context.
2. GREEN 11-20 + inner-lower break tends to travel to BD first.
3. GREEN 21+ + inner-lower break behaves more like a BUY candidate.
4. BLUE 21+ + inner-lower break behaves relatively cleanly.
5. GRAY 4-20 + light-gray support from above is a support candidate.
6. Recent BLUE->GRAY + light-gray support is a boundary-support candidate.

### SELL-side
1. Recent GRAY->BLUE + inner-upper break tends to continue toward BS.
2. BLUE 4-20 + inner-upper break is an avoid-final-exit context.
3. GREEN 21+ + inner-upper break behaves more like a tactical SELL candidate.
4. Recent BLUE->GRAY + light-gray resistance is a pressure candidate.

## Minimum sample rule

n >= 5 required before a context may be compared as a candidate.
n < 5 is insufficient and must not be treated as confirmation or rejection.

## Validation interpretation

Each candidate will be marked:
- SUPPORTS_ABT
- MIXED
- CONTRADICTS_ABT
- INSUFFICIENT_N

No trading rule is frozen after AAPL alone.
