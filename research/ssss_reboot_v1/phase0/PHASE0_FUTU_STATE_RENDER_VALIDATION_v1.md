# SSSS Reboot v1 — Phase 0 Futu State Render Validation v1

Status: **STATE-RENDER GATE PASS / EVENT-DATE GATE PARTIAL**
Date: 2026-10-02

## Purpose

Validate the corrected SSSS reconstruction against five real Futu screenshots
supplied by the user.

Important:
The screenshots show historical formula output rendered as of the screenshot's
latest bar. Therefore this validation uses `RENDER_ASOF`, not the causal
`FIRST_OBSERVED` ledger.

Independent OHLCV source:
Twelve Data, U.S. daily regular-session bars, through 2026-10-01.

## Corrected state model used

Fast:
- point-in-time/chart-as-of double-XMA25;
- ZD1 / MID / ZK1.

Slow:
- author-corrected 20..1 weighted H/L, total weight 210;
- EMA90;
- slow lower/upper expansion exactly as in SSSS.

Color mapping:
- BLUE = UP
- GREEN = DOWN
- GRAY = RANGE
- EXPANSION = fourth topology

## CRSP

Reconstructed 2026 state runs:

- 2026-01-02 .. 2026-01-28: GRAY
- 2026-01-29 .. 2026-02-06: GREEN
- 2026-02-09 .. 2026-08-24: GRAY
- 2026-08-25 .. 2026-09-03: BLUE
- 2026-09-04 .. 2026-10-01: GRAY

Screenshot comparison:
- long gray middle section reproduced;
- brief late-August / early-September blue section reproduced;
- return to gray into the latest bars reproduced.

Decision: `CRSP_STATE_RENDER = PASS`

## PG

Reconstructed 2026 state runs:

- 2026-01-02 .. 2026-01-14: GREEN
- 2026-01-15 .. 2026-01-23: GRAY
- 2026-01-26 .. 2026-03-09: BLUE
- 2026-03-10 .. 2026-03-18: GRAY
- 2026-03-19 .. 2026-05-29: GREEN
- 2026-06-01 .. 2026-10-01: GRAY

Screenshot comparison:
- blue rally regime reproduced;
- following green decline regime reproduced;
- broad gray regime from June onward reproduced.

Decision: `PG_STATE_RENDER = PASS`

## WMT

Reconstructed 2026 state runs:

- 2026-01-02 .. 2026-05-18: BLUE
- 2026-05-19 .. 2026-06-01: GRAY
- 2026-06-02 .. 2026-10-01: GREEN

This is especially clean against the supplied screenshot:
- long blue first phase;
- short gray transition;
- long green declining phase.

Decision: `WMT_STATE_RENDER = PASS`

## AAPL

Reconstructed 2026 state runs:

- 2026-01-02 .. 2026-01-08: BLUE
- 2026-01-09 .. 2026-01-28: GRAY
- 2026-01-29 .. 2026-02-18: BLUE
- 2026-02-19 .. 2026-04-14: GRAY
- 2026-04-15 .. 2026-10-01: BLUE

Screenshot comparison:
- spring gray structure reproduced;
- sustained blue up-state beginning in April/May and continuing into the latest
  bars reproduced.

Decision: `AAPL_STATE_RENDER = PASS`

## ARM

Reconstructed 2026 state runs:

- 2026-01-02 .. 2026-02-23: GREEN
- 2026-02-24 .. 2026-03-12: GRAY
- 2026-03-13 .. 2026-07-22: BLUE
- 2026-07-23 .. 2026-10-01: GRAY

Screenshot comparison:
- large blue rising phase reproduced;
- later gray range regime reproduced.

Decision: `ARM_STATE_RENDER = PASS`

## Aggregate state-render decision

All five independent screenshot cases reproduce the visible large-scale regime
blocks under the corrected canonical formula.

`PHASE0_FUTU_5_SYMBOL_STATE_RENDER = PASS`

This materially supports all of the following together:

1. corrected 20..1 / 210 weighted channel;
2. corrected L use in the low weighted series;
3. double-XMA25 geometry;
4. slow-boundary expansion;
5. BLUE / GREEN / GRAY semantic mapping;
6. SSSS and ADKBY-E sharing the intended regime family.

## Event/icon validation

The reconstruction also generates lower-cross / upper-cross events and the
corresponding ADKBY 多 / 空 / 平 labels.

Examples from the independent reconstruction include:

WMT:
- 2026-01-06 BLUE lower -> 多
- 2026-02-03 BLUE upper -> 平
- 2026-05-22 GRAY lower -> 多
- 2026-06-16 GREEN upper -> 空
- 2026-07-01 GREEN lower -> 平

PG:
- 2026-01-28 BLUE lower -> 多
- 2026-02-04 BLUE upper -> 平
- 2026-04-24 GREEN upper -> 空
- 2026-06-01 GRAY lower -> 多

AAPL:
- 2026-03-13 GRAY lower -> 多
- 2026-05-13 BLUE upper -> 平
- 2026-09-22 BLUE upper -> 平

ARM:
- 2026-03-19 BLUE lower -> 多
- 2026-06-01 BLUE upper -> 平
- 2026-08-06 GRAY upper -> 空

CRSP:
- 2026-02-11 GRAY lower -> 多
- 2026-04-14 GRAY upper -> 空
- 2026-09-10 GRAY lower -> 多

The screenshots visibly contain icon/text events in the corresponding regions,
but the static images do not expose an exact date cursor for every icon.

Therefore:

`PHASE0_EVENT_VISUAL_TOPOLOGY = PASS`

`PHASE0_EVENT_EXACT_BAR_DATE_MATCH = PARTIAL / NEEDS DATE-LEVEL FUTU CHECK`

We do not claim exact icon-date equality from image position alone.

## Remaining Phase 0 gate

The largest unresolved formula item is:

`XMA(XMA(H/L,60),60)`

The source uses an even period (60), while public centered-XMA implementations
may normalize even periods differently.

Until direct Futu numerical calibration is obtained:

- BS remains uncalibrated;
- BD remains uncalibrated;
- no period-59 or period-61 substitution is allowed;
- the Phase-0 engine returns BS/BD as None.

Current overall status:

`PHASE0_SOURCE_RECONSTRUCTION = IN_PROGRESS`

Passed:
- source extraction;
- author corrections;
- double-XMA25 numeric calibration;
- canonical slow-channel numeric calibration;
- 5-symbol Futu state-render validation;
- event topology validation.

Open:
- exact XMA60 / BS / BD calibration;
- exact per-bar icon date spot checks.
