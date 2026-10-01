# SSSS Conditional Rail Rule Research v1

Status: FROZEN_BEFORE_LARGE_SAMPLE_RUN / DISCOVERY_AND_ROBUSTNESS
Date: 2026-10-01

## Objective

Convert user-observed SSSS geometry into conditional, data-supported rules without
forcing the strategy into the FIVEGZ three-buy/three-sell template.

The research object is the original Source-XMA geometry:
- BD: lower outer rail
- ZD1: fast lower rail
- GZB18=(ZK1+ZD1)/2: analytical fast midpoint
- ZK1: fast upper rail
- BS: upper outer rail
- fast state/color: UP / DOWN / RANGE, with EXPANSION stored separately
- light-gray slow band: GZB3..GZB4

No production rule exists at protocol freeze.

## Non-negotiable XMA chronology

For every symbol and every bar t:
1. expose only data <= t;
2. recompute right-edge double XMA25 and double XMA60;
3. save first-observed rails/state at t;
4. classify events at t;
5. only then advance to t+1;
6. never overwrite stored historical rails/events with later XMA repaint.

The implementation must pass the archived ABT 2025-01-15 calibration:
- ZD1 = 110.99182102887214
- GZB18 = 113.48360999503367
- ZK1 = 115.9753989611952

Any engine that fails this gate is rejected.

## Universe

Frozen 39 equities:
AAPL, MSFT, NVDA, AMD, AVGO, ORCL, INTC, QCOM, MU,
GOOGL, META, NFLX,
AMZN, TSLA, HD, MCD,
WMT, COST, PG, KO, PEP,
ABT, LLY, UNH, JNJ, TMO,
JPM, BAC, GS, V, MA,
CAT, BA, GE,
XOM, CVX,
LIN, NEE, PLD.

Crypto robustness:
BTC, ETH, BNB, SOL.

Daily timeframe first.
No minute-timeframe conclusion is inferred from daily results.

## Historical evidence classification

2020-2025 data have already been used in earlier Source-XMA research in other
forms. Therefore none of this historical work is called true OOS.

Use three frozen comparison blocks to reduce result-chasing:
- Block A: 2020-2022
- Block B: 2023-2024
- Block C: 2025

These are temporal robustness blocks, not OOS.

True prospective OOS begins only after a candidate rule set is frozen and new
unseen data arrive.

## Event families

### L1 Fast-lower excursion
Episode onset:
low < ZD1 after prior bar was not in a lower excursion.

By state:
UP / DOWN / RANGE / EXPANSION.

Measure:
- 3/5/10/20/40-bar close return
- MFE / MAE
- midpoint reached
- upper rail reached
- lower outer rail reached
- event-low broken
- time to midpoint / upper
- path order

Compare candidate actions:
- immediate entry
- watch only
- entry only after midpoint reclaim
- entry only after state transition
- entry after lower-outer confluence

Do not pre-select a winner.

### U1 Fast-upper excursion
Episode onset:
high > ZK1 after prior bar was not in an upper excursion.

Measure:
- 3/5/10/20/40-bar return, MFE, MAE
- midpoint reached
- lower rail reached
- upper outer reached
- new high
- time to midpoint/lower

Compare candidate actions:
- immediate reduce
- watch only
- reduce after midpoint loss
- exit after midpoint loss plus adverse state transition
- upper-fast + upper-outer confluence

### M1 Midpoint behavior
Study midpoint as a state transition / confirmation rail, not assume support.

Lower-origin sequence:
lower event -> midpoint reclaim -> upper / failure.

Upper-origin sequence:
upper event -> midpoint touch/loss -> lower / rebound.

Measure:
- probability
- elapsed bars
- MFE/MAE after confirmation
- failure rates by state

### O1 Outer rails
Study BD and BS both alone and conditional on proximity/confluence with fast rails.

Distance normalized by ATR14:
- <=0.25 ATR
- 0.25-0.50
- 0.50-1.00
- >1.00

No outer rail is pre-labelled support/resistance.

### G1 Light-gray band
Study GZB3..GZB4 by:
- approach from above / below
- fast state
- touch / enter / full cross
- band slope: rising / flat / falling
- subsequent fast-state transition
- distance to fast midpoint and fast rails

Do not model gray band as simple support/resistance unless data support it.

### S1 State transitions
Track:
UP -> RANGE
RANGE -> DOWN
DOWN -> RANGE
RANGE -> UP
UP -> DOWN / DOWN -> UP if direct
EXPANSION transitions

Measure how transition changes the meaning of L1/U1/M1/O1/G1.

## Rule promotion gates

A condition can become a candidate quantitative rule only if:

1. sample size is adequate;
2. effect direction is consistent across at least two temporal blocks;
3. not dominated by one or two symbols/sectors;
4. median agrees reasonably with mean;
5. MFE/MAE is compatible with the intended action;
6. result survives leave-one-symbol-out or contribution concentration audit;
7. the rule is materially better than the simpler unconditional event;
8. no threshold was chosen after viewing the same outcome without a new freeze.

Candidate action vocabulary:
- WATCH
- PROBE_ENTRY
- CONFIRM_ENTRY
- ADD
- HOLD
- REDUCE
- EXIT
- INVALIDATE

Signal count is not fixed. SSSS does not need three buys / three sells.

## Research rounds

Round 1 — Event map
Find which state/rail combinations have repeatable directional behavior.

Round 2 — Conditional paths
Add midpoint, outer confluence, gray-band structure, and state transitions.

Round 3 — Stability/falsification
Year block, sector, symbol concentration, volatility, MFE/MAE, bootstrap and
leave-one-out diagnostics.

Round 4 — Candidate strategy freeze
Only after the above, define explicit position actions and invalidation.

Round 5 — Prospective OOS
No further tuning after candidate freeze; evaluate on newly arriving untouched data.

## First hypotheses carried from ABT only

These are hypotheses, not rules:
- DOWN + fast lower may be a probe-long candidate.
- midpoint reclaim may improve a lower-origin entry.
- UP/red + fast upper may be a reduce/watch candidate.
- midpoint loss may be more informative than upper touch alone for exit.
- lower outer may strengthen lower-side setups.
- upper outer alone may not be resistance.
- RANGE + gray-band approach from above may be support-like.

All seven must be falsified on the larger universe.
