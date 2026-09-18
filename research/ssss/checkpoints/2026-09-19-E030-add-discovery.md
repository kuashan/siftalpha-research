# Research Checkpoint — 2026-09-19 — E030 ADD Discovery

## Experiment

E030 — Progress -> Controlled Pullback -> Re-acceleration ADD

Status: REJECT_DISCOVERY

## Governance

Pre-registered before results:
- Discovery: 25 stocks
- OOS: 10 stocks
- Frozen OOS: 5 stocks
- six fixed candidate variants
- fixed date range, execution convention, and pass/fail criteria

No OOS or Frozen OOS result was viewed.

## Discovery result

FastUpper reset:
- U075: 3 signals, 0 resolved, 3 stocks
- U100: 3 signals, 0 resolved, 3 stocks
- U150: 3 signals, 0 resolved, 3 stocks

FastMid test/reclaim:
- M075: 0 signals
- M100: 0 signals
- M150: 0 signals

The three U-family signals were in:
- AAPL
- MSFT
- XOM

All three remained unresolved by sample end.

## Pre-registered gate

Required to advance:
- >= 12 resolved ADD legs
- >= 6 Discovery stocks
- mean net ADD-leg return > 0
- median net ADD-leg return > 0
- profit factor > 1

The event-count gate failed before return-quality metrics could be evaluated.

## Decision

Reject the exact E030 six-variant family.

Do not open OOS.
Do not open Frozen OOS.
Do not add an ADD trigger to the production/research core model.

## Interpretation

The hypothesis was directionally sensible but the exact formulation was too restrictive:
- prior progress
- controlled pullback
- pre-Red requirement
- re-acceleration
- anti-chase cap

Together these conditions produced too few usable events in the available history.

Next research should formulate a materially different ADD hypothesis rather than loosening E030 after seeing this result.
