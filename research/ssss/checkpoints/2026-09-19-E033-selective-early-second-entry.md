# Research Checkpoint — 2026-09-19 — E033 Selective Early Second Entry

## Status

REJECT_DISCOVERY

## Coverage

- Discovery: 30 / 30 stocks
- 52 total trades
- 40 resolved
- 31 Mature
- 9 Failure
- Massive only
- first accessible bar: 2024-09-18
- normal 150-bar warm-up retained
- earliest E033 entry: 2025-04-28

## Benchmarks

BASE_1U:
- win 62.5%
- average +8.38%
- median +2.22%
- PF 6.41

NEXTDAY_2ND:
- win 62.5%
- average +8.45%
- median +2.57%
- PF 7.19

## Candidates

| Rule | Resolved adds | Stocks | Avg | Median | PF | Mature trigger | Failure trigger | Failure avoided | Median entry dist | Median timing | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| C04 | 28 | 19 | +5.62% | +1.44% | 4.97 | 71.0% | 66.7% | 33.3% | +0.37 ATR | 2 bars | Reject |
| D10 | 29 | 20 | +6.34% | +1.98% | 5.93 | 67.7% | 88.9% | 11.1% | -0.38 ATR | 1 bar | Reject |
| S10 | 17 | 14 | +5.03% | +2.78% | 5.95 | 38.7% | 55.6% | 44.4% | -1.43 ATR | 6 bars | Reject |
| R10 | 20 | 16 | +5.48% | +1.31% | 7.00 | 48.4% | 55.6% | 44.4% | +0.42 ATR | 3 bars | Reject |

R10 also failed winner-concentration control:
top 3 winners = 81.5% of gross positive ADD return.

## Main conclusion

Early second-unit economics are real, but the tested early signals do not reliably distinguish Mature from Failure paths.

Therefore the E032 opportunity map should not be interpreted as evidence for a selective technical ADD trigger.

The next research frontier is position sizing:
compare one-unit, two-unit-at-open, and mechanically split early-entry policies under explicit capital and risk normalization.
