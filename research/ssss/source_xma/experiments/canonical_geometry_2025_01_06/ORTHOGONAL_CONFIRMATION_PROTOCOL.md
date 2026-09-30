# Orthogonal Confirmation Protocol — Canonical XMA Geometry

Status: FROZEN BEFORE RUN  
Date: 2026-09-28

## Purpose

Test orthogonal information on already-defined canonical XMA geometry episodes.

No auxiliary factor creates the XMA event.

## XMA episodes

Lower:
- DOWN state
- candle overlaps ZD1 + BD
- lower gap <= 0.50 ATR14
- repeated events within 3 bars deduplicated

Upper:
- UP state
- candle overlaps ZK1 + BS
- upper gap <= 0.25 ATR14
- repeated events within 3 bars deduplicated

## Factors

### Volume Structure

Use only information available on or before event date.

Positive:
- event-day return > 0 AND RVOL20 >= 1.30
OR
- signed-volume-5 > +0.15 AND RVOL20 >= 0.90

Negative:
- event-day return < 0 AND RVOL20 >= 1.50
OR
- signed-volume-5 < -0.20 AND RVOL20 >= 1.00

Otherwise neutral.

### Daily Volume Profile proxy

60-bar rolling proxy:
- daily volume assigned to typical price (H+L+C)/3
- 24 price bins
- POC = highest-volume bin
- Value Area expands around POC until >=70% rolling volume

State:
- ABOVE_VAH
- INSIDE_VALUE
- BELOW_VAL

This is not exact intraday Volume Profile.

### Breadth

Stocks:
- frozen 15-name breadth proxy from prior orthogonal protocol
- not official S&P 500 breadth

Crypto:
- BTC/ETH/BNB/SOL cross-sectional breadth

No threshold changes.

### VIX

Use the previously frozen VIX context:
- positive: below MA20 and 5-day change <= -5%
- negative: >=1.15*MA20 or 5-day change >= +15%
- neutral otherwise

VIX is a cross-asset risk proxy for crypto, not a crypto-native volatility index.

## Evaluation

For lower and upper XMA episodes, compare outcomes by each factor separately.

Do NOT create an additive score.

Outcomes:
- +5
- +10
- +20 close return

Report:
- n
- positive rate
- mean
- median

Minimum-sample discipline:
- n < 5: INCONCLUSIVE
- n 5..9: OBSERVE
- n >=10: candidate evidence, still Discovery only

No threshold tuning after this run.
