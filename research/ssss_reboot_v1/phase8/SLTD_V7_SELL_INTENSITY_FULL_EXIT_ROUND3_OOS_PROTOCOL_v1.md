# SLTD V7 Sell Intensity & Full Exit Study v1 — Round 3 Fresh-Stock OOS Protocol

状态：ROUND3_PROTOCOL_FROZEN_BEFORE_RUN

## Provenance（来源）

- V6 immutable rollback commit:
  `05be43e350d9193ba01a2748ef4c0267438a84b1`
- V7 frozen candidate commit:
  `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`
- Round 1 verified commit:
  `39888969074101e3e6034bdcb4550ea4e30e70fe`
- Round 2 verified commit:
  `bf5f38158520a12ea96c3e19a159836380598f8d`

This branch is research-only and does not modify the frozen V7 candidate.

## OOS universe

These 20 stocks were not used in the Round 1 frozen-79 design universe, the Round 2 20-stock cross-timeframe universe, or the previous V7 fresh OOS10:

AXP, PNC, USB, COF, ICE,
CME, PGR, CB, VRTX, REGN,
BSX, HCA, MDLZ, CL, YUM,
GM, F, UBER, ETN, SLB

The runner contains an explicit overlap assertion against the known prior universes.

## Candidates admitted from Round 2

- S3_CUR25
- S3_CUR50
- S3_TARGET50
- S3_TARGET25

No rejected/WATCH Round 1 full-exit rule is reintroduced.

## Timeframes

- 1h
- 4h
- 1d

Total: 60 OOS series.

Execution remains universal:

selected bar close confirms signal
-> next selected bar open executes.

## Evaluation windows

Intraday:
- context approximately 365 days
- formal comparison approximately most recent 180 days

Daily:
- long-history formal window: 2020-01-02 through 2026-09-30
- earlier bars are retained only for indicator warmup

Only completed bars enter signal computation.

## Friction

- 5 bps primary
- 10 bps stress

## Baseline parity

For every OOS symbol/timeframe series, the custom simulator with no S3 overlay must reproduce frozen V7 `strategy.simulate_policy` to max absolute equity-curve difference <= 1e-10.

Any mismatch aborts the run.

## Frozen OOS decision gate

`ADVANCE_TO_CRYPTO` only if all hold at 5 bps:

- Better Calmar >= 33/60 series
- Median delta Calmar > 0
- Median delta MaxDD >= 0
- Median delta Return >= -1.0%
- 1h Better Calmar >= 8/20
- 4h Better Calmar >= 8/20
- 1d Better Calmar >= 8/20

`REJECTED_NOT_ADMITTED` if:

- Better Calmar <= 23/60
- Median delta Calmar < 0
- Median delta Return < 0

Otherwise: `WATCH`.

`ADVANCE_TO_CRYPTO` means the candidate has passed the stock OOS gate. Crypto cannot reverse or rewrite the stock conclusion; Round 4 only tests cross-asset portability.

If multiple variants pass, Round 3 does not post-hoc invent a composite score or force a winner. Pairwise and Pareto evidence from Rounds 1-3 will be preserved for the stock-selection decision.

`SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND3_OOS_PROTOCOL = FROZEN_BEFORE_RUN`
