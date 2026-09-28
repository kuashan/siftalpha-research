# Falsification Protocol Amendment 1 — Descriptive Baselines

Status: FROZEN BEFORE OUTCOME ANALYSIS
Date: 2026-09-28

The primary protocol remains unchanged.

This amendment adds two descriptive diagnostics explicitly requested in the research review. They do not alter event definitions, thresholds, or SUPPORT/REJECT criteria.

## A. All-state random baseline

For each event:
- same symbol;
- same validation window;
- control date must not itself be the same-family event;
- exclude +/-20 bars around same-family episodes;
- sample up to 20 eligible bars using deterministic seeded selection.

Report event return minus this all-state random baseline.

Purpose:
distinguish event behavior from unconditional symbol drift.

## B. Path-shape diagnostics

For each event and horizon 5/10/20:
- time to maximum favorable excursion;
- time to maximum adverse excursion;
- first bar with cumulative close return < 0;
- first bar with cumulative close return > 0.

For upper events, classify the post-event path descriptively:

- IMMEDIATE_DECLINE:
  cumulative close return is negative by bar 1 or 2 and MAE occurs before MFE;

- SPIKE_THEN_DECLINE:
  positive MFE occurs first, followed by negative MAE and terminal return < 0;

- SLOW_FADE:
  terminal return < 0 but neither of the above;

- CONTINUATION:
  terminal return >= 0.

These labels are descriptive only and are not new trading thresholds.

## Governance

No already-computed event outcome has been inspected to select this amendment.
No event threshold is changed.
Primary falsification criteria remain those in PROTOCOL_FROZEN_BEFORE_VALIDATION.md.
