# SLTD State Score Risk-Exposure v3 — Stage B Momentum Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

Parent:
- Stage A result: `IMPLEMENTED_AND_VERIFIED`
- Stage A commit: `e996e4344e5c40425bc93253d2e00501bacb3eb8`

## 1. Purpose

Test whether change in the risk-adjusted SLTD score contains incremental information
beyond the current score level itself.

This stage chooses exactly one pre-declared momentum definition:

- M1 = LEVEL_t - LEVEL_(t-1)
- M3 = LEVEL_t - median(LEVEL_(t-3:t-1))
- M5 = LEVEL_t - median(LEVEL_(t-5:t-1))

No other lookback may be introduced after results are observed.

## 2. Statistical boundary

Stage A already used the 2024-2026Q3 Temporal split to determine which state
descriptions are temporally stable.

Therefore:

- Discovery 2020-2023 is the only dataset allowed to SELECT M1/M3/M5.
- 2024-2026Q3 is a **temporal consistency check**, not a new independent OOS.
- no Stage B parameter may be selected or changed because of the Temporal result.
- final promotion of the overall v3 architecture still requires a new Fresh OOS universe
  untouched by all prior phases.

## 3. Frozen live LEVEL construction

Use the Stage-A temporally-stable state IDs only.

State utility used in live LEVEL is the **Discovery utility**, never the Temporal utility.

Per bar:

### REGIME
- if stable F2 matches, use F2;
- else if stable F1 matches, use F1.

### INNER
- stable F3.

### SLOW
- if stable F4 and/or F5 match, use their median as one component.

### EVENT
- within the same event, stable F7 overrides F6;
- multiple independent events are reduced by median to one EVENT component.

### TRANSITION
- stable F8 as a separate component;
- multiple transition-event matches are reduced by median.

Then:

`LEVEL_t = median(non-zero matched component utilities)`

If no stable component matches:

`LEVEL_t = 0`.

No outcome data from bar t or later enter LEVEL_t.

## 4. Realized forward utility label

For each bar t and h in {5,10,20}, outcomes use:

- entry reference = open t+1
- return_h
- up indicator_h
- MFE_h
- MAE_h
- per-bar RR_h

For each training segment and each symbol, estimate unconditional baselines using
training rows only.

Construct five baseline-relative dimensions:

- RETURN = return_h - symbol baseline median return_h
- UP_PROB = 1(return_h>0) - symbol baseline up probability
- MFE = MFE_h - symbol baseline median MFE_h
- MAE_SAFETY = MAE_h - symbol baseline median MAE_h
- RR = log(per-bar RR_h) - log(symbol baseline RR_h)

Collapse each dimension across 5/10/20 using the median.

Normalize every dimension with semantic zero preserved:

- center = 0
- scale = training median(abs(dimension))
- fallback = training P75(abs(dimension))
- degenerate dimensions are omitted

Then:

`FORWARD_UTILITY_t = median(non-missing normalized forward dimensions)`

This label is never available to the trading system; it is research-only.

## 5. Predictor form and asymmetry

For candidate Mk:

- LEVEL
- MOM_UP = max(Mk, 0)
- MOM_DOWN = min(Mk, 0)

The asymmetric candidate model is:

`FORWARD_UTILITY ~ 1 + LEVEL + MOM_UP + MOM_DOWN`

Comparator:

`FORWARD_UTILITY ~ 1 + LEVEL`

All predictor scales are learned on the training segment only, with semantic zero
preserved.

Linear coefficients are fitted by ordinary least squares via deterministic
`numpy.linalg.lstsq`.

No regularization parameter is tuned.

## 6. Discovery blocked walk-forward selection

Three folds:

1. train 2020 -> validate 2021
2. train 2020-2021 -> validate 2022
3. train 2020-2022 -> validate 2023

For every candidate M1/M3/M5 and every fold report:

- baseline MAE
- full-model MAE
- MAE improvement = (baseline - full) / baseline
- baseline rank correlation with realized utility
- full-model rank correlation
- rank-correlation improvement
- MOM_UP coefficient
- MOM_DOWN coefficient

Rank correlation is Pearson correlation of average ranks, implemented without external
statistical packages.

### Discovery selection score

Primary:
- median fold MAE improvement.

Required:
- median MAE improvement > 0;
- full model improves MAE in at least 2/3 folds.

Tie-breaks, in order:
1. larger median rank-correlation improvement;
2. more positive-MAE-improvement folds;
3. shorter lookback (M1 before M3 before M5).

The winning definition is frozen from Discovery only.

## 7. Temporal consistency check

After the winner is frozen:

- refit baseline and full models on all Discovery 2020-2023;
- apply unchanged to Temporal 2024-2026Q3;
- training-only baselines/scales are used.

Report:
- baseline vs full MAE;
- MAE improvement;
- baseline vs full rank correlation;
- top-quartile vs bottom-quartile realized forward utility under full prediction;
- MOM_UP and MOM_DOWN coefficients fitted on Discovery.

Stage B passes only if:

1. Discovery selection requirements pass;
2. Temporal full-model MAE < Temporal baseline MAE;
3. Temporal full-model rank correlation > Temporal baseline rank correlation;
4. Temporal top prediction quartile has higher median realized forward utility than
   bottom prediction quartile.

The Temporal result may reject Stage B but may not change the selected momentum window.

## 8. Decision

If all gates pass:

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_B = PROMOTED_TO_STAGE_C`

Otherwise:

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_B = REJECTED_NOT_ADMITTED`

No exposure thresholds are fitted in Stage B.
No V7 rule is used.
No Chan/缠论 is used.
No Fresh OOS is consumed.

`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_B_PROTOCOL = FROZEN`
