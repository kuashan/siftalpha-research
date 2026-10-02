# 5s-crypto V1 · Binance USDⓈ-M Futures integration

## Current state

- M1: CLOSED
- M1.1: CLOSED
- M2: CLOSED
- M2.1: IMPLEMENTED_AND_VERIFIED
- M2.2: IMPLEMENTED_AND_VERIFIED
- M2.3: IMPLEMENTED_AND_VERIFIED
- M2.3.1: IMPLEMENTED_AND_VERIFIED
- M2.3.2: IMPLEMENTED_AND_VERIFIED
- M2.3.3: IMPLEMENTED_AND_VERIFIED
- M3: CLOSED
- M4: CLOSED
- M4.1: IMPLEMENTED_AND_VERIFIED

Joint SiftAlpha + Binance Demo real-device acceptance:

`M3_M4_REAL_DEVICE_ACCEPTANCE = PASS`

Acceptance date: **2026-10-02**

This development round is formally closed.

The detailed milestone record is:
`integrations/5s_crypto_binance_usdm_v1/MILESTONES.md`

## Runtime architecture

One Python process manages four independent Strategy Slots:

BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT.

Each slot has its own:
- START/STOP intent
- capital budget
- leverage
- K-line timeframe
- 0% / 60% / 100% runtime position state
- signal/order state
- realized/unrealized PnL
- funding and trading fees
- recovery / reconciliation state

The frozen 5s-crypto V1 signal engine, scheduler, Binance Demo execution path,
idempotent order loop, and recovery / reconciliation gate are implemented and
have passed the completed M3 + M4 joint real-device acceptance.

## Frozen strategy boundary

The runtime uses the frozen `5s crypto v1` strategy contract:
- BUY-A / BUY-B initial target = 60%
- eligible W3 BUY-C top-up target = 100%
- SELL-A / SELL-B / SELL-C / multi-family SELL = full exit
- close-confirmed signal -> next-bar-open execution
- no independent Risk Exit layer

The runtime integration must not change this frozen strategy in place.

## Dashboard

The dashboard uses a mobile-first Chinese interface and includes:
- four symbol tabs
- top Demo connection and reconciliation status
- account / available / strategy capital / total PnL summary
- 300-bar candlestick + volume visualization
- B/S markers from real M3 signal audit events
- collapsible per-symbol trading settings

The chart's 300 bars are display-only.
The strategy scheduler keeps its independent 220-bar default fetch window.

## Capital meaning

A slot's `capital_budget_usdt` is its maximum strategy margin budget, not the account's total balance.

Example:
BTC budget 100 USDT, leverage 5x:
- initial 60% stage = 60 USDT margin / about 300 USDT notional
- BUY-C top-up to 100% = 100 USDT margin / about 500 USDT notional

The execution path verifies Binance available margin and symbol filters before an order.
Configured budgets do not reserve or transfer funds on Binance.

## Demo / LIVE boundary

Current authenticated automated trading integration is for Binance Futures Demo.

API credentials are handled by the current process and are not persisted as
plain credentials in SQLite.

LIVE trading remains unsupported in this closed development round.

## Closure

`M3 = CLOSED`

`M4 = CLOSED`

`5S_CRYPTO_V1_BINANCE_DEMO_INTEGRATION_ROUND = CLOSED`

See:
- `M3_1_ACCEPTANCE.md`
- `M3_2_ACCEPTANCE.md`
- `M4_ACCEPTANCE.md`
