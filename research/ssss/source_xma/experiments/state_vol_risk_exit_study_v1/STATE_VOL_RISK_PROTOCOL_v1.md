# SSSS State / Volatility-Aware Risk Exit Study Protocol v1

Status: **PRE_REGISTERED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Purpose

Test whether the current stock and Crypto controls benefit from a causal State / Volatility-Aware Risk Exit（状态 / 波动率感知风险退出）layer.

If no candidate preserves the strategy's right-tail economics while improving risk robustly, the study must close with **no risk-exit layer admitted**.

No BUY-A / BUY-B / BUY-C / SELL-A / SELL-B / SELL-C definition may change.

## 2. Frozen universes and baselines

Stocks: the frozen 39-stock universe from Stock Risk Exit v1.1.

Stock baseline:
- BUY-A / BUY-B -> 60%
- BUY-C within W3 -> +40% to 100%
- isolated SELL-A / SELL-B -> sell 50%
- SELL-C or same-bar multi-family SELL -> full exit
- after A/B half sale -> first later different SELL family exits the remainder.

Crypto: BTC / ETH / BNB / SOL only.

Crypto baseline:
- BUY-A / BUY-B -> 60%
- BUY-C within W3 -> +40% to 100%
- first SELL-A / SELL-B / SELL-C -> full exit.

Execution for both:
- close-confirmed signal;
- next-bar open execution;
- 5 bps adverse slippage per transaction;
- long / cash only;
- no time cap;
- sample-end open position = mark-to-market, with no synthetic final sell.

## 3. Frozen data

Stocks:
- Twelve Data daily OHLCV;
- same 39 stocks and same requested window as Stock Risk Exit v1.1;
- mostly 2010-01-04 through 2026-09-29; listing date applies where later.

Crypto:
- Binance spot UTC 1d OHLCV;
- same frozen windows as Crypto Risk Exit v1:
  - BTC 2017-08-17 through 2026-05-05
  - ETH 2017-08-17 through 2026-04-19
  - BNB 2017-11-06 through 2026-04-19
  - SOL 2020-08-11 through 2026-04-19.

Baseline reproduction must PASS before candidate interpretation.

## 4. Volatility definition

ATR14 uses completed daily bars only.

True Range:
`max(high-low, abs(high-prev_close), abs(low-prev_close))`

ATR14:
simple 14-bar mean of True Range.

For an open position at close t:

`LOSS_ATR = max(0, weighted_executed_cost - close_t) / ATR14_t`

`PEAK_DD_ATR = max(0, highest_completed_close_since_entry - close_t) / ATR14_t`

BUY-C top-up recalculates weighted executed cost.
The peak-close reference is not reset by BUY-C or by a stock A/B half sale.

## 5. Five-dimensional state deterioration

Ranks remain:
LONG=+2, LIGHT_LONG=+1, GRAY=0, LIGHT_SHORT=-1, SHORT=-2.

At close t:

`STATE_SCORE = Trend + Capital + Momentum + Acceleration + Anomaly`

`BEARISH_COUNT = number of dimensions <= -1`

`D3 = sum of each dimension's W3 net change`

Moderate deterioration:
- STATE_SCORE <= -2
- BEARISH_COUNT >= 2
- D3 <= -2

Severe deterioration:
- STATE_SCORE <= -4
- BEARISH_COUNT >= 3
- D3 <= -3

These are causal close-time conditions only.

## 6. Frozen candidate set

At most one risk action may be scheduled from a close. A risk exit is full exit of all remaining shares/coins at the next open with 5 bps adverse slippage.

Controls:
- ATR2_ONLY: LOSS_ATR >= 2
- ATR3_ONLY: LOSS_ATR >= 3

Formal candidates:
1. LOSS2_MOD: LOSS_ATR >= 2 AND Moderate deterioration.
2. LOSS3_MOD: LOSS_ATR >= 3 AND Moderate deterioration.
3. LOSS2_SEV: LOSS_ATR >= 2 AND Severe deterioration.
4. PEAK2_MOD: PEAK_DD_ATR >= 2 AND Moderate deterioration.
5. PEAK3_MOD: PEAK_DD_ATR >= 3 AND Moderate deterioration.
6. HYBRID25_MOD: max(LOSS_ATR, PEAK_DD_ATR) >= 2.5 AND Moderate deterioration.
7. CONFIRM_ADAPT:
   - before BUY-C confirmation: max(LOSS_ATR, PEAK_DD_ATR) >= 2 AND Moderate deterioration;
   - after BUY-C confirmation: max(LOSS_ATR, PEAK_DD_ATR) >= 3 AND Severe deterioration.
8. LOSS4_SEV: LOSS_ATR >= 4 AND Severe deterioration (catastrophe-only candidate).

No additional ATR multiple, state-score cutoff, bearish-count cutoff, or D3 cutoff may be introduced after results are observed in v1.

## 7. Precedence

At next open:
1. execute a normal SELL already scheduled from the prior close;
2. otherwise execute a risk exit already scheduled from the prior close;
3. otherwise execute scheduled BUY / BUY-C top-up.

A close that already schedules a normal full exit does not also schedule a risk exit.

After a risk exit, same-day re-entry is forbidden. Re-entry requires a later fresh BUY-A / BUY-B onset.

## 8. Required metrics

Per asset and configuration:
- cumulative return
- close MDD
- intraday-low MDD
- completed trades
- win rate
- mean / median trade
- P10 / P5 / CVaR10 / worst trade
- exposure
- normal exits / normal half exits
- risk exits
- gap exits at scheduled next open
- open-at-end

Matched baseline diagnostics:
- risk-exit count
- killed baseline winners
- saved baseline losers
- mean matched delta vs baseline
- killed-winner opportunity cost
- saved-loser improvement
- BUY-C-confirmed subset
- pre-confirmation subset
- post-exit 3 / 5 / 10 / 20-session behavior where available.

## 9. Statistical audit

Stocks:
- 39-stock aggregate
- per-stock results
- 5,000 deterministic stock-level bootstrap
- cross-stock consistency
- periods 2010-2014 / 2015-2019 / 2020-2026.

Crypto:
- per-coin results
- four-coin aggregate
- BTC separately
- 5,000 deterministic bootstrap
- cross-coin consistency
- periods 2017-2020 / 2021-2023 / 2024-2026.

## 10. Admission gates

A candidate may be promoted for an asset class only if all are satisfied:

A. Risk:
- mean intraday-low MDD improves versus that class baseline;
- bootstrap 95% interval for the mean MDD improvement is above 0 for stocks;
- for Crypto, at least 3/4 coins improve intraday MDD.

B. Return preservation:
- mean cumulative return is at least 90% of the positive baseline mean cumulative return for that asset class.

C. Tail:
- mean P5 is no worse than baseline;
- mean CVaR10 is no worse than baseline.

D. Consistency:
- stocks: intraday MDD improves on at least 24/39 stocks;
- Crypto: no candidate is promoted solely because one coin dominates the pooled result.

E. Right-tail protection:
- matched-trade evidence must not show a materially larger killed-winner count than saved-loser count;
- BUY-C-confirmed matched mean delta must not show a material systematic penalty.

Passing this development study yields only:
`PROMOTED_TO_NEXT_VALIDATION`

It does not directly freeze a production rule.

## 11. Universal vs asset-class-specific decision

`UNIVERSAL_STATE_VOL_RISK_EXIT` may be promoted only if the same candidate passes both Stock and Crypto admission gates.

A stock-only or crypto-only candidate may be promoted separately if it passes its own gates.

If no candidate passes for an asset class:
`<ASSET_CLASS>_RISK_EXIT = NOT_USED_RETAIN_BASELINE`

If no candidate passes either class:
`RISK_EXIT_LAYER = NOT_USED_RETAIN_BASELINES`

## 12. Closure discipline

The study must close after this frozen candidate set is evaluated.

Possible states:
- IMPLEMENTED_AND_VERIFIED
- PROMOTED_TO_NEXT_VALIDATION
- RETAINED
- REJECTED_NOT_ADMITTED
- BLOCKED_BY_DATA
- CLOSED

No post-result threshold repair is allowed inside v1.
