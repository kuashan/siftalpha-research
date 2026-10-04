# SLTD A-share 50 Integrated Risk v1 — Amendment B

Status: **FROZEN BEFORE ANY STRATEGY RESULT**

## 1. Reason

The initial Yahoo/yfinance integrity-only audit did not complete in a reasonable deterministic
runtime across the frozen 50-symbol A-share universe.

No strategy return, state utility, Severe Risk result, or Fresh OOS performance was produced.

Therefore this is a data-source engineering amendment, not a result-driven research change.

## 2. Source override

Primary A-share historical source is changed to:

- AkShare
- Eastmoney A-share daily history endpoint exposed by
  `akshare.stock_zh_a_hist`

Request:
- `period="daily"`
- `adjust="qfq"` (前复权)
- start: 2016-01-01
- end: 2026-09-30

Normalized columns archived:
- Date
- Open
- High
- Low
- Close
- Volume

The new immutable snapshot directory is:

`ashare50_data_snapshot_v2`

The older Yahoo attempt is not an admissible research snapshot for Phase18 and must not trigger
strategy research.

## 3. Why qfq is used

The study requires continuous technical geometry across historical dividend / ex-right events.
All systems in Phase18 use the identical qfq series.

The study remains comparative strategy research rather than literal brokerage cash accounting.

## 4. Everything else unchanged

Unchanged:
- frozen 50 symbols
- 35 DEVELOPMENT / 15 FRESH_OOS split
- 2018-2026Q3 formal window
- causal close -> next fillable open semantics
- T+1 handling
- locked limit handling
- friction schedule
- 12 frozen rules
- C2
- A-share-only learning of the new risk layer
- Fresh OOS prohibition before admission

## 5. Freeze

`SLTD_ASHARE50_INTEGRATED_RISK_V1_AMENDMENT_B = FROZEN`
