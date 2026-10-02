# SSSS V4 — Untouched Validation for Five New Candidate Conditions

Status: **FROZEN BEFORE OUTCOME RUN**
Date: 2026-10-02

## 1. Governance

The already validated v3 candidate conditions remain preserved as:

`VALIDATED_CORE_V3`

They are not downgraded, re-tuned, or redefined in this round.

V4 formally validates only these five newly discovered conditions:

1. **NEW-BUY-1**
   - BLUE
   - state age 11-20
   - new LOWER event
   - WICK_ONLY
   - expected path: MID before BD

2. **NEW-AVOID-BUY-1**
   - GREEN
   - state age 11-20
   - new LOWER event
   - CLOSE_BELOW
   - expected path: BD before MID

3. **NEW-HOLD-1**
   - BLUE
   - state age 11-20
   - new UPPER event
   - CLOSE_ABOVE
   - expected path: BS before MID

4. **NEW-HOLD-2**
   - BLUE
   - state age 21+
   - new UPPER event
   - FULL_ABOVE
   - expected path: BS before MID

5. **NEW-SELL-1**
   - GREEN
   - state age 4-10
   - new UPPER event
   - any subtype
   - expected path: MID before BS

No origin-state condition is added because the five candidate definitions above
were discovered and reported without an origin-state restriction.

## 2. Frozen event definitions

LOWER event:
- current Low < current FIRST_OBSERVED ZD1
- previous bar was not already below prior FIRST_OBSERVED ZD1

LOWER subtype:
- WICK_ONLY: Low < ZD1 and Close >= ZD1
- CLOSE_BELOW: Close < ZD1 and High >= ZD1
- FULL_BELOW: High < ZD1

UPPER event:
- current High > current FIRST_OBSERVED ZK1
- previous bar was not already above prior FIRST_OBSERVED ZK1

UPPER subtype:
- WICK_ONLY: High > ZK1 and Close <= ZK1
- CLOSE_ABOVE: Close > ZK1 and Low <= ZK1
- FULL_ABOVE: Low > ZK1

Primary path horizon:
- 20 bars

Primary races:
- LOWER: MID vs BD
- UPPER: MID vs BS

## 3. Immutable SSSS reconstruction

FIRST_OBSERVED only.

At historical bar t:
- use only data <= t
- recompute right-edge XMA
- preserve original XMA formula
- never use finalized future-repainted historical rails

XMA formulas remain:
- XMA(XMA(L,25),25)
- XMA(XMA(H,25),25)
- XMA(XMA(L,60),60)
- XMA(XMA(H,60),60)

True light-gray band remains GZB4..GZB3, but it is not added as an extra filter
to these five V4 candidate definitions.

## 4. Untouched validation track A — cross-symbol OOS

The v3 study used the first 30 names of the frozen ordered 39-stock universe.
The remaining untouched nine stocks are:

- MA
- CAT
- BA
- GE
- XOM
- CVX
- LIN
- NEE
- PLD

Window:
- 2018-01-02 through 2025-12-31 where data exist
- earlier returned history is warm-up only

This track has never been used to discover the five V4 conditions.

### A status thresholds

For each candidate:
- eligible symbol: >= 2 candidate events
- breadth-qualified: pooled n >= 20 AND >= 5 eligible symbols

If breadth-qualified:
- **SUPPORTS_V3_DISCOVERY**:
  pooled primary probability >= 60% AND >= 70% of eligible symbols have primary
  probability > 50%
- **CONTRADICTS_V3_DISCOVERY**:
  pooled primary probability <= 40% AND >= 70% of eligible symbols favor the
  opposite direction
- **MIXED**: otherwise

If not breadth-qualified:
- **INSUFFICIENT_BREADTH**

## 5. Untouched validation track B — forward-time OOS

Use data after the v3 historical endpoint:

- main outcome period begins 2026-01-01
- ends at latest provider bar available on or before 2026-10-02
- only events with a complete 20-bar future window are eligible

Universe:
- all 39 frozen stocks
- BTC/USD
- ETH/USD
- BNB/USD
- SOL/USD

Historical data before 2026 are used only to reconstruct state, age, and rails
correctly at the start of the forward period.

### B-stock status thresholds

- eligible symbol: >= 2 candidate events
- breadth-qualified: pooled n >= 30 AND >= 10 eligible stocks

If breadth-qualified:
- SUPPORTS_V3_DISCOVERY:
  pooled >= 60% AND >= 65% eligible stocks > 50%
- CONTRADICTS_V3_DISCOVERY:
  pooled <= 40% AND >= 65% eligible stocks favor opposite
- MIXED otherwise

If not:
- INSUFFICIENT_BREADTH

### B-crypto status thresholds

- eligible crypto: >= 2 candidate events
- breadth-qualified: pooled n >= 12 AND >= 3 eligible crypto assets

If breadth-qualified:
- SUPPORTS_V3_DISCOVERY:
  pooled >= 60% AND >= 2/3 eligible crypto assets > 50%
- CONTRADICTS_V3_DISCOVERY:
  pooled <= 40% AND >= 2/3 favor opposite
- MIXED otherwise

If not:
- INSUFFICIENT_BREADTH

## 6. Final promotion rule

A newly discovered candidate may be promoted to `VALIDATED_V4` only if:

- Track A supports it, AND
- Track B stocks supports it.

Crypto is a separate transfer check and is not required for stock-rule promotion.

If one stock track supports and the other is MIXED:
- status = PARTIAL_SUPPORT

If either stock track contradicts:
- status = FAILED_VALIDATION

If either stock track lacks breadth:
- status = PENDING_MORE_OOS_DATA unless the other track contradicts.

## 7. Existing validated candidates

The v3 validated core stays intact during V4. V4 does not re-open those decisions.

`SSSS_V4_FIVE_CANDIDATE_OOS_PROTOCOL = FROZEN`
