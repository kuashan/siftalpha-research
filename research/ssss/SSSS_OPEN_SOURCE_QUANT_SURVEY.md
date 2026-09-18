# SSSS Open-Source Quant Strategy Survey

Last updated: 2026-09-19

Purpose:
extract reusable design ideas from mature open-source quant/trading projects without copying their reported backtest results or importing unvalidated rules into SSSS.

This is a source/research architecture document, not an experiment result.

## 1. Projects reviewed

### Freqtrade / freqtrade-strategies

Relevant design ideas:
- indicator pipelines are separated from entry/exit logic;
- informative higher-timeframe / reference-asset data can be merged causally;
- strategy optimization is explicitly treated as something that must be re-tested per pair, timeframe, and timerange;
- lookahead-analysis and recursive-analysis are first-class validation tools;
- example strategies commonly combine trend, momentum, volatility, and volume dimensions.

Examples found in the public strategy repository include:
- ADX + directional movement + SAR + momentum
- Bollinger Bands + MACD
- RSI / Stochastic / MFI combinations
- Supertrend ensembles
- rolling volume conditions
- multi-timeframe informative-pair context

Important warning:
do not copy Hyperopt-tuned parameter values into SSSS.

Sources:
- https://github.com/freqtrade/freqtrade
- https://github.com/freqtrade/freqtrade-strategies
- https://docs.freqtrade.io/en/latest/lookahead-analysis/

### Jesse

Relevant design ideas:
- multi-timeframe and multi-symbol strategies;
- explicit prevention of higher-timeframe lookahead;
- strategy logic, ordering, risk management, and metrics are distinct concerns;
- partial fills and multi-order entries are supported as execution concepts.

Source:
- https://github.com/jesse-ai/jesse

### QuantConnect LEAN

Most important architectural lesson:
separate:
1. Universe Selection
2. Alpha / signal generation
3. Portfolio Construction
4. Risk Management
5. Execution

This directly matches the lesson from E032/E033:
positive early marginal economics do not automatically imply a new alpha signal; some effects belong in position sizing or execution instead.

LEAN also exposes a broad indicator library including:
- ADX
- Aroon
- Choppiness Index
- Donchian Channel
- Hurst Exponent
- Kaufman Efficiency Ratio
- KAMA
- Keltner Channels
- NATR
- OBV
- CMF
- Bollinger Bands

Sources:
- https://github.com/QuantConnect/Lean
- https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/overview

### Microsoft Qlib

Relevant design ideas:
- feature libraries are grouped across distinct information families;
- train / validation / test segments are explicit;
- factor research uses many orthogonal feature types rather than repeated variants of the same moving-average idea;
- Alpha158 includes examples from momentum, volatility, regression fit, correlation, residual, and volume-weighted feature families.

SSSS should borrow this feature-family mindset without adopting a black-box model prematurely.

Source:
- https://github.com/microsoft/qlib

### Hummingbot

Relevant design ideas:
- alpha/controller logic is separated from executors;
- DCA, grid, TWAP, position executors, and triple-barrier risk controls are execution/risk components rather than alpha indicators;
- exchange connectors standardize different crypto venues.

This is important for the future crypto deployment architecture.

Source:
- https://github.com/hummingbot/hummingbot

### NautilusTrader

Relevant design ideas:
- same strategy implementation can be used in backtest and live environments;
- event-driven architecture;
- multiple venues and asset classes;
- execution / reconciliation differences between simulation and live are explicit.

SSSS Android production work should eventually preserve this principle:
research signal semantics should not change between backtest and live execution.

Source:
- https://github.com/nautechsystems/nautilus_trader

### Pandas TA Classic

Used as an implementation/reference library for candidate indicator formulas.

Relevant native indicators:
- Choppiness Index
- KAMA
- Supertrend
- Squeeze / Squeeze Pro
- CMF
- OBV
- VWAP / VWMA
- NATR
- Aroon
- Vortex
- entropy

Source:
- https://github.com/xgboosted/pandas-ta-classic

### CCXT

Preferred open-source crypto market-data / exchange abstraction for research tooling.

Relevant capabilities:
- common public/private exchange API
- fetchOHLCV
- market metadata
- funding-rate APIs where supported
- exchange-specific rate-limit handling

Source:
- https://github.com/ccxt/ccxt

## 2. What SSSS already has

SSSS already contains strong price/trend-structure information:

- fast DEMA band
- slow white band
- normalized fast-vs-slow separation
- dsep structural acceleration
- effective GREEN / GRAY / RED state machine
- ATR-based price-near-white logic
- causal next-open execution

Therefore another ordinary moving-average crossover is low priority.

## 3. Highest-priority orthogonal research families

### A. Volume / Flow — PRIORITY 1

Why:
SSSS currently uses almost no volume information.

Candidate features:

#### CMF20

Chaikin Money Flow over 20 bars.

Concept:
detect whether closes tend to occur toward the high or low of the bar, weighted by volume.

Research forms:
- CMF20 level
- CMF20 > 0
- CMF20 slope / change
- divergence between price progress and CMF progress

#### OBV normalized slope

Raw OBV is scale-dependent.

Prefer:

OBVImpulse10 =
(OBV[t] - OBV[t-10])
/
SUM(volume, 10)

This is approximately scale-normalized and bounded by the signed-volume construction.

Research forms:
- sign
- magnitude bucket
- divergence vs price

#### Relative volume

RVOL20 = volume / rolling_mean(volume, 20)

Do not use absolute volume thresholds across assets.

Research forms:
- breakout with elevated RVOL
- quiet pullback followed by RVOL expansion
- volume exhaustion after mature trend

Potential SSSS use:
- OPEN quality context
- early Mature-vs-Failure discrimination
- crypto breakout confirmation

### B. Trend Efficiency / Choppiness — PRIORITY 2

Goal:
distinguish directional progress from noisy back-and-forth motion.

#### Kaufman Efficiency Ratio

From the KAMA construction:

ER10 =
abs(C[t] - C[t-10])
/
SUM(abs(C[i] - C[i-1]), 10)

High ER:
movement is directionally efficient.

Low ER:
movement is noisy/choppy.

Why attractive for SSSS:
two trades can have the same dsep / band state while one progresses efficiently and the other repeatedly mean-reverts.

#### CHOP14

Choppiness Index:

100 * log10(
SUM(TR_1, 14)
/
(HH14 - LL14)
)
/
log10(14)

Lower values = more directional.
Higher values = more choppy.

Do not assume textbook thresholds are valid for SSSS.
First use continuous / bucket diagnostics.

#### ADX14

ADX is common in open-source strategies and may still be useful as a diagnostic.

Priority below ER / CHOP because it is more closely related to directional trend strength already represented by SSSS.

### C. Volatility Compression / Release — PRIORITY 3

#### Bollinger / Keltner Squeeze

Default open-source implementation concept:
- Bollinger Bands 20 / 2
- Keltner Channels 20 / 1.5
- squeeze ON when Bollinger lies inside Keltner
- squeeze OFF when Bollinger expands outside Keltner

Why potentially useful:
SSSS knows structural band location but does not explicitly label volatility compression/release.

Potential uses:
- avoid weak breakout inside unresolved compression
- identify release after compression
- classify high-quality early continuation

#### NATR

Normalized ATR allows volatility comparison across stocks and crypto prices.

Prefer rolling percentile / relative change rather than one global absolute threshold.

### D. Multi-Timeframe Context — PRIORITY 4

Important:
the previous hard 2D MTF filter was rejected.

Therefore future higher-timeframe information must NOT automatically become a mandatory gate.

Use as:
- diagnostic context
- interaction feature
- sizing context

Candidate examples:
- daily SSSS signal with weekly / 3D trend-efficiency context
- daily crypto signal with 4H / 1D agreement
- altcoin signal with BTC reference-market regime

Freqtrade/Jesse design shows that informative higher-timeframe/reference-asset data can be handled without lookahead when aligned correctly.

### E. Crypto Market Context — CRYPTO-SPECIFIC

For altcoins, BTC is a market-context candidate.

Potential context features:
- BTC effective state
- BTC ER / CHOP
- BTC 20-day return
- asset return minus BTC return
- asset volatility relative to BTC

These must be treated as context features first, not hard filters.

Later derivatives-only layer:
- funding rate
- open interest
- basis
- liquidation / order-flow features

Do not mix these into the first OHLCV transfer round.

## 4. Lower-priority / likely redundant indicators

Lower initial priority:
- ordinary EMA/SMA crossovers
- MACD
- Supertrend
- KAMA line crossover itself
- PSAR
- generic Aroon/Vortex direction signals

Reason:
they mainly restate trend direction already heavily represented by the current SSSS price structure.

They may still be useful later as:
- independent robustness checks
- risk/exit context
- adaptive smoothing alternatives

but should not be the first new feature family.

## 5. Architecture rule adopted from open-source review

Going forward keep these layers distinct:

1. Universe
2. Alpha / signal
3. Position sizing
4. Risk management
5. Execution
6. Data / venue adapter

An effect found in one layer must not be mislabeled as another.

Examples:
- E033 early second-unit economics may be position sizing, not alpha.
- Hummingbot-style triple barriers belong to risk/execution research.
- BTC regime for altcoins is market context, not automatically an entry rule.

## 6. Validation rule adopted from open-source review

In addition to existing pre-registration:

- maintain strict causality
- add a lookahead-bias audit for every new derived feature
- record warm-up requirements per indicator
- avoid full-series aggregations without rolling windows
- preserve provider / venue identity
- compare backtest and paper/live signal timestamps before production
- use fixed static data snapshots for experiment reproducibility

## 7. Proposed research sequence

### Wave 1 — Orthogonal feature diagnostics

Price-independent / less-redundant:
- CMF20
- normalized OBV impulse
- RVOL20
- ER10
- CHOP14
- Squeeze state
- NATR20 relative regime

Goal:
measure whether these features separate Mature vs Failure paths and improve incremental-return maps.

### Wave 2 — Exact rules

Only after Wave 1:
convert at most a few diagnostic relationships into exact causal rules.

Then run:
Discovery -> OOS -> Frozen OOS.

### Wave 3 — Crypto context

Test:
- BTC regime context for altcoins
- asset-vs-BTC relative momentum
- venue robustness

### Wave 4 — Position sizing and risk

After alpha/context work:
- volatility-normalized sizing
- staged position sizing
- triple-barrier diagnostics
- drawdown / exposure constraints

Do not optimize allocation percentages before the signal/context frontier is stable.
