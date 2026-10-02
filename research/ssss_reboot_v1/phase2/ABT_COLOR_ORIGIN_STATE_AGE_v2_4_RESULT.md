# SSSS Reboot — ABT Color-Origin + State-Age Refinement v2.4 Result

Status: **COMPLETE / EXPLORATORY REFINEMENT**
Date: 2026-10-02

## Boundary

- ABT daily
- Main sample: 2018-01-02 through 2025-12-30 returned by provider
- 2010-2017 used only as warm-up
- FIRST_OBSERVED bar-by-bar XMA
- XMA25/XMA60 unchanged
- true light-gray band = GZB4..GZB3
- this round reuses the same ABT discovery sample and is **not** independent validation
- candidate discussion requires n >= 5

## 1. Lower inner rail — BUY-side refinement

### Color x state age

- **BLUE|21_PLUS** — n=42; MID-first 73.8%; BD-first 26.2%; hit upper 47.6%; touch light-gray 78.6%; MFE20 4.2%; MAE20 -3.6%; ret20 0.9%
- **BLUE|11_20** — n=7; MID-first 57.1%; BD-first 42.9%; hit upper 57.1%; touch light-gray 100.0%; MFE20 6.1%; MAE20 -2.3%; ret20 2.5%
- **GRAY|4_10** — n=6; MID-first 33.3%; BD-first 66.7%; hit upper 50.0%; touch light-gray 83.3%; MFE20 2.8%; MAE20 -4.3%; ret20 -2.1%
- **GREEN|11_20** — n=11; MID-first 9.1%; BD-first 90.9%; hit upper 54.5%; touch light-gray 63.6%; MFE20 4.7%; MAE20 -4.1%; ret20 0.8%
- **GREEN|21_PLUS** — n=12; MID-first 58.3%; BD-first 41.7%; hit upper 83.3%; touch light-gray 75.0%; MFE20 7.3%; MAE20 -2.6%; ret20 5.1%

### Recent color transition

- **GRAY->GREEN** — n=5; MID-first 0.0%; BD-first 100.0%; hit upper 20.0%; touch light-gray 0.0%; MFE20 2.2%; MAE20 -6.3%; ret20 -2.0%

### BUY-side pilot reading

- GREEN 11-20 bars at the inner lower rail remains a poor immediate-entry context:
  BD is reached first in 90.9% of 11 events.
- GREEN 21+ bars changes character materially:
  MID-first 58.3%,
  upper-rail hit 83.3%,
  median MFE20 7.3%
  vs median MAE20 -2.6%.
- BLUE 21+ bars is the largest relatively cleaner lower-rail group:
  n=42,
  MID-first 73.8%,
  BD-first 26.2%.
- A recent GRAY->GREEN transition is especially adverse at the inner lower rail:
  n=5, BD-first 100.0%, MID-first 0.0%, median MAE20 -6.3%.

## 2. Upper inner rail — SELL-side refinement

### Color x state age

- **BLUE|21_PLUS** — n=39; MID-first 46.2%; BS-first 51.3%; hit lower 59.0%; touch light-gray 59.0%; upside MFE20 2.6%; downside MAE20 -4.3%; ret20 -2.1%
- **GRAY|11_20** — n=13; MID-first 30.8%; BS-first 69.2%; hit lower 15.4%; touch light-gray 38.5%; upside MFE20 6.1%; downside MAE20 -2.0%; ret20 5.9%
- **BLUE|4_10** — n=9; MID-first 0.0%; BS-first 100.0%; hit lower 33.3%; touch light-gray 22.2%; upside MFE20 5.6%; downside MAE20 -1.5%; ret20 2.7%
- **BLUE|11_20** — n=7; MID-first 0.0%; BS-first 100.0%; hit lower 57.1%; touch light-gray 28.6%; upside MFE20 4.0%; downside MAE20 -3.6%; ret20 -0.9%
- **GREEN|21_PLUS** — n=15; MID-first 60.0%; BS-first 40.0%; hit lower 53.3%; touch light-gray 93.3%; upside MFE20 3.0%; downside MAE20 -6.3%; ret20 0.8%

### Recent color transition

- **GRAY->BLUE** — n=6; MID-first 0.0%; BS-first 100.0%; hit lower 33.3%; touch light-gray 33.3%; upside MFE20 5.4%; downside MAE20 -2.3%; ret20 2.6%

### SELL-side pilot reading

- BLUE 4-10 bars is not a clean inner-upper SELL context in this sample:
  n=9, BS-first 100.0%.
- BLUE 11-20 bars shows the same continuation pattern:
  n=7, BS-first 100.0%.
- GREEN 21+ bars is more mean-reverting from the inner upper rail:
  MID-first 60.0%,
  BS-first 40.0%,
  median downside excursion 6.3%.
- Recent GRAY->BLUE upper events strongly continued toward BS:
  n=6, BS-first 100.0%, MID-first 0.0%.

## 3. True light-gray band — support from above

### Color x state age

- **BLUE|21_PLUS** — n=42; HOLD20 71.4%; BREAK20 28.6%; MFE20 5.3%; MAE20 -3.2%; ret20 2.2%
- **GRAY|4_10** — n=17; HOLD20 88.2%; BREAK20 11.8%; MFE20 7.1%; MAE20 -1.8%; ret20 4.7%
- **GRAY|11_20** — n=12; HOLD20 91.7%; BREAK20 8.3%; MFE20 7.2%; MAE20 -2.4%; ret20 3.6%
- **GRAY|21_PLUS** — n=9; HOLD20 88.9%; BREAK20 11.1%; MFE20 1.8%; MAE20 -5.4%; ret20 -0.9%

### Recent color transition

- **BLUE->GRAY** — n=6; HOLD20 83.3%; BREAK20 16.7%; MFE20 5.5%; MAE20 -3.2%; ret20 4.4%

## 4. True light-gray band — resistance from below

### Color x state age

- **BLUE|21_PLUS** — n=7; HOLD20 71.4%; BREAK20 28.6%; MFE20 4.5%; MAE20 -3.2%; ret20 2.2%
- **GRAY|4_10** — n=8; HOLD20 62.5%; BREAK20 37.5%; MFE20 1.6%; MAE20 -5.2%; ret20 -2.5%
- **GRAY|11_20** — n=8; HOLD20 87.5%; BREAK20 12.5%; MFE20 7.0%; MAE20 -2.5%; ret20 6.4%
- **GREEN|21_PLUS** — n=17; HOLD20 64.7%; BREAK20 35.3%; MFE20 4.7%; MAE20 -4.7%; ret20 3.1%

### Recent color transition

- **BLUE->GRAY** — n=5; HOLD20 80.0%; BREAK20 20.0%; MFE20 1.5%; MAE20 -7.3%; ret20 -5.6%

## 5. Candidate map for later cross-symbol validation

These are **candidates to validate**, not final rules.

### BUY candidates / avoid zones

- Candidate: GREEN 21+ + inner-lower break.
- Candidate: BLUE 21+ + inner-lower break.
- Avoid-as-first-entry candidate: GREEN 11-20 + inner-lower break; price often travels to BD first.
- Strong avoid signal to validate: recent GRAY->GREEN + inner-lower break; current ABT sample went to BD first in every eligible event.
- Light-gray support candidate: GRAY 4-20 bars, especially when approached from above.
- Recent BLUE->GRAY + light-gray support is a candidate boundary-support event.

### SELL candidates / avoid zones

- Avoid-as-final-exit candidate: BLUE 4-20 + inner-upper break; current ABT sample usually travels to BS first.
- Strong continuation signal to validate: recent GRAY->BLUE + inner-upper break; current eligible ABT events all went to BS first.
- Candidate tactical SELL/trim context: GREEN 21+ + inner-upper break.
- Light-gray resistance candidate: recent BLUE->GRAY from below.
- GRAY light-gray resistance can be short-term pressure, but some age buckets later resume upward, so HOLD probability alone must not be equated with a 20-bar bearish outcome.

## Closure

`ABT_COLOR_ORIGIN_STATE_AGE_v2_4 = COMPLETE`

Next step should validate the same candidate map on another symbol without
changing these definitions.
