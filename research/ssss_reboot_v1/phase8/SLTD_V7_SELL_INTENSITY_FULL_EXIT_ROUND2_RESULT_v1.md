# SLTD V7 Sell Intensity & Full Exit Study v1 — Round 2

状态：**IMPLEMENTED_AND_VERIFIED**

- 股票：20
- 周期：1h / 4h
- series：40
- 正式比较窗口：最近约 180 天
- 5 bps primary；10 bps stress
- 每个 series 的冻结 V7 baseline parity：PASS

## 5 bps 核心结果

| Variant | Status | Better Return | Better MDD | Better Calmar | Median ΔReturn | Median ΔMDD | Median ΔCalmar | S3 Exec | C2 exits |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S3_CUR25 | ADVANCE_TO_OOS | 21/40 | 26/40 | 22/40 | +0.06% | +0.06% | +0.0139 | 88 | 35 |
| S3_CUR50 | ADVANCE_TO_OOS | 23/40 | 30/40 | 27/40 | +0.27% | +0.44% | +0.0704 | 88 | 35 |
| S3_TARGET50 | ADVANCE_TO_OOS | 18/40 | 27/40 | 22/40 | +0.00% | +0.17% | +0.0077 | 78 | 35 |
| S3_TARGET25 | ADVANCE_TO_OOS | 19/40 | 30/40 | 23/40 | +0.00% | +0.48% | +0.0695 | 82 | 35 |

## S3_CUR25 — ADVANCE_TO_OOS
- 1h: Better Calmar 10/20; Median ΔReturn -0.03%; Median ΔMDD +0.00%; Median ΔCalmar +0.0035
- 4h: Better Calmar 12/20; Median ΔReturn +0.17%; Median ΔMDD +0.15%; Median ΔCalmar +0.0203
- 10 bps stress: Better Calmar 22/40; Median ΔReturn +0.00%; Median ΔMDD +0.05%; Median ΔCalmar +0.0115

## S3_CUR50 — ADVANCE_TO_OOS
- 1h: Better Calmar 12/20; Median ΔReturn +0.06%; Median ΔMDD +0.33%; Median ΔCalmar +0.0303
- 4h: Better Calmar 15/20; Median ΔReturn +0.53%; Median ΔMDD +0.67%; Median ΔCalmar +0.1393
- 10 bps stress: Better Calmar 26/40; Median ΔReturn +0.26%; Median ΔMDD +0.43%; Median ΔCalmar +0.0673

## S3_TARGET50 — ADVANCE_TO_OOS
- 1h: Better Calmar 12/20; Median ΔReturn -0.19%; Median ΔMDD +0.33%; Median ΔCalmar +0.0317
- 4h: Better Calmar 10/20; Median ΔReturn +0.01%; Median ΔMDD +0.00%; Median ΔCalmar +0.0021
- 10 bps stress: Better Calmar 21/40; Median ΔReturn +0.00%; Median ΔMDD +0.15%; Median ΔCalmar +0.0055

## S3_TARGET25 — ADVANCE_TO_OOS
- 1h: Better Calmar 11/20; Median ΔReturn -0.32%; Median ΔMDD +0.62%; Median ΔCalmar +0.0342
- 4h: Better Calmar 12/20; Median ΔReturn +0.19%; Median ΔMDD +0.08%; Median ΔCalmar +0.1436
- 10 bps stress: Better Calmar 24/40; Median ΔReturn +0.00%; Median ΔMDD +0.47%; Median ΔCalmar +0.0529

## 边界

- Round 2 只验证 S3 卖出强度的跨周期通用性，不新增 FULL EXIT 条件。
- S1/S2、S3 FULL、Direct C2、ZD1 FULL 已按 Round 1 门槛停留在 WATCH/REJECT，不进入本轮。
- 只有 ADVANCE_TO_OOS 才可进入 Round 3 fresh-stock OOS。
- 本轮不修改正式 V7。

`SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND2 = IMPLEMENTED_AND_VERIFIED`
