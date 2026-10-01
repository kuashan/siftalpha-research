# 5s-crypto V1 · Binance USDⓈ-M Futures integration

Bounded execution-integration project for frozen `5s-crypto V1`.

## Status

- M1: CLOSED
- M1.1: CLOSED
- M2: **IMPLEMENTED_AWAITING_TESTNET_ACCEPTANCE**
- M3: NOT_STARTED
- M4: NOT_STARTED

## Install M2 dependency

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

Official SDK is pinned:
`binance-sdk-derivatives-trading-usds-futures==17.5.0`

## PAPER console

```bash
FIVES_MODE=PAPER python app.py
```

## Binance Futures Testnet acceptance

Provide credentials only as environment variables:

```bash
export FIVES_MODE=TESTNET
export BINANCE_TESTNET_API_KEY='...'
export BINANCE_TESTNET_API_SECRET='...'
python m2_testnet_check.py
```

To explicitly apply the frozen execution account settings on Testnet:

```bash
python m2_testnet_check.py --apply-account-settings
```

To perform the bounded Testnet order submit/cancel probe:

```bash
python m2_testnet_check.py --order-probe BTCUSDT
```

The script is hard-guarded against PAPER/LIVE authenticated use. M2 contains no production URL for authenticated mutations.

## Frozen boundaries

Universe:
BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT.

Product:
Binance USDⓈ-M perpetual futures.

Account semantics:
One-way + Long-only + Isolated.

Selectable intervals:
15m / 1h / 2h / 4h / 6h / 12h / 1d.

Validation boundary:
1d remains the validated 5s-crypto V1 baseline; sub-daily intervals remain experimental.

M3 cannot start until M2's real Testnet acceptance is CLOSED.
