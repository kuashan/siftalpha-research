# Falsification v1 — Hypothesis Ledger Coverage Audit

Status: COMPLETE
Date: 2026-09-28
Branch: research/source-xma-walkforward

## Purpose

This audit checks whether the final Hypothesis Ledger fully covers the hypotheses that were actually registered in the frozen v1 protocol.

This is not a new experiment and does not add new hypotheses.

Classification rules:

- COVERED: registered as a testable hypothesis and has a terminal ledger status.
- DESCRIPTIVE_ONLY: registered as analysis/context, not a directional hypothesis.
- EXPLORATORY_ONLY: studied outside the formal hypothesis family without frozen validation criteria.
- MISSING: registered hypothesis without terminal classification.

## Audit result

Final conclusion:

**No missing closure-relevant hypothesis was identified from the frozen v1 protocol.**

The Ledger is complete for formal closure purposes.

## Coverage mapping

| Protocol item | Classification | Ledger status |
|---|---|---|
| Upper strict confluence incremental bearish/exhaustion information | COVERED | REJECT |
| Lower strict confluence delayed reversal/dislocation information | COVERED | REJECT |
| Lower BELOW_VAL incremental value | COVERED | INCONCLUSIVE / DATA NOT AVAILABLE |
| State transitions lifecycle information | COVERED | OBSERVE / NOT PROMOTED |
| FAST_MID_ANALYTIC lifecycle information | COVERED | OBSERVE / NOT PROMOTED |
| Time-to-confirm / time-stop analysis | COVERED | OBSERVE / NOT PROMOTED |
| HYS2 incremental interaction | COVERED | INCONCLUSIVE / DATA NOT AVAILABLE |
| Volume interaction | COVERED | INCONCLUSIVE / DATA NOT AVAILABLE |
| Breadth interaction | COVERED | INCONCLUSIVE / DATA NOT AVAILABLE |
| VIX expanded dimensions | COVERED | INCONCLUSIVE / DATA NOT AVAILABLE |
| Crypto upper/lower robustness | COVERED | REJECT |

## Symmetry and transition decomposition audit

Checked items:

- UP -> RANGE
- UP -> DOWN
- DOWN -> RANGE
- DOWN -> UP

Finding:

These are covered under the independent state-transition analysis and transition-path analysis. They are not separate directional hypotheses in the frozen protocol.

Classification:

DESCRIPTIVE / LIFECYCLE ANALYSIS

No additional Ledger entry required.

## Continuous-variable audit

Checked potential continuous-variable candidates:

- dev20
- penetration depth
- upperGapAtr
- lowerGapAtr
- distance-to-mid style measures

Finding:

The frozen protocol uses some continuous variables as:

- event definitions;
- matching covariates;
- descriptive decomposition variables.

No separate registered hypothesis was found stating that these continuous variables themselves predict future returns.

Classification:

EXPLORATORY_ONLY / SUPPORTING VARIABLE

No missing Ledger item.

## Midpoint audit

FAST_MID_ANALYTIC was registered as an independent event study:

- cross above midpoint;
- cross below midpoint;
- reclaim after lower confluence;
- loss after upper confluence.

Final classification:

OBSERVE / NOT PROMOTED

No separate continuous midpoint regression hypothesis was registered.

## Multiple testing coverage

The Ledger correctly records the limitation:

- BH-FDR q=0.10 was preregistered;
- complete BH vector cannot be computed as preregistered;
- no result is promoted.

This is a protocol limitation, not an omitted hypothesis.

## Final audit status

HYPOTHESIS LEDGER COVERAGE = PASS

v1 is complete for formal hypothesis closure.

Remaining limitations are methodological:

1. control-level persistence;
2. independence sensitivity;
3. incomplete BH-FDR execution;
4. Validation B boundary coverage;
5. 2026H1 forward-horizon contamination.

No v2 is opened by this audit.
