# ABT January 2025 Canonical XMA Rerun v1

Status: **IMPLEMENTED_AND_VERIFIED**

Date: 2026-09-29

## Purpose

Re-run the original ABT January 2025 discovery using the corrected Canonical
XMA slow-channel/state definitions, while holding the original January trading
logic, position path, execution convention, and transaction assumptions fixed.

This is an apples-to-apples formula-correction test. It is intentionally not
the later FEB_XMA_v1 full mechanical scan.

## Repository state

Branch:
`research/source-xma-walkforward`

Start HEAD:
`c5346c23bd58ac9e09dbad86dc099635b37e2987`

## Data

ABT OHLCV:
`Devesh176/Replicating_portfolio/data/ABT.csv`

Blob SHA:
`e9071f4a01e8f50cdab0155b0779ef09ef85e1d4`

Window:
2025-01-02 through 2025-01-31.

## Canonical corrections applied

1. Weighted slow high/low channel uses exactly lags 0..19 with weights 20..1
   and denominator 210.
2. The SSSS low-channel lag-11 H/L error is eliminated by the common
   canonical LOW implementation.
3. Research regime classification uses the mutually exclusive four-state
   partition:
   BULL / BEAR / RANGE / EXPANSION.

Unchanged:
- point-in-time first-observed double XMA(25) fast rails;
- DEA3_RAW / DEA33B_RAW momentum;
- RVOL20;
- next-tradable-open execution;
- fractional shares;
- zero commission;
- 5 bps one-way adverse slippage;
- original January sizing 30% -> 70% -> 100% -> 70% -> 0%.

## Key-state comparison

The five original actionable checkpoints retain the same actionable regime:

| Date | Legacy raw | Canonical | Decision implication |
|---|---|---|---|
| 2025-01-15 | RANGE | RANGE | probe remains valid |
| 2025-01-16 | RANGE | RANGE | confirmation remains valid |
| 2025-01-21 | RANGE | RANGE | breakout/add remains valid |
| 2025-01-28 | BULL | BULL | reduction remains valid |
| 2025-01-30 | BULL | BULL | exit remains valid |

Across the full January window, exactly one regime label changes:

- 2025-01-27: legacy RANGE -> canonical BULL.

This does not alter the original January action sequence; the position remains
fully long on that session and the next archived action is still the
2025-01-28 reduction.

Representative slow-rail changes:

- 2025-01-15:
  - legacy SlowLower 110.120874 -> canonical 109.598537
  - legacy SlowUpper 119.171692 -> canonical 118.605482
- 2025-01-21:
  - legacy SlowLower 110.076337 -> canonical 109.554317
  - legacy SlowUpper 119.116378 -> canonical 118.550641
- 2025-01-30:
  - legacy SlowLower 110.128383 -> canonical 109.606541
  - legacy SlowUpper 119.866087 -> canonical 119.300496

The slow structure moves, but not enough to invalidate the original actionable
states.

## Canonical rerun result

Original archived execution chain remains:

- 2025-01-15 signal -> 2025-01-16 open: 30% probe
- 2025-01-16 signal -> 2025-01-17 open: raise to 70%
- 2025-01-21 signal -> 2025-01-22 open: raise to 100%
- 2025-01-28 signal -> 2025-01-29 open: reduce to 70%
- 2025-01-30 signal -> 2025-01-31 open: exit to 0%

Result:

- Initial capital: $10,000.00
- Final capital: **$11,345.4916**
- January return: **+13.4549%**
- Close-to-close max drawdown: approximately **-1.58%**

Therefore:

`ABT_2025_01_CANONICAL_FORMULA_RERUN = PASS`

The canonical formula corrections do **not** explain away the original January
ABT result.

## Important scope note

A separate experiment that applies the later FEB_XMA_v1 mechanical rule set
from the beginning of January can generate additional early-January
probe/exit actions. That is a strategy-definition change, not merely a formula
correction, and is therefore not used for this apples-to-apples rerun.

This report isolates only the effect of correcting the XMA slow-channel and
state formulas.
