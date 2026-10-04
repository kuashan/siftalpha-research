# SLTD State Score Risk-Exposure v3 — Closeout

Status: **CLOSED**

## Repository-grounded starting point

This phase began only after auditing the real remote research history.

It confirmed that the user's proposed standalone State Score / Exposure direction had
already been tested in two earlier forms:

- Phase12 continuous score exposure:
  `research/sltd-state-score-exposure-map-v1@29ceeeb73328e0f1b1108f01ab14179e858c7e5e`
  -> `REJECTED_NOT_ADMITTED`

- Phase13 hysteretic score regime:
  `research/sltd-state-score-regime-v2@a7b10493450867960e9bdd8ff05f9e3905e854a6`
  -> `REJECTED_SCORE_REGIME_V2`

Both preserved evidence that the score itself contains predictive information, but
their trading mappings were inferior to V7.

## Stage A — risk-adjusted state layer

Commit:
`e996e4344e5c40425bc93253d2e00501bacb3eb8`

Decision:
`IMPLEMENTED_AND_VERIFIED`

Results:

- Discovery state keys: 359
- Discovery support-pass: 198
- Temporal-stable states: 82
- Stable positive utilities: 43
- Stable negative utilities: 39
- Stable components: REGIME, INNER, SLOW, EVENT, TRANSITION

The state utility jointly used:

- 5/10/20-bar return excess
- up-probability lift
- MFE excess
- MAE safety lift
- risk/reward lift

Nested state overlap was controlled before live score aggregation.

No Chan/缠论 was used.
No Fresh OOS was consumed.

## Stage B — score momentum

Commit:
`bf2264581fbf10b31933fa37787e2980b391cca0`

Decision:
`REJECTED_NOT_ADMITTED`

Discovery blocked walk-forward:

- M1 median MAE improvement: -0.016%; positive folds 0/3
- M3 median MAE improvement: -0.022%; positive folds 0/3
- M5 median MAE improvement: -0.026%; positive folds 0/3

Discovery therefore did not support adding Score Momentum.

Temporal consistency for the Discovery-selected least-bad M1:

- LEVEL-only MAE: 1.055399
- LEVEL + asymmetric momentum MAE: 1.055453
- MAE improvement: -0.005%
- baseline rank correlation: 0.03653
- full rank correlation: 0.03661

Top-vs-bottom prediction separation remained directionally sensible, but this cannot
override the pre-registered MAE gates.

## Frozen interpretation

1. The richer risk-adjusted **Score Level** survives and remains research-admissible.
2. Score Momentum does **not** demonstrate incremental predictive value.
3. M1/M3/M5 must not be added to the exposure mapping merely because some descriptive
   diagnostics look favorable.
4. Stage C of v3 is not allowed to proceed.
5. V7 remains unchanged and is still benchmark-only.
6. Chan/缠论 remains excluded.
7. No Fresh OOS was consumed by v3, preserving untouched capacity for a future final test.

## Next admissible architecture

A future continuation must be a new, separately pre-registered study:

`risk-adjusted SLTD Score Level -> data-derived monotone Target Exposure`

It must:

- exclude Score Momentum;
- use the Stage-A Discovery utility as the state score source;
- derive exposure cut points from Discovery only;
- not recycle the rejected manual Phase12 75%-centered threshold map;
- compare against V7, Buy & Hold, SMA200 and exposure-matched fixed-long;
- reserve a genuinely untouched Fresh OOS universe for final admission.

This is a simplification justified by a failed ablation question, not an ad-hoc rule addition.

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_A = IMPLEMENTED_AND_VERIFIED`

`SLTD_STATE_SCORE_MOMENTUM = REJECTED_NOT_ADMITTED`

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3 = CLOSED`
