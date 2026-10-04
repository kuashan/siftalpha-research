# Pure SLTD State Probability Study v1 — Result

Status: **COMPLETE**

This study tests the predictive value of pure SLTD state information. Chan/缠论 is excluded.

## Funnel

- Discovery state keys: **359**
- Passed discovery gate: **46**
- Passed 79-stock temporal validation: **22**
- Confirmed on fresh 10-stock OOS: **20**
- OOS-confirmed positive states: **12**
- OOS-confirmed negative states: **8**

## OOS-confirmed states

| Direction | Family | State key | Discovery 10d excess | Temporal 10d excess | OOS 10d excess | OOS 20d excess |
|---|---|---|---:|---:|---:|---:|
| POSITIVE | F7_COLOR_AGE_EVENT_SUBTYPE | `GREEN|21_PLUS|LOWER|CLOSE_BELOW` | 2.52% | 1.32% | 2.75% | 3.25% |
| POSITIVE | F3_COLOR_AGE_INNER | `GREEN|21_PLUS|BELOW_ZD1` | 2.11% | 1.65% | 1.56% | 1.20% |
| POSITIVE | F6_COLOR_AGE_EVENT | `GREEN|21_PLUS|LOWER` | 2.05% | 1.17% | 1.99% | 3.63% |
| POSITIVE | F3_COLOR_AGE_INNER | `GREEN|21_PLUS|LOWER_HALF` | 1.87% | 1.39% | 1.55% | 2.00% |
| POSITIVE | F4_COLOR_AGE_SLOWPOS | `GREEN|21_PLUS|BELOW_GZB4` | 1.71% | 0.80% | 1.52% | 2.25% |
| POSITIVE | F4_COLOR_AGE_SLOWPOS | `GREEN|21_PLUS|ABOVE_GZB3` | 1.62% | 0.80% | 0.90% | 3.15% |
| POSITIVE | F2_COLOR_AGE_ORIGIN | `GREEN|21_PLUS|GRAY` | 1.50% | 0.63% | 1.67% | 2.73% |
| POSITIVE | F3_COLOR_AGE_INNER | `GREEN|11_20|BELOW_ZD1` | 1.49% | 2.18% | 2.25% | 5.17% |
| POSITIVE | F1_COLOR_AGE | `GREEN|21_PLUS` | 1.37% | 0.63% | 1.57% | 2.46% |
| POSITIVE | F5_COLOR_AGE_SLOWTREND | `GREEN|21_PLUS|DOWN` | 1.37% | 0.63% | 1.57% | 2.46% |
| POSITIVE | F3_COLOR_AGE_INNER | `GREEN|21_PLUS|UPPER_HALF` | 0.98% | 0.65% | 1.05% | 2.46% |
| NEGATIVE | F7_COLOR_AGE_EVENT_SUBTYPE | `BLUE|21_PLUS|UPPER|WICK_ONLY` | -0.88% | -0.48% | -0.71% | -1.09% |
| POSITIVE | F6_COLOR_AGE_EVENT | `GREEN|21_PLUS|UPPER` | 0.72% | 0.91% | 0.84% | 1.35% |
| NEGATIVE | F3_COLOR_AGE_INNER | `BLUE|21_PLUS|ABOVE_ZK1` | -0.53% | -0.46% | -0.61% | -0.57% |
| NEGATIVE | F4_COLOR_AGE_SLOWPOS | `BLUE|21_PLUS|ABOVE_GZB3` | -0.40% | -0.33% | -0.55% | -0.97% |
| NEGATIVE | F3_COLOR_AGE_INNER | `BLUE|21_PLUS|UPPER_HALF` | -0.37% | -0.37% | -0.55% | -1.16% |
| NEGATIVE | F5_COLOR_AGE_SLOWTREND | `BLUE|21_PLUS|UP` | -0.37% | -0.22% | -0.42% | -0.87% |
| NEGATIVE | F1_COLOR_AGE | `BLUE|21_PLUS` | -0.36% | -0.21% | -0.42% | -0.87% |
| NEGATIVE | F2_COLOR_AGE_ORIGIN | `BLUE|21_PLUS|GRAY` | -0.36% | -0.21% | -0.42% | -0.87% |
| NEGATIVE | F6_COLOR_AGE_EVENT | `BLUE|21_PLUS|UPPER` | -0.31% | -0.51% | -0.90% | -1.00% |

## Family funnel

| Family | Discovery keys | Discovery pass | Temporal pass | OOS confirmed |
|---|---:|---:|---:|---:|
| F1_COLOR_AGE | 15 | 3 | 2 | 2 |
| F2_COLOR_AGE_ORIGIN | 34 | 5 | 2 | 2 |
| F3_COLOR_AGE_INNER | 57 | 10 | 6 | 6 |
| F4_COLOR_AGE_SLOWPOS | 44 | 5 | 3 | 3 |
| F5_COLOR_AGE_SLOWTREND | 22 | 3 | 2 | 2 |
| F6_COLOR_AGE_EVENT | 58 | 10 | 4 | 3 |
| F7_COLOR_AGE_EVENT_SUBTYPE | 104 | 10 | 3 | 2 |
| F8_TRANSITION_EVENT | 25 | 0 | 0 | 0 |

## Decision

At least one positive and one negative state survived all gates.
A separate `PURE_SLTD_PROBABILITY_MAP_CANDIDATE` is therefore allowed by protocol.

No V7 trading rule was changed by this run.

`PURE_SLTD_STATE_PROBABILITY_V1 = COMPLETE`
