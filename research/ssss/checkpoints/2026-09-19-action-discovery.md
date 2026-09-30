# Research Checkpoint — 2026-09-19 — Action Discovery

## Core model

No production core-rule changes.

- OPEN: Qualified GRB
- Failure CLOSE: Gray -> Green
- Mature CLOSE: Red -> Gray

## ADD

No validated ADD trigger.

Rejected in this round:
- repeated Qualified GRB within the same effective Green episode
- Red-confirmed breakout above the pre-Red path high

## REDUCE

Rejected:
- No-Progress Gray with MFE < 1 ATR and close <= entry
- Red profit-giveback + Raw Gray

Candidate only:
- RTE after at least 2 ATR of prior MFE
- baseline event count remains small
- latest 10-stock OOS produced no qualifying event

## RE-ADD

No validated RE-ADD trigger.

Rejected:
- RTE -> dsep > 0
- RTE -> reclaim RTE-day high while still Red

## Research principle confirmed

A complete state machine must support OPEN / ADD / REDUCE / RE-ADD / HOLD / CLOSE, but a missing action trigger must remain unimplemented until it passes independent validation.

## Next focus

Search for path-dependent action logic with two goals:
1. protect the left tail without cutting rare large winners;
2. identify rare ADD opportunities only when incremental exposure has positive median and OOS value.

Do not optimize action percentages until the action triggers themselves are validated.
