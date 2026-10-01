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
- 1d = validated 5s-crypto V1 baseline
- sub-daily = experimental / unvalidated

## M2 — Binance Futures Testnet adapter
Status: **IMPLEMENTED_AWAITING_TESTNET_ACCEPTANCE**

Implemented:
- official Binance modular USDⓈ-M SDK pinned at 17.5.0
- hard TESTNET-only authenticated adapter
- Testnet credential loading from environment only
- exchange information / symbol filters
- selected-timeframe K-line retrieval
- notional and leverage brackets
- position-mode read and One-way enforcement
- position read and Isolated enforcement
- leverage mutation
- balance / position / open-order / order readback
- Testnet LIMIT BUY submit + cancel primitives
- bounded M2 acceptance CLI
- mock-backed deterministic unit tests

Still required before M2 may be CLOSED:
- real Binance Futures Testnet credentials
- authenticated balance/position/bracket reads PASS
- One-way validation/apply PASS
- Isolated validation/apply PASS on all four symbols
- requested leverage apply/readback PASS on all four symbols
- selected K-line interval read PASS
- one Testnet submit/cancel probe PASS and no orphan order remains

No LIVE.

## M3 — Frozen 5s-crypto V1 signal engine + execution
Status: **NOT_STARTED**

M3 must not start before M2 is CLOSED.

Scope only:
- Python port of frozen three-buy/three-sell equations
- deterministic parity against daily research fixtures
- completed-bar gating
- next-bar-open intent generation
- 60% initial / +40% W3 C confirmation
- SELL-A/B/C full exit
- funding-fee ledger fields
- idempotent client order IDs

## M4 — Recovery + end-to-end Testnet acceptance
Status: **NOT_STARTED**

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
LIVE deployment, other exchanges, Hedge Mode, short selling, Cross Margin, portfolio margin, strategy optimization, timeframe-specific optimization, and automatic leverage optimization are out of scope.
