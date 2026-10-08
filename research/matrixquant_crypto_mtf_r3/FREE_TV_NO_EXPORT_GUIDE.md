# Free TradingView alternative — no chart CSV export needed

**Status:** IMPLEMENTED_AS_DIAGNOSTIC / TRADINGVIEW_RUNTIME_NOT_YET_VERIFIED

Use [TV_PARITY_FREE_NO_EXPORT.pine](TV_PARITY_FREE_NO_EXPORT.pine) in your *own, unpublished* Pine Editor script (Pine Logs are intended for personal scripts).

## Quick steps (free account)

1. Open TradingView BINANCE:BTCUSDT, **4h**, normal candles.
2. Create a **new** Pine indicator and **replace ALL editor text**, including the default sample `indicator()` declaration, with the linked script. There must be only one `indicator()`. Do not append to the previous code.
3. Save and add the script to chart. The indicator pane should have a compact **R3 table** of the latest 8 **confirmed** candle timestamps (UTC), PAI raw, WT raw, WT signal, and WT/PAI confirmed bullish/bearish divergence booleans (1/0). If no table appears, capture the exact Pine compiler/runtime error.
4. Take a full-resolution screenshot **including chart ticker, timeframe and table** and share it for an **initial spot-check**. Screenshots do not count as complete per-bar parity evidence.
5. For more precise numbers without a paid CSV plan, open Pine Editor **More (...) → Pine Logs**; the script writes the latest **40** confirmed historical bars by default. Each line has a `TVR3|` delimiter, UTC timestamp, chart OHLC, PAI, WT, signal/histogram, pivot flags and divergence-confirmation flags. If your browser allows selecting/copying messages, paste them as text; **do not share credentials**.
6. To collect more samples, change the **R3 Free Parity → Confirmed candles in Pine Logs** setting from 40 to up to 500. Full per-bar parity requires enough candles for JS warm-up (250) and a matching data source. If the logs cannot be copied, don't try to purchase anything; use the table screenshot as a limited inspection and leave the full parity gate pending.

## Critical constraints

- Only visual diagnostics / logs are added to original PAI and WT formulas, not trading rules; the script has a single `indicator()`.
- Pine logs are created **once per confirmed candle** near the chart's last bar (`barstate.isconfirmed`, `bar_index >= last_bar_index - FreeParityBars`); no variable-offset history loop is used. This prevents the prior error `requested historical offset (36) ... buffer limit (35)` without changing original indicator logic. The script skips the earliest 250 warm-up bars.
- Chart symbol matters: BINANCE BTCUSDT != Twelve Data BTC/USD. A screenshot of TV values cannot be compared naively to a different provider's last-bar values. For numeric comparison use OHLC copied from the **same** TV log records.
- Even after matching numeric PAI/WT samples, Pine-computed historical signal offsets and engine execution timing require explicit parity validation before any strategy promotion.
- The fallback was generated and audited statically in GitHub. It has **not** been compiled in a live TradingView account by the assistant; share any displayed errors as-is.
- Do not touch the frozen SSSS/5s crypto live strategies.

## Runtime fix record (2026-10-08)

- Version: same `TV_PARITY_FREE_NO_EXPORT.pine` URL, now updated in-place.
- Root cause: last-history-bar log loop requested offset `[n]` up to the user-selected candle count; the runtime had allocated a smaller 35-bar buffer.
- Fix: log each currently closed candle directly (`time`, `open`, `high`, `low`, `close`, raw indicator and confirmed flags), filter by `last_bar_index`, and retain the small on-chart table. Avoid script-wide `max_bars_back=500` allocation.
- Regression: GitHub Actions runs `test_free_no_export_source.js` with frozen R2 replay; **CI success is static/regression evidence, not a live Pine compile/runtime PASS**.
- User action: select ALL code in Pine Editor and replace it with the latest complete file; do not append to a previous script. If the error persists, send the exact bar/line error.
