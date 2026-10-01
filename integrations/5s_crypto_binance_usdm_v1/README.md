# 5s-crypto V1 · Binance USDⓈ-M Futures integration

This directory is the bounded execution-integration project for the frozen `5s-crypto V1` research baseline.

## M1 status

`M1 = CLOSED`

M1 is intentionally PAPER-only. It does not accept or use Binance credentials and cannot place orders. The M1 web console uses only the Python standard library.

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
- Strategy timeframe: 1d
- Position mode: One-way
- Direction: Long-only
- Margin: Isolated
- Initial target: 60%
- W3 BUY-C confirmation target: 100%
- SELL-A/B/C: 0% target (full exit)
- Signal known only after completed bar close
- Execution intent belongs to next bar open

Leverage is an execution parameter, not a strategy signal parameter.

For a configured bot capital budget `B`, target fraction `f`, and leverage `L`, the M1 preview uses:

`target_notional = B × f × L`

This futures wrapper changes risk mechanics relative to the unlevered research baseline; future performance must account for funding, liquidation mechanics, exchange fees, and actual fills.
