# SLTD V7 Sell Intensity & Full Exit Study v1 — Round 2 Protocol

状态：ROUND2_PROTOCOL_FROZEN_BEFORE_RUN

## Provenance（来源）

- V6 immutable rollback:
  - branch: `baseline/sltd-v6-15rules-position-v1`
  - commit: `05be43e350d9193ba01a2748ef4c0267438a84b1`
- V7 frozen candidate:
  - branch: `candidate/sltd-v7-12rules-position-v1`
  - commit: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`
- Round 1 verified result:
  - branch: `research/sltd-v7-sell-intensity-full-exit-v1`
  - commit: `39888969074101e3e6034bdcb4550ea4e30e70fe`
- Intraday data/strategy support is copied unchanged from verified Universal Sell research:
  - source commit: `ea0d2ec5f484bdc35b1f134f236bbd933c9caf15`
  - files: `integrations/sltd_v7_siftalpha_v1/data_provider.py`, `strategy.py`

This branch is research-only and does not modify the frozen V7 candidate.

## Round 1 admission result

Only these variants are admitted to Round 2:

1. `S3_CUR25`
2. `S3_CUR50`
3. `S3_TARGET50`
4. `S3_TARGET25`

Not admitted to Round 2:

- all S1 intensity variants
- all S2 intensity variants
- S3 FULL
- S1+S3 layered variants
- DIRECT_C2_FULL
- ZD1 full-exit escalations

## S3 definition

`S3_MATURE_BLUE_WICK_CONFIRM_DOWN`:

- previous bar: BLUE
- previous BLUE run age >= 21
- previous bar has upper event
- previous upper subtype = WICK_ONLY
- current bar close < previous bar close

Signal is confirmed only after the current selected-timeframe bar closes and executes at the next selected-timeframe bar open.

## Universe and timeframes

Stocks (same cross-timeframe discovery universe used by the verified Universal Sell Study):

ABT, AAPL, MSFT, NVDA, AMD,
AMZN, META, GOOGL, JPM, BAC,
XOM, CVX, LLY, UNH, WMT,
COST, CAT, BA, MA, V

Timeframes:
- 1h
- 4h

Total: 40 series.

History:
- fetch/simulation context: approximately 365 days
- formal comparison: most recent approximately 180 days
- minimum warmup: frozen strategy minimum
- only completed bars are eligible
- 4h is session-anchored aggregation of completed 1h source bars, using the verified data provider

Friction:
- 5 bps primary
- 10 bps stress

## Sell intensity semantics

Native V7 SELL remains unchanged: sell 25% of current remaining position.

For an actually resolved S3 SELL:

- CUR25: sell 25% of current position
- CUR50: sell 50% of current position
- TARGET50: reduce position to no more than 50%
- TARGET25: reduce position to no more than 25%

An S3 SELL that conflicts on the same bar with another action class follows frozen V7 conflict semantics: NO_CHANGE_MIXED.

An actually executed S3 SELL arms frozen C2 exactly like an actually executed native SELL. A later actually executed BUY resets C2.

No direct C2 and no new full-exit rule are added in Round 2.

## Baseline parity requirement

For every symbol/timeframe series, a custom no-extra-sell simulation must reproduce frozen `strategy.simulate_policy` equity to numerical tolerance before candidate results are accepted.

Any parity failure aborts the run.

## Required metrics

Per variant overall and by timeframe:

- Total Return
- CAGR
- Max Drawdown
- Calmar
- Better Return series count
- Better MaxDD series count
- Better Calmar series count
- Median delta Return
- Median delta MaxDD
- Median delta Calmar
- S3 signal count
- actually executed S3 sell count
- C2 full-exit count
- 5-bar re-buy after C2 full exit
- 10 bps stress metrics

## Frozen Round 2 decision gate

`ADVANCE_TO_OOS` only if all are true at 5 bps:

- Better Calmar >= 22/40 series
- Median delta Calmar > 0
- Median delta MaxDD >= 0
- Median delta Return >= -1.0%
- 1h Better Calmar >= 8/20
- 4h Better Calmar >= 8/20

`REJECTED_NOT_ADMITTED` if:

- Better Calmar <= 15/40
- Median delta Calmar < 0
- Median delta Return < 0

Otherwise: `WATCH`.

Round 2 cannot change formal V7. Only `ADVANCE_TO_OOS` variants may enter Round 3 fresh-stock OOS.

`SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND2_PROTOCOL = FROZEN_BEFORE_RUN`
