# XMA Falsification v2 — Protocol Input Checklist

Status: PRE-PROTOCOL CHECKLIST ONLY / NO EXPERIMENT AUTHORIZED
Date: 2026-09-28

## Purpose

This document does not define v2 hypotheses.

It defines the questions that must be answered before writing and freezing the v2 Protocol.

No experiment, data analysis, or sealed-window access is authorized by this document.

---

# 1. Candidate Condition Variables

Before protocol writing, identify candidate XMA condition variables.

For each candidate:

- definition;
- intended interpretation;
- why it is a condition variable rather than a standalone signal;
- required data fields;
- availability status.

Candidate classes may include:

- market context variables;
- volatility variables;
- volume variables;
- breadth variables;
- lifecycle variables;
- other preregisterable context dimensions.

No candidate becomes a hypothesis until protocol freeze.

---

# 2. Data Availability Audit Requirements

Before any v2 hypothesis is accepted, record:

- required features;
- current availability;
- historical coverage;
- universe coverage;
- frequency;
- missing-data handling.

Unknown availability is not an acceptable basis for hypothesis testing.

---

# 3. Sealed Window Rule Input

The sealed window is not selected here.

Required rule:

- sealed window begins only after v2 Protocol freeze;
- pre-freeze data cannot be considered untouched holdout;
- no v1 forward-horizon exposed data may become v2 sealed data;
- sealed data cannot be used for Discovery, Validation, Sensitivity, or Robustness before final unlock.

---

# 4. FDR Family Design Questions

Before Protocol freeze determine:

- hypothesis family structure;
- primary statistic grouping;
- correction method;
- whether families are separated by research category or statistic type.

The final family structure must be frozen before outcome inspection.

---

# 5. Primary Statistic Design Questions

Every hypothesis must specify one primary statistic before testing.

Open decisions:

- absolute metric or relative metric;
- matched or unmatched comparison;
- return-based or risk-based statistic;
- single horizon definition.

No post-result statistic selection is allowed.

---

# 6. Sample Size and Statistical Power Inputs

Before Protocol freeze determine:

- raw event minimum;
- market-wave cluster minimum;
- symbol cluster minimum;
- ESS reporting method;
- minimum detectable effect (MDE).

Sample size rules must exist before testing.

---

# 7. Research Category Inputs

For each v2 category define:

## Risk Management

Potential inputs:

- MAE;
- drawdown;
- holding duration.

Required:

primary statistic;
MDE;
data fields.

## Position Lifecycle

Potential inputs:

- conditional transition probability;
- lifecycle outcome distribution.

Required:

primary statistic;
MDE;
data fields.

## Cross-sectional Ranking

Potential inputs:

- relative return ranking;
- information coefficient.

Required:

primary statistic;
MDE;
data fields.

## Conditional Information

Potential inputs:

- interaction effects between XMA state and frozen context variables.

Required:

primary statistic;
MDE;
data fields.

---

# 8. Decay Assumption Input

Before Protocol freeze determine:

- how discovery effect decay is modeled;
- how promotion thresholds incorporate decay;
- how discovery results are prevented from overstating expected future performance.

The decay coefficient belongs to Protocol, not this checklist.

---

# 9. Product Infrastructure Boundary

Allowed before v2 Protocol freeze:

- market data connection;
- execution infrastructure;
- order lifecycle framework;
- risk controls;
- monitoring;
- logging;
- kill switch.

Not allowed:

- XMA trading rules;
- strategy logic;
- execution rules derived from rejected v1 hypotheses.

---

# 10. Completion Criteria Before Protocol Writing

All items above must have explicit answers before creating:

`XMA_FALSIFICATION_V2_PROTOCOL.md`

Current status:

CHECKLIST DRAFTED

Next steps:

1. Review checklist.
2. Resolve open design questions.
3. Freeze v2 Protocol.
4. Select sealed window.
5. Authorize experiments only after freeze.
