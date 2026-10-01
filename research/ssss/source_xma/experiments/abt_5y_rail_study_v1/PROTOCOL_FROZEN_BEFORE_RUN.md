# ABT 5-Year SSSS Rail Study v1

Status: FROZEN_BEFORE_RUN / DISCOVERY
Date: 2026-10-01

## Scope
- Symbol: ABT
- Timeframe: 1D
- Evaluation window: 2021-01-01 through 2025-12-31
- Warm-up: 2020-01-01 through 2020-12-31 only
- No 2020 outcome is included in evaluation statistics.

## Mandatory XMA chronology
For every bar t:
1. use only data available through t;
2. recompute right-edge XMA25 and XMA60 point-in-time;
3. save first-observed ZD1 / GZB18 / ZK1 / BD / BS and color state;
4. classify current event;
5. only then advance to t+1;
6. later XMA repaint must never overwrite the stored state/event at t.

XMA uses the centered/truncated Source-XMA behavior documented in
XMA_IMPLEMENTATION_REFERENCES.md:
- odd N=25 => 12 bars left, 12 right when available;
- even N=60 => 30 bars left, 29 right when available;
- at the right edge, unavailable future bars are truncated.

## Structures
- lower outer: BD
- fast lower: ZD1
- analytical fast midpoint: GZB18=(ZK1+ZD1)/2
- fast upper: ZK1
- upper outer: BS
- raw Source-SSSS state/color authority: UP / DOWN / RANGE
- light-gray slow band: GZB3..GZB4
- EXPANSION stored separately

## Event definitions
Same as rail_color_path_study_v1:
- LOWER_FAST onset: low < ZD1 after a non-excursion bar
- UPPER_FAST onset: high > ZK1 after a non-excursion bar
- LOWER_OUTER onset: low <= BD after a non-event bar
- UPPER_OUTER onset: high >= BS after a non-event bar
- GRAY_SUPPORT: approach from above and touch/enter GZB3..GZB4
- GRAY_RESIST: approach from below and touch/enter GZB3..GZB4

Repeated contiguous fast/outer excursions are one episode.

## Measurements
By color/state:
- event count
- forward close return 3/5/10/20 bars
- MFE / MAE
- lower-event path: upper / midpoint-only / continue-down / unresolved
- upper-event path: lower / midpoint-only / continue-up / unresolved
- midpoint 3-bar hold after descent from upper
- midpoint rebound-to-upper-before-lower
- outer-rail state behavior
- light-gray-band interaction behavior
- year-by-year stability

## Governance
This is a single-asset Discovery study.
No production buy/sell/add/reduce/exit rule may be promoted from ABT alone.
