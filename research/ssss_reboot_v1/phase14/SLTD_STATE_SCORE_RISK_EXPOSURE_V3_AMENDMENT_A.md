# SLTD State Score Risk-Exposure v3 — Amendment A

Status: **PRE-RESULT NUMERICAL CLARIFICATION / FROZEN**

This amendment is created before any Stage-A result exists.

## 1. Risk/reward numerical definition

The master protocol defines:

`RR = median(MFE_h) / max(abs(median(MAE_h)), 1e-6)`

and then uses `log(RR_state) - log(RR_symbol_baseline)`.

Because a valid forward window can have a non-positive median MFE, the numerator also
requires the same numerical floor before taking a logarithm.

Frozen executable definition:

`RR = max(median(MFE_h), 1e-6) / max(abs(median(MAE_h)), 1e-6)`

`RR_LIFT = log(RR_state) - log(RR_symbol_baseline)`

This is a numerical-domain clarification only. It does not use any observed Stage-A result.

## 2. Stage-A admission gate

Stage A is `IMPLEMENTED_AND_VERIFIED` only if the Temporal split contains:

- at least one stable positive state utility;
- at least one stable negative state utility;
- stable states represented in at least three of the five live components:
  REGIME, INNER, SLOW, EVENT, TRANSITION.

Otherwise:

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_A = REJECTED_NOT_ADMITTED`

No exposure mapping or portfolio claim is allowed from Stage A alone.

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_AMENDMENT_A = FROZEN_BEFORE_RESULT`
