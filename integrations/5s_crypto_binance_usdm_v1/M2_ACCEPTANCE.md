# M2 Acceptance

Status: **IMPLEMENTED_AWAITING_TESTNET_ACCEPTANCE**

Implementation date: 2026-10-01

## Implemented offline

The adapter is deliberately locked to `FIVES_MODE=TESTNET` for every authenticated read/mutation path.

Official dependency:
`binance-sdk-derivatives-trading-usds-futures==17.5.0`

Implemented endpoints/capabilities:
- exchange information
- selected K-line retrieval
- notional/leverage brackets
- current position mode
- change to One-way mode
- account balance
- position information
- current open orders
- query order
- change margin type to ISOLATED
- change initial leverage
- submit Testnet LIMIT BUY
- cancel Testnet order

## Real Testnet closure gate

M2 MUST remain open until a real Binance Futures Testnet account passes:

1. `FIVES_MODE=TESTNET`
2. credentials load without being logged
3. BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT exchange filters read
4. persisted selected timeframe returns K-lines
5. leverage brackets read for all four symbols
6. One-way account mode confirmed/applied
7. ISOLATED confirmed/applied for all four symbols
8. configured leverage confirmed/applied for all four symbols
9. balance / position / open-order reads succeed
10. a Testnet LIMIT BUY is submitted and canceled
11. no orphan open order remains

No claim of PASS is allowed before those authenticated checks occur.
