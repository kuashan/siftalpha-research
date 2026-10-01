# FIVEGZ5SE Crypto Risk Exit Statistical Audit v1

Status: **COMPUTED_COMPLETE**

Date: 2026-10-01

Universe: BTC / ETH / BNB / SOL only.

Grid:
- baseline signal-only
- HARD 5 / 8 / 10 / 12 / 15 / 20%
- TRAIL 5 / 8 / 10 / 12 / 15 / 20%
- 36 hard+trail combinations
- 49 configurations per coin
- 196 total portfolio runs

Bootstrap:
- 5000 deterministic resamples
- seed 20261001

## 1. Baseline mean across four coins

The frozen 60% + W3 BUY-C top-up + FULL_FIRST signal-only baseline is approximately:

- mean cumulative return: +68.74%
- BTC: +7.24%
- ETH: +29.39%
- BNB: +95.19%
- SOL: +143.14%

Signal-only intraday-low MDD:
- BTC -56.88%
- ETH -77.17%
- BNB -63.62%
- SOL -65.92%

## 2. Fixed hard stops

All six hard-stop levels reduce cumulative return on all four coins.

HARD_5:
- mean return delta: -79.71 pp
- 95% bootstrap CI: [-159.61, -28.37] pp
- mean intraday MDD improvement: +18.12 pp
- P5 improvement: +13.13 pp
- CVaR10 improvement: +15.20 pp
- worst-trade improvement: +24.48 pp
- total stop exits: 246
- return improved on 0/4 coins

HARD_10:
- mean return delta: -89.70 pp
- 95% CI: [-158.28, -46.58] pp
- mean intraday MDD improvement: +6.37 pp
- MDD CI crosses zero
- P5 improvement: +10.13 pp
- CVaR10 improvement: +11.92 pp
- worst-trade improvement: +20.49 pp
- total stop exits: 165
- return improved on 0/4

HARD_15:
- mean return delta: -85.29 pp
- 95% CI: [-162.81, -31.23] pp
- mean intraday MDD improvement: only +0.72 pp
- MDD CI crosses zero
- total stop exits: 116
- return improved on 0/4

HARD_20:
- mean return delta: -57.13 pp
- 95% CI: [-91.73, -22.53] pp
- mean intraday MDD effect: -0.20 pp (slightly worse)
- P5 improvement: +4.14 pp
- CVaR10 improvement: +6.36 pp
- worst-trade improvement: +13.49 pp
- total stop exits: 74
- return improved on 0/4

Thus deeper hard stops reduce stop frequency, but 20% still does not preserve the baseline return and does not produce reliable MDD improvement.

## 3. Why hard stops fail

Across the four baseline portfolios:

- total completed trades: 253
- baseline winning trades: 160

Matched stop audit:

HARD_5:
- baseline winners stopped: 78 = 48.75% of all baseline winners
- mean opportunity cost per killed winner: -11.57 pp
- improved baseline losers: 60
- mean improvement per saved loser: +9.50 pp

HARD_10:
- baseline winners stopped: 47 = 29.38%
- mean opportunity cost: -15.65 pp
- improved losers: 43
- mean saved-loss improvement: +9.42 pp

HARD_15:
- baseline winners stopped: 26 = 16.25%
- mean opportunity cost: -19.26 pp
- improved losers: 36
- mean saved-loss improvement: +7.96 pp

HARD_20:
- baseline winners stopped: 11 = 6.88%
- mean opportunity cost: -18.67 pp
- improved losers: 25
- mean saved-loss improvement: +7.70 pp

The key asymmetry is that the strategy's large winners often survive substantial interim drawdowns. Cutting even a relatively small number of them has a larger effect than the loss reduction from many stopped losers.

## 4. Trailing stops

Trailing stops show the same structural problem.

TRAIL_8:
- mean return delta: -50.14 pp
- bootstrap 95% CI: [-160.33, +56.04] pp
- mean intraday MDD improvement: +7.73 pp
- P5 improvement: +7.60 pp
- CVaR10 improvement: +9.39 pp
- worst-trade improvement: +10.95 pp
- total stop exits: 206
- return improves only on BNB

TRAIL_10:
- mean return delta: -86.78 pp
- mean intraday MDD improvement: +6.26 pp
- return improved on 0/4

Other trailing levels are also cross-coin inconsistent. BTC and SOL have no tested trailing rule that improves both return and intraday MDD.

## 5. Combined hard + trailing

The strongest risk reduction comes from tight combined stops, but at a large return cost.

HARD_5_TRAIL_5:
- mean return: +16.49%
- mean return delta vs baseline: -52.26 pp
- mean intraday MDD improvement: +26.53 pp
- risk metrics improve on all four coins
- 285 stop exits
- 82 matched baseline winners killed
- only 2/4 coins improve return

A less aggressive return/risk compromise among configurations that improve intraday MDD on at least 3/4 coins is HARD_15_TRAIL_8:

- mean return: +28.09%
- mean return delta: -40.65 pp
- bootstrap CI for return delta: [-154.49, +68.37] pp
- mean intraday MDD improvement: +10.89 pp
- P5 improvement: +7.98 pp
- CVaR10 improvement: +10.69 pp
- worst-trade improvement: +20.50 pp
- return improves only on 1/4 coins (BNB)

This is not cross-coin robust enough for admission.

## 6. Per-coin heterogeneity

BTC:
- no tested configuration improves both cumulative return and intraday MDD.

ETH:
- a small number of configurations do both, but they are not shared by BTC/SOL.

BNB:
- many trailing / combined configurations improve both return and drawdown.
- BNB is the major source of apparent success for several stop rules.

SOL:
- no tested configuration improves both cumulative return and intraday MDD.

This strongly rejects a universal fixed-percentage stop across the four-coin universe.

## 7. Period robustness

Matched trade deltas for representative stops:

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

No tested fixed rule shows stable positive matched value across all three eras.

## 8. BUY-C confirmed position diagnostic

Stops on already BUY-C-confirmed positions are uncommon but especially damaging.

HARD_10:
- confirmed matched stops: 8
- 6/8 correspond to baseline winners
- mean risk-minus-baseline trade delta: -14.31 pp

TRAIL_10:
- confirmed matched stops: 11
- 9/11 correspond to baseline winners
- mean delta: -12.18 pp

Sample sizes are small and no new rule is admitted from this stratification, but it is evidence against applying one universal loss percentage irrespective of model state.

## 9. Statistical conclusion

The study confirms that a fixed-percentage stop can mechanically improve tail statistics, but this does not translate into a robust portfolio improvement.

The cost is systematic truncation of right-tail winners.

Statuses:

`UNIVERSAL_HARD_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`

`UNIVERSAL_TRAILING_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`

`UNIVERSAL_HARD_TRAIL_COMBINATION = REJECTED_NOT_ADMITTED`

`CRYPTO_SIGNAL_ONLY_FULL_FIRST_CONTROL = RETAINED`

The concept of an emergency risk layer is NOT rejected. What is rejected is the naive fixed-percentage implementation tested here.

A future risk study should be preregistered separately and should test state-aware and/or volatility-aware emergency exits rather than another in-sample search for a fixed percentage.
