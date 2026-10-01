# SSSS Reboot — ABT Rail Support / Resistance Pilot v1.1

Status: **PILOT COMPLETE / SINGLE-SYMBOL DISCOVERY**
Date: 2026-10-02

## Boundary

- Symbol: ABT
- Daily bars
- Main window: 2020-01-02 through 2025-12-30 returned by provider
- XMA: original source XMA25 / XMA60, unchanged
- Historical method: FIRST_OBSERVED, recalculated bar-by-bar
- No finalized/repainted future rail is backfilled into prior decisions
- This is one-symbol discovery evidence, not a frozen trading rule

State names are used as the primary key:
- UP = source COLOR000066 (deep blue)
- DOWN = source COLOR003300 (deep green)
- RANGE = source COLOR555555 (deep gray)

## 1. Inner lower rail excursion

20-bar results:

| State | n | 20d median return | 20d median MFE | 20d median MAE | Hit MID | Hit upper rail | Hit outer lower BD | MID first | BD first |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| UP | 33 | 0.1% | 2.6% | -4.2% | 81.8% | 48.5% | 48.5% | 57.6% | 39.4% |
| DOWN | 29 | 2.3% | 4.8% | -4.1% | 89.7% | 58.6% | 75.9% | 27.6% | 72.4% |
| RANGE | 12 | 0.6% | 3.6% | -3.2% | 91.7% | 58.3% | 58.3% | 50.0% | 50.0% |

Pilot reading:
- DOWN lower-rail excursions often eventually rebound, but they more often reach BD before MID.
- UP and RANGE have a more balanced / less adverse first-hit path.
- A lower-rail excursion is therefore not the same structural event across the three states.

## 2. Inner upper rail excursion

20-bar results:

| State | n | 20d median return | 20d median MFE | 20d median MAE | Hit MID | Hit lower rail | Hit outer upper BS | MID first | BS first |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| UP | 38 | -0.4% | 3.6% | -3.8% | 89.5% | 50.0% | 68.4% | 34.2% | 63.2% |
| DOWN | 22 | 1.6% | 3.0% | -3.9% | 86.4% | 45.5% | 50.0% | 59.1% | 40.9% |
| RANGE | 14 | 4.8% | 5.0% | -2.6% | 71.4% | 28.6% | 71.4% | 35.7% | 57.1% |

Pilot reading:
- In UP, an upper-rail excursion frequently continues to BS before it falls to MID.
- In DOWN, MID is reached before BS more often than the reverse.
- Therefore treating every inner upper-rail excursion as the same immediate sell point is not supported by this ABT pilot.

## 3. MID support from above

20-bar structural race:

| State | n | Close back above MID on touch | Hit upper before lower (support success) | Hit lower before upper (failure) |
|---|---:|---:|---:|---:|
| UP | 115 | 49.6% | 48.7% | 49.6% |
| DOWN | 61 | 55.6% | 65.6% | 34.4% |
| RANGE | 50 | 66.7% | 54.0% | 46.0% |

ABT does not show one universal MID-support probability; it is state-dependent.

## 4. Outer lower BD as support candidate

20-bar results:

| State | n | 20d median return | Median MFE | Median MAE | Re-hit inner lower rail | Reach MID |
|---|---:|---:|---:|---:|---:|---:|
| UP | 6 | 1.6% | 7.1% | -4.1% | 100.0% | 100.0% |
| DOWN | 20 | 2.0% | 5.8% | -3.4% | 100.0% | 85.0% |
| RANGE | 10 | 4.1% | 7.3% | -1.3% | 100.0% | 70.0% |

In this pilot, every complete 20-bar BD event returned at least to the inner lower rail.

## 5. Outer upper BS as resistance candidate

20-bar results:

| State | n | 20d median return | Median MFE | Median MAE | Re-hit inner upper rail | Reach MID |
|---|---:|---:|---:|---:|---:|---:|
| UP | 21 | 0.7% | 4.3% | -3.0% | 100.0% | 95.2% |
| DOWN | 4 | 1.9% | 4.9% | -2.6% | 100.0% | 50.0% |
| RANGE | 10 | 2.3% | 5.0% | -3.4% | 100.0% | 80.0% |

Every complete 20-bar BS event returned to at least the inner upper rail in this pilot.
That supports a mean-reversion / pressure interpretation, but not necessarily an
immediate short because the close-to-close return can still be positive.

## 6. Light-gray slow band

Support from above:

| State | episodes | Hold above band on touch | Exit upward first within 20 | Exit downward first |
|---|---:|---:|---:|---:|
| UP | 60 | 45.0% | 81.7% | 8.3% |
| DOWN | 1 | 0.0% | 100.0% | 0.0% |
| RANGE | 7 | 57.1% | 100.0% | 0.0% |

Resistance from below:

| State | episodes | Hold below band on touch | Exit downward first within 20 | Exit upward first |
|---|---:|---:|---:|---:|
| UP | 0 | — | — | — |
| DOWN | 45 | 47.8% | 82.2% | 8.9% |
| RANGE | 8 | 50.0% | 87.5% | 12.5% |

The slow-band directional hypothesis is visible in ABT, especially:
- support-from-above in UP;
- resistance-from-below in DOWN.

But the single-symbol sample is not sufficient for a final rule.

## 7. Pilot status

All four user questions produce coherent measurable outputs.

No XMA modification was required.

The pilot is suitable for discussion before scaling to additional symbols.

`ABT_RAIL_STUDY_PILOT_v1_1 = COMPLETE`
