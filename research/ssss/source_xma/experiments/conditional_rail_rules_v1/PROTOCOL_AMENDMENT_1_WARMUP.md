# Protocol Amendment 1 — Warm-up Boundary

Status: FROZEN_BEFORE_LARGE_SAMPLE_OUTCOME_ANALYSIS
Date: 2026-10-01

This amendment changes no rail, state, event, threshold, or outcome definition.

Reason:
Round 1 evaluates calendar 2020. The Source-SSSS slow structure contains a
20-observation weighted input followed by EMA90. Starting indicator
initialization on 2020-01-02 would create an artificial beginning-of-sample
slow-band condition inside the evaluation window.

Rule:
- Load 2019-01-01 through 2025-12-31 where available.
- 2019 is warm-up only.
- No 2019 event or return enters Round 1 statistics.
- Evaluation is 2020-01-01 through 2025-12-31.
- XMA remains literal point-in-time first-observed at every bar.
- ABT 2025-01-15 calibration remains mandatory and unchanged.

If a symbol lacks sufficient 2019 history, flag it rather than silently
changing the warm-up rule.
