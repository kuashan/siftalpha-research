# MatrixQuant Crypto MTF Round 2 — Results and Validation

**Status: COMPUTED / R2_RESEARCH_CLOSED / NOT_VALIDATED_FOR_LIVE_TRADING.**
2026-10-08. The rule definitions were committed before outcomes: `dac2f8f6ae3e58b4ba5901a3b2eafb6f4308c147`. Prior research and SSSS / 5s production remain unchanged.

## Provenance / replay

- Sources: newly fetched Twelve Data BTC/USD, ETH/USD, BNB/USD, SOL/USD. Spot-equivalent provider symbols; actual exchange/venue not proven. **These are not archived Binance USDM candles**, and the original GitHub research supplied past results and fetch scripts, not an immutable raw OHLCV set to reuse.
- 16 individual, exact provider-response CSV snapshots frozen under [data/](data/), each with blob SHA, date bounds, counts and data quality in [RAW_SNAPSHOT_MANIFEST.json](RAW_SNAPSHOT_MANIFEST.json).
- Offline recomputation source: [backtest_engine.js](backtest_engine.js), run via `node backtest_engine.js` from this folder. Program writes `REPLAY_RESULTS.json` and `REPLAY_SUMMARY.csv`. The complete calculation result from the connected tool is [RESULTS.json](RESULTS.json), with comparison matrix in [SUMMARY.csv](SUMMARY.csv).
- 15min 5000 bars from 2026-08-08..09-30, 1h 5000 from 2026-03-05..09-30, 4h 5000 from 2024-06-18..2026-09-30, daily 2242–3321 bars from varying earliest dates up to 2026-09-30.
- 0 duplicate timestamps or invalid OHLC records across 16 snapshots; all 12 intraday datasets have no time-step gap. **ETH daily has 2020-11-13..14 and 2021-01-07..09 missing days**. The late daily assessment starts after those gaps.
- No cryptocurrency volume returned; the original volume-dependent Trend Detector was not evaluated. Gold Zone was not evaluated. Reconstructed PAI, WT and regular WT histogram divergence follow source formulas but **no independent TradingView/Pine value-by-value parity** has been performed. Ties and initialization remain potential parity risks.
- All prices used as source delivered, no leverage, futures funding, liquidations, margin, volume requirements, intrabar stops or hedging. A flat 0.15% all-in friction per side is a **test assumption**, not a broker quote.
- Each symbol starts with independent $10,000; long or fully in cash, 100% when long. Close-confirmed signals execute next candle open, terminal open positions at last close, with entry/exit friction.
- Initial 250 bars warm up the indicators, the remaining bars split 60% early and 40% late. Because prior Round 1 already used overlapping daily history, **this late split is not true untouched OOS**. Different timeframe late splits span different dates. All percentages below are cumulative nonannualized returns; median across four symbols ≠ executable portfolio return.

## 7 frozen rule versions

See [PROTOCOL_FROZEN_BEFORE_OUTCOMES.md](PROTOCOL_FROZEN_BEFORE_OUTCOMES.md) for full operational definitions.

- PAI_SLOW: PAI cross above +5 entry, below -5 exit.
- PAI_FAST: same entry, PAI cross below +5 exit.
- PAI_WT: new PAI > +5 and WT > signal state entry, PAI < -5 or WT < signal exit.
- WT_WITH_PAI: WT upcross signal with PAI > -5 entry; WT downcross exit.
- WT_BULL_CONFIRM: PAI_WT with bullish WT divergence confirmed in prior five bars.
- PAI_BEAR_EXIT: PAI_SLOW plus a confirmed bearish WT divergence as exit.
- PAI_WT_BEAR_EXIT: PAI_WT plus confirmed bearish WT divergence as exit.

## Summary — late segment only

### 15min — chronological late section from 2026-09-10 05:00:00

| Fixed rule | Median net return | Hold median | Outperform holding | Positive coins | Trades across 4 coins | Median exposure |
|---|---:|---:|---:|---:|---:|---:|
|PAI_SLOW|-6.6%|+6.8%|0/4|0/4|156|50.7%|
|PAI_FAST|-16.7%|+6.8%|0/4|0/4|255|32.8%|
|PAI_WT|-20.1%|+6.8%|0/4|0/4|309|24.5%|
|WT_WITH_PAI|-26.5%|+6.8%|0/4|0/4|401|30.4%|
|WT_BULL_CONFIRM|-1.6%|+6.8%|0/4|0/4|23|2.3%|
|PAI_BEAR_EXIT|-7.6%|+6.8%|0/4|0/4|199|36.2%|
|PAI_WT_BEAR_EXIT|-18.4%|+6.8%|0/4|0/4|314|21.5%|


### 1h — chronological late section from 2026-07-12 20:00:00

| Fixed rule | Median net return | Hold median | Outperform holding | Positive coins | Trades across 4 coins | Median exposure |
|---|---:|---:|---:|---:|---:|---:|
|PAI_SLOW|+22.5%|+38.5%|0/4|4/4|140|53.4%|
|PAI_FAST|+7.8%|+38.5%|0/4|4/4|245|34.7%|
|PAI_WT|-5.7%|+38.5%|0/4|0/4|305|25.1%|
|WT_WITH_PAI|-7.7%|+38.5%|0/4|0/4|380|30.5%|
|WT_BULL_CONFIRM|-2.1%|+38.5%|0/4|0/4|15|1.1%|
|PAI_BEAR_EXIT|+15.8%|+38.5%|0/4|4/4|186|35.1%|
|PAI_WT_BEAR_EXIT|-9.7%|+38.5%|0/4|0/4|309|21.1%|


### 4h — chronological late section from 2025-11-17 08:00:00

| Fixed rule | Median net return | Hold median | Outperform holding | Positive coins | Trades across 4 coins | Median exposure |
|---|---:|---:|---:|---:|---:|---:|
|PAI_SLOW|-32.3%|-16.3%|0/4|0/4|159|48.0%|
|PAI_FAST|-28.8%|-16.3%|0/4|0/4|231|31.1%|
|PAI_WT|-27.0%|-16.3%|0/4|0/4|283|22.0%|
|WT_WITH_PAI|-32.0%|-16.3%|0/4|0/4|336|25.7%|
|WT_BULL_CONFIRM|-1.3%|-16.3%|4/4|0/4|19|2.3%|
|PAI_BEAR_EXIT|-36.2%|-16.3%|1/4|0/4|190|32.5%|
|PAI_WT_BEAR_EXIT|-29.1%|-16.3%|0/4|0/4|288|20.1%|


### 1day — chronological late section from 2023-05-21

| Fixed rule | Median net return | Hold median | Outperform holding | Positive coins | Trades across 4 coins | Median exposure |
|---|---:|---:|---:|---:|---:|---:|
|PAI_SLOW|+142.9%|+123.8%|3/4|4/4|77|50.4%|
|PAI_FAST|+115.7%|+123.8%|3/4|3/4|122|33.8%|
|PAI_WT|+84.3%|+123.8%|2/4|4/4|159|24.2%|
|WT_WITH_PAI|+25.3%|+123.8%|1/4|3/4|202|27.1%|
|WT_BULL_CONFIRM|+4.8%|+123.8%|1/4|4/4|8|1.7%|
|PAI_BEAR_EXIT|+103.9%|+123.8%|3/4|4/4|96|31.5%|
|PAI_WT_BEAR_EXIT|+75.9%|+123.8%|2/4|4/4|160|20.3%|


## Per-symbol late returns and drawdown

|Timeframe|Coin|PAI slow|PAI fast|PAI+WT|PAI+bear exit|Hold|PAI max drawdown|
|---|---|---:|---:|---:|---:|---:|---:|
|15min|BTC/USD|-6.8%|-17.9%|-21.4%|-8.9%|+6.2%|-9.2%|
|15min|ETH/USD|-3.0%|-18.9%|-16.4%|-6.3%|+7.5%|-12.7%|
|15min|BNB/USD|-9.8%|-14.3%|-24.1%|-11.3%|+4.6%|-11.1%|
|15min|SOL/USD|-6.5%|-15.5%|-18.7%|-4.5%|+16.2%|-11.9%|
|1h|BTC/USD|+17.1%|+3.2%|-10.5%|+7.9%|+29.5%|-9.8%|
|1h|ETH/USD|+27.9%|+13.1%|-9.3%|+23.7%|+46.3%|-13.4%|
|1h|BNB/USD|+12.7%|+2.8%|-1.4%|+2.4%|+30.6%|-9.4%|
|1h|SOL/USD|+47.6%|+12.4%|-2.1%|+34.1%|+52.7%|-6.9%|
|4h|BTC/USD|-33.3%|-17.5%|-27.4%|-38.4%|-13.2%|-45.8%|
|4h|ETH/USD|-31.3%|-24.9%|-24.2%|-33.9%|-16.7%|-48.0%|
|4h|BNB/USD|-30.1%|-32.8%|-26.5%|-17.8%|-18.9%|-41.8%|
|4h|SOL/USD|-54.4%|-47.7%|-44.7%|-63.7%|-16.0%|-69.0%|
|1day|BTC/USD|+212.3%|+208.2%|+104.6%|+273.2%|+207.5%|-35.5%|
|1day|ETH/USD|+154.6%|+84.4%|+111.7%|+85.1%|+40.1%|-49.6%|
|1day|BNB/USD|+131.2%|+147.0%|+64.0%|+102.0%|+213.6%|-38.0%|
|1day|SOL/USD|+2.5%|-14.5%|+21.0%|+105.7%|-33.8%|-50.6%|

## Independent signal event diagnostics — following 20 candles

Event samples can overlap and gross 20-bar returns include background market drift. They do **not** represent conditional probability of a correct trading instruction. MFE and MAE separately available for every coin in RESULTS.json.

|Timeframe|Confirmed signal|Events|Gross mean following 20 bars|Positive following 20 bars|
|---|---|---:|---:|---:|
|15min|PAI_BUY|254|+0.1%|52.0%|
|15min|PAI_SELL|236|+0.1%|53.0%|
|15min|WT_BULL|98|-0.1%|53.1%|
|15min|WT_BEAR|121|-0.0%|43.8%|
|1h|PAI_BUY|242|+0.7%|57.4%|
|1h|PAI_SELL|209|+0.0%|49.3%|
|1h|WT_BULL|101|+0.3%|60.4%|
|1h|WT_BEAR|127|+0.6%|56.7%|
|4h|PAI_BUY|230|-0.3%|43.0%|
|4h|PAI_SELL|235|+0.5%|59.1%|
|4h|WT_BULL|103|+0.0%|46.6%|
|4h|WT_BEAR|102|+0.3%|45.1%|
|1day|PAI_BUY|118|+4.5%|61.0%|
|1day|PAI_SELL|136|+3.0%|52.2%|
|1day|WT_BULL|54|-0.2%|46.3%|
|1day|WT_BEAR|79|-0.1%|48.1%|


## Findings and interpretation

1. **15m PAI_SLOW loses in all four coins**, with 156 combined closed trades in the late ~20-day segment. Under 0.15% per-side cost: BTC -6.84%, ETH -2.99%, BNB -9.79%, SOL -6.45%. Under 0.05%: +0.93%, +4.68%, -2.27%, +0.94%; under 0.30%: all negative from -13.47% to -20.01%. The apparent behavior is highly cost-sensitive.
2. **1h PAI_SLOW earns profits in all four**, but 0/4 beats same-window buy-and-hold. PAI_WT is negative in all four. Its added WT filter raised churning and made performance worse in this sample.
3. **4h PAI_SLOW and PAI_WT both lose in all four coins** during the late section beginning 2025-11-17. The underlying market also fell but the strategies did not protect capital sufficiently. WT_BULL_CONFIRM does beat negative buy-and-hold in 4/4 by staying mostly in cash (only ~2.3% median exposure), not by proven tradable alpha.
4. **1day PAI_SLOW beats buy-and-hold in 3/4 late sections** (BTC, ETH, SOL; not BNB), yet drawdown is still large: BTC -35.5%, ETH -49.6%, BNB -38.0%, SOL -50.6%. Not acceptable as an unmodified leveraged USDM system.
5. **PAI_BEAR_EXIT daily** improved BTC (PAI +212.3% -> +273.2%) and SOL (+2.5% -> +105.7%) but worsened ETH (+154.6% -> +85.1%) and BNB (+131.2% -> +102.1%). A universal sell rule is **not** supported.
6. Confirmed **WT bearish divergence is not invariably an immediate SELL**: pooled 1h bearish divergence n=127, following 20-bar gross mean return +0.60%, 56.7% positive.
7. The optimal timeframe cannot be inferred from these tables alone: 15m / 1h / 4h / 1day late sections sample different calendar regimes; no duration-matched or exposure-matched control in this round.
8. Full-market return is not sufficient: numerical parity, venue authenticity, funding/friction, stop/liquidation risk, and genuine OOS are still unverified.

## Audited gates and disposition

- `RULE_PROTOCOL_FROZEN_BEFORE_CALC=PASS`
- `RAW_DATA_PRESERVED_IN_GITHUB=PASS (16/16, git blob SHA manifest)`
- `OHLC_QUALITY=PASS with disclosed ETH daily gaps`
- `EXECUTION_SYNTHETIC_TEST=PASS (next-open, both sides fee, no signal=no trade)`
- `RESULTS=COMPUTED (16 series, 7 rules, 28 cross-asset summary rows)`
- `INDEPENDENT_PINE_PARITY=PENDING`
- `BINANCE_USDM_PROVIDER_PARITY_AND_FUNDING=PENDING`
- `TRUE_UNTOUCHED_OUT_OF_SAMPLE=PENDING`
- `AUTOMATED_TRADING_DEPLOYMENT=NOT_AUTHORIZED`

**R2 final status: RESEARCH_COMPUTED / NOT_PROMOTED.** The next meaningful gate is verification of a per-bar TV/Pine comparison (BTC 4h + daily), then a venue-native dataset and calendar-period-matched comparison before any more rule selection. Do not modify 5s/SSSS frozen baselines or reinterpret this as a validated live system.
