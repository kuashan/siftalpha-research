# MatrixQuant R6 — 原作者理论驱动的独立策略证伪（结果前冻结）
Date: 2026-10-09
Status: PROTOCOL_FROZEN_BEFORE_RESULTS / NOT_TRADING_APPROVED
Base audited R5 HEAD: 4fce721be80f96d48b9465f707ea0d9152cfcb65. R4/R5 CLOSED; do NOT alter.
Source: MatrixQuant original archived Pine source `research/matrixquant_crypto_mtf_r3/ORIGINAL_MatrixQuant_Multi_Factor_Reversal_Analyzer.pine` and author official https://www.tradingview.com/script/m82RL973/
Author's heuristics: Trend Detector direction (above50/rising bull; below50/falling bear), PAI trend/straddle state, WT momentum crossover, Gold Zone volatility compression. Distinguish directional following vs user's earlier contrarian top/bottom hypothesis, already rejected for promotion. Gold Zone alone is NOT buy.
Two fixed parameter sets:
- MODIFIED: PAI price stochastic 14, SMA3; population standard deviation CLOSE 21 and stochastic std 14; WT EMA10/10/21, four Laguerre stages g=.08 always ON, signal SMA4; Trend OHLC momentum 13, CLOSE momentum21; Gold 8/8 threshold30. This is the user's TDX translation.
- ORIGINAL: PAI stochastic20/SMA3, STD20 with stochastic20; WT EMA10/10/21, Laguerre OFF (source default g=.02 unused), SMA4 signal; Trend OHLC length8/CLOSE20; Gold8/8 threshold30.
Both use source expression Trend=(OhlcUpLine + OhlcStrength / CloseTrendLine + CloseStrength), not a four-score average. Exclude/flag invalid zero denominators (may be a problematic original feature).
NO lookahead. All signals only current candle CLOSE, transactions NEXT candle OPEN. daily close-to-close portfolio mark. Analyze 20 frozen Twelve Data 1day OHLCV archived in R4 batch01/02/03 with 2018..2026 coverage, 250-bar warmup, period 2020-01-01..2026-08-31.
Candidate market logic: long-only cash/long, no short, 100% cash invested if entry, back to cash if exit; enter once on newly true condition, exit once on newly true exit condition.
- A_PAI: enter PAIraw>+5 on first transition above; exit PAIraw<-5 (threshold baseline).
- B_PAI_TREND: enter PAI crosses>+5 and Trend>50; exit PAIraw<-5 OR Trend<50 (close-confirmed state; no bypass).
- C_ALIGN: enter on fresh all-aligned state (Trend>50, PAIraw>+5, WT main>signal); exit PAIraw<-5 OR Trend<50. WT determines entry but not premature exit.
- D_GOLD: enter when PAI crosses>+5, Trend>50 and rising, Gold<30 within previous five completed candles INCLUDING current confirmation; exit PAIraw<-5 OR Trend<50. NO Gold-only buy.
- E_WT_CROSS: enter on WT line crosses UP over signal with Trend>50 and PAIraw>+5; exit PAIraw<-5 OR Trend<50.
- F_SLOW_EXIT: enter fresh all-aligned state (as C); exit ONLY when Trend<50 AND PAIraw<-5 (conservative trend persistence exit).
No other thresholds, stop losses, risk knobs, sector-targeted tuning, model extensions or additional factors. A/B are intentional baselines; A was tested before in slightly different context but both parameter settings now re-evaluated under same archive.
Costs 0.15% one-way including assumed slippage; per-stock full cash/long simulation with no dividends, fractional shares, same-day pending order processed at next open; no rehypothecation, leverage or overnight costs. At final sample date, mark open position to market and assess exit cost, but exclude forced liquidation from completed round-trip win rate. Record per-stock compounded total return, maxDD from start equity (incl day mark), open-to-close trade win, number, exposure days, 5/10/20-bar event positive directional stats for entries (no fees), missed openings, buyhold.
Time segmentation:
Discovery window 2020-01-01..2023-12-29. Choose candidate using PREDECLARED rank priority: number of stocks beating contemporaneous exposure-matched buy-and-hold at same invested fraction (passive allocation of exposure proportion plus cash) then median excess return over that benchmark, then lower drawdown, then fewer trades. Exclude candidates with total completed exits <40 or zero entries on >=5 stocks in discovery.
Forward-era historical replication 2024-01-01..2026-08-31; **not pristine OOS**, because prior studies and user looked at market prices. Report ALL candidate results both windows, selected candidate unchanged; do not reselect afterwards. Compare A baseline, full buyhold, exposure-matched passive baseline. 20-stock median per asset is NOT a portfolio.
Threshold choice and model family were selected using author theory *before* reading R6 results. Results only one iteration, do not optimize on results.
Quality: archive raw batch file hashes/observations; assert no duplicates/nonpositive prices/outliers >45%; check source numeric logic on sample. Comparability caveat: modified TDX not independently validated vs TradingView on exact bars, corporate action adjustment and fee estimate uncertain; formal model promotion requires external untouched market OOS, instrument precision, corporate action parity and live simulator. Avoid false "probability" label.
Do not modify any existing indicators, SSSS/5s strategies, backend, servers, or live trading. If none replicates robustly, REJECT all and close.
