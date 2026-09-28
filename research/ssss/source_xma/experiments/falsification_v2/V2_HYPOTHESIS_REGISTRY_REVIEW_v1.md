# XMA Falsification v2 — Hypothesis Registry Review v1

Status: **PASS FOR REGISTRY STRUCTURE / NOT PROTOCOL FREEZE**

Date: 2026-09-28

Reviewed artifact:
- path: `research/ssss/source_xma/experiments/falsification_v2/V2_HYPOTHESIS_REGISTRY_DRAFT.md`
- registry commit: `9ed1a5c43df45a7ce8f93f9560bb14b8cb6aaa80`
- registry blob SHA: `8842f62efd57ce32e1fd62fbfd4aaaf797bf7ee0`

No v2 outcome data were accessed or analyzed for this review.

## Mechanical completeness check

PASS.

- formal hypotheses: exactly H1-H14;
- family counts: F1=2, F2=2, F3=2, F4=4, F5=4;
- every H1-H14 entry contains all 14 required fields;
- no TBD / 待定 / 视结果而定 token remains;
- guards G-F1 through G-F5 are present;
- formal hypothesis budget remains 14;
- guard entries remain outside the 14-hypothesis budget.

## Review item 1 — Primary-statistic overlap

**PASS.**

The registered primary statistics are distinct at the hypothesis-identity level.

F1:
- H1: median-quantile-regression DOWN coefficient for ATR-normalized MAE;
- H2: median-quantile-regression DOWN coefficient for ATR-normalized maximum drawdown.

F2:
- H3: 20-bar midpoint-touch probability difference;
- H4: Kaplan-Meier median first-touch waiting-time difference.

F3:
- H5: rank-biserial correlation for High/Low Sector RS membership;
- H6: partial Spearman correlation for continuous Sector RS.

F4:
- H7-H10 use the same estimator form (mean 10-bar matched excess return), but are non-duplicate registered hypotheses because the frozen condition identities differ:
  - Volatility × DOWN;
  - Volatility × UP;
  - Volume × DOWN;
  - Volume × UP.

F5:
- H11-H14 use the same DiD estimator form, but are non-duplicate registered hypotheses because the frozen condition identities differ:
  - Breadth × DOWN;
  - Breadth × UP;
  - VIX × DOWN;
  - VIX × UP.

Interpretation rule:

`primary-statistic identity = estimator + registered condition + registered state + horizon`.

Repeated estimator form inside one family is permitted; duplicate hypothesis identity is not.

No duplicate formal hypothesis was identified.

## Review item 2 — Outcome-family separation

**PASS.**

The five research families remain separated by primary outcome type:

- F1 Risk: absolute ATR-normalized risk metrics only;
- F2 Lifecycle: midpoint path probability / timing only;
- F3 Cross-sectional: rank / correlation metrics only;
- F4 Conditional: matched excess return only;
- F5 Risk-Off: direction-normalized difference-in-differences only.

No formal hypothesis uses a primary outcome belonging to another family.

Specific checks:
- F1 does not use matched excess return;
- F2 does not use MAE, drawdown, or return as a primary statistic;
- F3 does not use F4 matched-excess or F5 DiD;
- F4 does not use absolute risk metrics;
- F5 does not use raw matched excess as its primary statistic; matched excess is only an internal cell component of the DiD.

## Review item 3 — Unique family membership

**PASS.**

Every H1-H14 entry belongs to exactly one formal FDR family:

- H1-H2 -> F1
- H3-H4 -> F2
- H5-H6 -> F3
- H7-H10 -> F4
- H11-H14 -> F5

No cross-family duplicate membership was identified.

Candidate-variable placement is also unique:
- Distance to midpoint -> F2 only;
- Sector relative strength -> F3 only;
- Volatility z-score -> F4 only;
- Volume z-score -> F4 only;
- Market Breadth -> F5 only;
- VIX change -> F5 only;
- discrete XMA state is the internal condition source for F1 and is not counted as one of the six external/lifecycle candidate fields.

## Guard review

**PASS FOR REGISTRY DESIGN.**

- G-F1 through G-F5 exist;
- each has a deterministic generation rule;
- each freezes a random seed where permutation is used;
- each specifies sample matching;
- each specifies a primary statistic, horizon, MDE/pass band, sample floor, and insufficiency handling;
- guard insufficiency/failure blocks promotion of the linked family.

Guards are methodological controls and remain outside H1-H14.

## Governance consistency correction

A prior One-Pager Amendment contained a 12-hypothesis maximum.

This conflict is now explicitly superseded by:

`V2_PROTOCOL_DESIGN_ONEPAGER_AMENDMENT_v2.md`

which freezes the final formal budget at 14:
2 + 2 + 2 + 4 + 4.

## Decision

**V2 HYPOTHESIS REGISTRY DRAFT REVIEW = PASS**

Meaning:
- Registry structure is complete enough to be incorporated into a Protocol draft;
- no hypothesis may be added after this review;
- candidate variables may not be added or replaced;
- this PASS does **not** freeze the v2 Protocol;
- this PASS does **not** authorize v2 data access or experiment execution;
- data freeze, code freeze, FDR manifest, preprocessing spec, Protocol review, and sealed-window designation remain outstanding.

Next authorized step:

**Draft `XMA_FALSIFICATION_V2_PROTOCOL.md` from the reviewed Registry and governing design artifacts, without running v2 data.**
