# XMA Falsification v2 — Engineering Closure v2

Status: **PRE-FREEZE ENGINEERING CLOSED / TWO EXTERNAL GATES REMAIN**

Date: 2026-09-28

This document supersedes the operational status in `V2_ENGINEERING_CLOSURE_v1.md`.

It does not supersede historical evidence recorded there.

No additional pre-freeze research design or feature engineering is authorized after this closure.

---

# 1. Engineering terminal state

## Research-design engineering

**CLOSED**

Completed and implemented:

- H1-H14 Registry;
- F1-F5 family boundaries;
- Event/Episode construction;
- exact trading-session wave logic;
- feature definitions;
- Market Data Panel schema/cache;
- matched-control pipeline;
- F5 deterministic DiD pairing;
- ESS;
- statistical estimators;
- BH-FDR;
- Guard/negative controls;
- Data/Code manifest generation;
- hosted-CI definition;
- self-hosted-CI recovery path;
- policy-approved yfinance fallback adapter;
- provider-parity preregistration and audit tooling.

No new:
- candidate variable;
- hypothesis;
- threshold;
- horizon;
- primary statistic;
- direction;
- MDE;
- sample floor;
- FDR family

may be introduced as part of engineering closure.

---

# 2. Deterministic test status

## Independent execution

`PASS`

Current deterministic suite count:

`21 / 21 PASS`

Evidence:

`V2_INDEPENDENT_EXECUTION_CHECK_v1.md`

This includes:
- Market Data Panel tests;
- feature-definition behavior;
- Episode construction;
- exact session-wave behavior;
- ESS;
- BH;
- deterministic F5 pairing;
- Guard logic;
- KM / rank statistics;
- provider-parity audit behavior.

One test-definition defect was discovered during real execution and corrected:

- old test accidentally expected a new Episode at qualifying gap=3;
- frozen Protocol requires gap<=3 to remain one Episode;
- corrected test now uses gap=4 for a new Episode.

This correction changed the test, not the scientific Protocol.

## Freeze-grade execution

`NOT YET PASS`

Reason:

the 21-test PASS was obtained in an independent execution environment, not the candidate frozen runtime.

Candidate frozen runtime remains:

- Python 3.12
- numpy 2.5.3
- pandas 3.0.6
- scipy 1.18.1
- statsmodels 0.15.0
- yfinance 1.7.0 when fallback-data tooling is used

F2 Code Freeze requires the same suite to pass under the recorded freeze-grade runtime.

---

# 3. GitHub Actions execution gate

Status:

`OPEN EXTERNAL GATE`

Evidence shows repository/account-level GitHub-hosted Actions execution failure:

- new v2 hosted workflow fails before any step starts;
- the workflow was simplified to pure shell and still fails before steps;
- independent pre-existing E043 scheduled workflow shows the same signature;
- failed jobs expose:
  - `steps = null`
  - `logs_url = null`

Therefore:

`NOT CLASSIFIED AS PYTHON TEST FAILURE`

Diagnostic artifact:

`V2_GITHUB_ACTIONS_DIAGNOSTIC_v1.md`

The current connector cannot read the private annotation text that would distinguish the exact account/billing/runner entitlement cause.

## Recovery path A — GitHub-hosted

Resolve the repository/account GitHub Actions execution entitlement/billing/spending gate.

Then run:

`V2 Research Infra`

and require all deterministic tests PASS.

## Recovery path B — self-hosted

Prepared:

- `setup_self_hosted_runner.sh`
- `.github/workflows/v2-research-infra-selfhosted.yml`

The bootstrap supports:
- Linux x64;
- Linux arm64;
- fixed runner release/checksum;
- short-lived registration token;
- labels:
  - `siftalpha-research`
  - `v2`

The registration token is never stored in the repository.

Once an authorized self-hosted runner is registered, manually run:

`V2 Research Infra (Self Hosted)`

A successful self-hosted deterministic run is acceptable for P0/F2 provided the environment and hashes are recorded.

---

# 4. Official data-provider / Data Freeze gate

Status:

`OPEN EXTERNAL GATE`

Repository policy remains authoritative:

`SSSS_DATA_SOURCE_POLICY.md`

Current roles:

- Massive = primary research provider when available;
- yfinance = approved fallback/parity path;
- Twelve Data = development sanity source only for this v2 track unless governance is formally amended.

## Massive

Current ChatGPT tool/plugin surface does not expose the previously used Massive connection.

Therefore Massive-based F1 Data Freeze cannot currently be executed here.

## yfinance fallback

Engineering path is complete:

- `yfinance_panel_fetch.py`
- `requirements_yfinance.txt`
- `V2_PROVIDER_PARITY_PLAN_v1.md`
- `provider_parity_audit.py`
- `test_provider_parity.py`

Parity subset is frozen before result interpretation:

- AAPL
- NVDA
- TSLA
- JPM
- XOM
- NEE
- SPY
- XLK

Both fallback adjustment modes must be characterized:
- raw / `auto_adjust=False`
- auto-adjusted / `auto_adjust=True`

Current execution environment could not complete live Yahoo retrieval, so the parity dataset itself is not yet generated.

No one is authorized to infer parity from this missing retrieval.

## Official F1 Data Freeze requires

Stock/ETF panel:

- 39 frozen equities
- 11 frozen sector ETFs
- SPY

Total:

`51 / 51 series`

Plus separately:

- authoritative VIX Index snapshot.

All official snapshots must be persisted and hashed.

A daily Breadth value may use >=32/39 valid equities, but F1 Data Freeze still requires all 39 breadth members to exist in the frozen panel.

No mixed-provider ticker-by-ticker official panel is permitted.

---

# 5. Current freeze artifacts

Prepared candidates:

- `V2_FDR_MANIFEST_v1.json`
- `V2_GUARD_MANIFEST_v1.json`
- `V2_CODE_FREEZE_CANDIDATE_MANIFEST_v3.json`

Latest Code Freeze candidate includes:

- Protocol;
- Registry;
- feature engine;
- Market Data Panel;
- Twelve Data development fetcher;
- yfinance fallback fetcher;
- provider-parity tool/plan;
- Protocol engine;
- statistics;
- Guards;
- manifest generator;
- pinned dependencies;
- deterministic tests;
- hosted/self-hosted CI;
- non-freeze 21/21 PASS evidence;
- GitHub Actions diagnostic.

These remain:

`CANDIDATE ONLY / NOT FROZEN`

until external gates are cleared.

---

# 6. Protocol state

Current Protocol:

`XMA_FALSIFICATION_V2_PROTOCOL.md`

Latest engineering-aligned content includes:

- Massive/yfinance/Twelve provider roles;
- no mixed-provider stage;
- provider-parity gate;
- fallback adjustment-mode gate;
- hosted/self-hosted deterministic execution;
- exact executable Code Freeze artifact set.

Protocol status:

`DRAFT / READY FOR CONTENT-LOCK REVIEW`

F0 Protocol content lock has not been declared because the Protocol itself requires explicit research-owner approval.

---

# 7. Only permitted next actions

The next phase is **not** additional design.

Only these actions are permitted:

## Gate A — deterministic freeze-grade execution

Either:

- restore GitHub-hosted Actions execution;

or:

- register approved self-hosted runner.

Then:

- install exact pinned runtime;
- run deterministic suite;
- archive output;
- record runner/runtime hashes;
- classify P0 test execution.

## Gate B — official data admission/freeze

Either:

- restore Massive and build the complete official panel;

or:

- execute preregistered yfinance parity/admission path;
- make the explicit pre-outcome fallback-provider decision if Massive remains unavailable;
- download complete 51-series stage using one admitted adjustment mode;
- persist authoritative VIX;
- generate Data Freeze manifest.

After Gate A + Gate B:

1. F0 Protocol content lock / explicit approval;
2. F1 Data Freeze;
3. F2 Code Freeze;
4. F3 Full Protocol Freeze Acceptance;
5. F4 Sealed Window Start.

---

# 8. Scientific and trading authorization

v2 scientific hypothesis test:

`NOT AUTHORIZED`

sealed window:

`NOT STARTED`

real-money strategy logic from v2:

`NOT AUTHORIZED`

Product/execution infrastructure remains separable from this scientific freeze.

---

# 9. Closure decision

`PRE-FREEZE ENGINEERING = CLOSED`

`DETERMINISTIC LOGIC = IMPLEMENTED_AND_INDEPENDENTLY_VERIFIED`

`GITHUB-HOSTED FREEZE-GRADE EXECUTION = BLOCKED_BY_EXTERNAL_GATE`

`OFFICIAL DATA FREEZE = BLOCKED_BY_PROVIDER/RETRIEVAL GATE`

No third research-design blocker remains.

Do not reopen feature/research design merely because either external gate takes time to clear.
