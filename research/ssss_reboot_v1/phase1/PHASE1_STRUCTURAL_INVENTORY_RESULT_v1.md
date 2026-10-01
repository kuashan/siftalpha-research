# SSSS Reboot v1 — Phase 1 Structural Inventory Result v1

Status: **COMPLETE / DESCRIPTIVE ONLY**
Date: 2026-10-02
Representation: **FIRST_OBSERVED**

No future-return, MFE/MAE, PnL, win-rate, or trading-policy field was used.

## 1. Dataset

Structural calibration set:

- ABT
- CRSP
- PG
- WMT
- AAPL
- ARM

Daily U.S. regular-session OHLCV from Twelve Data.

Main count window:
2020-01-02 through 2026-10-01 where history exists.
ARM begins later because its history starts after IPO.

Ready FIRST_OBSERVED bars:

**9,226**

## 2. Four-state inventory

| State | Bars | Share |
|---|---:|---:|
| UP / BLUE | 4,298 | 46.59% |
| DOWN / GREEN | 2,404 | 26.06% |
| RANGE / GRAY | 2,503 | 27.13% |
| EXPANSION | 21 | 0.23% |

Reconciliation:

`4298 + 2404 + 2503 + 21 = 9226`

### Structural interpretation

The fourth EXPANSION topology is real, not merely a theoretical missing case,
but it is rare in this six-symbol structural calibration set.

It appears:
- WMT: 18 bars
- AAPL: 3 bars
- ABT / CRSP / PG / ARM: 0 bars

No performance meaning is attached to EXPANSION in Phase 1.

## 3. State persistence by symbol

Median run length in trading bars:

| Symbol | UP | DOWN | RANGE | EXPANSION |
|---|---:|---:|---:|---:|
| ABT | 49 | 27.5 | 11 | — |
| CRSP | 35 | 35 | 15.5 | — |
| PG | 34.5 | 34 | 14 | — |
| WMT | 43 | 19 | 12 | 9 |
| AAPL | 49 | 30 | 13.5 | 3 |
| ARM | 43 | 53 | 28.5 | — |

Maximum observed run lengths:

| Symbol | UP | DOWN | RANGE | EXPANSION |
|---|---:|---:|---:|---:|
| ABT | 118 | 125 | 62 | — |
| CRSP | 96 | 172 | 58 | — |
| PG | 179 | 84 | 76 | — |
| WMT | 286 | 78 | 81 | 17 |
| AAPL | 206 | 76 | 34 | 3 |
| ARM | 104 | 61 | 54 | — |

The three main states are persistent multi-bar structures, not single-bar
decorations.

## 4. Transition topology

Pooled state transitions:

| Transition | Count |
|---|---:|
| UP -> RANGE | 69 |
| RANGE -> DOWN | 62 |
| DOWN -> RANGE | 62 |
| RANGE -> UP | 66 |
| UP -> DOWN | 1 |
| DOWN -> EXPANSION | 2 |
| EXPANSION -> DOWN | 2 |
| EXPANSION -> UP | 1 |
| UP -> EXPANSION | 1 |

Total transitions: **266**

The four transitions that pass through RANGE account for:

`259 / 266 = 97.37%`

of all observed state changes.

Direct UP -> DOWN occurs only once in this calibration set.

This is a structural fact only. It does not imply that a RANGE transition should
be traded.

## 5. State-run reconciliation

Total state runs:

- UP: 72
- DOWN: 65
- RANGE: 132
- EXPANSION: 3

Total:

`272 runs`

Across six independent symbol histories:

`272 - 6 = 266 expected transitions`

Observed:

`266 transitions`

Reconciliation: **PASS**

## 6. Primitive fast-rail interactions

| Primitive | Count | Share of ready bars |
|---|---:|---:|
| LOWER_TOUCH | 1,319 | 14.30% |
| UPPER_TOUCH | 1,637 | 17.74% |
| LOWER_CROSS | 482 | 5.22% |
| UPPER_CROSS | 540 | 5.85% |
| MID_CROSS_UP | 570 | 6.18% |
| MID_CROSS_DOWN | 577 | 6.25% |
| FULL_BELOW_LOWER | 879 | 9.53% |
| FULL_ABOVE_UPPER | 1,366 | 14.81% |
| CLOSE_BELOW_LOWER | 1,525 | 16.53% |
| CLOSE_ABOVE_UPPER | 2,234 | 24.21% |

These are geometric observations only.

## 7. Outer-rail interactions

| Primitive | Count | Share |
|---|---:|---:|
| BD_TOUCH | 596 | 6.46% |
| BS_TOUCH | 864 | 9.36% |
| FULL_BELOW_BD | 416 | 4.51% |
| FULL_ABOVE_BS | 1,540 | 16.69% |
| CLOSE_BELOW_BD | 692 | 7.50% |
| CLOSE_ABOVE_BS | 1,977 | 21.43% |

The source outer rails are therefore active structural objects rather than
nearly unreachable decorative lines.

Phase 1 does not infer whether crossing them is good or bad.

## 8. SSSS / ADKBY source-display reconciliation

SSSS display conditions:

- money-bag: 482
- person: 538
- total displayed rail icons: **1,020**

ADKBY text labels:

- 多: 341
- 空: 301
- 平: 378
- total: **1,020**

Reconciliation:

`SSSS icon total = ADKBY 多/空/平 total = 1020`

This strongly supports the formula-level mapping between:
- SSSS lower/upper rail events;
- current state;
- ADKBY 多/空/平 semantic text.

Raw UPPER_CROSS count is 540, two higher than the SSSS person count.
Those two cases occur when the state is EXPANSION, where the original three
GZB12/GZB13/GZB14 display branches do not assign a normal icon/text semantic.

This is direct evidence that EXPANSION is genuinely outside the three-state
source display vocabulary.

## 9. Momentum decomposition

Raw two-component direction:

| Class | Bars | Share |
|---|---:|---:|
| both/effective UP | 4,028 | 43.66% |
| both/effective DOWN | 4,008 | 43.44% |
| CONFLICT | 1,190 | 12.90% |

In all 1,190 conflict bars:
- one raw component rises;
- the other falls;
- SSSS `rising OR` is true;
- SSSS `falling OR` is also true.

Therefore:

`SSSS_RISING = TRUE`

and

`SSSS_FALLING = TRUE`

can coexist on a material fraction of bars.

ADKBY-E collapses those bars through:

`ISRED = any component rising`

This is a real source-semantic difference, not a rare floating-point edge case.

Phase 2 must preserve both raw momentum components before defining any event
that uses momentum.

## 10. ADKBY auxiliary display frequency

- warning: 443 bars (4.80%)
- star: 461 bars (5.00%)

These are common enough to retain in the structural schema, but Phase 1 assigns
no predictive meaning to either symbol.

## 11. What Phase 1 establishes

The source system has a coherent observable architecture:

```text
PRICE
  -> XMA25 FAST GEOMETRY
  -> CORRECTED SLOW STRUCTURE
  -> FOUR-STATE TOPOLOGY
  -> XMA60 OUTER GEOMETRY
  -> PRIMITIVE RAIL INTERACTIONS
  -> SOURCE DISPLAY SEMANTICS
```

ADKBY-E is structurally consistent with the SSSS inner XMA25 state/event family,
while adding normalization and semantic display labels.

No trading rule has been created.

## 12. Phase-1 boundary

Not evaluated:
- what happens after any state;
- what happens after any rail touch/cross;
- whether 多/空/平 are profitable;
- whether money-bag/person should be acted upon;
- whether warning/star predicts reversal;
- whether any transition is bullish or bearish.

Those questions remain prohibited until a Phase-2 Event Atlas is frozen and
Phase 3 later measures forward behavior.
