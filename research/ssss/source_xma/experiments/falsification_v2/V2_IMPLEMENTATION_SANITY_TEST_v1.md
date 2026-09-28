# XMA Falsification v2 — Implementation Sanity Test v1

Status: **IMPLEMENTED_AND_VERIFIED FOR PROTOCOL DRAFT**

Date: 2026-09-28

This is a development implementation test, not a v2 hypothesis test.

No return-performance comparison, hypothesis p-value, FDR decision, or trading-rule promotion is made here.

## 1. Governance

Authorized by:
- `V2_BOUNDED_DEVELOPMENT_TESTING_AMENDMENT_v1.md`

Definitions:
- `V2_VARIABLE_DEFINITION_RESOLUTION_v1.md`

Implementation:
- `v2_feature_definitions.py`
- implementation correction commit: `7fcce28ad3d307116171a09929d7deaeb66fbf32`

All dates/data accessed in this development test are development-contaminated and can never be relabeled as the future sealed window.

The future sealed window must start only after Protocol/Data/Code freeze.

## 2. Data sources used for sanity testing

### Equity / ETF daily OHLCV

Provider used for development test:
- Twelve Data

Purpose:
- implementation and coverage validation only.

Observed provider constraint:
- current connection limit: 8 API credits per minute.

This constraint does not change any feature definition.

It creates a production/data-pipeline requirement:
- cache historical data;
- rate-limit requests;
- batch work across cached symbol snapshots rather than refetching every feature computation.

### VIX

Development source:
- public GitHub dataset `datasets/finance-vix`
- file: `data/vix-daily.csv`
- blob SHA observed during test: `c05e0d9c28ddf3b98d0531017ef5b5180df05ae1`
- dataset declares Cboe VIX historical CSV as its upstream source.

Final Data Freeze must use and hash the authoritative frozen VIX source/snapshot; this development mirror is not itself the final data freeze.

## 3. Volatility z-score and Volume z-score

Real daily OHLCV test symbols:
- AAPL
- MSFT
- JPM

Each returned 5,000 daily rows in the development query.

Observed implementation coverage per symbol:
- VOL_Z valid observations: 4,920
- first computable VOL_Z in returned history: 2007-03-08
- VOLUME_Z valid observations: 4,940
- first computable VOLUME_Z in returned history: 2007-02-07

Result:

**PASS — formulas are computable with the frozen 20/60 and 60-observation warm-up rules.**

No lookback was shortened to accommodate data availability.

## 4. H4 FAST_MID_ANALYTIC quantile implementation

Point-in-time double-XMA endpoint logic was applied to real daily OHLCV.

Reference window:
- 2020-01-02 through 2025-12-31 only.

Valid reference observations:
- AAPL: 1,508
- MSFT: 1,508
- JPM: 1,508

All exceed the frozen H4 minimum of 252.

Development-calculated example thresholds:

| Symbol | P10 | P40 | P60 | P90 |
| --- | ---: | ---: | ---: | ---: |
| AAPL | -1.7284 | 0.0007 | 1.0344 | 2.7149 |
| MSFT | -1.6848 | 0.0236 | 0.8925 | 2.5975 |
| JPM | -1.7358 | -0.0197 | 0.8358 | 2.6351 |

These numbers demonstrate computability.

They are not the final all-symbol H4 Data-Freeze manifest.

Result:

**PASS — H4 reference-population and quantile implementation are operational.**

## 5. Sector RS

Frozen 11 ETFs tested:
- XLK
- XLC
- XLY
- XLP
- XLV
- XLF
- XLI
- XLE
- XLB
- XLU
- XLRE

Benchmark:
- SPY

All 11 ETF series were available with sufficient history for the 20-bar calculation on the sampled development date 2025-06-27.

Example RS20 ordering on that date, weakest to strongest:

1. XLP
2. XLRE
3. XLU
4. XLV
5. XLY
6. XLB
7. XLF
8. XLI
9. XLE
10. XLC
11. XLK

The deterministic percentile ranks therefore span exactly 0.0 to 1.0.

Result:

**PASS — the frozen Sector RS formula and 11-sector ranking can be computed from real data.**

## 6. VIX 5-day Risk-Off feature

Development window checked:
- 2025-01-02 through 2025-06-30

Valid VIX 5-day change observations:
- 127

Dates satisfying the already frozen:
`VIX_CHG5 > +20%`

Development count:
- 22 dates

This count is not interpreted as predictive evidence.

Result:

**PASS — VIX 5-day change and fixed +20% Risk-Off condition are computable.**

## 7. Market Breadth implementation

Frozen universe size:
- 39 equities

Frozen valid-date threshold:
- at least 80% available
- ceiling(0.80 * 39) = 32 symbols

Because the development Twelve Data connection is limited to 8 requests/minute, the 39 symbols were retrieved in fixed batches.

The implementation test reached:
- 32 distinct real breadth-universe members with valid daily history
- exactly the frozen minimum valid membership threshold.

Test dates:
- 2025-05-20 through 2025-06-27 trading sessions.

For every sampled date the 32 retrieved members had enough history for their own SMA20.

Example combined development breadth:
- 2025-06-20: 46.875%
- prior-valid-observation rolling Q10 at that date: 56.25%
- frozen comparison therefore labels that development date Risk-Off.

This is an implementation example only; it is not evidence for H11/H12.

Result:

**PASS — the 80%-availability Breadth path and prior-20-valid-observation Q10 rule are operational on real data.**

The remaining seven members were not declared unavailable. They were simply unnecessary for exercising the frozen 80% path in this sanity test.

## 8. Implementation discrepancy found and fixed

During the test, the first Python implementation used:

`shift(1).rolling(20)`

directly on the calendar-indexed Breadth series.

That uses the prior 20 rows, not necessarily the prior 20 valid Breadth observations if missing dates exist.

The frozen text requires the prior 20 **valid** Breadth observations.

The implementation was corrected before Protocol drafting:

1. drop missing Breadth values;
2. calculate the prior-20 rolling Q10 on the valid series;
3. reindex the threshold to the original date index.

Correction commit:
`7fcce28ad3d307116171a09929d7deaeb66fbf32`

No outcome data were used to make this correction.

## 9. Data-infrastructure consequence for future trading

This test exposed a real operational requirement:

A breadth/ranking trading system cannot depend on live sequential refetching of dozens of symbols under a low per-minute API allowance.

Product/data infrastructure must therefore maintain a cached market-data panel containing at least:

- 39 breadth symbols;
- 11 sector ETFs;
- SPY;
- VIX;
- OHLCV history sufficient for all warm-ups.

Feature computation should consume the cached panel, not issue one remote request per feature evaluation.

This is an infrastructure requirement, not a strategy rule.

## 10. Stage decision

Variable Definition Resolution:
**IMPLEMENTED_AND_VERIFIED**

Protocol Input Gap stage:
**CLOSED**

No further parameter refinement is authorized for:
- VOL_Z;
- VOLUME_Z;
- Sector RS20;
- BREADTH20;
- F3 ATR14/close volatility control;
- H4 reference period/quantile method;
- VIX_CHG5.

Any later change requires Amendment.

## 11. Next step

Begin `XMA_FALSIFICATION_V2_PROTOCOL.md`.

The Protocol must incorporate these definitions unchanged and add:
- exact Episode construction;
- matching/control construction;
- Statistical Analysis Plan;
- cluster/ESS method;
- FDR plan;
- Guard gate;
- Data/Code Freeze manifests;
- separate Freeze Procedure;
- separate Amendment Procedure;
- sealed-window rule;
- decision/failure modes.

Scientific v2 hypothesis testing remains **NOT AUTHORIZED** until Protocol/Data/Code freeze is complete.
