# XMA Geometry + Three-Color Band State Model

Status: RESEARCH DESIGN / SOURCE-DERIVED
Added: 2026-09-28

## Why this matters

The Source-XMA system must not be reduced to only lower rail / midpoint / upper rail.
The three-color fast band is itself a structural state variable.

Research model:

PRICE/CANDLE GEOMETRY × RAIL GEOMETRY × THREE-COLOR BAND STATE × STATE TRANSITION

External factors such as volume, VIX, breadth and Volume Profile are confirmation/context layers only after the pure-XMA geometry/state event is defined.

## Source logic for the three-color band

Fast XMA channel:
- upper = GZB10 / ZK1
- lower = GZB11 / ZD1

Slow outer structure:
- upper = GZB8
- lower = GZB9

Source states:

GZB12 = GZB11 >= GZB9 AND GZB10 >= GZB8
GZB13 = GZB10 <= GZB8 AND GZB11 <= GZB9
GZB14 = GZB11 >= GZB9 AND GZB10 <= GZB8

Geometric interpretation:
- GZB12 = fast channel shifted upward relative to slow structure
- GZB13 = fast channel shifted downward relative to slow structure
- GZB14 = fast channel contained inside slow structure / compression-range state

Important: visual color names should be taken from the actual Futu rendering/version rather than inferred solely from source COLOR hex/name. Store the underlying GZB12/GZB13/GZB14 state id in addition to rendered color.

## Implicit fourth topology

GZB11 < GZB9 AND GZB10 > GZB8

The fast channel straddles / expands outside both slow boundaries.
Research label: EXPANSION_STRADDLE.

## Band transitions are first-class information

Record static state and transitions:
- DOWN_STATE -> RANGE_STATE
- RANGE_STATE -> UP_STATE
- UP_STATE -> RANGE_STATE
- RANGE_STATE -> DOWN_STATE
- DOWN_STATE -> UP_STATE
- UP_STATE -> DOWN_STATE

Also record:
- duration in current state
- transition speed
- whether transition occurs before or after a rail/candle event

## Joint geometry hypotheses

### Lower confluence event

Candidate: price/candle interacts with the outer lower rail and lower white fast rail near their convergence.

The same geometry can mean different things depending on band state:
- UP_STATE: candidate trend-pullback / continuation buy
- RANGE_STATE: candidate range-reversal buy
- DOWN_STATE: candidate falling-knife / weak counter-trend setup
- EXPANSION_STRADDLE: separate high-volatility case

Therefore lower confluence is not one universal buy signal.

### Upper confluence / exceed event

Candidate: price/candle interacts with or exceeds the outer upper rail and upper white fast rail near their convergence.

- UP_STATE: may be rail-ride continuation, not a top
- UP_STATE -> RANGE_STATE: stronger exhaustion candidate
- RANGE_STATE: range-extreme / rejection candidate
- DOWN_STATE: rebound exhaustion candidate

Therefore upper confluence is not one universal sell/top signal.

## Primary research event schema

For every bar, record:

Band state:
- GZB12 / UP_STATE
- GZB13 / DOWN_STATE
- GZB14 / RANGE_STATE
- EXPANSION_STRADDLE
- days_in_state
- previous_state
- transition_type

Price vs fast white rails:
- low vs ZD1
- high vs ZK1
- close vs ZD1
- close vs ZK1
- full candle below/inside/above fast channel
- reclaim / rejection

Price vs outer rails:
- distance to outer lower rail
- distance to outer upper rail
- touch / pierce / close-through / reclaim

Rail-to-rail geometry:
- outer lower vs fast lower distance
- outer upper vs fast upper distance
- convergence/divergence rate
- fast-channel width
- slow-structure width

## Research order

1. Pure XMA geometry + color state only
2. Measure forward 1/3/5/10-bar behavior
3. Separate continuation vs reversal vs failure
4. Only then test Volume Structure / Volume Profile / Breadth / VIX

No external factor may define the original XMA event.