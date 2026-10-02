# FIVEGZ5SE Crypto Risk Exit Study Final Report v1

Status: **IMPLEMENTED_AND_VERIFIED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Question

The study tested whether the current BTC / ETH / BNB / SOL three-buy/three-sell system is missing a useful fixed-loss Risk Exit（风险退出）layer.

The frozen trading baseline remained:

- BUY-A / BUY-B -> 60%
- BUY-C within W3 -> add 40% to 100%
- first SELL-A / SELL-B / SELL-C -> 100% exit

Only the independent risk layer changed.

## 2. Data and experiment size

Universe:
- BTC
- ETH
- BNB
- SOL

History:
- BTC: 2017-08-17 to 2026-05-05
- ETH: 2017-08-17 to 2026-04-19
- BNB: 2017-11-06 to 2026-04-19
- SOL: 2020-08-11 to 2026-04-19

Real Binance spot UTC daily OHLCV.

Configurations:
- signal-only baseline
- hard stops at 5 / 8 / 10 / 12 / 15 / 20%
- trailing stops at 5 / 8 / 10 / 12 / 15 / 20%
- all 36 hard+trailing pairs

49 configurations per coin.
196 complete portfolio runs.

The new simulator reproduced the previous frozen baseline to floating-point precision before risk exits were enabled.

## 3. Main result

A fixed percentage risk exit does reduce individual tail losses.

But across the four-coin universe, every tested universal hard-stop level sacrifices too much of the strategy's right-tail winners.

The same structural problem appears in trailing stops and hard+trailing combinations.

Therefore the data do NOT support adding a universal fixed loss percentage to the current production candidate.

## 4. Hard-stop evidence

Four-coin frozen signal-only baseline mean cumulative return:
- approximately +68.74%

HARD_5:
- mean return delta: -79.71 percentage points
- intraday MDD improvement: +18.12 pp
- P5 improvement: +13.13 pp
- CVaR10 improvement: +15.20 pp
- 246 stop exits
- return improved on 0/4 coins

HARD_10:
- mean return delta: -89.70 pp
- intraday MDD improvement: +6.37 pp
- 165 stop exits
- return improved on 0/4

HARD_15:
- mean return delta: -85.29 pp
- intraday MDD improvement: only +0.72 pp
- 116 stop exits
- return improved on 0/4

HARD_20:
- mean return delta: -57.13 pp
- intraday MDD effect: approximately flat / slightly worse
- P5 improves +4.14 pp
- CVaR10 improves +6.36 pp
- 74 stop exits
- return improved on 0/4

No tested hard-stop percentage is admitted.

## 5. Why even a 20% stop fails

Across the four baseline portfolios:

- completed trades: 253
- winning trades: 160

HARD_20:
- 74 total stops
- 62 stops can be directly matched to the same baseline entry
- 11 of those stop events cut trades that the baseline eventually closed profitably
- those killed winners represent 6.88% of all baseline winning trades
- mean opportunity cost per killed winner: -18.67 pp
- 25 baseline losers were improved
- mean improvement per saved loser: +7.70 pp

The strategy has asymmetric payoff.

A relatively small number of winners contribute large right-tail gains. A stop can save several moderate losers but still destroy more expectancy by truncating a few large recovering winners.

This pattern is also visible at 5 / 8 / 10 / 12 / 15%.

## 6. Trailing stops

Trailing stops are not a general solution.

Example TRAIL_8:
- mean return delta: -50.14 pp
- mean intraday MDD improvement: +7.73 pp
- P5 improvement: +7.60 pp
- CVaR10 improvement: +9.39 pp
- total stop exits: 206
- return improves only on BNB

BTC and SOL have no tested trailing configuration that improves both return and intraday MDD.

## 7. Combined risk exits

The strongest risk reduction appears in tight combined rules, but they still destroy too much expected return.

HARD_5 + TRAIL_5:
- mean return: +16.49%
- mean return delta: -52.26 pp
- mean intraday MDD improvement: +26.53 pp
- risk improves on all four coins
- 285 stop exits
- 82 matched baseline winners killed
- only 2/4 coins improve return

A less aggressive example, HARD_15 + TRAIL_8:
- mean return: +28.09%
- mean return delta: -40.65 pp
- mean intraday MDD improvement: +10.89 pp
- P5 improvement: +7.98 pp
- CVaR10 improvement: +10.69 pp
- return improves only on BNB

No combined rule is admitted.

## 8. Cross-coin inconsistency

BTC:
- zero tested risk configurations improve both cumulative return and intraday MDD.

ETH:
- a few configurations do, but they do not transfer to BTC / SOL.

BNB:
- many trailing / combined risk exits improve both return and drawdown.
- BNB is the major source of apparent success in several pooled configurations.

SOL:
- zero tested configurations improve both return and intraday MDD.

A universal fixed-percentage rule would therefore be driven by coin-specific behavior rather than robust cross-coin evidence.

## 9. Time-period inconsistency

Representative matched-trade deltas:

HARD_10:
- 2017-2020: -0.91 pp
- 2021-2023: -6.86 pp
- 2024-2026: -1.51 pp

HARD_15:
- 2017-2020: -0.93 pp
- 2021-2023: -7.38 pp
- 2024-2026: -3.21 pp

HARD_20:
- 2017-2020: +0.20 pp
- 2021-2023: -2.75 pp
- 2024-2026: -4.46 pp

TRAIL_8:
- 2017-2020: -0.33 pp
- 2021-2023: -5.26 pp
- 2024-2026: -1.26 pp

No fixed rule is positive across all three eras.

## 10. BUY-C confirmed positions

A fixed risk stop appears especially dangerous after BUY-C confirmation.

HARD_10:
- 8 confirmed matched stops
- 6/8 corresponding baseline trades eventually profit
- mean risk-minus-baseline delta: -14.31 pp

TRAIL_10:
- 11 confirmed matched stops
- 9/11 baseline trades eventually profit
- mean delta: -12.18 pp

The sample is too small to create a new state-dependent rule from this study, but it rejects the idea that the same fixed loss threshold should blindly apply to every model state.

## 11. Decision

The following are formally rejected for the current Crypto candidate:

`UNIVERSAL_HARD_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`

`UNIVERSAL_TRAILING_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`

`UNIVERSAL_HARD_TRAIL_COMBINATION = REJECTED_NOT_ADMITTED`

The current operating control remains:

`CRYPTO_SIGNAL_ONLY_FULL_FIRST_CONTROL = RETAINED`

Current logic remains:

```
BUY-A / BUY-B -> 60%
BUY-C within W3 -> +40% to 100%

SELL-A -> full exit
SELL-B -> full exit
SELL-C -> full exit (until the separate SELL-C study changes it)
```

No fixed 5 / 8 / 10 / 12 / 15 / 20% stop is added.

## 12. What this study does NOT mean

It does NOT prove that Risk Exit（风险退出）is useless.

It proves that a universal fixed percentage based only on loss size is too crude for the current strategy.

The data show why:
- volatility differs materially by coin and era;
- profitable trades can experience large interim drawdowns;
- BUY-C-confirmed positions behave differently from weak / unconfirmed positions;
- right-tail winners are economically more important than a simple win/loss count suggests.

## 13. Next valid research direction

A future study may test a preregistered **State-Aware / Volatility-Aware Risk Exit（状态感知 / 波动率感知风险退出）**.

Candidate concepts for a new protocol, not admitted rules:
- volatility-normalized emergency exits rather than one fixed percentage;
- state deterioration + adverse price move as a joint condition;
- different emergency handling before vs after BUY-C confirmation;
- a true catastrophe backstop wider than the 5-20% range, preregistered before seeing its results.

No specific threshold from those concepts is admitted by this study.

Status:

`STATE_OR_VOLATILITY_AWARE_RISK_EXIT = PROMOTED_TO_NEXT_VALIDATION`

## 14. Closure

`CRYPTO_RISK_EXIT_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`

This round is CLOSED.

Do not reopen 5 / 8 / 10 / 12 / 15 / 20% universal fixed stop searches unless new untouched validation data or a materially different preregistered hypothesis justifies it.
