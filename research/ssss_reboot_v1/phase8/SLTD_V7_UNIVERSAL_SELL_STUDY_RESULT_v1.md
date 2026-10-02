# SLTD V7 Universal Sell Study（通用卖出研究）Result v1

状态：IMPLEMENTED_AND_VERIFIED

- 股票：20
- 周期：1h, 4h, 1d
- series：60
- 正式比较窗口：最近约 180 天
- 摩擦：5.0 bps

## 汇总

| Candidate | Status | Better Calmar | Better MDD | Better Return | Median ΔReturn | Median ΔMDD | Median ΔCalmar | Added SELL | 5-bar rebuy |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S1_MATURE_BLUE_UPPER_WICK | WATCH | 29/60 | 40/60 | 30/60 | +0.0000 | +0.0045 | +0.0000 | 213 | 34/213 |
| S2_MATURE_BLUE_UPPER_ANY | WATCH | 31/60 | 41/60 | 30/60 | +0.0002 | +0.0048 | +0.0039 | 242 | 34/242 |
| S3_MATURE_BLUE_WICK_CONFIRM_DOWN | WATCH | 21/60 | 30/60 | 22/60 | +0.0000 | +0.0000 | +0.0000 | 96 | 25/96 |
| S4_BLUE_TO_GRAY_UPPER | WATCH | 6/60 | 6/60 | 6/60 | +0.0000 | +0.0000 | +0.0000 | 6 | 2/6 |
| S5_BLUE_TO_GRAY_BEARISH | REJECT_NOT_ADMITTED | 18/60 | 48/60 | 18/60 | -0.0082 | +0.0226 | -0.1728 | 374 | 54/374 |
| C1_S1_PLUS_S4 | WATCH | 29/60 | 42/60 | 29/60 | +0.0000 | +0.0053 | +0.0000 | 218 | 36/218 |
| C2_S3_PLUS_S4 | WATCH | 23/60 | 33/60 | 23/60 | +0.0000 | +0.0000 | +0.0000 | 102 | 27/102 |
| C3_S1_PLUS_S5 | REJECT_NOT_ADMITTED | 22/60 | 55/60 | 23/60 | -0.0024 | +0.0303 | -0.1000 | 585 | 85/585 |

## S1_MATURE_BLUE_UPPER_WICK — WATCH
- 1h: better Calmar 12/20; median ΔReturn +0.0024; median ΔMDD +0.0036; median ΔCalmar +0.0453
- 4h: better Calmar 14/20; median ΔReturn +0.0063; median ΔMDD +0.0146; median ΔCalmar +0.0947
- 1d: better Calmar 3/20; median ΔReturn +0.0000; median ΔMDD +0.0000; median ΔCalmar +0.0000

## S2_MATURE_BLUE_UPPER_ANY — WATCH
- 1h: better Calmar 13/20; median ΔReturn +0.0024; median ΔMDD +0.0040; median ΔCalmar +0.0671
- 4h: better Calmar 15/20; median ΔReturn +0.0096; median ΔMDD +0.0146; median ΔCalmar +0.1053
- 1d: better Calmar 3/20; median ΔReturn +0.0000; median ΔMDD +0.0000; median ΔCalmar +0.0000

## S3_MATURE_BLUE_WICK_CONFIRM_DOWN — WATCH
- 1h: better Calmar 9/20; median ΔReturn -0.0003; median ΔMDD +0.0000; median ΔCalmar -0.0030
- 4h: better Calmar 12/20; median ΔReturn +0.0013; median ΔMDD +0.0020; median ΔCalmar +0.0241
- 1d: better Calmar 0/20; median ΔReturn +0.0000; median ΔMDD +0.0000; median ΔCalmar +0.0000

## S4_BLUE_TO_GRAY_UPPER — WATCH
- 1h: better Calmar 4/20; median ΔReturn +0.0000; median ΔMDD +0.0000; median ΔCalmar +0.0000
- 4h: better Calmar 2/20; median ΔReturn +0.0000; median ΔMDD +0.0000; median ΔCalmar +0.0000
- 1d: better Calmar 0/20; median ΔReturn +0.0000; median ΔMDD +0.0000; median ΔCalmar +0.0000

## S5_BLUE_TO_GRAY_BEARISH — REJECT_NOT_ADMITTED
- 1h: better Calmar 7/20; median ΔReturn -0.0619; median ΔMDD +0.0396; median ΔCalmar -1.2891
- 4h: better Calmar 6/20; median ΔReturn -0.0189; median ΔMDD +0.0231; median ΔCalmar -0.2181
- 1d: better Calmar 5/20; median ΔReturn +0.0000; median ΔMDD +0.0047; median ΔCalmar +0.0000

## C1_S1_PLUS_S4 — WATCH
- 1h: better Calmar 13/20; median ΔReturn +0.0024; median ΔMDD +0.0049; median ΔCalmar +0.0671
- 4h: better Calmar 13/20; median ΔReturn +0.0057; median ΔMDD +0.0153; median ΔCalmar +0.0947
- 1d: better Calmar 3/20; median ΔReturn +0.0000; median ΔMDD +0.0000; median ΔCalmar +0.0000

## C2_S3_PLUS_S4 — WATCH
- 1h: better Calmar 11/20; median ΔReturn +0.0005; median ΔMDD +0.0021; median ΔCalmar +0.0163
- 4h: better Calmar 12/20; median ΔReturn +0.0020; median ΔMDD +0.0050; median ΔCalmar +0.0298
- 1d: better Calmar 0/20; median ΔReturn +0.0000; median ΔMDD +0.0000; median ΔCalmar +0.0000

## C3_S1_PLUS_S5 — REJECT_NOT_ADMITTED
- 1h: better Calmar 6/20; median ΔReturn -0.0836; median ΔMDD +0.0554; median ΔCalmar -1.2425
- 4h: better Calmar 10/20; median ΔReturn -0.0031; median ΔMDD +0.0426; median ΔCalmar -0.0397
- 1d: better Calmar 6/20; median ΔReturn +0.0000; median ΔMDD +0.0130; median ΔCalmar +0.0000

## 边界

- 本轮是 20 股票 × 1h/4h/1d 的 discovery/screen，不是最终 OOS。
- 没有修改正式 V7 12 条规则、25% 仓位政策或 C2。
- ADVANCE_TO_OOS 只代表值得进入 fresh-stock 独立验证。
