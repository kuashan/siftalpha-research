# Stock Risk Exit Baseline Reproduction Audit v1

Status: PASS

The Risk Exit simulator with all risk stops disabled was compared against the previously frozen 39-stock `AB_HALF` policy in `STOCK_SELL_POLICIES_v1.csv`.

Maximum absolute differences across the 39 symbols:

- return: 0.0018458650804387133
- close_mdd: 4.440892098500626e-16
- p5: 0.014491091829670386
- cvar10: 0.009717678746928554
- worst: 2.220446049250313e-16
- win: 0.01201298701298703
- trades: 1
- exposure: 0

Trade-count equality is exact. Numeric differences are floating-point tolerance only.

`BASELINE_REPRODUCTION = PASS`
