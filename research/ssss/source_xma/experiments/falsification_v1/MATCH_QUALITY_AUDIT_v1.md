# Falsification v1 — Match Quality Audit

Status: COVERAGE / MISSINGNESS AUDIT COMPLETE; CONTROL-BALANCE SUB-AUDIT DATA NOT PERSISTED  
Date: 2026-09-28

## Governance

The v1 matching specification remains frozen:

- same symbol;
- same exclusive XMA state;
- same validation window;
- non-event controls excluding the frozen event-exclusion region;
- 5 nearest controls by standardized distance over:
  - dev20;
  - prior 20-bar return;
  - ATR14 / close.

No 52-week position, extra momentum horizon, volume z-score, gap feature, volatility bucket, or other variable is added after observing outcomes.

Any expanded matching specification belongs to a separately preregistered v2.

## Coverage

| Window | Event | Raw n | Matchable n | Coverage |
| --- | --- | ---: | ---: | ---: |
| A | Upper | 392 | 392 | 100.0% |
| A | Lower | 325 | 325 | 100.0% |
| B | Upper | 46 | 39 | 84.8% |
| B | Lower | 20 | 12 | 60.0% |

Validation A has complete frozen-match coverage.

Validation B does not.

## Validation B Upper — missingness is systematic

Seven of 46 Upper events are unmatchable.

All seven are:
- symbol: PLD;
- sector: Real Estate;
- controlPoolN = 0.

Therefore the 2025H2 Upper matched estimate does not represent PLD / Real Estate.

Missingness SMD, defined here only as matchable minus unmatchable event characteristics:

- dev20: 0.295
- prior20: 0.270
- ATR%: 0.961

This is a missingness diagnostic, not a matching-balance SMD.

The frozen 5-bar matched excess is -1.7% on n=39 matchable events.

Interpretation:
**conditional on the matchable non-PLD subset.**

## Validation B Lower — matched result is explicitly conditional on matchability

Only 12 of 20 Lower events are matchable.

Unmatched events:
- MSFT: 2
- NFLX: 4
- KO: 1
- LLY: 1

The missingness is not random with respect to observed characteristics.

Mean ATR%:
- matchable: 2.1%
- unmatchable: 2.9%

Missingness SMD:
- dev20: 0.029
- prior20: -0.063
- ATR%: -0.726

The frozen matched excess values are:
- 10-bar: -1.4%
- 20-bar: -2.8%

Both are based on n=12, not n=20.

Required label:
**CONDITIONAL ON MATCHABILITY.**

No claim is made that the eight unmatchable events would have behaved similarly.

## What cannot be audited from the persisted v1 artifacts

The persisted matched-event rows contain:
- event covariates;
- matched mean returns;
- match count;
- eligible control-pool size.

They do not persist:
- control identifiers;
- each selected control date;
- each selected control's dev20 / prior20 / ATR%;
- per-control matching distance.

Therefore a true event-vs-control pre/post covariate balance table cannot be reconstructed from the repository artifacts alone.

This is recorded as:
**INCONCLUSIVE / DATA NOT PERSISTED** for the control-balance sub-audit.

The missing control rows are not regenerated from a new external vendor because doing so after outcome inspection would mix data provenance and create an avoidable reconstruction degree of freedom.

## v2 reproducibility requirement

Before any v2 outcome is inspected, matching output must persist for every event:
- control symbol and date;
- all matching covariates;
- standardized distance;
- eligibility/exclusion reason;
- control-pool size;
- selected-control rank.

Then pre/post SMD and variance-ratio tables can be reproduced exactly.

## Decision

1. Frozen v1 matching variables remain unchanged.
2. Validation A matching coverage is complete.
3. Validation B Upper matched inference excludes PLD / Real Estate.
4. Validation B Lower matched inference is conditional on the 60% matchable subset.
5. No unmatchable event is silently imputed or assumed to follow the matched subset.
6. The absent control-level covariate snapshot is a documented v1 reproducibility limitation, not repaired post hoc.
