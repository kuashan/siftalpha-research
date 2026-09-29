# AMZN 2025 FIVEGZ5SE Full Trading Backtest & V1 Logic

Status: **EXPLORATORY_V1_BACKTEST_COMPLETE**

Date: 2026-09-29

## Scope

- Symbol: AMZN
- Period: 2025-01-02 through 2025-12-31
- FIVEGZ5SE market mode: `SCTYPE=1`
- Initial capital: $10,000
- Long/cash only
- Signal at close t
- Execution at next-session open
- 5 bps adverse slippage on each buy and sell
- Commission: $0
- No use of the original formula's OPEN/CLEAR/REDUCE/RISK labels as decision rules

The formula-native action labels were ignored during signal discovery.

## Research process

The replay was analyzed in layers:
1. single-dimension t-1 -> t transitions;
2. pair interactions;
3. multi-dimension directional changes;
4. continuous-variable filters;
5. event de-duplication;
6. grid search over entry/exit/holding-period combinations;
7. chronological split:
   - Jan-Jun discovery/training;
   - Jul-Sep validation;
   - Oct-Dec final temporal check.

A total of 64,920 entry/exit/holding-period combinations were evaluated in the
initial whole-year grid. A stricter chronological search retained 49,970
train-eligible combinations after requiring minimum training trades.

Important caveat:
the calendar split is a robustness check, not a pristine untouched holdout,
because exploratory full-year transition statistics had already been inspected
before the split. Final confirmation therefore requires another year and/or
other symbols.

## Rejected simple hypothesis

"More dimensions turn bullish simultaneously = stronger buy" failed.

When Trend, Capital, Momentum and Acceleration all improved on the same bar:

- n = 9 de-duplicated events
- 5-day mean return = -1.84%
- 5-day median = -2.33%
- 5-day positive rate = 22.2%
- 20-day mean = -2.21%

Therefore a simultaneous four-core-dimension jump is treated as an
**anti-chase veto candidate**, not a buy confirmation.

## V1 entry logic

The most robust simple transition rule retained after chronological checks is:

At close t:

```
previous Trend <= GRAY
current Trend >= LIGHT_LONG

current Momentum >= LIGHT_LONG
current Acceleration >= LIGHT_LONG

NOT(
    dTrendState > 0
    AND dCapitalState > 0
    AND dMomentumState > 0
    AND dAccelerationState > 0
)
```

Interpretation:

- Trend must newly cross from non-positive/neutral into a positive state.
- Momentum and Acceleration must already be positive on the current bar.
- A bar where all four core dimensions jump upward simultaneously is rejected
  as a chase/over-extension candidate.
- No original author action label is used.
- No RVOL threshold is required in V1; the earlier 0.8-1.5 filter was not
  retained as the most robust chronological rule.

Execution:
buy at next-session open with 5 bps adverse slippage.

## V1 exit logic

At close t, exit at next-session open when either:

### A. Trend degrades from strongest state

```
Trend: LONG -> LIGHT_LONG
```

or

### B. Acceleration remains in the bearish zone and changes severity

```
Acceleration: LIGHT_SHORT -> SHORT
```

or

```
Acceleration: SHORT -> LIGHT_SHORT
```

If neither exit fires, maximum holding time is 15 trading sessions.

The SHORT -> LIGHT_SHORT case is retained because AMZN 2025 showed that merely
becoming "less negative" while staying inside the negative acceleration zone
did not reliably mean the downside was over.

## Full-year result

Initial:
- $10,000.00

Final:
- **$14,649.57**

Cumulative return:
- **+46.50%**

Close-to-close maximum drawdown:
- **-7.23%**

Annualized daily Sharpe:
- **1.71**

Exposure:
- **29.2% of sessions**

Trades:
- **8**

Winning trades:
- **7 / 8 = 87.5%**

Average trade:
- **+4.99%**

Median trade:
- **+3.29%**

Best trade:
- **+14.00%**

Worst trade:
- **-0.70%**

## AMZN buy-and-hold benchmark

Using first 2025 open entry and final 2025 close exit, with the same 5 bps
entry/exit slippage:

- return: **+3.86%**
- close-to-close max drawdown: **-30.88%**

This comparison is descriptive only; the strategy has only eight trades.

## Chronological robustness

### Jan-Jun discovery/training

Strategy:
- **+25.20%**

AMZN buy-and-hold:
- **-1.29%**
- max drawdown -30.88%

### Jul-Sep validation

Strategy:
- **+5.94%**

AMZN buy-and-hold:
- **-0.07%**
- max drawdown -9.59%

### Oct-Dec temporal check

Strategy:
- **+10.45%**

AMZN buy-and-hold:
- **+6.09%**
- max drawdown -14.51%

The strategy remained positive in all three chronological segments.

## Trade ledger

| Signal | Entry | Exit | Hold | Return | Exit reason |
|---|---|---|---:|---:|---|
| 2025-01-21 | 2025-01-22 | 2025-01-30 | 6 | +2.10% | state exit |
| 2025-04-02 | 2025-04-03 | 2025-04-14 | 7 | +2.00% | state exit |
| 2025-04-23 | 2025-04-24 | 2025-05-15 | 15 | +14.00% | state exit |
| 2025-05-22 | 2025-05-23 | 2025-06-13 | 14 | +5.46% | state exit |
| 2025-07-18 | 2025-07-21 | 2025-07-25 | 4 | +2.72% | state exit |
| 2025-08-22 | 2025-08-25 | 2025-09-09 | 10 | +3.86% | state exit |
| 2025-09-16 | 2025-09-17 | 2025-09-19 | 2 | -0.70% | state exit |
| 2025-10-09 | 2025-10-10 | 2025-10-31 | 15 | +10.45% | time exit |

## Concentration stress test

To assess whether the result depends entirely on one or two lucky trades:

- Full compounded return: +46.50%
- Remove best trade (+14.00%): approximately **+28.51%**
- Remove two best trades (+14.00% and +10.45%): approximately **+16.35%**

The result is still positive after removing the largest winners, but the sample
remains too small for statistical admission.

## Holding-period sensitivity

Same V1 entry/exit family:

- max hold 5 days: +15.47%, MDD -9.23%
- max hold 7 days: +19.83%, MDD -7.23%
- max hold 10 days: +23.31%, MDD -7.23%
- max hold 15 days: **+46.50%, MDD -7.23%**
- max hold 20 days: +45.87%, MDD -7.23%

The result is not a knife-edge at exactly 15 days: 20 days remains similar.
However 15-20 days materially outperform 5-10 days in this one-year sample.

## Interpretation

The current AMZN evidence suggests that the useful structure is not:
- "all red = buy";
- "all green = sell";
- original author action labels.

The better candidate behavior is:

1. **Entry on a coordinated but not explosive transition into positive trend**:
   trend crosses from non-positive to positive while momentum and acceleration
   are positive.
2. **Avoid synchronous four-dimension surges**:
   they behaved more like late chase events in this sample.
3. **Exit when the strongest trend starts to lose strength or when acceleration
   remains trapped in the bearish zone**.
4. **Allow winners time to develop**:
   15-20 sessions performed much better than a forced 5-day exit.

## What is still unproven

This is not yet a universal trading rule.

Reasons:
- one stock;
- one year;
- only 8 final V1 trades;
- exploratory statistics were viewed before the calendar split;
- exact state-engine parity with Futu still needs final spot checks;
- no cross-stock or cross-year OOS validation yet.

Therefore:

`AMZN_2025_FIVEGZ5SE_V1 = EXPLORATORY_BACKTEST_PASS`

Not yet:

`IMPLEMENTED_AND_VERIFIED`

## Next optimization cycle

The next AMZN-only cycle should not reopen hundreds of arbitrary rules.

Freeze V1 and test only controlled changes:

1. partial exit vs full exit on the first deterioration signal;
2. 15 vs 20 day maximum hold;
3. whether capital-state confirmation improves or only removes good trades;
4. whether continuous Momentum/Acceleration strength margins improve V1;
5. whether a re-entry cooldown after exit improves drawdown;
6. month-by-month and trade-by-trade attribution.

After that, the rule must be tested on additional symbols/years before any
threshold is promoted.

Closure:
`AMZN_2025_V1_FULL_TRADING_BACKTEST = COMPLETE`
