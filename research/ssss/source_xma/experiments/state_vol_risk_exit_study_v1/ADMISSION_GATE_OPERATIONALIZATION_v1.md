# State / Volatility-Aware Risk Exit v1 Admission Gate Operationalization

Date: 2026-10-01

Status: **PRE-INTERPRETATION CLARIFICATION**

This note does not add or modify any candidate, ATR multiple, state threshold, universe, execution rule, or metric. It makes two qualitative gates from `STATE_VOL_RISK_PROTOCOL_v1.md` mechanically testable before aggregate interpretation.

## 1. Right-tail protection gate

The protocol requires:
- no materially larger killed-winner count than saved-loser count;
- no material systematic BUY-C-confirmed penalty.

For v1 these are operationalized as:

- `killed_winners <= saved_losers`
- and, if `confirmed_matched_stops > 0`, then `confirmed_mean_delta >= 0`.

If there are zero BUY-C-confirmed matched risk exits, the confirmed-subset condition is treated as not violated rather than inferred positive.

No tolerance or effect-size threshold is fitted from results.

## 2. Crypto single-coin dominance gate

The protocol requires that a Crypto candidate cannot be promoted solely because one coin dominates the pooled result.

For each formal candidate:

1. compute each coin's cumulative-return delta vs its own baseline;
2. identify the coin with the largest positive return delta (or the largest return delta if all are non-positive);
3. remove that single coin;
4. on the remaining three coins require:
   - candidate mean cumulative return >= 90% of their positive baseline mean cumulative return;
   - mean intraday-low MDD improvement > 0;
   - mean P5 delta >= 0;
   - mean CVaR10 delta >= 0.

Failure of any leave-one-out condition means the pooled Crypto result is classified as potentially single-coin-driven and fails admission.

## 3. Other gates unchanged

All other gates remain exactly as preregistered:
- Stock MDD bootstrap 95% lower bound > 0;
- Stock MDD improvement on at least 24/39 stocks;
- Crypto MDD improvement on at least 3/4 coins;
- >=90% aggregate mean-return preservation;
- aggregate P5 and CVaR10 no worse than baseline;
- formal candidates only; ATR2_ONLY / ATR3_ONLY remain controls;
- passing means only `PROMOTED_TO_NEXT_VALIDATION`.

No post-result repair is allowed.
