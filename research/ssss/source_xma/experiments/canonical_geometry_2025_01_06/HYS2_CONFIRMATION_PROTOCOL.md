# HYS2 Confirmation Protocol — Canonical XMA Geometry

Status: FROZEN BEFORE HYS2 CONFIRMATION RUN  
Date: 2026-09-28

## Purpose

Test HYS2 only as an auxiliary confirmation layer on already-defined canonical XMA geometry events.

HYS2 does not create the XMA event.

## XMA events are unchanged

Lower precursor episode:
- state = DOWN
- candle overlaps ZD1 and BD
- abs(ZD1-BD) <= 0.50 ATR14
- repeated qualifying bars within 3 bars deduplicated

Upper warning episode:
- state = UP
- candle overlaps ZK1 and BS
- abs(ZK1-BS) <= 0.25 ATR14
- repeated qualifying bars within 3 bars deduplicated

## HYS2 market branch

Stocks:
- SCQH=1

Crypto:
- SCQH=2

These reproduce the source branches; they are not assumed optimal.

## Causal confirmation window

Only HYS2 information already available by the XMA event date may confirm the event.

Use the current bar and previous 3 bars:

```text
lookback = t-3 .. t
```

No future HYS2 event is used to label an XMA event as confirmed.

## Lower-side HYS2 features

Record separately:
1. `HYS_RESONANCE_RECENT`
   - source ★ resonance occurred in t-3..t
2. `HYS_FIRE_BOTTOM_RECENT`
   - source fire-bottom value > 0 in t-3..t
3. `HYS_BULL_CROSS_RECENT`
   - ordinary L1/L2 bullish cross with L2<55 in t-3..t

Do not combine them into one score before ablation.

## Upper-side HYS2 features

Record separately:
1. `HYS_FIRE_TOP_RECENT`
   - source fire-top value < 0 in t-3..t
2. `HYS_BEAR_CROSS_RECENT`
   - L2 crosses above L1 with L2>70 in t-3..t

Fire-top is not interpreted as an automatic short.

## Evaluation

For each XMA episode compare:
- HYS feature present
- HYS feature absent

Outcomes:
- +5 / +10 / +20 close return
- positive-return rate
- median return

Minimum sample guidance:
- n < 5: INCONCLUSIVE
- n 5..9: OBSERVE
- n >=10: eligible for stronger candidate status, still Discovery only

No HYS2 threshold will be tuned after seeing this window.
