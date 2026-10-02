# SSSS Reboot — ABT Integrated Rail + True Light-Gray Band Study v2.1 Protocol Correction

Status: **FROZEN BEFORE CLEAN RERUN**
Date: 2026-10-02

## Why v2.1 exists

The previous ABT studies kept the visual light-gray band as a secondary event and,
more importantly, used the expanded state thresholds GZB8/GZB9 when testing that
event.

That was incorrect for the user's visual "light-gray band".

The source explicitly renders:

`STICKLINE(1=1,GZB3,GZB4,5,0),COLORLIGRAY;`

Therefore:

- TRUE_LIGHT_GRAY_UPPER = GZB3
- TRUE_LIGHT_GRAY_LOWER = GZB4

GZB8/GZB9 remain part of the three-state classification geometry only.
They must NOT be used as the visible light-gray support/resistance band.

All earlier statistics labelled as "light-gray band support/resistance" are
superseded and must not be cited.

## Main statistical window

Symbol: ABT
Interval: daily
Main study window: **2018-01-02 through 2025-12-31** where data exist.

Earlier history may be loaded only as warm-up for the weighted/EMA/XMA structures.
Earlier warm-up bars are excluded from event counts and outcomes.

## XMA

Original XMA structure remains immutable.

All historical values use FIRST_OBSERVED bar-by-bar reconstruction.
No finalized/repainted history is backfilled.

## Integrated event system

Every primary event retains:
- current_state: UP / DOWN / RANGE
- origin_state of the current run
- state_run_age
- age_bucket:
  - FRESH 1-3
  - EARLY 4-10
  - MATURE 11-20
  - LATE 21+
- recent_transition: run_age <= 5

### Inner / outer rails

Retain the frozen events:
- inner lower excursion at ZD1
- inner upper excursion at ZK1
- MID interaction
- outer lower BD
- outer upper BS

### TRUE light-gray band

#### Support-from-above episode

A new support episode begins when:
- prior close is above prior GZB3; and
- current bar reaches the true light-gray band:
  current Low <= current GZB3
  AND current High >= current GZB4; and
- the prior bar was not already in the same support-contact condition.

Record:
- current state / origin / run age;
- whether current close finishes above GZB3, inside [GZB4,GZB3], or below GZB4;
- first decisive exit after the touch:
  - UP_EXIT: close > current first-observed GZB3
  - DOWN_EXIT: close < current first-observed GZB4
- within 20 bars:
  - hit inner upper ZK1
  - hit inner lower ZD1
  - 20-bar MFE / MAE / close return.

Support-oriented structural outcome:
- ZK1 before ZD1 = SUPPORT_SUCCESS
- ZD1 before ZK1 = SUPPORT_FAILURE
- neither within 20 = UNRESOLVED

#### Resistance-from-below episode

A new resistance episode begins when:
- prior close is below prior GZB4; and
- current bar reaches the true light-gray band:
  current High >= current GZB4
  AND current Low <= current GZB3; and
- the prior bar was not already in the same resistance-contact condition.

Record:
- current state / origin / run age;
- whether current close finishes below GZB4, inside [GZB4,GZB3], or above GZB3;
- first decisive exit:
  - DOWN_EXIT: close < GZB4
  - UP_EXIT: close > GZB3
- within 20 bars:
  - hit ZD1
  - hit ZK1
  - MFE / MAE / close return.

Resistance-oriented structural outcome:
- ZD1 before ZK1 = RESISTANCE_SUCCESS
- ZK1 before ZD1 = RESISTANCE_FAILURE
- neither = UNRESOLVED

## Goal

The study is explicitly intended to discover statistically defensible future
BUY / SELL points.

But this run does not pre-label any event as a final trade.
It compares:
- three-state relationship;
- state origin;
- state age;
- inner/mid/outer rail location;
- true light-gray band interaction.

Only groups with n >= 5 may be discussed as candidate contexts.
