# Research Checkpoint — 2026-09-19 — E031 Partial Discovery

## Experiment

E031 — Structural Confirmation ADD

Status: IN_PROGRESS / DATA RATE LIMIT

## Pre-registration integrity

Unchanged.

Discovery:
30 fixed tickers.

OOS:
10 fixed tickers, not opened.

Frozen OOS:
LOW, BA, PGR, ADP, MDLZ, not opened.

Rule family:
- S050B
- S100B
- S150B
- S050X
- S100X
- S150X

No thresholds, formulas, cohorts, or evaluation gates have been changed.

## Successfully retrieved Discovery data

10 tickers:

AAPL, MSFT, NVDA, JPM, XOM, FDX, NEE, ORCL, WMT, GS

For these successful requests:
- 501 daily bars per ticker
- first available bar: 2024-09-18
- last available bar: 2026-09-17

## Retrieval interruption

The market-data provider returned an explicit RATE_LIMIT error while continuing Discovery retrieval.

Earlier zero-row parses for:
- ADBE
- WFC
- MRK
- TMO
- RTX
- AVGO

must not be interpreted as true missing data. They occurred during the provider-rate-limit condition.

## Research decision

No E031 result or candidate ranking is valid yet.

Do not:
- rank the six variants;
- freeze a Discovery winner;
- query OOS;
- query Frozen OOS;
- substitute tickers;
- change thresholds.

E031 must remain IN_PROGRESS until the complete pre-registered Discovery cohort can be evaluated.
