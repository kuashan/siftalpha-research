# Round 3 — Real TradingView BTC 4h 400-bar independent parity audit

**Date:** 2026-10-08  
**Gate state:** CORE_PAI_WT_NUMERIC_PARITY_PASS / WT_SIGNAL_PARITY_PASS / PAI_BEAR_DIVERGENCE_SINGLE_EXCEPTION / NO_TRADING_PROMOTION

## Immutable evidence
- [Original 400-row user-provided TradingView Pine Logs CSV](user_tv_logs/BTC_4H_20260802_20261008_TV_400_REAL.csv). SHA-256 of original uploaded CSV (bytes in container): `67a32e2f35ff65634029c63b13cc682acfe473de48cf50a7a165797ed8f21c30`. CSV header `日期,消息`; `TVR3|` records are UTC and the external log prefix uses +08:00.
- Data: **BINANCE:BTCUSDT 4h as per user chart context**, symbol not independently encoded inside log records. Candles 2026-08-02 20:00 UTC to 2026-10-08 08:00 UTC, 400 continuous 4h bars, 0 duplicate timestamps, 0 invalid OHLC.
- Indicator input: same chart TradingView OHLC (not Twelve Data), Pine default PAI = Stochastic20 SMA3 × STD20 Stochastic20, WT EMA10/EMA21, signal SMA4, normal regular divergences.
- Exclude **250** initial bars to make EMA initialization and rolling window values comparable; **150 bars** evaluated against 14 Pine diagnostic fields = **2,100 field-bar comparisons**.

## Results: tolerance `abs_error <= 0.0001` for four numerical fields; exact boolean event flags otherwise

| Diagnostic | Compared bars | Mismatches | Max numerical absolute error or TV positive events |
|---|---:|---:|---|
| PAI raw | 150 | **0** | max 4.984e-9 |
| WT main | 150 | **0** | max 2.253e-8 |
| WT signal | 150 | **0** | max 2.360e-8 |
| WT histogram | 150 | **0** | max 6.234e-9 |
| WT pivot low | 150 | 0 | 12 events |
| WT pivot high | 150 | 0 | 17 events |
| WT bullish regular divergence | 150 | 0 | 1 event |
| WT bearish regular divergence | 150 | 0 | 2 events |
| PAI pivot low | 150 | 0 | 15 events |
| PAI pivot high | 150 | 0 | 17 events |
| PAI bullish regular divergence | 150 | 0 | 0 events |
| **PAI bearish regular divergence** | 150 | **1** | TV=0, JS=1 at 2026-09-20 00:00 UTC |
| PAI cross above +5 | 150 | 0 | 4 events |
| PAI cross below -5 | 150 | 0 | 5 events |

**2,099 / 2,100** field-bar records match. That number is an agreement rate only, **not the probability a trading signal is profitable**. The 1 remaining miss means full 14-field parity is **not** a PASS.

## Reproducibility and source audit

1. Independent Python reconstruction computes `PAI, WT, signal, histogram, pivots, divergences, breakout flags` from the same 400 OHLC values. It found no numerical mismatches after the common 250-bar warmup.
2. An initial stricter-than-Pine pivot implementation yielded 2 PAI pivot-high discrepancies on **2026-09-14 00:00** and **2026-09-25 16:00**. Both involved equal-value PAI plateaus, not price inputs. Correcting to Pine's **last-on-plateau** tie convention fixes both without changing the original indicator.
3. On **2026-09-20 00:00 UTC**, Pine exports `PARITY_PAI_PIVOT_HIGH_CONFIRMED=1`, `PARITY_PAI_BEAR_CONFIRMED=0`; the JS/Python reconstruction infers regular bearish divergence `1`. The preceding pivot and price oscillator comparison meet the straightforward classical divergence conditions, but the exact Pine condition calls `PAIinRange(PAIpivotHighFound[1])`, internally using `ta.barssince()` under a short-circuited `and`. Pine v6 can evaluate local history-dependent calls inconsistently unless executed on every bar. **This is a plausible hypothesis, not proven root cause**; verify with targeted Pine component tracing if that PAI divergence is ever used in a trading rule. Official docs: https://www.tradingview.com/pine-script-docs/errors/CW10003/ and https://www.tradingview.com/pine-script-docs/language/execution-model/.
4. R2 fixed strategy family relied on PAI thresholds and WT and WT divergences, **not the separate PAI regular bearish divergence event**. Thus this exception does **not** directly change the tested R2 entry/exit signal definitions, but the BTC 4h parity observation cannot validate R2's other timeframes, other symbols, costs or futures execution.
5. Internal WT arithmetic independent of recomputation: histogram = WT-signal across all 400 rows within 1.01e-8; WT signal = SMA4(WT) within 7.51e-9 on rows where available.

## Continuous integration
- [400-real-bar + synthetic parity regression (GitHub Actions run 37784546439)](https://github.com/kuashan/siftalpha-research/actions/runs/37784546439): **SUCCESS**.
- `compare_tv_export.js` fixed its pivot tie behavior in R3 only, and `test_parity_checker.js` added plateau tie tests. `test_tv_pine_logs.js` tests the 400 real rows and requires exactly one known PAI bearish-divergence exception; rejects unexpected numerical/other event differences.
- **Original user MatrixQuant Pine Script unchanged. Frozen R2 backtest data, prior returns, SSSS and 5s trading code unchanged.**

## Disposition and next gate
- `SAME_FEED_OHLC_NUMERICAL_FORMULA_PARITY_150_BARS=PASS`.
- `WT_PIVOT_AND_REGULAR_DIVERGENCE_PARITY=PASS` for BTC 4h available sample.
- `PAI_THRESHOLD_CROSS_PARITY=PASS` for BTC 4h available sample.
- `PAI_BEAR_DIVERGENCE_PARITY=ONE_MISMATCH_UNEXPLAINED`.
- `REAL_WORLD_TRADING_EXECUTION_PARITY=PENDING`.
- `CRYPTO_OTHER_TIMEFRAMES_AND_COINS_PARITY=PENDING`.
- `TRADE_STRATEGY_PROMOTION=NOT_AUTHORIZED`.

Next logical task: targeted Pine diagnostics of `PAIoscLH`, `PAIdivPriceHH`, and `PAIinRange(PAIpivotHighFound[1])` at the known timestamp; test a version with globally precomputed `ta.barssince` while preserving original source separately. After that, verify at least BTC 1D or ETH 4h with fresh TV exported logs. Stop if user does not want further TV effort; do not infer full-market parity from one timeframe.
