# 5s-crypto V1 · Binance USDⓈ-M Futures integration

## Current state

- M1: CLOSED
- M1.1: CLOSED
- M2: IMPLEMENTED_AWAITING_TESTNET_ACCEPTANCE
- M2.1: IMPLEMENTED_AND_VERIFIED
- M2.2: IMPLEMENTED_AND_VERIFIED
- M2.3: IMPLEMENTED_AND_VERIFIED
- M3: NOT_STARTED
- M4: NOT_STARTED

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

Only enabled slots will be scheduled once M3 attaches the frozen 5s-crypto V1 signal engine.

The dashboard uses a mobile-first Chinese interface with four symbol tabs and displays total PnL across all four slots.

## Capital meaning

A slot's `capital_budget_usdt` is its maximum strategy margin budget, not the account's total balance.

Example:
BTC budget 100 USDT, leverage 5x:
- initial 60% stage = 60 USDT margin / about 300 USDT notional
- BUY-C top-up to 100% = 100 USDT margin / about 500 USDT notional

M3 must additionally verify real Binance available margin immediately before an order. Configured budgets do not reserve or transfer funds on Binance.

## Important M2.1 boundary

The START button currently persists the slot as `ARMED`; it does not yet run the frozen signal loop. M3 is the only milestone allowed to attach automatic strategy execution.

## Testnet

Use environment variables only:
`FIVES_MODE=TESTNET`
`BINANCE_TESTNET_API_KEY`
`BINANCE_TESTNET_API_SECRET`

LIVE remains unsupported in this round.


## K-line boundary contract

5s crypto V1 is not bound to a 24-hour/day boundary.

For every Strategy Slot:
- the selected timeframe defines the strategy bar;
- only a **completed** selected-timeframe K-line is evaluated;
- the currently forming K-line is excluded from confirmed signal calculation;
- once a bar closes, its signal is confirmed;
- any resulting action is executed on the **next K-line of the same timeframe**;
- changing 15m -> 1h changes the bar boundary, not the frozen signal formulas.

Formal runtime contract:
`SELECTED_TIMEFRAME_BAR_CLOSE_TO_NEXT_SELECTED_BAR_OPEN`
