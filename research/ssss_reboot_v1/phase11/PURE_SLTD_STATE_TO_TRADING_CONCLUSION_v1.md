# Pure SLTD State-to-Trading Research — Phase11 Conclusion v1

Status: **CLOSED_FOR_CURRENT_TWO_RULE_MAP**

## Scope

This phase tested the user's requested direction:

SLTD visual/state information -> quantified forward probability -> trading mapping.

Chan/缠论 was excluded from SLTD throughout.

## Stage 1 — State probability

Result: **IMPLEMENTED_AND_VERIFIED**

- Discovery keys: 359
- Discovery gate pass: 46
- Same-79 temporal survivors: 22
- Fresh OOS10 confirmed: 20
- Positive confirmed states: 12
- Negative confirmed states: 8

The strongest positive event-specific state was:
- GREEN age>=21 + LOWER + CLOSE_BELOW

The strongest negative event-specific state was:
- BLUE age>=21 + UPPER + WICK_ONLY

Conclusion:
**Pure SLTD state variables do contain measurable forward-return information.**

## Stage 2 — Minimal probability-map R2

Candidate:
- add PM_BUY_1 = GREEN21+ lower close-below -> BUY
- add PM_SELL_1 = BLUE21+ upper wick-only -> SELL
- retain all current V7 position/C2 rules

Fresh20 R2:
- V7 return: +42.95%
- PMAP return: +50.03%
- V7 Calmar: 0.261
- PMAP Calmar: 0.291
- return better: 13/20
- Calmar better: 13/20

However the pre-registered absolute post-SELL sanity gate failed.
R2 status:
**RESEARCH_ONLY_NOT_PROMOTED**

Post-hoc ablation, explicitly non-OOS:
- BUY_ONLY return +53.87%, Calmar 0.298
- SELL_ONLY return +40.51%, Calmar 0.269
- BOTH return +50.03%, Calmar 0.291
- V7 return +42.95%, Calmar 0.261

This diagnostic cannot promote a rule, but it showed that BUY contributed most of the
R2 return improvement while SELL mainly reduced drawdown.

## Stage 3 — Second untouched Fresh20 R3

The candidate rules were kept unchanged.
The event gate was prospectively corrected to the same symbol-drift-adjusted excess
definition used by the original probability study.

R3 5 bps:
- V7 return: +70.89%
- PMAP return: +68.06%
- V7 MaxDD: -18.82%
- PMAP MaxDD: -17.49%
- V7 Calmar: 0.439
- PMAP Calmar: 0.457
- PMAP return better: 12/20
- PMAP Calmar better: 15/20

R3 10 bps:
- V7 return: +70.32%
- PMAP return: +67.00%
- V7 Calmar: 0.436
- PMAP Calmar: 0.451

PM_BUY_1 R3:
- 86 events / 20 stocks
- 10d median excess: +1.20%; positive breadth 70%
- 20d median excess: +0.36%; positive breadth 55%
- interpretation: positive tendency persists, but the 20d breadth gate did not pass.

PM_SELL_1 R3:
- 276 events / 20 stocks
- 10d median excess: +0.37%; negative breadth 30%
- 20d median excess: -1.11%; negative breadth 60%
- interpretation: the sell effect is horizon-dependent and not stable enough as a universal immediate SELL trigger.

R3 status:
**REJECTED_NOT_ADMITTED**

## Final decision

1. Do **not** add PM_BUY_1 or PM_SELL_1 to the production SLTD rule set.
2. Keep current pure SLTD V7 unchanged.
3. Do **not** restore Chan into SLTD.
4. Preserve the probability research as evidence that the visual/state layer contains information.
5. Reject the current direct two-rule mapping from that information into trades.

The key distinction is now data-supported:

- SLTD state information has predictive content.
- The tested direct mapping of the strongest positive/negative state into two extra
  BUY/SELL rules is not stable enough to replace or extend V7.

Any future SLTD redesign should not continue by adding isolated manual rules one by one.
If resumed, it should be a separately pre-registered **state-score / exposure-map** study
that maps the state probability layer to target exposure, not another ad-hoc rule patch.

Current production status:
**PURE_SLTD_V7_UNCHANGED**

Current candidate status:
**PURE_SLTD_TWO_RULE_PROBABILITY_MAP = REJECTED_NOT_ADMITTED**

Phase status:
**PURE_SLTD_STATE_TO_TRADING_PHASE11 = CLOSED**
