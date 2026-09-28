# Falsification v1 — Time-to-Confirmation Survival (Stocks)

Status: STAGE 2 COMPLETE FOR FROZEN STOCK CONFLUENCE EVENTS  
Date: 2026-09-28

## Scope

This analysis implements the already-frozen time-to-event task without changing any geometry threshold.

Frozen endpoints:

- Lower strict confluence -> leave DOWN;
- Lower strict confluence -> FAST_MID_ANALYTIC reclaim;
- Upper strict confluence -> leave UP;
- Upper strict confluence -> FAST_MID_ANALYTIC loss.

Frozen horizons: 3 / 5 / 10 / 20 / 40 bars.

Event population is the corrected full stock set from:
- EQUITY_EVENTS_CHUNK1.json
- EQUITY_EVENTS_CHUNK2.json
- EQUITY_EVENTS_CHUNK3.json

This is important because the older EVENTS_ENRICHED.json contains only the earlier partial event population and is not used here.

Method:
Kaplan-Meier cumulative endpoint probability with right-censoring at the frozen validation-window end.
Same-bar endpoint is counted as bar 0.

No time-stop is promoted from this analysis.

## Lower strict confluence

### Leave DOWN

| Window | n | by 3 | by 5 | by 10 | by 20 | by 40 | KM median bar |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Validation A | 325 | 0.0% | 0.0% | 0.9% | 22.0% | 61.6% | 33 |
| Validation B | 20 | 0.0% | 0.0% | 5.0% | 23.4% | 45.3% | not reached |
| Combined | 345 | 0.0% | 0.0% | 1.2% | 22.0% | 61.1% | 34 |

Observed event-time median among uncensored cases:
- A: 33 bars
- B: 20 bars
- Combined: 32 bars

Interpretation:
leaving DOWN is generally slow. In Validation A, essentially no lower-confluence event leaves DOWN inside 5 bars, only about 0.9% by 10 bars, and about 61.6% by 40 bars.
Validation B has only n=20, so it remains below the frozen >=30 subgroup threshold.

### FAST_MID_ANALYTIC reclaim

| Window | n | by 3 | by 5 | by 10 | by 20 | by 40 | KM median bar |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Validation A | 325 | 23.2% | 39.2% | 66.9% | 91.1% | 100.0% | 7 |
| Validation B | 20 | 35.0% | 50.0% | 65.7% | 84.8% | 100.0% | 5 |
| Combined | 345 | 23.9% | 39.8% | 66.8% | 90.7% | 100.0% | 7 |

Interpretation:
midpoint reclaim happens much earlier than formal departure from DOWN.
Validation A reaches a KM median of 7 bars, versus 33 bars for leaving DOWN.

However, this is timing evidence only.
The independent midpoint study already showed that midpoint crossing direction alone is not a validated directional-return signal.
Therefore:
FAST_MID_ANALYTIC reclaim remains a lifecycle observation marker, not a promoted buy confirmation.

## Upper strict confluence

### Leave UP

| Window | n | by 3 | by 5 | by 10 | by 20 | by 40 | KM median bar |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Validation A | 392 | 0.5% | 0.8% | 2.3% | 13.1% | 44.4% | not reached |
| Validation B | 46 | 0.0% | 0.0% | 2.2% | 9.4% | 37.3% | not reached |
| Combined | 438 | 0.5% | 0.7% | 2.3% | 12.7% | 43.8% | not reached |

Interpretation:
leaving UP is also slow.
Even by 40 bars, only about 44.4% of Validation A and 37.3% of Validation B have left UP.
A 50% KM median is not reached inside 40 bars.

This reinforces the earlier falsification result:
upper strict confluence is not an automatic top or immediate deterioration event.

### FAST_MID_ANALYTIC loss

| Window | n | by 3 | by 5 | by 10 | by 20 | by 40 | KM median bar |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Validation A | 392 | 23.7% | 35.2% | 57.1% | 82.1% | 98.0% | 9 |
| Validation B | 46 | 24.2% | 50.9% | 73.2% | 88.9% | 97.8% | 5 |
| Combined | 438 | 23.8% | 36.8% | 58.8% | 82.8% | 97.9% | 9 |

Interpretation:
midpoint loss occurs substantially earlier than leaving UP.
KM median:
- Validation A: 9 bars
- Validation B: 5 bars

Again, timing does not imply edge.
The independent midpoint study found no standalone directional advantage, so midpoint loss cannot be promoted as an automatic sell/short condition.

## Falsification conclusion

1. State departure is slow after both lower and upper strict confluence.
2. FAST_MID_ANALYTIC crossing is a much faster post-confluence event.
3. The faster timing does not rescue the failed general confluence hypotheses.
4. It also does not validate midpoint crossing as a directional signal.
5. No time-stop is promoted in Falsification v1.
6. Any future rule such as "confluence + midpoint event within N bars" would be a new conditional hypothesis and must be preregistered for a later sealed window; N must not be chosen from these holdout outcomes.

Classification:
- lower confluence -> leave DOWN timing: DESCRIPTIVE
- lower confluence -> midpoint reclaim timing: OBSERVE / LIFECYCLE CONTEXT
- upper confluence -> leave UP timing: DESCRIPTIVE
- upper confluence -> midpoint loss timing: OBSERVE / LIFECYCLE CONTEXT

The 2026H1 sealed window remains untouched.
