# SLTD V8 Universal Sell Study R1 Result

状态：IMPLEMENTED_AND_VERIFIED

Run: 37011787195  
Artifact: 11228321473  
Branch base: feature/sltd-v7-market-window-v8 @ 08c3415ef6cfd123b226c0a0f848fa8b3c6b4e86

## 范围

- 20 股票：AAPL, MSFT, NVDA, AMZN, META, TSLA, WMT, COST, ABT, LLY, UNH, JPM, BAC, V, CAT, XOM, NEE, PLD, IBM, DIS
- 周期：1h / 4h / 1d
- 正式窗口：2025-02-03 .. 2026-09-30
- 交易摩擦：5 bps
- 共 60 个 symbol × timeframe 单元
- 12 条 V7 规则、25% 仓位管理、NO_CHANGE_MIXED、C2 均保持不变，只附加候选 SELL 做对照。

## 基线

V7 BASE 中位结果：
- 1h：Return +10.87%，MaxDD -22.79%，Calmar 0.2965，turnover 10.4259
- 4h：Return +12.92%，MaxDD -20.71%，Calmar 0.3375，turnover 3.2691
- 1d：Return +6.09%，MaxDD -20.02%，Calmar 0.2187，turnover 1.7298

## 候选汇总

| 候选 | 1h ΔCalmar | 4h ΔCalmar | 1d ΔCalmar | Calmar改善单元 | 中位ΔReturn | 新增SELL | 卖后5根 | 卖后10根 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S1 成熟蓝色21+：上轨仅影线 | -0.0284 | +0.0082 | +0.0167 | 37/60 | +0.99% | 643 | -0.04% | -0.05% |
| S2 成熟蓝色21+：任何上轨事件 | -0.0342 | +0.0082 | +0.0167 | 38/60 | +0.82% | 696 | -0.04% | -0.01% |
| S3 蓝转灰首根 | -0.0589 | -0.0614 | -0.2400 | 17/60 | -3.39% | 546 | +0.06% | +0.06% |
| S4 蓝转灰前10根+上轨 | -0.1462 | -0.0112 | -0.1480 | 22/60 | 0.00% | 138 | -0.05% | +0.29% |
| S5 S1+S3 | -0.1275 | -0.0206 | -0.1533 | 22/60 | -2.02% | 1152 | +0.02% | +0.02% |
| S6 S1+S4 | -0.1904 | +0.0200 | -0.0696 | 35/60 | +0.65% | 777 | -0.05% | -0.03% |
| S7 S3+S4 | -0.0629 | -0.0482 | -0.3470 | 19/60 | -3.76% | 679 | +0.04% | +0.11% |

## R1 结论

### 晋级 R2

1. S1_MATURE_BLUE_UPPER_WICK  
   成熟 BLUE（run_age >= 21）出现 upper 且 upper_subtype = WICK_ONLY 时，普通 SELL 25%。

2. S2_MATURE_BLUE_UPPER_ANY  
   成熟 BLUE（run_age >= 21）出现任意 upper 事件时，普通 SELL 25%。

两者都满足 R1 预设门槛：
- 4h 与 1d 的 median Calmar 均改善；
- 60 个单元中 Calmar 改善分别为 37/60、38/60；
- 聚合 median Return 没有牺牲，反而分别 +0.99%、+0.82%；
- 新增卖出后 5/10 根的中位 forward return 接近 0 或略负，没有出现明显系统性“卖飞”。

### 淘汰 / 不晋级

S3/S4/S5/S6/S7 不进入 R2。
核心原因是蓝转灰类卖出在多个周期明显损伤收益与 Calmar，尤其 1d；组合后还显著提高换手。

## 周期差异

S1/S2 不是“所有周期都直接变好”。

S1：
- 1h median Calmar：0.2965 -> 0.2681，下降；
- 4h：0.3375 -> 0.3457，改善；
- 1d：0.2187 -> 0.2354，改善。

S2：
- 1h：0.2965 -> 0.2623，下降；
- 4h：0.3375 -> 0.3457，改善；
- 1d：0.2187 -> 0.2354，改善。

这说明“策略语义跨周期一致”是成立的，但同一 SELL 条件在不同时间尺度上的统计价值仍需独立验证。不能因为引擎周期无关，就假设参数效应也完全相同。

## ABT 对照

ABT 与用户截图的现象一致：成熟蓝色阶段缺少 SELL 覆盖。

ABT：
- 1h BASE: Return +21.65%, MaxDD -13.69%, Calmar 0.9186
- 1h S1/S2: Return +22.72%, MaxDD -11.50%, Calmar 1.1460

- 4h BASE: Return -1.42%, MaxDD -14.60%, Calmar -0.0591
- 4h S1: Return -1.75%, MaxDD -12.68%, Calmar -0.0836
- 4h S2: Return -0.22%, MaxDD -12.68%, Calmar -0.0105

- 1d BASE: Return -9.51%, MaxDD -15.61%, Calmar -0.3758
- 1d S1/S2: Return -8.61%, MaxDD -14.96%, Calmar -0.3543

ABT 单标上 S2 对 4h 的表现比 S1 更符合截图中“成熟蓝色上轨区域应当有减仓”的直觉，但最终不能用 ABT 单标决定规则。

## 下一步

R2 必须用独立股票池验证 S1 与 S2，并重点解决 1h 退化问题：
- 判断 1h 是否需要更严格的成熟阈值（例如 30+ / 40+）；
- 判断 WICK_ONLY 是否优于 ANY；
- 继续保持统一 K 线结束确认 / 下一根同周期开盘执行；
- R2 结束前不修改正式 V7。
