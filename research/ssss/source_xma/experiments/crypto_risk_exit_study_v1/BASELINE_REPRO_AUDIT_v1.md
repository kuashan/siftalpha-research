# Crypto Risk Exit baseline reproducibility audit v1

Status: **PASS**

Date: 2026-10-01

The new risk-exit simulator was run with both risk mechanisms disabled and compared to the prior frozen 60% + W3 BUY-C top-up / FULL_FIRST Crypto baseline.

Results:

- BTC cumulative return delta: +2.22e-16; MDD delta: +2.22e-16; trades 71 vs 71
- ETH cumulative return delta: +4.44e-16; MDD delta: 0; trades 72 vs 72
- BNB cumulative return delta: -3.77e-15; MDD delta: 0; trades 65 vs 65
- SOL cumulative return delta: 0; MDD delta: -1.11e-16; trades 45 vs 45

All differences are floating-point noise only.

`RISK_EXIT_BASELINE_REPRODUCIBILITY = PASS`

Therefore the Risk Exit Study is an additive layer over the previously frozen baseline rather than a changed replay implementation.
