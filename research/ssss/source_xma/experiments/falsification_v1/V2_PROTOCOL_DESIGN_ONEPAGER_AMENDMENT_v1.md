# XMA Falsification v2 — Protocol Design One-Pager Amendment v1

Status: PRE-PROTOCOL DESIGN AMENDMENT ONLY

No experiment authorized.
No data access authorized.
No sealed window selected.

Purpose:

This amendment closes remaining structural gaps identified during One-Pager review before Protocol drafting.

---

# 1. Candidate Variable Orthogonality Requirement

Candidate variables must be identified at field level before Protocol drafting.

Candidate names may be frozen without freezing final implementation details.

Protocol must provide:

- exact definition;
- lookback window;
- normalization method;
- missing-data handling.

Each candidate must provide an orthogonality rationale relative to XMA geometry.

Special review requirements:

- volatility variables must address ATR/XMA collinearity;
- distance-to-midpoint must justify why it is not merely XMA geometry duplication;
- sector relative strength placement between cross-sectional and conditional families must be resolved before freeze.

Candidate variables cannot increase between One-Pager and Protocol.

---

# 2. Hypothesis Budget Freeze

The following limits are fixed inputs for Protocol drafting:

- candidate condition variables: maximum 6;
- hypotheses per variable: maximum 2;
- total hypotheses: maximum 12;
- hypotheses per FDR family: maximum 4.

Unavailable variables cannot be replaced by newly introduced candidates.

---

# 3. Guard Hypothesis Requirements

Guard hypotheses are methodological controls.

Each guard hypothesis requires:

- primary statistic;
- horizon;
- sample floor;
- FDR family assignment.

Guard expectation:

Null effect.

A guard failure indicates possible:

- data leakage;
- FDR implementation issue;
- false-positive process failure.

Family results cannot be promoted until reviewed.

---

# 4. Sealed Window Unlock Rule

Sealed window unlock is not automatic at freeze date plus duration.

Unlock requires the first date when ALL conditions are satisfied:

- minimum duration;
- minimum raw events;
- minimum market-wave clusters;
- minimum symbol clusters.

If conditions are not satisfied:

- do not lower standards;
- do not substitute sensitivity windows;
- do not redefine the start date.

Continue waiting.

---

# 5. Risk-Off Overlay Constraint

Risk-Off Overlay may only test:

Whether XMA incremental information disappears under predefined risk conditions.

It may not test:

Which environments maximize XMA performance.

Environment definitions must be frozen before testing.

Regime Mining is outside v2 scope.

---

# 6. Cross-Family Control

Each hypothesis belongs to exactly one FDR family.

A candidate variable cannot appear in multiple families without explicit preregistered justification.

Cross-family overlap must be resolved before Protocol freeze.

---

Current state:

One-Pager: FINAL REVIEW PASS
Protocol: NOT STARTED
Experiment: NOT AUTHORIZED
