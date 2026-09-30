# March–June 2025 Data Provenance

Run date: 2026-09-28

## Equities

Primary repository:
`Devesh176/Replicating_portfolio`

| Symbol | Blob SHA |
|---|---|
| ABT | e9071f4a01e8f50cdab0155b0779ef09ef85e1d4 |
| AAPL | 5b722f4ab77fe3dad0afc4d83163c16732bca352 |
| AMZN | 8103be5ce8a065e2f753a4738b4b74a35361b291 |
| ORCL | 09ac3f0ada8c73f16758a0ef34b5afaa327a9a1c |
| INTC | 1e6b806f9c86dfc3d6e45eb87384b4e816bef442 |
| MSFT | ff6c2f3fe35add1a815855badf4ec4dc221aa86c |
| NVDA | 0181202463fd062000e23d332c04ac486bd25e9a |
| GOOGL | 8af3a5f957af8c8efd7f3f24fb6d6b34d7af9027 |
| META | 7c4a6dfe89f68a96491fafd8b326e4e1cfcc915b |
| JPM | 448829ca757707e1720562977314fbca879510e6 |
| XOM | 5fdf45e182d2e8d589fe368de8cdccf26fa173a1 |

ARM:
- retained in Discovery universe
- not included in this run because only weekly public summaries were verified during this pass
- weekly data are insufficient for the daily Source-XMA engine

## Crypto

Primary repository:
`yanniedog/binance-historical-OHLCV-data`

Binance spot USDT daily bars:

| Symbol | File | Blob SHA |
|---|---|---|
| BTC | BTCUSDT_1d.csv | 47e67d38c79af08d446aa9b8d8d2fb50369ff249 |
| ETH | ETHUSDT_1d.csv | f98393cb828b584b023ce1bee1cad6e07c14a038 |
| BNB | BNBUSDT_1d.csv | 0b7fcf1a5b31c1ff04f328ff2028afc29ca7b179 |
| SOL | SOLUSDT_1d.csv | e01b90746f5ac0e298a1f59eb6afd63db8a685d6 |

## Execution limitation

Primary execution model is `SAME_BAR_CLOSE_PROXY_V2`.

This correctly assigns the action to the current bar instead of mechanically delaying it one bar.

However, daily OHLCV cannot reveal the exact intraday minute when the full condition first became true.

Therefore:
- the same-bar close fill is an execution proxy,
- it is not an exact intraday replay,
- exact first-confirm execution requires intraday bars.
