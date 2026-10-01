# FIVEGZ5SE Crypto Risk Exit Study Protocol v1

Status: **PRE_REGISTERED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Purpose

This study adds an independent Risk Exit（风险退出）layer to the already frozen Crypto three-buy/three-sell framework.

It answers:

1. Does a cost-based Hard Stop（成本硬止损）materially reduce catastrophic losses without destroying too much return?
2. Does a Trailing Drawdown Stop（移动回撤止损）protect open profits better than the current signal-only exit?
3. Is a combined Hard + Trailing rule superior to either mechanism alone?
4. Which stop levels reduce MDD / tail loss while avoiding excessive false stops?

No BUY-A / BUY-B / BUY-C / SELL-A / SELL-B / SELL-C equation may change in this study.

## 2. Frozen universe

Exactly:
- BTC
- ETH
- BNB
- SOL

No additional crypto asset may enter this study.

## 3. Frozen data

Binance spot UTC 1d OHLCV from the source frozen in the previous refinement:

- BTC: 2017-08-17 through 2026-05-05
- ETH: 2017-08-17 through 2026-04-19
- BNB: 2017-11-06 through 2026-04-19
- SOL: 2020-08-11 through 2026-04-19

Real Volume is required. No imputation.

These data are development / diagnostic after this study and are not untouched OOS.

## 4. Frozen baseline trading logic

Entry:
- first valid BUY-A or BUY-B -> next daily open buy 60%
- if BUY-C onsets within W3 after the initial signal -> next daily open add remaining 40% to 100%
- no BUY-C independent opening
- no A/A, B/B, A/B or B/A add
- after W3, no later C top-up

Normal exit baseline:
- first SELL-A / SELL-B / SELL-C -> next daily open exit 100%
- same-bar multi-family SELL -> next daily open exit 100%

Execution:
- 5 bps adverse slippage each transaction
- long / cash only
- no time-based forced exit
- final open position mark-to-market

## 5. Risk exit execution semantics

Risk exits are evaluated only while a position is open.

### 5.1 Hard Stop（成本硬止损）

Reference = current weighted-average executed cost of the whole open position.

After a BUY-C top-up, the weighted average cost is recalculated from actual executed quantities and prices.

Hard-stop candidates are frozen BEFORE computation:

- 5%
- 8%
- 10%
- 12%
- 15%
- 20%

Hard stop price:

`weighted_cost * (1 - stop_pct)`

Daily execution:
1. if the daily open is already below the stop price, exit at that open with 5 bps adverse slippage;
2. otherwise, if the daily low touches or crosses the stop price, exit at the stop price with 5 bps adverse slippage;
3. after a risk exit, no same-day re-entry;
4. re-entry requires a later fresh BUY-A / BUY-B onset.

### 5.2 Trailing Drawdown Stop（移动回撤止损）

To avoid unknown intraday high/low ordering on daily bars, trailing reference uses the highest **completed daily close** observed since entry.

The reference is NOT reset by BUY-C top-up.

Trailing candidates are frozen BEFORE computation:

- 5%
- 8%
- 10%
- 12%
- 15%
- 20%

Trailing stop price:

`highest_prior_close * (1 - trail_pct)`

Daily execution uses the same gap / intraday-low logic as the hard stop.

After surviving the day, the trailing reference updates with that day's close.

### 5.3 Combined rule

For every hard/trailing pair, the active risk stop is the tighter of:

- weighted-cost hard stop
- highest-prior-close trailing stop

Frozen grid:
6 hard-stop levels × 6 trailing levels = 36 combined configurations.

No threshold is added after seeing results.

## 6. Same-open precedence

At the next daily open:

1. execute any normal SELL already scheduled from the prior close;
2. otherwise execute any scheduled BUY / BUY-C top-up;
3. then evaluate that day's risk stop using open and low.

This prevents an intraday stop from overriding a normal SELL that was already known at the previous close.

## 7. Required controls

The study must compute:

- BASELINE_SIGNAL_ONLY
- HARD_5 / 8 / 10 / 12 / 15 / 20
- TRAIL_5 / 8 / 10 / 12 / 15 / 20
- all 36 HARD_x_TRAIL_y combinations

Total = 49 configurations per coin.

## 8. Required metrics

For every configuration and coin:

Portfolio:
- cumulative return
- close-to-close MDD
- intraday-low MDD
- completed trades
- trade win rate
- mean / median trade return
- P10
- P5
- CVaR10
- worst trade
- exposure
- normal SELL exits
- hard-stop exits
- trailing-stop exits
- gap-stop exits
- open-at-end

Risk-exit diagnostics:
- number of stop exits
- stop-return mean / median
- stop loss distribution
- number of stops whose matched baseline trade eventually finished profitable
- number of stops that improved a matched baseline losing trade
- mean matched trade-return delta vs signal-only baseline
- post-stop 3 / 5 / 10 / 20 day return
- post-stop additional adverse excursion
- post-stop recovery above pre-stop weighted cost

## 9. Comparison discipline

Primary objective is NOT maximum return.

Primary objectives, in order:

1. materially improve intraday-low MDD;
2. improve P5 / CVaR10 / worst-trade loss;
3. avoid large reduction in cumulative return;
4. avoid excessive false stops / killed baseline winners.

A configuration may not be called superior only because cumulative return is larger.

## 10. Statistical audit

Required:
- per-coin results
- pooled four-coin results
- BTC separately
- matched baseline trade audit
- deterministic bootstrap, 5000 resamples
- cross-coin consistency
- period diagnostics:
  - 2017-2020
  - 2021-2023
  - 2024-2026

## 11. Admission discipline

Because the same data are used to compare fixed stop levels, any selected stop is at most:

`PROMOTED_TO_NEXT_VALIDATION`

It cannot become a production-frozen threshold from this same study.

Possible closure labels:
- IMPLEMENTED_AND_VERIFIED
- PROMOTED_TO_NEXT_VALIDATION
- RETAINED
- REJECTED_NOT_ADMITTED
- BLOCKED_BY_DATA

## 12. Existing SELL-C work

This study does NOT optimize SELL-C partial retention.

Risk exits are evaluated against the current Crypto FULL_FIRST normal-exit control to isolate the value of the risk layer.

SELL-C differentiation remains a separate later study.
