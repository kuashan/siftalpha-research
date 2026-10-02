# SSSS V5 — 20 New Mainstream Stocks + 4 Crypto Revalidation and Optimization

Status: **FROZEN BEFORE OUTCOME RUN**
Date: 2026-10-02

## Objective

Re-evaluate and optimize the current 16 operation logics using a completely new
20-stock universe plus BTC / ETH / BNB / SOL.

The current logic set is preserved at the start of V5:

- 8 V3 validated candidates
- 5 V3 discoveries under validation
- 3 V3 mixed candidates

V5 may recommend retain / strengthen / weaken / demote after all five batches
are complete, but **no rule definition or threshold may change during the batch
runs**.

Exploratory new discoveries are allowed only after the 16 prespecified logics
have been evaluated. A new discovery is never promoted in V5 itself.

## Data window

Main outcome window:
- 2020-01-02 through 2026-09-30

Earlier history:
- warm-up only
- stocks requested from 2010-01-04 where available
- crypto requested from 2016-01-01 where available
- if crypto lacks sufficient pre-2020 history, first 180 returned daily bars
  are warm-up and not eligible as events

An event is eligible only when a complete 20-bar future window exists by the
provider end date.

Representation:
- FIRST_OBSERVED bar-by-bar
- original XMA unchanged
- true light-gray band = GZB4..GZB3

## New stock universe

These 20 symbols do not overlap with the previous 39-stock universe.

### Batch 1 — Technology
1. IBM
2. CSCO
3. CRM
4. ADBE
5. TXN

### Batch 2 — Consumer
6. DIS
7. NKE
8. SBUX
9. TGT
10. LOW

### Batch 3 — Healthcare
11. MRK
12. PFE
13. ABBV
14. AMGN
15. GILD

### Batch 4 — Financial / Energy / Industrial
16. C
17. MS
18. BLK
19. COP
20. UPS

### Batch 5 — Crypto
21. BTC/USD
22. ETH/USD
23. BNB/USD
24. SOL/USD

## Existing 16 logics

### A. Eight V3 validated candidates

1. BUY_BLUE_21P_LOWER
   - BLUE, age 21+, new LOWER
   - primary outcome: MID before BD

2. BUY_GRAY_4_10_LIGHT_SUPPORT
   - GRAY, age 4-10, new LIGHT_SUPPORT
   - primary outcome: SUPPORT_HOLD

3. BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT
   - recent BLUE -> GRAY, current age <= 5, new LIGHT_SUPPORT
   - primary outcome: SUPPORT_HOLD

4. CONT_BLUE_11_20_UPPER
   - BLUE, age 11-20, new UPPER
   - primary outcome: BS before MID

5. SELL_RECENT_BLUE_GRAY_LIGHT_RESIST
   - recent BLUE -> GRAY, current age <= 5, new LIGHT_RESIST
   - primary outcome: RESIST_HOLD

6. AVOID_GREEN_11_20_LOWER
   - GREEN, age 11-20, new LOWER
   - primary outcome: BD before MID

7. CONT_BLUE_4_10_UPPER
   - BLUE, age 4-10, new UPPER
   - primary outcome: BS before MID

8. CONT_RECENT_GRAY_BLUE_UPPER
   - recent GRAY -> BLUE, current age <= 5, new UPPER
   - primary outcome: BS before MID

### B. Five V3 discoveries

9. BLUE_11_20_LOWER_WICK_ONLY
   - BLUE, age 11-20, new LOWER, WICK_ONLY
   - primary outcome: MID before BD

10. GREEN_11_20_LOWER_CLOSE_BELOW
    - GREEN, age 11-20, new LOWER, CLOSE_BELOW
    - primary outcome: BD before MID

11. BLUE_11_20_UPPER_CLOSE_ABOVE
    - BLUE, age 11-20, new UPPER, CLOSE_ABOVE
    - primary outcome: BS before MID

12. BLUE_21P_UPPER_FULL_ABOVE
    - BLUE, age 21+, new UPPER, FULL_ABOVE
    - primary outcome: BS before MID

13. GREEN_4_10_UPPER
    - GREEN, age 4-10, new UPPER
    - primary outcome: MID before BS

### C. Three V3 mixed candidates

14. BUY_GREEN_21P_LOWER
    - GREEN, age 21+, new LOWER
    - primary outcome: MID before BD

15. AVOID_RECENT_GRAY_GREEN_LOWER
    - recent GRAY -> GREEN, current age <= 5, new LOWER
    - primary outcome: BD before MID

16. SELL_GREEN_21P_UPPER
    - GREEN, age 21+, new UPPER
    - primary outcome: MID before BS

## Frozen event definitions

LOWER:
- Low < current FIRST_OBSERVED ZD1
- prior bar not already below prior FIRST_OBSERVED ZD1

LOWER subtype:
- WICK_ONLY: Low < ZD1 and Close >= ZD1
- CLOSE_BELOW: Close < ZD1 and High >= ZD1
- FULL_BELOW: High < ZD1

UPPER:
- High > current FIRST_OBSERVED ZK1
- prior bar not already above prior FIRST_OBSERVED ZK1

UPPER subtype:
- WICK_ONLY: High > ZK1 and Close <= ZK1
- CLOSE_ABOVE: Close > ZK1 and Low <= ZK1
- FULL_ABOVE: Low > ZK1

LIGHT_SUPPORT:
- prior Close > prior GZB3
- current bar intersects [GZB4,GZB3]
- de-cluster consecutive contacts
- HOLD if the first decisive close is above GZB3 before any close below GZB4
- BREAK if close below GZB4 occurs first

LIGHT_RESIST:
- prior Close < prior GZB4
- current bar intersects [GZB4,GZB3]
- de-cluster consecutive contacts
- HOLD if the first decisive close is below GZB4 before any close above GZB3
- BREAK if close above GZB3 occurs first

For consistency with V3, light-gray outcome scanning includes the event bar.
No event-bar close-zone subgroup may be used as evidence because of the known
tautology risk.

## Metrics

For every logic:
- n
- pooled primary-outcome probability
- eligible symbols
- supporting symbols
- support fraction
- median per-symbol probability
- 20-bar median return
- 20-bar median MFE
- 20-bar median MAE

Eligible stock symbol for breadth:
- >= 3 logic events

Eligible crypto symbol for breadth:
- >= 3 logic events

## V5 classification thresholds

### Stocks

Breadth-qualified when:
- pooled n >= 30
- >= 7 eligible stocks

Then:

**STRONG_REPEAT**
- pooled primary probability >= 65%
- support fraction >= 70%

**REPEAT**
- pooled primary probability >= 58%
- support fraction >= 60%

**CONTRADICTED**
- pooled primary probability <= 42%
- at least 60% of eligible symbols favor the opposite direction

**MIXED**
- breadth-qualified but none of the above

Otherwise:
- **INSUFFICIENT_BREADTH**

### Crypto

Breadth-qualified when:
- pooled n >= 20
- >= 3 eligible crypto assets

Then:

**STRONG_REPEAT**
- pooled >= 65%
- support fraction >= 2/3

**REPEAT**
- pooled >= 58%
- support fraction >= 2/3

**CONTRADICTED**
- pooled <= 42%
- at least 2/3 favor the opposite direction

**MIXED**
- otherwise

Otherwise:
- **INSUFFICIENT_BREADTH**

## Final optimization statuses after all five batches

The combined stock result is primary.

- KEEP_STRONG: V5 stock STRONG_REPEAT
- KEEP: V5 stock REPEAT
- KEEP_ASSET_SPECIFIC: stock/crypto materially diverge but one class has broad support
- WATCH: MIXED or INSUFFICIENT_BREADTH without contradiction
- DEMOTE: CONTRADICTED

For the five V3 discoveries:
- PROMOTE_V5 only when stock result is STRONG_REPEAT or REPEAT
- Crypto is reported separately and is not required for stock promotion

For the three previous MIXED rules:
- they may be promoted only if V5 stock result is STRONG_REPEAT
- otherwise they remain MIXED/WATCH

## Exploratory search after prespecified evaluation

Only after all 16 logics are evaluated, scan the same event features for broad
new patterns:
- color
- state age
- origin
- subtype
- true light-gray interaction
- MID / BD / BS path

A new finding is reported only if:
- stocks pooled n >= 40
- >= 8 eligible stocks
- pooled primary probability >= 70%
- support fraction >= 75%

All such findings receive:
`NEW_V5_DISCOVERY_REQUIRES_FUTURE_VALIDATION`

If nothing meets these thresholds, record:
`NO_NEW_BROAD_DISCOVERY`

No threshold tuning after results are seen.

## Batch discipline

Each batch is:
1. fetched
2. calculated
3. written to the repository
4. reported complete
before starting the next batch.

After Batch 5:
- merge all five batches
- evaluate the 16 logics
- run exploratory scan
- produce final V5 result + summary + optimized rulebook

`SSSS_V5_20_NEW_STOCK_4_CRYPTO_PROTOCOL = FROZEN`
