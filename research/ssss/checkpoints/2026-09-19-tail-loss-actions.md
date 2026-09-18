# Research Checkpoint — 2026-09-19 — Tail-Loss Position Actions

## Baseline unchanged

- 71 completed trades
- win rate 59.2%
- average net return +8.84%
- median +1.96%
- 10 losses worse than -5%
- 5 losses worse than -10%

## Tail-loss REDUCE research

Rejected as mandatory actions:
- No-Progress + FastMid (failed second frozen OOS)
- no-progress loss thresholds at -1 / -1.5 / -2 entry ATR
- profit round-trip after prior +2 / +3 ATR MFE

Warning-only:
- No-Progress + WhiteLower
  - selective toward tail losses
  - but OOS economic advantage was small

## Staged-entry research

Delaying one full notional unit until Effective Red:
- normal OPEN unit average +8.84%
- delayed Red unit average +3.89%
- full shift costs about 4.95 percentage points of average return

Conclusion:
- do not replace early OPEN exposure with a fully delayed Red entry
- future work should search for an ADD point that proves direction without chasing

## State machine

- OPEN = validated
- ADD = none validated
- REDUCE = RTE candidate only; WhiteLower no-progress warning-only
- RE-ADD = none validated
- CLOSE failure = validated
- CLOSE mature = validated

## Next research

Find the intermediate ADD zone between:
- Qualified GRB (early but uncertain)
- Effective Red (safer but too late)

Candidate structure should combine:
- trade has proven direction
- structure remains healthy
- price has not become overextended
