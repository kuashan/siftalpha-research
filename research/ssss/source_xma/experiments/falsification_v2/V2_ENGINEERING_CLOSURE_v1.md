# XMA Falsification v2 — Engineering Closure v1

Status: **ENGINEERING IMPLEMENTATION COMPLETE / FULL FREEZE BLOCKED BY EXTERNAL INFRASTRUCTURE**

Date: 2026-09-28

This document closes the pre-freeze engineering implementation stage.

No new research variable, hypothesis, threshold, horizon, MDE, family, or trading rule is authorized after this closure.

## 1. Completed engineering scope

### Market Data Panel

Implemented:
- provider-agnostic normalized OHLCV cache;
- immutable raw/normalized hashes;
- per-symbol coverage audit;
- 51-series Data-Freeze completeness gate;
- 32/39 per-date Breadth eligibility kept separate from 51/51 panel completeness;
- resumable/rate-limited Twelve Data development fetcher;
- exact raw/normalized manifest metadata.

Development history availability:
- frozen Breadth equities checked: 39/39 available from development provider;
- frozen sector ETFs + SPY were exercised in development implementation testing.

### Feature implementation

Implemented:
- ATR14;
- dev20;
- prior20;
- point-in-time FAST_MID_ANALYTIC;
- distance-to-mid;
- H4 frozen calibration quantiles;
- VOL_Z;
- VOLUME_Z;
- Sector RS;
- F3 ATR14/close volatility control;
- Market Breadth;
- Breadth Q10 based on prior 20 valid observations;
- VIX_CHG5.

### Protocol mechanics

Implemented:
- F1 continuous state-run Episodes;
- F2/F4/F5 debounced Episodes;
- exact trading-session index requirement;
- market-wave clustering primitive;
- design-effect ESS;
- matched-control standardized Euclidean distance;
- deterministic 5-nearest selection;
- explicit control-reuse semantics;
- deterministic F5 A→B one-use pairing;
- BH-FDR implementation;
- Guard pass/fail primitive.

### Statistical primitives

Implemented:
- median quantile-regression state coefficient;
- H3 probability difference;
- Kaplan-Meier median waiting time;
- H4 median-difference statistic;
- F3 rank-biserial statistic;
- F3 partial Spearman implementation;
- market-wave cluster bootstrap;
- bootstrap SE + Student-t raw p-value interface.

### Negative controls

Implemented:
- G-F1 state-label permutation;
- G-F2 distance permutation;
- G-F3 Sector-RS permutation;
- G-F4 external-condition permutation;
- G-F5 market-wide date-level Risk-Off permutation;
- fixed guard seeds;
- fixed-seed rejection-sampling primitive;
- no alternate-seed searching.

### Freeze machinery

Implemented:
- deterministic SHA-256 manifest generator;
- FDR candidate manifest;
- Guard candidate manifest;
- Code Freeze Candidate Manifest v2.

## 2. Exact dependency candidate

Python target:
- 3.12

Pinned candidate runtime:
- numpy 2.5.3
- pandas 3.0.6
- scipy 1.18.1
- statsmodels 0.15.0

These versions are recorded in `requirements_v2.txt`.

They remain Code-Freeze candidates until deterministic tests actually execute successfully.

## 3. Deterministic test suite

Committed:
- `test_v2_infrastructure.py`
- `test_v2_protocol_engine.py`
- `test_v2_statistics_guards.py`

The suite covers:
- 32/39 Breadth calculation path vs 51/51 freeze readiness;
- SHA/manifest generation;
- prior-20-valid Breadth threshold behavior;
- Episode debounce;
- F1 state-run interruption;
- trading-session wave clustering;
- design-effect ESS;
- BH behavior;
- deterministic F5 pairing;
- Guard gate;
- deterministic Guard permutations/rejection stream;
- Kaplan-Meier median;
- rank-biserial and partial-Spearman primitives.

## 4. GitHub Actions blocker

Workflow:
`.github/workflows/v2-research-infra.yml`

The workflow was simplified to pure shell:
- no `actions/checkout`;
- no `actions/setup-python`;
- checkout uses the repository GITHUB_TOKEN directly;
- pinned dependencies are installed by pip;
- unittest is invoked directly.

Despite removing external `uses:` actions, GitHub Actions runs still fail before any workflow step starts.

Observed repeatedly:
- job conclusion = failure;
- `steps = null`;
- `logs_url = null`;
- check-run annotations exist, but the current GitHub connector does not expose their text.

Example latest observed pre-closure run family:
- V2 Research Infra run series #1 through #15;
- failures occur at job startup, before Python execution.

Classification:

`GITHUB_ACTIONS_STARTUP_BLOCK / NOT A PYTHON TEST FAILURE`

Because no test step starts, these failures provide no evidence that deterministic unit tests themselves failed.

This blocker must be resolved at the GitHub Actions account/repository/runner layer.

## 5. Official data-source blocker

Repository policy states:
- Massive is current primary research source;
- yfinance is approved fallback subject to provider-parity audit;
- no silent ticker-by-ticker provider mixing.

Current tool surface:
- Massive is not available;
- plugin-directory lookup for `Massive` returned no available plugin;
- Twelve Data was usable for development sanity testing but has not been adopted as an official frozen research provider.

Therefore F1 Data Freeze is not complete.

No one is authorized to silently declare Twelve Data the official v2 source.

Allowed resolutions:
1. restore the Massive connection and freeze the complete stage from Massive; or
2. use the policy-approved fallback path, including a provider-parity audit and a full-stage redownload from one replacement provider.

## 6. Freeze candidates already prepared

- `V2_FDR_MANIFEST_v1.json`
- `V2_GUARD_MANIFEST_v1.json`
- `V2_CODE_FREEZE_CANDIDATE_MANIFEST_v2.json`

They are candidates only.

They must not be renamed or interpreted as final freeze manifests until:
- deterministic tests execute and pass;
- official Data Freeze is complete;
- final code hashes are refreshed.

## 7. Protocol state

Critical Protocol sections were reviewed and corrected.

Current Protocol includes:
- exact risk outcome signs/formulas;
- exact Episode rules;
- exact trading-session semantics;
- exact matching/control persistence;
- deterministic F5 A/B pairing;
- cluster/ESS rules;
- frozen family-size BH handling;
- Guard gate outside BH;
- Market Data Panel P0 prerequisite;
- Data Freeze;
- Code Freeze;
- Full Freeze Acceptance;
- sealed-window start after full acceptance.

Section 11 now binds Code Freeze to the actual executable module set.

Protocol content remains:
`DRAFT / NOT FULLY FROZEN`

## 8. Engineering stage terminal decision

**ENGINEERING IMPLEMENTATION = COMPLETE**

No additional pre-freeze feature engineering is authorized.

**FULL FREEZE = BLOCKED_BY_EXTERNAL_INFRASTRUCTURE**

Open blockers are exactly:

1. `GITHUB_ACTIONS_STARTUP_BLOCK`
2. `OFFICIAL_DATA_PROVIDER_NOT_CONNECTED_OR_FROZEN`

No third research-design blocker is open.

## 9. Resume rule

When either blocker is resolved, resume only at the corresponding gate.

### If GitHub Actions is fixed

Run the already-committed deterministic suite.

If tests fail:
- fix implementation bugs only;
- do not change hypotheses/variables/statistics to make tests pass.

If tests pass:
- mark P0 test execution PASS;
- proceed to official Data Freeze.

### If official data provider is restored first

Build/cache the complete:
- 39 equities;
- 11 sector ETFs;
- SPY;
- authoritative VIX snapshot.

Do not inspect scientific v2 outcomes.

Generate Data Freeze manifest, then wait for deterministic code-test PASS before Full Freeze Acceptance.

## 10. Scientific authorization

v2 scientific hypothesis testing:
**NOT AUTHORIZED**

sealed window:
**NOT STARTED**

real-money strategy logic:
**NOT AUTHORIZED BY v2**

The next research-scientific step is not more design.

It is Full Freeze Acceptance after the two external engineering blockers are cleared.
