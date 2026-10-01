# 5s-crypto V1 Binance USDⓈ-M integration — bounded milestones

## M1 — Local control skeleton
Status: **CLOSED**

## M1.1 — Configurable K-line interval
Status: **CLOSED**

## M2 — Binance Futures Demo adapter
Status: **CLOSED**

Implemented:
- official Binance modular USDⓈ-M SDK pinned at 17.5.0
- hard TESTNET-only authenticated adapter
- exchange information / filters / leverage brackets
- One-way + Isolated validation/apply paths
- leverage mutation
- account / position / order readback
- Testnet LIMIT BUY submit + cancel primitives

Still required before M2 may be CLOSED:
- real Binance Futures Testnet credentials
- authenticated account and four-symbol checks
- account settings apply/readback PASS
- one submit/cancel probe PASS with no orphan order

## M2.1 — Four independent Strategy Slots
Status: **IMPLEMENTED_AND_VERIFIED**

Each BTC/ETH/BNB/SOL slot independently persists:
- enabled/start-stop intent
- capital budget USDT
- leverage
- timeframe
- runtime state
- realized/unrealized PnL
- funding/trading fees
- total PnL

## M2.2 — Testnet credential entry + virtual account connection
Status: **IMPLEMENTED_AND_VERIFIED**

Added:
- explicit TESTNET environment selector
- API Key / API Secret input form
- API Secret stored only in process memory
- no credential persistence to SQLite
- no secret echo to UI or API status
- connection test against Binance Futures Testnet
- virtual USDT total balance display
- virtual available balance display
- non-zero managed-position count
- One-way account status
- re-test action
- disconnect + in-memory credential wipe
- LIVE remains unavailable

Security boundary:
A failed connection does not retain submitted credentials.
Successful credentials vanish when the Python process exits.

## M2.3 — Mobile-first Chinese dashboard redesign
Status: **IMPLEMENTED_AND_VERIFIED**

UI-only scope:
- compact mobile-first dashboard
- collapsible Testnet account connection
- four-symbol tab switcher instead of four vertically stacked cards
- one visible symbol workspace at a time on mobile
- Chinese visible labels throughout the dashboard
- Chinese signal and timeframe presentation
- no external front-end framework/runtime dependency
- no strategy/execution semantic changes

## M2.3.1 — Dynamic local Web port
Status: **IMPLEMENTED_AND_VERIFIED**

Fixes Android/SiftAlpha local port collisions:
- Web server defaults to port 0 so the OS allocates a free loopback port
- SIFTALPHA_WEB_URL is printed only after bind succeeds
- no fixed 8080 dependency remains
- Web UI stays loopback-only on 127.0.0.1

## M2.3.2 — Binance Futures Demo routing
Status: **IMPLEMENTED_AND_VERIFIED**

Fixes the virtual-account environment mismatch:
- Web credentials now route to Binance Futures Demo
- Demo REST base URL: https://demo-fapi.binance.com
- SDK configuration/constants are imported from binance_common
- Futures Testnet remains available only for lower-level compatibility
- connection failures return safe Chinese diagnostics without exposing secrets

## M2.3.3 — Binance server clock synchronization
Status: **IMPLEMENTED_AND_VERIFIED**

Fixes Binance error -1021 / timestamp outside recvWindow:
- fetch Binance Futures Demo server time before signed requests
- estimate offset using the midpoint of request round-trip time
- patch only the current Python process SDK timestamp generator
- refresh the offset at most every 5 minutes while signed calls continue
- do not change Android or Alpine system time
- public market-data calls remain unchanged
- strategy logic remains unchanged

## M3 — Frozen 5s-crypto V1 signal engine + execution
Status: **IN_PROGRESS**

User accepted the M2 Demo connection path on 2026-10-01 and authorized entry into M3.

### M3.1 — Frozen signal engine parity
Status: **IMPLEMENTED_AND_VERIFIED**

Scope:
- exact Python port of the frozen research state/signal equations
- bar-by-bar parity test against the frozen JavaScript research implementation
- no scheduler or order execution yet

### M3.2 — Four-symbol independent scheduler
Status: **IMPLEMENTED_AWAITING_CI**

### M3.3 — Binance Demo execution + idempotent order loop
Status: **NOT_STARTED**

## M4 — Recovery + end-to-end Testnet acceptance
Status: **NOT_STARTED**

## Hard stop boundary
This development round ends at M4.
No LIVE, cross-symbol capital rebalancing, dynamic leverage, automatic budget optimization, Hedge Mode, short selling, Cross Margin, other exchanges, or strategy optimization.
