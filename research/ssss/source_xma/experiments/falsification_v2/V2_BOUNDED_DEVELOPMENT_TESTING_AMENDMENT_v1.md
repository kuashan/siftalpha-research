# XMA Falsification v2 — Bounded Development Testing Amendment v1

Status: **PRE-PROTOCOL GOVERNANCE AMENDMENT / LIMITED DEVELOPMENT TESTING AUTHORIZED**

Date: 2026-09-28

## 1. Purpose

v2 research exists to support future trading decisions.

Research governance must prevent false discovery, but it must not create an endless design loop that never reaches executable testing.

Therefore v2 adopts a bounded cycle:

```text
DEFINE
→ IMPLEMENT
→ DEVELOPMENT SANITY TEST
→ FREEZE OR REJECT
→ MOVE FORWARD
```

The purpose of development testing is to verify implementation, data availability, missingness, sample formation, and reproducibility.

It is **not** permitted to use development-test outcomes to tune a hypothesis.

## 2. Development data may be used before Protocol Freeze

Allowed only on data already exposed by earlier research or on an explicitly designated non-sealed development window.

Development tests may verify:

- formulas;
- event construction;
- control construction;
- missing-data behavior;
- matching coverage;
- sample counts;
- cluster construction;
- code reproducibility;
- whether a variable can actually be computed.

Development tests may NOT be used to:

- choose a threshold because returns look better;
- change H1-H14 direction;
- change horizon;
- change MDE;
- change primary statistic;
- add a candidate variable;
- replace a failed variable;
- promote a trading signal.

## 3. Sealed-window protection

The future sealed window remains completely unavailable.

No development test may use:

- the future v2 sealed window;
- any date later designated as part of that sealed window;
- a window whose results are later relabeled as untouched OOS.

Once a date is used for development, it can never be part of the sealed window.

## 4. Stage closure rule

Every design stage must end in one of:

- `IMPLEMENTED_AND_VERIFIED`
- `REJECTED_NOT_ADMITTED`
- `BLOCKED_BY_DATA`

No stage may remain open indefinitely.

For a definition problem, at most one preregistered implementation is selected without outcome inspection.

If that implementation cannot be computed reproducibly on development data, the linked hypothesis is rejected/not admitted rather than repeatedly redesigned.

## 5. Trading orientation

All v2 research artifacts must state how the result would eventually map to one of:

- risk admission;
- position lifecycle;
- cross-sectional ranking;
- conditional information;
- risk-off suppression.

This mapping is descriptive only until a hypothesis survives the frozen Protocol and sealed validation.

No live trading rule is authorized by this amendment.

## 6. Product-line separation

Execution infrastructure may proceed independently:

- market-data ingestion;
- order lifecycle;
- risk controls;
- logs;
- monitoring;
- kill switch.

Research-derived strategy logic remains prohibited until validation gates are passed.

## 7. Next authorized step

Resolve the six gaps from `V2_PROTOCOL_INPUT_GAP_AUDIT_v1.md`, then perform a bounded implementation sanity test on non-sealed development data.

The sanity test must report implementation validity and data coverage, not trading performance.

Protocol drafting begins only after this bounded test closes the variable-definition stage.

Experiment authorization for scientific v2 hypothesis testing remains **NOT AUTHORIZED**.
