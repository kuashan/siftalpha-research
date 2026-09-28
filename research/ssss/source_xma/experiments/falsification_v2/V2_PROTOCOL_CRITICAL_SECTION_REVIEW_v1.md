# XMA Falsification v2 — Critical Section Review v1

Status: **PASS AFTER CORRECTIONS / FULL FREEZE NOT YET AUTHORIZED**

Date: 2026-09-28

Reviewed Protocol commit lineage through:
`10a938d61107ec2918fd5df3e3fbb3312fe0979f`

Current branch later contains Market Data Panel infrastructure and Breadth-availability updates.

Scope of this review:
1. Variable Specification
2. Episode Construction
3. Matched Control Pipeline
4. Statistical Analysis Plan / clustering / ESS / FDR interface
5. Freeze Procedure

No scientific v2 outcome was inspected.

## 1. Variable Specification — PASS AFTER CORRECTION

Existing six-variable definitions were retained.

Correction added:
- exact forward return convention;
- H1 MAE defined as positive adverse-risk magnitude using future lows relative to anchor close;
- H2 maximum drawdown defined as positive close-path peak-to-trough magnitude;
- F4/F5 matched returns explicitly use the same 10-bar close-return convention.

Reason:
without sign/price-path conventions, two implementers could reverse H1 direction or compute H2 from intraday high/low instead of closes.

## 2. Episode Construction — PASS AFTER CORRECTION

Frozen:
- trading-session integer indexing;
- for F2/F4/F5, successive qualifying anchors with index gap <=3 remain one Episode;
- this is exactly 0-2 intervening nonqualifying bars;
- three consecutive nonqualifying bars close the Episode;
- gap >=4 starts a new Episode;
- no calendar-day substitute;
- F1 overrides this debounce and uses maximal consecutive UP_STATE/DOWN_STATE runs;
- F3 unit is date × XMA-state snapshot;
- incomplete forward windows are ineligible and audited;
- overlapping horizons are retained and handled statistically.

Reason:
the earlier wording could merge short F1 state interruptions and left an off-by-one ambiguity in "within 3 bars."

## 3. Matched Control Pipeline — PASS AFTER CORRECTION

Frozen distance:
- dev20;
- prior20 return;
- ATR14/close;
- event-specific eligible-pool mean/sample-std standardization;
- standardized Euclidean distance.

Frozen F4 control rule:
- same symbol;
- same XMA state;
- external condition false;
- outside ±20 trading bars of every same-H Episode;
- complete covariates and 10-bar outcome;
- exactly 5 nearest controls.

Control reuse:
- 5 controls inside one event must be distinct;
- a historical control row may be reused across different events/pairs;
- reuse is persisted.

This avoids order-dependent control-pool depletion.

Required persistence now includes event/control identities, raw and standardized covariates, pool moments, distance, rank, pool size, returns, reuse counts, and pool eligibility audit.

### F5 DiD

A/B pairing is deterministic, not random.

B for each A:
- same symbol;
- same calendar quarter;
- Normal environment;
- same tested XMA state;
- nearest trading-session anchor;
- unique B within hypothesis;
- A processed by date then symbol;
- ties resolved deterministically.

No B-sampling seed exists.

C/D:
- reuse the same frozen matching covariates;
- same symbol/environment as source;
- must be outside tested XMA state;
- ±20-bar exclusion;
- exactly 5 nearest controls.

Therefore the DeepSeek concern that F5 still required a random A/B sample seed does not apply to the current Protocol.

## 4. Statistical Analysis Plan — PASS AFTER MATERIAL CORRECTIONS

### F1

The earlier draft used CR2 wording with median quantile regression without a fully frozen practical implementation.

Replaced with the common market-wave cluster bootstrap used across H1-H14.

### F3

The earlier draft simultaneously included date fixed effects and same-day SPY return.

Within date×state snapshots, SPY same-day return is constant, so this creates exact/redundant date-level control information and can become collinear.

Corrected implementation:
- exact date×state conditioning controls the same-day market context;
- SPY same-day return is recorded but not fitted as a within-snapshot varying coefficient;
- industry return and ATR14/close are the varying within-snapshot controls;
- no extra date fixed-effect column is added.

### Bootstrap raw p-value

The earlier draft counted the sign of ordinary bootstrap estimates as the BH input.

That is not a clean frozen null test because ordinary resampling is centered on the observed empirical distribution, not explicitly on the null.

Corrected:
- 10,000 market-wave cluster resamples;
- bootstrap estimates cluster-robust SE;
- `t_obs = T_obs/SE_boot`;
- reference Student-t with df = number_of_waves - 1;
- registered one-/two-sided tail gives raw p;
- percentile bootstrap interval remains descriptive.

### H4

At least 9,500/10,000 bootstrap resamples must yield estimable KM median difference or H4 becomes `INSUFFICIENT STATISTIC`.

### FDR family-size integrity

Family size remains frozen.

If a registered hypothesis is `INSUFFICIENT SAMPLE` or `INSUFFICIENT STATISTIC`, it receives `p=1.0` for BH rather than being removed from the family.

This prevents post-freeze multiplicity shrinkage.

### ESS unit correction

F3 ESS now uses date×state snapshot-level statistics, not individual symbol rows, consistent with the registered F3 primary unit.

## 5. Freeze Procedure — PASS AFTER CORRECTION

A new prerequisite P0 is explicit:

**Market Data Panel readiness before full Protocol Freeze.**

P0 requires:
- provider-agnostic cache/normalizer;
- resumable rate-limited provider adapter;
- immutable raw snapshots;
- normalized schema;
- hashes/coverage manifest;
- cache reuse dry-run;
- official freeze policy requiring all 51 stock/ETF series.

Important distinction:

- Data Freeze panel completeness = 39 equities + 11 sector ETFs + SPY = 51/51;
- one Breadth date may still be computable with >=32/39 valid equity values.

Therefore 32/39 is not permission to permanently omit seven symbols.

F0 is renamed/defined as Protocol content lock only.

The actual experiment-authorizing Protocol Freeze occurs only at F3 after:
- F0 Protocol content lock;
- F1 Data Freeze;
- F2 Code Freeze;
- F3 Freeze Acceptance.

The sealed window starts only after F3.

## 6. Breadth development availability

The initial implementation test intentionally stopped once 32/39 real equity histories were available because 32 is the frozen daily Breadth minimum.

The seven not used in that first path test were:
- BA
- GE
- XOM
- CVX
- LIN
- NEE
- PLD

Because these are sector-concentrated, treating the 32-symbol subset as the final panel would indeed create a plausible bias risk.

A later development check fetched all seven successfully, each with 5,000 daily rows.

Development-provider history availability is therefore confirmed for 39/39 Breadth symbols.

This does not replace final Data Freeze.

## 7. Market Data Panel infrastructure

Committed:
- `market_data_panel.py`
- `twelve_data_panel_fetch.py`
- `test_v2_infrastructure.py`
- `.github/workflows/v2-research-infra.yml`

Panel behavior:
- provider-agnostic normalized schema;
- raw/normalized SHA-256;
- no refetch on cache hit unless explicitly forced;
- 32/39 Breadth-path status separate from 51/51 freeze-readiness;
- provider-specific fetcher rate-limited below observed Twelve Data ceiling.

GitHub Actions Run #36380007959 was triggered twice (initial + failed-job rerun).

Both attempts ended before any workflow step started:
- `steps = null`
- `logs_url = null`

Therefore this run is classified:
`CI_RUNNER_STARTUP_FAILURE / NOT A TEST FAILURE`

It cannot be used as evidence that the Python tests failed.

The deterministic test definitions remain committed and must pass before F2 Code Freeze.

## Decision

Critical Protocol sections:
**PASS AFTER CORRECTIONS**

Market Data Panel code:
**IMPLEMENTED**

39/39 Breadth development history availability:
**CONFIRMED**

Market Data Panel deterministic CI:
**BLOCKED BY GITHUB RUNNER STARTUP / NOT YET PASS**

Full Protocol Freeze:
**NOT AUTHORIZED**

Scientific v2 experiment:
**NOT AUTHORIZED**

Next actions are bounded:
1. obtain one successful deterministic infrastructure-test execution;
2. complete Protocol content review/approval;
3. populate and freeze the official 51-series stock/ETF panel plus VIX;
4. freeze code and create F3 Freeze Acceptance.

No new variable or hypothesis research is authorized.
