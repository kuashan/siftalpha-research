# SSSS Conditional Rail Rules v1 — Round 2 Consolidated Result

Status: **ROUND2 COMPLETE / DISCOVERY ONLY**
Date: 2026-10-01

## Scope
- 39 frozen equities
- 2020-2025 daily evaluation
- 2019 warm-up
- strict first-observed point-in-time XMA25/XMA60
- fast rail events: 5619
- gray-band events: 5781

## 1. Lower rail

| Initial state | n | 20-bar mean | median | Mid reclaim <=10 | Mid reclaim <=20 | 20-bar after reclaim |
|---|---:|---:|---:|---:|---:|---:|
| UP | 1343 | +1.293% | +1.259% | 57.26% | 85.03% | +1.758% |
| DOWN | 629 | **+2.975%** | **+2.707%** | **66.14%** | **89.03%** | **+2.864%** |
| RANGE | 607 | +1.099% | +1.185% | 57.66% | 87.15% | +1.287% |

DOWN + lower is the strongest broad lower-rail candidate.
Its event return is positive in every time block:
- 2020-2022: +2.513%
- 2023-2024: +3.332%
- 2025: +3.786%

Mid reclaim is common, but it does not create the edge by itself:
DOWN event +2.975% vs post-reclaim +2.864%.

After reclaim, first rail decision within the original 20-bar window:
- UP initial: upper first 789/1142 = 69.1%; lower-outer first 109/1142 = 9.5%
- DOWN initial: upper first 378/560 = 67.5%; lower-outer first 98/560 = 17.5%
- RANGE initial: upper first 385/529 = 72.8%; lower-outer first 56/529 = 10.6%

## 2. Lower-event state transitions

### RANGE -> UP
- n=25 across 20 symbols
- 20-bar mean **+10.581%**
- median **+8.509%**
- positive **96.0%**
- 2020-2022 +10.904%
- 2023-2024 +9.151%
- 2025 +12.003%

This is the strongest bullish transition found in Round 2, but sample size remains modest.

### DOWN -> RANGE
- n=33 across 24 symbols
- mean +6.573%
- median +7.569%
- positive 75.76%
- but 2025 mean -2.386%

Promising but not temporally stable enough to promote.

### UP -> RANGE after a lower event
- n=367 across all 39 symbols
- mean **-1.495%**
- median -1.075%
- positive only 43.05%
- all three time blocks have negative mean

This is a robust deterioration/invalidation candidate.

## 3. Upper rail

| Initial state | n | 20-bar mean | median | Mid loss <=10 | Mid loss <=20 | 20-bar after mid loss |
|---|---:|---:|---:|---:|---:|---:|
| UP | 1654 | **+1.241%** | +0.893% | 53.57% | 78.72% | **+0.596%** |
| DOWN | 742 | +2.130% | +2.057% | 45.82% | 71.29% | +0.575% |
| RANGE | 638 | +1.024% | +1.263% | 51.41% | 76.80% | +1.142% |

Important falsification:
**UP/red + upper rail alone is not a sell rule in the six-year 39-stock sample.**
Even after midpoint loss, average 20-bar return remains positive.

Therefore midpoint loss alone is also insufficient as a full-exit rule.

## 4. Upper-event state transitions

### UP -> RANGE
- n=39 across 24 symbols
- 20-bar mean **-7.572%**
- median **-4.752%**
- positive only 20.51%
- block means: -8.660%, -6.313%, -7.936%

This is a strong bearish/reduce-exit candidate.

### RANGE -> DOWN
- n=27 across 18 symbols
- 20-bar mean **-9.553%**
- median **-8.052%**
- positive only 7.41%
- block means: -8.635%, -10.224%, -10.588%

This is the strongest bearish transition found in Round 2.

## 5. Outer-rail confluence

No universal rule that "closer fast/outer rails = stronger signal" survived.

For DOWN lower events:
- <=0.25 ATR: n=133, +2.648%
- 0.25-0.50: n=117, +3.315%
- 0.50-1.00: n=169, +2.694%
- >1.00: n=210, +3.215%

There is no monotonic proximity effect.

One candidate exception:
RANGE lower with fast/outer distance 0.25-0.50 ATR:
- n=37 / 20 symbols
- mean **+4.519%**
- median **+6.719%**
- positive **78.38%**
- only 2 cases in 2025, so this remains a hypothesis, not a rule.

Upper-outer proximity did not produce a stable sell edge.

## 6. Light-gray band

### RANGE + approach from above + rising slow band
- n=775 / all 39 symbols
- 20-bar mean **+1.195%**
- median +1.032%
- positive 56.13%
- block means +1.072%, +0.756%, +2.422%

This behaves mildly support-like.

### RANGE + full cross from below through gray band
- n=145 / 37 symbols
- 20-bar mean **+2.867%**
- median **+2.698%**
- positive 62.07%
- block means +3.485%, +2.580%, +1.816%

This is a much clearer bullish structural event.
It directly contradicts a simple rule that the gray band is always resistance when approached from below.

### RANGE + full cross from above through gray band
- n=174
- mean -0.434%
- not stable across blocks

Therefore the gray band is best treated as a slow structural regime zone, not a fixed support/resistance strip.

## 7. Round 2 research interpretation

Current evidence supports studying the following conditional map:

Potential bullish side:
1. DOWN + lower fast rail = broad probe-entry candidate.
2. RANGE -> UP after a lower event = strong confirmation/add candidate.
3. RANGE full cross upward through the gray band = structural bullish confirmation.
4. Midpoint reclaim alone is confirmation of recovery, not sufficient alpha by itself.

Potential bearish side:
1. Upper rail alone = watch, not automatic sell.
2. Midpoint loss alone = insufficient.
3. UP -> RANGE after an upper event = strong reduce/exit candidate.
4. RANGE -> DOWN after an upper event = strongest exit/invalidation candidate.

Rejected as general standalone rules:
- any lower rail = buy
- red/UP upper rail = sell
- midpoint loss = full exit
- outer rail proximity always strengthens signal
- gray band from below = resistance

No production strategy is frozen yet.
Round 3 must test concentration, volatility dependence, leave-one-symbol-out stability, MFE/MAE, and false-positive/failure behavior before rule promotion.
