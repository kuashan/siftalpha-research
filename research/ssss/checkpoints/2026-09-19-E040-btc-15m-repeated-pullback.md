# Research Checkpoint — 2026-09-19 — E040 BTC 15m Repeated Pullback

## Status
NO_REPEATED_PULLBACK_LADDER

## Main result

Best robust local pullback step:
1%.

Best structural validity floor:
FastLower.

Full 1% ladder:
- +24.47% portfolio return
- +22.84% stress-friction return
- versus E037 benchmark +19.03% / +17.77%
- but max drawdown 12.04% vs benchmark 9.82%

Therefore the full ladder failed the drawdown gate.

## Repeated ADD

1% / FastLower:
- 150 total ADD events
- +2.24% mean incremental unit return
- +0.38% median
- PF 3.03

Second ADD:
- 26 events
- +1.93% mean
- +0.53% median

Repeated ADD economics passed.

## Loss-state ADD

97 events:
- mean +2.91%
- median +1.22%
- PF 3.44
- stress median +1.16%

Strongest repeatable action family.

## Profit-state ADD

53 events:
- mean +1.01%
- median -0.46%
- stress median -0.52%

Do not reuse the loss-add rule for profitable pullbacks.

## REDUCE

No candidate.

At 1% / FastLower:
- median edge +0.54%
- mean edge -0.43%
- Failure mean +1.52%
- Mature mean -0.91%

Large Mature continuations remain the problem.

## Threshold map

1%:
robust repeated loss-add signal.

2%:
enough events, but second-add median negative.

3%:
too sparse.

4%:
nearly no valid adds.

5%-10%:
no FastLower-valid ladder actions.

## Discovery-only candidate

Provisional inactive candidate:

LOSS_PULLBACK_ADD:
- D = 1%
- local-reset anchor
- current position losing
- close >= FastLower
- EffectiveState GREEN or RED
- dsep > 0
- +10pp
- max exposure 50%

Requires new preregistered OOS validation.
