# FIVEGZ5SE Stock Risk Exit Study Final Report v1.1

Status: **IMPLEMENTED_AND_VERIFIED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

This v1.1 report supersedes the invalidated first-pass closure documented in `CORRECTION_NOTE_v1a.md`.

## 1. Frozen baseline
- BUY-A / BUY-B -> 60%
- BUY-C within W3 -> +40% to 100%
- isolated SELL-A / SELL-B -> sell 50%
- SELL-C or same-bar multi-family SELL -> full exit
- after A/B half sale -> next later different SELL exits the remainder

No BUY/SELL definition was changed.

## 2. Experiment
- 39 stocks
- 49 configurations per stock
- 1,911 corrected runs
- hard stops: 5 / 8 / 10 / 12 / 15 / 20%
- trailing stops: 5 / 8 / 10 / 12 / 15 / 20%
- all 36 hard+trailing combinations
- 5,000-resample deterministic bootstrap
- three-era diagnostics
- matched baseline trade audit
- sector-diversity inspection

Baseline reproduction passed before interpretation.

## 3. Baseline
Mean cumulative return: **154.92%**

Mean intraday-low MDD: **-30.65%**

Mean P5: **-6.95%**

Mean CVaR10: **-8.22%**

## 4. Hard-stop evidence
- HARD_5: mean return 66.90%; delta -88.02 pp (95% -131.28 to -50.44); intraday MDD -27.87%; MDD improvement 2.77 pp (95% 0.20 to 5.34); P5 delta 3.28 pp; CVaR10 delta 4.11 pp; return improved 8/39; MDD improved 25/39; stops 1752; killed winners 476; saved losers 414.
- HARD_8: mean return 80.98%; delta -73.94 pp (95% -112.11 to -40.61); intraday MDD -28.58%; MDD improvement 2.07 pp (95% -0.50 to 4.64); P5 delta 1.68 pp; CVaR10 delta 2.39 pp; return improved 5/39; MDD improved 24/39; stops 1051; killed winners 212; saved losers 263.
- HARD_10: mean return 88.30%; delta -66.62 pp (95% -103.09 to -36.88); intraday MDD -29.89%; MDD improvement 0.75 pp (95% -1.50 to 2.98); P5 delta 0.58 pp; CVaR10 delta 1.29 pp; return improved 5/39; MDD improved 21/39; stops 779; killed winners 112; saved losers 198.
- HARD_12: mean return 94.59%; delta -60.33 pp (95% -90.62 to -36.38); intraday MDD -30.96%; MDD improvement -0.32 pp (95% -2.54 to 1.97); P5 delta -0.36 pp; CVaR10 delta 0.33 pp; return improved 3/39; MDD improved 18/39; stops 583; killed winners 67; saved losers 154.
- HARD_15: mean return 119.69%; delta -35.23 pp (95% -63.83 to -11.64); intraday MDD -30.25%; MDD improvement 0.39 pp (95% -1.61 to 2.31); P5 delta -1.18 pp; CVaR10 delta -0.35 pp; return improved 11/39; MDD improved 17/39; stops 368; killed winners 28; saved losers 108.
- HARD_20: mean return 135.06%; delta -19.86 pp (95% -36.82 to -5.36); intraday MDD -30.66%; MDD improvement -0.01 pp (95% -1.80 to 1.62); P5 delta -1.07 pp; CVaR10 delta -0.60 pp; return improved 7/39; MDD improved 21/39; stops 196; killed winners 8; saved losers 54.

No hard-stop level is admitted.

Key trade-off:
- HARD_5 materially improves tail metrics and average MDD, but mean cumulative return falls by 88.02 percentage points.
- HARD_10 still loses 66.62 pp of mean return while aggregate MDD improvement is much weaker.
- HARD_20 loses 19.86 pp of mean return and provides no reliable average MDD benefit; P5 and CVaR10 are worse than baseline.

`UNIVERSAL_STOCK_HARD_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`

## 5. Trailing-stop evidence
- TRAIL_5: mean return 61.51%; delta -93.41 pp (95% -142.55 to -48.71); intraday MDD -26.70%; MDD improvement 3.94 pp (95% 1.67 to 6.39); P5 delta 2.79 pp; CVaR10 delta 3.72 pp; return improved 9/39; MDD improved 25/39; stops 2584; killed winners 805; saved losers 483.
- TRAIL_8: mean return 85.54%; delta -69.38 pp (95% -110.30 to -32.85); intraday MDD -28.63%; MDD improvement 2.01 pp (95% -0.61 to 4.69); P5 delta 1.51 pp; CVaR10 delta 2.30 pp; return improved 7/39; MDD improved 22/39; stops 1524; killed winners 433; saved losers 338.
- TRAIL_10: mean return 97.78%; delta -57.14 pp (95% -94.30 to -25.05); intraday MDD -28.27%; MDD improvement 2.37 pp (95% 0.48 to 4.41); P5 delta 0.61 pp; CVaR10 delta 1.44 pp; return improved 7/39; MDD improved 21/39; stops 1088; killed winners 272; saved losers 271.
- TRAIL_12: mean return 100.55%; delta -54.37 pp (95% -86.59 to -27.44); intraday MDD -29.79%; MDD improvement 0.86 pp (95% -1.05 to 2.89); P5 delta -0.01 pp; CVaR10 delta 0.73 pp; return improved 8/39; MDD improved 24/39; stops 815; killed winners 178; saved losers 209.
- TRAIL_15: mean return 100.94%; delta -53.98 pp (95% -86.74 to -27.72); intraday MDD -30.67%; MDD improvement -0.02 pp (95% -2.02 to 1.97); P5 delta -0.96 pp; CVaR10 delta -0.26 pp; return improved 5/39; MDD improved 23/39; stops 525; killed winners 79; saved losers 137.
- TRAIL_20: mean return 127.56%; delta -27.36 pp (95% -48.88 to -11.70); intraday MDD -31.32%; MDD improvement -0.67 pp (95% -2.61 to 1.08); P5 delta -1.26 pp; CVaR10 delta -0.72 pp; return improved 7/39; MDD improved 17/39; stops 264; killed winners 20; saved losers 67.

No trailing-stop level is admitted.

TRAIL_5 and TRAIL_10 compress tail losses and drawdown, but sacrifice too much return. Wider trailing stops preserve more return but stop providing reliable downside improvement.

`UNIVERSAL_STOCK_TRAILING_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`

## 6. Combined rules
The strongest MDD-reduction combinations are:
- HARD_5_TRAIL_5: mean return 52.91%; delta -102.01 pp (95% -154.82 to -56.35); intraday MDD -26.15%; MDD improvement 4.49 pp (95% 1.63 to 7.57); P5 delta 3.61 pp; CVaR10 delta 4.53 pp; return improved 8/39; MDD improved 24/39; stops 2719; killed winners 851; saved losers 499.
- HARD_12_TRAIL_5: mean return 62.12%; delta -92.80 pp (95% -141.95 to -48.04); intraday MDD -26.52%; MDD improvement 4.13 pp (95% 1.74 to 6.65); P5 delta 2.79 pp; CVaR10 delta 3.74 pp; return improved 9/39; MDD improved 25/39; stops 2584; killed winners 805; saved losers 484.
- HARD_8_TRAIL_5: mean return 59.62%; delta -95.30 pp (95% -145.44 to -49.83); intraday MDD -26.53%; MDD improvement 4.11 pp (95% 1.54 to 6.80); P5 delta 2.85 pp; CVaR10 delta 3.82 pp; return improved 9/39; MDD improved 23/39; stops 2594; killed winners 808; saved losers 486.
- HARD_10_TRAIL_5: mean return 60.78%; delta -94.14 pp (95% -143.83 to -48.99); intraday MDD -26.57%; MDD improvement 4.07 pp (95% 1.66 to 6.58); P5 delta 2.77 pp; CVaR10 delta 3.74 pp; return improved 8/39; MDD improved 24/39; stops 2586; killed winners 805; saved losers 485.

The combinations that preserve the most return are:
- HARD_20_TRAIL_20: mean return 127.70%; delta -27.22 pp (95% -49.20 to -10.42); intraday MDD -31.23%; MDD improvement -0.58 pp (95% -2.48 to 1.20); P5 delta -1.29 pp; CVaR10 delta -0.71 pp; return improved 7/39; MDD improved 18/39; stops 271; killed winners 20; saved losers 68.
- HARD_15_TRAIL_20: mean return 117.78%; delta -37.14 pp (95% -66.48 to -13.69); intraday MDD -30.46%; MDD improvement 0.18 pp (95% -1.86 to 2.18); P5 delta -1.13 pp; CVaR10 delta -0.35 pp; return improved 9/39; MDD improved 18/39; stops 388; killed winners 35; saved losers 112.
- HARD_20_TRAIL_15: mean return 100.67%; delta -54.25 pp (95% -87.10 to -27.79); intraday MDD -30.77%; MDD improvement -0.12 pp (95% -2.18 to 1.91); P5 delta -0.97 pp; CVaR10 delta -0.29 pp; return improved 5/39; MDD improved 23/39; stops 526; killed winners 79; saved losers 136.
- HARD_20_TRAIL_12: mean return 100.34%; delta -54.58 pp (95% -86.79 to -27.64); intraday MDD -29.93%; MDD improvement 0.71 pp (95% -1.29 to 2.79); P5 delta -0.01 pp; CVaR10 delta 0.70 pp; return improved 8/39; MDD improved 24/39; stops 816; killed winners 178; saved losers 209.

None earns admission.

`UNIVERSAL_STOCK_HARD_TRAIL_COMBINATION = REJECTED_NOT_ADMITTED`

## 7. Why fixed stops fail
The stock strategy has the same broad structural issue found in Crypto: a fixed loss percentage is blind to state and volatility.

Tight stops:
- save many losers;
- improve P5 / CVaR / worst trade;
- sometimes improve MDD;
- but repeatedly cut recovering winners and reduce exposure to large right-tail outcomes.

Wide stops:
- kill fewer winners;
- but trigger too late and too rarely to deliver reliable aggregate risk reduction.

Therefore the missing risk layer is not well represented by a universal loss percentage.

## 8. Current stock candidate remains
`STOCK_SELECTIVE_SIGNAL_EXIT_CONTROL = RETAINED`

```
BUY-A / BUY-B -> 60%
BUY-C within W3 -> +40% to 100%

isolated SELL-A -> sell 50%
isolated SELL-B -> sell 50%
SELL-C -> full exit
same-bar >=2 SELL families -> full exit
after A/B half sale -> next later distinct SELL exits remainder
```

No universal fixed 5 / 8 / 10 / 12 / 15 / 20% hard or trailing stop is added.

## 9. Next valid risk research
The evidence supports a new preregistered study of:
- ATR / realized-volatility-normalized emergency exits;
- adverse price move + five-dimension state deterioration jointly;
- different emergency handling before vs after BUY-C confirmation;
- catastrophe-only backstops rather than ordinary fixed stops.

`STATE_OR_VOLATILITY_AWARE_STOCK_RISK_EXIT = PROMOTED_TO_NEXT_VALIDATION`

## 10. Closure
`STOCK_RISK_EXIT_STUDY_V1_1 = IMPLEMENTED_AND_VERIFIED`

This corrected round is CLOSED.
