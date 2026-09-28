# XMA Falsification v2 — Synthetic Development Backtest Report v1

Status: **DEVELOPMENT / CONTAMINATED / NOT OOS**

Date: 2026-09-28

Frozen trading translation:
- `V2_SYNTHETIC_TRADING_MAP_v1.md`
- map freeze commit: `0c842346dd83a18cd5e73397e293321a278b1e08`

The trading map was committed before portfolio returns were computed.

## Result

Development data:
- raw source window: 2020-01-02 through 2025-12-30
- first actual investment: 2020-06-09
- final date: 2025-12-30
- 39-stock shared capital pool
- long-only
- equal-weight active positions
- next-open execution
- 5 bps one-way turnover cost

Portfolio:

- initial capital: **$10,000.00**
- final capital: **$10,797.53**
- cumulative return: **+7.98%**
- CAGR: **+1.39%**
- maximum drawdown: **-30.95%**
- annualized Sharpe, rf=0: **0.17**
- positive daily-return rate: **40.41%**
- average gross exposure: **71.31%**
- average active positions: **3.96**

Trading activity:

- total entries: **2,054**
- total exits: **2,054**
- TREND_LONG entries: **1,727**
- REBOUND_LONG entries: **327**
- cumulative absolute weight turnover: **931.43x**

Annual portfolio return:

- 2020: **+6.72%**
- 2021: **+6.50%**
- 2022: **-22.66%**
- 2023: **+20.02%**
- 2024: **+4.59%**
- 2025: **-2.09%**

## SPY comparison

Over the identical executable interval:

- SPY raw open-to-open return: **+114.63%**
- SPY after 5 bps entry + 5 bps exit: **+114.41%**

Equivalent $10,000 SPY ending value is approximately **$21,441**.

The synthetic v2 portfolio ended at **$10,797.53**.

Therefore the frozen-map synthetic portfolio produced positive nominal return but very large relative underperformance.

## Interpretation

This development backtest does NOT show a usable trading edge.

The main reasons visible from the portfolio statistics are:

1. very low CAGR relative to equity-market opportunity cost;
2. maximum drawdown far too large for the achieved return;
3. Sharpe near zero;
4. extremely high turnover;
5. material failure in 2022 and another negative year in 2025;
6. large underperformance versus passive SPY despite average 71% market exposure.

This result must be retained.

It is not permissible to tune v2 thresholds, candidate variables, or hypothesis directions on this same development history merely to improve the portfolio curve.

## Scientific boundary

This is not the formal v2 H1-H14 scientific test.

It answers a different practical question:

> If the currently registered v2 directions are mechanically translated into one simple trading strategy, does that strategy look economically attractive on contaminated history?

Current answer:

**NO — nominally profitable, but economically weak and decisively inferior to SPY.**

The formal frozen v2 scientific experiment remains separate.
