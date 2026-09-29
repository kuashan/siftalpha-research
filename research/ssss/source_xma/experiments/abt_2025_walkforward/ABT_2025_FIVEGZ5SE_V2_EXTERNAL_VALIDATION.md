# ABT 2025 FIVEGZ5SE V2 External Validation

Status: **OOS_FAIL / V2_NOT_ADMITTED**

Date: 2026-09-29

Rule under test:
`FIVEGZ5SE_TRADING_PATH_V2`

Origin of rule:
- developed and pruned on AMZN 2023-2025;
- no ABT-2025 parameter tuning was performed before this run.

## 1. Test scope

- Symbol: ABT
- Period: 2025-01-02 through 2025-12-31
- Sessions: 250
- SCTYPE=1
- next-session-open execution
- 5 bps adverse slippage each side
- long/cash only
- max hold 30 trading sessions
- no original formula action labels used

Frozen path:

### Entry

BUY-A onset OR BUY-B onset.

Same-bar SELL onset vetoes a new entry.

### Exit

First onset of SELL-A / SELL-B / SELL-C exits 100%.

Otherwise time exit at 30 trading sessions.

## 2. Engine parity gate

Before accepting the annual result, the replay was checked against the
previously archived ABT January 2025 five-dimension calibration table.

Calibration dates checked: 14

Five-dimensional state mismatches:
**0**

Therefore:

`ABT_2025_ENGINE_PARITY = PASS`

The annual strategy result is not rejected because of a replay mismatch.

## 3. Signal counts

During ABT 2025:

- BUY-A onsets: 6
- BUY-B onsets: 5
- SELL-A onsets: 6
- SELL-B onsets: 3
- SELL-C onsets: 3
- same-bar buy/sell conflicts: 1

Only five entries were actually taken because signals can occur while already
holding and same-bar SELL has priority.

## 4. V2 annual result

Initial capital:
$10,000.00

Final capital:
**$9,123.84**

Cumulative return:
**-8.76%**

Maximum drawdown:
**-16.20%**

Annualized daily Sharpe:
**-0.47**

Trades:
**5**

Win rate:
**40.0%**

Mean trade:
**-1.77%**

Median trade:
**-2.30%**

Exposure:
**39.6%**

## 5. ABT buy-and-hold benchmark

Same 2025 period and same 5 bps entry/exit slippage:

- return: **+10.09%**
- maximum drawdown: **-14.06%**

Thus V2:
- underperformed buy-and-hold by about **18.85 percentage points**;
- had a worse maximum drawdown;
- had negative Sharpe.

This is a substantive external-validation failure.

## 6. Trade ledger

| Signal | Entry | Exit | Hold | Return | Exit |
|---|---|---|---:|---:|---|
| 2025-01-10 | 2025-01-13 | 2025-01-22 | 6 | +1.26% | SELL-C |
| 2025-03-10 | 2025-03-11 | 2025-04-23 | 30 | -3.64% | TIME |
| 2025-06-09 | 2025-06-10 | 2025-07-24 | 30 | -6.29% | TIME |
| 2025-09-15 | 2025-09-16 | 2025-09-19 | 3 | +2.13% | SELL-C |
| 2025-10-07 | 2025-10-08 | 2025-11-19 | 30 | -2.30% | TIME |

Key diagnostic fact:

All three losing trades ended because of the **30-session time cap**.

SELL-A/B/C did not fire soon enough to protect those losing ABT positions.

The two profitable trades both exited through SELL-C.

This does not justify modifying SELL-A/B/C on ABT; it is diagnostic evidence
only.

## 7. Interpretation

This test directly challenges the strongest concern about the AMZN result:
stock-specific overfitting.

AMZN 2023-2025 development:
- +259.67%
- MDD -13.88%

ABT 2025 external test:
- **-8.76%**
- MDD **-16.20%**

The magnitude and sign reversal are too large to describe as normal
performance variation.

The correct conclusion is:

`FIVEGZ5SE_TRADING_PATH_V2` has **not generalized from AMZN to ABT**.

It must not be promoted to the overall multi-stock validation stage as a
frozen trading rule.

## 8. What is rejected

Rejected:

`FIVEGZ5SE_TRADING_PATH_V2 = REJECTED_NOT_ADMITTED`

for general use.

This rejection applies to the **complete V2 trading path**, not to the entire
FIVEGZ5SE indicator research.

BUY-A, BUY-B and SELL-A/B/C remain research hypotheses whose portability must
be re-examined.

## 9. OOS contamination rule

ABT 2025 has now been opened as an external validation set.

If the research uses these ABT results to change:
- BUY-A/B definitions;
- SELL-A/B/C definitions;
- max holding period;
- conflict logic;
- any threshold;

then ABT 2025 becomes development/diagnostic data and must **not** later be
presented as untouched OOS evidence.

Any revised version will require a different untouched symbol/period for final
validation.

## 10. Research state

`ABT_2025_FIVEGZ5SE_V2_ENGINE_PARITY = PASS`

`ABT_2025_FIVEGZ5SE_V2_EXTERNAL_VALIDATION = FAIL`

`FIVEGZ5SE_TRADING_PATH_V2 = REJECTED_NOT_ADMITTED`

Closure:
`ABT_2025_V2_TEST = CLOSED`
