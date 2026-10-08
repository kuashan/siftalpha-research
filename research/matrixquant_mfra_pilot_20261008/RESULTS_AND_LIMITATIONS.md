# MatrixQuant Multi-Factor Reversal Analyzer — PAI / WT independent pilot

**Status:** PILOT_COMPLETED / NOT_VALIDATED_FOR_TRADING

**Run date:** 2026-10-08  
**Research source repository HEAD:** `d04ee21bbda3b45c467d384e966dd2d2c06fb1fe` (main)  
**Working branch:** `research/matrixquant-mfra-pai-wt-pilot-20261008`  
**Ticker-level result data:** [per_symbol_results.csv](per_symbol_results.csv) (return fields are ratios; e.g. 0.10 = +10%).

## 1. Provenance and hard limitations

- Audited GitHub research repository main and several research branches. The repository has historical research outcomes (including stock/crypto batch JSON and event ledgers), fetch utilities, and Twelve Data provenance, but **no verified repository-stored complete raw OHLCV bar archive** for rebuilding this unrelated Pine indicator. Do NOT claim the pilot used immutable bars recovered from GitHub.
- To make a new calculation possible, **re-fetched** daily bars from the connected **Twelve Data** source, which is also listed in existing SSSS research provenance. New fetches are not guaranteed byte-identical to earlier runs; snapshots and provider response hashes were not persisted.
- Requested range: 2018-01-01 through 2026-09-30; stock rows were 2018-01-02 to 2026-09-29 (2,197 each). BTC/BNB 3,195 bars, ETH 3,174 bars; SOL starts 2020-08-11 (2,242 bars).
- 20 US listed stocks: AAPL MSFT NVDA AMD ABT JNJ AMZN GOOGL META ORCL LLY JPM BAC GS WMT PG COST XOM CAT TSLA. Crypto: BTC/USD ETH/USD BNB/USD SOL/USD.
- No returned stocks had OHLC high/low consistency violations or absolute open-to-prior-close jumps >45%; this is **not** an adjustment / corporate action parity certification.
- Returned crypto daily bars **lacked volume**, so the original Trend Detector (which requires volume) was not tested.
- Provider-specific adjustments, dividend treatment, venue/crypto exchange, exact Pine indicator numerical parity, and source GitHub raw-data reproducibility have **not** been independently verified.
- Pure long-only spot-equivalent simplified model, not leverage, shorting, funding, borrow, margin, financing, stop-loss or portfolio rebalancing; no dividends credited. Do not map directly to Binance perpetual execution.
- This is a fresh standalone MatrixQuant investigation; no deprecated XMA branch rules were imported; 5s/SSSS frozen families were not modified.

## 2. Exact pilot logic

Reconstructed default **PAI** from Pine:
- price stochastic(close, high, low, 20), then SMA(3) normalized as `(stoch_sma3-50)/50`.
- dispersion = rolling population stdev(close,20); dispersion stochastic(stdev,stdev,stdev,20).
- PAI = price-momentum * dispersion stochastic, in approximately -100..100.
Reconstructed default **WT** from `hlc3` with EMA(10), EMA(10) absolute deviation, `(price-EMA)/(0.015*EMAdev)`, EMA(21), signal SMA(4). No Laguerre, no HTF.

- **PAI**: enter long when PAI crosses above +5; exit when crosses below -5.
- **PAI_WT**: enter on a fresh state of `PAI > +5 AND WT > signal`; exit whenever `PAI < -5 OR WT < signal`.
- **PAI_WT_DIV**: enter on a fresh state satisfying PAI_WT and a WT histogram *confirmed regular bullish divergence in the last five bars*; exit as PAI_WT. The WT pivot uses left 5, right 1 and prior-pivot spacing 5..60; price must make a lower low while oscillator makes a higher low. The signal time is the **confirmation bar**, not the plot's offset/back-painted bar.
- 100% of a synthetic $10,000 per symbol when long, otherwise cash. Buy or sell only at the **next bar open after the close-confirmed signal**, except the terminal open position is marked/closed at the last close.
- Combined friction **0.15% per side**, representing a test assumption for commission plus slippage (not a measured brokerage fee).
- Evaluate 2020-01-01..2026-09-30; additional separate 2024-01-01..2026-09-30 historical subperiod using indicators with earlier warm-up bars.
- Benchmark per symbol: buy once at the sample's first open and sell at last close with equivalent entry/exit friction. Buy-and-hold dividends excluded.
- Return, drawdown, turnover and exposure are computed **per asset**, not a pooled portfolio.

## 3. Cross-asset summary

*Percentages below are cumulative or median per-asset returns, **not annualized**; medians are not the returns of an executable equal-weight portfolio.*

| Asset group / period | PAI median | PAI + WT median | PAI + WT + divergence median | Buy-and-hold median | PAI beats BH | PAI+WT beats BH |
|---|---:|---:|---:|---:|---:|---:|
| Stocks 2020–2026 (n=20) | +85.4% | -6.4% | +3.7% | +216.5% | 0/20 | 0/20 |
| Stocks 2024–2026 (n=20) | +36.4% | +2.6% | +3.2% | +72.7% | 4/20 | 1/20 |
| Crypto 2020–2026 (n=4) | +6,736.4% | +1,792.3% | +14.3% | +2,633.6% | 4/4 | 1/4 |
| Crypto 2024–2026 (n=4) | +85.9% | +61.8% | +4.8% | +57.3% | 1/4 | 2/4 |

Full-period stock trade counts: PAI 669 exits (median exposure 58.4%), PAI+WT 1,569 exits (median exposure 28.7%), divergence model 95 exits (median exposure ~2.4%).  
Full-period crypto trade counts: PAI 155, PAI+WT 357, divergence 18.

Median stock maximum equity drawdown: PAI -39.2%, PAI+WT -38.6%. Median crypto: PAI -57.8%, PAI+WT -46.2%. **Comparative buy-and-hold drawdown and exposure-matched benchmarks not yet computed.**

## 4. Event-only diagnostic — subsequent 20-bar long return

At each **confirmed** signal, hypothetical return = close of bar t+20 / open of bar t+1 - 1, with enough future bars only. All overlapping event windows are retained; pooled samples are **not independent**, returns are **gross of trading friction**, and market drift was not removed. This diagnostic does not validate a trading system.

| Event | 20 stocks: events | Stocks mean 20-bar return | Stocks positive % | 4 crypto: events | Crypto mean 20-bar return | Crypto positive % |
|---|---:|---:|---:|---:|---:|---:|
| PAI crosses +5 | 1,131 | +1.86% | 57.65% | 257 | +8.67% | 55.25% |
| PAI crosses -5 | 941 | +1.90% | 56.85% | 272 | +1.07% | 50.00% |
| WT regular bullish divergence | 455 | +2.29% | 58.68% | 123 | +0.47% | 43.90% |
| WT regular bearish divergence | 717 | +2.27% | 61.92% | 183 | +3.63% | 52.46% |
| PAI regular bullish divergence | 222 | +2.91% | 62.61% | 66 | +1.67% | 57.58% |
| PAI regular bearish divergence | 399 | +1.95% | 54.89% | 108 | +11.21% | 59.26% |
| WT bull divergence + fresh composite confirmation | 96 | +3.59% | 68.75% | 17 | +7.56% | 58.82% |

Crucial observation: stock WT bearish divergence was **not** followed by a negative average return at 20 bars (+2.27%), so mapping every ▼ marker to mandatory sell is **not supported** by this pilot. The composite-with-divergence observation has small samples and tiny exposure, and cannot be claimed superior from these event averages.

## 5. Inferences / next test gates

1. For the **tested rules only**, the 20-stock full window decisively fails the buy-and-hold hurdle: 0/20 PAI and 0/20 PAI+WT outperformance. Do not promote as an equity production strategy.
2. 4/4 crypto PAI gains over buy-and-hold in 2020–2026, but only 1/4 beats holding in 2024–2026. This fragility prevents formal promotion.
3. WT overlay sharply raises trade counts while lowering market exposure; the lower return can partly reflect underexposure to rising markets. Benchmark against **exposure-matched passive or regime baselines**, not just buy-and-hold.
4. Neither the bullish nor bearish pivot marker should be equated to an immediate executable market order, particularly because the plotted markers are shifted back to their pivot bar.
5. There is **no true immutable event/OHLC artifact** or Pine-vs-reproduction parity test yet. Required before definitive quant conclusions: snapshot exact OHLCV, verify stocks' splits/dividends, align exchange definitions, compare indicator values and signal timestamps against TradingView Pine, test unmatched market regime periods and roundtrip costs.
6. Gold Zone and volume-dependent Trend Detector, staged BUY-A/B/C, and full sell-policy search were **not tested** here.

**Disposition: PILOT_COMPLETE / NOT_VALIDATED / NO_PRODUCTION_CHANGE.**
