# FIVEGZ5SE 39-Stock Signal Sequence and Position-Management Study v1

Status: **IMPLEMENTED_AND_VERIFIED**

Date: 2026-09-30

Starting HEAD:
`b0b3d5b269b0f11288c2b278bbe4f0e04cbc98a8`

## Scope

Universe: 39 U.S. stocks previously used as the broad FIVEGZ5SE universe.

Study window:
- source data begins 2020-01-02;
- first ~63 sessions per symbol are warm-up only;
- effective signal study begins around 2020-04-02;
- end date 2025-12-31.

Sample:
- symbols: **39**
- completed baseline positions: **1233**
- subsequent BUY onsets while already holding: **1588**
- first SELL events: **1233**

Important governance:
This entire 39-symbol set is now **development/diagnostic data for signal-sequence and position-management design**.
It must not later be described as untouched OOS for a rule created from this study.

No formula-native OPEN/CLEAR/REDUCE/RISK labels are used.

## 1. BUY repeat vs cross-family confirmation

Same-family repeat BUY:
- n=826
- 10d mean=0.80%
- 10d median=0.63%
- 10d positive=54.48%

Cross-family BUY:
- n=762
- 10d mean=0.85%
- 10d median=0.65%
- 10d positive=54.86%

Generic cross-family confirmation is **not materially stronger** than repeat confirmation at 10 days.

More importantly, position outcomes deteriorate as more distinct BUY families appear before exit:

- 1 distinct BUY family: n=627, mean trade=2.00%, median=2.15%, win=66.67%
- 2 distinct BUY family: n=418, mean trade=1.50%, median=1.88%, win=63.64%
- 3 distinct BUY family: n=188, mean trade=1.02%, median=1.37%, win=60.11%

Positions with same-family repeat:
- n=469
- mean=-0.95%
- median=0.17%
- win=50.75%

Positions with no repeat:
- n=764
- mean=3.29%
- median=2.76%
- win=73.17%

Interpretation:
Repeated BUY signals are often a marker of a position that is taking longer to resolve, not a universal reason to add.

## 2. BUY order matters

First cross-family transition:

- A->B: n=117, mean=1.33%, median=1.92%, win=66.67%
- A->C: n=147, mean=2.74%, median=3.18%, win=68.03%
- B->A: n=124, mean=-1.13%, median=-1.68%, win=45.97%
- B->C: n=69, mean=3.29%, median=2.87%, win=75.36%
- C->A: n=68, mean=0.02%, median=0.09%, win=51.47%
- C->B: n=39, mean=0.85%, median=0.93%, win=66.67%

Key asymmetry:
- A -> C and B -> C are positive;
- B -> A is negative;
- C -> A is approximately flat.

Therefore:
`ANY_SECOND_BUY = ADD` is rejected.

C-related confirmation is interesting, but is not admitted as a sizing rule from this development sample alone.

## 3. Matched sizing controls

The key matched control is 50% initial allocation with no later add versus 50% initial allocation plus cross-family add.

Cross-confirmation add vs static 50%:
- mean return delta: **20.97 pp**
- median delta: **14.78 pp**
- 95% bootstrap mean CI: [11.16, 32.34] pp
- improved symbols: 28/39

Thus cross-family confirmation contains real incremental information relative to simply staying half-sized.

However, compared with entering full size immediately, a selective C-anchored staged entry is materially worse:
- mean delta: **-31.72 pp**
- median delta: **-10.67 pp**
- improved symbols: 13/39
- it reduces drawdown mainly because average invested weight is much lower.

Decision on BUY sizing:

`BUY_POSITION_POLICY = FULL_ON_FIRST_VALID_BUY`

`SAME_FAMILY_REPEAT_ADD = REJECTED_NOT_ADMITTED`

`GENERIC_CROSS_FAMILY_ADD = REJECTED_NOT_ADMITTED`

Cross-family sequence remains diagnostic metadata, not a pyramiding rule.

## 4. SELL timing evidence

All first SELL events:
- n=1233
- next 5d mean=0.26%
- next 10d mean=0.69%

If a different SELL family appears within 3 sessions:
- n=337
- delay to second distinct SELL mean=-0.38%
- median=-0.55%

A negative delay return means waiting produced a worse exit price.
Fast multi-family confirmation therefore argues for early exit, not waiting.

First-family behavior:

- SELL-A: 10d mean after first signal=0.99%; delay to later distinct SELL mean=3.76%
- SELL-B: 10d mean=1.20%; delay to later distinct SELL mean=2.98%
- SELL-C: 10d mean=0.42%; delay to later distinct SELL mean=0.17%
- same-day multi-SELL: 5d mean=-0.41%; 10d mean=0.06%

A/B are frequently early warnings.
C and same-day confluence are materially less suitable for delayed exit.

## 5. SELL policy backtests across 39 symbols

Baseline:
`FULL EXIT ON FIRST SELL`

Selective candidate:
- first SELL is single A or single B -> sell 50%;
- first SELL contains C or multiple SELL families -> sell 100%;
- after A/B half-exit, remaining half exits only on the next **different** SELL family;
- no arbitrary time cap.

Selective A/B-half + next-distinct versus baseline:
- mean return delta: **3.45 pp**
- median delta: **4.22 pp**
- bootstrap mean CI: [-6.31, 12.29] pp
- bootstrap median CI: [0.63, 9.68] pp
- return improved: 26/39 symbols
- MDD improved: 28/39 symbols
- mean MDD delta: 2.77 pp

The more conservative variant that exits the remaining half on the next **any** SELL:
- mean return delta: 1.58 pp
- median delta: 1.49 pp
- improved: 22/39
- MDD improved: 25/39

The next-distinct version is stronger, but it can leave a residual half-position for a long time when no different SELL appears.

Full waiting until a second distinct SELL has high historical return but is rejected as an operating rule because it materially raises invested time, worsens drawdown on many symbols, and leaves many positions open at sample end.

## 6. Research decision

### BUY

Keep the current one-shot full entry.

Do **not** add on:
- repeated same-family BUY;
- generic second different BUY;
- generic third BUY.

Reason:
confirmation has information, but the full-size first entry still wins on absolute portfolio return across the broad sample.

### SELL

The data does **not** support treating A/B/C as identical exits.

Best next candidate:

```
if first SELL is C or same-day multi-family:
    exit 100%

if first SELL is single A or single B:
    exit 50%
    hold remaining 50%
    exit remaining 50% on next different SELL family
```

No time-based forced exit.

This is **promoted to the next candidate-validation stage**, not frozen into the strategy yet.

Formal states:

`BUY_REPEAT_PYRAMIDING = REJECTED_NOT_ADMITTED`

`BUY_GENERIC_CROSS_PYRAMIDING = REJECTED_NOT_ADMITTED`

`BUY_FIRST_VALID_SIGNAL_FULL_SIZE = RETAINED`

`SELL_ALL_FIRST_SIGNAL = CHALLENGED_BY_DATA`

`SELL_SELECTIVE_A_B_HALF_C_FULL = PROMOTED_TO_NEXT_VALIDATION`

`SELL_WAIT_FOR_SECOND_DISTINCT_FULL_POSITION = REJECTED_NOT_ADMITTED`

## 7. Next validation boundary

Because all 39 stocks are now development/diagnostic data for this position-management design, any formal admission of the selective exit rule requires a different untouched validation set or a later untouched time period.

Closure:

`FIVEGZ5SE_SIGNAL_SEQUENCE_39_STOCK_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`
