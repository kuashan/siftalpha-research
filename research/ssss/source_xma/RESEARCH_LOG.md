# Source-XMA Research Log

## 2026-09-27 — Track initialization

Repository baseline inspected before changes:
- repository: kuashan/siftalpha-research
- visibility: private
- default branch: main
- main HEAD at inspection: 512375038ba794536d785e51ad29fa14b9897d4b

Existing official SSSS state was read before opening this track.

Important boundary:
- existing official research uses a causal DEMA rewrite for the current model;
- this new track deliberately restores the original XMA for source-behavior research;
- the existing causal conclusions and model files were not modified.

Source findings recorded at initialization:
1. SSSS and ADKBY-E share the same double-XMA(25) core fast structure.
2. ADKBY-E's normalized 20000/80000 levels map to the same lower/upper fast-band geometry.
3. SSSS low slow-structure formula contains REF(H,11) in the low-weighted series.
4. ADKBY-E uses REF(L,11).
5. SSSS omits lag 19 and includes lag 20 at weight 1.
6. ADKBY-E includes both lag 19 and lag 20 at weight 1 while retaining denominator 210.
7. Therefore the slow structures are not mathematically identical and must be recorded separately.
8. The original three regime states leave an unclassified/expansion geometry; the research vocabulary adds EXPANSION / REGIME_UNCLEAR.
9. The author's icons/text remain comparison observations, not our target decision labels.

First case study:
- ABT daily
- anchor 2025-01-01
- first tradable session 2025-01-02
- walk forward toward latest available data
- preserve XMA
- no conventional return-optimization backtest

Evidence warning:
A later ABT history chart was already viewed before this repository track was initialized. Therefore the ABT replay is exploratory / previously seen, not OOS or Frozen OOS.

Current next step:
Obtain point-in-time ABT daily OHLCV and establish an exact, documented XMA reproduction path before populating observations.csv and decisions.csv.


## 2026-09-28 — ABT first-month walk-forward completed

Window:
- 2025-01-02 through 2025-01-31
- 20 trading sessions
- source XMA preserved
- point-in-time first-observed XMA values used for decisions
- $10,000 paper capital
- next-open execution
- 5 bps one-way slippage
- fractional shares

Key source-system events:
- 2025-01-15: SSSS LOW_ICON + ADKBY-E 多
- 2025-01-21: SSSS HIGH_ICON + ADKBY-E 空 while source state was still RANGE

Independent interpretation:
- Jan-15 lower extreme -> 30% probe only because both momentum components were still down
- Jan-16 XMA-mid reclaim + BOTH_UP -> target 70%
- Jan-21 FastUpper breakout + BOTH_UP + RVOL 1.65x -> override the source RANGE short signal; target 100%
- Jan-28 extreme extension + momentum deceleration -> reduce to 70%
- Jan-30 slow-momentum turn negative / conflict -> exit remaining position next open
- Jan-31 BULL regime prevented an automatic short reversal

Paper result:
- final capital: $11,345.49
- net return: +13.45%
- close-to-close equity max drawdown: about -1.58%
- result is exploratory, not OOS

Source-literal comparison:
- following Jan-15 long then Jan-21 high-side exit literally would have produced about +2.70% net under the same execution friction
- reversing the Jan-21 ADKBY-E 空 into a literal short and covering Jan-31 open would have lost about -12.59% before borrow cost

Auxiliary-factor ablation:
- volume as mandatory entry gate: harmful in this month
- volume as breakout confirmation: helpful
- VIX as a hard gate: not supported; retain as context only

Important XMA observation:
- XMA historical values near the right edge revise materially as later bars arrive
- decisions remain tied to the first-observed point-in-time XMA values
- revisions are stored in experiments/abt_2025_walkforward/revisions.csv

Artifacts:
- observations.csv
- decisions.csv
- paper_trades.csv
- revisions.csv
- FIRST_MONTH_REPORT.md
- visual_report.html

Next research step:
continue the same walk-forward method into February 2025 without retroactively rewriting January decisions.


## 2026-09-28 — HYS2 candidate + multi-asset expansion

A new source indicator, HYS2.ftindex, was received and inspected.

Source SHA-256:
`40936da053455c2e4d05d4bab3f28757e3c59c6cc92668e7c98dd443743799c3`

Decision:
- do NOT merge HYS2 into the XMA baseline;
- log it as CANDIDATE_FEATURE;
- evaluate low-side panic/new-low impulse and ★共振 separately;
- do NOT treat 火焰山顶 as an automatic sell or short;
- do NOT retroactively change January decisions.

ABT January post-hoc finding:
- HYS2 new-30-day-low / fire-bottom impulse occurred on Jan-15;
- HYS2 ★共振 occurred on Jan-16, aligning with the previously frozen XMA confirmation entry;
- HYS2 fire-top was active during Jan-21 onward breakout and would have been harmful if interpreted as an automatic short.

The research universe is expanded from a single ABT case to a multi-asset Discovery universe including ARM, ORCL, AAPL, AMZN, INTC and other widely recognized liquid names. See MULTI_ASSET_UNIVERSE.md.

No rule requires opening a short position. Exit and short-entry are separate decisions.


## 2026-09-28 — FIVEGZ5SE candidate state engine

User supplied FIVEGZ5SE.txt and explicitly warned that textual annotations, especially concepts labeled "清" and "抄", are not reliable semantics.

Source:
- SHA-256: 61bc9f7cad7a2efb6374a187c680fa75789b2468824885e5127c5f70333400c9
- size: 93,201 bytes

Research decision:
- evaluate actual boolean logic, not displayed names;
- do not merge into the XMA baseline;
- treat the five raw dimensions as auxiliary states;
- freeze prior January XMA decisions unchanged.

Key findings:
- "当下清仓" is actually trend-short AND capital-short AND momentum-short; record it as triple-bear confirmation, not mandatory liquidation.
- "底部双重背离" is not mathematical divergence; it is weak-trend + capital/momentum recovery.
- several COUNT-based comments overstate dimension counting; the code counts bars after OR aggregation.
- MOM_CONTINUOUS_DAYS=0 disables the intended continuity gate.
- ABT Jan-16 composite risk conflicts with the previously frozen XMA confirmation entry.
- ABT Jan-21 all five dimensions turn LONG and strongly confirm the breakout.
- ABT Jan-24 reduce-state is earlier than the later price peak; treat as caution, not mandatory reduction.
- Jan-30/31 triple-bear confirmation still does not occur, so it is too late as a primary exit rule in this case.

See FIVEGZ5SE_EVALUATION.md.


## 2026-09-28 — February 2025 multi-asset Discovery run

Protocol was frozen before execution:
`experiments/multi_asset_2025_02/PROTOCOL_FROZEN_BEFORE_RUN.md`

Universe:
ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM.

ARM was not forced into the batch because a sufficiently verified common OHLCV source was not available.

Four variants:
- XMA_ONLY
- XMA_HYS2
- XMA_FIVEGZ
- XMA_HYS2_FIVEGZ

Cross-symbol result:
- combined had the highest mean return (+0.151%)
- XMA_FIVEGZ had the best downside profile (worst -1.271%, mean max DD -0.233%)
- HYS2 improved NVDA but worsened multiple losers when used as a global sizing boost
- FIVEGZ raw color states were the most consistent risk-control addition

Critical findings:
1. repeated XMA probes are too permissive in persistent declines (GOOGL/AMZN)
2. slow BEAR regime can miss fast transition rallies (INTC; weaker AAPL example)
3. next-open execution needs a gap-against-signal re-evaluation rule
4. FIVEGZ color transitions should be interpreted as a state continuum, not literal text commands
5. no automatic shorting rule was introduced

No February rule was retroactively changed.
Candidate fixes must be frozen before the next month.


## 2026-09-28 — March–June 2025 multi-asset run

Frozen protocol:
`experiments/multi_asset_2025_03_06/PROTOCOL_FROZEN_BEFORE_RUN.md`
commit:
`bd58431a8214c76549e624c49422c9a9850e6851`

Primary execution model changed from legacy next-open to:
`SAME_BAR_CLOSE_PROXY_V2`.

Reason:
the signal/action belongs to the current K bar once the full rule is satisfied.

Limitation:
daily bars cannot identify exact intraday first-confirm time; same-bar close is a causal execution proxy, not a minute replay.

Universe:
11 equities + BTC / ETH / BNB / SOL.

Major findings:
1. XMA + FIVEGZ had the highest equity mean return (+1.101%) but the result is strongly ORCL-driven; trimmed mean remains negative.
2. Combined HYS2+FIVEGZ was not robust and worsened median/worst outcomes.
3. Crypto SCTYPE=2 FIVEGZ was harmful in this window; do not promote it.
4. HYS2 was only selectively helpful in crypto.
5. Transition Override was too aggressive. On 2025-04-09 it fired across many assets simultaneously; first override exposure must be smaller in the next preregistered version.
6. Three-bar cooldown reduced but did not eliminate repeated failed probes.
7. No automatic shorting was introduced.
8. ARM remains excluded until verified daily OHLCV is available.

No March–June rule was retroactively changed.


## 2026-09-28 — Orthogonal-feature March–June re-test

Frozen before result:
- protocol commit 9f19b858c611140bc9c4980ac6d60d00ddf36d66
- breadth retrieval amendment commit 52e1f52965eb0526053c2434f5d9caf8ee29c137

Chronology:
- stocks start 2025-03-03
- crypto start 2025-03-01
- Source-XMA recomputed one bar at a time with end=t
- no future XMA revision used
- same-bar close proxy + 5bps

HYS2/FIVEGZ were removed from trade control.

Main results:
- equities XMA_ONLY +1.786% mean / +2.784% median
- equities Volume improved 8/11 names but worsened worst-case and drawdown
- VIX frozen rule produced no sizing changes on recorded XMA decision bars
- breadth proxy was mixed
- daily Volume Profile proxy was near-neutral/slightly helpful
- all-factor additive sizing had highest stock mean but materially worse tail risk

Crypto:
- XMA_ONLY mean +0.748%
- Volume Profile proxy +0.887% with slightly better mean drawdown
- Volume+Breadth interaction was strongly harmful
- all-factor additive sizing was harmful

Research conclusion:
- Source-XMA should remain the decision center
- orthogonal factors should answer specific questions, not vote linearly for larger size
- stock Volume Structure is the strongest auxiliary candidate, but as breakout-quality/cap logic rather than generic size bonus
- crypto Volume Profile proxy is the strongest next candidate
- VIX/Breadth remain context until stronger evidence

No March–June threshold was changed after result.

## 2026-09-28 — Three-color band promoted to core XMA state

Research correction: the Source-XMA three-color band is not decorative and must not be omitted from geometry research.

The underlying state equations are GZB12 / GZB13 / GZB14:
- upward fast-channel relation
- downward fast-channel relation
- contained/range relation

An implicit fourth EXPANSION_STRADDLE topology is also recorded when the fast channel expands outside both slow boundaries.

From this point forward, every candidate rail/candle event is conditioned on:
- current band state
- previous band state
- transition type
- duration in state

In particular:
- lower-rail confluence is not treated as one universal buy signal;
- upper-rail confluence/exceed is not treated as one universal top signal;
- the same geometry may represent continuation or reversal depending on the band color/state and its transition.

See XMA_GEOMETRY_COLOR_STATE_MODEL.md.

## 2026-09-28 — Full XMA research specification frozen

Created:
`XMA_FULL_RESEARCH_SPECIFICATION.md`

The master research direction is now formally defined as:

```text
XMA Geometry
× Three-Color Band State / Transition
× Selective HYS2 Confirmation
× Orthogonal Auxiliary Context
× Lifecycle Position Management
```

Important governance:
- XMA remains primary;
- HYS2 is an auxiliary research object, not an automatic trade engine;
- Volume / Volume Profile / Breadth / VIX are tested as orthogonal information;
- FIVEGZ text labels remain non-authoritative;
- pure XMA geometry is studied before external confirmation;
- all future rules must be frozen before a new validation window;
- each research phase has explicit closure criteria.

This document is now the master specification for the next research phase.


## 2026-09-28 — Formula canonicalization gate before further research

A source-formula audit identified issues that must be resolved before the next run.

Canonical decisions:
- SSSS GZB2 lag-11 term: H -> L
- weighted high/low channels: lags 0..19 only, weights 20..1, denominator 210
- SSSS and ADKBY-E share the same canonical weighted definition
- HYS2 SCQH is confirmed as external .ftindex parameter metadata; do not hard-code SCQH:=0 in the cross-market formula
- research three-color classification is expanded to four mutually exclusive states, adding EXPANSION_STRADDLE and removing equality ambiguity

Governance:
all earlier raw-source runs remain preserved but are marked LEGACY_RAW_SOURCE_EXPLORATORY relative to the corrected canonical model.

See:
- FORMULA_CORRECTION_AUDIT_v1.md
- CANONICAL_WEIGHTED_CHANNEL_v1.md


## 2026-09-28 — Canonical geometry Phase 1–5 first synthesis

The corrected canonical v1 formulas were used to restart XMA geometry research point-in-time from the first evaluation day.

Key preliminary findings:
- strict UP-state upper fast/outer confluence (ZK1 + BS within 0.25 ATR and candle overlap) is strongly different from ordinary rail riding;
- deduplicated strict upper episodes had negative 5/10-bar forward distribution, while far-gap UP rail riding was mildly positive;
- DOWN-state lower confluence is not an immediate universal buy; it behaves more like an early dislocation precursor;
- the current same-bar full-reclaim definition was harmful and is dropped;
- HYS2 fire-bottom/fire-top were largely redundant with strict XMA geometry in this window;
- recent HYS2 resonance did not improve strict lower confluence and is not promoted;
- lower confluence below rolling Value Area showed the cleanest auxiliary separation so far;
- negative volume / negative breadth around lower confluence may reflect capitulation, but samples remain small;
- VIX frozen rule was neutral.

See:
`experiments/canonical_geometry_2025_01_06/PHASE1_5_SYNTHESIS.md`

No trading rule or position size is promoted yet.


## 2026-09-28 — Falsification v1 overturns broad canonical geometry rules

A preregistered falsification protocol was frozen before holdout outcome analysis.

Universe:
- 39 US equities across 11 sectors
- BTC / ETH / BNB / SOL

Holdouts:
- Validation A: 2020–2024 untouched historical holdout
- Validation B: 2025H2 forward holdout
- 2026H1 remains sealed

Primary results:
1. The Jan–Jun 2025 strict upper-confluence bearish effect did not replicate.
   - equities combined n=438
   - 5-bar raw ≈ +0.05%
   - sector excess ≈ +0.11%
   - matched-control excess ≈ +0.08%
   - clustered CIs span zero
   - crypto sign was positive
   => REJECT AS GENERAL RULE.

2. Lower strict confluence showed positive raw 10-bar rebound in historical data but negative matched excess.
   - Validation A n=325
   - raw +0.82%
   - matched excess -3.29%
   - symbol-cluster 95% CI roughly [-4.63%, -1.78%]
   - combined matched excess -3.22%
   => the raw rebound is largely generic DOWN-state mean reversion; REJECT GENERAL BUY RULE.

3. Deep-pierce reclaim, shallow interaction and deep no-reclaim all had negative matched excess.
   => no penetration subtype is promoted.

4. Common state transitions did not show strong standalone matched excess.
   => keep as descriptive lifecycle states, not directional signals.

5. FAST_MID_ANALYTIC up/down crossings both had positive absolute forward drift.
   => midpoint crossing alone is not directional evidence.

See:
`experiments/falsification_v1/FALSIFICATION_V1_INTERIM_REPORT.md`

This negative result is preserved without threshold repair.


## 2026-09-28 — Falsification v1 Stage 1

The research direction was explicitly switched from effect discovery to effect falsification.

Frozen protocol:
`experiments/falsification_v1/PROTOCOL_FROZEN_BEFORE_VALIDATION.md`

Major result:
the Jan–Jun 2025 strict upper-confluence bearish effect did NOT generalize to 2020–2024 equities and was positive in crypto.

Forward 2025 H2 equities again showed a bearish upper-confluence effect, including negative matched-control and SPY-relative returns, but n=28 and temporal/symbol concentration remain material.

Therefore the universal upper-top hypothesis is rejected and retained only as a regime-dependent candidate.

The lower strict-confluence delayed-rebound interpretation also failed geometry-specific controls:
2020–2024 absolute returns rebounded, but matched same-state controls did better; 2025 H2 was outright negative.

Therefore lower confluence is rejected as a standalone buy/rebound rule.

See:
`experiments/falsification_v1/STAGE1_FALSIFICATION_REPORT.md`

Stage 2 remains:
state transitions, analytic midpoint, survival/time-stop distributions, Below-VAL interaction, HYS2 interaction regression, Volume interaction, and multiple-testing control.

## 2026-09-28 — Falsification v1 stock time-to-confirm survival

Completed the frozen time-to-event analysis over the corrected full stock confluence population.

Event source:
- EQUITY_EVENTS_CHUNK1/2/3
- not the older partial EVENTS_ENRICHED event set.

Kaplan-Meier right-censored results show:
- lower confluence -> FAST_MID_ANALYTIC reclaim is much faster than leaving DOWN;
- upper confluence -> FAST_MID_ANALYTIC loss is much faster than leaving UP;
- formal state departure is slow in both directions.

Key Validation A timing:
- lower midpoint reclaim KM median: 7 bars;
- lower leave-DOWN KM median: 33 bars;
- upper midpoint loss KM median: 9 bars;
- upper leave-UP does not reach 50% by 40 bars.

This does not rescue midpoint crossing as a directional signal because the independent midpoint study already failed directional validation.

No time-stop and no new conditional threshold is promoted.

See:
- experiments/falsification_v1/TIME_TO_CONFIRM_SURVIVAL_STOCK_v1.md
- experiments/falsification_v1/TIME_TO_CONFIRM_SURVIVAL_STOCK_v1.json

Next frozen tasks remain:
- expanded-holdout Below-VAL interaction;
- HYS2 2x2 interaction/logistic regression;
- Volume/Breadth/VIX falsification;
- registered-family multiple-testing control after the family is complete.

## 2026-09-28 — Falsification v1 matching + independence audit

Match Quality Audit completed for coverage and missingness without changing the frozen matching variables.

Coverage:
- Validation A Upper: 392/392
- Validation A Lower: 325/325
- Validation B Upper: 39/46
- Validation B Lower: 12/20

Validation B missingness is systematic:
- all 7 unmatchable Upper events are PLD / Real Estate;
- Lower unmatchable events are concentrated in NFLX/MSFT and have materially different ATR% distribution.

Therefore:
- B Upper matched estimates exclude PLD / Real Estate;
- B Lower matched estimates are explicitly CONDITIONAL ON MATCHABILITY.

The v1 artifacts did not persist selected control identities and their matching covariates, so true event-vs-control pre/post SMD balance cannot be reconstructed from repository artifacts alone.
This is recorded as DATA NOT PERSISTED rather than regenerated post hoc from a new vendor.

Independence Audit:
- Upper combined: raw 438, frozen +/-2-day market waves 192;
- Lower combined: raw 345, frozen +/-2-day market waves 130.
- +/-5-day sensitivity collapses these to 72 and 60, showing wave-count sensitivity to linkage width.

Market-wave count is not called ESS.

Supplemental ICC-based ESS is reported separately and cluster bootstrap remains primary.

A Transition Path protocol was frozen before path outcomes are inspected:
- max 3 states / 2 transitions;
- max 60 bars;
- STALLED_60 separated from WINDOW_CENSORED;
- same-origin-state random-path baseline;
- no confluence/HYS/Regime rescue split.

Governance Amendment 2 also freezes:
- Upper general-top rule = REJECT;
- Lower incremental-buy rule = REJECT;
- no Regime mining or same-window repair;
- v1 can close with explicit DATA NOT AVAILABLE classifications;
- Hypothesis Ledger required before closure.

## 2026-09-28 — Falsification v1 state-density audit

Reconstructed daily UP/RANGE/DOWN occupancy directly from the persisted as-of transition sequence without re-downloading data or recalculating XMA.

Aggregate occupancy:
- Validation A: UP 51.0%, RANGE 25.8%, DOWN 23.2%
- Validation B: UP 59.9%, RANGE 26.4%, DOWN 13.7%

Strict-event density conditional on eligible state remains similar:
- Upper: 15.67 vs 15.49 events per 1000 UP bars
- Lower: 28.59 vs 29.50 events per 1000 DOWN bars

Therefore the A/B outcome disagreement is not explained simply by event rarity within its required state.

No Regime interpretation or trading threshold is introduced.

## 2026-09-28 — Falsification v1 transition-path study

Completed the preregistered 3-state / 2-transition path study with 60 bars per transition step.

Validation A:
- DOWN->RANGE anchors: n=284, wave n=104
  - target UP: 62.3%
  - conditional same-origin random controls after RANGE entry: 61.6%
- UP->RANGE anchors: n=338, wave n=143
  - target DOWN: 49.7%
  - conditional same-origin random controls after RANGE entry: 47.7%

The transition-path split is therefore close to the same-origin random-path baseline.

Decision:
common transition paths remain DESCRIPTIVE LIFECYCLE CONTEXT / NOT PROMOTED.

No deeper path subdivision is opened in v1.

## 2026-09-28 — Crypto robustness + auxiliary data closure

Crypto robustness is now reported separately from equities.

Key extreme:
- BNB upper-confluence event on 2021-02-01;
- +20-bar return about +473.6%;
- contributes about 39.8% of total absolute 20-bar movement in the Validation A Upper crypto set.

Therefore crypto reports now include median, 10% trimmed/winsorized mean, drop-top-1/2/5, event contribution, symbol decomposition and leave-one-symbol-out.

No crypto rule is promoted.

Auxiliary expanded-holdout audit:
the repository preserves Discovery/Exploratory HYS2/Volume/Profile/Breadth/VIX studies, but not the 2020-2024 + 2025H2 feature panel or full raw 39-symbol OHLCV needed to reproduce them without post-outcome vendor reconstruction.

Terminal v1 classifications:
- Below-VAL: INCONCLUSIVE / DATA NOT AVAILABLE
- HYS2 2x2/logistic: INCONCLUSIVE / DATA NOT AVAILABLE
- Volume interaction: INCONCLUSIVE / DATA NOT AVAILABLE
- Breadth interaction: INCONCLUSIVE / DATA NOT AVAILABLE
- VIX expanded dimensions: INCONCLUSIVE / DATA NOT AVAILABLE
- HYS2 fire-bottom/top: REDUNDANT WITHIN STRICT XMA EVENT SAMPLE only; global redundancy not established.

## 2026-09-28 — Falsification v1 CLOSED

Falsification v1 is formally CLOSED.

Final core classifications:
- Upper strict confluence => general top/decline rule: REJECT
- Lower strict confluence => incremental buy/rebound rule: REJECT
- common state transitions / midpoint / transition paths: OBSERVE / NOT PROMOTED
- Below-VAL / HYS2 interaction / Volume / Breadth / VIX expanded holdout: INCONCLUSIVE / DATA NOT AVAILABLE
- HYS2 fire-bottom/top: REDUNDANT WITHIN STRICT XMA EVENT SAMPLE only

Independence:
- Upper 438 episodes -> 192 frozen +/-2-day market-wave clusters
- Lower 345 -> 130

2026H1 remains sealed:
max persisted v1 event date = 2025-12-29.

No Regime rescue, threshold repair, matching expansion, or v2 hypothesis is opened automatically.

See:
- experiments/falsification_v1/HYPOTHESIS_LEDGER_v1.md
- experiments/falsification_v1/FALSIFICATION_V1_CLOSURE_REPORT.md

