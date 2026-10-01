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


## E035 result — BTC 15m baseline selection

Status: NO_15M_BASELINE.

All three fixed 15m baseline configurations failed the pre-registered eligibility gate.

Best structural reference:
B2 NATIVE_24H
- 47 resolved
- 32 Mature / 15 Failure
- 4.06 resolved lifecycles per 30 days
- median hold 46.75h
- base-friction average +0.59%
- base-friction median -0.43%
- base PF 1.56
- stress-friction average +0.53%

B2 is NOT a validated baseline.
It is only the most informative reference for the next Discovery round because positive mean/PF coexist with a negative typical trade.

E035 stopped before any dynamic action map was opened.

All temporal and cross-asset holdouts remain unopened.


## Active research round — E036

Status: PRE-REGISTERED.

E036 uses the failed-but-informative B2 NATIVE_24H structure strictly as a Discovery reference.

Goal:
repair the 15m engine through multiple distinct OPEN modes first.

Four fixed OPEN modes:
- GRB
- FAST_BREAKOUT
- GREEN_TRANSITION
- FASTMID_RECLAIM

At least two must pass independently and their union must pass a cost-robust Multi-Open Reference gate.

Only then may the Discovery-only ADD / REDUCE / RE-ADD / CLOSE repair maps be opened.

No holdout period or cross-asset 15m data is opened in E036.


## E036 result — 15m OPEN role discovery

Status: NO_MULTI_OPEN_REFERENCE.

Only GREEN_TRANSITION passed the fixed OPEN-mode gate.

O3 GREEN_TRANSITION:
- 70 resolved
- base mean +0.94%
- base median +0.24%
- base PF 1.91
- stress median +0.18%

GRB, FAST_BREAKOUT, and FASTMID_RECLAIM all had positive averages but negative base/stress medians.

Implication:
for 15m BTC, early state transition appears more suitable as starter exposure.
Later breakout/reclaim evidence may be better studied as ADD rather than independent OPEN.

E036 action maps remained unopened by rule.


## Active research round — E037

Status: PRE-REGISTERED.

GREEN_TRANSITION is fixed as the Discovery starter OPEN reference.

Later GRB / FAST_BREAKOUT / FASTMID_RECLAIM evidence is reclassified to ADD research.

E037 maps the full post-entry dynamic action surface:
- ADD
- REDUCE
- RE-ADD
- CLOSE

No position percentage is assigned and no action can be validated inside E037.

All temporal and cross-asset holdouts remain unopened.


## E037 result — 15m dynamic action surface

Status: DYNAMIC_ACTION_ZONES_FOUND.

GREEN_TRANSITION starter reference:
- 48 resolved one-at-a-time lifecycles
- base mean +0.95%
- base median +0.21%
- base PF 1.97

Direct post-entry confirmation ADD events all failed positive-median gates:
- GRB
- FAST_BREAKOUT
- FASTMID_RECLAIM

However 10 ADD opportunity-map cells passed.

Strongest:
MFE < 1 EntryATR AND current progress <= 0:
- 32 events
- base mean +1.49%
- base median +0.64%
- stress median +0.58%
- PF 2.44
- median timing 1 bar after starter

Other passing zones cluster:
- PRE_RED
- first few bars
- price at/below starter entry
- low MFE / limited extension

No REDUCE / RE-ADD / CLOSE zone passed.

Important:
15m BTC independently reproduces the earlier equity finding that marginal exposure economics are strongest early and weaken with later confirmation.

Current 15m architecture frontier:
- STARTER OPEN: GREEN_TRANSITION Discovery candidate
- ADD: early opportunity zones only; no exact validated trigger
- REDUCE: none accepted
- RE-ADD: none accepted
- CLOSE: B2 reference close remains diagnostic benchmark; no earlier replacement found

Holdouts remain unopened.


## Active research round — E038

Status: PRE-REGISTERED.

E038 changes the research unit from isolated REDUCE / RE-ADD signals to a paired tactical tranche cycle.

Architecture:
- 30% starter core
- 10% early tactical ADD
- tactical REDUCE sells only that 10%
- RE-ADD restores that 10%
- the 30% core stays invested until the existing reference CLOSE

The exact first-ADD formula is tested literally as one re-add candidate, alongside three recovery-specific alternatives.

No full-close rule is changed in E038.
All holdouts remain unopened.


## E038 result — tactical REDUCE / RE-ADD pairing

Status: NO_TACTICAL_REDUCE_CANDIDATE.

32 starter lifecycles contained the leading first ADD.

Key result:
GREEN->GRAY after ADD is informative but not a general REDUCE action.

For the tactical 10% tranche:
- Failure-path incremental benefit from reducing at GREEN->GRAY was strongly positive;
- Mature-path average incremental value was strongly negative because large continuations were sacrificed.

Therefore GREEN->GRAY is better treated as a risk-classification point than as an unconditional reduce command.

Exact reuse of the first ADD formula for RE-ADD failed structurally and empirically:
- 5/32 re-adds after GREEN->GRAY
- 0 after mature-giveback reduction
- 0 after RTE reduction

Reason:
RunningMFE<1 ATR is cumulative from the original starter and normally cannot become true again later in a mature lifecycle.

No tested recovery rule passed.

Current 15m action frontier:
- STARTER OPEN: GREEN_TRANSITION Discovery candidate
- FIRST ADD: early unextended zone Discovery candidate
- REDUCE: no validated action; GREEN->GRAY becomes priority risk-classification checkpoint
- RE-ADD: requires a new local-reset/recovery formulation
- CLOSE: keep current reference close


## Active research round — E039

Status: PRE-REGISTERED.

New 15m sizing architecture:
- OPEN 30%
- TREND_ADD +10pp
- LOSS_ADD +10pp
- max exposure 50%
- PROFIT_RISK_REDUCE: sell 15% of current position
- LOSS_RISK_REDUCE: sell 15% of current position
- reference CLOSE unchanged

Two causal probability outputs:
- P_UP
- P_DD4H

Loss-add threshold is selected only from the frozen -2%..-8% grid using chronological OOF Discovery predictions.

Any surviving rule is DISCOVERY_CANDIDATE only.


## E039 result — probability-guided sizing

Status: NO_PROBABILITY_ACTION_MODEL.

Chronological OOF testing of 63 fixed probability/loss-threshold combinations produced zero eligible full action engines.

The simpler E037 benchmark remained better.

Provisional LOSS_ADD research zone:
-6% to -7% position loss.

Research center:
-6%.

Evidence at -6%:
- 7 events
- mean incremental unit return +0.40%
- median +1.14%
- PF 1.34
- q25 -1.59%

Insufficient event count for activation.

Therefore the mutable 15m research configuration records:
- LOSS_ADD_CANDIDATE_THRESHOLD = -0.06
- LOSS_ADD_CANDIDATE_BAND = (-0.07, -0.06)
- LOSS_ADD_ENABLED = False

Probability-guided TREND_ADD and both REDUCE modes are also disabled.

Current architecture intent remains:
- OPEN 30%
- two future ADD modes
- two future REDUCE modes
- current CLOSE unchanged

but none of the new probability actions is validated.


## Active research round — E040

Status: PRE-REGISTERED.

Research target:
repeated local-reset pullback sizing.

Unlike E039 one-time loss thresholds, E040 allows repeated sizing actions inside one lifecycle.

Candidate pullback steps:
1% through 10%.

Every sizing action resets the local pullback anchor.

Model bullish validity is tested using three existing structural floors.

Current risk constraints:
- starter 30%
- +10pp per ADD
- max exposure 50%
- REDUCE = 15% of current position quantity
- minimum core exposure 30%
- reference CLOSE unchanged

All holdouts remain unopened.


## E040 result — repeated pullback ladder

Status: NO_REPEATED_PULLBACK_LADDER.

A full repeated ADD/REDUCE ladder did not pass all portfolio gates.

But one action family became materially clearer:

LOSS_PULLBACK_ADD provisional Discovery rule:
- local pullback step = 1%
- local anchor resets after every sizing action
- bullish validity floor = FastLower
- continuation state = Effective GREEN or RED with dsep > 0
- current position is losing
- +10pp exposure
- max total exposure currently 50%

Discovery evidence:
97 loss-state ADD events,
+2.91% mean incremental unit return,
+1.22% median,
PF 3.44,
stress median +1.16%.

Second ADD under the overall 1% ladder also remained positive:
26 events,
+1.93% mean,
+0.53% median.

By contrast:
profit-state 1% pullback ADD had negative median economics.

Repeated REDUCE also failed:
typical edge sometimes positive, but large Mature continuations made mean edge negative.

Therefore:
- 1% is the current provisional repeated LOSS-ADD step;
- it is inactive pending OOS;
- do not reuse it for profitable-position ADD;
- no repeated REDUCE threshold is active.


## Active research round — E041

Status: PRE-REGISTERED.

Research target:
isolate the E040 provisional 1% FastLower LOSS_PULLBACK_ADD and determine whether one or two loss-add steps best preserve economic value within the existing drawdown tolerance.

Frozen variants:
- L1: maximum one LOSS_PULLBACK_ADD, max exposure 40%
- L2: maximum two LOSS_PULLBACK_ADD actions, max exposure 50%

TREND_PULLBACK_ADD is disabled.
Repeated REDUCE / RE-ADD are disabled.
Reference CLOSE is unchanged.

E041 is Discovery-only.
BTC OOS / Frozen OOS and ETH/SOL/BNB 15m remain unopened.


## E041 result — loss-add ladder depth / drawdown attribution

Status: NO_LOSS_ADD_DEPTH_CANDIDATE.

The E040 provisional 1% FastLower LOSS_PULLBACK_ADD was isolated from rejected TREND_ADD and REDUCE actions.

L1 — at most one LOSS_ADD:
- 20 events;
- mean +2.18%;
- median +0.57%;
- PF 2.68;
- portfolio +18.61%;
- stress +17.44%;
- maxDD 9.33%.

L1 failed:
- top-3 winner concentration 64.9% > 60%;
- portfolio return and stress return were both below E037 Benchmark B.

L2 — at most two LOSS_ADDs:
- 37 pooled events;
- pooled mean +2.50%;
- pooled median +1.07%;
- PF 3.06;
- portfolio +23.98%;
- stress +22.63%.

Second LOSS_ADD:
- 17 events;
- mean +2.88%;
- median +1.22%;
- PF 3.58;
- stress median +1.16%;
- positive rate 76.5%.

However:
- L2 bar-level maxDD = 11.33%;
- Benchmark B maxDD = 9.82%;
- frozen allowed ceiling = 10.80%.

Thus the second step adds strong terminal economics but raises path drawdown above the pre-registered risk limit.

Drawdown attribution:
- L1 maxDD is about 0.49pp below Benchmark B;
- moving L1 -> L2 adds about 2.00pp maxDD;
- L2 is about 15.43% worse than Benchmark B on maxDD.

No E041 action is activated.
The existing 1% LOSS_PULLBACK_ADD remains an inactive Discovery research frontier only.

All BTC temporal holdouts and ETH/SOL/BNB 15m holdouts remain unopened.

Next frontier:
a causal SECOND LOSS_ADD risk-admission rule; do not retune the 1% pullback step.


## Active research round — E042

Status: PRE-REGISTERED.

Research target:
causal risk admission for the SECOND fixed LOSS_PULLBACK_ADD only.

Frozen:
- 1% pullback step;
- FastLower validity;
- first LOSS_ADD 30% -> 40%;
- second candidate ADD 40% -> 50%;
- TREND_ADD disabled;
- REDUCE / RE-ADD disabled;
- reference CLOSE unchanged.

Seven fixed causal admission candidates use only existing SSSS structure / already-completed path information.

E042 is Discovery-only.
BTC OOS / Frozen OOS and ETH/SOL/BNB 15m remain unopened.


## E042 result — second LOSS_ADD risk admission

Status: NO_SECOND_LOSS_ADD_RISK_GATE.

E041 continuity was reproduced:
- 20 first LOSS_ADD events;
- 17 second LOSS_ADD signals;
- L1 +18.61% / maxDD 9.33%;
- L2 +23.98% / maxDD 11.33%.

Key candidate results:

C1 GREEN_ONLY:
- all 17 signals were already GREEN;
- no discrimination;
- identical to L2;
- maxDD 11.33%.

C2 ABOVE_FASTMID:
- 8 events;
- second-add median +0.82%;
- PF 12.61;
- portfolio +20.26%;
- maxDD 9.50%;
- but retained only 24.9% of L2 incremental return over Benchmark B;
- fails the frozen 50% economic-preservation gate.

C3 DSEP_ACCEL:
- 9 events;
- portfolio +19.06%;
- maxDD 10.96%;
- fails risk and preservation.

C4 FASTLOWER_BUFFER_05ATR:
- 16 events;
- portfolio +22.86%;
- retained 77.4% of L2 incremental return;
- maxDD 10.96% > 10.80% cap;
- concentration 35.97% > 35% ceiling.

C5 POST_FIRST_ADD_MAE_LE_1ATR:
- only 5 events;
- portfolio +18.64%;
- maxDD 10.03%;
- too sparse and economically weak.

C6 duplicated C3 in this sample.
C7 duplicated C5 in this sample.

No candidate passed all pre-registered gates.

All temporal and cross-asset 15m holdouts remain unopened.

Next frontier:
local path-shape structure between first LOSS_ADD and the first second-LOSS_ADD signal.
Do not retune the E042 scalar thresholds.


## Active research round — E043

Status: ACTIVE FORWARD PAPER TRADING.

Assets:
BTC / ETH / BNB.

Timeframe:
5m.

Forward decision boundary:
first completed bar starting at or after 2026-09-20 18:20 UTC.

Pre-boundary data:
WARMUP_ONLY.

Research combines:
F1 LMD2/LMD3,
F2 causalized structural support/resistance,
F3 DXBD,
F4 KDJ/flow/MACD resonance,
F5 existing SSSS structural family.

10x is the instrument leverage setting; margin allocation is separately capped by the E043 risk engine.

No live exchange-order connector is attached.


## E043 active — 5m API forward paper trading

Status:
ACTIVE_FORWARD_PAPER / WAIT_STALE_DATA.

Assets:
BTC / ETH / BNB.

Execution:
- 5m completed bars;
- 10x instrument leverage;
- paper trading only;
- no live exchange order routing connected.

Formula families:
- F1 LMD2/LMD3;
- F2 causalized support/resistance / SAR structure;
- F3 DXBD;
- F4 KDJ / flow / MACD resonance;
- F5 existing SSSS structural state.

Critical causality rule:
BACKSET / retrospective pivot drawing / REFDATE display behavior cannot trigger forward orders.

Seen calibration:
2026-09-18 through 2026-09-19 23:55 UTC.

True forward start:
strictly after 2026-09-20 18:09 UTC.

Current API limitation:
Massive historical 5m endpoint latest available bar at activation = 2026-09-19 23:55 UTC.
Massive real-time Snapshot = NOT_ENTITLED.

Therefore:
no paper position is open.
No trade is backfilled from stale data.


## E043 automation status

Status:
ACTIVE_FORWARD / AUTOMATION_BLOCKED.

The 5m paper engine, trade ledger, state file, indicator-family map, Binance public API source, and scheduled workflow are present.

First scheduled/push workflow attempt failed before any step executed:
runner_id=0,
steps=[].

This is not a strategy failure.
No paper order has been generated.

Massive near-real-time 5m data is also unavailable under the connected entitlement, so forward 5m execution currently requires an available external runner or sub-hour API execution service.

## Stock Risk Exit Study v1.1 — corrected closure — 2026-10-01

Status: **IMPLEMENTED_AND_VERIFIED / CLOSED**.

Scope:
- frozen 39-stock universe;
- 49 configurations per stock;
- 1,911 corrected portfolio runs;
- 5,000 deterministic stock-level bootstrap resamples;
- matched baseline trade audit;
- 2010-2014 / 2015-2019 / 2020-2026 diagnostics;
- sector-diversity inspection.

Correction:
- the first-pass closure was invalidated because sample-end open positions were synthetically sold;
- v1.1 restores frozen mark-to-market semantics;
- corrected baseline reproduction vs frozen AB_HALF control passed on all 39 stocks;
- trades / win / exposure differences are exactly zero and remaining numeric differences are floating-point tolerance only.

Corrected baseline aggregate:
- mean cumulative return +154.92%;
- mean intraday-low MDD -30.65%;
- mean P5 -6.95%;
- mean CVaR10 -8.22%;
- 2,606 completed trades.

Decisions:
- `UNIVERSAL_STOCK_HARD_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`
- `UNIVERSAL_STOCK_TRAILING_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`
- `UNIVERSAL_STOCK_HARD_TRAIL_COMBINATION = REJECTED_NOT_ADMITTED`
- `STOCK_SELECTIVE_SIGNAL_EXIT_CONTROL = RETAINED`
- `STATE_OR_VOLATILITY_AWARE_STOCK_RISK_EXIT = PROMOTED_TO_NEXT_VALIDATION`
- `STOCK_RISK_EXIT_STUDY_V1_1 = IMPLEMENTED_AND_VERIFIED`

Canonical corrected report:
`research/ssss/source_xma/experiments/stock_risk_exit_study_v1/FIVEGZ5SE_STOCK_RISK_EXIT_FINAL_v1_1.md`

The invalidated first-pass report is historical only and must not be used as the current result.

## State / Volatility-Aware Risk Exit Study v1 — 2026-10-01

Status: **IMPLEMENTED_AND_VERIFIED / CLOSED**.

Baseline reproduction:
- stocks 39/39 exact PASS;
- Crypto BTC / ETH / BNB / SOL exact PASS.

Formal candidate results:
- stock pass: 0 / 8;
- Crypto pass: 0 / 8;
- universal pass: 0 / 8.

Final decisions:
- `STOCK_RISK_EXIT = NOT_USED_RETAIN_BASELINE`
- `CRYPTO_RISK_EXIT = NOT_USED_RETAIN_BASELINE`
- `UNIVERSAL_STATE_VOL_RISK_EXIT = REJECTED_NOT_ADMITTED`
- `RISK_EXIT_LAYER = NOT_USED_RETAIN_BASELINES`
- `STATE_VOL_RISK_EXIT_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`

Canonical final report:
`research/ssss/source_xma/experiments/state_vol_risk_exit_study_v1/FIVEGZ5SE_STATE_VOL_RISK_EXIT_FINAL_v1.md`

Round CLOSED. No post-result threshold tuning is allowed inside v1.

## Crypto SELL-C Partial Exit Study v1 — 2026-10-01

Status: **IMPLEMENTED_AND_VERIFIED / CLOSED**.

Tested on frozen BTC / ETH / BNB / SOL:
- SELL-C 25%
- SELL-C 50%
- SELL-C 75%
- SELL-C 100% control

Baseline reproduction: PASS.

Corrected final result:
- 25% partial: mean return +233.09%, MDD +1.04pp better, but P5 -3.50pp and CVaR -1.94pp worse.
- 50% partial: mean return +154.96%, MDD +2.79pp better, but P5 -2.07pp and CVaR -1.41pp worse.
- 75% partial: mean return +91.02%, MDD +4.12pp better, but P5 -1.48pp and CVaR -0.93pp worse; SOL return also fell materially.
- 100% control: mean return +68.74%, retained because no partial policy passed all preregistered gates.

Decisions:
- `CRYPTO_SELL_C_25 = REJECTED_NOT_ADMITTED`
- `CRYPTO_SELL_C_50 = REJECTED_NOT_ADMITTED`
- `CRYPTO_SELL_C_75 = REJECTED_NOT_ADMITTED`
- `CRYPTO_SELL_C_FULL = RETAINED`
- `CRYPTO_SELL_C_PARTIAL_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`

Canonical report:
`research/ssss/source_xma/experiments/crypto_sell_c_partial_study_v1/FIVEGZ5SE_CRYPTO_SELL_C_PARTIAL_FINAL_v1.md`

Round CLOSED. Do not tune further percentages on the same development data.

## Stock three-buy / three-sell open-issues audit — 2026-10-01

`STOCK_THREE_BUY_THREE_SELL_STRUCTURAL_OPEN_ISSUES = NONE_IDENTIFIED`

The stock rules are structurally defined. Remaining work is genuine future OOS validation for:
- 60% initial + W3 BUY-C top-up to 100%;
- isolated SELL-A / SELL-B half exit.

No new stock optimization round is opened.

## Crypto V1 baseline freeze — 2026-10-01

Status: **FROZEN_BASELINE**.

The current SSSS Crypto framework is now formally named:

`Crypto V1`

Frozen core:
- BTC / ETH / BNB / SOL development evidence;
- BUY-A / BUY-B -> 60%;
- W3 BUY-C -> +40% to 100%;
- SELL-A -> full exit;
- SELL-B -> full exit;
- SELL-C -> full exit;
- no independent Risk Exit layer;
- execution = `Close Confirmed -> Next Bar Open`;
- no fixed 24-hour delay.

Canonical baseline:
`research/ssss/CRYPTO_V1_BASELINE.md`

`CRYPTO_V1 = FROZEN_BASELINE`

Future changes must not overwrite Crypto V1; they require a new experiment/version.

