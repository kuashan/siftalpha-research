# Stock Risk Exit Study v1 Correction Note v1a

Date: 2026-10-01

Status: **CORRECTION_REQUIRED**

The first aggregate closure attempt at commit `688bfbc5433b4abbd490718e4531e082f615eec4` is NOT the valid final result.

Audit found that the initial risk-exit simulator incorrectly handled an open position at the final sample date:

- incorrect implementation: force-sold the remaining position at the final close, charged an extra 5 bps sell slippage, and counted it as a completed trade;
- frozen protocol / previous refinement semantics: mark the open position to market at the final close, do not charge a synthetic exit slippage, and do not count it as a completed trade.

This produced small but non-zero baseline mismatches on stocks that remained open at sample end, including a maximum one-trade difference and non-floating-point differences in return / P5 / CVaR / win rate.

Therefore:
- all first-pass aggregated stock risk-exit conclusions are invalidated;
- the underlying protocol remains valid;
- the simulator must be corrected;
- all 39 stocks x 49 configurations must be recomputed;
- only a baseline reproduction PASS against the prior frozen AB_HALF control may authorize final interpretation.

`FIRST_PASS_STOCK_RISK_EXIT_CLOSURE = INVALIDATED_BY_AUDIT`
