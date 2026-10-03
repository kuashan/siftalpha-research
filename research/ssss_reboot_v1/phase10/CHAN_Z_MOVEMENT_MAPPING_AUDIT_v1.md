# CHAN_Z_MOVEMENT_MAPPING_AUDIT_v1

Status: **MAPPING_FROZEN_FOR_DIAGNOSTIC__NO_CENTER_CODE_CHANGE_YET**

Date: 2026-10-03
Repository: `kuashan/siftalpha-research`
Branch: `feature/chan-standalone-v2`
Remote HEAD before this document: `ce0291ae41966ce2a0bce754828b9ac0a4372b55`

## 0. Purpose

This document resolves the representation boundary between the original Chan
`Z走势段 / Zn` definition and the current generic `StructUnit` sequence.

It is deliberately written **before** changing `build_zhongshus()`,
B2/S2, or B3/S3.

No signal-count target, PnL target, or single-symbol observation is admissible
as theory evidence.

## 1. Original-source definition frozen here

For one Zhongshu, the first three consecutive completed lower-level trend
types form the seed when their price ranges overlap.

Let those three lower-level movements be:

`A -> B -> C`

A and C have the same direction; B is opposite.

The original lesson 20 then defines the lower-level movements whose direction
is the same as the Zhongshu-forming direction as the **Z movements**:

`Z1, Z2, Z3, ...`

Therefore, in a correctly alternating lower-level movement sequence whose
seed begins at index `i`, the canonical Z-movement candidate indices are:

`i, i+2, i+4, i+6, ...`

not every consecutive `StructUnit`.

For every Z movement `Zn`:

- `gn = high(Zn)`
- `dn = low(Zn)`
- `GG = max(gn)`
- `DD = min(dn)`
- the initial Zhongshu interval is determined from the first two Z movements:
  `ZG = min(g1, g2)`
  `ZD = max(d1, d2)`

The center-extension theorem is applied to these Z movements:
`[dn, gn]` overlapping `[ZD, ZG]` means extension.

This theorem must **not** be mechanically applied to every intervening
opposite-direction lower-level movement.

## 2. Third-class point mapping

The source definition requires:

1. an already formed Zhongshu;
2. one **completed lower-level trend type** leaves the Zhongshu;
3. the **first completed lower-level trend type** returning toward it;
4. for B3, return low does not break `ZG`;
5. for S3, return high does not break `ZD`.

Therefore B3/S3 must be represented with explicit semantic roles:

- `departure_unit`
- `first_return_unit`

A generic condition such as "some unit is outside the box" is insufficient.

## 3. Required machine preconditions

Before a `StructUnit` sequence can be used as a canonical lower-level
movement stream for Zhongshu construction, the following must be true:

### M1 — Completed
Only completed units with a valid confirmation index participate.

### M2 — Time order
Units are strictly ordered and contiguous in structural sequence.

### M3 — Direction alternation
Adjacent lower-level trend types alternate direction.

If adjacent units have the same direction, the stream has not yet been
normalized into the canonical lower-level trend-type sequence and must not be
fed directly to the Z-movement parity rule.

### M4 — Seed overlap
For a seed `A,B,C`, all three lower-level movement intervals have a common
overlap.

### M5 — Z parity
Once the seed starts at `i`, `A,C,E,...` (same parity) are the Z-movement
subsequence. Their direction must remain equal to the seed's Z direction.

## 4. Audit of current v2.2 representation

Current `build_zhongshus()`:

- consumes every completed `StructUnit`;
- seeds from three consecutive units;
- computes `ZG/ZD` from all three interval highs/lows;
- defines `touches()` for every later alternating unit;
- uses one-unit look-ahead to decide whether to absorb a touching unit or
  treat it as departure.

This is a practical heuristic, but it does **not explicitly encode Zn**.

Important consequence:

`CURRENT_BUILD_ZHONGSHUS != PROVEN_CANONICAL_Z_MOVEMENT_IMPLEMENTATION`

This does not automatically mean every output center is wrong. It means the
implementation cannot be certified until the lower-level unit stream and its
Z parity are proven and fixtures demonstrate equivalence.

## 5. Why no immediate rewrite is allowed

A naive replacement such as:

> "absorb every unit that overlaps [ZD,ZG]"

would also be wrong, because lesson 20's extension theorem applies to the Z
movements, not indiscriminately to every alternating unit.

Likewise, deleting one of the current B3 engineering forms before identifying
which unit is the canonical departure and which is the first return could
create a second over-modification.

Therefore:

- do not change B2/S2 here;
- do not change B3/S3 here;
- do not rewrite Zhongshu extension here.

First diagnose the actual L1+ `StructUnit` streams.

## 6. Diagnostic required before implementation

Across the frozen historical snapshot, for every formal level L1+ record:

- unit count;
- completed unit count;
- adjacent same-direction violations;
- time-order violations;
- candidate seed count;
- seed-overlap count;
- for each seed, whether same-parity units preserve Z direction;
- current Zhongshu count;
- candidate canonical Z-seed count.

The purpose is **structural falsification only**.

No minimum count is required for PASS.

## 7. Decision gate

### If L1 segment streams satisfy M1-M5

Implement a dedicated Zhongshu constructor whose internal model explicitly
stores:

- `z_direction`
- `z_unit_indices`
- `ZG/ZD/GG/DD`
- center seed confirmation
- departure candidate
- first-return candidate

Then compare the new constructor against exact lesson-derived fixtures before
using market data.

### If L1 segment streams violate M1-M5

Do not patch Zhongshu around the malformed stream.

Return to segment / lower-level trend-type normalization first.

## 8. Current closure

Original-source Z mapping: **FROZEN**
Current generic `StructUnit -> Zn` equivalence: **NOT PROVEN**
Zhongshu code change: **BLOCKED PENDING DIAGNOSTIC**
B2/B3 formula change: **BLOCKED PENDING Z MAPPING**

`CHAN_Z_MOVEMENT_MAPPING_AUDIT_v1 = READY_FOR_STRUCTURAL_DIAGNOSTIC`
