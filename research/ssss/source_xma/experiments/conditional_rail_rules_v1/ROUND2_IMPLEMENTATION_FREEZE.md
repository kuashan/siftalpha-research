# SSSS Conditional Rail Rules v1 — Round 2 Implementation Freeze

Status: FROZEN_BEFORE_ROUND2_OUTCOME_ANALYSIS
Date: 2026-10-01

## Scope
Universe: frozen 39 equities.
Evaluation window: 2020-01-01 through 2025-12-31.
Warm-up source begins 2019-01-01.

## Mandatory XMA chronology
For every symbol and every bar t:
1. expose only data <= t;
2. recompute right-edge double XMA25 and double XMA60;
3. store first-observed rails and raw Source-SSSS state;
4. classify current event;
5. only then advance to t+1;
6. never overwrite prior rails/events with later repaint.

## Base rails
- lower outer: BD
- fast lower: ZD1
- analytical midpoint: MID=(ZK1+ZD1)/2
- fast upper: ZK1
- upper outer: BS
- slow light-gray band: GZB3..GZB4

## State authority
Raw Source-SSSS state:
- UP
- DOWN
- RANGE
- EXPANSION stored separately.

## R2-L: Lower-origin sequence
Episode starts on first bar with LOW < ZD1 after prior bar was not below ZD1.

Within the next 20 trading bars:
- MID_RECLAIM = first bar whose CLOSE >= its own first-observed MID after at least one event/or subsequent CLOSE < MID has existed.
- UPPER_HIT = first bar whose HIGH >= its own first-observed ZK1.
- LOWER_OUTER_HIT = first bar whose LOW <= its own first-observed BD.
- EVENT_LOW_BREAK = later LOW < event-bar LOW.

Measure:
- event-close forward returns;
- probability MID_RECLAIM within 3/5/10/20 bars;
- after MID_RECLAIM, 5/10/20-bar return from reclaim close;
- after MID_RECLAIM, probability UPPER_HIT before LOWER_OUTER_HIT;
- failure = LOWER_OUTER_HIT before UPPER_HIT after reclaim.

## R2-U: Upper-origin sequence
Episode starts on first bar with HIGH > ZK1 after prior bar was not above ZK1.

Within next 20 bars:
- MID_LOSS = first bar whose CLOSE <= its own first-observed MID after at least one event/or subsequent CLOSE > MID has existed.
- LOWER_HIT = first bar whose LOW <= its own first-observed ZD1.
- UPPER_OUTER_HIT = first bar whose HIGH >= its own first-observed BS.
- EVENT_HIGH_BREAK = later HIGH > event-bar HIGH.

Measure:
- probability MID_LOSS within 3/5/10/20 bars;
- after MID_LOSS, 5/10/20-bar return from loss close;
- after MID_LOSS, probability LOWER_HIT before UPPER_OUTER_HIT;
- continuation = UPPER_OUTER_HIT before LOWER_HIT after loss.

## R2-O: Outer-rail confluence
At lower-fast event:
DIST_LOWER_ATR = abs(ZD1-BD)/ATR14.
At upper-fast event:
DIST_UPPER_ATR = abs(ZK1-BS)/ATR14.

Bins:
- <=0.25 ATR
- (0.25,0.50]
- (0.50,1.00]
- >1.00

Compare event counts, 5/20-bar returns, positive-rate, MFE/MAE by state and bin.

## R2-G: Slow gray-band structure
For gray-band approach events record:
- approach: FROM_ABOVE / FROM_BELOW
- penetration: TOUCH_RECLAIM / ENTER_BAND / FULL_CROSS or analogous reject form
- slow-band slope over 5 bars:
  RISING if midpoint(GZB3,GZB4)_t > midpoint_{t-5}
  FALLING if <
  FLAT only if exact equality
- fast state at event
- 5/20-bar outcome.

No slope threshold is tuned in this round.

## R2-S: State transition conditioning
For every lower/upper fast event, inspect the first raw-state transition within 10 bars.
Record exact transition, e.g. DOWN->RANGE, RANGE->UP, UP->RANGE.

Compare:
- event outcome with no transition;
- outcome after specific transition;
- lower-origin MID_RECLAIM and upper-origin MID_LOSS rates by transition.

## Robustness blocks
A: 2020-2022
B: 2023-2024
C: 2025

No condition is promoted unless its direction is reasonably consistent across multiple blocks and not explained by a tiny sample.

## Governance
Round 2 discovers conditional paths only.
No position size, full strategy, or production rule is frozen here.
