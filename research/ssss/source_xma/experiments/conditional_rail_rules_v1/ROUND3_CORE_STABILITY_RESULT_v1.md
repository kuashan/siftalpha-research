# SSSS Conditional Rail Rules v1 — Round 3 Core Stability Result

Status: **CORE STABILITY COMPLETE / MFE-MAE PART B PENDING**
Date: 2026-10-01

Strict chronology: first-observed point-in-time XMA25/XMA60 only.
Input: all 39 equities, Round-2 frozen event ledgers.
Fast events: 5619
Gray-band events: 5781

## Candidate stability

| ID | Condition | n | symbols | 20-bar mean | median | expected-sign symbols | failure | severe failure | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| B1 | DOWN + LOWER_FAST | 629 | 39 | 2.98% | 2.71% | 87.18% | 39.27% | 18.28% | ROBUST_CANDIDATE |
| B2 | LOWER_FAST then RANGE->UP | 25 | 20 | 10.58% | 8.51% | 100.00% | 4.00% | 4.00% | CONDITIONAL_CANDIDATE_SMALL_SAMPLE |
| B3 | GRAY FROM_BELOW + RANGE + FULL_CROSS | 145 | 37 | 2.87% | 2.70% | 75.68% | 37.93% | 16.55% | CONDITIONAL_CANDIDATE |
| S1 | UPPER_FAST then UP->RANGE | 39 | 24 | -7.57% | -4.75% | 87.50% | 20.51% | 0.00% | ROBUST_CANDIDATE_MODERATE_SAMPLE |
| S2 | UPPER_FAST then RANGE->DOWN | 27 | 18 | -9.55% | -8.05% | 88.89% | 7.41% | 3.70% | CONDITIONAL_CANDIDATE_STRONG_EFFECT_SMALL_SAMPLE |
| C1 | LOWER_FAST then UP->RANGE | 367 | 39 | -1.49% | -1.08% | 66.67% | 44.69% | 19.07% | OBSERVE_ONLY |

## B1 — DOWN + lower fast rail
- n=629, all 39 symbols.
- 20-bar mean 2.98%, median 2.71%.
- 87.18% of symbol-level means are positive.
- Leave-one-symbol-out mean remains positive for every omitted symbol:
  2.80% to 3.18%.
- Temporal blocks remain positive:
  A 2.51%,
  B 3.33%,
  C 3.79%.
- Failure rate 39.27%;
  severe <=-5% failure 18.28%.
- Classification: **ROBUST_CANDIDATE**, but failure tail means it is a probe/recovery setup, not evidence for unconditional full-size entry.

## B2 — lower event then RANGE -> UP
- n=25, 20 symbols.
- mean 10.58%, median 8.51%.
- all symbol-level means have the expected positive sign.
- leave-one-symbol-out remains positive: 9.92% to 11.34%.
- only 4.00% failures (1 event).
- All three frozen time blocks are strongly positive.
- Classification: **CONDITIONAL_CANDIDATE** because effect is exceptionally strong but sample is only 25 events.

## B3 — RANGE full cross upward through gray band
- n=145, 37 symbols.
- mean 2.87%, median 2.70%.
- leave-one-symbol-out remains positive: 2.41% to 3.21%.
- A/B/C block means remain positive, but effect weakens over time.
- Failure rate 37.93%.
- Classification: **CONDITIONAL_CANDIDATE**, useful as structural confirmation rather than standalone entry.

## S1 — upper event then UP -> RANGE
- n=39, 24 symbols.
- mean -7.57%, median -4.75%.
- expected bearish sign at 87.50% of symbol-level means.
- leave-one-symbol-out remains negative: -8.33% to -6.74%.
- A/B/C block means are all negative.
- False-positive rate 20.51%; no >=+5% severe false positive in this sample.
- Classification: **ROBUST_CANDIDATE_MODERATE_SAMPLE**.

## S2 — upper event then RANGE -> DOWN
- n=27, 18 symbols.
- mean -9.55%, median -8.05%.
- expected bearish sign at 88.89% of symbol-level means.
- leave-one-symbol-out remains negative: -10.21% to -8.34%.
- A/B/C block means: -8.63%,
  -10.22%,
  -10.59%.
- False-positive rate only 7.41%.
- Classification: **CONDITIONAL_CANDIDATE_STRONG_EFFECT_SMALL_SAMPLE**.
  It is the strongest bearish effect but only 27 events.

## C1 — lower event then UP -> RANGE
- n=367, mean -1.49%.
- leave-one-out sign is stable and all broad blocks are negative, but
  symbol-level sign agreement is only 66.67%
  and failure rate is 44.69%.
- Classification: **OBSERVE_ONLY**. It is deterioration context, not a clean standalone exit.

## Concentration
No candidate flips sign in leave-one-symbol-out testing.
B1 is the broadest: 629 events / 39 symbols.
B2 and S2 remain the most sample-size-sensitive because they have only 25 and 27 events.

Top-5 expected-direction contribution shares:
- B1 33.50%
- B2 42.56%
- B3 47.14%
- S1 49.83%
- S2 54.71%

These are material but no single symbol removal destroys any effect.

## Round-3 part B
MFE/MAE excursion audit remains required before final Round-3 closure.
Volatility dependence is explicitly **NOT TESTED** in this round because no
new volatility variable was frozen; inventing one after seeing outcomes is forbidden.
