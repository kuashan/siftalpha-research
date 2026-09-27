# ABT 2025-Present Source-XMA Walk-Forward

Status: READY FOR DATA / EXPLORATORY  
Ticker: ABT  
Timeframe: 1D  
Anchor: 2025-01-01  
First tradable session: 2025-01-02

## Purpose

Use ABT as the first detailed case study for reconstructing the original SSSS + ADKBY-E XMA information day by day.

This is not a conventional strategy backtest.

We are not asking "which threshold maximizes return?"

We are asking:

- what did the XMA structure show at each point?
- how did that structure revise as later bars arrived?
- which combinations of regime, location, momentum, and confirmation deserve our own action labels?
- where do the author's displayed signals help, and where are they misleading or redundant?

## Prior-knowledge warning

A later ABT chart through roughly September 2026 has already been visually inspected.

Therefore this entire ABT replay is exploratory / previously seen.

It cannot be OOS or Frozen OOS validation.

## Files

- `observations.csv` — point-in-time indicator state
- `decisions.csv` — our independent decision labels and reasons
- future revision snapshots may be added under `revisions/`

## First pass

The first pass should not optimize parameters.

Use the source formulas and the initial decision vocabulary in `../../SIGNAL_LOGIC.md`.

Any material rule change discovered during the replay must be timestamped in the research notes rather than silently rewriting earlier decisions.
