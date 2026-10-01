# 5s-crypto V1 · Binance USDⓈ-M Futures integration

This directory is the bounded execution-integration project for the frozen `5s-crypto V1` research baseline.

## Current status

`M1 = CLOSED`
`M1.1 = CLOSED`

The console is intentionally PAPER-only at this stage. It does not accept or use Binance credentials and cannot place orders.

## Selectable K-line intervals

- 15m
- 1h
- 2h
- 4h
- 6h
- 12h
- 1d

The execution invariant is always:

`completed bar close -> next bar open`

Important validation boundary:
- `1d` = current validated 5s-crypto V1 research baseline
- all sub-daily intervals = selectable for PAPER/Testnet integration testing, but **experimental / unvalidated** until separately validated

## Run

```bash
python -m venv .venv
. .venv/bin/activate
python app.py
```

Open `http://127.0.0.1:8080`.

## Frozen deployment semantics

- Universe: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT
- Product: Binance USDⓈ-M perpetual futures
- Position mode: One-way
- Direction: Long-only
- Margin: Isolated
- Initial target: 60%
- W3 BUY-C confirmation target: 100%
- SELL-A/B/C: 0% target (full exit)

Leverage and timeframe are execution/configuration parameters. They do not alter the frozen BUY/SELL equations.

For a configured bot capital budget `B`, target fraction `f`, and leverage `L`:

`target_notional = B × f × L`

The futures wrapper changes risk mechanics relative to the unlevered research baseline; future performance must account for funding, liquidation mechanics, exchange fees, and actual fills.
