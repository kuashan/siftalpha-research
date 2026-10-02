# SSSS V6 — Independent Validation of Five V5 Discoveries

Status: **FROZEN BEFORE OUTCOME RUN**
Date: 2026-10-02

## Objective

Independently validate the five discoveries surfaced by V5.

V6 does **not** modify:
- XMA formulas
- color-state definitions
- state-age buckets
- event definitions
- subtype definitions
- outcome horizons
- the five candidate definitions

## Five frozen V5 discoveries

### V6-A
ID: NEW_V5_A_GREEN_TO_GRAY_1_3_LIGHT_SUPPORT

Definition:
- origin state = GREEN
- current state = GRAY
- current GRAY age = 1-3 bars
- new LIGHT_SUPPORT event

Primary outcome:
- SUPPORT_HOLD within 20 bars

V5 discovery:
- n = 48
- p = 87.5%
- eligible symbols = 9
- support fraction = 100%

### V6-B
ID: NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE

Definition:
- current state = BLUE
- state age = 21+
- new UPPER event
- subtype = CLOSE_ABOVE

Primary outcome:
- BS before MID within 20 bars

V5 discovery:
- n = 228
- p = 82.9%
- eligible symbols = 20
- support fraction = 95%

### V6-C
ID: NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY

Definition:
- current state = GRAY
- state age = 4-10
- new LOWER event
- subtype = WICK_ONLY

Primary outcome:
- MID before BD within 20 bars

V5 discovery:
- n = 45
- p = 82.2%
- eligible symbols = 9
- support fraction = 77.8%

### V6-D
ID: NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY

Definition:
- current state = GREEN
- state age = 11-20
- new UPPER event
- subtype = WICK_ONLY

Primary outcome:
- MID before BS within 20 bars

V5 discovery:
- n = 49
- p = 77.6%
- eligible symbols = 8
- support fraction = 87.5%

### V6-E
ID: NEW_V5_E_GREEN_11_20_LIGHT_RESIST

Definition:
- current state = GREEN
- state age = 11-20
- new LIGHT_RESIST event

Primary outcome:
- RESIST_HOLD within 20 bars

V5 discovery:
- n = 88
- p = 78.4%
- eligible symbols = 16
- support fraction = 93.8%

## Independent universe

None of the following 20 stocks appeared in the earlier 39-stock universe or in
the V5 20-stock discovery universe.

### Batch 1 — Technology
- ACN
- NOW
- INTU
- AMAT
- LRCX

### Batch 2 — Consumer
- BKNG
- TJX
- CMG
- ROST
- MAR

### Batch 3 — Healthcare
- DHR
- SYK
- MDT
- BMY
- ISRG

### Batch 4 — Financial / Industrial
- SCHW
- SPGI
- DE
- HON
- RTX

### Batch 5 — independent crypto transfer
The V5 crypto discovery set BTC/ETH/BNB/SOL is **not** reused as independent
evidence. V6 instead uses:
- XRP/USD
- ADA/USD
- DOGE/USD
- LTC/USD

## Data window

Main validation window:
- 2020-01-02 through 2026-09-30

Warm-up:
- stocks requested from 2010-01-04 where available
- crypto requested from 2016-01-01 where available
- earlier bars are warm-up only
- if crypto has insufficient pre-2020 history, at least the first 180 returned
  daily bars are warm-up and excluded from event eligibility

An event is eligible only when a complete 20-bar future window exists.

## Historical reconstruction

Representation:
- FIRST_OBSERVED only

At bar t:
- use only data <= t
- recompute right-edge XMA
- store the state visible at t
- never substitute finalized future-repainted rails

Immutable formulas:
- XMA(XMA(L,25),25)
- XMA(XMA(H,25),25)
- XMA(XMA(L,60),60)
- XMA(XMA(H,60),60)

True light-gray band:
- upper = GZB3
- lower = GZB4

## Frozen event definitions

LOWER:
- Low < current FIRST_OBSERVED ZD1
- previous bar was not already below previous FIRST_OBSERVED ZD1

LOWER subtype:
- WICK_ONLY: Low < ZD1 and Close >= ZD1
- CLOSE_BELOW: Close < ZD1 and High >= ZD1
- FULL_BELOW: High < ZD1

UPPER:
- High > current FIRST_OBSERVED ZK1
- previous bar was not already above previous FIRST_OBSERVED ZK1

UPPER subtype:
- WICK_ONLY: High > ZK1 and Close <= ZK1
- CLOSE_ABOVE: Close > ZK1 and Low <= ZK1
- FULL_ABOVE: Low > ZK1

LIGHT_SUPPORT:
- prior Close > prior GZB3
- current bar intersects [GZB4,GZB3]
- de-cluster consecutive contacts
- HOLD = first decisive close above GZB3 before a close below GZB4
- BREAK = close below GZB4 first

LIGHT_RESIST:
- prior Close < prior GZB4
- current bar intersects [GZB4,GZB3]
- de-cluster consecutive contacts
- HOLD = first decisive close below GZB4 before a close above GZB3
- BREAK = close above GZB3 first

For strict comparability with V5, the light-band outcome scan begins on the
event bar.

## V6 validation statistics

For each rule:
- pooled n
- primary hits
- pooled probability
- eligible symbols
- supporting symbols
- neutral symbols
- opposing symbols
- support fraction
- median per-symbol probability
- 20-bar median return
- 20-bar median MFE
- 20-bar median MAE

Eligible stock:
- >= 3 rule events

Eligible crypto:
- >= 3 rule events

## Stock classification

Breadth-qualified:
- pooled n >= 30
- >= 7 eligible stocks

Then:

**VALIDATED_V6_STRONG**
- pooled probability >= 65%
- support fraction >= 70%

**VALIDATED_V6**
- pooled probability >= 58%
- support fraction >= 60%

**CONTRADICTED_V6**
- pooled probability <= 42%
- >= 60% of eligible symbols favor the opposite direction

**MIXED_V6**
- breadth-qualified but none of the above

Otherwise:
- **INSUFFICIENT_BREADTH**

## Crypto transfer classification

Breadth-qualified:
- pooled n >= 20
- >= 3 eligible crypto assets

Then:

**SUPPORTS_V6_STOCK**
- pooled probability >= 60%
- at least 2/3 eligible assets > 50%

**CONTRADICTS_V6_STOCK**
- pooled probability <= 40%
- at least 2/3 favor the opposite direction

**MIXED**
- otherwise

Otherwise:
- **INSUFFICIENT_BREADTH**

## Final V6 disposition

- PROMOTE_TO_FORMAL: stock = VALIDATED_V6_STRONG or VALIDATED_V6
- HOLD_FOR_MORE_DATA: stock = INSUFFICIENT_BREADTH
- KEEP_AS_WATCH: stock = MIXED_V6
- DROP_DISCOVERY: stock = CONTRADICTED_V6

Crypto is a transfer check and does not override the stock validation status.

## Batch discipline

Each batch must be calculated, written to GitHub, and closed before the next
batch.

After Batch 5:
- merge all independent evidence
- classify all five rules
- compare V5 discovery vs V6 validation
- write V6 final result and machine-readable summary

`SSSS_V6_FIVE_V5_DISCOVERY_INDEPENDENT_PROTOCOL = FROZEN`
