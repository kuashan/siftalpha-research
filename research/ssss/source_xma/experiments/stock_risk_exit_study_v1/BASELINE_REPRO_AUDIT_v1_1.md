# Stock Risk Exit Baseline Reproduction Audit v1.1

Status: **PASS**

Date: 2026-10-01

The corrected simulator was compared against the previously frozen 39-stock `AB_HALF` baseline from `STOCK_SELL_POLICIES_v1.csv`.

Corrected sample-end semantics:
- an open position at the final sample date is marked to market at the final close;
- no synthetic final sell is created;
- no extra 5 bps exit slippage is charged;
- the open position is not counted as a completed trade.

Maximum absolute differences across all 39 stocks:
- return: 1.7763568394002505e-14
- mdd: 4.440892098500626e-16
- p5: 1.942890293094024e-16
- cvar10: 8.326672684688674e-17
- worst: 2.220446049250313e-16
- win: 0
- trades: 0
- exposure: 0

All completed-trade counts, win rates, and exposure values match exactly. Numeric differences are floating-point tolerance only.

`BASELINE_REPRODUCTION_V1_1 = PASS`
