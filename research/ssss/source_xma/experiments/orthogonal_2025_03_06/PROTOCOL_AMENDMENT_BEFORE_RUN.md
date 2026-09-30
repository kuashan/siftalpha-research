# Protocol Amendment Before Run

Status: FROZEN BEFORE ANY ORTHOGONAL STRATEGY RESULT  
Date: 2026-09-28

The original protocol froze a 100-name breadth proxy sample.

During data retrieval, the GitHub connector's per-run tool-call ceiling prevented loading all 100 files in one deterministic research pass.

No orthogonal strategy result had been generated at that point.

To preserve reproducibility instead of silently using a partial sample, the breadth proxy is reduced **before the run** to a fixed diversified 15-name sample:

- V
- GS
- HD
- PG
- KO
- LLY
- UNH
- GE
- BA
- DE
- LMT
- PM
- SO
- CEG
- MU

The breadth formulas and thresholds are unchanged.

This remains a **breadth proxy**, not official S&P 500 breadth.

All other rules in PROTOCOL_FROZEN_BEFORE_RUN.md remain unchanged.
