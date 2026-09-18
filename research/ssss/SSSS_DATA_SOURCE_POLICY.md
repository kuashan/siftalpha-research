# SSSS Data Source Policy

Last updated: 2026-09-19

Purpose: make SSSS research resilient to vendor outages and rate limits without contaminating experiments through silent data-source changes.

## 1. Provider independence

Trading logic must not depend on a specific market-data vendor.

Research code should consume a normalized daily-bar schema:

```text
date
open
high
low
close
volume
provider
adjustment_mode
timezone
retrieved_at
```

Provider-specific download code belongs in the data layer, not the model layer.

## 2. Current source roles

### Massive

Current primary research source.

Use for official SSSS research when available.

Observed issue:
- intermittent RATE_LIMIT responses during multi-ticker historical retrieval.

### yfinance

Approved fallback for research / parity checking.

Use cases:
- historical daily-bar fallback
- provider comparison
- recovery when the primary source is temporarily unavailable

Limitations:
- unofficial Yahoo Finance access
- provider behavior may change
- Yahoo data-use terms apply
- do not treat as the sole production-grade real-time source

### Alpaca

Preferred future official API candidate for production/live market-data integration.

Use cases:
- historical bars
- real-time stock stream
- explicit adjustment modes
- authenticated and documented feed selection

Free/basic feed limitations must be considered separately from full-market SIP data.

## 3. No silent mixed-provider experiments

Do not construct an official research cohort by silently mixing providers ticker-by-ticker.

Example that is NOT allowed:

```text
28 Discovery tickers from Massive
+ 2 Discovery tickers from yfinance
= one official Discovery result
```

If a provider must change during an experiment:

1. keep the pre-registered ticker cohorts unchanged;
2. keep the strategy rule unchanged;
3. re-download the complete affected research stage from the replacement provider;
4. run a provider-parity audit;
5. record the provider switch before interpreting the replacement-provider result.

If the original provider later recovers, its completed result may be retained as the original-provider result.

## 4. Provider-parity audit

Before a replacement provider becomes an official source for a research stage, compare overlapping data on a representative subset.

Audit at minimum:

- first/last date
- bar count
- missing trading dates
- open/high/low/close
- volume
- split/corporate-action treatment
- timezone/session convention
- adjusted vs raw price semantics

Do not set a universal numeric tolerance until the parity study itself has been recorded.

Material mismatches must be explained before the replacement data are used for official experiment conclusions.

## 5. Corporate-action / adjustment rule

The provider adjustment mode must always be recorded.

Do not assume that two providers use the same meaning of "adjusted".

For SSSS, a provider migration must explicitly document how:
- stock splits
- cash dividends
- spin-offs
- symbol changes

are treated.

## 6. Research-stage source switching

Changing a data vendor does NOT by itself create a new experiment ID if all of the following remain unchanged:

- ticker cohorts
- date range
- strategy formula
- execution convention
- evaluation criteria

However, the provider change must be committed before the replacement-provider result is interpreted.

If any research rule or cohort changes at the same time, create a new experiment ID.

## 7. Production/live-data rule

Open-source clients are not the same thing as data vendors.

A GitHub project may provide:
- API wrappers
- WebSocket clients
- download utilities
- caching
- retries

but the underlying data still comes from Yahoo, Alpaca, exchanges, brokers, or another vendor.

For production/live SiftAlpha use, prefer a documented official API with known:
- market coverage
- latency
- entitlements
- rate limits
- corporate-action behavior
- support / uptime expectations

Use unofficial scraping-style access only as a diagnostic or backup path.

## 8. Raw-data reproducibility

When practical, cache raw downloaded bars or immutable checksums plus:
- provider
- request parameters
- retrieval timestamp
- package/client version

This allows later research to distinguish model changes from vendor-data revisions.

## 9. E031 note

E031 completed its full 30-stock Discovery cohort from Massive despite intermittent rate limits.

Therefore E031 did NOT require a provider switch and remains a single-provider Discovery result.
