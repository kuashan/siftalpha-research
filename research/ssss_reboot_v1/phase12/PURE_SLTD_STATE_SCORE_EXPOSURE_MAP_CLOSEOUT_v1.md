# Pure SLTD State Score -> Exposure Map v1 — Closeout

Status: **CLOSED**

## Final result

`PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_V1 = REJECTED_NOT_ADMITTED`

The standalone score-to-exposure architecture did not beat the current pure SLTD V7.

Fresh24, 5 bps:

- SCORE_EXPOSURE Return: +63.12%
- V7 Return: +77.26%
- SCORE_EXPOSURE MaxDD: -28.39%
- V7 MaxDD: -16.42%
- SCORE_EXPOSURE Calmar: 0.265
- V7 Calmar: 0.540

The candidate also failed the 10 bps V7 comparison.

## What did work

The score itself retained strong directional separation on the untouched Fresh24 sample.

25% target bucket:
- 10d cross-symbol excess: -0.17%
- 20d cross-symbol excess: -0.53%

100% target bucket:
- 10d cross-symbol excess: +1.06%
- 20d cross-symbol excess: +1.97%

All pre-registered extreme-bucket direction and support gates passed.

Therefore the rejection is **not** evidence that the SLTD state score is useless.
It is evidence that directly replacing V7 with a continuously rebalanced exposure map is inferior.

## Why the portfolio failed

The score system:
- remained invested every formal bar;
- changed target exposure far more often than V7;
- average turnover was 33.63 versus V7 5.23;
- reduced some weak-state exposure but did not reproduce V7's sparse entry/exit structure and C2 risk behavior.

That produced:
- a modest improvement over fixed 75% long,
- but materially worse drawdown and lower return than V7.

## Frozen interpretation

1. Pure SLTD state ranking is real enough to survive another untouched stock universe.
2. The state score is better treated as **context / confidence / gating information**.
3. It should not replace the current V7 position engine as a standalone exposure controller.
4. Production V7 remains unchanged.
5. Chan/缠论 remains excluded from SLTD.

## Boundary for any future continuation

Do not tune the rejected exposure thresholds on Fresh24.

If research resumes, the next admissible architecture is a separately pre-registered
**V7 + state-score gate** study, where the existing V7 remains the execution engine and
the score is allowed only to:
- admit or suppress a V7 action,
- or scale the size of an already-existing V7 action.

It must not invent a new isolated BUY/SELL rule from Fresh24 results.

`PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_PHASE12 = CLOSED`
