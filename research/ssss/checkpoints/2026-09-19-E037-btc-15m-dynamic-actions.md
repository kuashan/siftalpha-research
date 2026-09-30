# Research Checkpoint — 2026-09-19 — E037 BTC 15m Dynamic Actions

## Status
DYNAMIC_ACTION_ZONES_FOUND

## Starter reference

GREEN_TRANSITION / B2:

- 48 resolved one-at-a-time lifecycles
- 33 Mature / 15 Failure
- base mean +0.95%
- base median +0.21%
- base PF 1.97

## Direct ADD events

| Event | N | Base mean | Base median | PF | Decision |
|---|---:|---:|---:|---:|---|
| GRB | 35 | +0.74% | -0.36% | 1.63 | Fail |
| FAST_BREAKOUT | 47 | +0.56% | -0.18% | 1.50 | Fail |
| FASTMID_RECLAIM | 47 | +0.68% | -0.08% | 1.64 | Fail |

## ADD map

10 cells passed.

Best:
M_LT_1 | P_LE_0

- 32 events
- base mean +1.49%
- base median +0.64%
- stress median +0.58%
- PF 2.44
- q25 -0.77%
- median timing 1 bar

Early PRE_RED B00_07 also passed:
- 48 events
- base mean +0.89%
- base median +0.20%
- PF 1.88

## REDUCE
No passing zone.

## RE-ADD
No passing recovery.

## CLOSE
No passing zone.

GREEN->GRAY early close was a notable false temptation:
- median edge +0.38%
- mean edge -0.62%
- Mature median MFE sacrifice ratio 0.81

Therefore no earlier full-close replacement is accepted.

## Interpretation

The emerging 15m BTC engine is not:
late-confirmation OPEN -> late-confirmation ADD.

The strongest Discovery architecture is:

GREEN_TRANSITION starter
-> possible very-early ADD while still unextended
-> hold through large trend development
-> no validated tactical reduction / re-add yet
-> retain reference state-based close until better risk actions survive independent validation.

No production action is validated in E037.
