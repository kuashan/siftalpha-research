# SLTD V7 Sell Intensity & Full Exit Study v1 — Round 3 Fresh-Stock OOS

状态：**IMPLEMENTED_AND_VERIFIED**

- Fresh stocks：20
- 周期：1h / 4h / 1d
- series：60
- 与 prior design universes overlap：0
- 每个 series 冻结 V7 baseline parity：PASS

## 5 bps OOS 核心结果

| Variant | Status | Better Return | Better MDD | Better Calmar | Median ΔReturn | Median ΔMDD | Median ΔCalmar | S3 Exec | C2 exits |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S3_CUR25 | WATCH | 31/60 | 27/60 | 31/60 | +0.01% | +0.00% | +0.0003 | 195 | 99 |
| S3_CUR50 | WATCH | 26/60 | 32/60 | 27/60 | +0.00% | +0.00% | +0.0000 | 195 | 99 |
| S3_TARGET50 | WATCH | 27/60 | 26/60 | 28/60 | +0.00% | +0.00% | +0.0000 | 175 | 99 |
| S3_TARGET25 | WATCH | 26/60 | 37/60 | 28/60 | +0.00% | +0.00% | +0.0000 | 189 | 99 |

## S3_CUR25 — WATCH
- 1h: Better Return 13/20; Better MDD 13/20; Better Calmar 13/20; Median ΔReturn +0.29%; Median ΔMDD +0.00%; Median ΔCalmar +0.0342
- 4h: Better Return 9/20; Better MDD 7/20; Better Calmar 8/20; Median ΔReturn +0.00%; Median ΔMDD +0.00%; Median ΔCalmar +0.0000
- 1d: Better Return 9/20; Better MDD 7/20; Better Calmar 10/20; Median ΔReturn +0.00%; Median ΔMDD +0.00%; Median ΔCalmar +0.0003
- 10 bps stress: Better Calmar 31/60; Median ΔReturn +0.01%; Median ΔMDD +0.00%; Median ΔCalmar +0.0000

## S3_CUR50 — WATCH
- 1h: Better Return 11/20; Better MDD 12/20; Better Calmar 12/20; Median ΔReturn +0.40%; Median ΔMDD +0.11%; Median ΔCalmar +0.0499
- 4h: Better Return 9/20; Better MDD 10/20; Better Calmar 9/20; Median ΔReturn +0.00%; Median ΔMDD +0.00%; Median ΔCalmar +0.0000
- 1d: Better Return 6/20; Better MDD 10/20; Better Calmar 6/20; Median ΔReturn -1.43%; Median ΔMDD +0.00%; Median ΔCalmar -0.0022
- 10 bps stress: Better Calmar 26/60; Median ΔReturn +0.00%; Median ΔMDD +0.00%; Median ΔCalmar +0.0000

## S3_TARGET50 — WATCH
- 1h: Better Return 13/20; Better MDD 11/20; Better Calmar 13/20; Median ΔReturn +0.39%; Median ΔMDD +0.01%; Median ΔCalmar +0.0502
- 4h: Better Return 7/20; Better MDD 5/20; Better Calmar 7/20; Median ΔReturn +0.00%; Median ΔMDD +0.00%; Median ΔCalmar +0.0000
- 1d: Better Return 7/20; Better MDD 10/20; Better Calmar 8/20; Median ΔReturn -3.19%; Median ΔMDD +0.00%; Median ΔCalmar +0.0000
- 10 bps stress: Better Calmar 27/60; Median ΔReturn +0.00%; Median ΔMDD +0.00%; Median ΔCalmar +0.0000

## S3_TARGET25 — WATCH
- 1h: Better Return 12/20; Better MDD 15/20; Better Calmar 12/20; Median ΔReturn +0.38%; Median ΔMDD +0.18%; Median ΔCalmar +0.0602
- 4h: Better Return 8/20; Better MDD 10/20; Better Calmar 9/20; Median ΔReturn +0.00%; Median ΔMDD +0.00%; Median ΔCalmar +0.0000
- 1d: Better Return 6/20; Better MDD 12/20; Better Calmar 7/20; Median ΔReturn -6.01%; Median ΔMDD +0.11%; Median ΔCalmar -0.0111
- 10 bps stress: Better Calmar 27/60; Median ΔReturn +0.00%; Median ΔMDD +0.00%; Median ΔCalmar +0.0000

## Governance（治理）

- ADVANCE_TO_CRYPTO 表示股票 OOS 已通过；Crypto 只能测试跨资产可移植性，不能反向改写股票结论。
- 本轮不把多个通过候选强行压成单一 winner；pairwise 数据保存在 JSON，供后续股票选择决策使用。
- 本轮不修改正式 V7。

`SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND3_OOS = IMPLEMENTED_AND_VERIFIED`
