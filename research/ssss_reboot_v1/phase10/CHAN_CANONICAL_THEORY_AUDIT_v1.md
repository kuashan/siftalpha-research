# CHAN_CANONICAL_THEORY_AUDIT_v1

Status: **T1_T2_AUDIT_COMPLETE__SOURCE_DRIVEN_CORRECTIONS_REQUIRED**

Date: 2026-10-03  
Repository: `kuashan/siftalpha-research`  
Branch: `feature/chan-standalone-v2`  
Audit base remote HEAD: `21176536d8dd2501676718617623ed6a73976683`

## 0. Scope and hard boundary

This audit is theory-first.

Definition authority order:

1. original `教你炒股票` source;
2. later original clarifications / corrections;
3. multiple mature implementations only as cross-checks;
4. explicit engineering choices where machine specification is not uniquely given;
5. broad-market validation;
6. single-stock examples last.

No rule in this audit is admitted because it increases signal count, improves PnL, or makes a particular symbol show B1/B2/B3/S1/S2/S3.

No SLTD/V7/E/5s rule is used.

## 1. Remote-state audit

The previous handoff recorded:
`e438ac9310beda084e547411d41b463c8459ba49`

The real branch HEAD at audit start was:
`21176536d8dd2501676718617623ed6a73976683`

The branch advanced by exactly two commits:

- `4328a2646adc337eff7c347161b451418c964828` — added `NEW_CHAT_CHAN_THEORY_AUDIT_HANDOFF_2026-10-03.md`
- `21176536d8dd2501676718617623ed6a73976683` — added `CHAN_STANDALONE_NEXT_CHAT_HANDOFF_v1.md`

Both commits are documentation-only. No Chan implementation code changed in this drift.

The NEW_CHAT handoff also references three files that do not exist at the audited HEAD and cannot be found by repository search:

- `CHAN_THEORY_ENGINEERING_BOUNDARY_v1.md`
- `CHAN_SLTD_RESEARCH_PROTOCOL_v1.md`
- `CHAN_C0A_RECONSTRUCTION_CLOSURE_v1.md`

They are therefore treated as stale/missing references. No content is reconstructed from conversation memory.

## 2. Classification vocabulary

Major rules are classified as:

- `CANONICAL_SOURCE_CONFIRMED`
- `LATER_SOURCE_CLARIFICATION`
- `ENGINEERING_CHOICE_EXPLICIT`
- `COMMUNITY_VARIANT_NOT_CANONICAL`
- `NEEDS_CORRECTION`

Current v2.2 implementation decisions are additionally labeled:

- `KEEP_AS_CANONICAL`
- `KEEP_AS_ENGINEERING_CHOICE`
- `REVISE_OVERMODIFIED`
- `REJECT_UNSUPPORTED`

## 3. Canonical definition matrix

| Area | Source-backed definition | Source | Classification | v2.2 disposition |
|---|---|---|---|---|
| K inclusion | Inclusion is processed left-to-right with associativity/order. Once direction is known, upward inclusion keeps the higher high/higher low; downward inclusion keeps the lower high/lower low. Direction is determined from the previous non-inclusive K relationship. | Lessons 65, 77 | CANONICAL_SOURCE_CONFIRMED | Partial keep |
| Initial inclusion direction | If the data window begins inside an inclusion chain and no prior non-inclusive K exists, the original definition does not justify simply assuming upward direction. | Lesson 65 | ENGINEERING_CHOICE_EXPLICIT | REVISE_OVERMODIFIED if it can change downstream structure |
| Fractal | After inclusion processing, a top/bottom fractal is a strict three-K geometric structure. Confirmation requires the right-side K to exist. | Lessons 62, 65, 77 | CANONICAL_SOURCE_CONFIRMED | KEEP_AS_CANONICAL |
| Bi minimum separation | A Bi joins a top and bottom fractal, with at least one K not belonging to either endpoint fractal. | Lesson 77; later discussion around 106 | LATER_SOURCE_CLARIFICATION | KEEP_AS_CANONICAL subject to exact counting regression |
| Bi endpoint price relation | The top-fractal K range must actually stand above the bottom-fractal K range; otherwise a Bi cannot be formed. | Lesson 77 | CANONICAL_SOURCE_CONFIRMED | KEEP_AS_CANONICAL |
| Same-type fractal handling | Stronger same-type fractals can replace earlier provisional endpoints; Bi partition must remain unique. | Lessons 65, 77 | LATER_SOURCE_CLARIFICATION | KEEP_AS_CANONICAL, but add exact equality/sequence fixtures |
| Segment prerequisite | A segment has at least three Bi, an odd number of Bi when complete, and its first three Bi must overlap. | Lessons 65, 77 | LATER_SOURCE_CLARIFICATION | NEEDS_CORRECTION: current code does not explicitly enforce first-three-Bi overlap before segment construction |
| Segment destruction | A completed segment is confirmed only when destroyed by an opposite segment; feature-sequence first/second situations govern confirmation. | Lessons 67, 71, 77, 78 | LATER_SOURCE_CLARIFICATION | NEEDS_CORRECTION / deep reimplementation audit |
| Feature sequence | Feature elements are the Bi opposite the segment direction; inclusion is handled within the same feature sequence; gap and no-gap cases have different confirmation logic. | Lessons 67, 71, 77 | LATER_SOURCE_CLARIFICATION | Current implementation is an engineering approximation; cannot be labeled canonical yet |
| Zhongshu definition | A Zhongshu is the overlap of at least three consecutive lower-level trend types. | Lessons 17, 18, 20 | CANONICAL_SOURCE_CONFIRMED | KEEP definition; revise unit semantics where needed |
| L0 Bi-overlap center | A center built directly from Bi is a practical/local proxy unless the selected minimum-level convention explicitly makes those Bi the valid lower-level trend units. | Lessons 17, 20; community implementations vary | COMMUNITY_VARIANT_NOT_CANONICAL | KEEP only as explicitly labeled proxy; do not emit it as canonical BSP context |
| Zhongshu extension | Extension continues whenever a relevant Z movement interval overlaps `[ZD,ZG]`. Whether the following movement later departs does not retroactively turn an overlapping movement into the departure. | Lesson 20 central theorem 1 | CANONICAL_SOURCE_CONFIRMED | NEEDS_CORRECTION: current look-ahead absorption rule contradicts the theorem |
| Two-center relation | Later `GG < prior DD` gives downward relation; later `DD > prior GG` gives upward relation. ZG/ZD separation with outer-range overlap can imply higher-level center expansion instead. | Lesson 20 central theorem 2 | CANONICAL_SOURCE_CONFIRMED | KEEP_AS_CANONICAL; do not loosen to ZG/ZD to manufacture B1/S1 |
| Trend vs consolidation | Consolidation contains one center; a trend contains at least two same-direction same-level centers. | Lesson 17 | CANONICAL_SOURCE_CONFIRMED | KEEP concept; current partition implementation remains engineering until uniqueness is verified |
| Structural level | K-line timeframe is not the same thing as Chan structural level. Levels arise recursively from completed lower-level trend types. | Lessons 17, 77 | CANONICAL_SOURCE_CONFIRMED | Current timeframe/level separation is correct |
| Recursive level construction | Higher-level objects must be built from completed lower-level trend types under a consistent same-level decomposition, not merely from arbitrary grouped objects. | Lessons 17, 20, 38 and later level discussion | CANONICAL_SOURCE_CONFIRMED at concept level | Current `build_trend_types/build_levels` is ENGINEERING_CHOICE_EXPLICIT and not yet canonical |
| Trend divergence prerequisite | Standard divergence requires a real trend context, not an arbitrary A/B/C or ordinary MACD divergence. | Lessons 24, 27, 37 | CANONICAL_SOURCE_CONFIRMED | KEEP structural prerequisite |
| MACD role | MACD is an auxiliary force-comparison tool, explicitly described as convenient but not absolutely precise. No canonical fixed `0.25 × DIF` eligibility gate exists. | Lesson 24 | CANONICAL_SOURCE_CONFIRMED | Removal of 0.25 hard gate = KEEP_AS_CANONICAL |
| Trend B1/S1 new extreme | In a standard `a+A+b+B+c` trend divergence, c must make a new high in an uptrend / new low in a downtrend. If c does not, the situation is handled as consolidation divergence around the last center, not standard trend divergence. | Lesson 37 | CANONICAL_SOURCE_CONFIRMED | REVISE_OVERMODIFIED: current `(not new_extreme) OR weaker` is too broad |
| B1/S1 force comparison | When c makes the required new extreme, compare the same-direction trend movements' force; MACD area/shape can assist but should not redefine the structural prerequisite. | Lessons 24, 37 | CANONICAL_SOURCE_CONFIRMED + ENGINEERING_CHOICE_EXPLICIT for exact metric | Keep concept; exact `hist area OR DIF extreme` is an engineering proxy and must be labeled/tested as such |
| B2/S2 independence | A same-level B2/S2 can exist when a small-level-to-large-level transition means no standard same-level B1/S1 was emitted. | Lesson 53 | LATER_SOURCE_CLARIFICATION | KEEP_AS_CANONICAL in principle |
| Standard B2/S2 | After a structural high/low, one lower-level move leaves and the next lower-level move returns; no new high/low gives S2/B2 symmetrically. | Lessons 17, 21, 53 | CANONICAL_SOURCE_CONFIRMED / LATER_SOURCE_CLARIFICATION | KEEP concept |
| B2/S2 with consolidation divergence | The return may make a new extreme and still form B2/S2 if a valid consolidation divergence exists. | Lessons 53, 101 | LATER_SOURCE_CLARIFICATION | KEEP concept, but current implementation is too loose |
| Current B2 consolidation-divergence proxy | v2.2 labels a weaker MACD force comparison against `prior_same` as consolidation divergence without requiring the full relevant consolidation/center geometry. | Current code vs lessons 24/53/101 | NEEDS_CORRECTION | REVISE_OVERMODIFIED |
| B3/S3 | A completed lower-level trend type leaves an already formed center; the first completed lower-level trend type returns; its low/high does not re-enter `ZG/ZD`. It must be the first return. | Lesson 20 | CANONICAL_SOURCE_CONFIRMED | Keep only when lower-level unit semantics are valid |
| B3/S3 "absorbed last unit is departure" form | The source requires an already formed center, a lower-level departure, then the first lower-level return. Whether a center-forming/extension unit whose tail exits the center can simultaneously supply the departure leg depends on the exact Z-movement decomposition and is not resolved by the current generic StructUnit abstraction. | Lessons 18, 20 | ENGINEERING_CHOICE_EXPLICIT / NEEDS_SOURCE_MAPPING | DO_NOT_CHANGE_YET; first freeze canonical Z-movement mapping |
| Anchor vs confirmation | Structural anchor and first-observed confirmation must be separate. A trading event cannot be backdated to the anchor. | Original theory's real-time uniqueness principle + causal engineering contract | ENGINEERING_CHOICE_EXPLICIT, source-consistent | KEEP |
| Prefix replay ledger | Recomputing each prefix is a valid anti-lookahead method, but a structure marked confirmed should not later disappear/reassign if the underlying canonical confirmation was correct. | Lessons 65, 77 real-time uniqueness + engineering contract | ENGINEERING_CHOICE_EXPLICIT | KEEP mechanism; add invalidation/reassignment regressions |
| Fixed 1600-bar window | Truncating history at an arbitrary window can change path-dependent inclusion/segment/level state near the left boundary. | Engineering | ENGINEERING_CHOICE_EXPLICIT | Must add warm-up/stability contract; not canonical |
| 480-bar causal replay horizon | This is a performance engineering limit, not a theory definition. | Engineering | ENGINEERING_CHOICE_EXPLICIT | Keep only with explicit scope/seed stability tests |

## 4. Critical source correction: Lesson 37 vs current v2.2

The most important audit result is a direct source contradiction.

Current v2.2 states that for standard B1/S1 trend divergence:

`outside_center AND ((not new_extreme) OR weaker)`

and comments attribute the non-new-extreme case to lesson 38.

That attribution is not valid.

Lesson 37 explicitly distinguishes the cases:

- standard trend divergence in `a+A+b+B+c` requires A and B to be same-level centers;
- c must be a lower-level movement and contain the relevant third-class structure relative to B;
- in an uptrend c must make a new high; in a downtrend c must make a new low;
- if c fails to make the new extreme, the situation is analyzed as consolidation divergence around the last center rather than standard trend divergence.

Lesson 38 discusses same-level decomposition/connection and cannot be transplanted as a redefinition of standard trend B1/S1.

Therefore:

`V2_2_B1_S1_NON_NEW_EXTREME = REVISE_OVERMODIFIED`

This conclusion is source-driven, not count-driven.

## 5. Critical center correction

Current `build_zhongshus` contains a look-ahead rule that can treat a movement which overlaps `[ZD,ZG]` as the "departure" merely because the next movement does not return.

That conflicts with lesson 20 central theorem 1: overlap with `[ZD,ZG]` is the criterion for center extension.

Therefore:

`V2_2_ZHONGSHU_Z_MOVEMENT_MAPPING = NEEDS_CORRECTION`

Important refinement: lesson 20's extension theorem is stated for Z-movements (the lower-level trend types in the same direction as center formation), while the current generic implementation scans every alternating StructUnit. Therefore the safe correction is **not** to mechanically absorb every unit that touches [ZD,ZG]. The implementation must first encode which units are the canonical Z-movements, then apply the overlap theorem to those units. Until that mapping is explicit, the current look-ahead heuristic is not canonical, but it must not be replaced by an equally unsourced all-unit rule.

## 6. Critical segment correction

Lessons 65 and 77 explicitly require the first three Bi of a segment to overlap.

The current segment scanner requires a candidate extreme after at least three Bi and implements feature-sequence confirmation, but it does not explicitly prove/enforce that the first three Bi of every emitted segment overlap before creating the segment.

Therefore every emitted segment cannot yet be called canonical.

`V2_2_SEGMENT_INITIAL_OVERLAP_GUARD = NEEDS_CORRECTION`

Additionally, the current recovery logic may pop and rebuild a previously emitted segment. That is acceptable only for an unfinished/provisional segment. A previously canonical-confirmed segment must not be revised by future bars. A dedicated regression is required.

## 7. B2/S2 audit

Two recent v2.2 directions are source-supported:

1. B2/S2 must not be hard-dependent on a previously emitted same-level B1/S1.
2. A return that creates a new extreme may still be B2/S2 when it forms a genuine consolidation divergence.

However, v2.2 currently computes the second case with a generic weaker-force comparison against `prior_same`, without requiring the structural consolidation context used by the source definition.

Therefore:

- `B2_S2_NO_B1_DEPENDENCY = KEEP_AS_CANONICAL`
- `B2_S2_NEW_EXTREME_PZ_DIVERGENCE_CONCEPT = KEEP_AS_CANONICAL`
- `CURRENT_PZ_DIVERGENCE_IMPLEMENTATION = REVISE_OVERMODIFIED`

## 8. B3/S3 audit

Lessons 18/20 are strict about the semantic objects:

- a center must already be formed;
- a completed lower-level trend type leaves it;
- the first completed lower-level trend type returns;
- the return remains outside the center boundary.

The current explicit "departure unit + next return unit" form can approximate this only when the unit at that level truly represents a completed lower-level trend type.

For the alternative form where the last center-related unit's tail already exits and the following opposite unit is treated as the first return, the source text found so far does not uniquely settle the machine-level attribution because the current StructUnit abstraction does not encode the canonical Z-movement subsequence. Removing it now would itself risk over-modification.

Therefore:

- explicit departure + first return: `KEEP_CONCEPT_REQUIRES_VALID_UNIT_LEVEL`
- absorbed-last-unit form: `DO_NOT_CHANGE_YET__NEEDS_Z_MOVEMENT_MAPPING`

## 9. L0 / recursive level audit

The current code honestly marks L0 Bi-level centers as `canonical=False`, which is good.

However, signals are still emitted from all levels, including L0, while the product/source metadata is named `CHAN_STANDALONE_BSP_CANONICAL_V2_2`.

That overstates canonical status.

Until a minimum-level convention is explicitly frozen and validated:

- L0 Bi-center = local engineering proxy;
- L1+ may only be called canonical when their segment/lower-level trend units have passed the segment and recursion audits;
- all BSP labels should carry whether their source level is canonical or proxy.

`CHAN_SOURCE = CHAN_STANDALONE_BSP_CANONICAL_V2_2` is therefore inaccurate at this stage.

## 10. Causality audit

The separation of:

- `anchor_index`
- first-observed `confirm_index`

is correct and must remain.

`replay_first_observed_signals` is a strong anti-lookahead design because it recomputes finite prefixes.

But there is an unresolved canonicality test:

- after a signal is first observed from a "confirmed" structural object, can future bars cause that structural object to disappear or be reassigned?

If yes, the ledger is correctly remembering what the engine said at the time, but the engine's earlier "confirmed" classification was premature.

Required regression categories:

1. confirmed Bi endpoint never later changes;
2. confirmed segment endpoint never later changes;
3. confirmed Zhongshu seed/boundary never retroactively changes under canonical rules;
4. confirmed BSP identity does not depend on future structural reassignment.

## 11. Open-source cross-check outcome

Cross-checked as implementation references, not definition authorities:

- `Vespa314/chan.py`
- `waditu/czsc`
- `yijixiuxin/chanlun-pro`
- `mikonos/chanlun-kline`
- `neil-pan-s/one-quant-doc` (no useful indexed evidence found in first pass)

Observed pattern:

- mature projects expose multiple Bi/segment/Zhongshu/divergence options;
- feature-sequence segment handling is recognized as complex;
- some projects use practical Bi-level centers or configurable center-position relations;
- force/divergence thresholds vary by implementation.

Conclusion:

`OPEN_SOURCE_VARIANTS != CANONICAL_AUTHORITY`

They are useful to reveal ambiguity and edge cases, but do not override the original source.

## 12. T2 — v2.2 change audit

### KEEP

- removal of proprietary `0.25 × DIF` hard eligibility gate;
- strict GG/DD same-level center relation;
- B2/S2 not hard-dependent on emitted B1/S1;
- B2/S2 consolidation-divergence case as a concept;
- anchor/confirm separation;
- FIRST_OBSERVED prefix replay as a causality mechanism;
- Chan independence from SLTD/V7/E/5s.

### REVISE_OVERMODIFIED

1. B1/S1 accepting `not new_extreme` as standard trend divergence.
2. B2/S2 "consolidation divergence" being reduced to generic weaker MACD force without sufficient structural context.

### NEEDS_CORRECTION / CANNOT YET CERTIFY

1. Zhongshu implementation lacks an explicit canonical Z-movement mapping; current look-ahead heuristic is not certifiable yet;
2. B3/S3 form attribution depends on that unresolved Z-movement mapping and must not be changed prematurely;
3. segment first-three-Bi overlap is not explicitly enforced for every emitted segment;
4. feature-sequence second-case/recovery behavior requires adversarial fixtures;
5. recursive `build_trend_types/build_levels` remains an engineering partition, not proven canonical;
6. L0 proxy signals must not be represented as canonical;
7. fixed left-window boundary and replay horizon require structural stability contracts.

## 13. Mandatory implementation order after this audit

Do not perform one large rewrite.

Correct only source-confirmed mismatches in this order:

### C1 — Definition/status correction
- stop labeling the whole engine `CANONICAL_V2_2`;
- preserve v2.2 as candidate pending correction;
- expose proxy/canonical level status.

### C2 — B1/S1 correction
- standard trend B1/S1 requires the c movement to make the required new extreme and then show weaker force;
- non-new-extreme case must not emit standard trend B1/S1 merely for that reason.

### C3 — Zhongshu Z-movement mapping
- first encode the center-formation direction and canonical Z-movement subsequence;
- only then apply lesson-20 extension/new-center rules;
- do not replace the current heuristic with an all-unit overlap heuristic.

### C4 — B3/S3 after C3
- re-audit both engineering forms against the explicit Z-movement mapping;
- change only the form that becomes demonstrably inconsistent;
- require completed lower-level departure/return semantics.

### C5 — B2/S2 structural consolidation-divergence correction
- preserve independence from B1/S1;
- preserve source-supported consolidation-divergence case;
- require the correct consolidation/center structural context before force comparison.

### C6 — Segment canonical gate
- enforce first-three-Bi overlap;
- add lesson-67/71/77/78 first/second-case fixtures;
- prove that confirmed segment endpoints are never retroactively changed.

### C7 — Recursive levels
- freeze a same-level decomposition contract;
- certify L1+ only after segment and trend-type unit semantics pass.

### C8 — Causal regression
- prefix stability tests for Bi/segment/Zhongshu/BSP;
- no PnL/signal-count optimization.

## 14. Tests that must change

Current tests that explicitly require B1/S1 without a new extreme encode the over-modified behavior and must be removed or rewritten:

- `test_s1_can_occur_without_a_new_high`
- `test_b1_can_occur_without_a_new_low`
- `test_s1_can_diverge_without_new_high`

They should be replaced with tests asserting that these cases are not standard trend B1/S1 and, where the proper structural prerequisites are constructed, may be classified as consolidation-divergence contexts instead.

The B2/S2 tests should be strengthened so that a generic weak return is insufficient without a valid consolidation structure.

## 15. Closure state

T1 canonical matrix: **COMPLETE WITH EXPLICIT UNRESOLVED ENGINEERING MAPPINGS**  
T2 audit against v2.2: **COMPLETE FOR ADMISSION/REJECTION DECISIONS; CENTER/B3 HELD FROM CODE CHANGE PENDING Z-MAPPING**  
Code correction: **NOT STARTED IN THIS AUDIT DOCUMENT**  
Canonical engine closure: **NOT COMPLETE**

Blocking corrections were identified from source theory; therefore the next phase may modify code, but only the items listed above and only with regression fixtures tied to the cited source rules.

`CHAN_CANONICAL_THEORY_AUDIT_v1 = T1_T2_CLOSED_WITH_B1_CORRECTION_AND_CENTER_B3_MAPPING_BLOCKER`
