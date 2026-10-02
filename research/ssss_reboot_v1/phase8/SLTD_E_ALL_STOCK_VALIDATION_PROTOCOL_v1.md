# SLTD E All-Stock Validation v1

Status: **FROZEN BEFORE RUN**

Date: 2026-10-02

## Purpose

Evaluate the user-confirmed SLTD E v1 strategy on every archived mainstream U.S. stock daily dataset currently available in the SiftAlpha research repository.

This run is an evaluation only. It must not retune E, relax any rule, or modify the frozen V7 candidate.

## Source strategy

E implementation source:
- branch: `feature/sltd-v7-e-strategy-v1`
- commit: `f990eb9d2d4567d8acdc617fb1b4b9dd01b45f1c`
- specification: `integrations/sltd_v7_siftalpha_v1/E_STRATEGY_SPEC_v1.md`

Frozen V7 comparison source:
- branch: `candidate/sltd-v7-12rules-position-v1`
- commit: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`

## Universe

Use every archived daily stock snapshot currently available from the long-window SLTD studies:

1. Prior frozen 79-stock universe in Phase 7, Batches 1-8.
2. Fresh OOS10 universe in Phase 8:
   WFC, LMT, PM, ADP, WM, UNP, SO, VZ, PANW, CVS.

Required combined count: **89 unique stocks**.
Any duplicate symbol or missing file is a hard failure.

The OOS10 subset remains separately reported so it is not hidden inside the reused 79-stock sample.

## Timeframe and higher timeframe

- selected timeframe: **1d**
- E higher timeframe: **5d**
- 5d is aggregated causally from non-overlapping completed daily bars.
- no future bar or still-forming higher-timeframe bar may be used.

## Historical window

- warm-up data: use all archived history before the formal window.
- formal evaluation: **2020-01-02 through 2026-09-30**.
- strategy starts flat at the first formal bar.
- signals are confirmed at selected-bar close.
- actions execute at the next available selected-bar open.

## E rules

Use the exact user-confirmed E v1 state machine without retuning:
- C1 +25pp;
- C2 higher-timeframe confirmation +25pp;
- C3 GZB3-GZB4 touch +25pp;
- cap 75%;
- each buy condition once per holding cycle;
- ZK1 close cross up: -50pp;
- BS touch in exit sequence: -25pp;
- GZB3-GZB4 touch in exit sequence: full exit;
- after exit sequence starts, close back below ZK1: full exit;
- same-bar sell priority: full exit > BS -25pp > ZK1 -50pp;
- no short, no leverage.

## Execution accounting

Percentage-point actions are target-exposure actions:
- 75% -> -50pp -> target 25%;
- target 25% -> -25pp -> target 0%.

At each execution open, rebalance the symbol account to the target exposure as a fraction of pre-trade equity.
Trading friction is charged on absolute traded notional.

Primary friction: **5 bps**.
Stress friction: **10 bps**.

## Comparators

Run the same 89 stocks and formal window for:
1. SLTD E v1.
2. frozen SLTD V7 12-rule candidate.
3. Buy & Hold: invest 100% at first formal open and hold to formal end.

No comparator may change the E rules.

## Required outputs

For 5bps and 10bps where applicable:
- equal-weight 89-stock portfolio Return, CAGR, MaxDD, Calmar;
- equal-weight prior-79 metrics;
- equal-weight fresh-OOS10 metrics;
- per-symbol Return, CAGR, MaxDD, Calmar;
- E versus V7 breadth counts;
- E versus Buy & Hold breadth counts;
- median per-symbol deltas;
- number of profitable symbols;
- number of positive-Calmar symbols;
- mean time in market;
- turnover;
- execution count;
- E rule execution counts;
- yearly portfolio returns for 2020 through 2026;
- era metrics:
  - 2020-2021
  - 2022-2023
  - 2024-2026Q3.

## Interpretation boundary

The prior 79 stocks are reused research data and are not independent OOS.
The separate 10-stock subset is independent of the prior 79 and must remain separately visible.
No E rule is promoted, deleted, or changed by this run alone.

`SLTD_E_ALL_STOCK_VALIDATION_V1_PROTOCOL = FROZEN`
