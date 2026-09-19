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


## E031 result — completed at Discovery

E031 Structural Confirmation ADD completed all 30 pre-registered Discovery stocks.

All six variants were rejected at Discovery.

Key result:
- S050B: 43 signals, 34 resolved, 25 stocks, average +4.21%, median -2.90%, profit factor 2.24, median execution distance 2.50 EntryATR.
- S100B: 29 resolved, average +4.22%, median -2.97%.
- S150B: 13 resolved, average +11.05%, median -3.13%.
- S050X: 19 resolved, average +3.96%, median -3.47%.
- S100X: 15 resolved, average +10.07%, median -2.70%.
- S150X: 9 resolved, average +12.88%, median -3.13%.

Every variant failed the required positive-median condition.

Therefore:
- E031 = REJECT_DISCOVERY
- OOS was not opened
- Frozen OOS was not opened
- no ADD rule was added

Interpretation:
normalized band separation captures some large trends but does not solve incremental entry timing. Higher thresholds become later and more winner-concentrated.

Current action maturity remains:
- OPEN: validated
- ADD: no validated trigger
- HOLD: active
- REDUCE: RTE candidate only; WhiteLower no-progress warning-only
- RE-ADD: no validated trigger
- FAILURE CLOSE: validated
- MATURE CLOSE: validated


## Data-source resilience

SSSS now follows `SSSS_DATA_SOURCE_POLICY.md`.

Massive remains the current primary research source.

A yfinance fallback downloader is retained for research recovery and provider-parity testing.

Provider switching is allowed without changing the experiment ID only when:
- cohorts stay fixed;
- date range stays fixed;
- strategy formula stays fixed;
- execution and evaluation rules stay fixed;
- the replacement provider is documented before its result is interpreted.

Do not silently mix providers ticker-by-ticker inside an official research stage.


## Active research round — E032

Status: PRE-REGISTERED.

Research target:
ADD Opportunity Map.

E032 does not start from a proposed trigger.

It maps the hypothetical marginal return of adding one unit at every causally available in-trade decision bar and holding that unit to the already validated official final CLOSE.

Formal maps are frozen to:
1. lifecycle phase x bars since entry
2. current progress x giveback
3. running MFE x current progress
4. StructuralSep x fast-band price location
5. effective state x dsep sign

Primary cell statistics use first-entry-per-trade counting to prevent long trades from dominating through repeated daily observations.

E032 is Discovery-only:
- OOS must remain unopened;
- Frozen OOS must remain unopened;
- any discovered zone requires a new Experiment ID before rule validation.

See:
- `preregistrations/E032.md`
- `SSSS_SAMPLE_SPLITS.md`
- `SSSS_SAMPLE_SPLITS.csv`


## E032 result — ADD Opportunity Map

Status: CANDIDATE_ZONES_FOUND.

Discovery completed:
- 30 / 30 stocks
- 40 resolved trades
- 3332 all-bar hypothetical ADD observations
- 15 formal map cells passed the pre-registered candidate-zone gate

The strongest zones concentrate early in the lifecycle:
- before Effective Red
- near the original entry price
- before large price extension

The strongest formal cell was:
StructuralSep < 0 and close < FastMid
with 30 first-entry trade events across 22 stocks, +4.65% average hypothetical ADD return and +2.97% median.

Other top zones include:
- PRE_RED in the first 0-4 bars
- Effective Green with dsep > 0
- running MFE < 1 EntryATR while current progress <= 0

Important interpretation:
these zones are not validated ADD triggers.
Several are so close to the original OPEN that they may simply imply that earlier exposure is economically superior to delayed confirmation.

E032 did not open OOS.
E032 did not open Frozen OOS.
No production/research ADD action was added.

Current action maturity remains:
- OPEN: validated
- ADD: no validated trigger
- HOLD: active
- REDUCE: RTE candidate only; WhiteLower no-progress warning-only
- RE-ADD: no validated trigger
- FAILURE CLOSE: validated
- MATURE CLOSE: validated

Next research frontier:
separate "increase starter exposure" from a genuinely selective early second-entry rule.


## Active research round — E033

Status: PRE-REGISTERED.

Research target:
Selective Early Second Entry.

Motivation:
E032 showed that marginal ADD economics cluster early and near the original entry. E033 now tests whether genuinely new early post-entry information can select which trades deserve a second unit.

Fixed candidates:
- C04: early continuation
- D10: early discount / unproven trend
- S10: structural discount
- R10: early entry reclaim

Benchmarks:
- BASE_1U
- IMMEDIATE_2U
- NEXTDAY_2ND

E033 must distinguish a real selective second-entry rule from simply increasing starter size.

OOS and Frozen OOS remain unopened until the protocol gates permit them.


## E033 data coverage note — pre-result

Before any E033 outcome was computed, Massive entitlement was checked.

Bars before 2024-09-18 are not included in the current plan.

E033 therefore uses the accessible Massive history beginning 2024-09-18 and retains the model's 150-bar warm-up requirement.

No E033 rule, cohort, or pass/fail threshold changed.


## E033 result — Selective Early Second Entry

Status: REJECT_DISCOVERY.

Discovery:
- 30 / 30 stocks
- 52 total trades
- 40 resolved
- 31 Mature
- 9 Failure

All four pre-registered candidates produced positive average and median ADD-leg economics, but none met the required path-selectivity gate.

Key examples:
- C04: +5.62% average / +1.44% median, but Mature trigger 71.0% vs Failure 66.7%
- D10: +6.34% / +1.98%, but Failure trigger 88.9% exceeded Mature 67.7%
- S10: +5.03% / +2.78%, but Failure trigger 55.6% exceeded Mature 38.7%
- R10: +5.48% / +1.31%, but Failure trigger 55.6% exceeded Mature 48.4% and top-3 winners contributed 81.5%

Therefore:
- E033 = REJECT_DISCOVERY
- OOS not opened
- Frozen OOS not opened
- no ADD trigger added

Important research implication:
early second-unit economics are positive, but the tested early information does not reliably select which trades deserve the extra unit.

This shifts the research frontier from ADD-signal discovery toward position sizing and mechanical split-entry policy comparison.


## Open-source quant research pivot

The research frontier has broadened beyond iterative SSSS-only indicator tweaks.

A source survey now prioritizes orthogonal feature families:
1. volume / flow
2. trend efficiency / choppiness
3. volatility compression / release
4. multi-timeframe context
5. crypto-specific BTC / derivatives context

A separate crypto research track is now defined.

Proposed 12-asset crypto research universe:
- Discovery/core: BTC, ETH, SOL, BNB
- fresh OOS candidates: XRP, ADA, DOGE, TRX
- fresh Frozen OOS candidates: LINK, AVAX, LTC, BCH

No empirical OOS/Frozen OOS designation becomes official until the exact exchange, quote pair, timeframe, date range, and rule are pre-registered.

CCXT is added as the preferred open-source crypto OHLCV research adapter.

Important:
equity and crypto evidence must be reported independently; do not average them into one validation score.


## Historical feature duplication audit

Before opening the next feature experiment, retained research history was audited.

Result:
- ER10: NEW
- CHOP14: NEW
- CMF20: PARTIAL_OVERLAP but materially different from generic volume hard filtering
- OBVImpulse10: PARTIAL_OVERLAP but materially different from generic volume hard filtering
- RVOL20: DEFER because the exact old volume-filter formula is unrecovered
- Squeeze: PARTIAL_OVERLAP with fast-width / volatility-expansion research
- NATR regime: PARTIAL_OVERLAP with prior ATR research

The next safe feature-diagnostic set is limited to:
ER10, CHOP14, CMF20, OBVImpulse10.

Do not open a new hard-filter experiment until these features first show incremental diagnostic value.


## Active research round — E034

Status: PRE-REGISTERED.

E034 follows the mandatory historical duplication audit.

Included features:
- ER10
- CHOP14
- CMF20
- OBVImpulse10

Excluded:
- RVOL20 due unresolved overlap with prior volume hard filter
- Squeeze due overlap with prior volatility-expansion research
- NATR regime due extensive prior ATR-family research

Two fixed snapshots:
- Qualified GRB signal close
- original OPEN execution-day close

Tracks:
- 30-stock Equity Discovery
- BTC / ETH / SOL / BNB Crypto Discovery

Equity and crypto results must remain separate.

E034 is diagnostic only and cannot create a trading rule.


## E034 provider coverage — pre-result

Before feature outcomes were computed, actual Massive coverage was frozen:

- equity: from 2024-09-18
- BTC/USD: 2024-09-18 to 2026-09-17
- ETH/USD: 2024-09-18 to 2026-09-17
- SOL/USD: 2024-09-18 to 2026-09-17
- BNB/USD: 2026-03-04 to 2026-09-17 only

BNB is not replaced.

Normal warm-up remains mandatory and BNB may legitimately be too sparse.


## E034 result — Orthogonal Feature Diagnostic

Status: NO_DIAGNOSTIC_CANDIDATE.

Equity:
- 30/30 stocks
- 40 resolved lifecycles
- 31 Mature / 9 Failure
- ER10, CHOP14, CMF20, and OBVImpulse10 were tested at two fixed snapshots
- no feature/snapshot passed the pre-registered diagnostic gate

Largest equity separation:
CHOP14 at entry-day close:
- Mature median 51.79
- Failure median 56.98
- Cliff delta -0.190
- below the required |0.33| threshold
- quartile behavior was not monotonic

Crypto:
- BTC / ETH / SOL / BNB
- only 7 resolved lifecycles
- 4 Mature / 3 Failure
- all feature/snapshot results classified TOO_SPARSE

Therefore:
- no trading rule is created
- all equity holdouts remain unopened
- all crypto holdouts remain unopened

Research implication:
single-snapshot ER / CHOP / CMF / normalized-OBV levels did not solve Mature-vs-Failure discrimination on equities.
Crypto needs more independent lifecycle history before these features can be judged.


## 15m crypto dynamic-position direction

The intended SSSS architecture is reaffirmed as a complete dynamic position state machine:

FLAT -> OPEN -> HOLD -> ADD / REDUCE / RE-ADD -> CLOSE -> FLAT.

The current executable model's lack of validated ADD / REDUCE / RE-ADD actions is a research-maturity limitation, not the intended final design.

For crypto, the next architecture track should be 15-minute native rather than attempting to increase trade frequency only by loosening the daily OPEN rule.

Important:
daily parameter counts must not be copied directly to 15m bars, and they must not be mechanically time-scaled without validation.

A separate 15m model version should be developed and validated while keeping the frozen daily core unchanged.

See:
`SSSS_15M_DYNAMIC_POSITION_ARCHITECTURE.md`


## Active research round — E035

Status: PRE-REGISTERED.

Target:
BTC 15m native dynamic position engine Discovery map.

Relationship to prior work:
- 15m timeframe = NEW
- dynamic action architecture = PARTIAL_OVERLAP with prior daily ADD / REDUCE / RE-ADD work

E035 first selects one usable 15m structural baseline from three fixed configurations.

Only then, on the selected baseline, it maps the economics of:
- multiple OPEN modes
- ADD
- REDUCE
- RE-ADD recovery
- earlier CLOSE

No position percentages are assigned.

No action can be accepted from E035 itself.

Temporal holdouts are frozen and must remain unopened:
- BTC 15m OOS: 2025-09-01 through 2026-03-31
- BTC 15m Frozen OOS: 2026-04-01 through 2026-09-17

ETH / SOL / BNB 15m outcomes also remain unopened in E035.


## E035 15m Discovery data integrity — pre-result

Raw BTC 15m Discovery snapshot completed:
- 33,312 continuous bars
- 2024-09-19 00:00 UTC through 2025-08-31 23:45 UTC
- no duplicate timestamps
- no missing 15m intervals
- no zero-volume bars
- raw fingerprint: 2f6aba04f4ca730c

94 composite-feed bars had sub-1-basis-point OHLC boundary rounding inconsistencies.

Before any B0/B1/B2 result was computed, sanitation was frozen to:
- high = max(high, open, close)
- low = min(low, open, close)

No rows are removed and no other field is changed.
