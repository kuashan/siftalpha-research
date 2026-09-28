# XMA Falsification v2 Protocol Design Onepager

Status: PRE-PROTOCOL DESIGN DOCUMENT ONLY

## Scope

This document defines the design constraints for XMA Falsification v2. It does not authorize experiment execution, data access, sealed window selection, or hypothesis testing.

## Research Question

Determine whether XMA geometry provides incremental information when combined with pre-registered external or lifecycle conditions. XMA is not treated as a standalone trading signal in v2.

## Candidate Variables (fixed)

Maximum candidate variables: 6. Candidates cannot be replaced after this document is approved.

1. Volatility z-score
   - Orthogonality: external realized volatility information not contained in XMA geometry.
   - Family: F4 Conditional.

2. Volume z-score
   - Orthogonality: volume information is independent from XMA geometry.
   - Family: F4 Conditional.

3. Market Breadth level
   - Orthogonality: market participation information.
   - Family: F5 Risk-Off only.

4. VIX change
   - Orthogonality: external risk shock information.
   - Family: F5 Risk-Off only.

5. Sector relative strength
   - Orthogonality: cross-sectional information.
   - Family: F3 Cross-sectional only.

6. Distance to midpoint
   - Orthogonality: XMA internal continuous state variable used for lifecycle analysis, distinct from discrete XMA state.
   - Family: F2 Lifecycle only.

## Hypothesis Budget

Total hypothesis maximum: 14.

- F1 Risk: 2
- F2 Lifecycle: 2
- F3 Cross-sectional: 2
- F4 Conditional: 4
- F5 Risk-Off: 4

Guard hypotheses are independent of the 14 hypothesis budget.

## FDR Family Structure

F1 Risk:
- XMA internal state conditions.
- Absolute risk outcomes only.

F2 Lifecycle:
- Distance-to-mid and transition path statistics only.
- No MAE, drawdown, or return statistics.

F3 Cross-sectional:
- Sector relative strength only.

F4 Conditional:
- External variables interacting with XMA states.
- Relative return statistics only.

F5 Risk-Off:
- Only tests whether XMA incremental information disappears under predefined risk conditions.
- Not Regime Mining.

## Statistical Boundaries

- Event definition: Episode after continuous-event deduplication.
- Matched control pipeline: dev20, prior20, ATR14/close.
- MDE and sample floors must be fixed before Protocol freeze.
- Sample floor rule: raw events >=100, wave clusters >=30, symbol clusters >=20 per hypothesis.

## Sealed Window Rule

Unlock condition requires all:
- duration >=12 months
- raw events >=100
- wave clusters >=30
- symbol clusters >=20

If insufficient, continue waiting. No sensitivity window substitution.

## Freeze Requirements

Protocol freeze requires:
- Protocol hash
- XMA code hash
- Event detection hash
- State classification hash
- Data version
- Data SHA-256
- preprocessing specification

