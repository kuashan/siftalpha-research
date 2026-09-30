# XMA Falsification v2 — Protocol Design One-Pager

Status: PRE-PROTOCOL DESIGN DOCUMENT ONLY

No experiment authorized.
No data access authorized.
No sealed window selected.

## Purpose

This document defines the skeleton required before writing `XMA_FALSIFICATION_V2_PROTOCOL.md`.

It does not define final hypotheses.
It does not authorize testing.

The purpose is to prevent Protocol drafting from creating additional researcher degrees of freedom.

---

# 1. v2 Research Question

v2 does not ask whether XMA geometry is a standalone trading signal.

v1 already tested the directional signal interpretation.

v2 asks:

> Does XMA geometry provide incremental information as a condition variable when combined with orthogonal context variables?

---

# 2. Candidate Condition Variable Design

Candidate variables must be specified at field-name level before Protocol drafting.

Examples of candidate names may include:

- Volatility z-score
- Volume z-score
- Market breadth level
- VIX change
- Sector relative strength
- Distance to midpoint

One-Pager specifies variable names only.
Protocol specifies exact windows, transformations, normalization, and missing-data handling.

Candidate variables cannot be added after Protocol freeze.

Each candidate must provide:

- orthogonality rationale relative to XMA geometry;
- required data fields;
- availability status;
- missing-data treatment.

No candidate variable becomes a hypothesis without Protocol registration.

Candidate variables unavailable after freeze are not replaced by new variables.

---

# 3. Hypothesis Budget

Frozen design limits:

- candidate condition variables: maximum 6;
- hypotheses per variable: maximum 2;
- total hypotheses: maximum 12;
- hypotheses per FDR family: maximum 4.

These limits cannot be expanded during Protocol drafting or after outcome inspection.

---

# 4. FDR Family Skeleton

Initial family structure:

| Family | Scope | Maximum hypotheses |
|---|---|---:|
| F1 Risk | MAE / Drawdown / Duration | 3 |
| F2 Lifecycle | XMA state transition conditional paths | 3 |
| F3 Cross-sectional | Ranking / IC | 2 |
| F4 Conditional | XMA × external variable interaction | 2 |
| F5 Risk-Off | Predefined failure environment tests | 2 |
| F6 Null / Control | Guard hypotheses | methodological control |

Each family requires:

- frozen membership;
- comparable scalar statistics;
- predefined correction procedure.

Each family must contain at least one guard hypothesis.

If guard hypotheses become significant after correction, the family is frozen pending methodology review.

---

# 5. Research Category Boundaries

Lifecycle:

- condition variable = XMA internal state transition.

Conditional:

- condition variable = external variable combined with XMA state.

Risk-Off:

- only tests whether XMA incremental information disappears under predefined risk conditions.

Risk-Off cannot search for environments where XMA is strongest.

That would be Regime Mining and is outside v2.

---

# 6. Primary Statistic Requirements

Every hypothesis must contain:

- one primary statistic;
- one horizon;
- one comparison method;
- one expected direction;
- one MDE;
- one sample floor;
- one FDR family.

No TBD values are allowed in Protocol draft.

---

# 7. MDE and Sample Requirements

MDE must be based on economic significance, not statistical significance alone.

Protocol must define:

- raw event minimum;
- market-wave cluster minimum;
- symbol cluster minimum;
- ESS calculation method.

Minimum floors must be satisfied simultaneously.

---

# 8. Sealed Window Input

Protocol must define:

- freeze date rule;
- sealed window start rule;
- minimum duration;
- minimum event count;
- minimum cluster count.

Required minimum rules:

- duration >= 12 months;
- raw events >= 100 per hypothesis;
- market-wave clusters >= 30;
- symbol clusters >= 20.

If insufficient at expiry:

- do not lower standards;
- do not substitute sensitivity windows;
- do not redefine the start date.

Continue waiting.

---

# 9. Required Freeze Artifacts

Protocol freeze requires:

- Protocol commit hash;
- XMA calculation code commit hash;
- event detection code commit hash;
- state classification code commit hash;
- data version;
- data SHA-256;
- sealed window definition.

---

# 10. Cross-Family Interference Rules

Rules:

- one hypothesis belongs to one family only;
- one variable cannot be duplicated across families without explicit justification;
- overlapping hypotheses must be resolved before Protocol freeze.

---

# 11. Failure Mode Registration

Protocol must define handling for:

- all hypotheses rejected;
- mixed outcomes;
- insufficient sealed-window samples;
- data hash mismatch;
- code bug discovery after freeze.

---

# 12. Non-Goals

v2 will not:

- optimize parameters;
- perform Regime Mining;
- switch signal families;
- create portfolios;
- design position sizing;
- optimize execution;
- create short-selling rules.

---

# Current State

Protocol Design One-Pager: FINAL REVIEW READY

Next step:

Review this frozen-design skeleton before drafting `XMA_FALSIFICATION_V2_PROTOCOL.md`.

No experiment is authorized.
No data access is authorized.
