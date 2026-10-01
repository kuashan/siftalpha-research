# SSSS Conditional Rail Rules v1 — Round 3 Final Result

Status: **ROUND 3 COMPLETE**
Date: 2026-10-01

All candidates were matched 100% back to the strict first-observed XMA event ledger.
No finalized/repainted XMA value was used.

## MFE / MAE completion

| ID | n | 20-bar favorable mean | 20-bar adverse mean | Fav/Adv ratio | Round-3 status |
|---|---:|---:|---:|---:|---|
| B1 | 629 | 9.62% | 6.72% | 1.43 | ROBUST_CANDIDATE |
| B2 | 25 | 14.69% | 1.05% | 13.94 | CONDITIONAL_CANDIDATE_SMALL_SAMPLE |
| B3 | 145 | 7.85% | 4.89% | 1.60 | CONDITIONAL_CANDIDATE |
| S1 | 39 | 13.28% | 1.48% | 8.95 | ROBUST_CANDIDATE_MODERATE_SAMPLE |
| S2 | 27 | 14.42% | 1.11% | 13.03 | CONDITIONAL_CANDIDATE_STRONG_EFFECT_SMALL_SAMPLE |
| C1 | 367 | 7.87% | 4.76% | 1.65 | OBSERVE_ONLY |

## Key excursion findings

- B1 DOWN + LOWER_FAST: mean MFE20 9.62%, mean MAE20 -6.72%. Favorable/adverse ratio 1.43. Broadly positive but drawdown tail remains material.
- B2 RANGE->UP after lower event: mean favorable excursion 14.69%, mean adverse excursion 1.05%, ratio 13.94. Exceptionally clean but only 25 events.
- B3 upward gray-band full cross in RANGE: favorable 7.85% vs adverse 4.89%, ratio 1.60.
- S1 UP->RANGE after upper event: bearish favorable excursion 13.28% vs adverse 1.48%, ratio 8.95.
- S2 RANGE->DOWN after upper event: bearish favorable excursion 14.42% vs adverse 1.11%, ratio 13.03. Strongest bearish excursion profile, but only 27 events.
- C1 remains OBSERVE_ONLY.

## Final Round-3 classification

B1 = ROBUST_CANDIDATE  
B2 = CONDITIONAL_CANDIDATE_SMALL_SAMPLE  
B3 = CONDITIONAL_CANDIDATE  
S1 = ROBUST_CANDIDATE_MODERATE_SAMPLE  
S2 = CONDITIONAL_CANDIDATE_STRONG_EFFECT_SMALL_SAMPLE  
C1 = OBSERVE_ONLY

## Important actionability gate

B2, S1 and S2 are transition-conditioned signals. Their current Round-2/Round-3
returns and MFE/MAE are anchored to the original rail-event date. The state
transition is only known later. Therefore these effects are valid research
associations, but they must NOT yet be treated as executable trade returns.

Before candidate strategy freeze, run a separate actionability audit from the
actual transition-detection bar. This is not a Round-3 incompleteness; it is the
next gate required before production-rule promotion.

Volatility dependence remains NOT TESTED because Round 3 explicitly forbade
inventing a new volatility variable after seeing outcomes.
