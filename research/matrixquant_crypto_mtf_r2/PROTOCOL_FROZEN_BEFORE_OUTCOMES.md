# MatrixQuant Crypto Multi-Timeframe Round 2 — Pre-registered protocol

**Status:** FROZEN_BEFORE_OUTCOMES  
Date: 2026-10-08  
Base study: `research/matrixquant_mfra_pilot_20261008`, inherited from `0fb2325970b70abd055ad32260479cf50f914a8f`.

## Universe and data
- Four independently evaluated crypto symbols: BTC/USD, ETH/USD, BNB/USD, SOL/USD.
- Native Twelve Data OHLC close/open/high/low (volume absent in the provider's crypto series); **spot-equivalent reference data**, not Binance USDⓈ-M futures/mark prices.
- 15min, 1h, 4h, 1day, each requesting up to the provider cap of **5000** most recent historical bars with end_date **2026-09-30**. The available effective date range differs by timeframe and coin and must be reported. No inference from daily bars to intraday bars.
- Preserve exact returned textual CSV snapshots separately for every symbol/timeframe on this branch, plus row counts. Reject duplicate timestamps, invalid high/low/open/close values, sort timestamp ascending. If provider response has an error or insufficient rows, report unavailable, no fabricated test.
- Exclude first 250 available bars as common warm-up (indicator calculations may begin sooner). Trade observation begins at index >=250; chronological 60%/40% split of remaining eligible observations for descriptive **early/late split**, NOT true untouched OOS, since rules were informed by previous pilot.
- No parameter search or rule modification after seeing this batch.

## Default indicator replication
- PAI: SMA3(Stochastic(close,high,low,20)); price momentum = (SMA3-50)/50. Dispersion = population stdev(close,20); dispersion Stochastic(stdev,stdev,stdev,20); PAI = product. Thresholds +5 and -5 **raw** (not plotted normalized units). No HTF mode, no repaint option.
- WT: HLC3; ESA EMA10, deviation EMA10(abs(hlc3-ESA)); CI=(hlc3-ESA)/(0.015*deviation); WT=EMA21(CI); WT signal SMA4(WT). No Laguerre.
- WT regular bullish/bearish divergence detected at pivot of WT histogram (WT - signal) with left=5,right=1; compare current indicator pivot to immediately prior same-type oscillator pivot, with preceding pivot spacing 5..60; compare corresponding price lows/highs. **Confirmation at t = pivot+right**; no backdated trading.
- This is an independent engine: requires additional numeric parity check against TradingView/Pine before any deployment.

## Fixed candidates (long only)
- **A / PAI_SLOW:** long at cross PAI above +5, exit when cross PAI below -5.
- **B / PAI_FAST:** same entry, exit when cross PAI below +5.
- **C / PAI_WT:** long when `PAI > +5 AND WT > signal` state first becomes true; exit when `PAI < -5 OR WT < signal`.
- **D / WT_WITH_PAI:** long on WT crossover above signal with `PAI > -5`; exit on WT crossunder below signal.
- **E / WT_BULL_CONFIRM:** same as C, but entry requires WT regular bullish divergence **already confirmed within the past 5 bars**; same exit as C.
- **F / PAI_BEAR_EXIT:** same entry as A; exit when PAI crosses below -5 OR a WT regular bearish divergence is confirmed (first matching condition).
- **G / PAI_WT_BEAR_EXIT:** same entry as C; exit when `PAI < -5 OR WT < signal OR WT bearish divergence confirmed`.

## Execution
- Signals evaluated **only at candle close**; execute at **next candle open**. One long position at a time, all-in capital 100% per independently evaluated coin. No same-bar exit+reentry. If still long on final candle, mark-to-market liquidate at final close.
- Initial equity US$10,000 **per symbol**, no capital mixing between coins. Zero leverage, no derivatives funding, no dividends, no borrowing.
- Baseline friction **0.15% per side** (combined assumed commission + execution slippage), plus 0.05% and 0.30% per-side sensitivity on A and C. Terminal liquidation also incurs friction.
- Compare buy-and-hold in each exact time window with the same friction. Drawdown marked at candle close. Report trades, win percentage, exposure, ending equity return and maximum equity drawdown. Also report event-only 20-bar diagnostics where full future horizon exists, with overlapping-event caveat.
- Primary evaluation: late 40% of each instrument/timeframe, benchmark vs buy-and-hold and vs A. Early and full-window values are descriptive only.
- Not a claim of OOS validation, universality, or profitability in a leveraged exchange account.

## Gates
1. Data-inventory PASS only after saved snapshots independently read back.
2. Engine self-checks (synthetic cases and correct lag) PASS required.
3. Pine parity remains PENDING without independent TradingView values.
4. Strategy promotion strictly prohibited in Round 2. No changes to 5s crypto/stocks or SSSS production sources.
