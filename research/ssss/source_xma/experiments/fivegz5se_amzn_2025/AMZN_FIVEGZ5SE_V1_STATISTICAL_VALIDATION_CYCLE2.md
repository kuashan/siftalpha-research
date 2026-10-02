# AMZN FIVEGZ5SE V1 Statistical Validation Cycle 2

Status: **PROMISING_BUT_NOT_STATISTICALLY_ADMITTED**

Date: 2026-09-29

Frozen rule under test:
`AMZN_2025_FIVEGZ5SE_V1`

No formula-native OPEN/CLEAR/REDUCE/RISK label is used as a trading decision.

## 1. Engine consistency

The full-history SCTYPE=1 reconstruction was compared against the archived
AMZN 2025 replay.

2025 five-dimension state mismatches:
- Trend: 0
- Capital: 0
- Momentum: 0
- Acceleration: 0

Therefore the historical extension uses the same deterministic state engine as
the 2025 pilot.

## 2. Frozen V1 rule

Entry at close t:

```
previous Trend <= GRAY
current Trend >= LIGHT_LONG
current Momentum >= LIGHT_LONG
current Acceleration >= LIGHT_LONG

and NOT(
  Trend improves
  AND Capital improves
  AND Momentum improves
  AND Acceleration improves
)
```

Execution: next-session open, 5 bps adverse slippage.

Exit at close t if either:

```
Trend: LONG -> LIGHT_LONG
```

or

```
Acceleration: LIGHT_SHORT -> SHORT
or
Acceleration: SHORT -> LIGHT_SHORT
```

Otherwise maximum hold = 15 trading sessions.

## 3. 2025 development-year statistics

AMZN 2025:
- return +46.50%
- MDD -7.23%
- 8 trades
- win rate 87.5%
- mean trade +4.99%
- exposure 29.2%

Bootstrap 95%:
- mean trade: +2.08% to +8.35%
- compounded return: +17.72% to +88.09%

Wilson 95% CI for win rate:
- 52.91% to 97.76%

However:
- random 8-date baseline p for mean trade ≈ 0.071
- month-matched random p for mean trade ≈ 0.458

Therefore the 2025 result alone is not sufficient evidence of an independent
timing edge.

## 4. Current-state controlled test inside 2025

Using the same current positive Trend/Momentum/Acceleration state, compare:

A. Trend newly crossed from <= GRAY to positive
vs
B. Trend was already positive.

Results:
- transition-cross n=10, mean hypothetical trade +4.95%
- persistent-positive n=63, mean +1.50%
- difference +3.44 percentage points
- one-sided permutation p ≈ 0.033

This is evidence that transition path can carry information beyond the current
state in 2025.

Exact five-state matching was possible for 7 of 10 events and produced a mean
signal-minus-control difference of approximately +4.40 percentage points.

But same-month/current-triple matching reduced the average advantage to about
+1.86 percentage points.

## 5. Continuous-value scan inside 2025

Among the V1 candidate events, no continuous variable passed a conventional
small-sample significance threshold.

Spearman results:
- RVOL20 rho -0.152, p 0.686
- Trend gap rho +0.624, p 0.057
- Trend absolute change rho +0.176, p 0.640
- normalized Momentum rho +0.030, p 0.948
- Acceleration J change rho -0.055, p 0.892
- Acceleration RSI change rho +0.139, p 0.708
- capital price gap rho -0.188, p 0.605
- MA20 slope rho -0.273, p 0.452

Trend gap is the only variable showing a suggestive monotonic relationship, but
n is too small to admit it.

No new threshold is created from this scan.

## 6. Independent historical validation: AMZN 2020-2024

The V1 rule was frozen from 2025 and applied unchanged to the prior five years.

Annual results:

| Year | V1 return | MDD | Trades | Win rate | Buy & hold |
|---|---:|---:|---:|---:|---:|
| 2020 | +4.66% | -17.18% | 7 | 42.86% | +73.53% |
| 2021 | +2.27% | -9.08% | 8 | 62.50% | +1.87% |
| 2022 | +5.43% | -13.69% | 5 | 60.00% | -49.92% |
| 2023 | +11.75% | -7.23% | 11 | 72.73% | +77.61% |
| 2024 | +27.19% | -5.09% | 9 | 77.78% | +44.63% |

Important:
V1 was positive in all five historical validation years.

Combined 2020-2024:
- V1: +56.89%
- V1 MDD: -18.94%
- trades: 40
- win rate: 65.0%
- mean trade: +1.34%
- exposure: 20.59%

Buy & hold 2020-2024:
- +133.78%
- MDD: -56.15%

Approximate CAGR:
- V1: 9.43%
- buy & hold: 18.51%

Thus V1 has lower absolute return than AMZN buy-and-hold over the five-year
bull-heavy period, but materially lower exposure and drawdown.

## 7. Holdout uncertainty

For the 40 validation trades:

Bootstrap 95% CI:
- mean trade: -0.65% to +3.34%
- compounded return: -29.42% to +243.74%

Wilson 95% win-rate interval:
- 49.51% to 77.87%

The mean-trade confidence interval crosses zero.

Therefore:
**the 2020-2024 holdout does not yet statistically prove a positive
per-trade expectation at 95% confidence.**

## 8. Local-regime/random timing control

Using the same exit logic and sampling random entry dates from the same
calendar months as the V1 signals:

- p for random mean trade >= V1 mean ≈ 0.539
- p for random compounded result >= V1 compounded result ≈ 0.568

This is a major qualification.

It suggests that a meaningful portion of V1's observed return may come from
selecting generally favorable local market periods, not purely from the exact
five-dimension transition.

## 9. Current-state controlled test in 2020-2024

Within days where the current Trend/Momentum/Acceleration state is already
positive:

- new Trend-cross events: n=51, mean hypothetical trade +1.77%
- already-positive Trend controls: n=333, mean +0.56%
- difference: +1.20 percentage points
- one-sided permutation p ≈ 0.101

Direction is consistent with 2025 but does not meet p<0.05.

Thus the transition-path hypothesis remains **promising but unconfirmed**.

## 10. Holding-period sensitivity on 2020-2024

Frozen entry + frozen exit family:

- 10-day max hold: +57.98%, MDD -19.89%
- 12-day max hold: +52.96%, MDD -18.94%
- 15-day max hold: +56.89%, MDD -18.94%
- 18-day max hold: +73.46%, MDD -18.94%
- 20-day max hold: +73.89%, MDD -18.94%

The result is not dependent on a single 15-day point.

However 18/20 days must **not** replace 15 merely because they look better on
the historical validation set. That would contaminate the holdout.

They are recorded only as robustness evidence.

## 11. Exit-family sensitivity on 2020-2024

Same frozen entry, max hold 15:

- Trend + Acceleration exit (V1): +56.89%, MDD -18.94%
- Trend-only exit: +56.48%, MDD -22.44%
- Acceleration-only exit: +46.79%, MDD -24.33%
- 2-negative-dimensions exit: +50.22%, MDD -24.73%

The combined V1 exit does not maximize raw return, but it produces the best
drawdown among these four simple exit families.

This supports retaining the combined exit for the next cross-symbol test.

## 12. Full 2020-2025 descriptive result

With the unchanged V1:

- cumulative return +129.83%
- MDD -18.94%
- 48 trades
- win rate 68.75%
- mean trade +1.95%
- exposure 22.02%

Bootstrap 95% CI for mean trade:
- +0.16% to +3.74%

Wilson 95% win-rate interval:
- 54.67% to 80.05%

Approximate CAGR:
- V1: 14.88%
- AMZN buy & hold: 16.18%

AMZN buy & hold 2020-2025:
- +145.96%
- MDD -56.15%

The full-period sample includes the 2025 development year and therefore cannot
be treated as an independent validation result.

## 13. Statistical conclusion

The correct conclusion is **not**:
"V1 is proven."

The current evidence supports:

1. V1 is positive in every year 2020-2025.
2. It substantially reduces drawdown and market exposure versus buy-and-hold.
3. The transition-path effect is directionally positive in both 2025 and the
   2020-2024 historical validation sample.
4. The exact entry edge is not yet robust to same-month random controls.
5. The 2020-2024 mean-trade bootstrap interval still crosses zero.
6. AMZN alone is insufficient for final signal admission.

Therefore the next statistically valid step is **cross-symbol validation with
the rule frozen exactly as above**.

Do not further optimize AMZN before that test.

Research state:

`FIVEGZ5SE_V1_AMZN_STATISTICAL_STATUS = PROMISING_BUT_NOT_ADMITTED`

Next gate:

`FIVEGZ5SE_V1_CROSS_SYMBOL_VALIDATION`
