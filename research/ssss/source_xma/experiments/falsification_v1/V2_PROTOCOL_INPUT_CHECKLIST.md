# XMA Falsification v2 — Protocol Input Checklist

Status: PRE-PROTOCOL CHECKLIST ONLY / NO EXPERIMENT AUTHORIZED
Date: 2026-09-28

## Purpose

This document does not define v2 hypotheses.

It defines the questions and constraints that must be resolved before writing and freezing the v2 Protocol.

No experiment, data analysis, strategy logic, or sealed-window access is authorized by this document.

---

# Additional Governance Constraints Before Protocol Freeze

## Data Freeze and Code Freeze

Protocol freeze must include both data freeze and code freeze.

### Data freeze

Before Protocol freeze:

- v2 historical datasets must be exported;
- dataset hashes (SHA-256 or equivalent) must be recorded;
- data versions and preprocessing specifications must be recorded in the Protocol appendix.

After Protocol freeze:

- historical data cannot silently change;
- preprocessing changes require Amendment.

### Code freeze

Before Protocol freeze:

- XMA calculation code commit hash must be recorded;
- event detection code commit hash must be recorded;
- state classification code commit hash must be recorded.

After Protocol freeze:

- code changes require Amendment;
- Amendment must document the reason and scope of change.

A text-only Protocol freeze is not sufficient research freeze.

---

# Candidate Condition Variable Scope

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

Unavailable candidate handling:

- Structurally unavailable: data source cannot provide the required history or feature definition; classify as REJECT before testing.
- Temporarily unavailable: data can theoretically be obtained before freeze; if still unavailable after Protocol freeze, classify according to frozen decision and do not keep permanently INCONCLUSIVE.

No candidate becomes a hypothesis until protocol freeze.

---

# Research Category Boundaries

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

Study only whether XMA information disappears or degrades under predefined extreme risk conditions.

Rules:

- must use predefined risk environments;
- cannot search for environments where XMA works best;
- cannot rescue failed directional hypotheses.

Searching for optimal regimes is Regime Mining and is outside v2 scope.

---

# Sealed Window Rule Input

The sealed window is not selected here.

Required rule:

- sealed window begins only after v2 Protocol freeze;
- pre-freeze data cannot be considered untouched holdout;
- no v1 forward-horizon exposed data may become v2 sealed data;
- sealed data cannot be used for Discovery, Validation, Sensitivity, or Robustness before final unlock;
- once unlocked, it cannot be resealed.

Protocol must additionally define:

- minimum sealed window duration;
- minimum event count;
- minimum cluster count.

If the sealed window expires with insufficient samples:

- do not lower standards;
- do not substitute sensitivity windows;
- extend observation until requirements are met.

---

# Completion Criteria Before Protocol Writing

All items above must have explicit answers before creating:

`XMA_FALSIFICATION_V2_PROTOCOL.md`

Current status:

CHECKLIST UPDATED AFTER FINAL GOVERNANCE REVIEW

Next steps:

1. Review final checklist.
2. Resolve remaining design questions.
3. Freeze v2 Protocol with data hash and code hash.
4. Select sealed window.
5. Authorize experiments only after freeze.
