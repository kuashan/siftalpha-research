# SSSS Current State

Last updated: 2026-09-19  
Research version: v0.1.0

## Scope

This document is the current source of truth for the SSSS research model.

The strategy is event-driven. Fixed 5/10/20-day holding periods are used only for research diagnostics and are not live exits.

## Current causal implementation

Source XMA is replaced by DEMA for causal execution.

Fast band:
- DEMA(H,25)
- DEMA(L,25)
- FastUpper = 2*DH - DL
- FastLower = 2*DL - DH
- FastMid = (DH+DL)/2

Slow white band:
- Source weighted HIGH/LOW structures
- EMA(90)
- Preserve source anomalies:
  - lag 19 omitted; lag 20 receives weight 1
  - lower structure uses HIGH at lag 11

Effective color/state requires 3 consecutive raw-state bars.

## OPEN / validated

Qualified GRB:

```
EffectiveState = GREEN
AND H > FastUpper
AND REF(H,1) <= REF(FastUpper,1)
AND dsep > 0
AND C >= WhiteLower - 2*ATR14
```

Signal is known after close and executed at the next tradable open.

## CLOSE / validated research rules

Failure path:

```
Qualified BUY
-> no RED maturity
-> Effective Gray -> Effective Green
-> CLOSE next open
```

Mature path:

```
Qualified BUY
-> Effective RED
-> HOLD
-> Effective Red -> Effective Gray
-> CLOSE next open
```

## Position-management status

- OPEN: validated research rule
- ADD: research; no validated trigger yet
- REDUCE: RTE is the leading candidate, not yet production/frozen
- RE-ADD: research; no validated trigger yet
- FAILURE CLOSE: validated research rule
- MATURE CLOSE: validated research rule

## RTE candidate

```
EffectiveState = RED
AND H > FastUpper
AND C >= O
AND FastWidth > REF(FastWidth,5)
AND dsep < 0
```

Current interpretation: tactical risk / REDUCE candidate, not full CLOSE.

## Corrected baseline

Universe: 45 mainstream liquid equities.  
Available history: approximately 2024-09 to 2026-09.

- Independent Qualified BUY lifecycles: 96
- Resolved lifecycles: 88
- Mature: 69
- Fail: 19
- Completed BUY->SELL trades: 71
- Win rate: 59.2%
- Average net return per completed trade: +8.84%
- Median net return: +1.96%
- Mature-path win rate: 76.9%
- Mature-path average net return: +13.98%
- Failure-path win rate: 10.5%
- Failure-path average net return: -5.25%
- Average winner: +18.91%
- Average loser: -5.75%
- Payoff ratio: ~3.29
- Profit factor: ~4.76

These figures are research results from the currently available ~2-year window, not a claim of long-run live performance.

## Important risk finding

The return distribution is positively skewed and relies materially on large trends.

- Top 5 winners contributed about 58.1% of gross positive returns.
- Top 10 winners contributed about 74.7%.
- Tail losses worse than -10% occurred and remain a major research target.

## Current next objective

Build a complete position state machine:

```
FLAT
 -> OPEN
 -> HOLD
 -> ADD / REDUCE / RE-ADD
 -> CLOSE
 -> FLAT
```

Do not optimize position percentages until action triggers themselves have passed out-of-sample validation.
