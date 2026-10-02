# SiftAlpha Market Data Boundary v1

Status: **IMPLEMENTED_BOUNDARY_V1**

## Frozen boundary

1. **Strategy（策略层）**
   - consumes normalized market bars / closed-bar state;
   - does not know Yahoo, Binance, Massive, Twelve Data or Tushare;
   - frozen strategy formulas are not modified when a provider changes.

2. **Market Profile（市场规则层）**
   - owns session / timezone / completed-bar semantics;
   - current profiles: CRYPTO 24/7, US equity, China A share;
   - provider choice must not redefine a market's K-line boundary.

3. **Provider（供应商层）**
   - fetches a complete requested window and converts it to the integration contract;
   - provider failure may fall through to the next provider;
   - bars from multiple providers MUST NOT be stitched into one strategy window.

4. **Router（行情路由层）**
   - routes by market, then provider priority;
   - future providers plug in here without strategy changes.

5. **Execution（交易执行层）**
   - API Key / Secret is only required for account reconciliation and order execution;
   - public market data + strategy signal calculation must keep working without credentials.

## Cache boundary

Any provider-backed cache must be isolated at least by:

`market + symbol + timeframe + provider`

A failed request for one symbol/market must never fall back to another symbol's cache.

## 5s crypto v1 adoption

This version adopts the boundary first for Crypto:

`Binance Public Market Data -> frozen 5s signal engine -> B/S chart markers`

is independent from:

`Binance authenticated account -> reconciliation -> order execution`

The existing frozen JS/Python signal engine remains unchanged.

## Deliberate non-scope for this version

- no Massive provider implementation;
- no Twelve Data provider implementation;
- no A-share provider implementation;
- no change to V7 or E strategy rules.

These are provider additions for later versions, not prerequisites for this boundary.

`SIFTALPHA_MARKET_DATA_BOUNDARY_V1 = IMPLEMENTED`
