# MatrixQuant R5 — PAI 极端高位后的真实趋势衰竭卖出研究（结果前冻结）
Date: 2026-10-09
Status: PROTOCOL_FROZEN / NO_TRADING_CHANGES
Baseline: R4 stock extreme 20-stock results branch HEAD ab753c9ad80a4bd6277488ddb0fbea5b50b3eff0. Prior round formally CLOSED, not silently reopened.
Hypothesis: PAI >85 in chart is a **warning**, not immediate exit; extra objective weakening might avoid early sell without merely losing exposure.
Data: exact existing three archived Twelve Data 1day OHLCV snapshots from prior stage (2018-01-02 to 2026-09-29, each 2197 bars, 20 prechosen U.S. stocks). Never pretend these are historical repo original full bars; previous round re-fetched them. Signal interval 2020-01-01 through 2026-08-31. Require 250-bar warmup and enough future bars. No additional stocks or timeframes. TDX PAI Stoch(14)+SMA3, STDP(C,21), stochastic of SD(14), scale 0..100. WT Laguerre gamma .08 and EMA 10/21 + signal MA4 as in R4. All color changes (blue middle, TOP RED, BOTTOM GREEN) are visual only; original Pine default PAI differs.
Top band PAI entering >=85 is baseline sell signal, not the fill activation condition (PAIraw >40 / normalized >70).

Freeze four comparator SELL event rules; all evaluated at current bar CLOSE and transact only next open:
- S0 TOP_ENTER: PAInorm>=85 AND prior<85 (same as R4).
- S1 PAI_DOWN80: PAInorm falls BELOW 80 after having reached >=85 in preceding 10 candles; current<80, previous>=80.
- S2 WT_BEAR: WaveTrend main crosses BELOW its signal, with a PAI>=85 top in preceding 10 candles; do NOT forward-fill future pivots.
- S3 PRICE_BREAK: current close BELOW the minimum LOW of prior five *completed* candles, with prior 10 candle top; trigger only on transition from not broken to broken (compare previous current against prior's five lows).
- S4 WT_AND_PRICE: PRICE_BREAK at present plus WT main<signal at present, and preceding10 top. S4 is a prespecified restrictive combined test only, no optimizing if rare.
20-bar within-event-class per-stock dedup, n/coverage and 5,10,20 day direction hit-rate, avg returns and MAE/MFE; split 2020–2023 vs 2024–Aug 2026 (later segment is *historical robustness*, NOT untouched OOS).
- PAI top episode timing audit: detect each TOP_ENTER, look forward up to 15 closed bars for the FIRST each S1..S4 confirmation; count confirmations, delay in bars, and opportunity cost from top+1 open to actual exit+1 open. This timing diagnostic is explicitly hindsight cohort analysis, not executable early exit.
- Long-only strategy: **same identical BUY condition** for all: first cross into PAI<=15 (R4 BUY). Compare sell S0..S4 and no-sell buy-hold benchmark. Cash flat, single full position, 0.15% per side costs, next-open execution, per-stock total return, max drawdown, trades, exposure, per-trade gross and net, median per asset and count beating raw S0. Compare results controlling for exposure caveat; no promotion solely from a return gain if drawdown worsens or no independent split stability.
- Exclude end-of-run forced liquidations from roundtrip win rate (mark to market only) and report open positions separately. No stop-loss or extra tuning.
- Quality gate: signal logic and indicator warmup checks; negative returns after events are *conditional direction rates*, not realized trade win rates; test counts for low sample groups. Explicitly disclose price adjustment, Pine parity and data source limitations.
- If no robust advantage, mark all tested sell rules REJECTED_FOR_PROMOTION, retain original source and old branch. No 5s/SSSS/server/live trading changes. One analysis cycle only, no infinite experiment.
