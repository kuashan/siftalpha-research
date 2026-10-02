# SLTD V7 Universal Sell Daily-79 Result v1

状态：IMPLEMENTED_AND_VERIFIED

- 股票：79
- 周期：1d
- 正式区间：2020-01-02 ~ 2026-09-30
- 摩擦：5.0 bps

| Candidate | Status | Impacted | Better Calmar | Better MDD | Better Return | Median ΔReturn | Median ΔMDD | Median ΔCalmar | SELL Exec | 5-bar rebuy |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S1_MATURE_BLUE_UPPER_WICK | ADVANCE_TO_OOS | 79/79 | 47/79 | 60/79 | 39/79 | -0.0003 | +0.0081 | +0.0077 | 1239 | 188/1239 |
| S2_MATURE_BLUE_UPPER_ANY | ADVANCE_TO_OOS | 79/79 | 46/79 | 61/79 | 38/79 | -0.0039 | +0.0093 | +0.0035 | 1349 | 191/1349 |
| S3_MATURE_BLUE_WICK_CONFIRM_DOWN | ADVANCE_TO_OOS | 78/79 | 47/79 | 54/79 | 41/79 | +0.0065 | +0.0034 | +0.0066 | 562 | 132/562 |
| S4_BLUE_TO_GRAY_UPPER | WATCH | 54/79 | 21/79 | 23/79 | 20/79 | +0.0000 | +0.0000 | +0.0000 | 80 | 23/80 |
| S5_BLUE_TO_GRAY_BEARISH | REJECT_NOT_ADMITTED | 79/79 | 17/79 | 53/79 | 11/79 | -0.4636 | +0.0362 | -0.1186 | 1956 | 293/1956 |
| C1_S1_PLUS_S4 | WATCH | 79/79 | 43/79 | 63/79 | 37/79 | -0.0095 | +0.0091 | +0.0045 | 1319 | 211/1319 |
| C2_S3_PLUS_S4 | WATCH | 79/79 | 41/79 | 56/79 | 36/79 | -0.0149 | +0.0035 | +0.0021 | 642 | 155/642 |
| C3_S1_PLUS_S5 | REJECT_NOT_ADMITTED | 79/79 | 22/79 | 66/79 | 11/79 | -0.4131 | +0.0668 | -0.0943 | 3138 | 473/3138 |

## 边界

- 使用冻结的 79 股票日线快照，避免实时行情漂移。
- 这是对 Round-1 跨周期发现的长期 1d 验证，不修改正式 V7。
- 只有同时经 1h / 4h 与长周期 1d 支持的候选，才值得进入 fresh-stock OOS。
