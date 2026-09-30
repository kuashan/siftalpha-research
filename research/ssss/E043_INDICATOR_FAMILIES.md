# E043 Indicator Family Map

## Purpose

This file maps the user's four active TongdaXin-style formula groups together with the existing SSSS feature family.

## F1 — LMD2 / LMD3

Core information:
- strong-body impulse;
- 2-bar gap / imbalance geometry;
- relative volume;
- EMA60 direction;
- ADX regime;
- dynamic zone midpoint;
- mitigation state;
- invalidation buffer.

Potential unique value:
market structure + participation.

Known implementation cautions:
- dynamic BARSLAST / VALUEWHEN windows must be reproduced exactly;
- divide-by-zero guards are numerical only and must not change signal meaning;
- LMD2 and LMD3 are variants of the same family and must not count as two independent votes.

## F2 — support / resistance / cost / SAR family

Components:
- GuBi dynamic line;
- dealer-cost line;
- short swing support/resistance;
- long swing support/resistance;
- Fibonacci levels;
- SAR / MA30 regime;
- EMA10 direction band.

Potential unique value:
price location and structural risk.

Causal audit:
- BACKSET is retrospective and cannot be used directly in live decisions;
- REFDATE and ISLASTBAR are display-oriented;
- pivot-derived support/resistance is usable only after confirmation delay;
- plotted historical lines may differ from what was knowable in real time.

## F3 — DXBD

Core information:
- 8-bar position in local range;
- EMA3 short oscillator;
- RSI-like short exhaustion cross.

Potential unique value:
very short-term timing / exhaustion.

Likely overlap:
KDJ and other stochastic transforms.
Therefore F3 and F4 momentum outputs cannot automatically stack confidence.

## F4 — KDJ / accumulation-distribution / MACD resonance

Core information:
- N15 stochastic/KDJ structure;
- O05 low-side accumulation intensity;
- O09 high-side distribution intensity;
- MACD histogram slope;
- filtered crossover / resonance.

Potential unique value:
momentum plus supply/demand pressure.

Audit item:
O06 uses a denominator based on SMA(MIN(HIGH-O01,0),10,1), which can be non-positive.
E043 preserves this exact definition first and reports its empirical numerical behavior.
No silent formula correction.

## F5 — existing SSSS structural family

Core information:
- fast DEMA band;
- slow White Band;
- ATR;
- separation and dsep;
- persistent Effective State;
- state transitions;
- FastLower/FastMid/FastUpper location.

Potential unique value:
persistent directional structure and regime.

Important:
E043 treats this as one structural family, not as several independent votes.

## Combination principle

The strategy should eventually answer:
- F1: is there a structural impulse / zone?
- F2: where is price relative to causal support / resistance / cost?
- F3/F4: is short-term momentum confirming or exhausting?
- F5 SSSS: is the broader state structurally compatible?
- Risk engine: can the position be held safely at 10x instrument leverage?

No family is assumed superior before forward evidence.
