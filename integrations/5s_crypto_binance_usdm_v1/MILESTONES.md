# 5s-crypto V1 Binance USDⓈ-M integration — bounded milestones

## M1 — Local control skeleton
Status: **CLOSED**

## M1.1 — Configurable K-line interval
Status: **CLOSED**

## M2 — Binance Futures Testnet adapter
Status: **IMPLEMENTED_AWAITING_TESTNET_ACCEPTANCE**

Implemented:
- official Binance modular USDⓈ-M SDK pinned at 17.5.0
- hard TESTNET-only authenticated adapter
- exchange information / filters / leverage brackets
- One-way + Isolated validation/apply paths
- leverage mutation
- account / position / order readback
- Testnet LIMIT BUY submit + cancel primitives
- per-symbol timeframe/leverage passed into Testnet checks

Still required before M2 may be CLOSED:
- real Binance Futures Testnet credentials
- authenticated account and four-symbol checks
- account settings apply/readback PASS
- one submit/cancel probe PASS with no orphan order

## M2.1 — Four independent Strategy Slots
Status: **IMPLEMENTED_AND_VERIFIED**

One process now owns four independent slots:
- BTCUSDT
- ETHUSDT
- BNBUSDT
- SOLUSDT

Each slot independently persists:
- enabled/start-stop intent
- capital budget USDT
- leverage
- timeframe
- runtime state
- realized PnL
- unrealized PnL
- funding fee
- trading fee
- total PnL

Dashboard aggregates:
- enabled symbol count
- all configured budgets
- enabled budgets
- realized PnL
- unrealized PnL
- total PnL

Old M1 global budget/timeframe values are migrated into existing symbol rows on schema upgrade.

Important boundary:
START in M2.1 means the slot is ARMED/enabled. M3 will attach the actual frozen signal scheduler/executor. No automatic trading is claimed in M2.1.

## M3 — Frozen 5s-crypto V1 signal engine + execution
Status: **NOT_STARTED**

M3 must not start before M2 real Testnet acceptance is CLOSED.

M3 will schedule only enabled slots and must:
- use each slot's own capital budget / leverage / timeframe
- apply 60% initial and W3 BUY-C to 100% independently per symbol
- keep SELL-A/B/C full exit
- update per-symbol and aggregate PnL
- check Binance available margin before every position increase
- reject an order if the slot's required margin cannot be satisfied
- keep sub-daily timeframes experimental

## M4 — Recovery + end-to-end Testnet acceptance
Status: **NOT_STARTED**

## Hard stop boundary
This development round ends at M4.
No cross-symbol capital rebalancing, dynamic leverage, automatic budget optimization, Hedge Mode, short selling, Cross Margin, other exchanges, or strategy optimization.
