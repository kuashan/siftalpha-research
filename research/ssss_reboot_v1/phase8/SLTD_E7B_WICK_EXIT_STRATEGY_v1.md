# SLTD E7B Wick Exit Strategy v1

Status: **USER_CONFIRMED / FROZEN FOR TEST**

Date: 2026-10-02

## 1. Governance

E7B is an independent strategy line derived from the frozen V7 12-rule candidate.

Frozen V7 remains immutable:
- branch: `candidate/sltd-v7-12rules-position-v1`
- commit: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`

E7B research branch:
- `research/sltd-e7-wick-exit-v1`

Changes to E7B must not modify V7.

## 2. Entry-side behavior

E7B preserves V7 candidate entry-side behavior so this study isolates the exit change:
- V7 candidate 12-rule signal taxonomy is reused.
- Candidate B deletions remain: B3 / S1 / S3 are not active.
- V7 conflict resolution remains `NO_CHANGE_MIXED`.
- first executed BUY from flat -> 25% target exposure.
- later executed BUY -> +25 percentage points, capped at 100%.
- HOLD and WAIT do not reduce a long position.
- original V7 ordinary SELL signals are not executed in E7B.
- original V7 C2 is not used.

Once E7B enters its dedicated exit stage, BUY / HOLD / WAIT / original SELL are ignored until the position is fully flat.

## 3. E7B first exit trigger

While holding a position and not already in the E7B exit stage:

A first upper-inner-rail crossing occurs when:

`current High > current ZK1`

AND

`previous High <= previous ZK1`.

Color is unrestricted.

Action:
- confirm on the completed signal bar;
- next selected-timeframe bar open, sell **50% of the current holding**;
- this is percentage of current holding, not 50 percentage points;
- after execution, enter E7B dedicated exit stage.

Example:
- 100% -> 50%
- 75% -> 37.5%
- 50% -> 25%
- 25% -> 12.5%

The signal bar itself cannot also trigger a final E7B exit. Final-exit conditions begin from subsequent bars.

## 4. E7B final exit stage

After the initial 50%-of-current-holding sale has executed, no further partial selling occurs.

The remaining position is fully liquidated at the next selected-timeframe open if any later completed bar satisfies one of these conditions:

### A. Upper outer rail
`High >= BS`

=> full exit.

### B. Shallow gray band above ZK1
The gray band is eligible only when:

`GZB4 > ZK1`

meaning the lower edge of the shallow gray band is already above the inner upper rail.

Touch is defined by K-line range intersection with the band:

`High >= GZB4 AND Low <= GZB3`

=> full exit.

### C. Failed breakout / lower-wick return
`Low < ZK1`

=> full exit.

This uses the user-confirmed A definition: any low below ZK1 is enough; the candle body does not have to remain above ZK1.

If multiple final-exit conditions occur on the same completed bar, execute only one full exit.

## 5. E7B adapted C2

Before the first E7B ZK1 breakout has occurred, E7B uses an adapted C2 defensive exit:

While long and not in E7B exit stage:

`color == GREEN AND High < GZB4`

=> next selected-timeframe open fully liquidate to 0%.

Priority on a bar where both the first E7B ZK1 crossing and adapted C2 are true:
- E7B ZK1 crossing has priority;
- schedule the 50%-of-current-holding sale;
- do not execute adapted C2 for that signal bar.

Once E7B exit stage begins:
- adapted C2 is disabled;
- only BS / eligible gray-band / Low<ZK1 final exits are allowed.

## 6. Execution contract

All signals are evaluated on completed selected-timeframe bars.

Signal on close t -> execute at next available selected-timeframe open.

No same-bar close execution and no look-ahead.

## 7. Reset

After any full exit:
- position = 0%;
- E7B exit stage resets;
- adapted C2 becomes available again;
- next valid BUY restarts the cycle at 25%.

## 8. Test scope

Formal evaluation:
- 89 unique archived mainstream U.S. stocks:
  - prior 79-stock universe;
  - fresh OOS10 subset.
- period: 2020-01-02 through 2026-09-30.
- timeframe: 1d.
- friction: 5 bps primary, 10 bps stress.
- compare E7B against frozen V7 under the same data and execution contract.

`SLTD_E7B_WICK_EXIT_STRATEGY_V1 = FROZEN_FOR_TEST`
