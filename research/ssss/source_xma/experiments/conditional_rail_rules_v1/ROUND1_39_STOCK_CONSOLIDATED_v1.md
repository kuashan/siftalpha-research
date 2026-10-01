# SSSS Conditional Rail Rules v1 — Round 1 39-Stock Consolidated

Status: ROUND1_COMPLETE / DISCOVERY_ROBUSTNESS
Date: 2026-10-01

## Scope

- 39 frozen US equities
- Daily bars
- Warm-up from 2019
- Evaluation: 2020-01-01 through 2025-12-31
- Strict first-observed point-in-time Source-XMA25 / XMA60
- 39/39 symbols completed
- Total classified rail/gray-band events across event families: 14,147

The 2020 onset boundary was explicitly corrected so the first evaluation bar
inherits the excursion state of the final warm-up bar.

## Important aggregation note

Batch means are consolidated by event-count weighting. Because events in the
final 20 bars of 2025 do not all have a complete +20-bar outcome, consolidated
20-bar means are approximate at the small boundary level. Promotion decisions
below rely primarily on direction consistency across six independent symbol
batches and the three frozen time blocks, not on small decimal differences.

Time blocks:
- A: 2020-2022
- B: 2023-2024
- C: 2025

## Round 1 findings

### 1. Fast lower rail

#### DOWN state
- n = 629
- approx +20-bar return: +2.97%
- approx positive +20 rate: 61.6%
- positive in 6/6 symbol batches
- Block A: +2.51%
- Block B: +3.33%
- Block C: +3.75%

Decision:
**PROMOTE TO ROUND 2.**
This is the strongest and most temporally stable unconditional lower-rail
candidate. Test midpoint reclaim, state transition, lower-outer confluence,
time-to-recovery and failure/invalidation.

#### UP state
- n = 1,343
- approx +20: +1.30%
- approx positive rate: 57.6%
- positive in 5/6 batches
- Block A +0.32%
- Block B +2.23%
- Block C +2.39%

Decision:
**KEEP, BUT DO NOT LABEL BAD BUY.**
ABT five-year evidence was negative for this condition, but the 39-stock
universe is modestly positive. The ABT conclusion does not generalize.
Round 2 must identify which UP-lower subpaths fail versus recover.

#### RANGE state
- n = 607
- approx +20: +1.09%
- positive in 4/6 batches
- Block A +0.45%
- Block B +0.99%
- Block C +3.48%

Decision:
**KEEP AS SECONDARY.**
Not stable enough to call a standalone buy. Test midpoint reclaim and gray-band
context.

### 2. Fast upper rail

The unconditional “upper rail = sell” hypothesis is **not supported** by the
39-stock six-year event map.

#### UP state
- n = 1,654
- approx +20: +1.23%
- positive in 5/6 batches
- A +0.72%, B +1.89%, C +1.25%

#### DOWN state
- n = 742
- approx +20: +2.13%
- positive in 6/6 batches
- A +1.48%, B +3.07%, C +2.83%

#### RANGE state
- n = 638
- approx +20: +1.03%
- positive in 5/6 batches
- A +0.98%, B +1.13%, C +0.92%

Decision:
**REJECT UPPER-TOUCH AS STANDALONE SELL.**
Promote only the conditional path question:
- upper touch -> midpoint loss?
- midpoint loss -> lower rail before rebound?
- UP -> RANGE / DOWN transition?
- upper-fast + upper-outer confluence?
A sell/reduce signal, if it exists, must come from the subsequent path/state
change, not the upper touch alone.

### 3. Lower outer rail BD

#### DOWN state
- n = 479
- approx +20: +3.16%
- approx positive rate: 61.4%
- positive in 6/6 batches
- A +3.08%, B +2.55%, C +4.40%

Decision:
**PROMOTE TO ROUND 2 AS STRONG LOWER-SIDE CONDITION.**
Test whether it improves DOWN + fast-lower entry, and whether immediate outer
touch versus fast-lower->outer sequence changes risk/reward.

#### UP state
- n = 282
- approx +20: -0.12%
- only 4/6 batches positive
- A -2.22%, B +4.38%, C -2.64%

Decision:
**UNSTABLE.**
Do not use lower outer as universal support.

#### RANGE state
- n = 263
- approx +20: +1.81%
- positive in 5/6 batches
- all three aggregate blocks positive

Decision:
**KEEP AS SECONDARY.**

### 4. Upper outer rail BS

No state provides evidence that BS should be a universal resistance/sell line.

UP:
- n = 1,146
- approx +20: +1.15%

DOWN:
- n = 197
- approx +20: +1.88%

RANGE:
- n = 377
- approx +20: +0.32%

Decision:
**REJECT BS TOUCH AS STANDALONE SELL.**
Only retain it as a possible confluence/exhaustion feature in Round 2.

### 5. Light-gray slow band: approach from above

#### RANGE state
- n = 1,220
- approx +20: +0.91%
- positive in 6/6 symbol batches
- A +0.90%
- B +0.74%
- C +1.30%

Decision:
**PROMOTE TO ROUND 2.**
This is the most stable gray-band support-like condition in Round 1, though
the effect is modest. Split by touch/enter/full-cross, gray-band slope, distance
to midpoint, and next state transition.

#### DOWN state
- n = 249
- approx +20: +1.19%
- only 4/6 batches positive
- C 2025 is negative

Decision:
**KEEP, NOT STABLE ENOUGH YET.**

#### UP state
- n = 1,629
- approx +20: +0.91%
- 4/6 batches positive
- mixed across batches

Decision:
**KEEP AS STRUCTURAL CONTEXT, NOT SUPPORT RULE.**

### 6. Light-gray slow band: approach from below

The simple “from below = resistance” hypothesis is not supported.

UP:
- n = 436
- approx +20: +0.71%
- only 2/6 batches positive
- A and C negative; B positive -> unstable

DOWN:
- n = 1,025
- approx +20: +1.45%
- 5/6 batches positive

RANGE:
- n = 1,196
- approx +20: +0.93%
- 5/6 batches positive

Decision:
**REJECT UNIVERSAL RESISTANCE INTERPRETATION.**
Gray band is a slow structural/regime zone. Round 2 must condition on band
slope, penetration depth, fast-state transition and midpoint relation.

## Round 1 candidate map

Promote:
1. DOWN + fast lower excursion
2. DOWN + lower outer
3. RANGE + gray-band approach from above
4. upper event -> subsequent midpoint loss / state deterioration (path study)

Keep secondary:
5. UP + lower fast
6. RANGE + lower fast
7. RANGE + lower outer
8. gray-band events in other states as structural context

Reject as standalone rules:
9. any-color upper fast = sell
10. upper outer = sell
11. light-gray band from below = universal resistance
12. lower outer = universal support across all colors

## Next round

Round 2 will test conditional sequences rather than isolated touches:

A. DOWN lower:
fast-lower -> midpoint reclaim -> upper / failure
fast-lower -> lower-outer -> midpoint reclaim / failure

B. UP/RANGE lower:
identify which subpaths separate winners from failures.

C. Upper-side:
upper touch -> midpoint hold/loss -> lower/rebound
plus state transitions UP->RANGE/DOWN and RANGE->DOWN.

D. Gray band:
approach direction + touch depth + band slope + fast state + next state
transition + relation to midpoint.

No production action or position size is frozen at Round 1.
