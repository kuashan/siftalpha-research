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

Before Protocol freeze, each candidate variable must provide:

- variable name;
- exact definition;
- orthogonality rationale relative to XMA geometry;
- required data fields;
- availability status;
- missing-data treatment.

Candidate count must be frozen before Protocol.

No candidate variable becomes a hypothesis without Protocol registration.

---

# 3. Hypothesis Budget

Protocol must define before testing:

- maximum candidate condition variables;
- maximum hypotheses per variable;
- total hypothesis count.

No additional hypotheses may be added after outcome inspection.

---

# 4. FDR Family Skeleton

Protocol must define:

- family count;
- family membership;
- scalar statistic compatibility;
- hierarchical correction structure.

Family size must be frozen before outcome inspection.

---

# 5. Primary Statistic Requirements

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

# 6. Sealed Window Input

Protocol must define:

- freeze date rule;
- sealed window start rule;
- minimum duration;
- minimum event count;
- minimum cluster count.

Insufficient sample size does not permit lowering standards.

---

# 7. Required Freeze Artifacts

Protocol freeze requires:

- Protocol commit hash;
- XMA calculation code commit hash;
- event detection code commit hash;
- state classification code commit hash;
- data version;
- data SHA-256;
- sealed window definition.

---

# 8. Failure Mode Registration

Protocol must define handling for:

- all hypotheses rejected;
- mixed outcomes;
- insufficient sealed-window samples;
- data hash mismatch;
- code bug discovery after freeze.

---

# 9. Non-Goals

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

Protocol Design One-Pager: DRAFT

Next step:

Review candidate variables, hypothesis budget, FDR family structure, and sealed-window minimum requirements before Protocol drafting.
