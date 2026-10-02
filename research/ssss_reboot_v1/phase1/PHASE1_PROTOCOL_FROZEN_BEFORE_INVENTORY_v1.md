# SSSS Reboot v1 — Phase 1 Structural Inventory Protocol v1

Status: **FROZEN BEFORE STRUCTURAL INVENTORY RUN**
Date: 2026-10-02
Parent Phase: `PHASE0_SOURCE_RECONSTRUCTION = PASS`

## 1. Purpose

Phase 1 describes what the corrected SSSS / ADKBY-E source system actually
contains and how often its observable structures occur.

Phase 1 is descriptive only.

Forbidden in Phase 1:
- forward returns;
- MFE / MAE;
- win rate;
- profit / loss;
- ranking a condition by future performance;
- BUY / SELL promotion;
- position sizing;
- strategy assembly.

## 2. Structural calibration set

The initial structural inventory uses six U.S. daily symbols:

- ABT — numerical calibration anchor
- CRSP — supplied Futu visual example
- PG — supplied Futu visual example
- WMT — supplied Futu visual example
- AAPL — supplied Futu visual example
- ARM — supplied Futu visual example

These symbols are used for reconstruction coverage and structural frequency
description only. They are not an OOS or performance universe.

Data source:
Twelve Data U.S. regular-session daily OHLCV.

Target window:
2020-01-02 through 2026-10-01 where history exists.
ARM begins at its available post-IPO history.

## 3. Required point-in-time representation

All structural statistics in the main Phase-1 inventory use:

`FIRST_OBSERVED`

For every bar t:
- provide only history <= t;
- recompute XMA25 and XMA60 at the finite right edge;
- calculate the corrected slow structure;
- persist only the value/state/event observable at t;
- advance to t+1.

`RENDER_ASOF` is retained only for Futu screenshot QA and is not used for
historical structural frequencies.

## 4. Canonical observable objects

### Price
- Open
- High
- Low
- Close
- Volume

### Fast XMA25 geometry
- VL25
- VH25
- D25 = VH25 - VL25
- ZD1 = VL25 - D25
- MID = (VH25 + VL25) / 2
- ZK1 = VH25 + D25

### Corrected slow structure
- W_H = weighted H over lags 0..19 with weights 20..1 / 210
- W_L = weighted L over lags 0..19 with weights 20..1 / 210
- GZB3 = EMA(W_H,90)
- GZB4 = EMA(W_L,90)
- GZB7 = GZB3 - GZB4
- GZB8 = GZB3 + 2*GZB7
- GZB9 = GZB4 - 2*GZB7

### Outer XMA60 geometry
- VH60 = XMA(XMA(H,60),60)
- VL60 = XMA(XMA(L,60),60)
- D60 = VH60 - VL60
- BS = VH60 + 2.2*D60
- BD = VL60 - 2.8*D60

### Four-state partition
- UP:
  `ZD1 >= GZB9 AND ZK1 >= GZB8`
- DOWN:
  `ZK1 <= GZB8 AND ZD1 <= GZB9`
- RANGE:
  `ZD1 >= GZB9 AND ZK1 <= GZB8`
- EXPANSION:
  all remaining topology, principally
  `ZD1 < GZB9 AND ZK1 > GZB8`

Colors:
- UP = BLUE
- DOWN = GREEN
- RANGE = GRAY
- EXPANSION = separate fourth state

### Momentum raw components
- M1 = EMA(EMA(C,3)-EMA(C,6),9)
- M2 = EMA(EMA(EMA(C,3)-EMA(C,9),3)-EMA(EMA(C,3)-EMA(C,9),9),9)

Persist independently:
- M1 delta
- M2 delta
- M1 rising / falling / flat
- M2 rising / falling / flat
- SSSS rising OR
- SSSS falling OR
- ADKBY ISRED

Do not collapse mixed-direction cases before recording both components.

### ADKBY normalized inner geometry
Using:
- short_top = VH25 + 2*D25
- short_bottom = VL25 - 2*D25

Persist normalized:
- O
- H
- L
- C

and fixed levels:
- 20,000 = ZD1
- 50,000 = MID
- 80,000 = ZK1

## 5. Primitive geometry flags

These are observations, not trading events.

Fast lower rail:
- LOWER_TOUCH:
  `L <= ZD1 <= H`
- FULL_BELOW_LOWER:
  `H < ZD1`
- CLOSE_BELOW_LOWER:
  `C < ZD1`
- LOWER_CROSS:
  exact source topology `CROSS(ZD1,L)`

Fast upper rail:
- UPPER_TOUCH:
  `L <= ZK1 <= H`
- FULL_ABOVE_UPPER:
  `L > ZK1`
- CLOSE_ABOVE_UPPER:
  `C > ZK1`
- UPPER_CROSS:
  exact source topology `CROSS(H,ZK1)`

Midline:
- CLOSE_ABOVE_MID
- CLOSE_BELOW_MID
- MID_CROSS_UP
- MID_CROSS_DOWN

Outer rails:
- BD_TOUCH / BS_TOUCH
- FULL_BELOW_BD / FULL_ABOVE_BS
- CLOSE_BELOW_BD / CLOSE_ABOVE_BS

No semantic action is attached to these flags.

## 6. Source display flags

Persist separately:
- SSSS money-bag display condition
- SSSS person display condition
- ADKBY 多
- ADKBY 空
- ADKBY 平
- ADKBY warning
- ADKBY star

These are source/display semantics, not validated actions.

## 7. State-path fields

For each bar after readiness:
- current state
- previous state
- state run length
- transition type when state changes

Examples:
- DOWN->RANGE
- RANGE->UP
- UP->RANGE
- RANGE->DOWN
- transitions involving EXPANSION

No transition is labeled favorable/bearish in Phase 1.

## 8. Phase-1 descriptive outputs

For each symbol and pooled calibration set:

- ready bar count;
- state bar counts and proportions;
- number of state runs;
- median state-run length;
- maximum state-run length;
- transition matrix counts;
- primitive fast-rail interaction counts;
- outer-rail interaction counts;
- lower/upper source-cross counts;
- ADKBY 多/空/平 counts;
- warning/star counts;
- momentum agreement / conflict counts.

No future price field may be joined to these records.

## 9. Readiness

A bar is Phase-1 ready when:
- corrected slow structure exists;
- fast XMA25 values exist;
- outer XMA60 values exist;
- both momentum components and one-bar deltas exist.

Warm-up bars are retained but excluded from state-frequency denominators.

## 10. Closure gate

Phase 1 may close only when:

1. every observable field above has one canonical definition;
2. the six-symbol FIRST_OBSERVED ledger is generated without future data;
3. state proportions and transition counts reconcile exactly to ready bars;
4. run lengths reconcile to state changes;
5. source lower/upper cross conditions reproduce the formula topology;
6. no forward-return or profitability field appears in the Phase-1 output;
7. remaining ambiguities, if any, are explicitly listed.

On closure:

`PHASE1_STRUCTURE_INVENTORY = CLOSED`

Only then may Phase 2 freeze a finite Event Atlas（事件图谱）.
