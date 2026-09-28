# XMA Falsification v2 Scope Amendment v1

Status: SCOPE AMENDMENT ONLY / NO EXPERIMENT AUTHORIZED
Date: 2026-09-28

This amendment supplements XMA_FALSIFICATION_V2_SCOPE.md.
It does not authorize experiments and does not modify any v1 conclusion.

## 1. Exit Condition Clarification

XMA research termination does not mean SiftAlpha research termination.

If v2 fails:

- XMA geometry research terminates under the defined scope;
- no automatic v3 is opened;
- future research may investigate a different signal family only through a new Discovery → Validation → Falsification lifecycle.

A failed XMA hypothesis cannot be used as the starting point for an unregistered renamed hypothesis.

## 2. Sealed Window Internal Protection Rule

The v2 sealed window is not only unavailable as a final validation set.

Before final unsealing:

- Discovery analysis must not use it;
- Validation analysis must not use it;
- Sensitivity analysis must not use it;
- Robustness analysis must not use it.

The sealed window is opened only once according to the frozen v2 protocol.

After unsealing, it cannot be resealed as a new untouched holdout.

## 3. Research vs Infrastructure Boundary

Before v2 protocol freeze:

SiftAlpha execution infrastructure may be developed, including:

- data ingestion;
- order management infrastructure;
- risk framework;
- monitoring;
- logging;
- manual kill switch.

However:

Infrastructure development must not contain:

- XMA trading rules;
- assumptions that XMA is a valid signal;
- execution logic derived from rejected v1 hypotheses.

## 4. Real Trading Gate Separation

Real trading requires three independent gates:

### Gate 1 — Execution Infrastructure

Required:

- data connection;
- order lifecycle;
- risk controls;
- monitoring.

No strategy assumption is required.

### Gate 2 — Paper Trading Validation

Required after a validated research hypothesis exists:

- live market data;
- simulated execution;
- signal logging;
- slippage tracking;
- minimum observation period defined by protocol.

### Gate 3 — Real Capital Deployment

Requires:

- completed paper validation;
- predefined drawdown limits;
- consistency between research and execution;
- operational exit procedure.

No gate may be skipped.

## 5. v2 Does Not Exist To Find Any Signal

The purpose of v2 is narrower:

XMA geometry alone was rejected as a directional signal in v1.

v2 asks only whether XMA geometry provides incremental information as a condition variable.

## Status

Approved as scope clarification.

v2 Protocol remains NOT STARTED.
