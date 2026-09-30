# ABT 2025 FIVEGZ5SE V2 External Validation — Corrected No-Time-Cap Run

Status: **OOS_FAIL / V2_NOT_ADMITTED**

Date: 2026-09-29

This report supersedes the earlier ABT run that imposed a 30-session forced
exit.

## 1. Corrected rule under test

Entry:

```
onset(BUY-A) OR onset(BUY-B)
```

Same-bar SELL onset vetoes a new entry.

Exit:

```
onset(SELL-A)
OR onset(SELL-B)
OR onset(SELL-C)
```

Execution:
- signal at close t;
- trade at next-session open;
- 5 bps adverse slippage each side.

**There is no maximum holding period.**

A position remains open until a SELL signal actually occurs.

If the sample ends while still holding:
- the portfolio is marked to the final close;
- that is not treated as an active strategy exit.

No original formula action labels are used.

## 2. Engine parity

Before accepting the annual result, the replay was checked against the archived
ABT January 2025 five-dimension calibration table.

Calibration rows checked: 14

State mismatches:
**0**

Therefore:

`ABT_2025_ENGINE_PARITY = PASS`

## 3. Signal counts

ABT 2025:

- BUY-A onsets: 6
- BUY-B onsets: 5
- SELL-A onsets: 6
- SELL-B onsets: 3
- SELL-C onsets: 3
- same-bar BUY/SELL conflicts: 1

## 4. Corrected annual result

Initial capital:
$10,000.00

Final marked portfolio value:
**$8,587.82**

Cumulative return:
**-14.12%**

Maximum drawdown:
**-17.16%**

Annualized daily Sharpe:
**-0.79**

Closed trades:
**5**

Closed-trade win rate:
**40.0%**

Average closed trade:
**-2.92%**

Exposure:
**48.0%**

Open position at year end:
**none**

## 5. Buy-and-hold benchmark

ABT 2025 buy-and-hold, with the same 5 bps entry/exit slippage:

- return: **+10.09%**

Thus the corrected V2 underperformed buy-and-hold by about:

**24.21 percentage points**

## 6. Trade ledger

| Signal | Entry | Exit | Hold | Return | Exit |
|---|---|---|---:|---:|---|
| 2025-01-10 | 2025-01-13 | 2025-01-22 | 6 | +1.26% | SELL-C |
| 2025-03-10 | 2025-03-11 | 2025-05-13 | 44 | -3.97% | SELL-A |
| 2025-06-09 | 2025-06-10 | 2025-08-01 | 36 | -6.15% | SELL-A |
| 2025-09-15 | 2025-09-16 | 2025-09-19 | 3 | +2.13% | SELL-C |
| 2025-10-07 | 2025-10-08 | 2025-11-20 | 31 | -7.86% | SELL-A |

## 7. Key correction and interpretation

The earlier 30-session rule was not part of the five-dimension signal logic and
could force an exit without a SELL signal.

Removing it was the correct research correction.

However the corrected ABT result is **worse**, not better:

- old 30-day-cap run: -8.76%
- corrected signal-only exit run: **-14.12%**

Therefore the ABT failure was **not caused by the artificial time cap**.

The real problem is that SELL-A/B/C did not identify deterioration early
enough in the three losing ABT positions.

Those losing positions eventually did receive SELL-A, but only after:

- 44 sessions: -3.97%
- 36 sessions: -6.15%
- 31 sessions: -7.86%

This is direct evidence that the current exit families are not sufficiently
portable from AMZN to ABT.

## 8. AMZN comparison under the same corrected holding rule

For reference, the same no-time-cap rule on AMZN 2023-2025 produced:

- marked cumulative return: **+280.26%**
- MDD: **-13.88%**
- 18 closed trades
- closed-trade win rate: **94.44%**
- one open position at 2025-12-31, unrealized +2.69%

The gap between AMZN and ABT therefore becomes even clearer after removing the
time cap.

## 9. Research conclusion

The correct conclusion is:

`FIVEGZ5SE_TRADING_PATH_V2` does not generalize from AMZN to ABT 2025.

The complete path remains:

`REJECTED_NOT_ADMITTED`

This rejection is about the current combined BUY/SELL path.

It does **not** reject the entire FIVEGZ5SE research program.

## 10. OOS contamination rule

ABT 2025 has now been opened and analyzed.

Any future rule change based on these ABT failures makes ABT 2025 part of
development/diagnostic data.

A later revised V3 must be validated on a different untouched symbol/period.

Closure:

`ABT_2025_FIVEGZ5SE_V2_NO_TIME_CAP = FAIL`

`FIVEGZ5SE_TRADING_PATH_V2 = REJECTED_NOT_ADMITTED`
