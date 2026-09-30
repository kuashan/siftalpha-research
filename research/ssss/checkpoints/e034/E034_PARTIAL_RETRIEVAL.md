# E034 Partial Retrieval Checkpoint

Date: 2026-09-19

Status: IN_PROGRESS

## Equity Discovery retrieval

Successfully retrieved and processed:
AAPL, MSFT, NVDA, JPM, XOM,
ADBE, WFC, MRK, FDX, NEE,
AVGO, PEP, C, MDT, UNP,
IBM,
LLY, GE, V, TGT, COP

Count:
21 / 30 tickers.

Pending only because of explicit Massive RATE_LIMIT responses:
ORCL, WMT, GS, TMO, RTX,
CVX, HD, AMGN, MCD

Count:
9 / 30 tickers.

Important:
- pending tickers are NOT treated as zero-event assets;
- no substitutions are allowed;
- no aggregate feature-outcome interpretation has been performed;
- equity OOS and Frozen OOS remain unopened;
- crypto OOS and Frozen OOS remain unopened.

## Implementation state

The causal feature implementation has been audited in:
E034_CAUSALITY_AUDIT.md

Partial batch records are stored under:
research/ssss/checkpoints/e034/

The official E034 decision must wait until all pre-registered Discovery data are complete or a full-stage provider switch is explicitly recorded according to SSSS_DATA_SOURCE_POLICY.md.
