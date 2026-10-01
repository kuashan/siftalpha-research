# SSSS Conditional Rail Rules v1 — Actionability Audit Integrity Review v1

Status: **ACTIONABILITY AUDIT NOT CLOSED / IMPLEMENTATION DEFECT CONFIRMED**
Date: 2026-10-02
Audited branch head before this note: `7b405b7067f3f21362fd520b779f28bf2a27242e`

## Scope

This review audits the five persisted Actionability Audit batches after Round 3.
It does not change Round 1, Round 2, or Round 3 results.

Frozen actionability candidates:
- B2 = LOWER_FAST then RANGE->UP
- S1 = UPPER_FAST then UP->RANGE
- S2 = UPPER_FAST then RANGE->DOWN

The frozen Actionability Audit protocol states that the persisted Round-2 strict
first-observed event ledger is authoritative and that events must not be
recomputed or relabeled using finalized/repainted XMA.

## Audit result

The five current actionability batches contain all 91 Round-3 transition-conditioned
candidate rows by ID count:

- B2: 25 total
- S1: 39 total
- S2: 27 total

However, 32 rows are currently marked `EVENT_NOT_FOUND`:

- B2: 9 invalid, 16 valid
- S1: 12 invalid, 27 valid
- S2: 11 invalid, 16 valid

A direct integrity comparison was then performed against the persisted
`ROUND2_BATCH1_v1.json` ... `ROUND2_BATCH5_v1.json` ledgers.

Match key:
`symbol + event_date + rail type + transition + transition_bars`

Result:

`32 / 32 EVENT_NOT_FOUND rows are present exactly in the authoritative Round-2 ledger.`

Therefore these 32 rows are not missing research events. The current actionability
implementation is re-finding/reconstructing source events in a way that is inconsistent
with the frozen protocol.

## Consequence

The current five Actionability Audit batches must not be consolidated into a final
promotion/rejection decision.

The 59 valid rows are an incomplete and potentially selected subset. Their statistics
may be used only as a diagnostic of what happens after transition detection, not as
final evidence.

## Preliminary diagnostic on currently valid rows only

These numbers are explicitly incomplete and must not be used for strategy freeze.

### B2
- valid: 16 / 25
- detection-close ret20 mean: +2.587%
- next-open ret20 mean: +2.281%
- next-open ret20 median: +3.755%
- expected-direction rate: 68.75%
- next-open favorable20 mean: +5.983%
- next-open adverse20 mean: 4.989%
- A/B/C next-open ret20 means: +2.279%, +0.829%, +3.252%
- leave-one-symbol-out pooled ret20 remains positive in all omissions

### S1
- valid: 27 / 39
- detection-close ret20 mean: -2.807%
- next-open ret20 mean: -2.665%
- next-open ret20 median: -0.544%
- expected-direction rate: 51.85%
- bearish favorable20 mean: 8.951%
- bearish adverse20 mean: 4.422%
- A/B/C next-open ret20 means: -0.822%, -4.643%, -2.743%
- leave-one-symbol-out pooled ret20 remains negative in all omissions

### S2
- valid: 16 / 27
- detection-close ret20 mean: -0.728%
- next-open ret20 mean: -0.736%
- next-open ret20 median: -1.308%
- expected-direction rate: 62.50%
- bearish favorable20 mean: 5.562%
- bearish adverse20 mean: 6.698%
- A/B/C next-open ret20 means: -0.079%, -6.886%, +4.101%
- leave-one-symbol-out pooled ret20 does **not** preserve the bearish sign in all omissions

The apparent edge decay from the original event-date anchored Round-3 measurements is
material, especially for S2, but no final conclusion is allowed until all 91 events
are mapped under the frozen actionability protocol.

## Required correction before final Actionability result

1. Read candidate events directly from the persisted Round-2 strict first-observed ledgers.
2. Do not re-detect or re-find the source XMA event.
3. For each authoritative event:
   - event index/date come from the persisted ledger;
   - transition and transition_bars come from the persisted ledger;
   - detection index = event index + transition_bars;
   - detection time becomes known only after the detection bar closes.
4. Map the detection date to the symbol's trading calendar.
5. Execute the diagnostic at the next tradable session open.
6. Recompute 5/10/20-bar returns, 20-bar MFE/MAE, temporal blocks, symbol breadth,
   expected-direction rate, and leave-one-symbol-out stability for all mappable events.
7. Only then issue an Actionability Consolidated Result and decide whether B2/S1/S2
   remain eligible for candidate strategy freeze.

## Research state after this review

- Round 1: COMPLETE
- Round 2: COMPLETE / DISCOVERY ONLY
- Round 3: COMPLETE
- Actionability Audit: **IN PROGRESS / CURRENT IMPLEMENTATION INVALIDATED FOR 32 EVENTS**
- Strategy 2 SSSS Structure: **RESEARCH_IN_PROGRESS**

No production BUY/SELL rule, sizing rule, or strategy freeze is authorized by this review.
