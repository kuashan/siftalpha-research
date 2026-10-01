# Crypto SELL-C Partial Exit Study Protocol v1

Status: **PRE_REGISTERED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Question

Resolve the remaining Crypto SELL-C question using only the frozen BTC / ETH / BNB / SOL daily data:

When the first isolated SELL-C occurs while long, should the strategy sell 25%, 50%, 75%, or 100% of the current position?

No BUY or SELL signal equation may change.

## 2. Frozen universe and data

Assets:
- BTC
- ETH
- BNB
- SOL

Data:
- Binance spot UTC 1d OHLCV
- same frozen windows already used by the Crypto refinement study:
  - BTC 2017-08-17 through 2026-05-05
  - ETH 2017-08-17 through 2026-04-19
  - BNB 2017-11-06 through 2026-04-19
  - SOL 2020-08-11 through 2026-04-19

The existing FULL_FIRST baseline must reproduce exactly before interpretation.

## 3. Frozen BUY logic

- first BUY-A / BUY-B -> buy 60% at next open
- if BUY-C onset occurs within W3 -> add remaining 40% at next open
- BUY-C cannot independently open
- no W5 top-up
- long / cash only
- 5 bps adverse slippage per transaction
- sample-end open position is mark-to-market

## 4. Frozen SELL-A / SELL-B behavior

- isolated SELL-A -> sell 100%
- isolated SELL-B -> sell 100%
- same-bar multi-family SELL -> sell 100%

Only isolated SELL-C is changed by this experiment.

## 5. Frozen SELL-C policies

Formal policies:
- C_SELL_25: first isolated SELL-C sells 25%, retains 75%
- C_SELL_50: first isolated SELL-C sells 50%, retains 50%
- C_SELL_75: first isolated SELL-C sells 75%, retains 25%
- C_SELL_100: first isolated SELL-C sells 100% (current control)

After a partial SELL-C:
- repeated SELL-C onsets do not sell more;
- the first later onset containing SELL-A or SELL-B exits all remaining position;
- any later same-bar multi-family SELL exits all remaining position;
- no same-day re-entry after a full exit;
- a later fresh BUY-A / BUY-B may open a new position normally.

No additional percentage may be added after seeing results.

## 6. Required metrics

Per coin and policy:
- cumulative return
- close MDD
- intraday-low MDD
- completed trades
- win rate
- mean / median trade
- P10 / P5 / CVaR10 / worst trade
- exposure
- SELL-C partial events
- full exits
- open-at-end

Cross-coin:
- four-coin mean and median return
- return delta vs C_SELL_100
- MDD delta vs C_SELL_100
- P5 and CVaR10 delta
- return-improved coin count
- MDD-improved coin count
- 5000 deterministic coin-level bootstrap, seed 20261001

SELL-C event audit:
- number of isolated first SELL-C events
- 3 / 5 / 10 / 20 day forward return
- wait-to-next-A/B return
- retained-position contribution by policy
- BUY-C-confirmed vs pre-confirmation subset
- periods 2017-2020 / 2021-2023 / 2024-2026

## 7. Admission gate

A partial SELL-C policy can be promoted only if all are true versus C_SELL_100:

1. Four-coin mean cumulative return is higher.
2. Cumulative return improves on at least 3 of 4 coins.
3. Four-coin mean intraday-low MDD is no worse.
4. Mean P5 is no worse.
5. Mean CVaR10 is no worse.
6. No single coin contributes more than 60% of the total positive return uplift across improving coins.
7. The policy is not driven only by 2017-2020; SELL-C retained-leg evidence must remain non-negative on average in both 2021-2023 and 2024-2026.
8. BUY-C-confirmed SELL-C events must not show a negative mean retained-leg contribution.

Passing v1 yields only:
`CRYPTO_SELL_C_PARTIAL = PROMOTED_TO_NEXT_VALIDATION`

If no partial policy passes:
`CRYPTO_SELL_C_FULL = RETAINED`

## 8. Closure

This study closes after evaluating exactly 25 / 50 / 75 / 100.

No post-result repair is allowed inside v1.

Possible final states:
- IMPLEMENTED_AND_VERIFIED
- PROMOTED_TO_NEXT_VALIDATION
- RETAINED
- REJECTED_NOT_ADMITTED
- CLOSED
