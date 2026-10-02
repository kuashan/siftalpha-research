# AMD 2020-2023 FIVEGZ5SE Three-Buy / Three-Sell Validation

Status: **EXTERNAL_VALIDATION_FAIL_INCREMENTAL**

Date: 2026-09-30

## 1. Scope

Symbol:
- AMD (Advanced Micro Devices)

Validation window:
- 2020-01-02 through 2023-12-29
- 1006 trading sessions

Warm-up:
- 2019-01-02 through 2019-12-31
- used only to initialize long rolling dependencies
- no 2019 return is included in the validation result

Strategy under test:

### BUY

BUY-A:
```
Trend W3 slope > 0
AND Momentum = SHORT
AND Momentum W5 slope < 0
```

BUY-B:
```
Capital = GRAY
AND Capital W1 net < 0
AND Acceleration W3 slope > 0
```

BUY-C / B-F5 neutral-zone recovery:
```
Trend = GRAY
AND Capital W3 net > 0
AND Capital positive on >=2 of last 3 bars
AND Capital W5 slope > 0
AND Anomaly = GRAY
```

### SELL

SELL-A:
```
Trend = GRAY
AND Acceleration positive on >=3 of last 5 bars
AND >=3 bullish dimensions on >=2 of last 3 bars
```

SELL-B:
```
Capital W5 slope < 0
AND Momentum >= LIGHT_LONG
AND Anomaly W1 net < 0
```

SELL-C:
```
Momentum = LONG
AND Anomaly W3 net > 0
AND >=3 bullish dimensions on >=2 of last 3 bars
```

Execution:
- signal at close t
- next-session open execution
- 5 bps adverse slippage each side
- long/cash only
- one position at a time
- no pyramiding
- same-bar SELL vetoes entry
- **no maximum holding period**
- original formula-native operation prompts are not used

## 2. Data verification

Primary validation series:
- Twelve Data daily OHLCV
- 2019-01-02 through 2023-12-29

Cross-check source:
- `Devesh176/Replicating_portfolio/data/AMD.csv`

Overlap audit for 2020-01-02 through 2023-12-29:
- matched sessions: **1006**
- missing dates: **0**
- maximum close absolute difference: < 0.000005 USD
- maximum open absolute difference: < 0.000005 USD
- maximum observed volume difference: approximately 0.205%

The two sources are effectively identical for strategy purposes.

## 3. V2 baseline: two buys / three sells

BUY-A OR BUY-B

SELL-A OR SELL-B OR SELL-C

Result:
- initial capital: $10,000
- final capital: **$12,061.59**
- cumulative return: **+20.62%**
- maximum drawdown: **-43.91%**
- annualized daily Sharpe: **0.31**
- closed trades: **25**
- win rate: **60.00%**
- mean trade: **+1.34%**
- median trade: **+1.71%**
- exposure: **36.98%**

Calendar-year portfolio returns:
- 2020: **+29.16%**
- 2021: **+2.20%**
- 2022: **-32.21%**
- 2023: **+30.62%**

Entry reasons:
- BUY-A: 18 executed entries
- BUY-B: 7 executed entries

Exit reasons:
- SELL-A: 11
- SELL-B: 3
- SELL-C: 11

## 4. Three-buy / three-sell candidate

BUY-A OR BUY-B OR BUY-C

SELL-A OR SELL-B OR SELL-C

Result:
- initial capital: $10,000
- final capital: **$11,924.03**
- cumulative return: **+19.24%**
- maximum drawdown: **-43.91%**
- annualized daily Sharpe: **0.30**
- closed trades: **26**
- win rate: **57.69%**
- mean trade: **+1.25%**
- median trade: **+1.53%**
- exposure: **37.38%**

Calendar-year portfolio returns:
- 2020: **+29.16%**
- 2021: **+2.20%**
- 2022: **-32.21%**
- 2023: **+29.13%**

Entry reasons:
- BUY-A: 18
- BUY-B: 7
- BUY-C: **1**

Exit reasons:
- SELL-A: 11
- SELL-B: 4
- SELL-C: 11

## 5. Incremental effect of BUY-C

Compared with V2:

- return: +20.62% -> **+19.24%**
- delta: **-1.38 percentage points**
- MDD: -43.91% -> **-43.91%**
- closed trades: 25 -> **26**
- win rate: 60.00% -> **57.69%**
- exposure: 36.98% -> **37.38%**

The single additional portfolio entry caused by BUY-C was:

- signal: 2023-07-13
- entry: 2023-07-14
- exit signal: 2023-07-19
- exit: 2023-07-20
- exit family: SELL-B
- trade return: **-1.14%**

Thus BUY-C did not add portfolio value on AMD 2020-2023.

## 6. BUY-C event-level audit

BUY-C generated **8 raw onset events**.

Only 2 were within ±3 trading sessions of an existing V2 buy event.
Six were genuinely new relative to V2 at that tolerance.

All BUY-C events:
- 5-day mean: **+1.59%**
- 10-day mean: **+3.35%**
- 20-day mean: **+1.40%**
- 10-day positive rate: **37.50%**

Six ±3-day novel BUY-C events:
- 10-day mean: **+3.41%**
- 10-day positive rate: **33.33%**

The positive mean is concentrated in a small number of large winners:
- 2023-03-03: +19.27% at 10 days
- 2023-05-02: +21.47% at 10 days

Several other novel BUY-C events were negative:
- 2021-01-25: -3.62%
- 2021-08-24: -1.81%
- 2021-12-23: -10.51%
- 2023-07-13: -4.36%

Interpretation:

BUY-C does **not** reproduce the stable AMZN behavior on AMD.
Its AMD mean is driven by a minority of large winners rather than high event
consistency.

## 7. Buy-and-hold reference

AMD buy-and-hold over 2020-01-02 through 2023-12-29,
using the same 5 bps entry/exit slippage:

- cumulative return: **+214.26%**
- maximum drawdown: **-65.45%**

Calendar-year buy-and-hold:
- 2020: +86.78%
- 2021: +55.90%
- 2022: -56.89%
- 2023: +130.26%

The strategy materially reduced drawdown relative to buy-and-hold but captured
only a small fraction of AMD's long-term appreciation.

This is especially visible in:
- 2021
- 2023

## 8. Main failure mode

The largest portfolio weakness is not only BUY-C.

The existing three sell families also allow very large losses before exit on AMD.

Examples:
- BUY-A 2021-11-16 -> SELL-A 2022-02-14: **-20.92%**
- BUY-A 2022-08-26 -> SELL-C 2022-10-06: **-29.64%**

Therefore AMD exposes two separate concerns:

1. BUY-C is not a stable incremental buy family across symbols.
2. Current SELL-A/B/C are too late in some AMD deterioration paths.

No rule is changed inside this validation.

## 9. Research conclusion

AMD 2020-2023 does **not** validate promotion of BUY-C into a general
three-buy / three-sell rule.

Formal states:

`AMD_2020_2023_V2 = +20.62%`

`AMD_2020_2023_THREE_BUY_THREE_SELL = +19.24%`

`BUY_C_INCREMENTAL_ON_AMD = FAIL`

`THREE_BUY_THREE_SELL_EXTERNAL_VALIDATION = FAIL_INCREMENTAL`

`V2 = PRESERVED`

`V3_CANDIDATE = NOT_ADMITTED`

This is not a claim that BUY-C has no research value.
It means the AMZN-derived incremental benefit did not generalize to AMD
2020-2023.

If AMD results are later used to modify the rules, AMD 2020-2023 must then be
treated as development/diagnostic data rather than untouched validation data.

Closure:

`AMD_2020_2023_THREE_BUY_THREE_SELL_VALIDATION = CLOSED`
