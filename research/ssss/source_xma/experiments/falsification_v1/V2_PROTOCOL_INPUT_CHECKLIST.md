# XMA Falsification v2 — Protocol Input Checklist

Status: PRE-PROTOCOL CHECKLIST ONLY / NO EXPERIMENT AUTHORIZED
Date: 2026-09-28

## Purpose

This document does not define v2 hypotheses.

It defines the questions and constraints that must be resolved before writing and freezing the v2 Protocol.

No experiment, data analysis, strategy logic, or sealed-window access is authorized by this document.

---

# 1. Candidate Condition Variable Scope

Before protocol writing, identify candidate XMA condition variables.

A candidate variable must answer:

1. Why can this variable provide orthogonal information relative to XMA geometry?
2. What part of XMA information is not already contained in this variable?
3. Why is this a condition variable rather than a standalone signal?

Required fields:

- definition;
- theoretical interpretation;
- orthogonality rationale;
- required data fields;
- availability status;
- missing-data treatment.

Candidate classes may include:

- market context variables;
- volatility variables;
- volume variables;
- breadth variables;
- lifecycle variables;
- other preregisterable context dimensions.

Candidate variable count must be bounded before Protocol freeze. Range expansion after seeing results is prohibited.

If a candidate variable is unavailable during v2 implementation, it cannot remain permanently INCONCLUSIVE. It must be classified according to the frozen protocol decision, with unavailable candidates excluded from testing.

No candidate becomes a hypothesis until protocol freeze.

---

# 2. Research Category Boundaries

v2 research categories are separated as follows:

## Risk Management

XMA as a risk/context variable.

## Position Lifecycle

Condition variable is XMA's own lifecycle state transition.

## Conditional Information

Condition variable is external context × XMA state interaction.

Lifecycle and Conditional Information share the same statistical design discipline but must not be mixed into one hypothesis family.

## Cross-sectional Ranking

XMA state as a relative ranking/context feature across assets.

## Risk-Off Overlay

Optional category:

Study when XMA information fails or degrades under predefined extreme risk conditions.

This is not Regime Mining and cannot be used to rescue failed directional hypotheses.

---

# 3. Data Availability Audit Requirements

Before any v2 hypothesis is accepted, record:

- required features;
- current availability;
- historical coverage;
- universe coverage;
- frequency;
- missing-data handling.

Unknown availability is not an acceptable basis for hypothesis testing.

Product data schema and research data schema must use the same specification.

Event logs must be designed before strategy integration and include future execution requirements such as:

- timestamp;
- state;
- signal context;
- confidence fields;
- execution result fields.

---

# 4. Sealed Window Rule Input

The sealed window is not selected here.

Required rule:

- sealed window begins only after v2 Protocol freeze;
- pre-freeze data cannot be considered untouched holdout;
- no v1 forward-horizon exposed data may become v2 sealed data;
- sealed data cannot be used for Discovery, Validation, Sensitivity, or Robustness before final unlock;
- once unlocked, it cannot be resealed.

---

# 5. FDR Family Design Questions

Before Protocol freeze determine:

- hypothesis family structure;
- primary statistic grouping;
- correction method;
- whether families are separated by research category or statistic type.

Requirements:

- family membership must correspond to comparable primary statistics;
- family size must be frozen before outcome inspection;
- hierarchical FDR structure should be considered (category level then within-family correction);
- any guard/null hypothesis design must be preregistered.

The final family structure must be frozen before outcome inspection.

---

# 6. Primary Statistic Design Questions

Every hypothesis must specify one primary statistic before testing.

Required decisions:

- absolute metric or relative metric;
- matched or unmatched comparison;
- return-based or risk-based statistic;
- single horizon definition.

No post-result statistic selection is allowed.

---

# 7. Sample Size, MDE and ESS Inputs

Before Protocol freeze determine:

- raw event minimum;
- market-wave cluster minimum;
- symbol cluster minimum;
- ESS reporting method;
- minimum detectable effect (MDE).

Requirements:

- MDE must be based on economic significance, not statistical significance alone;
- sample floor must include raw events, wave clusters, and symbol clusters;
- ESS methodology must be frozen before testing.

Examples of economic MDE categories:

- MAE improvement;
- drawdown reduction;
- holding duration change;
- cross-sectional IC improvement;
- risk-adjusted return improvement.

---

# 8. Research Category Inputs

For each v2 category define:

## Risk Management

Required:

- primary statistic;
- MDE;
- data fields.

## Position Lifecycle

Required:

- primary statistic;
- MDE;
- data fields.

## Cross-sectional Ranking

Required:

- primary statistic;
- MDE;
- data fields.

## Conditional Information

Required:

- primary statistic;
- MDE;
- data fields.

---

# 9. Decay Assumption Input

Before Protocol freeze determine:

- how discovery effect decay is modeled;
- how promotion thresholds incorporate decay;
- how discovery results are prevented from overstating expected future performance.

The decay coefficient belongs to Protocol, not this checklist.

---

# 10. Product Infrastructure Boundary

Allowed before v2 Protocol freeze:

- market data connection;
- execution infrastructure;
- order lifecycle framework;
- risk controls;
- monitoring;
- logging;
- independent kill switch infrastructure.

Not allowed:

- XMA trading rules;
- strategy logic;
- execution rules derived from rejected v1 hypotheses.

Kill switch must be independent from strategy logic.

---

# 11. Non-Goals

v2 will not:

- perform parameter optimization;
- perform Regime Mining;
- switch signal families;
- build multi-signal portfolios;
- create position-sizing rules;
- optimize execution costs;
- design short-selling systems.

v2 answers only one class of question:

**Does XMA geometry provide incremental information as a condition variable?**

---

# 12. Completion Criteria Before Protocol Writing

All items above must have explicit answers before creating:

`XMA_FALSIFICATION_V2_PROTOCOL.md`

Current status:

CHECKLIST UPDATED AFTER REVIEW

Next steps:

1. Review final checklist.
2. Resolve remaining design questions.
3. Freeze v2 Protocol.
4. Select sealed window.
5. Authorize experiments only after freeze.
