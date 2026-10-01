# SSSS Reboot v1 — Rail Support / Resistance Study Protocol v1

Status: **FROZEN BEFORE OUTCOME RUN**
Date: 2026-10-02
Parent:
- PHASE0_SOURCE_RECONSTRUCTION = PASS
- PHASE1_STRUCTURE_INVENTORY = CLOSED

## 1. Purpose

Test four user-defined questions without changing the original XMA structure:

1. When price exceeds the inner lower rail, how strong is the subsequent rebound
   under each of the three SSSS states?
2. When price exceeds the inner upper rail, how strong is the subsequent decline
   under each of the three states, and how often does the middle rail act as support?
3. When price reaches the outer lower/upper rail after exceeding the inner band,
   do the outer rails behave as additional support / resistance zones?
4. When price approaches the slow light-gray band from above or below, does that
   band behave as support / resistance?

## 2. XMA immutability

Hard constraint:
- preserve XMA(XMA(L,25),25)
- preserve XMA(XMA(H,25),25)
- preserve XMA(XMA(L,60),60)
- preserve XMA(XMA(H,60),60)

No EMA/DEMA/SMA/WMA replacement.
No causalized XMA substitute.
No change to centered/repainting behavior.

The only corrections allowed are the already-authorized non-XMA source typos:
- low weighted H/L typo -> L
- 20..1 weights over lags 0..19, denominator 210

## 3. Historical representation

All main results use **FIRST_OBSERVED**.

For every bar t:
1. only data <= t are visible;
2. recompute the right-edge XMA25 and XMA60 exactly as Futu/HQChart-style XMA;
3. persist the first-observed rails/state for t;
4. advance to t+1.

Future path evaluation uses the future bars' own first-observed moving rails.
No finalized historical XMA line is read back from the future.

## 4. Discovery universe

Stocks:
AAPL, MSFT, NVDA, AMD, AVGO, ORCL, INTC, QCOM, MU,
GOOGL, META, NFLX,
AMZN, TSLA, HD, MCD, WMT, COST, PG, KO, PEP,
ABT, LLY, UNH, JNJ, TMO,
JPM, BAC, GS, V, MA,
CAT, BA, GE, XOM, CVX, LIN, NEE, PLD

Discovery window:
2020-01-02 through 2025-12-31

Warm-up:
history beginning no later than 2018-01-02 where available.

2026 is not used in this discovery run and remains available for later forward/OOS checks.

## 5. State labels

Use formula states as the statistical primary key:
- UP_STATE
- DOWN_STATE
- RANGE_STATE

Display-color names are kept separately to avoid ambiguity in screenshots/UI.

EXPANSION is recorded but excluded from the three-color headline comparison because
it is outside the original three-state display vocabulary.

## 6. Episode de-clustering

Repeated consecutive bars outside the same rail must not be counted as independent
new signals.

A new excursion episode begins only when the current bar enters the condition
after the prior bar was not already in that same outside condition.

## 7. Question A — inner lower-rail excursion

Primary event:
- current Low < current ZD1
- previous bar was not already below its first-observed ZD1

Subtypes:
- WICK_ONLY: Low < ZD1 and Close >= ZD1
- CLOSE_BELOW: Close < ZD1 and High >= ZD1
- FULL_BELOW: High < ZD1

For each event and state record:

### Path targets
Within 5 / 10 / 20 / 40 bars:
- hit MID: future High >= that future bar's first-observed MID
- hit ZK1: future High >= that future bar's first-observed ZK1
- hit BD: future Low <= that future bar's first-observed BD

### First-hit race
- MID_BEFORE_BD
- BD_BEFORE_MID
- NEITHER within horizon

### Rebound strength
From event close:
- MFE_5 / MFE_10 / MFE_20 / MFE_40
- MAE_5 / MAE_10 / MAE_20 / MAE_40
- forward close return at 1 / 3 / 5 / 10 / 20 / 40 bars

This directly tests whether lower-rail excursions tend to:
- rebound only to MID,
- rebound to ZK1,
- or continue lower toward BD.

## 8. Question B — inner upper-rail excursion

Primary event:
- current High > current ZK1
- previous bar was not already above its first-observed ZK1

Subtypes:
- WICK_ONLY: High > ZK1 and Close <= ZK1
- CLOSE_ABOVE: Close > ZK1 and Low <= ZK1
- FULL_ABOVE: Low > ZK1

For each event and state record:

Within 5 / 10 / 20 / 40 bars:
- hit MID: future Low <= future first-observed MID
- hit ZD1: future Low <= future first-observed ZD1
- hit BS: future High >= future first-observed BS

First-hit race:
- MID_BEFORE_BS
- BS_BEFORE_MID
- NEITHER

Decline / continuation strength:
- MFE and MAE over 5 / 10 / 20 / 40 bars
- forward close return at 1 / 3 / 5 / 10 / 20 / 40 bars

## 9. Middle-rail support test

Separate event:
- price approaches MID from above;
- previous close > previous first-observed MID;
- current Low <= current MID.

For each state at the touch bar:

Immediate behavior:
- close back above MID on the touch bar?

20-bar structural race:
- hit ZK1 before ZD1 = MID_SUPPORT_SUCCESS
- hit ZD1 before ZK1 = MID_SUPPORT_FAILURE
- neither = UNRESOLVED

Also report 5 / 10 / 20-bar MFE / MAE and return.

This directly measures the support probability of MID inside each state.

## 10. Question C — outer rails

### Outer lower support candidate
New episode when:
- Low <= BD
- previous bar was not already at/below BD.

Record:
- state
- whether inner lower rail had already been exceeded in the same excursion
- hit ZD1 within 5 / 10 / 20 / 40 bars
- hit MID within 5 / 10 / 20 / 40 bars
- MFE / MAE / forward return

### Outer upper resistance candidate
New episode when:
- High >= BS
- previous bar was not already at/above BS.

Record:
- state
- whether inner upper rail had already been exceeded
- hit ZK1 within 5 / 10 / 20 / 40 bars
- hit MID within 5 / 10 / 20 / 40 bars
- MFE / MAE / forward return

Outer rails are not called support/resistance until the results justify it.

## 11. Question D — light-gray slow band

The slow band is [GZB9, GZB8].

### Support-from-above event
- previous bar entirely above the slow band or closes above GZB8;
- current Low <= GZB8;
- current High >= GZB9.

Primary exact-touch statistics:
- first decisive band exit upward vs downward;
- close above GZB8 after touch;
- close below GZB9 after touch;
- 5 / 10 / 20 / 40-bar return, MFE, MAE.

### Resistance-from-below event
- previous bar entirely below the slow band or closes below GZB9;
- current High >= GZB9;
- current Low <= GZB8.

Primary exact-touch statistics:
- first decisive band exit downward vs upward;
- close below GZB9 after touch;
- close above GZB8 after touch;
- 5 / 10 / 20 / 40-bar return, MFE, MAE.

Because exact touches may be rare, event count is reported first.
No looser threshold is introduced in this v1 protocol after seeing outcomes.

If exact-touch n is too small, a separately preregistered v2 may test near-touch
distance buckets.

## 12. Required reporting

For every event family:
- n
- state/color breakdown
- median and mean forward return
- p10/p25/p50/p75/p90
- positive-return rate
- MFE median / p25 / p75
- MAE median / p25 / p75
- target-hit probabilities
- first-hit race probabilities
- symbol breadth
- time-block stability
- leave-one-symbol-out directional stability where sample size permits

## 13. Interpretation discipline

This study may say:
- one state has stronger rebound than another;
- one rail behaves more consistently as support/resistance;
- a path target is reached with a measured probability.

It may not yet say:
- BUY here
- SELL here
- use x% position
- this is the final strategy

Trading rules come only after the empirical structure is known.

## 14. Closure

This study closes only after all four user questions have complete results.

No protocol change is allowed after outcome statistics are viewed in this run.
