# CHAN × SLTD Research Protocol v1

Status: **FROZEN_BEFORE_ENGINE_RECONSTRUCTION**
Date: 2026-10-03

Parent references:
- V7 frozen commit: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`
- prior profit-protection study: `SLTD_V7_PROFIT_PROTECTION_STUDY_V1 = COMPLETE`
- Chan theory / engineering boundary:
  `CHAN_THEORY_ENGINEERING_BOUNDARY_V1 = FROZEN_FOR_RESEARCH_DESIGN`

## 1. Main question

Does a causal Chan structure layer provide information that is materially different from,
and complementary to, the frozen SLTD state layer?

The first objective is **not** to maximize return.

The first objective is to determine whether Chan structure adds non-redundant information
about:
- trend continuation;
- local exhaustion;
- structural deterioration;
- structural recovery.

## 2. Frozen SLTD baseline

V7 remains unchanged.

SLTD inputs remain:
- FIRST_OBSERVED XMA25 / XMA60;
- corrected slow structure;
- BLUE / GREEN / GRAY / EXPANSION topology;
- existing V7 action taxonomy;
- existing position policy;
- existing C2.

No Chan result may change the frozen V7 branch during this study.

## 3. Research phases

### C0 — CHAN_ENGINE_RECONSTRUCTION

Purpose:
build a point-in-time Chan engine before looking at profitability.

Required objects:
- inclusion-adjusted K;
- fractal;
- Bi;
- segment;
- Zhongshu;
- trend / consolidation;
- PZ divergence;
- QS divergence;
- BSP1 / BSP2 / BSP3;
- provisional / confirmed / invalidated states.

Required validation:
1. original lesson examples where machine-readable reconstruction is possible;
2. lesson-81 corrected edge case;
3. cross-check against at least two independent open-source implementations;
4. bar-by-bar replay;
5. anchor / confirm timestamp separation.

Bi-definition ambiguity must be closed in C0 without PnL.

Closure states:
- `IMPLEMENTED_AND_VERIFIED`
- `BLOCKED_DEFINITION_AMBIGUITY`
- `REJECTED_RECONSTRUCTION`

No strategy performance test is allowed before C0 closes as IMPLEMENTED_AND_VERIFIED.

### C1 — CHAN_STRUCTURAL_INVENTORY

Purpose:
describe how Chan structures occur on the same daily market data used by SLTD.

Primary universe:
- the frozen 89-stock U.S. universe already used by V7 validation.

Window:
- 2020-01-02 through 2026-09-30, subject to exact available source coverage.

Representation:
- Chan FIRST_OBSERVED only;
- SLTD FIRST_OBSERVED only.

No forward return / PnL in C1.

For every completed daily bar persist:
- SLTD state;
- SLTD state age;
- upper / lower / BS / BD event flags;
- Chan current Bi direction and completion state;
- Chan current segment direction and completion state;
- latest confirmed fractal type;
- Zhongshu presence / location;
- consolidation vs trend;
- divergence labels;
- BSP labels;
- structural level;
- provisional / confirmed / invalidated transitions.

Required outputs:
- frequency table;
- state-duration table;
- SLTD × Chan cross-tab;
- transition matrix;
- event overlap / redundancy table.

C1 asks:
> Is Chan merely rediscovering SLTD, or is it observing another dimension?

### C2 — COMPLEMENTARITY EVENT STUDY

Only after C1 event vocabulary is frozen.

C2 may inspect future outcomes, but it remains an event study, not a strategy.

Pre-frozen event families:

#### E1 — LOCAL_TOP_CONFIRMATION
Examples:
- confirmed top fractal;
- confirmed end of an up Bi.

Question:
inside SLTD BLUE, does E1 identify higher near-term giveback risk?

#### E2 — SEGMENT_DETERIORATION
Examples:
- confirmed end of an up segment;
- transition into confirmed down segment structure.

Question:
does it identify more serious deterioration than E1?

#### E3 — STRUCTURAL_EXHAUSTION
Examples:
- PZ divergence;
- QS divergence;
- BSP1 / BSP2.

Question:
does exhaustion add information after controlling for SLTD state / age / rail location?

#### E4 — STRUCTURAL_BREAK
Examples:
- BSP3 sell;
- confirmed Zhongshu failure / downside structural continuation.

Question:
does it identify conditions where partial profit protection should escalate toward full exit?

#### E5 — STRUCTURAL_RECOVERY
Mirror buy-side structures after a prior E1–E4 deterioration.

Question:
can the Chan layer support re-entry / re-risking instead of one-way de-risking?

No new event family may be invented after C2 results are inspected.

### C3 — POSITION_OVERLAY STUDY

C3 runs only if C2 demonstrates incremental information.

V7 BUY / HOLD / WAIT remain frozen.

The first position-overlay study will be finite and hierarchical:

- `O1_WARNING_ONLY`
  - record E1; no trade.
- `O2_LOCAL_REDUCE_RECOVER`
  - confirmed local deterioration may reduce exposure;
  - corresponding structural recovery may restore the reduced slice.
- `O3_EXHAUSTION_REDUCE_RECOVER`
  - E3 controls a larger de-risk / re-risk cycle.
- `O4_STRUCTURAL_BREAK_EXIT`
  - E4 may escalate to full exit only after predefined confirmation.

Exact percentages are **not** selected in C0/C1/C2.
They must be frozen before C3 from a minimal finite set and cannot be tuned by symbol.

No unlimited combinatorial search is allowed.

## 4. Why recovery is mandatory

The previous SLTD profit-protection study showed that one-way de-risking can strongly reduce drawdown
while destroying trend return.

Chan theory itself distinguishes:
- larger-level trend exposure;
- lower-level sell / buy structures inside that exposure.

Therefore the first Chan overlay is required to study both:
- de-risk;
- re-risk.

A sell-only Chan overlay is not sufficient evidence.

## 5. Data discipline

Joint studies must use the same:
- OHLC source;
- adjustment policy;
- regular-session definition;
- trading calendar;
- bar completion rule.

No provider stitching.

If a small OHLC difference changes a fractal / Bi / segment split,
that sensitivity must be logged.

## 6. Primary evaluation metrics

C2 event study:
- forward MFE / MAE;
- peak-to-trough giveback after event;
- probability of new high before specified adverse move;
- duration to structural recovery / escalation;
- conditional results by SLTD state and state age.

C3 strategy study:
- Return;
- CAGR;
- MaxDD;
- Calmar;
- time in market;
- turnover;
- profit capture;
- giveback;
- Prior79 vs OOS10;
- per-symbol breadth;
- 5 bps / 10 bps.

## 7. Complementarity gate

Chan is considered structurally complementary only if C2 shows at least one pre-frozen event family
that:

1. has materially different occurrence timing from existing SLTD SELL / C2 events;
2. changes future giveback / MAE distribution inside the same SLTD state;
3. is not explained only by current SLTD state, state age or rail position;
4. reproduces directionally in OOS10.

If none satisfies these:
- `CHAN_SLTD_COMPLEMENTARITY = REJECTED`
- no position overlay is built.

## 8. Strategy admission gate

If C3 is reached, no overlay is admitted unless it improves the risk / giveback problem without
repeating the failure of the prior one-way profit-protection study.

Minimum conditions at primary 5 bps:
- all89 Calmar > frozen V7;
- all89 MaxDD less severe than V7;
- return retention >= 90% of V7;
- median giveback improves;
- OOS10 does not contradict risk / giveback direction;
- turnover increase remains explicitly reported.

Anything else:
- `MIXED_NOT_ADMITTED`
- or `REJECTED_NOT_ADMITTED`.

## 9. Finite stopping rules

This research does not loop indefinitely.

C0:
- one reconstruction decision.

C1:
- one structural inventory.

C2:
- exactly E1..E5.

C3:
- at most O1..O4.

After C3:
- ADMIT candidate;
- KEEP V7;
- or CLOSE Chan overlay research v1.

Any new hypothesis requires a new versioned protocol.

## 10. Immediate next action

Authorized now:

`C0_CHAN_ENGINE_RECONSTRUCTION`

Not authorized by this protocol:
- modifying frozen V7;
- product integration;
- Android UI changes;
- production trading.

## 11. Closure

`CHAN_SLTD_RESEARCH_PROTOCOL_V1 = FROZEN_BEFORE_ENGINE_RECONSTRUCTION`
