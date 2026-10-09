# MatrixQuant 改良 PAI 顶底区：20 美股首轮可复现研究结论
Date: 2026-10-09
Status: EVENT_STUDY_COMPUTED / LONG_ONLY_BACKTEST_COMPUTED / TRADE_EDGE_UNPROVEN / NO_PRODUCTION_CHANGE

## Fixed inputs and audit lineage
Protocol: PROTOCOL_FROZEN.md, commit 9125c6ef11deb7aaf7be4eaa504e29537172e04d
Source: user's TDX-translated modified MatrixQuant PAI Stochastic14 SMA3 with STDP(close,21) and stochastic14 of dispersion; normalized PAInorm=(PAIraw+100)/2. Current chart background colors are display-only; see frozen protocol for semantic distinction.
Data: 20 prespecified US stocks, 2018-01-02..2026-09-29, 2,197 OHLCV bars per stock, 43,940 total. Signal horizon 2020-01-01..2026-08-31, 33,480 evaluable symbol-dates. Twelve Data **re-fetched** snapshots raw_batch_01..03.json stored in same research branch, NOT assumed to equal earlier repository runs. No independently certified split/dividend adjustment or user-TDX per-bar parity.
Run code: run_stock_extremes.js
Machine-readable result: RESULTS_REPRODUCIBLE.json
Historical events: signal at bar close and observation from next bar open, 5/10/20 subsequent close; hypothetical transaction strategies trade next open, 0.15% one-way friction. Event direction hits exclude fees; event windows overlap, use 20-bar within-event class dedup as primary. 2024-2026 is a robustness subperiod, not pristine OOS.

## Semantics of top and bottom colors
Original Pine top fill activated by PAIraw>40 (PAInorm>70), physically drawn at panel y85..100. It does NOT mean PAI line itself is above 85. Original bottom fill activated by PAIraw<-40 (PAInorm<30), physically drawn at y0..15. PAI line genuinely *inside* drawn top band when PAInorm>=85 and bottom band when PAInorm<=15.
The user changed colors top to green, bottom to red in TDX; the mathematical activation remains unchanged.
Opposite-direction signal assumptions: bottom entry -> BUY hypothesis, top entry -> SELL hypothesis. No empirical claims about true future probability from right-hand 90%/99% labels.

## Main event-study outputs (nonoverlapping 20 bars per symbol and signal)
Benchmark any-date: 1,680, 5-day positive 57.14%, 20-day positive 57.08%, mean20 +2.06%.
PAI first <=15: 406 buy events; next 5-day positive 59.36%, next 10-day positive 61.58%, next 20-day positive 58.62%, mean20 +1.86%, avg20 MFE +8.72%, MAE -6.78%.
PAI first >=85: 585 hypothetical sell events; next 5-day NEGATIVE 39.66%, next 10-day negative 41.20%, next 20-day negative 40.68%, mean20 LONG +2.20%. Hence NOT reliable standalone sell.
PAI first below20: 455 bottom buy events; 5-day up 58.24%, 20-day up 57.36%.
PAI first above80: 637 top hypothetical sell events; 5-day down 41.92%, 20-day down 42.54%.
Bottom revisit exit-up20 after <=15 in preceding ten bars: 413 events; 5-day up 54.48%, 20-day up 55.21%.
Bottom confirmation + WT main>signal: 61 events; 5-day up 50.82%, 20-day up 55.74%.
Bottom confirmation + Gold<30 sometime in preceding 10 bars: 164 events; 5-day up 54.27%, 20-day up 56.71%.
Bottom confirmation + Trend rising: 337 events; 5-day up 53.41%, 20-day up 53.71%.
Top revisit cross-down80 after >=85 in preceding ten bars: 588 events; 5-day down 42.18%, 20-day down 43.37%.
Top confirmation + WT main<signal: 194 events; 5-day down 47.42%, 20-day down 45.88%. Conditional 2020-2023 had 20-day down 51.38%, but 2024-2026 only 38.82%: NOT stable.
All averages from RESULTS_REPRODUCIBLE.json (not independent verification of the modified version's parity to TradingView).

## Time segmentation
Early 2020-2023: first bottom <=15 n253; 5-day up 57.71% vs any-date 58.33%; 20-day up 57.71%.
Late 2024-2026: first bottom <=15 n153; 5-day up 62.09% vs any-date 52.65%; 20-day up 60.13%. This is an inconsistent conditional edge, not robust to time.
Early first top >=85 n351: 5-day down 37.61%, 20-day down 39.89%.
Late first top >=85 n234: 5-day down 42.74%, 20-day down 41.88%.
No fill/PAI combo proves >50% future-down sell probability. Top is best treated as potential *attention* condition, not a mandatory sell.

## Trading-simulation check (each asset independently, 2020..2026, +0.15% per side)
Naive buy first <=15, sell first >=85: median cumulative per-asset return +82.54%; median buy-and-hold +218.53%; 1/20 assets beat own buy/hold; 277 completed exits; median maximum drawdown -34.56%; median invested time 39.25%.
Confirmed buy crossing up 20 after extreme, confirmed sell crossing down80 after extreme: median return +91.75%; benchmark median +218.53%; 1/20 assets outperform; 278 exits; median MDD -34.06%; median exposure 40.26%.
Same confirmed pair conditioned on WT direction at the confirmation candle: median return +26.58%; benchmark +218.53%; 1/20 assets outperform; 42 exits; median exposure 18.88%.
These medians are not the return of an executable equal-weight 20-stock portfolio. Buy-and-hold is much more invested so comparison should also be exposure-matched before economic promotion. Dividends excluded and TDX/Pine parity not independently certified.

## Verdict
Finding: User's hypothesis that PAI entering the bottom drawn band implies stronger short-term rebound is plausible but limited; 2020-2023 does not beat benchmark in 5-day directional win rate. No robust/precise buy confirmation yet.
Finding: User's symmetrical upper-band SELL hypothesis fails this test; strong bull trends remain high and often appreciate.
Finding: Filtering by WT/Gold/Trend does not materially improve consistently, and reduces opportunity count/exposure.
No proven buy/sell rule for automatic order execution. Freeze exploratory investigation here, no threshold-fitting or adding more factors based on these same results. If asked for a next phase, prioritize paired risk/exposure matching and independent unseen-market validation after resolving modified TDX/Pine per-bar parity.
No modifications to existing 5s, SSSS, server, trading engine, or live orders.
