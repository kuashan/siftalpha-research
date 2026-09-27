# Source-XMA Signal Logic — Initial Research Draft

Status: DRAFT / NOT VALIDATED  
Date: 2026-09-27

## Design principle

The source indicators contain useful information, but their displayed icons are not accepted as the decision rule.

Our logic will use the original XMA structures and ask a different question:

> Given the current regime, where is price relative to the XMA structure, is momentum changing, and has the market confirmed or rejected the extreme move?

## Information hierarchy

### 1. Regime first

Use the relationship between the 25-XMA fast structure and the slow 90-period structure.

Research states:

- BULL: fast structure is structurally above / advancing through the slow structure.
- BEAR: fast structure is structurally below / declining through the slow structure.
- RANGE: fast structure is contained by the slow structure.
- EXPANSION: fast structure spans beyond both sides of the slow structure or otherwise falls outside the original three-state classification.

EXPANSION is not automatically long or short.

## 2. Location second

Define price as being in one of these zones:

- EXTREME_LOW
- LOWER_BAND
- MID_BAND
- UPPER_BAND
- EXTREME_HIGH

The exact coordinates come from the original XMA geometry, not from a replacement moving average.

## 3. Momentum third

Track the two source momentum components independently.

Research states:

- BOTH_UP
- FAST_UP_SLOW_FLAT_OR_UP
- CONFLICT
- FAST_DOWN_SLOW_FLAT_OR_DOWN
- BOTH_DOWN

Do not automatically treat "either one up" as bullish.

## 4. Candidate and confirmation are separate

An extreme price location creates a **watch state**, not an immediate entry.

Example long sequence:

```text
BULL or improving structural state
+ EXTREME_LOW / lower-band excursion
=> WATCH_LONG

then:
price stops extending lower
+ returns into / through a meaningful XMA boundary
+ momentum improves
=> ENTER_LONG
```

Example short sequence is the mirror image.

## 5. Trend-sensitive interpretation

The same extreme has different meaning in different regimes.

### In BULL
- lower extreme may become a long candidate;
- upper extreme is more naturally an exit/reduce candidate than an automatic short.

### In BEAR
- upper extreme may become a short candidate;
- lower extreme is more naturally an exit/reduce candidate than an automatic long.

### In RANGE
Both sides may support mean-reversion candidates, but confirmation is still required.

### In EXPANSION
Default to REGIME_UNCLEAR / NO_TRADE until the structure resolves. The purpose is to avoid forcing a three-state interpretation onto a geometry the source logic did not classify.

## 6. Initial action labels

### WATCH_LONG
Price has entered a lower extreme or lower structural boundary in a regime where a long could become valid, but confirmation is incomplete.

### ENTER_LONG
A prior WATCH_LONG exists and the next structural evidence shows recovery rather than continued deterioration.

Candidate confirmation ingredients:
- reclaim of a source-XMA boundary;
- no fresh lower extension;
- DEA3_RAW turns up;
- DEA33B_RAW is no longer deteriorating or also turns up;
- regime remains acceptable or improves.

No single ingredient is yet frozen as mandatory.

### EXIT_LONG
Candidate ingredients:
- upper extreme followed by loss of momentum;
- failed upper-band continuation;
- deterioration of regime;
- rejection back inside the XMA structure after an extended move.

### WATCH_SHORT / ENTER_SHORT / EXIT_SHORT
Mirror the long logic.

## 7. Signal reset

Do not print repeated independent entries while the same unresolved setup remains active.

A setup must reset before a new entry can be generated.

Possible reset events:
- return to MID_BAND;
- confirmed opposite-side transition;
- explicit exit;
- regime invalidation.

The exact reset rule will be learned from the ABT walk-forward replay and then frozen before later validation.

## 8. What this draft does NOT claim

- It is not a final trading system.
- It is not a backtest result.
- It does not claim XMA is causal.
- It does not replace the current DEMA-based SSSS model.
- It does not claim ABT is untouched evidence.

Its purpose is to give the walk-forward study a decision language that is independent of the original author's icons.
