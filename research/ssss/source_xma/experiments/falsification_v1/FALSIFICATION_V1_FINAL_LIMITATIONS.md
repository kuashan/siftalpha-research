# Falsification v1 — Final Limitations Archive

Status: FINAL AUDIT DOCUMENT
Date: 2026-09-28

## Purpose

This document records the methodological boundaries of Falsification v1 after terminal hypothesis classification.

It is part of v1 closure hardening.

It does not reopen experiments and does not create v2 hypotheses.

## Core closure principle

The main output of v1 is not the number of terminal classifications.

The main output is demonstrating that the falsification process can reject attractive in-sample findings when they fail independent validation.

Research objective:

**The first goal of the research system is not to discover signals, but to prevent believing signals that do not exist.**

---

# Limitation 1 — Match control rows were not fully persisted

v1 performed matched-control analysis, but the repository did not preserve every selected control row with:

- control identity;
- control date;
- covariate snapshot;
- matching distance.

Consequence:

The exact matched analysis cannot be fully reconstructed after the fact.

This is a v1 infrastructure limitation, not evidence for or against the hypothesis.

v2 hard requirement:

Every matched event must persist the complete control set.

---

# Limitation 2 — Independence estimates are sensitive to clustering definition

The frozen primary definition used market-wave clustering.

Primary:

- +/-2 trading day linkage.

Sensitivity:

- +/-5 trading day linkage.

The wave counts change substantially under wider linkage windows.

Therefore:

- wave count is a cluster description;
- wave count is not effective sample size (ESS);
- no statistical strength claim may use wave count alone.

v2 must report raw episodes, market waves, symbol clusters, and approximate ESS separately.

---

# Limitation 3 — BH-FDR correction was not completed as preregistered

The v1 protocol specified BH-FDR q=0.10.

However, a complete BH vector could not be produced without post-hoc specification choices because some feature data and scalar statistics were not frozen/preserved.

Therefore:

v1 contains no result that has passed a complete preregistered FDR correction.

Important distinction:

This does not mean FDR found failure.

It means the preregistered correction could not be completed without changing the specification.

v2 requirement:

Every hypothesis must define exactly one primary statistic before outcome inspection.

---

# Limitation 4 — Validation B State Density has partial window coverage

The persisted State Density reconstruction ends on 2025-12-30.

The frozen Validation B window ends on 2025-12-31.

Therefore the reconstructed B density is:

PARTIAL-WINDOW RECONSTRUCTION THROUGH 2025-12-30

No missing final day is guessed or backfilled.

---

# Limitation 5 — 2026H1 is not an untouched holdout

2026H1 was not opened as an independent validation window.

However, some Validation B event forward horizons extended into January 2026.

Therefore:

2026H1 does not satisfy the definition of an untouched holdout.

The distinction is:

- not used as an independent validation window: TRUE;
- never exposed through forward horizons: FALSE.

v2 cannot use 2026H1 as a clean sealed future window.

---

# Limitation 6 — INCONCLUSIVE does not mean NOT TESTED

The following terminal classes:

- BELOW_VAL;
- HYS2 interaction;
- Volume;
- Breadth;
- VIX expanded dimensions

are classified as:

INCONCLUSIVE / DATA NOT AVAILABLE.

Meaning:

The research question existed, but preserved v1 holdout data was insufficient to complete the preregistered test.

It does not mean the hypothesis was ignored.

It does not mean the hypothesis was rejected.

v2 may revisit these only with a new preregistered protocol.

---

# Limitation 7 — REJECT conclusions are direction failures, not statistical-power failures

Upper and Lower confluence hypotheses were rejected because validation direction failed.

Upper:

Validation A and Validation B did not show consistent directional behavior.

Lower:

Matched and same-state controls showed no incremental directional advantage.

The rejection is not primarily:

"sample size was too small".

It is:

"the registered proposition did not generalize in the tested windows."

Increasing statistical power alone is not a valid rescue path.

---

# Additional classification rules preserved for future review

## Transition direction decomposition

UP/RANGE/DOWN transition paths remain lifecycle analysis, not standalone directional trading hypotheses.

## Continuous variables

Variables such as:

- dev20;
- penetration depth;
- gap ATR;
- midpoint distance

were used as definitions, controls, or exploratory descriptors.

They were not registered standalone predictive hypotheses in v1.

---

# v1 Final Status

Falsification v1:

**CLOSED WITH INTEGRITY QUALIFICATIONS**

Closure is complete at the hypothesis level.

Remaining limitations are documented methodological constraints for future protocol design.

No v2 experiment is authorized by this document.
