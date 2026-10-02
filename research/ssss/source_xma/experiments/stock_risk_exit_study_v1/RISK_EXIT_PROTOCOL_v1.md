# FIVEGZ5SE Stock Risk Exit Study Protocol v1

Status: **PRE_REGISTERED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Purpose

This study tests whether the current 39-stock candidate benefits from an independent Risk Exit（风险退出）layer.

Questions:

1. Does a cost-based Hard Stop（成本硬止损）improve drawdown and tail loss without destroying too much return?
2. Does a Trailing Drawdown Stop（移动回撤止损）protect open profits better than the current SELL logic?
3. Do combined hard+trailing rules outperform either alone on a risk-adjusted basis?
4. Are fixed-percentage stops robust across stocks and eras, or do they mostly kill right-tail winners?

No BUY-A / BUY-B / BUY-C / SELL-A / SELL-B / SELL-C equation may change.

## 2. Frozen stock universe

Exactly the same 39 stocks used in the completed refinement study:

AAPL, MSFT, NVDA, AMD, AVGO, ORCL, INTC, QCOM, MU, GOOGL, META, NFLX, AMZN, TSLA,
HD, MCD, WMT, COST, PG, KO, PEP, ABT, LLY, UNH, JNJ, TMO, JPM, BAC, GS, V, MA,
CAT, BA, GE, XOM, CVX, LIN, NEE, PLD.

No stock may be added or removed after results are observed.

## 3. Data

Daily OHLCV from Twelve Data, requested:
- 2010-01-01 through 2026-09-30
- actual listing date applies where later
- real Volume required

These are development / diagnostic data and are not untouched OOS after this study.

## 4. Frozen stock candidate baseline

Entry:
- first valid BUY-A or BUY-B -> next session open buy 60%
- if BUY-C onsets within W3 after initial signal -> next session open add remaining 40% to 100%
- BUY-C never independently opens
- no A/A, B/B, A/B, B/A add
- after W3, no later C top-up

Normal exit:
- isolated first SELL-A -> next session open sell 50%
- isolated first SELL-B -> next session open sell 50%
- SELL-C -> next session open sell 100%
- same-bar >=2 SELL families -> next session open sell 100%
- after an A/B half sale, the first later onset from a different SELL family exits all remaining shares

Execution:
- 5 bps adverse slippage per transaction
- long / cash only
- no time-based forced exit
- sample-end open position mark-to-market

## 5. Risk exit semantics

Risk exits apply to all currently open shares, including after an A/B half sale.

### 5.1 Hard Stop（成本硬止损）

Reference = weighted-average executed cost of current open shares.

Because partial sells reduce quantity but do not change remaining-share acquisition cost per share, the weighted cost basis of the remaining shares is preserved after an A/B half sale.

BUY-C top-up recalculates weighted average cost from actual executed quantities and prices.

Frozen hard-stop candidates:

- 5%
- 8%
- 10%
- 12%
- 15%
- 20%

Stop price:
`weighted_cost * (1 - hard_pct)`

Execution:
1. if session open <= stop price -> exit all remaining shares at session open with 5 bps adverse slippage;
2. else if session low <= stop price -> exit all remaining shares at stop price with 5 bps adverse slippage;
3. after risk exit, no same-day re-entry;
4. re-entry requires a later fresh BUY-A / BUY-B onset.

### 5.2 Trailing Drawdown Stop（移动回撤止损）

To avoid unknown intraday high/low ordering on daily data, trailing reference uses highest completed daily close since the position opened.

The trailing reference:
- is not reset by BUY-C top-up;
- is not reset by A/B half sale.

Frozen trailing candidates:

- 5%
- 8%
- 10%
- 12%
- 15%
- 20%

Stop price:
`highest_prior_close * (1 - trail_pct)`

Execution uses the same gap / intraday-low logic as the hard stop.

### 5.3 Combined rule

For each hard/trailing pair, the active risk stop is the tighter price of:
- hard stop;
- trailing stop.

Frozen grid:
6 hard levels x 6 trailing levels = 36 combined configurations.

No threshold may be added after results are observed.

## 6. Same-open precedence

At next session open:

1. execute any normal SELL already scheduled from the prior close;
2. otherwise execute any scheduled BUY / BUY-C top-up;
3. then evaluate the session's risk stop using open and low.

This preserves causal ordering.

## 7. Required controls

Per stock:

- STOCK_BASELINE_SELECTIVE
- HARD_5 / 8 / 10 / 12 / 15 / 20
- TRAIL_5 / 8 / 10 / 12 / 15 / 20
- all 36 HARD_x_TRAIL_y combinations

49 configurations per stock.
39 stocks.
Total planned portfolio runs: 1,911.

## 8. Required metrics

Portfolio:
- cumulative return
- close-to-close MDD
- intraday-low MDD
- trades
- win rate
- mean / median trade return
- P10
- P5
- CVaR10
- worst trade
- exposure
- normal full exits
- normal half exits
- hard / trailing / both exits
- gap-stop exits

Risk-exit diagnostics:
- total stop exits
- matched baseline trade comparison
- killed baseline winners
- improved baseline losers
- opportunity cost of killed winners
- saved-loss improvement
- post-stop 3 / 5 / 10 / 20 session returns
- post-stop adverse excursion
- recovery above pre-stop weighted cost
- BUY-C-confirmed stop subset
- pre-confirmation stop subset

## 9. Primary decision discipline

The objective is NOT maximum return.

Primary priorities:

1. materially improve intraday-low MDD;
2. improve P5 / CVaR10 / worst-trade loss;
3. preserve enough of the baseline cumulative return;
4. avoid excessive false stops and killed winners;
5. require cross-stock and cross-era consistency.

A rule cannot be admitted only because mean return rises.

## 10. Statistical audit

Required:
- per-stock results
- 39-stock aggregate
- 5000 deterministic bootstrap resamples across stocks
- cross-stock consistency counts
- period diagnostics:
  - 2010-2014
  - 2015-2019
  - 2020-2026
- sector-diversity inspection using the frozen 39-stock set
- BUY-C-confirmed subset
- matched baseline trade audit

## 11. Admission rule

Because all tested thresholds are compared on development data, any promising threshold may only be:

`PROMOTED_TO_NEXT_VALIDATION`

It cannot become production-frozen directly from this study.

Possible closure labels:
- IMPLEMENTED_AND_VERIFIED
- PROMOTED_TO_NEXT_VALIDATION
- RETAINED
- REJECTED_NOT_ADMITTED
- BLOCKED_BY_DATA

## 12. Scope boundary

This study does not reopen:
- BUY-C W3 vs W5;
- 50/60/70 initial sizing optimization;
- SELL-A vs SELL-B asymmetric fractions;
- Crypto rules.

Only the stock Risk Exit layer is under test.
