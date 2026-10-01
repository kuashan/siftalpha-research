# SSSS Rail + Color Path Study v1

Status: FROZEN_BEFORE_RUN / DISCOVERY_ONLY
Date: 2026-10-01

## Purpose

Decompose the original Source-XMA SSSS structure into:

1. fast lower rail ZD1
2. fast midpoint GZB18 = (ZK1+ZD1)/2
3. fast upper rail ZK1
4. outer lower rail BD
5. outer upper rail BS
6. fast three-state colored band (UP / DOWN / RANGE; EXPANSION stored separately)
7. light-gray slow band GZB3..GZB4

This study tests rail interactions by state. It does not define a production trading rule.

## Color / state authority

Use formula state ids as authority:
- GZB12 = UP_STATE (source-rendered dark red)
- GZB13 = DOWN_STATE (source-rendered dark green; visual theme may differ)
- GZB14 = RANGE_STATE (dark gray)
- EXPANSION_STRADDLE = no original state color

Do not group by perceived screen color alone.

## Formula version

Primary: canonical Source-XMA v1 for comparability with the prior geometry study.
Sensitivity: preserve raw-source formula differences separately where practical.

Point-in-time XMA is mandatory. No finalized/repainted historical XMA may be used as if it were known at the event date.

## Discovery universe/window

Reuse the prior geometry Discovery scope:
Equities: ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM
Crypto: BTC, ETH, BNB, SOL
Primary evaluation: 2025-01-01/02 through 2025-06-30.
Earlier bars are warm-up only.

## A. Fast-lower excursion

Episode onset: first bar with low < ZD1 after a non-excursion bar; repeated bars are one episode until low >= ZD1.

Subtypes:
- PIERCE_LOWER: low < ZD1 and high >= ZD1
- FULL_BELOW: high < ZD1

For each state measure forward 3/5/10/20 bars:
- close return
- MFE / MAE
- reaches moving GZB18 midpoint
- reaches moving ZK1 upper fast rail
- reaches moving BD outer lower rail
- makes a new low below the event low

Path bucket through 20 bars:
- REACH_UPPER
- REACH_MID_ONLY
- CONTINUE_DOWN (no midpoint; new low)
- UNRESOLVED

## B. Fast-upper excursion

Episode onset: first bar with high > ZK1 after a non-excursion bar.

Subtypes:
- PIERCE_UPPER: high > ZK1 and low <= ZK1
- FULL_ABOVE: low > ZK1

For each state measure:
- forward close return, MFE, MAE
- reaches moving GZB18 midpoint
- reaches moving ZD1 lower fast rail
- reaches moving BS outer upper rail
- makes a new high above event high

Midpoint support diagnostic:
If price first falls from above and touches GZB18 within 20 bars:
- SUPPORT_HOLD_3 = no close below GZB18 for the next 3 bars
- SUPPORT_REBOUND = reaches ZK1 before reaching ZD1
Report both probabilities by event-state.

## C. Outer-rail interaction

Lower outer support event:
- low <= BD
Upper outer resistance event:
- high >= BS
Use episode onset/deduplication.

Measure by state:
- 3/5/10/20-bar return, MFE, MAE
- return to fast lower/mid/upper rails
- continued break beyond the event extreme

## D. Light-gray slow-band interaction

GZB3 = gray-band upper edge
GZB4 = gray-band lower edge

Support-side event:
- price approaches from above; previous close > GZB3
- current low <= GZB3

Resistance-side event:
- price approaches from below; previous close < GZB4
- current high >= GZB4

Classify:
- edge touch only
- enters band
- crosses through full band
- closes back on origin side

Measure 3/5/10/20-bar returns and path outcomes by:
- fast-band state
- slow-band slope direction
- touch/penetration subtype

## Governance

This is Discovery, not OOS.
No buy/sell rule, position size, stop, or leverage is promoted from this run alone.
