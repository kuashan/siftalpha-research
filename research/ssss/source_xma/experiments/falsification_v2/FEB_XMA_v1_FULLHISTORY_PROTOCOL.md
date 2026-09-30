# FEB_XMA_v1 Full-History Replay Protocol

Status: **FROZEN BEFORE FULL-HISTORY REPLAY**

Date: 2026-09-28

Purpose:
re-run the earliest frozen multi-asset Source-XMA engine derived directly from
the successful ABT January discovery on the current 39-equity historical dataset.

This is a development replay. It is not OOS evidence.

## Strategy identity

Strategy:
`FEB_XMA_v1`

Normative source:
`experiments/multi_asset_2025_02/PROTOCOL_FROZEN_BEFORE_RUN.md`

Do not substitute:
- MARJUN_XMA_v2;
- canonical corrected slow channel;
- v2 synthetic map;
- HYS2;
- FIVEGZ sizing;
- Breadth;
- VIX hard gates.

## Data

Equities:
the frozen 39-equity universe in `UNIVERSE_FROZEN_v1.md`.

Historical source:
same Devesh176/Replicating_portfolio OHLCV family used in v1/ABT research.

Replay span:
2020-01-02 through 2025-12-30.

Warm-up:
all available pre-2020 history in each source file may be used for indicators.

## Capital model

Preserve the original multi-asset research model:

- each symbol starts with an independent $10,000 sleeve;
- capital path is continuous through the replay;
- no monthly/annual reset;
- no cross-symbol capital competition;
- aggregate equal-capital portfolio return = arithmetic mean of the 39 sleeve returns.

## Execution

Unchanged from FEB_XMA_v1:

- signal after close;
- execute at next tradable open;
- fractional shares;
- $0 commission;
- 5 bps one-way adverse slippage;
- long-only.

Open positions on final date are liquidated at the final available close with
5 bps adverse slippage for terminal reporting.

## Legacy raw Source-XMA formulas

This replay intentionally reproduces the formula family used by FEB_XMA_v1.

Fast:
- point-in-time double XMA(25) high/low;
- FastUpper = VH25_X + (VH25_X-VL25_X);
- FastLower = VL25_X - (VH25_X-VL25_X);
- FastMid = (VH25_X+VL25_X)/2.

Slow regime:
use the ADKBY-E raw weighted high/low channel as historically implemented,
including lag 19 and lag 20 terms with denominator 210, then EMA90.

Regime:
- BULL when fast lower >= slow lower AND fast upper >= slow upper;
- BEAR when fast upper <= slow upper AND fast lower <= slow lower;
- RANGE when fast lower >= slow lower AND fast upper <= slow upper;
- otherwise EXPANSION.

Momentum:
- DEA3_RAW and DEA33B_RAW exactly from ADKBY-E;
- fast delta = DEA3_RAW(t)-DEA3_RAW(t-1);
- slow delta = DEA33B_RAW(t)-DEA33B_RAW(t-1);
- BOTH_UP iff both deltas >0.

Relative volume:
`RVOL20 = Volume / MA20(Volume)`.

Normalized position for price X:
`POS(X) = (X-FastLower)/(FastUpper-FastLower)*100000`.

## FEB_XMA_v1 actions

Flat lower-extreme probe:
- regime != BEAR;
- normalized low position <20,000 (this also covers the source lower-boundary cross case);
- target 25%;
- create 3-session WATCH_LONG.

Confirmation:
- WATCH_LONG active;
- close > FastMid;
- BOTH_UP;
- target 65%.

Independent breakout entry:
- regime != BEAR;
- close > FastUpper;
- BOTH_UP;
- RVOL20 >=1.50;
- target 70%.

Existing long breakout add:
- close > FastUpper;
- BOTH_UP;
- RVOL20 >=1.50;
- target 100%.

Extreme-deceleration reduce:
- normalized close position >120,000;
- current (fast delta + slow delta) < prior session's corresponding sum;
- reduce target by 30 percentage points;
- floor 40%.

Hard exit to 0% if ANY:
- regime == BEAR;
- close < FastMid AND momentum != BOTH_UP;
- slow delta <0 AND normalized close position >80,000.

No shorting.

## Watch semantics for full-history replay

A WATCH_LONG opened by a probe is valid for the probe bar plus the next
3 trading sessions for confirmation.

Expiry removes confirmation eligibility only; it does not itself liquidate
an existing 25% probe. Existing-long reduce/exit/breakout rules continue to apply.

## Evaluation

Report:
- equal-capital aggregate return;
- CAGR;
- max drawdown of aggregate equal-weight sleeve equity;
- annualized Sharpe;
- mean/median sleeve return;
- positive symbols;
- worst/best symbol;
- mean/median symbol max drawdown;
- execution count;
- average exposure;
- annual aggregate returns;
- SPY buy-and-hold over the comparable executable interval when available.

No rule changes are allowed after viewing replay returns.
