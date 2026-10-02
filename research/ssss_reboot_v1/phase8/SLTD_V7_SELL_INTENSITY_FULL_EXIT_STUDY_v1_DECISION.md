# SLTD V7 Sell Intensity & Full Exit Study v1 — Final Decision

研究状态：**CLOSED**

正式 V7 变更：**NONE**

V6 与 V7 冻结基线均保持不变。

## Source of truth

- V6 rollback baseline:
  - `baseline/sltd-v6-15rules-position-v1`
  - `05be43e350d9193ba01a2748ef4c0267438a84b1`
- V7 candidate baseline:
  - `candidate/sltd-v7-12rules-position-v1`
  - `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`

## Pre-study finding

ABT 4h audit established that the sell problem was taxonomy coverage, not an executor bug.

The current frozen ordinary SELL semantics are also confirmed to be "sell 25% of current remaining position", producing a geometric sequence such as 100% -> 75% -> 56.25% -> 42.19%.

## Daily79 precursor

Run `37012533636` completed successfully and was archived at commit
`8565a765a6f37f7372b4e282cc514e6c90bc8b82`.

Long-daily Universal Sell validation advanced S1, S2 and S3, while S5/C3 remained rejected.

## Round 1 — 79 stocks, long 1d

Run: `37019844530`

Verified result commit:
`39888969074101e3e6034bdcb4550ea4e30e70fe`

Status: `IMPLEMENTED_AND_VERIFIED`

Key result:

- S1 and S2 became progressively worse as sell intensity increased.
- S3 was the only trigger family where stronger selling improved risk-adjusted results without immediately destroying return.
- S3 CUR25, CUR50, TARGET50 and TARGET25 advanced to Round 2.
- S3 FULL improved MaxDD/Calmar but damaged CAGR enough to fail the frozen advancement gate.
- DIRECT_C2_FULL was `REJECTED_NOT_ADMITTED`.
- ZD1-based full-exit escalations remained `WATCH` with large return damage.

Therefore no new FULL EXIT condition was admitted.

## Round 2 — 20 stocks x 1h/4h

Run: `37020767460`

Verified result commit:
`bf5f38158520a12ea96c3e19a159836380598f8d`

Status: `IMPLEMENTED_AND_VERIFIED`

All 40 series passed frozen V7 baseline parity.

All four S3 intensity variants passed the pre-frozen cross-timeframe gate:

- S3_CUR25: Better Calmar 22/40; Median ΔCalmar +0.0139
- S3_CUR50: Better Calmar 27/40; Median ΔCalmar +0.0704
- S3_TARGET50: Better Calmar 22/40; Median ΔCalmar +0.0077
- S3_TARGET25: Better Calmar 23/40; Median ΔCalmar +0.0695

S3_CUR50 showed the strongest balanced Round-2 breadth, but Round 2 was not allowed to admit a formal rule without fresh-stock OOS.

## Round 3 — 20 fresh stocks x 1h/4h/1d

Run: `37021322192`

Verified result commit:
`ebec64607039cfc7647ae72dccfc2eea2aac4616`

Status: `IMPLEMENTED_AND_VERIFIED`

Fresh OOS overlap with prior design universes: 0.

All 60 series passed frozen V7 baseline parity.

Pre-frozen advancement requirement: Better Calmar >= 33/60 plus the other return/drawdown/timeframe gates.

Results:

| Variant | Status | Better Return | Better MDD | Better Calmar | Median ΔReturn | Median ΔMDD | Median ΔCalmar |
|---|---|---:|---:|---:|---:|---:|---:|
| S3_CUR25 | WATCH | 31/60 | 27/60 | 31/60 | +0.01% | +0.00% | +0.0003 |
| S3_CUR50 | WATCH | 26/60 | 32/60 | 27/60 | +0.00% | +0.00% | +0.0000 |
| S3_TARGET50 | WATCH | 27/60 | 26/60 | 28/60 | +0.00% | +0.00% | +0.0000 |
| S3_TARGET25 | WATCH | 26/60 | 37/60 | 28/60 | +0.00% | +0.00% | +0.0000 |

No variant passed the OOS gate.

Important daily OOS deterioration for stronger intensity:

- S3_CUR25 1d Median ΔReturn: +0.00%; Better Calmar 10/20
- S3_CUR50 1d Median ΔReturn: -1.43%; Better Calmar 6/20
- S3_TARGET50 1d Median ΔReturn: -3.19%; Better Calmar 8/20
- S3_TARGET25 1d Median ΔReturn: -6.01%; Better Calmar 7/20

This is direct evidence against admitting a stronger universal S3 sell intensity at this time.

## Final candidate states

- S3_CUR25: `WATCH` — closest to OOS admission, but 31/60 is below the frozen 33/60 requirement.
- S3_CUR50: `WATCH` — strong Round 2, but insufficient fresh-stock OOS breadth and weaker long-daily return.
- S3_TARGET50: `WATCH` — insufficient OOS breadth and material daily return damage.
- S3_TARGET25: `WATCH` — drawdown improvement is real, but daily return damage is too large for admission.
- S3_FULL: `WATCH_NOT_ADMITTED`
- S1/S2 strong/full intensity: `WATCH_NOT_ADMITTED`
- DIRECT_C2_FULL: `REJECTED_NOT_ADMITTED`
- ZD1 full-exit escalations: `WATCH_NOT_ADMITTED`

## Decision

1. Do **not** change V7 ordinary SELL sizing.
2. Do **not** add S3 as a formal V7 SELL rule yet.
3. Do **not** add a new universal FULL EXIT rule.
4. Keep the existing frozen C2 semantics unchanged.
5. Do **not** run Round 4 Crypto for this study, because the pre-frozen protocol required stock OOS admission first.
6. Preserve S3_CUR25 as the leading WATCH hypothesis for a future genuinely independent dataset; do not continue tuning on the same samples.

This study is intentionally closed here to prevent threshold relaxation, repeated sample reuse, and infinite research.

`SLTD_V7_SELL_INTENSITY_FULL_EXIT_STUDY_V1 = CLOSED_NO_ADMISSION`
