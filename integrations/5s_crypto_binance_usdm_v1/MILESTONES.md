# 5s-crypto V1 Binance USDⓈ-M integration — bounded milestones

## M1 — Local control skeleton
Status: **CLOSED**

## M1.1 — Configurable K-line interval
Status: **CLOSED**

## M2 — Binance Futures Demo adapter
Status: **CLOSED**

Implemented:
- official Binance modular USDⓈ-M SDK pinned at 17.5.0
- authenticated Demo adapter and account/position/order readback
- exchange information / filters / leverage brackets
- One-way + Isolated validation/apply paths
- leverage mutation
- submit/cancel primitives and verified Demo connection path

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
- connection test against Binance Futures Testnet / Demo path
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

- Web credentials route to Binance Futures Demo
- Demo REST base URL: https://demo-fapi.binance.com
- SDK configuration/constants are imported from binance_common
- Futures Testnet remains available only for lower-level compatibility
- connection failures return safe Chinese diagnostics without exposing secrets

## M2.3.3 — Binance server clock synchronization
Status: **IMPLEMENTED_AND_VERIFIED**

- fetch Binance Futures Demo server time before signed requests
- estimate offset using the midpoint of request round-trip time
- patch only the current Python process SDK timestamp generator
- refresh the offset at most every 5 minutes while signed calls continue
- do not change Android or Alpine system time
- public market-data calls remain unchanged
- strategy logic remains unchanged

## M3 — Frozen 5s-crypto V1 signal engine + execution
Status: **CLOSED**

Joint real-device acceptance with M4: **PASS**
Acceptance date: **2026-10-02**

### M3.1 — Frozen signal engine parity
Status: **IMPLEMENTED_AND_VERIFIED**

Scope:
- exact Python port of the frozen research state/signal equations
- bar-by-bar parity test against the frozen JavaScript research implementation

### M3.2 — Four-symbol independent scheduler
Status: **IMPLEMENTED_AND_VERIFIED**

### M3.3 — Binance Demo execution + idempotent order loop
Status: **IMPLEMENTED_AND_VERIFIED**

Implemented:
- 60% initial BUY-A/B Demo MARKET entry
- eligible W3 BUY-C remaining 40% top-up
- SELL-A/B/C and multi-family full reduce-only exit
- per-symbol configured budget/leverage/timeframe
- available-margin and symbol-filter checks
- One-way + Isolated enforcement
- deterministic clientOrderId and local order ledger
- crash-safe remote order lookup path
- realized/unrealized PnL + funding + commission accounting
- wired into the running Web app scheduler

## M4 — Recovery + end-to-end Demo acceptance
Status: **CLOSED**

Joint real-device acceptance with M3: **PASS**
Acceptance date: **2026-10-02**

Implemented and accepted:
- per-symbol startup/reconnect reconciliation gate
- SQLite filled-order ledger vs Binance Demo position reconciliation
- pending-order crash recovery by clientOrderId
- strategy-owned orphan order cleanup
- external/manual order and unknown-position blocking
- no stale signal backfill after downtime; recovery rebases at latest closed bar
- PnL/funding/fee refresh after recovery
- explicit re-reconcile, strategy-order cancel, and emergency-flat controls

### M4.1 — Visualization and compact dashboard
Status: **IMPLEMENTED_AND_VERIFIED**

- exact title: `5s crypto v 1`
- top connection + reconciliation status
- four summary metrics in one mobile row
- four symbol tabs in one mobile row
- per-symbol 300-bar candlestick + volume visualization
- chart timeframe follows the saved symbol timeframe
- B/S markers come from real M3 signal audit events
- 300-bar display is isolated from the strategy scheduler's 220-bar default fetch window
- trade settings are collapsible
- 3m / 5m are available as experimental monitoring/trading timeframes; frozen strategy equations and the 220-bar scheduler fetch window remain unchanged
- CI Run 36832764258 PASS

## Final closure

`M3 = CLOSED`

`M4 = CLOSED`

`5S_CRYPTO_V1_BINANCE_DEMO_INTEGRATION_ROUND = CLOSED`

The frozen 5s-crypto V1 strategy rules were not changed by this closure.

## Hard stop boundary

This development round is formally closed at M4.

Not included:
- LIVE
- cross-symbol capital rebalancing
- dynamic leverage
- automatic budget optimization
- Hedge Mode
- short selling
- Cross Margin
- other exchanges
- strategy optimization
