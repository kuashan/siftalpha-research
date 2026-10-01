# SSSS Conditional Rail Rules v1 — Round 3 Stability / Falsification Freeze

Status: FROZEN_BEFORE_ROUND3_OUTCOME_ANALYSIS
Date: 2026-10-01

## Purpose
Round 3 does not invent new signal families. It stress-tests the candidate
conditions retained by Round 2 and rejects effects that are concentrated,
unstable, or incompatible with their intended action.

## Candidate set frozen from Round 2

Bullish:
B1 = LOWER_FAST with initial state DOWN.
B2 = LOWER_FAST with transition RANGE->UP within the frozen Round-2 path window.
B3 = gray-band FROM_BELOW + RANGE + FULL_CROSS.

Bearish / exit:
S1 = UPPER_FAST with transition UP->RANGE.
S2 = UPPER_FAST with transition RANGE->DOWN.

Context-only comparator:
C1 = LOWER_FAST initial UP -> RANGE deterioration.

No new rail threshold or state-transition definition may be introduced in this
round.

## Chronology
All source events remain those produced by strict first-observed point-in-time
XMA25/XMA60:
data <= t only -> recompute right-edge XMA -> store t -> advance.

Round 3 may not recompute events with finalized/repainted XMA.

## Tests

### 1. Cross-symbol concentration
For each candidate:
- event count per symbol
- mean and median 20-bar return per symbol
- number/share of symbols whose condition-aligned outcome has the expected sign
- top-1 / top-3 / top-5 contribution to aggregate signed return
- Herfindahl-like event concentration from symbol event shares

Promotion warning if a small set of symbols dominates aggregate effect.

### 2. Leave-one-symbol-out
For each candidate:
- recompute pooled mean after removing each symbol in turn
- record min / max leave-one-out mean
- record whether expected sign survives every omission

This tests whether one name creates the effect.

### 3. Temporal robustness
Retain frozen blocks:
A = 2020-2022
B = 2023-2024
C = 2025

Also compute calendar-year means where sample size permits.
No rule is promoted if one period reverses the effect materially without a
clear sample-size explanation.

### 4. Tail and failure behavior
For each candidate:
- p10 / p25 / p50 / p75 / p90 of 20-bar return
- worst / best event
- trimmed mean excluding top/bottom 1%
- failure rate:
  bullish candidate => ret20 <= 0
  bearish candidate => ret20 >= 0
- severe failure:
  bullish => ret20 <= -5%
  bearish => ret20 >= +5%

### 5. MFE / MAE
Use the already stored strict event ledgers where available.
Compare:
- mean / median MFE10 and MAE10
- mean / median MFE20 and MAE20
- adverse/favorable excursion asymmetry

No stop threshold is optimized in Round 3.

### 6. Volatility dependence
No new volatility indicator is invented.
Use event-bar ATR-normalized geometry only if already present in frozen
ledgers; otherwise volatility dependence is reported as NOT TESTED rather than
silently defining a new variable.

### 7. False-positive structure
For B1/B2/B3, inspect negative 20-bar outcomes.
For S1/S2, inspect positive 20-bar outcomes.
Report whether failures cluster by symbol, time block, or transition lag.

## Promotion classes
After Round 3 each candidate receives one research status:
- ROBUST_CANDIDATE
- CONDITIONAL_CANDIDATE
- OBSERVE_ONLY
- REJECT

This is still research classification, not a production trading instruction.

## Hard restrictions
- no position sizing
- no leverage
- no stop-loss optimization
- no new state or rail thresholds
- no renaming into BUY/SELL production labels yet
- no use of future-repainted XMA
