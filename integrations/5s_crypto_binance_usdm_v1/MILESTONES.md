# 5s-crypto V1 Binance USDⓈ-M integration — bounded milestones

## M1 — Local control skeleton
Status: **CLOSED**

Scope:
- Web dashboard
- PAPER-only hard lock
- BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT only
- USDⓈ-M perpetual only
- One-way + Long-only + Isolated semantics
- Per-symbol leverage input 1..125x
- SQLite persistence
- Binance public connectivity probe
- No API key; no authenticated account mutation; no orders

## M1.1 — Configurable K-line interval
Status: **CLOSED**

Added only:
- selectable intervals: 15m / 1h / 2h / 4h / 6h / 12h / 1d
- SQLite persistence for selected interval
- status endpoint exposes interval and validation state
- 1d is explicitly labeled the validated 5s-crypto V1 baseline
- all sub-daily intervals are explicitly labeled experimental / unvalidated

No strategy rule is optimized or changed by M1.1.

## M2 — Binance Futures Testnet adapter
Scope only:
- official Binance modular USDⓈ-M SDK
- Testnet credentials
- exchange information / filters
- current leverage bracket
- isolated margin validation
- one-way validation
- change initial leverage
- account / position / order readback
- testnet order submit/cancel only
- use the persisted selected K-line interval for market-data subscription/polling

No LIVE.

## M3 — Frozen 5s-crypto V1 signal engine + execution
Scope only:
- Python port of the frozen three-buy/three-sell equations
- deterministic parity against existing daily research fixtures
- completed-bar gating
- next-bar-open intent generation for the selected interval
- 60% initial / +40% W3 C confirmation
- SELL-A/B/C full exit
- funding-fee ledger fields
- idempotent client order IDs

No strategy optimization. No new indicators. No timeframe-specific parameter tuning.
Sub-daily intervals remain experimental until separately validated.

## M4 — Recovery + end-to-end Testnet acceptance
Scope only:
- restart recovery
- pending-order reconciliation
- duplicate-order prevention
- exchange/account drift checks
- emergency stop
- end-to-end Testnet acceptance report

M4 closure state: `5S_CRYPTO_BINANCE_USDM_V1_INTEGRATION = CLOSED_TESTNET_READY`

## Hard stop boundary
This development round ends at M4.
LIVE deployment, other exchanges, Hedge Mode, short selling, Cross Margin, portfolio margin, strategy optimization, timeframe-specific optimization, and automatic leverage optimization are explicitly out of scope and require a new separately approved round/version.
