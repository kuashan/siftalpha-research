# XMA Falsification v2 — Independent Execution Check v1

Status: **PASS / NON-FREEZE EVIDENCE**

Date: 2026-09-28

Purpose:
separate code/test defects from the repository-wide GitHub-hosted Actions execution gate.

This check is not F2 Code Freeze acceptance.

## Environment

Independent execution sandbox:

- Python 3.13.5
- numpy 2.3.5
- pandas 2.2.3
- scipy 1.17.0
- statsmodels 0.14.6

These are not the candidate frozen versions in `requirements_v2.txt`.

Therefore this check proves executable logic, not frozen-environment reproducibility.

## Test sequence

The connector-fetched implementation/test logic was mirrored into an isolated execution directory and the committed test cases were exercised.

Initial run exposed one test-definition defect:

`test_debounce_gap_rule`

The test used qualifying indices:

`0, 2, 5, 7`

but the frozen Protocol says successive qualifying session gap <=3 remains the same Episode.

Because:

`5 - 2 = 3`

the implementation correctly returned one transitive Episode, while the test incorrectly expected two.

The repository test was corrected before rerun:

- commit: `a07776eddc6c11a707079f5a2e5c7ae90aa7e4d0`
- corrected qualifying indices: `0, 2, 6, 7`
- `6 - 2 = 4` correctly opens the second Episode.

No scientific outcome was inspected to make this correction.

## Final execution

Final deterministic suite:

- `test_v2_infrastructure.py`
- `test_v2_protocol_engine.py`
- `test_v2_statistics_guards.py`
- `test_provider_parity.py`

Result:

`21 tests / 21 PASS`

Covered behavior includes:

- 32/39 daily Breadth eligibility vs 51/51 Data-Freeze completeness;
- normalized panel hashes;
- prior-20-valid Breadth Q10;
- Episode debounce;
- F1 continuous-state runs;
- exact session-index market waves;
- design-effect ESS;
- BH-FDR;
- deterministic F5 pairing;
- Guard gate and fixed-seed permutations;
- KM median;
- rank-biserial / partial Spearman primitives;
- provider parity subset freeze;
- zero-difference parity behavior;
- corporate-action extraction;
- parity differences reported without automatic threshold classification.

## Interpretation

This result materially reduces the probability that the current engineering blocker is a Python/unit-test failure.

It does **not** replace the required frozen-environment execution because:

1. runtime versions differ from the candidate lock;
2. GitHub-hosted Actions still never starts a workflow step;
3. F2 Code Freeze requires the exact frozen source/runtime manifest.

Decision:

`INDEPENDENT_EXECUTION = PASS`

`F2_CODE_FREEZE = NOT YET PASS`
