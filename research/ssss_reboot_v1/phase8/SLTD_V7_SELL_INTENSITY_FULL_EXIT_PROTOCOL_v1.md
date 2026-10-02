# SLTD V7 Sell Intensity & Full Exit Study v1 — Protocol

状态：RESEARCH_PROTOCOL_FROZEN_BEFORE_RUN

## Source boundary

- V6 rollback baseline remains immutable:
  - branch: `baseline/sltd-v6-15rules-position-v1`
  - commit: `05be43e350d9193ba01a2748ef4c0267438a84b1`
- V7 candidate baseline remains immutable:
  - branch: `candidate/sltd-v7-12rules-position-v1`
  - commit: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`
- This study branches from the exact V7 candidate commit and may not rewrite V6 or V7.

## Evidence entering this study

Daily-79 Universal Sell validation completed successfully. S1, S2 and S3 advanced; S4 remained WATCH; S5 and C3 remained rejected.

This study does not assume that a valid SELL trigger should always use the same size.

## Round 1 scope

Frozen 79-stock daily snapshot only.

- timeframe: 1d
- formal window: 2020-01-02 through 2026-09-30
- representation: FIRST_OBSERVED
- execution: signal close -> next available open
- friction: 5 bps baseline, 10 bps stress
- long only, no leverage

## Sell trigger sources

- S1: mature BLUE age >= 21 + upper + WICK_ONLY
- S2: mature BLUE age >= 21 + any upper
- S3: S1 on previous bar + current close below previous close

The V7 native GREEN SELL rules remain unchanged and still use the frozen ordinary 25%-of-current reduction.

## Intensity screen

Each of S1/S2/S3 is tested independently with:

- CUR25: reduce current position by 25%
- CUR50: reduce current position by 50%
- TARGET50: reduce to no more than 50% position
- TARGET25: reduce to no more than 25% position
- FULL: liquidate to 0%

Layered candidates also test:

- S1 CUR25 -> S3 CUR50
- S1 CUR25 -> S3 TARGET25
- S1 CUR25 -> S3 FULL

## Full-exit escalation candidates

1. Frozen C2 remains available: after an actually executed SELL, GREEN + High < GZB4 -> next open full exit.
2. DIRECT_C2_FULL: test the same strong condition without requiring a prior SELL.
3. Candidate-armed ZD1 break: after an added candidate SELL actually executes, later close < ZD1 -> next open full exit.

No middle-line break is tested in Round 1 because the exact frozen middle-line formula has not been confirmed in this branch. No midpoint proxy may be invented.

## Required metrics

For every variant:

- Total Return
- CAGR
- Max Drawdown
- Calmar
- per-symbol breadth
- p10 symbol return delta
- p5/CVaR5 trade-tail information
- candidate SELL executions
- strong SELL executions
- full-exit count
- re-entry count
- 5-bar quick re-buy
- post-full-exit 1/3/5/10-bar returns
- wrong full-exit rate
- avoided 10-bar downside
- lost 10-bar upside

Wrong full exit is frozen before the run as: 10-bar close return from the exit open > 0.

## Round 1 decision gate

ADVANCE_TO_ROUND2 only if all hold at 5 bps:

- Better Calmar on at least 44/79 stocks
- portfolio Delta Calmar > 0
- portfolio Delta MaxDD >= 0
- portfolio Delta CAGR >= -0.5 percentage points

REJECTED_NOT_ADMITTED if:

- Better Calmar on at most 31/79 stocks
- Delta Calmar < 0
- Delta CAGR < 0

Otherwise WATCH.

Round 1 cannot change formal V7. Only ADVANCE_TO_ROUND2 candidates may enter 1h/4h cross-timeframe validation.

`SLTD_V7_SELL_INTENSITY_FULL_EXIT_PROTOCOL_V1 = FROZEN_BEFORE_RUN`
