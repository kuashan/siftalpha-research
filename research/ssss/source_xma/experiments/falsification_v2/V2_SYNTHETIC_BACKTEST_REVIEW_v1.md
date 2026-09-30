# XMA Falsification v2 — Synthetic Trading Backtest Review v1

Status: **DEVELOPMENT RESULT REVIEWED / NOT OOS / NOT PRODUCTION AUTHORIZATION**

Date: 2026-09-28

## 1. Ordering / contamination check

Synthetic trading map was frozen before the portfolio result:

- map file: `V2_SYNTHETIC_TRADING_MAP_v1.md`
- map commit: `0c842346dd83a18cd5e73397e293321a278b1e08`

Backtest result was committed later:

- result file: `V2_SYNTHETIC_BACKTEST_v1.json`
- result commit: `f757b31e606c5e090c42e5b578e9c9f8b881c03b`
- result commit timestamp: 2026-09-28T06:22:59Z

Therefore this run does not have a return-first / rule-second ordering defect.

The entire 2020-2025 interval is nevertheless development-contaminated and is not OOS.

## 2. Portfolio result

Executable interval:

- source history: 2020-01-02 through 2025-12-30
- first invested date: 2020-06-09
- initial capital: $10,000
- final capital: $10,797.53
- cumulative return: +7.9753%
- CAGR: +1.3902%
- maximum drawdown: -30.9471%
- annualized Sharpe (rf=0): 0.1685
- positive-day rate: 40.41%

## 3. Trading intensity

- total entries: 2,054
- total exits: 2,054
- TREND_LONG entries: 1,727
- REBOUND_LONG entries: 327
- total absolute target-weight turnover: 931.43x
- average gross exposure: 71.31%
- average active positions: 3.96

Implementation cost assumption:
- 5 bps one-way on absolute target-weight turnover.

## 4. Annual returns

- 2020: +6.72%
- 2021: +6.50%
- 2022: -22.66%
- 2023: +20.02%
- 2024: +4.59%
- 2025: -2.09%

The development strategy was not consistently profitable year by year.

## 5. Benchmark comparison

SPY over the identical executable interval:

- open-to-open raw return: +114.63%
- after 5 bps entry + 5 bps exit: +114.41%

Synthetic v2 portfolio:

- +7.98%

Therefore the current forced trading translation of v2 research logic did not produce competitive historical portfolio performance relative to passive SPY exposure.

## 6. Interpretation

The answer to:

> "If we force the currently frozen v2 directional logic into a trading strategy, did it historically make money?"

is:

**YES, NOMINALLY — but only +7.98% cumulative over the tested executable interval.**

The more important answer is:

**NO, it did not demonstrate an attractive trading edge in this synthetic implementation.**

Reasons visible directly in the result:

1. very low CAGR (+1.39%);
2. large maximum drawdown (-30.95%);
3. weak Sharpe (0.17);
4. extremely high turnover;
5. two losing calendar years;
6. massive underperformance versus SPY (+114.41% net benchmark).

## 7. Governance consequence

Do NOT optimize the synthetic trade map on this same 2020-2025 window.

Do NOT reinterpret the +7.98% as validated v2 profitability.

This result is useful because it answers the trading-oriented development question before the formal sealed scientific experiment:

- current frozen directional hypotheses do not automatically translate into a strong portfolio;
- v2 scientific testing remains necessary;
- if formal H1-H14 do not validate, no attempt should be made to rescue this synthetic portfolio through post-hoc tuning.

Current status:

`SYNTHETIC_V2_TRADING_BACKTEST = NOMINALLY_PROFITABLE_BUT_NOT_COMPETITIVE`

`FORMAL_V2_SCIENTIFIC_EXPERIMENT = NOT YET AUTHORIZED / NOT OOS`
