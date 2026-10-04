# SLTD V7 Multi-Strategy Binance USDM Demo v1 — Acceptance

Status: **IMPLEMENTED_AND_VERIFIED**

Branch:
`feature/sltd-v7-binance-usdm-demo-v1`

Verified functional HEAD after millisecond correction:
`300620fb734e8efed9a96ad55da5d5619005c6ce`

Base:
`feature/sltd-v7-multistrategy-overlay-v1@fbeb9063f5910887fb7ce547943abc85db99ae51`

Binance capability source:
`feature/5s-crypto-binance-usdm-v1@3290e345916337a663fc41370ac2f7407b6cc537`

Verification:
- Initial integration Run: **37191464884**
- Millisecond-contract verification Run: **37191649945**
- Compile V7 Binance modules: PASS
- Binance Demo foundation tests: PASS
- Existing multi-strategy regression: PASS

## Preserved strategy entries

Analysis/display:
- SLTD
- E
- 5s Stocks
- 缠论
- 顺势

Automatic Binance Demo execution:
- SLTD
- E
- 5s Stocks

Display/signal only:
- 缠论
- 顺势

## Binance Demo capabilities

- BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT
- Binance USDⓈ-M public candles
- Binance Demo authenticated trading
- API Secret kept in current Python process only
- server-time synchronization
- ONE_WAY
- ISOLATED
- configurable leverage
- configurable per-symbol budget
- deterministic idempotent clientOrderId
- reduce-only sells
- local filled-order ledger
- remote/local position reconciliation
- missed-bar blocking
- no historical order backfill
- manual stop
- emergency flatten
- unrealized PnL status

## Strategy ownership boundary

Each symbol has exactly one automatic strategy owner at a time.
The chart may still overlay multiple strategies.

Strategy switching is blocked while:
- symbol execution is active,
- strategy fraction is non-zero,
- Binance position is non-zero,
- or Binance has open orders.

## Live-start boundary

Starting a flat symbol baselines the current latest completed candle.
Historical signals are never replayed as new Binance orders.

## Crypto timestamp boundary

Binance `openTime` / `closeTime` remain **epoch milliseconds end-to-end** for
crypto bars, live strategy identity, scheduler/recovery state and deterministic
order IDs.

E XMA/higher-timeframe code converts milliseconds to seconds only transiently
when Python must construct a datetime for timezone/calendar bucketing; the
stored strategy `open_time` remains the original Binance millisecond value.

`SLTD_V7_BINANCE_USDM_DEMO_V1 = IMPLEMENTED_AND_VERIFIED`

## Millisecond correction closeout

The earlier provider-boundary conversion from Binance milliseconds to seconds was rejected.

Final rule:
- Binance crypto `openTime` / `closeTime`: native epoch milliseconds end-to-end.
- Scheduler/recovery baselines: milliseconds.
- Strategy bar identity: milliseconds.
- Deterministic clientOrderId signal identity: milliseconds.
- E XMA higher-timeframe grouping: preserves millisecond source identity.
- Only Python datetime calendar bucketing performs a temporary ms -> seconds conversion.

Verification Run **37191649945**: PASS.

`SLTD_V7_BINANCE_TIMESTAMP_CONTRACT = NATIVE_MILLISECONDS_VERIFIED`
