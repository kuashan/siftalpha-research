# Research Checkpoint — 2026-09-19 — E039 BTC 15m Probability Sizing

## Status
NO_PROBABILITY_ACTION_MODEL

## OOF design
48 resolved starter lifecycles.
First 15 training seed.
33 later lifecycles predicted chronologically out-of-fold.

Models:
- P_UP
- P_DD4H

Features:
existing causal SSSS state only.

## Portfolio result

63 fixed threshold combinations.

Eligible:
0.

Existing E037 benchmark over OOF evaluation:
+3.38%.

Best probability engine:
+2.85%.

Incremental:
-0.53pp.

Candidate max drawdown:
10.84%.

Benchmark max drawdown:
8.77%.

Probability sizing therefore did not improve the simpler reference.

## LOSS_ADD threshold

No threshold passed the minimum-evidence gate.

Most informative region:

-6%:
7 events,
+0.40% mean,
+1.14% median,
PF 1.34,
q25 -1.59%.

-7%:
4 events,
+1.87% mean,
+2.94% median,
PF 3.23,
but too sparse.

Research conclusion:
candidate band -6% to -7%.
Use -6% as provisional center only.

It remains disabled.

## Action taxonomy retained

- TREND_ADD
- LOSS_ADD
- PROFIT_RISK_REDUCE
- LOSS_RISK_REDUCE

None is activated.

Existing reference CLOSE remains unchanged.

## Next research implication

Do not add model complexity simply because probability outputs sound intuitive.

The next useful step is to improve state discrimination specifically at:
- profitable-but-risky states for partial reduction;
- -6% to -7% drawdown states for possible loss-add;

using a more local state/reset formulation or additional independently justified data, followed by fresh OOS validation.
