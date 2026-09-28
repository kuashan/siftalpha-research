# XMA Falsification v2 — Protocol Input Gap Audit v1

Status: **AUDIT COMPLETE / DEFINITION GAPS FOUND / PROTOCOL DRAFT BLOCKED**

Date: 2026-09-28

Experiment authorization: **NOT AUTHORIZED**  
v2 outcome-data access: **NOT AUTHORIZED**  
Sealed window: **NOT SELECTED**

## 0. Purpose and hard boundary

This audit asks one question:

> Can two independent implementers derive the same v2 variables and shared controls from the currently frozen repository definitions?

This audit may:
- identify an existing unique definition;
- canonicalize a definition already uniquely implied by frozen artifacts;
- identify a missing definition that must be resolved before Protocol drafting.

This audit may not:
- add a candidate variable;
- replace a candidate variable;
- add or restructure H1-H14;
- change a horizon, outcome, primary statistic, direction, MDE, sample floor, or FDR family;
- inspect v2 outcomes;
- select a definition because it produces a preferred result.

If a candidate variable cannot be given a unique point-in-time definition before Protocol freeze, classify it:

`INSUFFICIENT DEFINITION`

and the linked formal hypothesis is **REJECTED / NOT ADMITTED TO THE FROZEN PROTOCOL**. It may not be replaced by another variable.

A definition gap that is technically resolvable before Protocol freeze is classified:

`RESOLUTION REQUIRED BEFORE PROTOCOL`

This is not permission to inspect outcomes. The resolution must be committed and reviewed before Protocol drafting.

---

# 1. Sources inspected

Definition/governance artifacts only; no v2 outcome file was opened.

Primary sources:

- `models/ssss_current.py`
- `models/ssss_core_v0_1.py`
- `research/ssss/source_xma/CANONICAL_WEIGHTED_CHANNEL_v1.md`
- `research/ssss/source_xma/XMA_VISUAL_FORMULA_MAPPING_CANONICAL_v1.md`
- `research/ssss/source_xma/XMA_FULL_RESEARCH_SPECIFICATION.md`
- `research/ssss/source_xma/experiments/falsification_v1/PROTOCOL_FROZEN_BEFORE_VALIDATION.md`
- `research/ssss/source_xma/experiments/falsification_v1/UNIVERSE_FROZEN_v1.md`
- `research/ssss/source_xma/experiments/falsification_v1/MATCH_QUALITY_AUDIT_v1.md`
- `research/ssss/source_xma/experiments/falsification_v1/AUXILIARY_DATA_AVAILABILITY_AUDIT_v1.md`
- `research/ssss/source_xma/experiments/canonical_geometry_2025_01_06/ORTHOGONAL_CONFIRMATION_PROTOCOL.md`
- `research/ssss/source_xma/experiments/orthogonal_2025_03_06/PROTOCOL_FROZEN_BEFORE_RUN.md`
- `research/ssss/source_xma/experiments/orthogonal_2025_03_06/PROTOCOL_AMENDMENT_BEFORE_RUN.md`
- v2 One-Pager / Amendment v2 / Registry Draft / Registry Review.

---

# 2. Candidate-variable audit

## 2.1 Volatility z-score — H7 / H8

**Registry identity:** Volatility z-score  
**Family:** F4 Conditional  
**Status:** **RESOLUTION REQUIRED BEFORE PROTOCOL**

What is already frozen:
- the variable must represent external realized-volatility information rather than XMA geometry;
- condition threshold is `z > +1`;
- H7 is DOWN_STATE and H8 is UP_STATE;
- F4 outcome/primary statistic/horizon are already frozen.

What is NOT uniquely defined in the repository:
- realized-volatility input formula;
- simple return versus log return;
- realized-volatility lookback;
- z-score reference lookback;
- population versus sample standard deviation;
- annualized versus non-annualized scale;
- whether the current bar participates in the normalization window;
- warm-up/minimum-period rule;
- missing-value rule;
- zero-standard-deviation rule;
- outlier/winsorization rule.

Important constraint:
- ATR-based volatility may not be silently substituted merely because ATR14 already exists; the One-Pager explicitly requires the volatility candidate to address ATR/XMA collinearity.

**Protocol admission consequence:** H7/H8 remain blocked until one exact point-in-time formula is committed and reviewed. If no unique definition is frozen, H7/H8 become `INSUFFICIENT DEFINITION -> REJECT / NOT ADMITTED`.

---

## 2.2 Volume z-score — H9 / H10

**Registry identity:** Volume z-score  
**Family:** F4 Conditional  
**Status:** **RESOLUTION REQUIRED BEFORE PROTOCOL**

Historical definitions found:
- `RVOL20 = volume / MA20(volume)`;
- 5-bar signed-volume balance;
- accumulation/distribution rules.

These are historical Volume Structure variables. They are **not** the registered v2 `Volume z-score`.

Not uniquely defined:
- share volume versus dollar volume;
- raw volume versus log volume;
- signed versus unsigned volume;
- z-score lookback;
- mean/std convention;
- current-bar inclusion;
- warm-up/minimum periods;
- missing values;
- zero-volume handling;
- zero-standard-deviation handling;
- corporate-action treatment if raw share volume is used;
- outlier/winsorization rule.

**Protocol admission consequence:** H9/H10 remain blocked until one exact point-in-time Volume z-score definition is committed and reviewed. Historical RVOL20 or signed-volume rules may not silently replace the registered variable. Failure to freeze one definition => `INSUFFICIENT DEFINITION -> REJECT / NOT ADMITTED`.

---

## 2.3 Sector relative strength — H5 / H6

**Registry identity:** Sector relative strength  
**Family:** F3 Cross-sectional  
**Status:** **RESOLUTION REQUIRED BEFORE PROTOCOL**

Existing reusable frozen information:
- equity sector categories exist;
- frozen sector ETF mapping exists:
  - Technology -> XLK
  - Communication Services -> XLC
  - Consumer Discretionary -> XLY
  - Consumer Staples -> XLP
  - Health Care -> XLV
  - Financials -> XLF
  - Industrials -> XLI
  - Energy -> XLE
  - Materials -> XLB
  - Utilities -> XLU
  - Real Estate -> XLRE
- v1 sector-relative return used the mapped ETF and prohibited post-outcome substitute ETFs.

What is NOT uniquely defined:
- whether Sector RS is ETF-vs-SPY relative return, sector-vs-stock relative return, price ratio, or another construction;
- lookback;
- simple versus log-return form;
- benchmark;
- normalization/ranking rule;
- treatment of an unavailable sector ETF date;
- whether classification is explicitly GICS or only the repository's frozen broad-sector mapping.

No artifact currently supports calling the mapping GICS.

**Protocol admission consequence:** H5/H6 are blocked until a single formula, lookback, benchmark, and ranking convention are frozen. Failure => `INSUFFICIENT DEFINITION -> REJECT / NOT ADMITTED`.

---

## 2.4 Market Breadth level — H11 / H12

**Registry identity:** Market Breadth level  
**Family:** F5 Risk-Off  
**Status:** **RESOLUTION REQUIRED BEFORE PROTOCOL**

Historical breadth implementations found:
- percent advancing;
- percent above MA20;
- percent with positive 5-day return;
- historical 100-name proxy subsequently amended before that historical run to a frozen 15-name proxy;
- separate crypto breadth definition.

The v2 Registry additionally freezes the Risk-Off classifier form:
- Breadth level below its own trailing 20-trading-day 10th percentile.

What is NOT uniquely defined:
- which one scalar breadth series is `Market Breadth level`;
- breadth universe for v2;
- equal-weight versus another aggregation;
- constituent eligibility on a date;
- missing constituent rule;
- point-in-time universe membership rule;
- percentile interpolation/tie method;
- whether the current date is included in the trailing percentile window;
- minimum history required.

The historical 15-name proxy cannot silently become the v2 Breadth variable because that choice was made for an older exploratory run under a tool-call constraint, not for this Registry.

**Protocol admission consequence:** H11/H12 are blocked until one scalar breadth series and universe/missing/percentile implementation are frozen. Failure => `INSUFFICIENT DEFINITION -> REJECT / NOT ADMITTED`.

---

## 2.5 VIX change — H13 / H14

**Registry identity:** VIX 5-trading-day percentage change  
**Family:** F5 Risk-Off  
**Status:** **DEFINITION CAN BE CANONICALIZED WITHOUT NEW RESEARCH CHOICE**

The Registry already fixes:
- source field class: VIX close series;
- lookback: 5 trading bars;
- Risk-Off threshold: > +20%.

Canonical implementation for Protocol:
- `VIX_CHG5_t = VIX_CLOSE_t / VIX_CLOSE_{t-5} - 1`;
- Risk-Off if `VIX_CHG5_t > 0.20`;
- Normal if `VIX_CHG5_t <= 0.20`;
- no forward-fill across a missing required endpoint;
- if either endpoint is missing, the date is ineligible for H13/H14;
- no interpolation;
- no alternative volatility index substitution.

This formula does not change the registered variable, threshold, horizon, or hypothesis structure.

**Admission status:** H13/H14 variable definition is **READY FOR PROTOCOL**, subject to freezing the exact VIX data source/version in the later Data Freeze.

---

## 2.6 Distance to midpoint — H3 / H4

**Registry identity:** signed distance to midpoint  
**Family:** F2 Lifecycle  
**Status:** **PARTIALLY READY; H4 REFERENCE-POPULATION GAP REMAINS**

Authoritative analytic midpoint already exists:

`FAST_MID_ANALYTIC = GZB18 = (ZK1 + ZD1) / 2`

Important naming rule:
- v2 must call this `FAST_MID_ANALYTIC`;
- it must not claim that this is the visually observed thin white rail, because that visual mapping remains unresolved.

Canonical signed distance:

`DIST_MID_ATR_t = (CLOSE_t - FAST_MID_ANALYTIC_t) / ATR14_t`

H3 midpoint touch is already frozen:

`abs(CLOSE_t - FAST_MID_ANALYTIC_t) <= 0.25 * ATR14_t`

H3 is therefore definition-ready.

H4 still has one unresolved implementation degree of freedom:
- the exact historical reference interval used to estimate each symbol's P10/P40/P60/P90 thresholds.

The Registry says symbol-level quantiles from a frozen historical/pre-sealed dataset, but the exact reference dates are not yet frozen.

Additional H4 items that must be fixed with that reference interval:
- quantile estimator/interpolation method;
- minimum observations;
- tie/boundary inclusion;
- missing-value exclusion.

**Admission status:** H3 definition is **READY FOR PROTOCOL**. H4 remains blocked until its quantile reference population and estimator are frozen.

---

# 3. Shared-control and base-variable audit

## 3.1 ATR14

**Status:** READY

Repository code defines True Range as:

`TR_t = max(H_t-L_t, abs(H_t-C_{t-1}), abs(L_t-C_{t-1}))`

and:

`ATR14_t = arithmetic rolling mean(TR, 14)`

with 14 valid periods required.

Protocol must reference the frozen implementation/code hash; it must not substitute Wilder RMA unless an Amendment explicitly changes the variable.

---

## 3.2 dev20

**Status:** READY

Frozen formula:

`dev20_t = CLOSE_t / MA20(CLOSE)_t - 1`

Protocol still must freeze the precise MA20 implementation as arithmetic rolling mean with 20 valid closes.

---

## 3.3 prior20 return

**Status:** CANONICALIZATION REQUIRED, NO RESEARCH CHOICE NEEDED

v1 freezes the variable as `prior 20-bar return` but does not spell the arithmetic formula in the protocol text.

Canonical point-in-time implementation for the v2 matching contract:

`PRIOR20_t = CLOSE_t / CLOSE_{t-20} - 1`

No annualization and no log conversion.

If either endpoint is missing, the matching covariate is missing and the row is not eligible for a complete three-variable match.

---

## 3.4 same-day market return — F3 control

**Status:** CANONICALIZATION REQUIRED, LOW AMBIGUITY

The repository already uses SPY as the US-equity market benchmark.

Canonical daily control:

`MKT_RET_1D_t = SPY_CLOSE_t / SPY_CLOSE_{t-1} - 1`

No substitute benchmark is allowed after freeze.

Exact SPY source/version remains a Data Freeze item.

---

## 3.5 same-day industry return — F3 control

**Status:** CANONICALIZATION REQUIRED, LOW AMBIGUITY**

Use the already frozen sector ETF mapping listed in Section 2.3.

Canonical daily control:

`IND_RET_1D_t = SECTOR_ETF_CLOSE_t / SECTOR_ETF_CLOSE_{t-1} - 1`

Missing rule:
- if either mapped ETF endpoint is unavailable, the observation is ineligible for an F3 primary statistic requiring this control;
- no substitute ETF may be selected.

The Protocol must call this the repository's frozen broad-sector ETF mapping unless an authoritative classification artifact establishes a stricter taxonomy.

---

## 3.6 same-day volatility level — F3 control

**Status:** **RESOLUTION REQUIRED BEFORE PROTOCOL**

The Registry requires this control but does not define it.

Possible repository variables include:
- `ATR14/close`;
- realized-return volatility;
- other historical volatility contexts.

Selecting among them changes the F3 adjustment model.

Therefore this audit does not choose one silently.

H5/H6 cannot enter the frozen Protocol until this control is uniquely defined.

---

# 4. Definition-code audit

The current repository contains authoritative implementations for core XMA/ATR logic, but it does **not** yet contain frozen v2 calculation code for:

- Volatility z-score;
- Volume z-score;
- Sector RS;
- v2 Market Breadth;
- F3 same-day volatility control;
- H4 symbol-level quantile thresholds.

Before Protocol freeze, each admitted variable must have:
1. exact formula in text;
2. point-in-time calculation rule;
3. missing/warm-up/outlier rule;
4. executable implementation;
5. implementation commit hash recorded in the Protocol/Code Freeze manifest.

Text definition without frozen code is insufficient for final Protocol Freeze.

---

# 5. Gap matrix

| Item | Linked H | Status before Protocol |
| --- | --- | --- |
| ATR14 | H1-H4 / controls | READY |
| FAST_MID_ANALYTIC | H3-H4 | READY |
| H4 quantile reference population | H4 | RESOLUTION REQUIRED |
| dev20 | H7-H14 controls | READY |
| prior20 | H7-H14 controls | CANONICALIZE |
| SPY same-day return | H1-H2 / F3 | CANONICALIZE |
| sector ETF same-day return | H5-H6 | CANONICALIZE |
| F3 same-day volatility level | H5-H6 | RESOLUTION REQUIRED |
| Volatility z-score | H7-H8 | RESOLUTION REQUIRED |
| Volume z-score | H9-H10 | RESOLUTION REQUIRED |
| Sector RS | H5-H6 | RESOLUTION REQUIRED |
| Market Breadth level | H11-H12 | RESOLUTION REQUIRED |
| VIX 5-day change | H13-H14 | READY FOR PROTOCOL |

---

# 6. Hypothesis admission status after audit

No hypothesis is deleted or rewritten by this audit.

Definition readiness:

- H1-H2: base variables largely defined; statistical implementation still belongs to Protocol Statistical Analysis Plan.
- H3: variable definition ready.
- H4: **BLOCKED** by symbol-level quantile reference-population definition.
- H5-H6: **BLOCKED** by Sector RS and same-day volatility-control definitions.
- H7-H8: **BLOCKED** by Volatility z-score definition.
- H9-H10: **BLOCKED** by Volume z-score definition.
- H11-H12: **BLOCKED** by Market Breadth scalar/universe definition.
- H13-H14: VIX variable definition ready; F5 matching/statistical machinery remains a Protocol item.

A BLOCKED hypothesis is not yet REJECTED because its named variable is technically definable without changing the Registry. It must be resolved **before Protocol drafting**.

If the pre-Protocol definition-resolution step cannot produce one unique definition without inspecting v2 outcomes, the linked hypothesis must become:

`INSUFFICIENT DEFINITION -> REJECT / NOT ADMITTED`

No replacement hypothesis or candidate variable is allowed.

---

# 7. Protocol gate decision

**PROTOCOL INPUT GAP AUDIT = COMPLETE**

**FULL PROTOCOL DRAFT = BLOCKED**

The Protocol must not be drafted yet because unresolved variable-definition degrees of freedom remain.

Next authorized research-design step:

**V2 Variable Definition Resolution**

Only the unresolved items listed in this audit may be resolved:
1. Volatility z-score;
2. Volume z-score;
3. Sector RS;
4. Market Breadth level;
5. F3 same-day volatility control;
6. H4 symbol-level quantile reference population/estimator.

This next step may not:
- inspect v2 outcomes;
- add variables;
- add hypotheses;
- change H1-H14 structure;
- change horizon/outcome/statistic/MDE/sample floor/family;
- replace a variable that proves undefinable.

After those six definitions are committed and reviewed, Protocol drafting may begin.

Experiment remains **NOT AUTHORIZED**.
