# SSSS Reboot — ABT Color-Origin + State-Age Refinement v2.4 Protocol

Status: **FROZEN BEFORE REFINEMENT OUTPUT**
Date: 2026-10-02

## Purpose

Refine the already-completed ABT three-color bidirectional rail matrix by adding:

1. how long the current BLUE / GREEN / GRAY state has lasted;
2. which color state the current run came from;
3. the true light-gray band GZB3..GZB4 in the same BUY/SELL-path framework.

This is an **exploratory refinement of the same ABT 2018-2025 discovery sample**.
It is not an independent validation set.

## Data / execution

- Symbol: ABT
- Interval: daily
- Main window: 2018-01-02 through 2025-12-31 where provider data exist
- Earlier bars: warm-up only
- Historical representation: FIRST_OBSERVED, bar-by-bar
- XMA25/XMA60: unchanged

## Color states

Presentation labels:
- BLUE = GZB12 / COLOR000066
- GREEN = GZB13 / COLOR003300
- GRAY = GZB14 / COLOR555555

True light-gray band:
- upper = GZB3
- lower = GZB4

## State-age buckets

For every event, measure the number of consecutive bars already spent in the
current color state, including the event bar:

- FRESH = 1-3 bars
- EARLY = 4-10 bars
- MATURE = 11-20 bars
- LATE = 21+ bars

These bucket boundaries are frozen before viewing this round's grouped results.

## Origin-state definition

For the current continuous color run, record the immediately preceding state run.

Primary origin labels:
- BLUE
- GREEN
- GRAY

EXPANSION may be retained in the raw ledger but is not promoted in headline
three-color comparisons.

## Recent-transition definition

A transition is considered RECENT when:
- current state age <= 5 bars.

Recent transition pair examples:
- GRAY -> BLUE
- BLUE -> GRAY
- GRAY -> GREEN
- GREEN -> GRAY

No candidate conclusion may be promoted from n < 5.

## Primary BUY-side event

Same frozen lower-inner-rail event as v2.3:

- Low < ZD1
- previous bar was not already below prior FIRST_OBSERVED ZD1

For every color x age bucket and every recent origin->current transition with n>=5,
report at 20 bars:

- hit MID
- hit inner upper ZK1
- hit outer lower BD
- MID before BD
- BD before MID
- touch true light-gray band
- median MFE
- median MAE
- median close return

Interpretation goal:
identify contexts where an inner-lower break behaves more like a BUY candidate
versus a warning that price is still likely to travel toward BD.

## Primary SELL-side event

Same frozen upper-inner-rail event as v2.3:

- High > ZK1
- previous bar was not already above prior FIRST_OBSERVED ZK1

For every color x age bucket and every recent origin->current transition with n>=5,
report at 20 bars:

- hit MID
- hit inner lower ZD1
- hit outer upper BS
- MID before BS
- BS before MID
- touch true light-gray band
- median MFE
- median MAE
- median close return

Interpretation goal:
identify contexts where an inner-upper break behaves more like a SELL candidate
versus a continuation signal toward BS.

## True light-gray band

For support-from-above and resistance-from-below episodes, also group by:

- current color x age bucket
- recent origin->current transition where n>=5

Primary 20-bar response remains based on the band itself:

Support:
- HOLD = close back above GZB3 before any close below GZB4
- BREAK = close below GZB4 first

Resistance:
- HOLD = close back below GZB4 before any close above GZB3
- BREAK = close above GZB3 first

## Reporting discipline

1. First show color x age results.
2. Then show recent transition-pair results.
3. Only n>=5 may be discussed as a candidate context.
4. Do not call any context a final BUY or SELL rule from ABT alone.
5. This round must end with a short candidate map for later cross-symbol validation.
