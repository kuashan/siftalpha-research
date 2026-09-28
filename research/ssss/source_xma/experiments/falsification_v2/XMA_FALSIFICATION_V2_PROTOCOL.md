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

## 3.11 Return and risk-outcome conventions

Forward close return:

`RET_h(t) = CLOSE_{t+h}/CLOSE_t - 1`

where `t+h` means the h-th subsequent trading bar for that symbol.

H1 long-exposure adverse excursion is a **positive risk magnitude**:

`MAE10_ATR(t) = max(0, CLOSE_t - min(LOW_{t+1},...,LOW_{t+10})) / ATR14_t`

Larger is worse.

H2 closing-path maximum drawdown is a **positive risk magnitude**:

`MAX_DD10_ATR(t) = max_{t <= i < j <= t+10}(CLOSE_i - CLOSE_j) / ATR14_t`

The anchor close at t is part of the closing-price path. Intraday high/low drawdown is not substituted for H2.

F4/F5 10-bar event/control returns use `RET_10` exactly.

---

# 4. Episode and Event Construction

## 4.1 Trading-bar indexing and general Episode debounce

For each symbol, trading bars are assigned consecutive integer session indices.

For time-series hypotheses F2, F4, and F5:

- a hypothesis first defines a qualifying bar from its registered condition;
- Episode identity includes symbol, hypothesis id, and registered arm/condition identity;
- let successive qualifying session indices be `q_(j-1)` and `q_j`;
- if `q_j - q_(j-1) <= 3`, they belong to the same Episode;
- equivalently, at most 2 intervening non-qualifying trading bars may occur without opening a new Episode;
- Episode anchor = first qualifying bar in the Episode;
- after 3 consecutive non-qualifying trading bars following the last qualifying bar, the Episode is closed;
- only the anchor contributes one raw Episode to the primary analysis.

A later qualifying bar with session-index difference >=4 starts a new Episode.

No calendar-day distance substitutes for trading-bar distance.

No Episode is created or removed using future outcome information.

## 4.2 F1 Episode identity — continuous state run override

F1 does **not** use the 3-bar debounce.

For each symbol:
- a DOWN_STATE Episode is one maximal consecutive run of DOWN_STATE bars;
- an UP_STATE Episode is one maximal consecutive run of UP_STATE bars;
- any bar not in the current state ends that state Episode immediately;
- Episode anchor = first bar of the continuous state run.

This prevents a short state interruption from being silently merged into one risk-state Episode.

## 4.3 F2 Episode identity

H3:
- DOWN_STATE plus signed distance group.

H4:
- Extreme or Neutral distance group.

Episode identity includes the registered arm.

If an observation changes to the opposite registered arm, it is no longer qualifying for the prior arm. Re-entry follows the general Section 4.1 debounce rule.

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

Adjacent F3 snapshots are retained; temporal dependence is handled by market-wave clustering.

## 4.5 F4 Episode identity

Condition identity includes:
- XMA state;
- external field identity;
- `z > +1`.

Thus H7-H10 each create their own Episode set under Section 4.1.

## 4.6 F5 Episode identity

A/B event arms use the tested XMA state under:
- Risk-Off;
- Normal.

Risk-Off definition is Breadth or VIX according to H11-H14.

A and B are Episode anchors under Section 4.1.

C/D are controls, not additional raw Episodes.

## 4.7 Forward-window completeness

A primary outcome with horizon h requires exactly h subsequent trading bars for that symbol.

If the required forward horizon is incomplete:
- that Episode/snapshot is ineligible for that hypothesis primary statistic;
- it remains in an audit table with reason `INCOMPLETE_FORWARD_WINDOW`;
- no shorter horizon substitutes;
- no calendar-day approximation substitutes.

## 4.8 Horizon overlap

Distinct Episodes may have overlapping forward windows.

They are not removed solely because outcomes overlap.

Dependence is handled by:
- market-wave clustering;
- ESS;
- cluster bootstrap uncertainty.

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

For ESS only, define one scalar analysis value `Y_i` for each hypothesis primary unit:

- H1: Episode-level ATR-normalized MAE;
- H2: Episode-level ATR-normalized max drawdown;
- H3: Episode-level touch indicator 0/1;
- H4: Episode-level `min(first_touch_bar,20)`, with no-touch coded 20;
- H5: snapshot-level H5 rank-biserial correlation after the frozen within-snapshot adjustment;
- H6: snapshot-level H6 partial-Spearman correlation after the frozen within-snapshot adjustment;
- H7-H10: Episode-level matched excess;
- H11-H14: matched A/B-pair direction-normalized DiD contribution.

For F3, `n` in the ESS formula is therefore the number of eligible date×state snapshots, not the number of symbol rows inside those snapshots.

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

## 6.1 Matching covariates and distance

Exactly:
- dev20;
- prior20 return;
- ATR14/close.

For one event e and one covariate j, calculate from that event's eligible control pool:

`mu_j = mean(x_control,j)`

`s_j = sample_std(x_control,j, ddof=1)`

Then:

`z_event,j = (x_event,j-mu_j)/s_j`

`z_control,j = (x_control,j-mu_j)/s_j`

Distance:

`D(event,control) = sqrt(sum_j((z_event,j-z_control,j)^2))`

Rules:
- all 3 event covariates must be finite;
- all 3 control covariates must be finite;
- control must have a complete registered forward outcome;
- zero variance in any matching covariate makes the event `UNMATCHABLE`;
- no global normalization;
- no post-outcome caliper.

Tie-break:
1. lower distance;
2. earlier control trading date;
3. lexical symbol.

## 6.2 Control reuse and persistence

Within one event/source event:
- the selected 5 controls must be 5 distinct rows.

Across different events/pairs:
- a historical control row **may be reused**;
- this avoids order-dependent depletion of the control pool;
- reuse count is persisted and reported.

For every event and every selected control persist at minimum:
- hypothesis id;
- event id;
- event symbol/date;
- control symbol/date;
- event raw dev20/prior20/ATR14-close;
- control raw dev20/prior20/ATR14-close;
- eligible-pool means and sample stds for all 3 covariates;
- standardized event/control covariates;
- Euclidean distance;
- selected rank 1..5;
- eligible pool size;
- control forward return;
- event forward return;
- control reuse count;
- exclusion/eligibility audit reason for non-selected candidate rows in the pool audit artifact.

## 6.3 F4 controls

Eligible:
- same symbol;
- same exclusive XMA state;
- same frozen analysis window;
- tested external condition is false;
- outside ±20 trading bars, by session index, of every same-hypothesis Episode anchor;
- complete matching covariates;
- complete 10-bar forward return.

Select exactly 5 nearest controls under Section 6.1.

Fewer than 5:
event is `UNMATCHABLE`.

Event matched excess:

`ME10 = RET_10(event) - mean(RET_10(control_1..control_5))`

## 6.4 F5 four-cell design

A:
Risk-Off Episode in tested XMA state.

B:
Normal Episode in the same tested XMA state.

### A-to-B deterministic pairing

B is **not randomly sampled**.

For each hypothesis:
1. sort A Episodes by anchor trading date, then symbol;
2. for each A, eligible B must be:
   - same symbol;
   - same calendar quarter;
   - Normal environment;
   - same tested XMA state;
   - complete 10-bar forward outcome;
   - not previously assigned as B within that hypothesis;
3. choose B with minimum absolute trading-session distance from A;
4. tie -> earlier B date;
5. if still tied -> lexical event id.

If no unused eligible B exists:
A is `UNMATCHABLE_FOR_DID`.

There is therefore no B-sampling random seed.

### C and D controls

C controls A.
D controls B.

C/D eligibility:
- same symbol as source A/B;
- same Risk-Off/Normal environment as source;
- do not belong to the tested XMA state;
- outside ±20 trading bars, by session index, of every tested-state Episode anchor in the same hypothesis;
- complete matching covariates;
- complete 10-bar forward outcome;
- 5 nearest eligible controls under Section 6.1.

C/D controls may be reused across different A/B pairs, but the 5 controls within one source event must be distinct.

If either source event lacks 5 eligible controls:
the A/B pair is `UNMATCHABLE_FOR_DID`.

DOWN multiplier:
`s=+1`

UP multiplier:
`s=-1`

Pair contribution:

`d_i = s * ((RET_A - mean(RET_C1..5)) - (RET_B - mean(RET_D1..5)))`

F5 primary statistic:
mean of all matchable `d_i`.

---

# 7. Statistical Analysis Plan

No secondary outcome can replace a failed primary statistic.

All hypotheses first pass the raw/wave/symbol/ESS gates in Section 5.

## 7.1 F1

Model:
median quantile regression, tau=0.50.

H1 outcome:
`MAE10_ATR` from Section 3.11.

H2 outcome:
`MAX_DD10_ATR` from Section 3.11.

Predictors:
- intercept;
- `I(DOWN_STATE)`;
- SPY 10-bar forward return over the identical horizon;
- anchor ATR14/close.

UP_STATE is the reference.

Primary effect:
coefficient on `I(DOWN_STATE)`.

Uncertainty and raw p-value:
the common market-wave cluster bootstrap in Section 7.7.

## 7.2 H3

Primary:
`P(touch by 20 | distance<0) - P(touch by 20 | distance>=0)`.

Uncertainty and raw p-value:
Section 7.7 market-wave cluster bootstrap.

## 7.3 H4

Compute Kaplan-Meier curves separately for Extreme and Neutral.

Right-censor at 20.

Primary:
KM median first-touch waiting-time difference, `Extreme - Neutral`.

If the observed KM median is not estimable for either arm by horizon 20:
`INSUFFICIENT STATISTIC`.

No alternate survival statistic may replace it.

Bootstrap validity rule:
- each resample recomputes both KM medians and their difference;
- at least 9,500 of 10,000 resamples must yield an estimable difference;
- otherwise `INSUFFICIENT STATISTIC`.

## 7.4 F3 cross-sectional adjustment

F3 is conditioned exactly on `trading date × XMA state`.

Therefore SPY same-day return is constant within a snapshot and is controlled by exact date conditioning; it is recorded but no separate within-snapshot coefficient is estimated for this constant.

For each eligible date/state snapshot:

1. rank future 10-bar symbol return within the snapshot;
2. construct varying controls:
   - mapped sector ETF same-day return;
   - symbol ATR14/close;
3. if the within-snapshot control matrix is rank-deficient, mark that snapshot `CONTROL_MATRIX_RANK_DEFICIENT` and exclude it with audit record.

H5:
- residualize future-return rank on intercept + industry return + ATR14/close within each snapshot;
- pool eligible snapshot residuals with their frozen High/Low Sector-RS labels;
- primary statistic = rank-biserial correlation between High/Low membership and residualized future-return rank.

H6:
- rank Sector RS within the snapshot;
- residualize both Sector-RS rank and future-return rank on intercept + industry return + ATR14/close within each snapshot;
- pool the two residual series across eligible snapshots;
- primary statistic = Pearson correlation of pooled residual ranks, which is the frozen partial-Spearman implementation.

The exact date/state snapshot conditioning is the market-context control; no additional date fixed-effect column is added, avoiding collinearity with same-day SPY return.

Uncertainty and raw p-value:
Section 7.7, resampling whole F3 snapshots through their market-wave clusters and recomputing the full statistic.

## 7.5 F4

Primary:
mean event-level `ME10`.

Uncertainty and raw p-value:
Section 7.7 market-wave cluster bootstrap.

## 7.6 F5

Primary:
mean direction-normalized pair contribution `d_i`.

Each pair is assigned to the market wave of its A Risk-Off Episode.

Uncertainty and raw p-value:
Section 7.7, resampling A-wave clusters and carrying each selected A/B/C/D pair as an indivisible primary unit.

## 7.7 Common market-wave cluster bootstrap

Applies to H1-H14.

Resamples:
- B = 10,000.

Seed:
`2026092810 + H_number`.

Procedure:
1. determine the K market-wave clusters for the hypothesis;
2. sample K clusters with replacement;
3. include all primary units belonging to each sampled cluster;
4. recompute the **entire** primary estimator on that resample;
5. repeat B times.

No observation-level bootstrap is substituted.

No alternate seed may be selected.

Let:
- `T_obs` = observed primary statistic;
- `T_b` = valid bootstrap estimates.

Bootstrap standard error:

`SE_boot = sample_std(T_b, ddof=1)`

If `SE_boot = 0` or is non-finite:
`INSUFFICIENT STATISTIC`.

For H4, the 9,500-valid-replicate rule in Section 7.3 also applies.

95% descriptive interval:
2.5th and 97.5th percentiles of valid `T_b`.

Raw inferential p-value for BH:

`t_obs = T_obs / SE_boot`

Degrees of freedom:

`df = K - 1`

Using the Student-t distribution:
- registered positive one-sided: `p = 1 - F_t(t_obs; df)`;
- registered negative one-sided: `p = F_t(t_obs; df)`;
- two-sided: `p = 2 * min(F_t(t_obs;df), 1-F_t(t_obs;df))`.

This replaces the earlier draft's bootstrap-sign tail count. The bootstrap estimates cluster-robust uncertainty; the frozen t reference with `K-1` degrees of freedom supplies the raw p-value.

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
1. family membership and family size remain exactly as registered;
2. compute the frozen raw p-values for estimable members;
3. assign `p=1.0` to a registered member classified `INSUFFICIENT SAMPLE` or `INSUFFICIENT STATISTIC`;
4. apply BH to the full frozen family, including those p=1.0 placeholders.

Thus sample insufficiency never shrinks multiplicity after freeze.

A hypothesis may be SUPPORT only if all are true:
- sample floors including ESS pass;
- Guard gate for its family passes;
- effect direction matches Registry;
- absolute/directional effect reaches MDE;
- BH-adjusted q <=0.10.

Otherwise classification follows Section 15.

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

The official frozen stock/ETF Market Data Panel must cache all:
- 39 frozen equities;
- 11 frozen sector ETFs;
- SPY.

That is 51 stock/ETF series before Data Freeze acceptance.

The Breadth feature's per-date 32/39 rule is a **daily feature-eligibility rule**, not permission to omit 7 universe members from the frozen panel.

For every date on which Breadth is computed, persist the exact valid/missing member list so sector- or time-concentrated missingness is auditable.

VIX is frozen separately as the VIX Index source/snapshot and may not be replaced by a VIX futures ETF.

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

Order is mandatory.

## P0 — Market Data Panel readiness prerequisite

Before any full Protocol Freeze:

1. provider-agnostic cache/normalization code is committed;
2. provider-specific retrieval adapter is resumable and rate-limited;
3. raw snapshots are never silently overwritten;
4. normalized schema matches `SSSS_DATA_SOURCE_POLICY.md`;
5. manifest generation includes per-symbol raw/normalized hashes, row counts, first/last dates, duplicate count, and missing-OHLCV count;
6. development dry-run demonstrates cache reuse without refetching;
7. official freeze policy requires all 51 stock/ETF series, even though a single Breadth date may remain calculable with 32/39 equities.

Current infrastructure artifacts:
- `market_data_panel.py`
- `twelve_data_panel_fetch.py`

P0 is infrastructure readiness only. It is not Data Freeze.

## F0 — Protocol content lock

1. review this Protocol Draft;
2. resolve all implementation ambiguities and contradictions;
3. user/research owner explicitly approves the text for freezing;
4. commit the approved Protocol text;
5. record the Protocol commit SHA.

F0 locks Protocol content but **does not yet authorize the experiment** and is not the final Protocol Freeze.

## F1 — Data Freeze

1. choose the official provider under `SSSS_DATA_SOURCE_POLICY.md`;
2. retrieve and persist all required raw/calibration snapshots through the Market Data Panel;
3. require all 39 equities + 11 sector ETFs + SPY to exist in the frozen stock/ETF panel;
4. persist the authoritative VIX Index snapshot separately;
5. create SHA-256 manifest;
6. freeze adjustment, timezone, corporate-action, missing-bar, duplicate, and preprocessing semantics;
7. record per-date Breadth member availability;
8. commit `V2_DATA_FREEZE_MANIFEST.*`.

After F1:
data/vendor/preprocessing change follows Section 13.

## F2 — Code Freeze

1. run deterministic unit/integration tests on the frozen development/calibration data;
2. record commit/blob hashes for every code artifact in Section 11;
3. verify Market Data Panel cache reproducibility;
4. verify event/control/statistic reproduction from frozen inputs;
5. commit `V2_CODE_FREEZE_MANIFEST.*`.

## F3 — Full Protocol Freeze Acceptance

Create:
`V2_PROTOCOL_FREEZE_ACCEPTANCE.md`

It must contain:
- approved Protocol commit SHA;
- Data Freeze manifest SHA;
- Code Freeze manifest SHA;
- Registry SHA;
- FDR family manifest;
- Guard manifest;
- Market Data Panel manifest SHA;
- freeze timestamp;
- explicit user/research-owner approval reference.

**F3 is the moment called Protocol Freeze for experiment authorization.**

Only after F3 is committed is the scientific v2 experiment authorized to begin collecting its sealed window.

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
