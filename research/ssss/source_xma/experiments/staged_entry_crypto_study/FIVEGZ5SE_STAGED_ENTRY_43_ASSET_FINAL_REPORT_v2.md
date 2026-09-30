# FIVEGZ5SE Staged Entry 43-Asset Final Report v2

Status: **IMPLEMENTED_AND_VERIFIED**

Date: 2026-09-30  
Branch: `research/source-xma-walkforward`  
Computation commit: `366536295728c2069ce551d390d01d7cf4a94dc4`

## 1. Final universe

This final decision uses exactly:

- 39 U.S. stocks;
- BTC;
- ETH;
- BNB;
- SOL.

Total: **43 assets**.

BTC is treated as the primary crypto operating reference. ETH / BNB / SOL are secondary crypto robustness checks.

The previous 10-crypto aggregate is retained only as diagnostic history because the user subsequently narrowed the intended trading universe before final interpretation.

Effective sample ranges:

- stocks: approximately 2020-04-02 through 2025-12-31;
- BTC / ETH / BNB / SOL: 2021-03-07 through 2024-04-09 after warm-up.

All 43 assets are now development / diagnostic data for this staged-entry design and must not later be called untouched OOS for rules selected from this study.

## 2. Frozen candidate design

Initial signal:

- first valid BUY-A or BUY-B only;
- BUY-C never opens a new position independently.

Staged allocation candidates:

- 50% initial;
- 60% initial;
- 70% initial.

Top-up:

- only a later BUY-C onset after the initial A/B signal may top the position to 100%;
- W3 or W5 confirmation windows were tested exactly as pre-registered;
- A->A, B->B, A->B and B->A do not add;
- no pyramiding above 100%.

Execution:

- signal on close t;
- execute next-session open;
- 5 bps adverse slippage each side;
- no time-based forced exit;
- positions still open at sample end are mark-to-market.

Exit controls:

- FULL_FIRST: first SELL-A/B/C exits all;
- SELECTIVE: isolated SELL-A/B exits half, SELL-C or multi-family SELL exits all, and the next distinct SELL exits the remainder.

## 3. Confirmation quality: BUY-C after A/B

### W3 completed trades

Combined 43 assets:

- C-confirmed: n=111
- mean trade: +4.56%
- median trade: +4.21%
- win rate: 73.87%
- P5: -9.26%
- CVaR10: -10.99%
- worst: -22.36%

Unconfirmed:

- n=1125
- mean trade: +1.52%
- median trade: +1.90%
- win rate: 63.64%
- P5: -12.87%
- CVaR10: -16.20%
- worst: -47.68%

Crypto only:

- W3 confirmed n=8
- mean +19.77%
- win 87.50%
- worst -9.31%

Crypto W3 unconfirmed:

- n=98
- mean +1.55%
- win 68.37%
- worst -45.34%

Therefore BUY-C is strongly supported as a **confirmation / sizing signal** after A/B.

Important accounting note: portfolio configs record 112 W3 confirmations because one confirmation belongs to a position still open at sample end. The completed-trade accuracy table contains 111 confirmed completed trades.

## 4. W3 versus W5

W5 creates more confirmations, but does not produce cleaner crypto confirmation quality.

Combined completed confirmation trades:

- W3: n=111, win 73.87%, mean +4.56%, CVaR10 -10.99%, worst -22.36%
- W5: n=154, win 74.68%, mean +4.51%, CVaR10 -11.50%, worst -32.49%

Crypto:

- W3 confirmed: n=8, win 87.50%, mean +19.77%, worst -9.31%
- W5 confirmed: n=10, win 80.00%, mean +12.91%, worst -32.49%

BTC is the clearest warning against W5:

- 50%: W3 return +20.86% versus W5 -1.64%
- 60%: W3 +22.67% versus W5 +3.65%
- 70%: W3 +23.93% versus W5 +8.92%

Decision:

`C_CONFIRMATION_WINDOW_W3 = PROMOTED_TO_NEXT_VALIDATION`

`C_CONFIRMATION_WINDOW_W5 = REJECTED_NOT_ADMITTED`

for the current BTC-led operating design.

## 5. W3 FULL_FIRST: 50 / 60 / 70 versus immediate 100%

### Combined 43 assets

Immediate 100%:

- mean return +72.98%
- median return +24.48%
- mean MDD -37.72%
- mean P5 trade -12.16%
- mean CVaR10 -13.78%
- worst trade -47.68%

50% + C-confirm:

- mean return +36.86%
- median return +24.42%
- mean MDD -22.27%
- mean P5 -6.34%
- mean CVaR10 -7.30%
- worst -23.84%
- MDD improved on 43/43
- P5 improved on 43/43
- CVaR10 improved on 43/43
- return improved on 14/43

60% + C-confirm:

- mean return +43.36%
- median return +23.98%
- mean MDD -25.48%
- mean P5 -7.52%
- mean CVaR10 -8.56%
- worst -28.61%
- MDD improved on 43/43
- P5 improved on 43/43
- CVaR10 improved on 43/43
- return improved on 16/43

70% + C-confirm:

- mean return +50.20%
- median return +23.93%
- mean MDD -28.63%
- mean P5 -8.68%
- mean CVaR10 -9.86%
- worst -33.38%
- MDD improved on 43/43
- P5 improved on 43/43
- CVaR10 improved on 43/43
- return improved on 16/43

Interpretation:

The staged designs do **not** improve aggregate trade win rate materially. Their value is different: they reduce capital at risk during unconfirmed entries, while allowing a smaller number of higher-quality C-confirmed trades to reach full size.

The 50/60/70 choices form a smooth risk-return frontier. There is no statistically unique mathematical optimum.

## 6. Stocks versus crypto

### Stocks, W3 FULL_FIRST

100%:
- mean return +72.48%
- mean MDD -35.66%
- mean P5 -10.92%
- CVaR10 -12.39%

50%:
- return +33.93%
- MDD -20.88%
- P5 -5.75%
- CVaR10 -6.64%

60%:
- return +40.62%
- MDD -23.94%
- P5 -6.80%
- CVaR10 -7.76%

70%:
- return +47.78%
- MDD -26.94%
- P5 -7.83%
- CVaR10 -8.90%

Stocks therefore pay a meaningful return cost for staged sizing, but receive broad and consistent drawdown / tail-risk reduction.

### BTC / ETH / BNB / SOL, W3 FULL_FIRST

100%:
- mean return +77.87%
- mean MDD -57.85%
- mean P5 -24.17%
- CVaR10 -27.33%

50%:
- return +65.40%
- MDD -35.81%
- P5 -12.09%
- CVaR10 -13.66%

60%:
- return +70.08%
- MDD -40.58%
- P5 -14.50%
- CVaR10 -16.40%

70%:
- return +73.79%
- MDD -45.16%
- P5 -16.92%
- CVaR10 -19.13%

The four crypto assets show a more favorable staged-entry trade-off than the stock group: much of the return is retained while drawdown and tail losses fall materially.

## 7. BTC primary-asset audit

BTC W3 FULL_FIRST:

100%:
- return +23.99%
- MDD -51.24%
- P5 -26.06%
- CVaR10 -26.56%
- worst -32.49%

50%:
- return +20.86%
- MDD -27.18%
- P5 -13.03%
- CVaR10 -13.28%
- worst -16.24%

60%:
- return +22.67%
- MDD -32.26%
- P5 -15.63%
- CVaR10 -15.93%
- worst -19.49%

70%:
- return +23.93%
- MDD -37.19%
- P5 -18.24%
- CVaR10 -18.59%
- worst -22.74%

BTC therefore shows that staged entry is not merely a cross-asset averaging artifact.

At 60%, historical return is only 1.33 percentage points below immediate 100%, while:

- MDD improves by about 18.99 pp;
- P5 improves by about 10.42 pp;
- CVaR10 improves by about 10.62 pp.

At 70%, historical return is almost unchanged from immediate 100%, but risk reduction is smaller.

At 50%, risk reduction is strongest, with a somewhat larger return sacrifice.

## 8. Bootstrap robustness

Asset-level bootstrap, 5000 resamples, fixed seed 20260930.

Combined W3 50%:

- mean return delta: -36.12 pp
- 95% CI: [-59.50, -18.66]
- mean MDD improvement: +15.45 pp
- 95% CI: [+13.61, +17.34]
- mean P5 improvement: +5.82 pp
- 95% CI: [+4.80, +6.94]
- mean CVaR10 improvement: +6.48 pp
- 95% CI: [+5.43, +7.58]

Combined W3 60%:

- mean return delta: -29.62 pp
- 95% CI: [-48.98, -14.67]
- mean MDD improvement: +12.24 pp
- 95% CI: [+10.82, +13.70]
- mean P5 improvement: +4.64 pp
- 95% CI: [+3.82, +5.53]
- mean CVaR10 improvement: +5.22 pp
- 95% CI: [+4.35, +6.11]

Combined W3 70%:

- mean return delta: -22.79 pp
- 95% CI: [-38.23, -10.63]
- mean MDD improvement: +9.09 pp
- 95% CI: [+8.03, +10.10]
- mean P5 improvement: +3.48 pp
- 95% CI: [+2.87, +4.12]
- mean CVaR10 improvement: +3.92 pp
- 95% CI: [+3.29, +4.61]

Thus the broad result is robust:

- staged sizing reliably lowers drawdown and tail loss;
- it also sacrifices mean cross-asset return versus immediate 100%;
- the return sacrifice is heavily influenced by high-return stock outliers, because the median return delta is much smaller than the mean delta.

## 9. SELECTIVE SELL interaction

### Stocks

W3 60% SELECTIVE minus W3 60% FULL_FIRST:

- mean return delta +3.05 pp
- median return delta +2.95 pp
- return improved on 27/39
- mean MDD improvement +1.93 pp
- MDD improved on 26 stocks, worsened on 11, with ties on the remainder
- mean P5 change +0.13 pp
- mean CVaR10 change +0.21 pp

The stock evidence continues to support selective A/B half-exit as a candidate.

### BTC / ETH / BNB / SOL

W3 60% SELECTIVE minus FULL_FIRST:

- mean return delta -16.78 pp
- return worse on 4/4 crypto assets
- mean MDD change -2.65 pp, i.e. worse
- P5 change -1.61 pp, i.e. worse
- CVaR10 change -1.67 pp, i.e. worse

BTC alone, 60% W3:

FULL_FIRST:
- return +22.67%
- MDD -32.26%
- P5 -15.63%
- CVaR10 -15.93%

SELECTIVE:
- return +20.76%
- MDD -29.92%
- P5 -17.11%
- CVaR10 -15.99%

BTC SELECTIVE gains a small MDD improvement but gives up return and slightly worsens tail statistics. ETH, BNB and SOL show a more clearly unfavorable selective-exit result.

Therefore a combined 43-asset average is misleading here because the 39-stock majority hides the crypto deterioration.

Decisions:

`UNIVERSAL_SELECTIVE_SELL = REJECTED_NOT_ADMITTED`

`STOCK_SELECTIVE_A_B_HALF_C_FULL = PROMOTED_TO_NEXT_VALIDATION`

`CRYPTO_SELECTIVE_A_B_HALF_C_FULL = REJECTED_NOT_ADMITTED`

`CRYPTO_FULL_FIRST = RETAINED`

The formal global SELL baseline is therefore **not** replaced by one universal selective rule.

## 10. Initial allocation decision

50%, 60%, and 70% are not three independent alpha rules. They are three points on one risk-return frontier.

The evidence does not justify separate stock and crypto percentages yet:

- the crypto sample is only four assets;
- BTC is one primary asset;
- 60% sits between the strong protection of 50% and the higher return capture of 70%;
- 60% materially reduces risk in every tested asset;
- BTC at 60% retains almost all of the tested 100% return while reducing drawdown and tail losses substantially.

For the next operating candidate:

`INITIAL_ENTRY_60 = PROMOTED_TO_NEXT_VALIDATION`

`INITIAL_ENTRY_50 = RETAINED_AS_RISK_SENSITIVITY`

`INITIAL_ENTRY_70 = RETAINED_AS_RETURN_SENSITIVITY`

No separate stock/crypto initial percentage is admitted at this stage.

## 11. Candidate BUY operating scheme

The current data-supported candidate is:

```
First valid BUY-A or BUY-B
    -> open 60%

If BUY-C onsets within the next 3 trading sessions
    -> add the remaining 40%
    -> total position becomes 100%

If no BUY-C within W3
    -> do not add later
    -> keep the original 60% until SELL logic acts

A->A / B->B / A->B / B->A
    -> no add

No time-based forced exit.
```

This is promoted for next validation, not yet declared an untouched-OOS production freeze.

## 12. Important limitation: top-up causality

This experiment compares:

- immediate 100%;
- 50/60/70 initial + C-confirm top-up.

It did **not** include a matching control that stays permanently at 50/60/70 without ever topping up.

Therefore the study establishes that:

- C-confirmed trades are higher-quality on average;
- staged C-confirm policies reduce portfolio risk;
- W3 is preferable to W5;
- 60% is a defensible middle operating candidate.

But it does **not** fully isolate the incremental causal effect of the C top-up itself versus simply remaining at the initial partial size.

Status:

`C_CONFIRMATION_AS_SIZING_SIGNAL = IMPLEMENTED_AND_VERIFIED`

`C_TOPUP_INCREMENTAL_VS_STATIC_PARTIAL = BLOCKED_BY_DATA`

A future no-add control can answer that decomposition without changing the already-frozen 50/60/70 or W3 rule.

## 13. Answers to the eight required questions

1. **50 / 60 / 70:** 60% is promoted as the balanced next candidate; 50% remains the strongest risk-control sensitivity, 70% the strongest return-capture sensitivity.
2. **W3 or W5:** W3.
3. **Does A->C / B->C top-up improve the requested metrics?** The staged policy improves MDD/P5/CVaR very consistently, while sacrificing mean return. C-confirmed trades are clearly more accurate. The incremental top-up effect versus a static partial position is not isolated by this experiment.
4. **Does staged entry work in stocks and crypto?** Risk reduction is present in both. Return retention is materially better in BTC/ETH/BNB/SOL than in stocks.
5. **Different stock/crypto initial percentages?** Not admitted yet; four crypto assets are too small a class sample to justify added parameter complexity.
6. **Versus immediate 100%:** risk falls strongly and robustly; the cost is lower mean return. BTC shows the most favorable trade-off.
7. **Does SELECTIVE SELL synergize?** Yes in stocks; no in the four crypto assets. It must not be universal.
8. **Final candidate:** 60% initial + BUY-C within W3 to 100%; crypto keeps FULL_FIRST SELL. Stock selective SELL remains a separate next-validation candidate.

## 14. OOS governance

The following are no longer untouched OOS for staged-entry rule development:

- all 39 stocks in this study;
- BTC;
- ETH;
- BNB;
- SOL.

The six cryptocurrencies previously included in the superseded 10-crypto diagnostic aggregate are also development-exposed historically, but they are not part of the final 43-asset decision universe.

## 15. Closure

`FIVEGZ5SE_STAGED_ENTRY_43_ASSET_STUDY_V2 = IMPLEMENTED_AND_VERIFIED`

`BUY_60_W3_C_CONFIRM_CANDIDATE = PROMOTED_TO_NEXT_VALIDATION`

`W5_CONFIRMATION = REJECTED_NOT_ADMITTED`

`UNIVERSAL_SELECTIVE_SELL = REJECTED_NOT_ADMITTED`

`CRYPTO_FULL_FIRST_SELL = RETAINED`

`STOCK_SELECTIVE_SELL = PROMOTED_TO_NEXT_VALIDATION`

`C_TOPUP_INCREMENTAL_VS_STATIC_PARTIAL = BLOCKED_BY_DATA`

The historical V2 baseline is preserved and is not overwritten.
