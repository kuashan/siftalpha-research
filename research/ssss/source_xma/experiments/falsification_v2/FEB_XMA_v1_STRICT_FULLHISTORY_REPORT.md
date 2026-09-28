# FEB_XMA_v1 Strict Full-History Report

Status: **CLOSED — STRICT HISTORICAL REPLAY COMPLETE**

Date: 2026-09-29

## Executive answer

The original Source-XMA / FEB_XMA_v1 idea can make money in the frozen
39-symbol development universe in nominal aggregate terms, but this replay
does **not** support the stronger claim that it is a stable broad-market
trading edge.

Strict result for 39 independently funded $10,000 sleeves:

- Initial aggregate sleeve capital: $390,000.00
- Final aggregate sleeve capital: $430091.40
- Cumulative return: **10.28%**
- CAGR: **1.65%**
- Max drawdown: **-4.50%**
- Annualized Sharpe: **0.72**
- Positive symbols: **23/39**
- Mean sleeve return: **10.28%**
- Median sleeve return: **6.51%**
- Average target exposure: **11.26%**
- Average actual gross exposure: **11.25%**

The top five winners contribute approximately **83.31%** of
the total net dollar profit. The result is therefore highly concentrated.

SPY passive buy-and-hold over the same 2020-01-02 to 2025-12-30 window,
using 5 bps adverse entry and exit slippage:

- $10,000 -> $21212.94
- Cumulative return: **112.13%**
- CAGR: **13.37%**
- Max drawdown: **-34.10%**
- Annualized Sharpe: **0.71**

This is not an exposure-matched benchmark: FEB_XMA_v1 averages only about
11% exposure while SPY is continuously invested. It nevertheless shows that
the original FEB logic did not capture a large share of the available
buy-and-hold wealth creation.

## 1. Why this report supersedes the earlier +12.00% development replay

The repository previously contained a legacy full-history result:

- cumulative return: +12.00%
- CAGR: +1.91%
- Max DD: -4.69%
- Sharpe: 0.76

Integrity audit found that all three old replay batches already moved on
2020-01-06 even though the source series begin on 2020-01-02 and the raw
ADKBY-E slow structure requires REF(...,20).

That means the old replay allowed activity before the slow regime could be
defined. The most likely failure was treating missing regime as "not BEAR".

The old result remains preserved as development history, but is not the
strict answer.

The corrected implementation explicitly treats missing regime as NOT_READY
and does not trade until required inputs exist.

## 2. ABT January calibration

ABT 2025-01 remains a valid calibration success.

Recovered formulas reproduce the original five signal dates:
- 2025-01-15 probe;
- 2025-01-16 confirm;
- 2025-01-21 breakout/add;
- 2025-01-28 reduce;
- 2025-01-30 exit.

Original January sizing:
30% -> 70% -> 100% -> 70% -> 0%

reproduces:
$10,000 -> $11,345.49 (+13.45%).

Frozen FEB_XMA_v1 sizing:
25% -> 65% -> 100% -> 70% -> 0%

on the same signals/execution prices gives approximately:
$10,000 -> $11,329.76 (+13.30%).

So the January discovery itself was real under the recovered mechanics.

However ABT over the complete 2020-2025 strict replay is:
- total return: **-11.12%**
- CAGR: **-1.95%**
- Max DD: **-15.95%**
- Sharpe: **-0.34**

A successful January therefore did not generalize into a profitable six-year
ABT strategy.

## 3. Aggregate annual returns

| Year | FEB_XMA_v1 | SPY buy-and-hold |
|---|---:|---:|
| 2020 | 0.06% | 15.50% |
| 2021 | 2.37% | 27.04% |
| 2022 | -2.95% | -19.48% |
| 2023 | 2.12% | 24.29% |
| 2024 | 5.00% | 23.30% |
| 2025 | 3.46% | 17.16% |


FEB_XMA_v1 had one negative aggregate calendar year (2022), but the positive
years were generally small. Low average exposure explains part of the low
absolute return, but does not by itself establish incremental alpha.

## 4. Best and worst sleeves

Best five:
1. AVGO: 88.47%
2. AMD: 82.84%
3. ORCL: 75.24%
4. NVDA: 49.37%
5. META: 38.09%

Worst five:
1. AMZN: -28.96%
2. MCD: -24.66%
3. TMO: -24.25%
4. BA: -20.18%
5. KO: -17.86%

Net aggregate profit is $40091.40.
The top five winners contribute about $33400.48, or
83.31% of that net profit.

This concentration is one reason not to describe the strategy as broadly
stable.

## 5. Per-symbol metrics

| Symbol | Total Return | CAGR | Max DD | Sharpe | Trades | Avg Target Exposure |
|---|---:|---:|---:|---:|---:|---:|
| AAPL | 16.27% | 2.55% | -12.15% | 0.50 | 328 | 10.20% |
| MSFT | -8.11% | -1.40% | -16.86% | -0.18 | 351 | 11.43% |
| NVDA | 49.37% | 6.92% | -19.09% | 0.71 | 392 | 12.20% |
| AMD | 82.84% | 10.59% | -9.49% | 0.88 | 409 | 13.43% |
| AVGO | 88.47% | 11.15% | -17.49% | 0.86 | 392 | 14.30% |
| ORCL | 75.24% | 9.81% | -9.78% | 0.87 | 394 | 13.90% |
| INTC | -5.84% | -1.00% | -35.35% | 0.00 | 277 | 8.57% |
| QCOM | -4.93% | -0.84% | -25.87% | -0.04 | 321 | 9.11% |
| MU | 32.32% | 4.78% | -30.37% | 0.47 | 379 | 12.58% |
| GOOGL | 11.63% | 1.85% | -12.49% | 0.31 | 342 | 10.93% |
| META | 38.09% | 5.53% | -9.52% | 0.73 | 313 | 12.15% |
| NFLX | 22.30% | 3.42% | -23.05% | 0.34 | 413 | 14.46% |
| AMZN | -28.96% | -5.55% | -34.73% | -0.63 | 351 | 11.53% |
| TSLA | 25.17% | 3.82% | -29.43% | 0.31 | 363 | 9.70% |
| HD | -6.80% | -1.17% | -15.71% | -0.18 | 331 | 9.60% |
| MCD | -24.66% | -4.61% | -31.14% | -0.88 | 386 | 12.78% |
| WMT | 6.51% | 1.06% | -13.88% | 0.21 | 384 | 12.87% |
| COST | 11.34% | 1.81% | -12.32% | 0.36 | 368 | 11.69% |
| PG | -15.88% | -2.84% | -16.48% | -0.64 | 340 | 10.15% |
| KO | -17.86% | -3.23% | -18.37% | -0.57 | 350 | 10.81% |
| PEP | -2.49% | -0.42% | -8.34% | -0.09 | 324 | 8.93% |
| ABT | -11.12% | -1.95% | -15.95% | -0.34 | 295 | 8.68% |
| LLY | 22.63% | 3.46% | -11.27% | 0.42 | 425 | 14.52% |
| UNH | 1.02% | 0.17% | -7.94% | 0.06 | 326 | 10.43% |
| JNJ | 2.90% | 0.48% | -10.86% | 0.14 | 328 | 10.35% |
| TMO | -24.25% | -4.53% | -33.46% | -0.75 | 313 | 8.85% |
| JPM | 17.00% | 2.65% | -10.26% | 0.46 | 327 | 11.39% |
| BAC | 4.96% | 0.81% | -8.95% | 0.14 | 326 | 11.77% |
| GS | 20.64% | 3.18% | -20.40% | 0.48 | 356 | 11.74% |
| V | -4.56% | -0.78% | -12.20% | -0.13 | 356 | 11.87% |
| MA | 7.53% | 1.22% | -6.89% | 0.25 | 351 | 12.47% |
| CAT | 11.60% | 1.85% | -19.50% | 0.32 | 367 | 12.83% |
| BA | -20.18% | -3.69% | -29.92% | -0.37 | 347 | 10.03% |
| GE | 20.07% | 3.10% | -10.01% | 0.45 | 320 | 11.71% |
| XOM | 6.83% | 1.11% | -12.01% | 0.20 | 342 | 9.46% |
| CVX | -0.46% | -0.08% | -22.64% | 0.02 | 352 | 10.15% |
| LIN | 14.95% | 2.35% | -8.44% | 0.46 | 360 | 12.42% |
| NEE | -7.10% | -1.22% | -19.00% | -0.14 | 297 | 9.91% |
| PLD | -5.57% | -0.95% | -15.36% | -0.15 | 334 | 9.29% |


Full annual per-symbol returns are persisted in:
`FEB_XMA_v1_STRICT_PER_SYMBOL_METRICS.csv`.

Full daily equity/event ledgers are persisted in the strict batch JSON files.

## 6. Trading activity

Across 39 sleeves:
- probe executions: 5543
- confirmations: 667
- independent breakouts: 425
- breakout adds: 320
- reductions: 707
- exits: 5956
- terminal liquidations: 12
- total executions: 13630

## 7. Shared $10,000 portfolio

Status:
**BLOCKED_BY_PORTFOLIO_ALLOCATION_RULE**

FEB_XMA_v1 defines independent symbol targets but does not define a
cross-symbol ranking rule when simultaneous desired positions exceed 100%
shared gross exposure.

A shared-capital replay would therefore require a new portfolio-allocation
rule. No such rule was invented in this study.

The per-symbol sleeve result is the correct historically comparable answer.

## 8. Research conclusion

Question:
"Does the earliest Source-XMA / FEB_XMA_v1 logic make money on the larger,
longer dataset?"

Answer:
**Nominally yes in equal-funded sleeve aggregate, but not in a way that
demonstrates stable broad profitability.**

Evidence:
- aggregate +10.28% over roughly six years;
- CAGR only 1.65%;
- 16/39 symbols lose money;
- median sleeve earns only 6.51% total;
- top five winners generate about 83.3% of net profit;
- ABT itself is negative over the full six-year replay despite the strong
  January 2025 month;
- SPY buy-and-hold earns about 112.13% over the same
  period.

This does not mean Source-XMA geometry is useless. It means the frozen
FEB_XMA_v1 mapping is not supported as a standalone stable production
strategy by this broader historical replay.

Do not tune FEB_XMA_v1 after seeing this result. Preserve it as the earliest
mechanical baseline.

## 9. Reproducibility chain

ABT reproduction audit commit:
`8734bae3ca6029b2892f9138ba2bfe19d3c8bfd2`

Legacy full-history integrity audit commit:
`2eb827e8d06124c740c6e3e1681d88cd2d7aa848`

Strict implementation freeze commit:
`9e0e81af515fdc619be405f2884f07dc7920ad2a`

Executable engine commit:
`9b2aaf5769bc0fff49b85c164c9fb5c7465be6b6`

Strict aggregate results commit:
`2694f2ee1b84d1a28b229bb10bbeee289a2f0439`

Per-symbol CSV commit:
`3b8a4c3116b82a7c4db9d8b5ebdf97350b692894`

Closure:
`FEB_XMA_v1_STRICT_FULLHISTORY = CLOSED`
