# FIVEGZ5SE Three-Buy Three-Sell Refinement Final Report v1

Status: **IMPLEMENTED_AND_VERIFIED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Scope

This study closes the four questions preregistered in `FIVEGZ5SE_REFINEMENT_PROTOCOL_v1.md`:

1. Stocks: does W3 BUY-C top-up add value versus remaining at a static partial position?
2. Stocks: should isolated SELL-A / SELL-B exit half or all, and is there evidence that A and B need different actions?
3. Crypto: does W3 BUY-C top-up add independent value?
4. Crypto: should SELL-A / SELL-B / SELL-C remain operationally equivalent?

No BUY/SELL signal equation was changed.

### Stock sample

Exactly the frozen 39 U.S. stocks.

Requested daily horizon: 2010-01-01 through 2026-09-30.
Most symbols contain 2010-01-04 through 2026-09-29. META begins at its 2012 listing and TSLA at its 2010 listing.

### Crypto sample

Exactly BTC / ETH / BNB / SOL, Binance spot UTC 1d OHLCV:

- BTC: 2017-08-17 through 2026-05-05;
- ETH: 2017-08-17 through 2026-04-19;
- BNB: 2017-11-06 through 2026-04-19;
- SOL: 2020-08-11 through 2026-04-19.

Crypto source files contain real Volume. No missing-volume substitution was allowed.

## 2. Frozen execution

- SCTYPE=1 only.
- signal at close t;
- transaction at next bar/session open;
- 5 bps adverse slippage per transaction;
- long/cash only;
- no time-based forced exit;
- sample-end open positions are mark-to-market;
- BUY-C cannot independently open a position;
- W5 was not reopened.

The working BUY sizing candidate remained:

```
First BUY-A or BUY-B -> 60%
BUY-C onset within W3 -> add 40% -> 100%
No C within W3 -> remain 60%
```

## 3. Stock BUY-C top-up: static partial versus matched top-up

Primary 60% comparison across 39 stocks:

STATIC_60:
- mean cumulative return: +128.20%

TOPUP_60:
- mean cumulative return: +143.37%

Matched TOPUP_60 minus STATIC_60:
- mean return delta: **+15.17 percentage points**
- median return delta: **+3.27 pp**
- asset bootstrap 95% CI: **[+3.34, +29.80] pp**
- return improved on **24/39** stocks
- total completed trades: 3,135
- BUY-C confirmations: 272

Risk effect:
- mean MDD delta: **-1.62 pp** (negative means worse)
- bootstrap 95% CI: **[-2.46, -0.88] pp**
- MDD improved on only **8/39**
- P5 trade delta: **-0.28 pp**
- bootstrap 95% CI: **[-0.49, -0.11] pp**
- CVaR10 delta: **-0.47 pp**
- bootstrap 95% CI: **[-0.68, -0.30] pp**

The 50% and 70% matched controls give the same qualitative result:

- 50% top-up: return delta +16.27 pp, 95% CI [+4.18, +30.70]; risk metrics worsen on average.
- 70% top-up: return delta +13.25 pp, 95% CI [+2.70, +26.62]; risk metrics worsen on average.

### Stock BUY decision

BUY-C top-up has **incremental return value** versus staying static.

It is **not** a risk-reduction device in stocks. It increases market exposure precisely after confirmation and, over the extended sample, pays for that exposure with higher expected return but worse MDD and tail loss.

Status:

`STOCK_C_TOPUP_INCREMENTAL_VS_STATIC_PARTIAL = IMPLEMENTED_AND_VERIFIED`

`STOCK_BUY_60_W3_C_TOPUP = PROMOTED_TO_NEXT_VALIDATION`

The 60% operating candidate is not re-optimized in this study.

## 4. Stock SELL-A / SELL-B: half versus full

The BUY side is fixed at 60% initial + W3 BUY-C top-up.

### FULL_FIRST control

- mean return: +143.37%
- mean MDD: -31.86%

### Isolated A/B -> half, then next distinct SELL -> remainder

AB_HALF:
- mean return: +154.92%
- mean return delta versus FULL_FIRST: **+11.55 pp**
- median return delta: **+12.00 pp**
- bootstrap 95% CI of mean return delta: **[-4.54, +28.85] pp**
- return improved on **27/39**

Risk:
- mean MDD improves by **+2.14 pp**
- bootstrap 95% CI: **[+1.10, +3.29] pp**
- MDD improves on **29/39**
- P5 / CVaR10 deltas are approximately neutral and their bootstrap intervals cross zero.

Thus the strongest robust gain is not a guaranteed return increase; it is a broad **drawdown improvement** while retaining more upside than immediate full exit.

### Is A different from B?

A_HALF_B_FULL versus A_FULL_B_HALF:

Return difference, A-half minus B-half:
- mean +0.49 pp
- bootstrap 95% CI **[-15.58, +16.98] pp**

MDD difference:
- mean +0.87 pp
- bootstrap 95% CI **[-0.35, +2.24] pp**

P5 and CVaR10 differences also cross zero.

There is therefore no defensible evidence that SELL-A and SELL-B require different exit fractions.

Event behavior supports symmetric treatment:

SELL-A:
- 829 first isolated events
- wait-to-next-distinct mean +2.03%
- median +2.28%
- positive 64.90%
- asset-level wait mean 95% CI [+1.53%, +2.59%]
- 10-session forward mean +0.71%
- asset-level 10-session mean 95% CI [+0.20%, +1.19%]

SELL-B:
- 590 events
- wait-to-next-distinct mean +1.50%
- median +1.58%
- positive 67.46%
- asset-level wait mean 95% CI [+0.96%, +2.10%]
- 10-session forward mean +1.06%
- asset-level 10-session mean 95% CI [+0.80%, +1.49%]

Both families therefore frequently occur before additional upside is exhausted.

### Why not ignore A/B entirely?

AB_HOLD (ignore the first isolated A/B completely and wait for a distinct SELL):
- mean return delta +56.35 pp
- bootstrap 95% CI [+27.25, +91.30] pp
- but mean MDD worsens by about 1.10 pp
- P5 worsens by about 1.38 pp
- CVaR10 worsens by about 1.13 pp
- P5 and CVaR deterioration have bootstrap intervals fully below zero.

This is an aggressive return-maximizing behavior that gives up too much tail protection to be admitted as the balanced rule.

### Stock SELL decision

Current next-validation candidate:

```
isolated SELL-A -> sell 50%
isolated SELL-B -> sell 50%
SELL-C -> sell 100%
same-bar >=2 SELL families -> sell 100%

after A/B half-exit:
    first later onset from a different SELL family
    -> sell all remaining position
```

No finer A/B threshold is admitted. The study explicitly did not mine an in-sample numeric filter.

Statuses:

`STOCK_ISOLATED_SELL_A_B_HALF = PROMOTED_TO_NEXT_VALIDATION`

`STOCK_A_VS_B_DIFFERENT_EXIT = REJECTED_NOT_ADMITTED`

`STOCK_A_B_HOLD_TO_DISTINCT = REJECTED_NOT_ADMITTED`

`STOCK_SELL_C_OR_MULTI_FULL = RETAINED`

## 5. Crypto BUY-C top-up: matched causal result

Across BTC / ETH / BNB / SOL, 60% initial:

BTC:
- STATIC_60 -4.48%
- TOPUP_60 +7.24%
- delta **+11.73 pp**

ETH:
- STATIC_60 +14.96%
- TOPUP_60 +29.39%
- delta **+14.43 pp**

BNB:
- STATIC_60 +40.52%
- TOPUP_60 +95.19%
- delta **+54.67 pp**

SOL:
- STATIC_60 +93.87%
- TOPUP_60 +143.14%
- delta **+49.28 pp**

All four improve cumulative return.

Asset-level bootstrap of the four 60% deltas:
- mean +32.53 pp
- 95% CI **[+13.08, +51.97] pp**

Risk is mixed:
- MDD improves on 3/4 coins;
- the four-asset mean MDD effect is approximately flat and its CI crosses zero;
- P5 / CVaR10 are slightly worse on average, driven mainly by ETH.

### Direct added-40% leg audit

To avoid confusing portfolio sizing with the incremental top-up itself, every executed C top-up leg was isolated from the C next-open execution price to the subsequent SELL next-open execution price.

All four coins:
- n = 26
- mean added-leg return: **+9.75%**
- median: **+13.53%**
- win rate: **88.46%**
- event bootstrap 95% CI of mean: **[+4.16%, +14.75%]**
- worst: -34.59%
- best: +38.73%

By coin:
- BTC n=7, mean +4.91%, win 85.71%
- ETH n=7, mean +7.31%, win 85.71%
- BNB n=8, mean +12.10%, win 87.50%
- SOL n=4, mean +17.74%, win 100%

By era:
- 2017-2020: n=13, mean +10.31%
- 2021-2023: n=6, mean +13.57%
- 2024-2026: n=7, mean +5.42%

All three eras are positive.

### Crypto BUY decision

The old data gap is closed.

`CRYPTO_C_TOPUP_INCREMENTAL_VS_STATIC_PARTIAL = IMPLEMENTED_AND_VERIFIED`

The evidence supports BUY-C as a genuine sizing signal, not merely a descriptive confirmation signal.

The trade-off remains important: C top-up adds expected return, but it does not guarantee lower drawdown or better tail loss.

`CRYPTO_BUY_60_W3_C_TOPUP = PROMOTED_TO_NEXT_VALIDATION`

## 6. Crypto SELL-A / SELL-B / SELL-C are not equivalent

Using the same 60% + W3 C-top-up entry policy:

Event counts:
- first isolated SELL-A: 40
- SELL-B: 42
- SELL-C: 166
- same-bar multi-family: 5

### SELL-A

If A is ignored until a different SELL family appears:
- wait return mean: -4.42%
- event bootstrap 95% CI: **[-8.94%, -0.38%]**
- 10-session forward mean: -4.69%
- 95% CI: **[-8.77%, -0.50%]**

The evidence supports SELL-A as a genuine defensive exit.

`CRYPTO_SELL_A_FULL = RETAINED`

### SELL-B

If B is ignored:
- wait mean: -2.76%
- 95% CI: [-7.40%, +1.58%]
- 10-session mean: -1.16%
- 95% CI: [-5.68%, +3.17%]

This is weaker than A, but there is no statistically robust benefit to delaying B. Portfolio delay-B results also deteriorate in the four-coin aggregate.

`CRYPTO_SELL_B_FULL = RETAINED`

### SELL-C

SELL-C behaves differently.

If C is ignored until the next distinct SELL:
- wait mean: **+5.32%**
- bootstrap 95% CI: **[+2.41%, +8.22%]**
- 10-session forward mean: **+4.96%**
- 95% CI: **[+1.76%, +8.41%]**

Period robustness:
- 2017-2020: 10-session mean +6.53%
- 2021-2023: +6.58%
- 2024-2026: +1.64%

However:
- wait-return median is slightly negative overall;
- 2024-2026 median wait return is negative;
- the mean is driven by a meaningful right tail of large winners;
- delaying C to the next distinct SELL can worsen MDD and tail loss, especially in BNB / SOL.

Therefore `DELAY_C_TO_NEXT_DISTINCT` is too aggressive to admit.

An exploratory 50% SELL-C retention control improved cumulative return in BTC / ETH / BNB but not SOL, and tail statistics worsened in all four. It is evidence that C deserves separate treatment, not evidence that 50% is already the final answer.

Statuses:

`CRYPTO_DELAY_SELL_C_TO_DISTINCT = REJECTED_NOT_ADMITTED`

`CRYPTO_SELL_C_DIFFERENTIATION = PROMOTED_TO_NEXT_VALIDATION`

`CRYPTO_FULL_FIRST_CURRENT_CONTROL = RETAINED`

This means current operation should not silently change yet. The next preregistered validation should specifically compare full SELL-C against a fixed partial-C retention rule without changing SELL-A/B.

## 7. What is now materially more complete

### Stocks

The unresolved questions are substantially narrowed:

- BUY-C top-up has real incremental return value but increases stock risk.
- isolated SELL-A and SELL-B should be treated symmetrically; no evidence supports separate A/B fractions.
- immediate full exit on isolated A/B gives up too much subsequent upside.
- ignoring A/B completely gives up too much downside/tail protection.
- half-exit is the balanced next-validation candidate.
- SELL-C / multi-family full exit remains the control.

### Crypto

- BUY-C top-up has direct independent value, confirmed both by matched portfolio controls and by the added 40% leg itself.
- SELL-A is a strong full-exit signal.
- SELL-B has no evidence sufficient to justify delaying it.
- SELL-C is structurally different and is the only SELL family that clearly warrants another refinement round.
- simply waiting from SELL-C until a different SELL is too aggressive.

## 8. Current candidate implementation after this study

### Stock candidate for next validation

```
BUY-A or BUY-B -> 60%
BUY-C within W3 -> +40% to 100%

isolated SELL-A -> sell 50%
isolated SELL-B -> sell 50%
SELL-C -> sell 100%
same-bar multi SELL -> sell 100%
after A/B half sale, next distinct SELL -> sell remaining 100%
```

### Crypto current control

```
BUY-A or BUY-B -> 60%
BUY-C within W3 -> +40% to 100%

first SELL-A / SELL-B / SELL-C -> sell 100%
```

For Crypto, SELL-C partial retention is the next validation target, not yet the current operating rule.

## 9. OOS governance

All 39 stocks through 2026-09-29 and BTC / ETH / BNB / SOL through the source-specific 2026 endpoints have now influenced this refinement.

They are development / diagnostic data for these decisions and must not be represented later as untouched OOS for the rules selected here.

Any formal production freeze should therefore use:
- a genuinely later forward period;
- or a separately frozen untouched asset/time universe;
- with no parameter changes after observation.

## 10. Closure

`FIVEGZ5SE_THREE_BUY_THREE_SELL_REFINEMENT_V1 = IMPLEMENTED_AND_VERIFIED`

`STOCK_C_TOPUP_INCREMENTAL_VS_STATIC_PARTIAL = IMPLEMENTED_AND_VERIFIED`

`STOCK_ISOLATED_SELL_A_B_HALF = PROMOTED_TO_NEXT_VALIDATION`

`STOCK_A_VS_B_DIFFERENT_EXIT = REJECTED_NOT_ADMITTED`

`STOCK_A_B_HOLD_TO_DISTINCT = REJECTED_NOT_ADMITTED`

`CRYPTO_C_TOPUP_INCREMENTAL_VS_STATIC_PARTIAL = IMPLEMENTED_AND_VERIFIED`

`CRYPTO_SELL_A_FULL = RETAINED`

`CRYPTO_SELL_B_FULL = RETAINED`

`CRYPTO_DELAY_SELL_C_TO_DISTINCT = REJECTED_NOT_ADMITTED`

`CRYPTO_SELL_C_DIFFERENTIATION = PROMOTED_TO_NEXT_VALIDATION`

Historical V2 and the prior 43-asset staged-entry report remain preserved and are not overwritten.
