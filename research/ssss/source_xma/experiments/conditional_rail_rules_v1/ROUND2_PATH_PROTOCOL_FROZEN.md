# SSSS Conditional Rail Rules v1 — Round 2 Path Protocol

Status: FROZEN_BEFORE_ROUND2_RUN
Date: 2026-10-01

## Purpose

Round 1 showed that isolated rail touches are insufficient for final rules.
Round 2 tests conditional paths and confirmations without changing the frozen
Source-XMA chronology.

No production trade action is assumed.

## XMA chronology

Unchanged:
for each t use only data <= t, recompute first-observed right-edge XMA25/XMA60,
freeze t, then advance. No later repaint may overwrite t.

## Event anchors

Reuse Round 1 episode onsets:
- LOWER_FAST: first low < moving ZD1 after a non-excursion bar
- UPPER_FAST: first high > moving ZK1 after a non-excursion bar

Primary states:
UP / DOWN / RANGE.
EXPANSION is recorded but not promoted due low sample count.

## A. Lower-origin paths

For every LOWER_FAST event at t0:

### A1 MID_TOUCH
First j in (t0, t0+20] with:
high_j >= MID_j.

### A2 MID_CLOSE_RECLAIM
First j in (t0, t0+20] with:
close_j >= MID_j.

This is a close-known confirmation candidate, not an entry rule.

### A3 UPPER_TOUCH
First j in (t0, t0+20] with:
high_j >= ZK1_j.

### A4 LOWER_OUTER_TOUCH
First j in [t0, t0+20] with:
low_j <= BD_j.

### A5 NEW_LOW_BEFORE_RECLAIM
Before A2 occurs, any bar with:
low_j < low_t0.

### A6 STATE_IMPROVEMENT
For DOWN-origin events, first transition after t0 within 20 bars to:
RANGE or UP.

For UP-origin events, separately record UP->RANGE/DOWN deterioration.

### Lower sequence buckets
Using first occurrence order:
- MID_RECLAIM_THEN_UPPER
- OUTER_THEN_MID_RECLAIM
- MID_RECLAIM_NO_UPPER
- NEW_LOW_BEFORE_MID
- NO_MID_RECLAIM_20

For each bucket measure:
- count
- event-close forward returns
- returns from confirmation close A2 at +5/+10/+20
- MFE/MAE from event and from A2
- time to A2 / A3
- state at A2
- whether A6 occurred before A2

No bucket is pre-labelled buy/add/failure.

## B. Upper-origin paths

For every UPPER_FAST event at t0:

### B1 MID_TOUCH
First j in (t0, t0+20] with:
low_j <= MID_j.

### B2 MID_CLOSE_LOSS
First j in (t0, t0+20] with:
close_j <= MID_j.

### B3 LOWER_TOUCH
First j in (t0, t0+20] with:
low_j <= ZD1_j.

### B4 UPPER_OUTER_TOUCH
First j in [t0, t0+20] with:
high_j >= BS_j.

### B5 NEW_HIGH_BEFORE_MID_LOSS
Before B2 occurs, any bar with:
high_j > high_t0.

### B6 STATE_DETERIORATION
For UP-origin:
first transition within 20 bars from UP to RANGE or DOWN.

For RANGE-origin:
first RANGE->DOWN transition.

### Upper sequence buckets
- MID_LOSS_THEN_LOWER
- MID_LOSS_THEN_REBOUND_UPPER
- NEW_HIGH_BEFORE_MID_LOSS
- MID_TOUCH_NO_CLOSE_LOSS
- NO_MID_LOSS_20

After B2, define rebound comparison:
- first subsequent ZK1 touch
- first subsequent ZD1 touch
Whichever occurs first decides rebound/lower outcome.

Measure returns/MFE/MAE from event and B2.

No bucket is pre-labelled reduce/exit.

## C. Fast/outer confluence

At event t0 calculate ATR14 and same-bar rail distance:

Lower:
abs(ZD1_t0 - BD_t0) / ATR14_t0

Upper:
abs(ZK1_t0 - BS_t0) / ATR14_t0

Frozen bins:
- <=0.25 ATR
- >0.25 to <=0.50
- >0.50 to <=1.00
- >1.00

No threshold selection after outcome inspection.
Compare path probabilities and MFE/MAE across all bins.

## D. Gray-band conditional structure

For each gray-band approach event:

### Direction
- support-side: prior close > GZB3 and current low <= GZB3
- resistance-side: prior close < GZB4 and current high >= GZB4

### Penetration
- TOUCH_RECLAIM / TOUCH_REJECT
- ENTER_BAND
- FULL_CROSS

### Slow-band slope
Use midpoint of slow band:
GRAY_MID=(GZB3+GZB4)/2

Slope over 5 bars:
GRAY_SLOPE5 = GRAY_MID_t - GRAY_MID_{t-5}

Normalize:
GRAY_SLOPE5_ATR = GRAY_SLOPE5 / ATR14_t

Frozen slope classes:
- RISING: > +0.10 ATR
- FLAT: [-0.10,+0.10] ATR
- FALLING: < -0.10 ATR

Threshold is frozen before Round 2 outcome access.

### Relation to fast midpoint
DIST_MID_ATR = (close - MID) / ATR14

Frozen bins:
- below -0.5
- [-0.5,+0.5]
- above +0.5

Measure state transition within 20 bars and forward 5/10/20 return/MFE/MAE.

## E. Temporal stability

All Round 2 summaries retain:
- A = 2020-2022
- B = 2023-2024
- C = 2025

A conditional path is only eligible for later rule promotion if:
- direction is coherent in at least two blocks;
- no single block wholly explains the effect;
- sample count is not trivial;
- median/mean and MFE/MAE do not contradict the intended action.

## F. Round 2 outputs

Required:
1. lower path table by origin state
2. upper path table by origin state
3. midpoint confirmation/loss table
4. outer confluence table by ATR bin
5. gray-band conditional table
6. temporal stability table
7. falsified hypotheses list
8. candidate conditions for Round 3

No position sizing, stop loss, leverage or production signal naming in Round 2.
