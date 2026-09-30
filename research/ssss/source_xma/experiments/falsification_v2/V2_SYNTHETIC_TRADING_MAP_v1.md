# XMA Falsification v2 — Synthetic Trading Map v1

Status: **PRE-RETURN DEVELOPMENT MAP / FROZEN BEFORE BACKTEST**

Date: 2026-09-28

Purpose:
translate the already-registered v2 directional hypotheses into one deterministic
development-only trading rule so we can answer:

> If the current v2 logic were forced into a trading strategy, did it historically make money?

This is NOT the v2 scientific hypothesis test and is NOT production authorization.

No historical portfolio return was inspected before this mapping was committed.

## 1. Development window

Use already contaminated historical data only:

- 2020-01-02 through 2025-12-30
- never eligible for future sealed-window status.

Signals begin only when every required feature for that symbol/date exists.

## 2. Universe

Frozen 39-equity v1/v2 universe.

Shared capital pool only.

No independent $10,000 sleeve per symbol.

## 3. Execution

- signal calculated using close-t information;
- target portfolio executed at next trading-day open;
- long-only;
- maximum gross exposure = 100%;
- uninvested capital remains cash at 0%;
- all active positions equal-weighted;
- no leverage;
- no shorting;
- 5 bps one-way implementation cost applied to absolute portfolio weight turnover.

## 4. Market Risk-Off gate

Risk-Off is TRUE when either:

- frozen Breadth Risk-Off is TRUE; OR
- frozen VIX Risk-Off is TRUE.

When Risk-Off becomes TRUE:
- no new long entry;
- all existing synthetic positions receive EXIT at the next open.

## 5. Sector RS gate

A stock is eligible for a new long only when its frozen sector ETF:

`RS_PCT >= 0.80`

using the frozen 11-sector cross-sectional RS20 rank.

Existing positions also exit at next open when the sector falls below 0.80.

## 6. TREND_LONG

New TREND_LONG when all are true at close t:

- XMA state = UP_STATE;
- Sector RS percentile >=0.80;
- VOL_Z <= +1;
- VOLUME_Z <= +1;
- Market Risk-Off = FALSE.

This maps:
- F1 lower adverse-risk expectation in UP versus DOWN;
- F3 positive Sector-RS direction;
- H8/H10 negative registered direction for high Vol/Volume inside UP_STATE.

TREND_LONG remains active while all are true:

- state remains UP_STATE;
- Sector RS percentile >=0.80;
- VOL_Z <= +1;
- VOLUME_Z <= +1;
- Risk-Off = FALSE;
- holding age <20 trading bars.

Otherwise exit next open.

## 7. REBOUND_LONG

New REBOUND_LONG when all are true at close t:

- XMA state = DOWN_STATE;
- Sector RS percentile >=0.80;
- `VOL_Z > +1 OR VOLUME_Z > +1`;
- Market Risk-Off = FALSE.

This maps H7/H9 registered positive conditional direction.

Once entered, the high-z condition is an entry condition, not a required holding condition.

REBOUND_LONG exits at next open when ANY occurs:

- first frozen analytic-midpoint touch:
  `abs(close - FAST_MID_ANALYTIC) <= 0.25*ATR14`;
- state is no longer DOWN_STATE;
- Sector RS percentile <0.80;
- Risk-Off = TRUE;
- holding age reaches 20 trading bars.

## 8. Position conflict

A symbol can hold at most one mode.

If flat:
- evaluate TREND_LONG first;
- otherwise evaluate REBOUND_LONG.

No same-day long-to-long mode conversion.
A mode exit is executed first; any later re-entry requires a new close signal.

## 9. Daily portfolio mechanics

At every close:
1. update existing position states;
2. determine exits;
3. determine new entries for flat symbols;
4. form next-open active set;
5. next open: equal-weight active positions.

Portfolio weights may change because:
- entries;
- exits;
- active-count changes.

All absolute target-weight changes incur 5 bps one-way cost.

## 10. Required report

Report at minimum:

- first eligible trading date;
- final date;
- initial capital = $10,000;
- final capital;
- cumulative return;
- CAGR;
- maximum drawdown;
- annualized Sharpe using daily open-to-open portfolio returns, rf=0;
- positive-day rate;
- average gross exposure;
- total turnover;
- entry count;
- exit count;
- TREND_LONG entries;
- REBOUND_LONG entries;
- SPY buy-and-hold return over identical executable interval;
- annual return table.

No parameter may be changed after seeing this development backtest.
