# SSSS Current State

Last updated: 2026-09-19  
Research version: v0.1.0

## Scope

This document is the current source of truth for the SSSS research model.

The strategy is event-driven. Fixed 5/10/20-day holding periods are used only for research diagnostics and are not live exits.

## Current causal implementation

Source XMA is replaced by DEMA for causal execution.

Fast band:
- DEMA(H,25)
- DEMA(L,25)
- FastUpper = 2*DH - DL
- FastLower = 2*DL - DH
- FastMid = (DH+DL)/2

Slow white band:
- Source weighted HIGH/LOW structures
- EMA(90)
- Preserve source anomalies:
  - lag 19 omitted; lag 20 receives weight 1
  - lower structure uses HIGH at lag 11

Effective color/state requires 3 consecutive raw-state bars.

## OPEN / validated

Qualified GRB:

```
EffectiveState = GREEN
AND H > FastUpper
AND REF(H,1) <= REF(FastUpper,1)
AND dsep > 0
AND C >= WhiteLower - 2*ATR14
```

Signal is known after close and executed at the next tradable open.

## CLOSE / validated research rules

Failure path:

```
Qualified BUY
-> no RED maturity
-> Effective Gray -> Effective Green
-> CLOSE next open
```

Mature path:

```
Qualified BUY
-> Effective RED
-> HOLD
-> Effective Red -> Effective Gray
-> CLOSE next open
```

## Position-management status

- OPEN: validated research rule
- ADD: research; no validated trigger yet
- REDUCE: RTE is the leading candidate, not yet production/frozen
- RE-ADD: research; no validated trigger yet
- FAILURE CLOSE: validated research rule
- MATURE CLOSE: validated research rule

## RTE candidate

```
EffectiveState = RED
AND H > FastUpper
AND C >= O
AND FastWidth > REF(FastWidth,5)
AND dsep < 0
```

Current interpretation: tactical risk / REDUCE candidate, not full CLOSE.

## Corrected baseline

Universe: 45 mainstream liquid equities.  
Available history: approximately 2024-09 to 2026-09.

- Independent Qualified BUY lifecycles: 96
- Resolved lifecycles: 88
- Mature: 69
- Fail: 19
- Completed BUY->SELL trades: 71
- Win rate: 59.2%
- Average net return per completed trade: +8.84%
- Median net return: +1.96%
- Mature-path win rate: 76.9%
- Mature-path average net return: +13.98%
- Failure-path win rate: 10.5%
- Failure-path average net return: -5.25%
- Average winner: +18.91%
- Average loser: -5.75%
- Payoff ratio: ~3.29
- Profit factor: ~4.76

These figures are research results from the currently available ~2-year window, not a claim of long-run live performance.

## Important risk finding

The return distribution is positively skewed and relies materially on large trends.

- Top 5 winners contributed about 58.1% of gross positive returns.
- Top 10 winners contributed about 74.7%.
- Tail losses worse than -10% occurred and remain a major research target.

## Current next objective

Build a complete position state machine:

```
FLAT
 -> OPEN
 -> HOLD
 -> ADD / REDUCE / RE-ADD
 -> CLOSE
 -> FLAT
```

Do not optimize position percentages until action triggers themselves have passed out-of-sample validation.


## Latest action-discovery round

No new production action was accepted.

### ADD

Rejected after discovery/OOS:
- Repeat Qualified GRB within the same effective Green episode
  - baseline: 37 events, 51.4% win, +7.31% average, +0.66% median
  - new OOS: 5 events, 20% win, -5.22% average, -2.44% median
- Effective Red then breakout above the pre-Red path high
  - 33 events, 39.4% win, +7.50% average, -2.63% median
  - positive mean was driven by a small number of large trend continuations

Conclusion: no validated ADD trigger exists yet.

### REDUCE

Rejected as general REDUCE:
- No-Progress Gray with MFE < 1 ATR and close <= entry
  - baseline median price advantage ~+1.11%, but average ~-2.54%
  - new OOS average ~-1.20%
- Profit Giveback + Raw Gray
  - baseline price advantage only ~+0.23%
  - new OOS average ~-0.68%

RTE after at least 2 ATR of prior favorable excursion remains a research candidate only:
- baseline: 8 events
- 62.5% occurred above the later final close price
- average price advantage ~+1.46%
- median price advantage ~+5.82%
- latest 10-stock OOS produced zero such events, so evidence remains too sparse

### RE-ADD

Rejected:
- RTE reduction followed by dsep > 0
- RTE reduction followed by a close above the RTE-day high while still Red

For the latter:
- 6 baseline events
- re-add leg win rate 33.3%
- average re-add leg -0.95%
- median re-add leg -3.05%
- average buyback price was about 1.4% above the earlier RTE reduction price

### Current action maturity

- OPEN: validated research rule
- ADD: no validated trigger
- HOLD: active
- REDUCE: RTE remains candidate only
- RE-ADD: no validated trigger
- FAILURE CLOSE: validated research rule
- MATURE CLOSE: validated research rule


## Tail-loss action update — 2026-09-19

No new mandatory position action was accepted.

Rejected as general REDUCE after OOS:
- No-Progress + FastMid
- no-progress loss thresholds at -1 / -1.5 / -2 entry ATR
- profit round-trip after prior +2 / +3 ATR MFE

No-Progress + WhiteLower remains only a warning / possible second-stage REDUCE candidate:
- classification toward tail losses was reasonably selective
- but independent action-price advantage was small, so it is not yet an accepted trade action

A full shift of a second exposure unit from OPEN to Effective Red was also rejected:
- OPEN unit average return: +8.84%
- delayed Red unit average return: +3.89%
- full unit shift reduced average return by about 4.95 percentage points

Interpretation:
- initial exposure must remain early enough to participate in large trends
- but future position sizing should still consider a starter-position architecture
- the next useful research target is an ADD event that confirms the trade without chasing

Current action maturity remains:
- OPEN: validated research rule
- ADD: no validated trigger
- HOLD: active
- REDUCE: RTE remains the leading candidate; WhiteLower no-progress is warning-only
- RE-ADD: no validated trigger
- FAILURE CLOSE: validated
- MATURE CLOSE: validated


## Official universe and sample-split source

The corrected baseline must be interpreted together with:

- `SSSS_UNIVERSE_45.md` — exact 45-stock baseline membership
- `SSSS_SAMPLE_SPLITS.md` — Discovery / OOS / Frozen OOS audit history
- `SSSS_SAMPLE_SPLITS.csv` — machine-readable split ledger
- `ssss_universe.py` — executable cohort configuration

Do not recompute or compare baseline statistics using a different universe without explicitly versioning the universe change.


## Mandatory research-round pre-registration

Every new SSSS research round must follow `SSSS_RESEARCH_PROTOCOL.md`.

Before any result is computed or inspected:

- assign a new experiment ID;
- write the exact Discovery, OOS, and Frozen OOS ticker lists;
- write the date ranges, overlap status, rule definition, execution convention, and evaluation criteria;
- update the sample-split audit;
- commit the pre-registration to `main`.

Only after that commit may Discovery begin.

OOS is not a second Discovery stage. Frozen OOS must remain untouched until the candidate rule has been frozen.

If a cohort or tested rule changes after results are viewed, the work must receive a new experiment ID and a new pre-registration commit.


## Active research round — E030

Status: PRE-REGISTERED.

Research target:
Progress -> Controlled Pullback -> Re-acceleration ADD.

The exact E030 Discovery / OOS / Frozen OOS split, six-variant Discovery family, date window, execution convention, and pass/fail criteria are frozen in:

- `preregistrations/E030.md`
- `SSSS_SAMPLE_SPLITS.md`
- `SSSS_SAMPLE_SPLITS.csv`

No E030 result may be interpreted unless the sequence in `SSSS_RESEARCH_PROTOCOL.md` is followed.

Current phase: Discovery may begin only after the pre-registration commits are confirmed on `main`.


## E030 result — completed at Discovery

E030 Progress -> Controlled Pullback -> Re-acceleration ADD failed its pre-registered Discovery gate.

Results:
- FastUpper-reset variants U075 / U100 / U150: 3 signals each, 0 resolved ADD legs, 3 stocks
- FastMid-test variants M075 / M100 / M150: 0 signals

Required minimum:
- 12 resolved ADD legs
- 6 Discovery stocks

Therefore:
- E030 = REJECT_DISCOVERY
- E030 OOS was not opened
- E030 Frozen OOS was not opened
- no ADD rule was added to the model

Current action maturity remains:
- OPEN: validated
- ADD: no validated trigger
- HOLD: active
- REDUCE: RTE candidate only; WhiteLower no-progress warning-only
- RE-ADD: no validated trigger
- FAILURE CLOSE: validated
- MATURE CLOSE: validated

Research implication:
The next ADD round should keep the idea of "prove direction without chasing" but remove at least one structural bottleneck rather than merely loosening E030 thresholds after seeing the result. A new formulation requires a new experiment ID and a new pre-registration.


## Active research round — E031

Status: PRE-REGISTERED.

Research target:
Structural Confirmation ADD.

Core variable:
StructuralSep = (FastMid - WhiteMid) / WhiteWidth.

The E031 sample split, six fixed variants, requested data window, execution convention, and pass/fail gates are frozen in:

- `preregistrations/E031.md`
- `SSSS_SAMPLE_SPLITS.md`
- `SSSS_SAMPLE_SPLITS.csv`

E031 is materially different from E030 because it removes the required prior-profit / pullback / re-acceleration sequence and tests model-band structural separation directly.

Current phase:
Discovery may begin only after the pre-registration commits are confirmed on `main`.


## E031 execution checkpoint — Discovery partial

E031 remains IN_PROGRESS.

Data retrieval completed successfully for 10 of 30 Discovery tickers before the market-data provider returned an explicit RATE_LIMIT response:

- AAPL
- MSFT
- NVDA
- JPM
- XOM
- FDX
- NEE
- ORCL
- WMT
- GS

For the successfully retrieved tickers, the provider returned 501 daily bars from 2024-09-18 through 2026-09-17.

The apparent zero-row responses previously observed for ADBE / WFC / MRK / TMO / RTX / AVGO were diagnosed as provider rate-limit failures, not true missing-market-data observations.

No E031 Discovery conclusion is allowed from the partial 10-stock subset.

Still unopened:
- E031 OOS: QCOM, NKE, SCHW, GILD, CSX, META, AMD, CRM, TXN, AMZN
- E031 Frozen OOS: LOW, BA, PGR, ADP, MDLZ

Rules, thresholds, cohorts, and evaluation gates remain exactly as pre-registered in `preregistrations/E031.md`.

Do not alter or replace any ticker because of the provider rate limit.
