# XMA Falsification v2 — yfinance Provider Parity Plan v1

Status: **PRE-AUDIT PLAN / NO OFFICIAL PROVIDER SWITCH YET**

Date: 2026-09-28

Purpose:
use the fallback path already authorized by `SSSS_DATA_SOURCE_POLICY.md` while Massive is unavailable.

This plan is frozen before interpreting parity results.

## Candidate client

- package: `yfinance`
- version: `1.7.0`
- release date: 2026-08-26
- PyPI wheel SHA-256:
  `91281ecd1f71069a37155ff8653aff2d3085f3492bd8721f18b70955da62911a`

yfinance remains an unofficial Yahoo Finance client and is not treated as the future production/live vendor.

## Representative parity subset

Fixed before audit:

- AAPL — split/dividend-sensitive mega-cap technology
- NVDA — recent split-sensitive semiconductor
- TSLA — split-sensitive high-volatility discretionary/auto
- JPM — financial
- XOM — energy
- NEE — utilities
- SPY — market benchmark ETF
- XLK — sector ETF

No symbol may be added or removed because its parity looks better or worse.

## Comparison modes

Fetch both yfinance modes for the same dates:

### YF_RAW
- `auto_adjust=False`
- `back_adjust=False`
- `repair=False`
- `actions=True`
- `keepna=True`

### YF_AUTO_ADJUST
- `auto_adjust=True`
- `back_adjust=False`
- `repair=False`
- `actions=True`
- `keepna=True`

Do not enable `repair=True`; doing so would add a second transformation layer.

## Development parity reference

Where Massive overlap cannot currently be retrieved, Twelve Data development snapshots may be used only to characterize the two yfinance modes.

That comparison cannot by itself certify provider parity with Massive.

Official fallback admission requires either:

1. restored Massive overlap compared against yfinance; or
2. a documented governance decision that the complete v2 stage will use yfinance as the replacement provider, with the adjustment semantics independently audited against corporate-action records and the full stage re-downloaded before any scientific outcome is interpreted.

## Required parity fields

For every symbol/mode:

- first/last date
- bar count
- overlap bar count
- dates missing on either side
- OHLC difference distributions
- volume difference distributions
- duplicate dates
- timezone/session metadata
- adjustment mode
- dividends
- stock splits
- raw Close vs Adj Close relationship where available

No universal numerical tolerance is predeclared.

The audit records the observed differences first.

Material discrepancies must be explained before official Data Freeze.

## Date window

Primary parity window:

`2024-01-02 through 2025-12-31`

This window is already development-contaminated and can never become the v2 sealed window.

## Decision states

- `PARITY_ACCEPTABLE_FOR_FALLBACK`
- `PARITY_REQUIRES_EXPLANATION`
- `PARITY_REJECTED`
- `PRIMARY_PROVIDER_OVERLAP_UNAVAILABLE`

No scientific hypothesis result may influence the parity decision.
