# MatrixQuant 股票 PAI 极端区研究 — 结果前冻结协议
Date: 2026-10-09
Status: PROTOCOL_FROZEN / READ_ONLY_TRADING
Source: research/matrixquant_crypto_mtf_r3/ORIGINAL_MatrixQuant_Multi_Factor_Reversal_Analyzer.pine
Derived display: user's TDX MyLang formula in conversation, PAI Stoch14/SMA3, STDP(close,21), STD stochastic14; WT EMA10/EMA10/EMA21/SMA4 with Laguerre gamma0.08; Gold RSI8. Color-only tweaks are non-signal.
IMPORTANT: The original Pine defaults are DIFFERENT (PAI 20/3/20 and Laguerre disabled); do not mix original default results with this user's modified indicator. Original Pine explanatory descriptions are hypotheses, not verified trade triggers.

Data: Twelve Data 1day stocks (same provider used in prior MatrixQuant pilot), refetch 2018-01-01..2026-09-30 for 20 prespecified stocks AAPL MSFT NVDA AMD ABT JNJ AMZN GOOGL META ORCL LLY JPM BAC GS WMT PG COST XOM CAT TSLA. Record provider and data timestamps; repository previous experiments do NOT contain auditable full OHLCV snapshots. If rate limits prohibit all 20, label subset honestly. Use 2020-01-01..2026-08-31 signal period; 2018-2019 warmup; final 20 bars reserved for outcome. Data adjustedness not fully certified. Event-based close confirmation, next session open hypothetical execution.

Source semantics: top fill activated when PAIRAW>40 (display PAI>70), drawn on y85..100; bottom fill when PAIRAW<-40 (PAI<30), drawn on y0..15. 'PAI inside colored fill' top means PAI>=85; bottom means PAI<=15. Do not equate fill ON with PAI inside its graphic area, and do not use actual display colors as features.

PREDECLARED tests:
- reference all eligible timestamps.
- low fill-on (PAI<30), low-inside (PAI<=15), first inside low (prior >15), enter PAI below20, exit PAI above20.
- high fill-on (PAI>70), high-inside (PAI>=85), first inside high (prior <85), enter PAI above80, exit PAI below80.
- directional 5/10/20 trading-day returns (close bar t+H / open t+1 -1), same-sign hit rates for buy/up and sell/down; MFE/MAE over next20. Gross of fees, overlap caution. For nonoverlap event-level, skip any within 20 of last same-class event *per stock*.
- Confirm-first candidate low: having PAI<=15 within previous 10 bars, current PAI crosses back ABOVE 20 (prev<=20); high reverse having >=85 within 10 bars, current PAI crosses back BELOW 80.
- Contrasts: candidate raw vs confirmed, confirmed + WT state (WT main>signal for buy / <signal for sell), confirmed + Gold (Gold<30 for buy, not preselect for sell), confirmed + Trend slope (TRENDVAL today > prior for buy / < prior for sell). These are TESTS, not automatic promotion. WT/Gold/Trend must be recreated from user's modified formula with strict zero guards, and numerical TV parity of modified variant is NOT independently certified.
- Execution-level long-only round trips: flat -> next-open BUY on confirmed-low, long -> next-open SELL on confirmed-high. Test one fixed candidate pair and raw pair, all-in with 0.15% side friction. Compare equity return, max drawdown, number of trades and buy-hold, including risk exposure; no optimizing thresholds after results.
- Unseen segment analysis 2024..2026 as a temporal robustness check (NOT pristine OOS since user viewed historic charts and hypotheses).
- No automated trading approval from event study alone; 5s/SSSS/production untouched; no new threshold tuning without separate authorization.
