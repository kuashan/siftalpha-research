# SLTD A-share 50 Integrated Risk v1 — Stage A Result

Status: **PROMOTED_TO_INTEGRATED_HOLDOUT**

- Market: **China A-share main board**
- Development symbols used: **35**
- Fresh OOS performance read: **NO**
- US fitted state weights used: **NO**
- Chan/缠论: **NOT USED**
- Score Momentum: **NOT USED**

## State funnel

- Discovery state keys: **290**
- Discovery support-pass: **191**
- Temporally stable negative states: **28**
- Stable negative components: **EVENT, INNER, REGIME, SLOW**
- Severe threshold (Discovery negative-risk 25th percentile): **-1.32665**

## Severe Risk diagnostics

| Split | Events | Symbols | 10d ret excess | 20d ret excess | 10d MAE safety | 20d MAE safety | 10d loss lift | 20d loss lift | 10d FDD diff | 20d FDD diff |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Discovery | 4760 | 35 | -0.609% | -1.268% | -0.328% | -0.638% | 5.925% | 6.858% | -0.298% | -0.219% |
| Temporal | 2182 | 35 | -0.013% | -0.317% | -0.226% | -0.249% | 3.459% | 0.618% | -0.390% | -0.525% |

## Strongest A-share stable negative states

| Component | State | Discovery utility | Temporal utility | D 10d return excess | T 10d return excess |
|---|---|---:|---:|---:|---:|
| EVENT | `F6_COLOR_AGE_EVENT::BLUE|11_20|LIGHT_SUPPORT` | -2.797 | -0.987 | -0.374% | -0.454% |
| EVENT | `F7_COLOR_AGE_EVENT_SUBTYPE::BLUE|11_20|LIGHT_SUPPORT|CONTACT` | -2.797 | -0.987 | -0.374% | -0.454% |
| EVENT | `F7_COLOR_AGE_EVENT_SUBTYPE::GRAY|21_PLUS|LOWER|CLOSE_BELOW` | -2.379 | -1.923 | -0.636% | -0.187% |
| EVENT | `F7_COLOR_AGE_EVENT_SUBTYPE::BLUE|21_PLUS|UPPER|WICK_ONLY` | -2.225 | -7.489 | -0.821% | -2.882% |
| INNER | `F3_COLOR_AGE_INNER::BLUE|21_PLUS|UPPER_HALF` | -1.976 | -3.635 | -0.664% | -1.101% |
| SLOW | `F4_COLOR_AGE_SLOWPOS::GREEN|21_PLUS|ABOVE_GZB3` | -1.973 | -4.932 | -0.746% | -1.409% |
| EVENT | `F7_COLOR_AGE_EVENT_SUBTYPE::BLUE|11_20|LOWER|WICK_ONLY` | -1.826 | -1.720 | -0.576% | -0.400% |
| INNER | `F3_COLOR_AGE_INNER::BLUE|4_10|ABOVE_ZK1` | -1.772 | -1.016 | -1.052% | -0.450% |
| INNER | `F3_COLOR_AGE_INNER::BLUE|21_PLUS|LOWER_HALF` | -1.754 | -1.621 | -0.791% | -0.417% |
| SLOW | `F4_COLOR_AGE_SLOWPOS::BLUE|4_10|ABOVE_GZB3` | -1.739 | -0.041 | -1.011% | -0.288% |
| INNER | `F3_COLOR_AGE_INNER::BLUE|11_20|ABOVE_ZK1` | -1.727 | -1.579 | -0.353% | -0.332% |
| REGIME | `F2_COLOR_AGE_ORIGIN::BLUE|4_10|GRAY` | -1.715 | -0.512 | -0.964% | -0.238% |
| EVENT | `F7_COLOR_AGE_EVENT_SUBTYPE::BLUE|21_PLUS|UPPER|CLOSE_ABOVE` | -1.661 | -0.472 | -1.415% | -0.929% |
| REGIME | `F2_COLOR_AGE_ORIGIN::GRAY|11_20|GREEN` | -1.602 | -0.603 | -0.537% | -0.239% |
| EVENT | `F6_COLOR_AGE_EVENT::GRAY|21_PLUS|LOWER` | -1.591 | -5.251 | -0.320% | -2.180% |
| EVENT | `F6_COLOR_AGE_EVENT::BLUE|21_PLUS|UPPER` | -1.412 | -5.686 | -0.999% | -1.953% |
| REGIME | `F2_COLOR_AGE_ORIGIN::BLUE|11_20|GRAY` | -1.327 | -0.111 | -0.590% | -0.164% |
| EVENT | `F6_COLOR_AGE_EVENT::BLUE|11_20|LOWER` | -1.079 | -2.714 | -0.387% | -1.048% |
| SLOW | `F4_COLOR_AGE_SLOWPOS::BLUE|21_PLUS|ABOVE_GZB3` | -1.062 | -2.648 | -0.556% | -0.887% |
| REGIME | `F1_COLOR_AGE::BLUE|21_PLUS` | -0.883 | -2.188 | -0.346% | -0.574% |
| REGIME | `F2_COLOR_AGE_ORIGIN::BLUE|21_PLUS|GRAY` | -0.883 | -2.353 | -0.318% | -0.686% |
| SLOW | `F5_COLOR_AGE_SLOWTREND::BLUE|21_PLUS|UP` | -0.883 | -2.188 | -0.346% | -0.574% |
| EVENT | `F7_COLOR_AGE_EVENT_SUBTYPE::BLUE|21_PLUS|LOWER|WICK_ONLY` | -0.537 | -1.876 | -0.759% | -0.565% |
| INNER | `F3_COLOR_AGE_INNER::BLUE|11_20|UPPER_HALF` | -0.453 | -1.140 | -0.899% | -0.818% |
| SLOW | `F5_COLOR_AGE_SLOWTREND::GRAY|11_20|DOWN` | -0.218 | -1.178 | -0.092% | -0.395% |

## Gates

- temporal_event_count_ge_500: **PASS**
- temporal_symbol_count_ge_20: **PASS**
- temporal_ret10_excess_negative: **PASS**
- temporal_ret20_excess_negative: **PASS**
- temporal_mae10_safety_negative: **PASS**
- temporal_mae20_safety_negative: **PASS**
- temporal_loss10_lift_positive: **PASS**
- temporal_loss20_lift_positive: **PASS**
- temporal_fdd10_worse: **PASS**
- temporal_fdd20_worse: **PASS**

`SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_A = PROMOTED_TO_INTEGRATED_HOLDOUT`
