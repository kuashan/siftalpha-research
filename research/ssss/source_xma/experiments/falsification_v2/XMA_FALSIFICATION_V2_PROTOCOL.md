# XMA Falsification v2 Protocol

Status: **FULL PROTOCOL DRAFT / NOT FROZEN / EXPERIMENT NOT AUTHORIZED**

Date: 2026-09-28

## 0. Acceptance standard

This Protocol is an execution contract.

Two independent implementers using:
- this Protocol;
- the frozen Registry;
- the frozen data snapshot;
- the frozen code commit;

must produce the same:
- feature values;
- Episode anchors;
- market-wave clusters;
- matched controls;
- primary statistics;
- Guard decisions;
- FDR decisions;
- hypothesis classifications.

If two reasonable implementations can differ, the Protocol is not ready to freeze.

## 0.1 Governing artifacts

This Protocol incorporates:

- `XMA_FALSIFICATION_V2_SCOPE.md`
- `XMA_FALSIFICATION_V2_SCOPE_AMENDMENT_v1.md`
- `V2_PROTOCOL_INPUT_CHECKLIST.md`
- `V2_PROTOCOL_DESIGN_ONEPAGER.md`
- `V2_PROTOCOL_DESIGN_ONEPAGER_AMENDMENT_v2.md`
- `V2_HYPOTHESIS_REGISTRY_DRAFT.md` at/after commit `96bb62e90ffdb4602f7fded476c4b6ae4aec6988`
- `V2_HYPOTHESIS_REGISTRY_REVIEW_v2.md`
- `V2_PROTOCOL_INPUT_GAP_AUDIT_v1.md`
- `V2_VARIABLE_DEFINITION_RESOLUTION_v1.md`
- `V2_BOUNDED_DEVELOPMENT_TESTING_AMENDMENT_v1.md`
- `V2_IMPLEMENTATION_SANITY_TEST_v1.md`
- `v2_feature_definitions.py` at/after commit `7fcce28ad3d307116171a09929d7deaeb66fbf32`

Any contradiction must be resolved before Protocol Freeze.

---

# 1. Scope and non-goals

v2 asks:

> Does XMA geometry provide incremental information when used as a condition/context variable?

v2 does not:
- re-test XMA as a universal standalone buy/sell signal;
- optimize rejected v1 upper/lower confluence rules;
- search for the regime where XMA performs best;
- add new candidate variables after seeing data;
- introduce position sizing, execution-cost optimization, portfolio optimization, or short-strategy design.

Formal hypothesis budget:
- F1 Risk: H1-H2
- F2 Lifecycle: H3-H4
- F3 Cross-sectional: H5-H6
- F4 Conditional: H7-H10
- F5 Risk-Off: H11-H14

Total: 14.

No H15 or reserve hypothesis exists.

---

# 2. Registered hypothesis manifest

The complete 14-field hypothesis definitions in `V2_HYPOTHESIS_REGISTRY_DRAFT.md` are normative.

Compact primary-statistic manifest:

| H | Family | Primary statistic | Horizon | Test |
| --- | --- | --- | --- | --- |
| H1 | F1 | DOWN coefficient in median quantile regression of ATR-normalized MAE | 10 | one-sided + |
| H2 | F1 | DOWN coefficient in median quantile regression of ATR-normalized max drawdown | 10 | one-sided + |
| H3 | F2 | midpoint-touch probability difference | 20 | two-sided |
| H4 | F2 | KM median first-touch waiting-time difference | 20 | two-sided |
| H5 | F3 | rank-biserial correlation, High vs Low Sector RS | 10 | one-sided + |
| H6 | F3 | partial Spearman correlation for continuous Sector RS | 10 | one-sided + |
| H7 | F4 | mean matched excess, Volatility × DOWN | 10 | one-sided + |
| H8 | F4 | mean matched excess, Volatility × UP | 10 | one-sided - |
| H9 | F4 | mean matched excess, Volume × DOWN | 10 | one-sided + |
| H10 | F4 | mean matched excess, Volume × UP | 10 | one-sided - |
| H11 | F5 | direction-normalized Breadth × DOWN DiD | 10 | one-sided - |
| H12 | F5 | direction-normalized Breadth × UP DiD | 10 | one-sided - |
| H13 | F5 | direction-normalized VIX × DOWN DiD | 10 | one-sided - |
| H14 | F5 | direction-normalized VIX × UP DiD | 10 | one-sided - |

No primary statistic may be replaced after Protocol Freeze.

---

# 3. Variable Specification

All definitions below are point-in-time.

## 3.1 ATR14

`TR_t = max(H_t-L_t, |H_t-C_{t-1}|, |L_t-C_{t-1}|)`

`ATR14_t = mean(TR_{t-13:t})`

Rules:
- arithmetic mean;
- 14 valid TR values;
- no Wilder RMA substitution.

## 3.2 FAST_MID_ANALYTIC

Source-XMA:

`A25 = XMA(XMA(H,25),25)`

`B25 = XMA(XMA(L,25),25)`

`FAST_MID_ANALYTIC = (A25+B25)/2`

XMA is the source-track centered/truncated XMA.

At date t:
- only data available through t may be supplied;
- record the first-observed right-edge value;
- future repainting may not rewrite prior feature snapshots.

This variable is not claimed to be the visually observed thin white line.

## 3.3 Distance to midpoint

`DIST_MID_ATR = (CLOSE - FAST_MID_ANALYTIC)/ATR14`

Midpoint touch:

`|CLOSE - FAST_MID_ANALYTIC| <= 0.25*ATR14`

## 3.4 H4 calibration quantiles

Per symbol.

Reference interval:
- 2020-01-02 through 2025-12-31 inclusive.

Quantiles:
- P10
- P40
- P60
- P90

Method:
- linear interpolation;
- >=252 valid observations;
- missing values excluded;
- boundary ties included.

Extreme:
`DIST <= P10 OR DIST >= P90`

Neutral:
`P40 <= DIST <= P60`

Quantiles are frozen calibration constants and never recomputed on sealed data.

## 3.5 Volatility z-score

`r_t = ln(C_t/C_{t-1})`

`RV20_t = sample_std(r_{t-19:t}, ddof=1)`

Reference moments use the prior 60 RV20 values, excluding current:

`VOL_Z_t = (RV20_t - mean(RV20_{t-60:t-1})) / sample_std(RV20_{t-60:t-1})`

Rules:
- no annualization;
- 60 valid prior RV20 values;
- reference std=0 => missing;
- no clipping/winsorization/fill.

F4 condition:
`VOL_Z > +1`.

## 3.6 Volume z-score

`DOLLAR_VOLUME_t = CLOSE_t * VOLUME_t`

`LDV_t = ln(1 + DOLLAR_VOLUME_t)`

`VOLUME_Z_t = (LDV_t - mean(LDV_{t-60:t-1})) / sample_std(LDV_{t-60:t-1})`

Rules:
- prior 60 observations exclude current;
- negative volume invalid;
- zero volume retained;
- no clipping/winsorization/fill.

F4 condition:
`VOLUME_Z > +1`.

## 3.7 Sector RS

Frozen sector ETF mapping:
- Technology XLK
- Communication Services XLC
- Consumer Discretionary XLY
- Consumer Staples XLP
- Health Care XLV
- Financials XLF
- Industrials XLI
- Energy XLE
- Materials XLB
- Utilities XLU
- Real Estate XLRE

Benchmark:
SPY.

`SECTOR_RET20 = ETF_t/ETF_{t-20}-1`

`SPY_RET20 = SPY_t/SPY_{t-20}-1`

`SECTOR_RS20 = SECTOR_RET20 - SPY_RET20`

Cross-sectional percentile rank each date:

`RS_PCT=(rank_average-1)/(N-1)`

Requirements:
- all 11 ETFs available for that F3 date;
- average rank for ties;
- weakest=0;
- strongest=1.

H5:
- Low <=0.20
- High >=0.80.

H6:
- continuous RS_PCT.

## 3.8 F3 controls

Market:
`SPY_RET_1D = SPY_t/SPY_{t-1}-1`

Industry:
`IND_RET_1D = mapped_sector_ETF_t/mapped_sector_ETF_{t-1}-1`

Volatility:
`VOL_LEVEL = ATR14/CLOSE`

No substitute benchmark/ETF after freeze.

## 3.9 Market Breadth

Universe:
the fixed 39 equities in `UNIVERSE_FROZEN_v1.md`.

For each member:

`ABOVE20_i,t = 1(CLOSE_i,t > SMA20_i,t)`

`BREADTH20_t = 100 * mean(ABOVE20_i,t)`

Rules:
- static 39-symbol membership;
- equal weight;
- at least 32/39 valid member values;
- otherwise missing;
- no fill.

Risk-Off threshold:

take the prior 20 **valid** Breadth observations, excluding current.

`BREADTH_Q10_t = Q10(prior 20 valid BREADTH20)`

Risk-Off:
`BREADTH20_t < BREADTH_Q10_t`

Normal:
`BREADTH20_t >= BREADTH_Q10_t`

Quantile method:
linear.

## 3.10 VIX

`VIX_CHG5_t = VIX_CLOSE_t/VIX_CLOSE_{t-5}-1`

Risk-Off:
`VIX_CHG5 > +0.20`

Normal:
`VIX_CHG5 <= +0.20`

No VIX futures ETF may substitute for the VIX Index.

---

# 4. Episode and Event Construction

## 4.1 General Episode rule

A hypothesis first defines a qualifying bar/observation from its registered condition.

For time-series hypotheses F1, F2, F4, F5:

- same symbol;
- same hypothesis condition identity;
- qualifying anchors separated by <=3 trading bars are linked into one Episode by transitive closure;
- Episode anchor = first qualifying bar in the linked Episode;
- Episode closes after 3 consecutive trading bars without a qualifying observation;
- only the anchor contributes one raw Episode to the primary analysis.

A new qualifying observation after >3 trading bars begins a new Episode.

No Episode is created or removed using future outcome information.

## 4.2 F1 Episode identity

Qualifying condition:
- UP_STATE for the UP arm;
- DOWN_STATE for the DOWN arm.

One continuous state run is therefore one Episode unless a state interruption creates a >3-bar separation under the rule above.

## 4.3 F2 Episode identity

H3:
- DOWN_STATE plus signed distance group.

H4:
- Extreme or Neutral distance group.

Episode identity includes the registered arm. Crossing from one registered arm to another ends the old arm's qualification.

## 4.4 F3 cross-sectional observation unit

F3 is inherently cross-sectional and does not use a same-symbol multi-bar Episode as its primary unit.

Primary F3 observation unit:

`trading date × XMA state cross-section`

Eligibility:
- >=20 eligible symbols in the state cross-section;
- required Sector RS and controls present.

Within a date/state snapshot:
- H5 compares High vs Low Sector RS members;
- H6 uses continuous Sector RS rank.

For Registry/sample-count terminology, one eligible date/state snapshot is one **F3 cross-sectional Episode**.

Adjacent F3 snapshots are not deleted; temporal dependence is handled by market-wave clustering.

## 4.5 F4 Episode identity

Condition identity includes:
- XMA state;
- external field identity;
- `z > +1`.

Thus H7-H10 each create their own Episode set.

## 4.6 F5 Episode identity

A/B event arms use the tested XMA state under:
- Risk-Off;
- Normal.

Risk-Off definition is Breadth or VIX according to H11-H14.

C/D are controls, not additional raw Episodes.

## 4.7 Forward-window completeness

A primary outcome requires all registered forward bars through its horizon.

If the required forward horizon is incomplete:
- that Episode/snapshot is ineligible for that hypothesis primary statistic;
- it remains in an audit table with reason `INCOMPLETE_FORWARD_WINDOW`;
- no shorter horizon substitutes.

## 4.8 Horizon overlap

Distinct Episodes may have overlapping forward windows.

They are not removed solely because outcomes overlap.

Dependence is handled by:
- market-wave clustering;
- ESS;
- cluster-robust uncertainty.

No post-outcome overlap filter is allowed.

---

# 5. Market-Wave Clustering and Sample Floors

## 5.1 Wave definition

For each hypothesis separately:

1. pool all primary Episode/snapshot anchor dates across symbols;
2. sort by trading date;
3. anchors whose dates differ by <=2 trading days are joined;
4. apply transitive closure.

The resulting component is one market wave.

This is the only primary market-wave definition.

No ±5-day replacement is allowed in the primary analysis.

## 5.2 Required floors

Every hypothesis must satisfy:
- raw primary units >=100;
- market waves >=30;
- symbols >=20;
- ESS >=100.

For H1/H2 and multi-arm tests:
each hypothesis-defining event arm must independently satisfy the raw/wave/symbol floors where the Registry explicitly requires per-arm floors.

For F5:
A and B event arms each satisfy the registered floors.

## 5.3 ESS — design-effect based

Let:
- n = raw primary units;
- K = market-wave clusters;
- m_k = size of cluster k;
- m_bar = n/K;
- CV_m = sample_sd(m_k)/m_bar.

For ESS only, define an event-level analysis value `Y_i`:

- H1: ATR-normalized MAE;
- H2: ATR-normalized max drawdown;
- H3: touch indicator 0/1;
- H4: `min(first_touch_bar,20)`, with no-touch coded 20;
- H5: adjusted 10-bar future-return rank;
- H6: 10-bar future-return rank;
- H7-H10: event-level matched excess;
- H11-H14: event-pair direction-normalized DiD contribution.

Estimate one-way ICC using ANOVA:

`MS_B = sum_k m_k*(mean_k-mean_all)^2/(K-1)`

`MS_W = sum_k sum_i (Y_ik-mean_k)^2/(n-K)`

For unequal cluster sizes:

`m0 = (n - sum_k(m_k^2)/n)/(K-1)`

`rho_raw = (MS_B-MS_W)/(MS_B+(m0-1)*MS_W)`

`rho = min(1,max(0,rho_raw))`

Design effect:

`DEFF = max(1, 1 + (((1+CV_m^2)*m_bar)-1)*rho)`

Effective sample size:

`ESS = n/DEFF`

If ESS <100:
`INSUFFICIENT SAMPLE`

No relaxation of the ±2-day wave rule is permitted.

---

# 6. Matched-Control Pipeline

## 6.1 Distance covariates

Exactly:
- dev20;
- prior20 return;
- ATR14/close.

Standardization:
- for each event, standardize each matching covariate using mean and sample std calculated from that event's eligible control pool;
- zero-variance covariate in the eligible pool makes the event unmatchable;
- no global normalization.

Distance:
standardized Euclidean distance.

Tie-break:
1. lower distance;
2. earlier control date;
3. lexical symbol, although same-symbol rules normally make symbol tie-break unnecessary.

Persist every selected control row and pool metadata.

## 6.2 F4 controls

Eligible:
- same symbol;
- same exclusive XMA state;
- same analysis window;
- tested external condition is false;
- not within ±20 trading bars of a same-hypothesis event.

Select exactly 5 nearest controls.

Fewer than 5:
event is `UNMATCHABLE`.

Event matched excess:

`R_event,10 - mean(R_control1..5,10)`

## 6.3 F5 four-cell design

A:
Risk-Off event in tested XMA state.

B:
Normal event in same tested XMA state.

B-to-A pairing:
- same symbol;
- same calendar quarter;
- nearest Episode-anchor date;
- tie -> earlier B date;
- one B may be used only once within a hypothesis;
- matching is deterministic in chronological A order.

If no unused B exists:
A is primary-statistic unmatchable.

C controls A.
D controls B.

C/D:
- same symbol as source event;
- same Risk-Off/Normal environment as source;
- do not belong to tested XMA state;
- outside ±20 bars of tested-state Episodes;
- 5 nearest by the frozen distance covariates.

DOWN multiplier:
`s=+1`

UP multiplier:
`s=-1`

Pair contribution:

`d_i=s*((A-C)-(B-D))`

F5 primary statistic:
mean of `d_i`.

---

# 7. Statistical Analysis Plan

No secondary outcome can replace a failed primary statistic.

## 7.1 F1

Model:
median quantile regression, tau=0.50.

H1 outcome:
ATR-normalized MAE.

H2 outcome:
ATR-normalized maximum drawdown.

Predictors:
- intercept;
- `I(DOWN_STATE)`;
- SPY same-horizon 10-bar return;
- anchor ATR14/close.

Primary effect:
coefficient on `I(DOWN_STATE)`.

Uncertainty:
CR2 cluster-robust covariance by market wave.

Raw p-value:
coefficient t/Wald test using CR2 small-sample degrees of freedom.

## 7.2 H3

Primary:
difference in midpoint-touch probability.

Uncertainty:
market-wave cluster bootstrap.

## 7.3 H4

Compute Kaplan-Meier curves separately for Extreme and Neutral.

Right-censor at 20.

Primary:
KM median first-touch wait difference, Extreme-Neutral.

If the KM median is not estimable for either arm by horizon 20:
`INSUFFICIENT STATISTIC`

No alternate survival statistic may replace it.

Uncertainty:
market-wave cluster bootstrap.

## 7.4 F3 controls and partial ranking

H5/H6 use pooled eligible symbol-date observations from F3 snapshots.

Create control matrix:
- SPY_RET_1D;
- IND_RET_1D;
- ATR14/close;
- date fixed effects;
- XMA-state fixed effects.

H5:
- residualize future 10-bar return rank on control matrix;
- rank-biserial correlation between High/Low RS membership and residualized rank.

H6:
- rank Sector RS and future 10-bar return;
- residualize both rank variables on the control matrix;
- Pearson correlation of the two residual series = frozen partial Spearman statistic.

Uncertainty:
market-wave cluster bootstrap over F3 date/state snapshots.

## 7.5 F4

Primary:
mean event-level 10-bar matched excess.

Uncertainty:
market-wave cluster bootstrap.

## 7.6 F5

Primary:
mean direction-normalized pair contribution `d_i`.

Each pair is assigned to the market wave of its A Risk-Off Episode for the primary cluster analysis.

Uncertainty:
market-wave cluster bootstrap of A-wave clusters.

## 7.7 Cluster bootstrap

For H3-H14 except F1 CR2:

- B = 10,000 resamples;
- sample market-wave clusters with replacement;
- include all primary units belonging to sampled clusters;
- recompute the full primary statistic.

Seeds:
`2026092810 + H_number`

No alternate seed may be selected.

95% interval:
bootstrap percentile interval.

Raw bootstrap tail probability:
- positive one-sided: `(1 + count(T_b <= 0))/(B+1)`
- negative one-sided: `(1 + count(T_b >= 0))/(B+1)`
- two-sided: `min(1, 2*min(P_b(T_b<=0), P_b(T_b>=0)))`
with +1 finite-sample correction in each empirical tail count.

These raw tail probabilities are the frozen p-like inputs to BH for non-F1 families.

---

# 8. Multiple Testing / FDR

Scientific hypotheses only.

Guard controls never enter BH.

Correction:
Benjamini-Hochberg.

Target:
`q = 0.10`

Families:
- F1: H1,H2
- F2: H3,H4
- F3: H5,H6
- F4: H7,H8,H9,H10
- F5: H11,H12,H13,H14

No cross-family pooling.

For each family:
1. compute frozen raw p/p-like values;
2. apply BH to all registered and testable members;
3. a member that is `INSUFFICIENT SAMPLE` or `INSUFFICIENT STATISTIC` is not treated as evidence; it cannot be promoted.

A hypothesis may be SUPPORT only if all are true:
- sample floors including ESS pass;
- Guard gate for its family passes;
- effect direction matches Registry;
- absolute/directional effect reaches MDE;
- BH-adjusted q <=0.10.

Otherwise classification follows Section 14.

---

# 9. Guard / Negative-Control Protocol

Guards are independent methodological gates.

They do not test whether XMA is scientifically useful.

They test whether the pipeline produces a material effect after the registered information has been removed.

Generation rules and seeds:
G-F1..G-F5 are frozen in the Registry.

Guard p-values:
- may be reported diagnostically;
- never enter BH.

Guard PASS:
- registered sample floor is satisfied; and
- `abs(guard_effect) < linked MDE`.

Guard INSUFFICIENT:
sample floor fails.

Guard FAIL:
`abs(guard_effect) >= linked MDE`.

If Guard is FAIL or INSUFFICIENT:
the entire linked family is:
`NOT ELIGIBLE FOR PROMOTION`

even if scientific hypotheses meet BH/MDE criteria.

No seed rerolling.

---

# 10. Data Specification and Data Freeze Requirements

Before Protocol Freeze becomes executable, create a Data Freeze manifest.

It must record:

- provider name;
- endpoint/product;
- retrieval date;
- timezone/calendar convention;
- raw date range;
- universe;
- raw-file hashes;
- adjustment semantics;
- split/dividend treatment;
- missing-bar rule;
- duplicate rule;
- OHLCV schema;
- SPY source;
- sector ETF sources;
- VIX source;
- breadth member sources;
- H4 calibration snapshot hashes.

Required raw data must be persisted, not merely retrievable by API.

The development Twelve Data data used during sanity testing is not automatically the final frozen provider.

No vendor may be changed after outcome inspection.

---

# 11. Code Freeze Requirements

Before experiment authorization, freeze and record commit hashes for:

- Source-XMA point-in-time implementation;
- XMA state classification;
- Episode builder;
- market-wave clustering;
- `v2_feature_definitions.py`;
- matched-control builder;
- F5 pair builder;
- ESS implementation;
- statistical tests/bootstrap;
- BH-FDR implementation;
- Guard generation;
- result-classification code.

A text-only Protocol is not sufficient.

---

# 12. Freeze Procedure

Freeze is a process, not one commit.

Order is mandatory:

## F0 — Protocol approval

1. Protocol Draft review.
2. Resolve all contradictions.
3. user explicitly approves freeze.
4. commit final Protocol.
5. record Protocol commit SHA.

Until F0 completes:
Protocol wording may change through reviewed commits.

## F1 — Data Freeze

1. retrieve all required non-sealed historical/calibration data;
2. persist raw snapshots;
3. create SHA-256 manifest;
4. freeze preprocessing/data-source specification;
5. commit Data Freeze manifest.

After F1:
data/vendor/preprocessing change requires Amendment or restart according to Section 13.

## F2 — Code Freeze

1. run deterministic tests;
2. record all code commit hashes;
3. commit Code Freeze manifest;
4. require clean reproducibility on frozen historical/dev data.

## F3 — Freeze Acceptance

Create:
`V2_PROTOCOL_FREEZE_ACCEPTANCE.md`

It must contain:
- Protocol SHA;
- Data manifest SHA;
- code commit/hash manifest;
- Registry SHA;
- FDR manifest;
- Guard manifest;
- freeze timestamp;
- explicit user approval reference.

Only after F3 is committed is the experiment design frozen.

## F4 — Sealed Window Start

The sealed window starts on the first eligible trading session **after F3**.

No earlier date can be retroactively declared sealed.

---

# 13. Amendment Procedure

Every post-freeze change is classified before implementation.

## 13.1 Clarification Amendment

Allowed only if:
- no computed value changes;
- no event membership changes;
- no control selection changes;
- no statistic/p-value changes.

Examples:
- typo;
- documentation wording;
- non-semantic code comment.

Sealed-window start unchanged.

## 13.2 Reproducibility Amendment

For a defect that changes implementation but not the scientific definition.

Requirements:
- document bug;
- document affected artifacts;
- regenerate hashes;
- re-run development reproducibility;
- re-freeze affected code/data layers.

If the bug affected any sealed-window value already computed or inspected:
the current sealed experiment is invalid and must restart with a new future sealed window.

## 13.3 Scientific-definition change

Includes any change to:
- candidate variable formula;
- threshold;
- hypothesis condition;
- horizon;
- primary statistic;
- direction;
- MDE;
- sample floor;
- Episode construction;
- matching covariates/eligibility;
- wave definition;
- FDR family/method;
- Guard generation rule.

This is not a repair of the same experiment.

Required action:
- invalidate current frozen experiment;
- issue formal Amendment describing why;
- freeze a new Protocol version;
- use a new future sealed window.

No already-opened sealed data may be reused as untouched validation.

## 13.4 Hypothesis deletion

A hypothesis may be deleted before F3 Freeze Acceptance only with explicit reason.

No replacement hypothesis may be added.

After F3, deletion because of observed result is prohibited.

---

# 14. Sealed Window

The sealed window is not named in this Draft.

Start:
first eligible trading session after F3 Freeze Acceptance.

Minimum duration:
12 calendar months.

Unlock occurs on the first date when all frozen conditions simultaneously hold for every testable registered hypothesis:

- duration >=12 months;
- raw floor passes;
- wave floor passes;
- symbol floor passes;
- ESS >=100;
- F5 A/B floors pass where applicable.

If calendar duration is satisfied but any hypothesis remains below floor:
continue waiting.

Prohibited:
- lowering floors;
- redefining start;
- substituting sensitivity data;
- peeking and resealing.

The sealed window opens once.

After unlock it can never be called untouched again.

---

# 15. Decision and Failure Modes

Each H receives one terminal classification after the frozen test.

## SUPPORT

All required:
- sample/ESS pass;
- Guard pass;
- correct direction;
- effect >= MDE;
- BH q<=0.10.

## REJECT

Use when:
- primary statistic is testable;
- sample floor passes;
- registered scientific proposition does not meet SUPPORT.

This includes wrong direction, sub-MDE effect, or BH failure.

## INSUFFICIENT SAMPLE

Use when:
- raw/wave/symbol/ESS floor fails.

No lower standard or alternate window.

## INSUFFICIENT STATISTIC

Use when the frozen primary statistic cannot be estimated despite otherwise eligible data, e.g. H4 median not reached.

No secondary statistic may replace it.

## NOT ELIGIBLE FOR PROMOTION — GUARD

Family Guard fails or is insufficient.

Scientific estimates are still archived, but no member of the family is promoted.

## DATA INTEGRITY FAILURE

Examples:
- frozen raw hash mismatch;
- undocumented vendor revision;
- missing frozen snapshot;
- impossible reconstruction.

Stop the affected analysis.

## CODE INTEGRITY FAILURE

Frozen code hash mismatch or post-freeze bug.

Follow Section 13.

## PROTOCOL VIOLATION

Any unregistered:
- threshold change;
- variable replacement;
- hypothesis addition;
- outcome-driven sample rule.

The affected frozen experiment is invalid.

## All v2 hypotheses rejected

XMA geometry v2 research closes.

No automatic v3.

Future SiftAlpha research may start a different signal family only through a new Discovery → Validation → Falsification lifecycle.

---

# 16. Reporting Requirements

For every hypothesis persist:

- hypothesis id;
- frozen condition;
- raw n;
- market-wave count;
- symbol count;
- ICC;
- DEFF;
- ESS;
- primary estimate;
- 95% interval;
- raw p/p-like value;
- BH q;
- MDE check;
- direction check;
- Guard status;
- final classification.

Persist event/control rows sufficient to reproduce every statistic.

Matched-control outputs must include identities and dates.

No report may show only aggregate means without underlying reproducibility artifacts.

---

# 17. Trading-Service Boundary

v2 findings are research evidence, not automatic order rules.

A validated result may become a candidate input to:

- F1 -> risk admission;
- F2 -> position lifecycle;
- F3 -> cross-sectional ranking;
- F4 -> conditional-information gate;
- F5 -> risk-off suppression.

Before real capital:

1. execution infrastructure gate;
2. paper-trading validation gate;
3. real-capital deployment gate.

A rejected or unvalidated hypothesis must not enter strategy logic.

---

# 18. Current Authorization

Protocol Draft:
**CREATED**

Protocol Freeze:
**NOT AUTHORIZED YET**

Data Freeze:
**NOT COMPLETED**

Code Freeze:
**NOT COMPLETED**

Sealed Window:
**NOT STARTED**

Scientific v2 hypothesis testing:
**NOT AUTHORIZED**

Development implementation testing on already contaminated/non-sealed data:
**AUTHORIZED ONLY UNDER V2_BOUNDED_DEVELOPMENT_TESTING_AMENDMENT_v1**
