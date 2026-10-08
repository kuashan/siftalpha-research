# MatrixQuant R3 — TradingView/Pine numerical parity protocol and user export guide

**State:** OFFLINE_ENGINE_REGRESSION_PASS / EXTERNAL_TRADINGVIEW_PARITY_PENDING

Last source branch audited: `research/matrixquant-crypto-mtf-r2-20261008` HEAD `5bacf8e0123aec8ace8413064c4813f0d1f61d24`; main HEAD `d04ee21bbda3b45c467d384e966dd2d2c06fb1fe`. Work isolated on `research/matrixquant-pine-parity-r3-20261008`. No production changes.

## Authorship and source scope
- The user provided the complete **MatrixQuant Multi-Factor Reversal Analyzer** Pine Script v6. Original copyright header: `© MatrixQuant`; license header: **Mozilla Public License 2.0**.
- Original preserved without indicator logic changes in `ORIGINAL_MatrixQuant_Multi_Factor_Reversal_Analyzer.pine`.
- Instrumented copy `TV_PARITY_EXPORT.pine` changes **only** `indicator()` display title / precision and appends 14 `plot(..., display=display.data_window)` instrumentation columns. **Not** a new strategy; no order placement or parameter changes.
- This copy may be pasted into TradingView's Pine Editor. It has NOT yet been compiled on TradingView in this research session, since no authenticated Pine execution is connected; if any editor diagnostic occurs, capture verbatim rather than infer compile success.

## Default settings that must remain untouched for parity
- PAI: PriceSRC = close, LBlen=20, LBsmooth=3, DispMethod=Standard Deviation, DispLen=20, StraddleArea=5.
- PAI HTF mode **None**, Use HTF Repaint **false**.
- WaveTrend: WTchanLen=10, WTavgLen=21, Laguerre smoothing disabled; divergence source = Histogram.
- WT pivots left=5/right=1, min spacing=5/max=60; PAI pivots left=2/right=2, min=2/max=10.
- Regular divergence enabled; hidden divergence disabled.
- Important: the original PAI index plots normalized values, but numeric parity compares **PAIvalue raw** (roughly -100..100); otherwise a false discrepancy is guaranteed.
- WT uses the raw WTline / signal / histogram rather than the +100 / 2 plot normalization; plotting is affine and unchanged for pivots.

## User: export once (BTC 4h first, then BTC 1D)

1. In TradingView, open the BTC chart you actually use, e.g. `BINANCE:BTCUSDT`. Select **4 hours (4h)**. Do not enable Heikin-Ashi or transformed candles; use standard OHLC.
2. Open Pine Editor; **create a NEW script** (do not overwrite your original). Copy the full contents of `TV_PARITY_EXPORT.pine` from this repository branch. Add to chart. Keep the default inputs listed above.
3. TradingView chart top toolbar/menu → **Export chart data... / 导出图表数据** → export CSV. According to official TradingView docs, chart exports can include OHLC and values plotted by indicator scripts, including `display.data_window`.
4. Ensure exported CSV includes `time`, OHLC and columns **PARITY_PAI_RAW**, **PARITY_WT_RAW**, **PARITY_WT_SIGNAL_RAW**, **PARITY_WT_HIST_RAW** plus confirmed-flag columns.
5. Scroll left/load more bars before export; **at least 350 bars**, preferably **800+**. 250 bars are discarded as warm-up. Save CSV with name `BTCUSDT_4H_TV_PARITY.csv`. Repeat at 1D after this is accepted.
6. Supply CSV to the assistant; it can be checked against the TV-exported OHLC and uploaded/archived after provenance review. If exporting is unavailable, a few screenshots of the Pine data window can support only a **partial spot check**, never a complete parity PASS.

## Offline comparison

Prerequisite: Node.js (tested by GitHub Actions on Node 22).

```bash
node research/matrixquant_crypto_mtf_r3/compare_tv_export.js BTCUSDT_4H_TV_PARITY.csv
```

Creates `BTCUSDT_4H_TV_PARITY_PARITY_REPORT.json`. Uses **OHLC from that exact TradingView CSV**, not different Twelve Data or Binance candles, so venue data differences cannot masquerade as formula differences. Reports per-field counts, missing/mismatching bars and first discrepancies. Default absolute tolerance 0.0001 for numerics and strict 0/1 agreement for flags; optional `--warmup=250 --abs-tol=0.0001`.

**Acceptance for one CSV**: all 14 fields with >=100 compared bars after warm-up; zero numeric/flag discrepancies within tolerance. Check both 4h and 1D before any TradingView parity claim. Test other coins/timeframes only after base two pass; divergent TV chart sources require individually captured matching OHLC.
Watch for pivot equality/tie handling, `ta.ema/ta.sma` missing-data initialization, and source compiler corrections.

## Findings from source-vs-engine manual static audit

| Feature | Original Pine | R2 JS | Current judgment |
|---|---|---|---|
| PAI price stochastic | SMA3(ta.stoch(close,high,low,20)) -> (x-50)/50 | same expression | static alignment |
| PAI dispersion | ta.stdev(close,20), ta.stoch(disp,disp,disp,20) | 20-bar population std + stochastic | static alignment, TV numeric pending |
| PAI trade boundary | ta.crossover(value,5) / ta.crossunder(value,-5) | over/under at +5/-5 | static alignment |
| WT | hlc3, EMA10, EMA10 abs dev, EMA21, signal SMA4 | same operations | static alignment, TV numeric pending |
| WT histogram pivots | left5, right1; `valuewhen` and `barssince(pivotFound[1])` | prior pivot with `k - prev - 1` bars | static alignment, equal-pivot tie check pending |
| PAI pivots | left2, right2; range2..10 | not traded by the frozen R2 strategies | in R3 diagnostic only; requires TV check |
| Plot placement | `offset = -right` | flags at confirmation bar t | intentional correct causal timing, must match TV confirmed column |
| Trend Detector + Gold Zone | original script supports both | not implemented in R2 | **OUT OF SCOPE**, no parity claim |
| HTF/Laguerre/alternative dispersion | configurable in Pine | not implemented in R2 | default OFF only; no parity claim |

## Executed tests (not independent Pine parity)

GitHub Actions: **MatrixQuant R3 Pine Parity Offline Regression**, run `37776740385`, SHA `01ab0443e45fce67feebcf1089517715affe7128`, job `113309388534`, reported **SUCCESS**.

Tests: R2 full 16-series × 7-strategy replay from saved CSV snapshots unchanged (sampled scalar parity for three principal strategies across 16 series); synthetic exported CSV with 14 columns matches reconstruction; a corrupted numeric CSV column must be detected; right-side 1-bar pivot delay test; next-open execution, two-sided fee, no-trade tests. **No live TradingView/Pine values were available for this CI run.**

## Gate dispositions

- `SOURCE_RECOVERED=PASS`
- `SOURCE_PRESERVED_WITH_MPL_NOTICE=PASS`
- `R2_BRANCH_HEAD_RECHECK=PASS`
- `STATIC_DEFAULT_FORMULA_MAPPING=COMPLETE_WITH_CAVEATS`
- `R2_OFFLINE_REPLAY=PASS`
- `TV_EXPORT_INSTRUMENT=WRITTEN / COMPILE_UNVERIFIED`
- `TV_PINE_REAL_BAR_NUMERICAL_PARITY=PENDING_TV_CSV`
- `BINANCE_USDM_SOURCE_AND_FUNDING_PARITY=PENDING`
- `PRODUCTION_CHANGE=NONE`

**Next action:** obtain TradingView-exported `BTCUSDT_4H_TV_PARITY.csv` with the instrumented source; run full comparator and report mismatch counts before changing any model formulas or strategy thresholds.
