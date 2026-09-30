# SSSS Crypto Research Plan

Last updated: 2026-09-19

Purpose:
create a dedicated crypto research track for SSSS without mixing crypto and equity evidence.

## 1. Why separate crypto from equities

Crypto differs materially from US equities:

- 24/7 trading
- no overnight close/open boundary in the same sense
- fragmented venues
- exchange-specific candles and volume
- higher volatility
- spot and perpetual derivatives coexist
- funding / basis / open interest can matter
- no corporate-action adjustment problem, but venue integrity matters

Therefore:
crypto and equity results must be reported separately.

A rule that works on both may be called cross-asset only after both tracks validate independently.

## 2. Initial crypto universe

Stablecoins are excluded as traded assets.

### Core / Discovery assets

BTC
ETH
SOL
BNB

Reason:
already used in historical SSSS crypto work, therefore suitable for Discovery but NOT untouched validation.

### Fresh OOS candidates

XRP
ADA
DOGE
TRX

No occurrence of these symbols was found in the retained SSSS repository at the time this plan was created.

### Fresh Frozen OOS candidates

LINK
AVAX
LTC
BCH

No occurrence of these symbols was found in the retained SSSS repository at the time this plan was created.

Important:
the exact exchange / quote pair must be frozen before the first empirical crypto experiment.
For example BTC/USDT on one venue is not assumed identical to BTC/USD on another venue.

## 3. Data architecture

Preferred research adapter:
CCXT.

Requirements:
- record exchange id
- record spot vs perpetual
- record symbol
- record quote currency
- record timeframe
- record raw exchange timestamps
- record retrieval time
- record package version
- cache immutable raw OHLCV

Do not mix venues inside one official experiment stage unless the experiment is explicitly a cross-venue study.

## 4. Initial timeframe

First transfer test:
1D bars.

Reason:
the frozen SSSS core was developed as a daily-bar model.

Do not simultaneously change:
- asset class
- timeframe
- execution semantics
- core signal formula

After daily transfer is understood, test 4H as a separate experiment.

## 5. Crypto execution convention

Crypto trades continuously.

For a daily signal:
- signal is known only after the chosen venue's daily candle closes
- execute at the next tradable bar/open convention defined by the venue dataset

The daily session boundary must be explicit, preferably UTC 00:00 boundaries when using exchange-native daily candles.

Do not silently compare a UTC-day backtest with a different live session boundary.

## 6. Initial feature families

Use the same orthogonal Wave-1 features as equities:

- CMF20
- normalized OBV impulse
- RVOL20
- ER10
- CHOP14
- Squeeze state
- NATR regime

Crypto-only context added later:
- BTC state/context for non-BTC assets
- funding
- open interest
- basis

## 7. Cross-asset interpretation

Possible final classifications:

CROSS_ASSET:
validated independently in equity and crypto tracks.

EQUITY_SPECIFIC:
validated only in equities.

CRYPTO_SPECIFIC:
validated only in crypto.

UNSTABLE:
sign/relation reverses across tracks or OOS.

Do not average equity and crypto results into one score.

## 8. Planned experiment order

1. Build/review crypto OHLCV snapshots.
2. Audit base SSSS transfer on BTC/ETH/SOL/BNB.
3. Run orthogonal feature diagnostics on core crypto assets.
4. Freeze exact candidate rules.
5. Open XRP/ADA/DOGE/TRX OOS only after a rule is frozen.
6. Open LINK/AVAX/LTC/BCH Frozen OOS only after OOS passes.
7. Repeat selected candidates on equities independently.
8. Only then consider one unified cross-asset production rule.
