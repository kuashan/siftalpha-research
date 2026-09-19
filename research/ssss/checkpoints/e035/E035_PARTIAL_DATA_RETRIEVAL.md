# E035 Partial 15m Data Retrieval

Date: 2026-09-19
Status: IN_PROGRESS

Provider:
Massive Crypto composite aggregates.

Ticker:
X:BTCUSD

Timeframe:
15 minutes.

Discovery request:
2024-09-18 through 2025-08-31.

Observed provider behavior:
- 15m history is paginated by underlying base-aggregate limits.
- one page contains roughly 3333 15m bars.
- the response appends a "Next page available" metadata line that must not be parsed as market data.

Current retrieval status:
- 3 complete pages retrieved in one pagination pass
- 9999 valid 15m bars collected before the provider returned explicit RATE_LIMIT
- this partial set is NOT eligible for Phase A strategy interpretation
- no B0/B1/B2 result has been computed from the partial set

Rules:
- do not convert RATE_LIMIT into missing market bars
- do not substitute another provider ticker-by-ticker/page-by-page
- Discovery interpretation requires the full requested Discovery period or a formally recorded full-stage provider switch
- OOS / Frozen OOS / ETH / SOL / BNB 15m remain unopened
