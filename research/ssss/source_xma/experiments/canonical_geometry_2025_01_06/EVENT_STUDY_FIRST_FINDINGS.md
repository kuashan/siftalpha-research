# Canonical Geometry Study — First Findings

Status: PHASE 1 DISCOVERY  
Formula baseline: SSSS_CANONICAL_v1 / ADKBY-E_CANONICAL_v1  
Window: Jan–Jun 2025  
Universe: 11 US equities + BTC/ETH/BNB/SOL

## Critical implementation correction

XMA25 and XMA60 are calculated point-in-time from the first evaluation bar forward.

For XMA60, the public XMA implementation uses the even-period geometry implied by:
- p = floor((N-2)/2)
- for N=60: offsets -30 .. +29, truncated at the current right edge.

Previous exploratory code that treated XMA60 like a symmetric ±12 window is not reused here.

## Finding A — upper outer/fast confluence is materially different from generic rail riding

Define a strict upper confluence episode as:
- state = UP
- candle overlaps both ZK1 and BS
- abs(ZK1-BS) <= 0.25 ATR14
- repeated bars within 3 bars are deduplicated to the first episode event

Result:

```text
Raw bars:
5-day mean: -4.57%
5-day median: -4.61%
positive rate: 17.6%
n = 17

Episode-deduplicated:
5-day mean: -4.32%
5-day median: -5.16%
positive rate: 30.0%
n = 10
```

This is strongly different from an UP-state fast-rail ride where the outer rail is still >0.5 ATR away.

Far rail-ride:
- 5-day mean: 0.40%
- 5-day median: 0.50%
- positive rate: 54.7%
- n = 53

Interpretation:
**the user's "upper rail convergence / exceed" observation is not the same event as ordinary strong-trend rail riding.**
This is the first strong evidence that the distance between the outer rail and fast white rail matters.

Do not yet promote to an automatic sell rule:
- sample is still discovery;
- repeated episodes and asset concentration must be monitored;
- exact visual color-to-formula mapping is still unresolved.

## Finding B — lower confluence is NOT a standalone buy

DOWN-state lower overlap within 0.5 ATR:

Episode-deduplicated:
- 5-day mean: -0.07%
- median: 0.04%
- positive rate: 50.0%
- n = 28

This is not strong enough to call a universal buy.

The raw examples contain both:
- successful reversal precursors (BTC/ETH/SOL/JPM examples)
- continued decline / large MAE examples.

Interpretation:
**lower confluence is better treated as WATCH / REVERSAL CANDIDATE, not immediate full entry.**

## Finding C — color/state transition should be the confirmation layer

Among deduplicated DOWN-state lower-confluence episodes, a subset leaves DOWN state within the next 5 bars.

This creates a tradable two-step structure:

```text
STEP 1:
lower confluence in DOWN
=> WATCH / optional very small probe

STEP 2:
subsequent state improvement out of DOWN
=> candidate confirmation event
```

Observed cases with state improvement within 5 bars:
- count = 0
- average lag = NA bars

This sample is still small, so classification remains OBSERVE.

## Finding D — upper confluence + later color deterioration deserves priority

For deduplicated UP-state strict upper-confluence episodes, record whether the band leaves UP within 5 bars.

Cases that deteriorate:
- count = 2

Cases remaining UP:
- count = 8

This is now a priority lifecycle hypothesis:
```text
UP + upper confluence
=> EXTENDED / WARNING

then:
UP -> RANGE/DOWN
=> REDUCE / EXIT candidate
```

rather than:
```text
upper confluence => instant short
```

## Finding E — no EXPANSION_STRADDLE observed in this window

The exclusive corrected state machine produced no EXPANSION_STRADDLE bars in the Jan–Jun 2025 sample.

This does not mean the fourth topology is impossible.

It means:
- it is geometrically valid,
- but was not observed in this discovery window.

Status: OBSERVE.

## Current hypothesis classification

- H1 Lower confluence is a universal buy: **DROP**
- H2 Lower confluence + state improvement is a better reversal structure: **OBSERVE**
- H3 Upper confluence is not universally bearish: **KEEP**
- H4 Upper confluence + subsequent UP deterioration is an exhaustion candidate: **OBSERVE / PRIORITY**
- H5 Far outer-gap rail ride can be continuation: **KEEP**
- H6 RANGE compression may precede expansion: **OBSERVE**

## Next Phase-1 work

Before adding HYS2 or external factors:
1. map exact visual rails in the user's current Futu rendering;
2. separate upper confluence episodes by stock vs crypto;
3. study body/wick reclaim/rejection at the confluence;
4. build the two-step lower reversal event:
   confluence precursor -> state improvement -> midpoint reclaim;
5. build the upper lifecycle:
   confluence -> state deterioration -> midpoint loss.

Only after those pure-XMA sequences are defined should HYS2 be tested as confirmation.
