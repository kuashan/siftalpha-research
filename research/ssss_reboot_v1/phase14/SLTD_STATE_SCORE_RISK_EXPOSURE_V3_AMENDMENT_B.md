# SLTD State Score Risk-Exposure v3 — Amendment B

Status: **PRE-RESULT SEMANTIC NORMALIZATION CORRECTION / FROZEN**

This amendment is created before any Stage-A result file exists.

## Problem corrected

The master protocol originally said to center each predictive dimension on the median
across supported Discovery states before robust-z normalization.

That would be inappropriate here because every raw predictive dimension is already a
lift/excess relative to the symbol's unconditional baseline.

Therefore:

- raw value = 0 already has a natural semantic meaning: neutral versus baseline;
- raw value > 0 means favorable versus baseline;
- raw value < 0 means unfavorable versus baseline.

Centering again on the cross-state median would turn absolute predictive direction into
relative ranking among states and could invert the meaning of a positive or negative score.

## Frozen normalization

For each dimension on supported Discovery states:

- semantic center = **0**
- scale = median(abs(raw_dimension))
- if that scale is effectively zero, use the 75th percentile of abs(raw_dimension)
- if still effectively zero, mark the dimension non-informative

Then:

`normalized_dimension = raw_dimension / scale`

The composite remains:

`STATE_UTILITY = median(non-missing normalized dimensions)`

This preserves zero as the true neutral point while keeping dimension magnitudes
comparable without manually chosen coefficients.

No Stage-A result, Temporal result, or Fresh OOS result was available when this
correction was frozen.

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_AMENDMENT_B = FROZEN_BEFORE_RESULT`
