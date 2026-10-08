# MatrixQuant Multi-Factor Reversal Analyzer + PAI BUY/SELL v1

**Status: IMPLEMENTED (standalone indicator source); TradingView live compile/screenshot acceptance PENDING.**  
Based on the exact archived original `research/matrixquant_crypto_mtf_r3/ORIGINAL_MatrixQuant_Multi_Factor_Reversal_Analyzer.pine` at R3 HEAD `e16e21c5569678a3bb4a165879d91ab2b7b58230`.

## Delivered Pine indicator
- [MatrixQuant_MFRA_PAI_BUY_SELL_v1.pine](MatrixQuant_MFRA_PAI_BUY_SELL_v1.pine)
- Original MatrixQuant Pine v6 indicator formulas remain byte-for-byte unchanged aside from the display-only `indicator()` title and the **new appended signal block**. TradingView original script has been preserved separately and was not overwritten.
- Retains PAI, WT, Gold Zone, regular/hidden divergences and Trend Detector exactly as written by MatrixQuant. Author/license comment `© MatrixQuant` and `MPL-2.0` retained.
- Indicator stays `overlay=false`; only its new BUY/SELL `plotshape(..., force_overlay=true)` markers appear on the price chart; underlying indicator remains in its own pane.
- No 400-bar logging/table diagnostics included in this **clean signal version**. Those remain in the separate R3 parity-debug version.

## Final visual rules (long-side prototype; not short sell)
1. BUY: **current fully closed candle** `ta.crossover(PAIvalue, StraddleArea)`; the indicator default `StraddleArea=5` corresponds to raw PAI crossing above +5. Only show a BUY if the local **virtual** position is flat.
2. SELL: **current fully closed candle** `ta.crossunder(PAIvalue, -StraddleArea)`; default corresponds to raw PAI crossing below -5. Only show a SELL if the local **virtual** position is long.
3. A single `var bool MFRA_virtualLong` eliminates duplicate BUY markers before the next SELL and eliminates orphan SELL markers while flat. This local state is a **visual signal-tracking model**, NOT an execution fill or actual exchange/broker position.
4. `barstate.isconfirmed` prevents signal painting during an **unclosed** current candle. `offset=0` on each marker means no back-shifting. Marker sits on **signal confirmation candle** (BUY green below bar / SELL red above bar).
5. **Execution convention** remains: signal confirmed at current candle **close**; earliest simulated/real order timing is the **next candle open**. This indicator never sends orders.
6. Two `alertcondition()` conditions are exposed for TradingView alerts; set alert frequency to **Once Per Bar Close**.
7. Settings: `PAI 交易信号丨Trade Signals` → display tags / display on price candles. Turning off visual tags does not disable the underlying alerts; alerts must be configured separately in TradingView.
8. If PAI is already above +5 when the script is added, no backfilled BUY is invented. The visual virtual position begins flat and waits for the next confirmed positive crossover. Same for historical chart warmup.

## Scope and validation
- TradingView v6 official documentation confirms `plotshape(... force_overlay = true)` works with `overlay=false` indicator for showing new markers on price chart: https://www.tradingview.com/pine-script-docs/visuals/text-and-shapes/
- Source static audit: exactly **one indicator()** declaration; original PAI/WT/Gold Zone calculations unchanged; only title and appended signal/input/plotshape/alertcondition block differ.
- **Pine live compiler/run on user's TradingView chart not yet confirmed**. Do not label real TradingView compile PASS until user installs it and checks.
- Prior R3 400-bar TV source-Python parity test: raw PAI, WT numeric comparisons passed on BTC 4h; one unproven PAI bearish divergence discrepancy does **not** affect this signal version.
- Prior R2 crypto pilot found PAI slow long-only strategy research-worthy on some samples but volatile and not generally superior across timeframes; **no profit or deployment guarantee**.

**State:** `SOURCE_ADDED=YES`, `REAL_TRADING=NO`, `ORIGINAL_SOURCE_MODIFIED=NO`, `FREEZE_FAMILIES_UNCHANGED=YES`.
