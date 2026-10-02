# FIVEGZ5SE Stock Risk Exit Study Final Report v1

Status: **IMPLEMENTED_AND_VERIFIED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Question
Test whether the current 39-stock three-buy/three-sell candidate needs a universal fixed-percentage Risk Exit（风险退出）layer.

Frozen baseline:
- BUY-A / BUY-B -> 60%
- BUY-C within W3 -> add 40% to 100%
- isolated SELL-A / SELL-B -> sell 50%
- SELL-C or same-bar multi-family SELL -> full exit
- after A/B half exit, next later different SELL family -> exit remainder

Only the risk layer changed.

## 2. Experiment size
- 39 stocks
- 49 configurations per stock
- 1,911 full portfolio runs
- 5,000-resample deterministic bootstrap
- three era diagnostics

Baseline reproduction passed before interpreting stop results.

## 3. Baseline
Mean cumulative return across the 39 stocks:
- **154.89%**

Mean intraday-low MDD:
- **-30.65%**

Mean P5 trade return:
- **-7.07%**

Mean CVaR10:
- **-8.31%**

## 4. Main hard-stop result
- HARD_5: mean return 66.88%; delta -88.01 pp [95% -131.27, -50.43]; intraday MDD -27.87%; MDD improvement 2.77 pp [0.20, 5.34]; P5 delta 3.40 pp; CVaR10 delta 4.21 pp; return improved 8/39; MDD improved 25/39; stops 1752; killed winners 476; saved losers 422.
- HARD_8: mean return 80.96%; delta -73.93 pp [95% -112.09, -40.60]; intraday MDD -28.58%; MDD improvement 2.07 pp [-0.50, 4.64]; P5 delta 1.80 pp; CVaR10 delta 2.48 pp; return improved 5/39; MDD improved 24/39; stops 1051; killed winners 212; saved losers 270.
- HARD_10: mean return 88.28%; delta -66.61 pp [95% -103.07, -36.86]; intraday MDD -29.89%; MDD improvement 0.75 pp [-1.50, 2.98]; P5 delta 0.70 pp; CVaR10 delta 1.37 pp; return improved 5/39; MDD improved 21/39; stops 779; killed winners 112; saved losers 204.
- HARD_12: mean return 94.57%; delta -60.32 pp [95% -90.60, -36.38]; intraday MDD -30.96%; MDD improvement -0.32 pp [-2.54, 1.97]; P5 delta -0.24 pp; CVaR10 delta 0.40 pp; return improved 3/39; MDD improved 18/39; stops 583; killed winners 67; saved losers 157.
- HARD_15: mean return 119.66%; delta -35.23 pp [95% -63.83, -11.64]; intraday MDD -30.25%; MDD improvement 0.39 pp [-1.61, 2.31]; P5 delta -1.06 pp; CVaR10 delta -0.29 pp; return improved 11/39; MDD improved 17/39; stops 368; killed winners 28; saved losers 108.
- HARD_20: mean return 135.03%; delta -19.86 pp [95% -36.82, -5.36]; intraday MDD -30.66%; MDD improvement -0.01 pp [-1.80, 1.62]; P5 delta -0.97 pp; CVaR10 delta -0.59 pp; return improved 7/39; MDD improved 21/39; stops 196; killed winners 8; saved losers 54.

All six universal hard stops reduce mean cumulative return. HARD_5 gives the clearest risk reduction, but mean return falls by 88.01 percentage points. HARD_20 preserves more return but provides essentially no reliable aggregate MDD improvement and worsens lower-tail trade metrics.

Decision:
`UNIVERSAL_STOCK_HARD_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`

## 5. Trailing-stop result
- TRAIL_5: mean return 61.50%; delta -93.39 pp [95% -142.53, -48.70]; intraday MDD -26.70%; MDD improvement 3.94 pp [1.67, 6.39]; P5 delta 2.92 pp; CVaR10 delta 3.81 pp; return improved 9/39; MDD improved 25/39; stops 2584; killed winners 807; saved losers 491.
- TRAIL_8: mean return 85.53%; delta -69.36 pp [95% -110.28, -32.84]; intraday MDD -28.63%; MDD improvement 2.01 pp [-0.61, 4.69]; P5 delta 1.64 pp; CVaR10 delta 2.38 pp; return improved 7/39; MDD improved 22/39; stops 1524; killed winners 434; saved losers 345.
- TRAIL_10: mean return 97.76%; delta -57.13 pp [95% -94.29, -25.04]; intraday MDD -28.27%; MDD improvement 2.37 pp [0.48, 4.41]; P5 delta 0.74 pp; CVaR10 delta 1.53 pp; return improved 7/39; MDD improved 21/39; stops 1088; killed winners 273; saved losers 277.
- TRAIL_12: mean return 100.53%; delta -54.36 pp [95% -86.59, -27.43]; intraday MDD -29.79%; MDD improvement 0.86 pp [-1.05, 2.89]; P5 delta 0.12 pp; CVaR10 delta 0.80 pp; return improved 8/39; MDD improved 24/39; stops 815; killed winners 179; saved losers 213.
- TRAIL_15: mean return 100.91%; delta -53.97 pp [95% -86.73, -27.72]; intraday MDD -30.67%; MDD improvement -0.02 pp [-2.02, 1.97]; P5 delta -0.86 pp; CVaR10 delta -0.17 pp; return improved 5/39; MDD improved 23/39; stops 525; killed winners 79; saved losers 140.
- TRAIL_20: mean return 127.53%; delta -27.36 pp [95% -48.87, -11.69]; intraday MDD -31.32%; MDD improvement -0.67 pp [-2.61, 1.08]; P5 delta -1.16 pp; CVaR10 delta -0.70 pp; return improved 7/39; MDD improved 17/39; stops 264; killed winners 20; saved losers 68.

TRAIL_5 and TRAIL_10 improve several tail-risk metrics, but at very large return cost. Wider trailing stops preserve more return while losing reliable risk benefit.

Decision:
`UNIVERSAL_STOCK_TRAILING_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`

## 6. Combined hard + trailing
The most aggressive combinations deliver the largest risk compression, but they also kill the most right-tail winners and create the largest return sacrifice.

Representative:
- HARD_5_TRAIL_5: mean return 52.90%; delta -101.99 pp [95% -154.80, -56.33]; intraday MDD -26.15%; MDD improvement 4.49 pp [1.63, 7.57]; P5 delta 3.74 pp; CVaR10 delta 4.61 pp; return improved 8/39; MDD improved 24/39; stops 2719; killed winners 853; saved losers 507.
- HARD_12_TRAIL_5: mean return 62.10%; delta -92.78 pp [95% -141.92, -48.03]; intraday MDD -26.52%; MDD improvement 4.13 pp [1.74, 6.65]; P5 delta 2.91 pp; CVaR10 delta 3.83 pp; return improved 9/39; MDD improved 25/39; stops 2584; killed winners 807; saved losers 492.
- HARD_8_TRAIL_5: mean return 59.61%; delta -95.28 pp [95% -145.40, -49.82]; intraday MDD -26.53%; MDD improvement 4.11 pp [1.54, 6.80]; P5 delta 2.97 pp; CVaR10 delta 3.92 pp; return improved 9/39; MDD improved 23/39; stops 2594; killed winners 810; saved losers 494.

The least damaging combinations by mean return are still materially below the baseline and do not show reliable risk superiority:
- HARD_20_TRAIL_20: mean return 127.67%; delta -27.22 pp [95% -49.20, -10.41]; intraday MDD -31.23%; MDD improvement -0.58 pp [-2.48, 1.20]; P5 delta -1.17 pp; CVaR10 delta -0.69 pp; return improved 7/39; MDD improved 18/39; stops 271; killed winners 20; saved losers 69.
- HARD_15_TRAIL_20: mean return 117.75%; delta -37.13 pp [95% -66.48, -13.69]; intraday MDD -30.46%; MDD improvement 0.18 pp [-1.86, 2.18]; P5 delta -1.01 pp; CVaR10 delta -0.29 pp; return improved 9/39; MDD improved 18/39; stops 388; killed winners 35; saved losers 113.
- HARD_20_TRAIL_15: mean return 100.65%; delta -54.24 pp [95% -87.09, -27.78]; intraday MDD -30.77%; MDD improvement -0.12 pp [-2.18, 1.91]; P5 delta -0.87 pp; CVaR10 delta -0.19 pp; return improved 5/39; MDD improved 23/39; stops 526; killed winners 79; saved losers 139.

Decision:
`UNIVERSAL_STOCK_HARD_TRAIL_COMBINATION = REJECTED_NOT_ADMITTED`

## 7. What the data mean
The stock strategy, like the Crypto version, contains economically important recovering / right-tail winners.

Tight fixed stops:
- reduce worst losses;
- improve P5/CVaR;
- reduce some drawdowns;
- but repeatedly cut trades that later recover and contribute materially to cumulative return.

Wide fixed stops:
- trigger less often;
- preserve more right-tail winners;
- but provide too little reliable risk reduction to justify adding an always-on universal rule.

The result does **not** mean risk control is useless. It means loss percentage alone is too crude.

## 8. Current stock control remains
`STOCK_SELECTIVE_SIGNAL_EXIT_CONTROL = RETAINED`

Current candidate stays:

```
BUY-A / BUY-B -> 60%
BUY-C within W3 -> +40% to 100%

isolated SELL-A -> sell 50%
isolated SELL-B -> sell 50%
SELL-C -> full exit
same-bar >=2 SELL families -> full exit
after A/B half sale -> next later distinct SELL exits remainder
```

No universal 5 / 8 / 10 / 12 / 15 / 20% hard stop or trailing stop is added.

## 9. Next valid direction
A future preregistered study may test:
- ATR / realized-volatility normalized emergency exits;
- adverse price move + five-dimension state deterioration jointly;
- different emergency handling before and after BUY-C confirmation;
- catastrophe-only backstops rather than ordinary trade stops.

Status:
`STATE_OR_VOLATILITY_AWARE_STOCK_RISK_EXIT = PROMOTED_TO_NEXT_VALIDATION`

## 10. Closure
`STOCK_RISK_EXIT_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`

This round is CLOSED.
