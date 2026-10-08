# MatrixQuant R3: first actual TradingView Pine Logs audit (7 x BTC 4h bars)

**Result:** REAL_TV_LOG_RECEIVED / PARTIAL_INTERNAL_ARITHMETIC_PASS / INDEPENDENT_PINE_PARITY_PENDING

Input: user-pasted seven **real Pine Logs** lines, labeled `TVR3|`, UTC candles from **2026-10-01 20:00** through **2026-10-02 20:00**, each containing timestamp, OHLC, 4 indicator values, and 10 binary flags.

- [Unmodified received logs](user_tv_logs/BTC_4H_20261001_20261002_TVR3_7LINES.log)
- [Machine-readable seven-bar audit](user_tv_logs/BTC_4H_20261001_20261002_7LINE_AUDIT.json)
- [Offline longer-Pine-Logs numerical comparator](compare_tv_logs.js)
- [Exact preserved MatrixQuant formula](ORIGINAL_MatrixQuant_Multi_Factor_Reversal_Analyzer.pine)
- [Free Pine Logger](TV_PARITY_FREE_NO_EXPORT.pine)
- [Frozen 16-asset round 2](../matrixquant_crypto_mtf_r2/RESULTS.json)

## Verified on user-provided log lines

- Timestamp interval: all six adjacent gaps exactly 4 hours. No duplicated timestamps, no OHLC inconsistency.
- `WT histogram = WT raw - signal raw`: maximum absolute difference approximately **1e-8**, consistent with eight-decimal logging.
- `WT signal = SMA4(WT raw)`: four fully checkable rolling windows, maximum absolute difference approximately **2.5e-9**, consistent with rounding.
- `2026-10-01 20:00 UTC`: Pine `PAI_cross_above_5=1`; PAI +12.4257 and WT above its signal. An entry **would** be eligible on the following bar open, `2026-10-02 00:00 UTC`, price **84877.5**, if no prior position exists. The prior candle is absent, so the full crossing cannot be independently recomputed from this excerpt.
- `2026-10-02 16:00 UTC`: WT crosses beneath its 4-bar signal. If an open position exists, a WT-exit rule would execute on the **next** bar open, `2026-10-02 20:00 UTC`, price **84303.8**.
- Hypothetical PAI+WT candidate roundtrip described above: **-0.6759% gross**, **-0.9737% after assumed 0.15% per-side friction**. This is illustrative, not an observed trading fill.
- `2026-10-02 20:00 UTC`: raw PAI crosses below **-5** (from +17.2754 to -15.2101); any PAI-only exit is eligible at **2026-10-03 00:00 UTC** open, *not contained in the seven observations*.
- No WT or PAI bullish/bearish divergence confirmation events in these seven bars. Pivot confirmations are **not equivalent to divergences**. One WT pivot-high flag appeared at `2026-10-02 00:00 UTC`; one PAI pivot-high flag appeared at `2026-10-02 16:00 UTC`.

## Why this is NOT full TradingView-vs-JS parity

The full PAI and WT reconstruction needs rolling windows and EMA prior history. Seven OHLC rows cannot recreate initialized WT/PAI. Even passing histogram/SMA checks shows only **internal algebraic consistency**. The earlier R2 history came from Twelve Data `BTC/USD`, which is not the same chart source as Binance `BTCUSDT`; do not compare the provider's raw K lines as if they were identical.

## Next user handoff (free, no TradingView subscription)

1. In the existing Pine indicator settings, under `R3 Free Parity丨免费校验`, set **Confirmed candles in Pine Logs** from **40** to **400**. There is no need to change the script.
2. Reload/reapply the indicator, open Pine Logs and **copy all `TVR3|` records** (not the source code). Prefer saving to a plain `.txt` file and uploading that text file; pasted text is fine if complete. Keep the exact original UTC timestamp and the delimited `|` fields.
3. R3 checker can be run with `node research/matrixquant_crypto_mtf_r3/compare_tv_logs.js <user-logs.txt>`. It reads the chart OHLC from the same TV logs and compares **14 indicator/confirmation fields** after a 250-bar warmup. At least **350 consecutive TVR3 rows** are needed; 400 gives 150 comparison candles.
4. A successful full-data comparison does NOT validate exchange-order execution, slippage/funding, or trade profitability; it validates only this specific source's default PAI, WT, and divergence signal formulas.

## Tests

GitHub Actions `37782765027` at commit `df3df178bddf9d9983fc0af9d0c1e686087f2cbd`: **SUCCESS**. R2 replay and R3 source-static checks passed, along with Pine Logs parser tests (the real 7-row sample correctly rejected as insufficient, synthetic 520-row fixture matches all 14 fields, altered synthetic PAI value is detected). **No 350+ real TradingView bars were supplied yet.**

**Gate:** `PARTIAL_ALGEBRA_PASS`, `REAL_FULL_TV_PINE_NUMERIC_PARITY=PENDING_MORE_LOGS`; `PRODUCTION_CHANGE=NONE`.
