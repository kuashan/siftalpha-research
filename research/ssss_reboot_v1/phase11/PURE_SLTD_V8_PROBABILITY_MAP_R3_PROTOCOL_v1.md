# Pure SLTD V8 Probability-Map Candidate R3 — Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

## Purpose

R2 showed that the two-rule pure-SLTD probability map improved portfolio return,
Calmar and breadth on a fresh 20-stock universe, but it failed a sell sanity gate
that required the post-SELL absolute return to be non-positive.

That gate was not aligned with the original state-probability study, whose primary
signal was **symbol-drift-adjusted excess return**. In an upward-drifting stock,
a useful risk-reduction state can have positive absolute forward return while still
have materially negative excess return.

R3 fixes that methodological mismatch prospectively on a completely new stock universe.
R2 is not reclassified and remains RESEARCH_ONLY_NOT_PROMOTED.

## Candidate is unchanged

No condition is altered from R2.

### PM_BUY_1

- GREEN
- run_age >= 21
- lower = true
- lower_subtype = CLOSE_BELOW
- action: ordinary BUY using existing +25 percentage-point policy

### PM_SELL_1

- BLUE
- run_age >= 21
- upper = true
- upper_subtype = WICK_ONLY
- action: ordinary SELL of 25% of current holding
- executed SELL arms existing C2

Everything else remains frozen:
- current 12 V7 rules,
- NO_CHANGE_MIXED,
- C2 hard exit priority,
- signal close -> next available open,
- no Chan/缠论 inside SLTD.

## Fresh R3 universe — 20 stocks

No symbol overlaps:
- the original 79,
- the prior fresh OOS10,
- or R2 Fresh20.

Financial:
- PNC, USB, CME

Healthcare:
- HCA, CI, BDX

Industrials:
- ETN, PH, ITW

Materials:
- APD, SHW, FCX

Consumer:
- YUM, ORLY

Real estate:
- AMT, CCI

Utilities:
- ED, SRE

Energy:
- PSX, KMI

Data are fetched only after this protocol is committed.

## Window and execution

- Daily bars
- warm-up: earliest available from 2010-01-04
- formal evaluation: 2020-01-02 .. 2026-09-30
- Yahoo Finance raw unadjusted OHLC, consistent with the existing US-stock protocol
- 5 bps primary friction
- 10 bps sensitivity
- signal at bar close -> next bar open execution

## Systems

1. V7_BASE
2. PMAP_14 = V7 + PM_BUY_1 + PM_SELL_1
3. BUY_HOLD
4. SMA200_TREND

## Event validation — drift-adjusted

For every symbol and horizon h in {10, 20}:

- unconditional median = median forward return of all eligible bars,
  entry at next-bar open;
- event median = median forward return after the specified event;
- event excess = event median - unconditional median.

Across symbols, use:
- median event excess;
- directional breadth among symbols containing the event.

Support requirements:
- PM_BUY_1: >= 60 total events and present in >= 10 stocks;
- PM_SELL_1: >= 100 total events and present in >= 12 stocks.

PM_BUY_1 gate:
- cross-symbol median excess > 0 at 10d and 20d;
- positive excess breadth >= 60% at 10d and 20d.

PM_SELL_1 gate:
- cross-symbol median excess < 0 at 10d and 20d;
- negative excess breadth >= 60% at 10d and 20d.

Absolute forward returns are reported but are not the primary gate.

## Portfolio admission gates

At 5 bps, PMAP_14 must:
- beat V7_BASE total return;
- beat V7_BASE Calmar;
- not worsen portfolio MaxDD by more than 1.0 percentage point;
- beat V7_BASE total return in >= 11/20 symbols;
- beat V7_BASE Calmar in >= 11/20 symbols.

At 10 bps:
- PMAP_14 must still beat V7_BASE total return;
- PMAP_14 must still beat V7_BASE Calmar.

Simple-baseline guard:
- PMAP_14 Calmar > SMA200_TREND Calmar,
  OR PMAP_14 has higher return than SMA200_TREND with no worse MaxDD.

## Decision

All portfolio, friction, support and drift-adjusted event gates pass:
- PROMOTE_TO_ENGINEERING_CANDIDATE

Portfolio gates pass but any event/support/friction gate fails:
- RESEARCH_ONLY_NOT_PROMOTED

Return or Calmar fails versus V7 at 5 bps:
- REJECTED_NOT_ADMITTED

No thresholds may be changed after R3 data are observed.

PURE_SLTD_V8_PROBABILITY_MAP_R3_PROTOCOL = FROZEN
