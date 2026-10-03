# Chan × SLTD C0-A Reconstruction Closure v1

Status: **IMPLEMENTED_AND_VERIFIED**
Date: 2026-10-03

Parent protocol:
- `CHAN_SLTD_RESEARCH_PROTOCOL_V1 = FROZEN_BEFORE_ENGINE_RECONSTRUCTION`

## Scope closed in C0-A

Implemented and verified without PnL:

1. causal inclusion handling;
2. three-unit fractals after inclusion handling;
3. separate Bi source variants:
   - `strict77`
   - `late106`
4. feature-sequence segment reconstruction;
5. lesson-67 / 71 / 78 segment cases;
6. synthetic lesson-81 corrected topology:
   - 5 above 7 -> three segments;
   - 5 not above 7 -> one continuing segment;
7. explicit `anchor_raw_index` vs `confirm_raw_index`;
8. prefix replay for first-observed segment confirmation.

## Important bug caught during verification

The first CI run exposed a timestamp-index bug in synthetic fixtures:
default raw indices collapsed anchor and confirmation times.

The bug was corrected before closure.

No Chan structural rule was changed by that fix.

## CI

- failed diagnostic run: `37087542471`
- verified run: `37087577510`
- final result: **SUCCESS**

## Not yet closed

C0 as a whole remains open.

Still required:
- canonical Zhongshu reconstruction;
- consolidation / trend classification;
- PZ / QS divergence;
- BSP1 / BSP2 / BSP3;
- provisional / confirmed / invalidated handling for those higher objects;
- cross-implementation checks on complete structure chains;
- final Bi variant decision without using PnL.

## State

`CHAN_C0A_CORE_GEOMETRY = IMPLEMENTED_AND_VERIFIED`

`CHAN_ENGINE_RECONSTRUCTION = IN_PROGRESS`
