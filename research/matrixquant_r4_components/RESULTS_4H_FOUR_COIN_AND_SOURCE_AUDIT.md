# MatrixQuant R4-A 四组件审计 + BTC/ETH/BNB/SOL 4h 独立事件研究

**日期：2026-10-09**  
**状态：COMPONENT_SOURCE_AUDIT_PASS / FOUR_COIN_4H_EVENT_COMPUTED / ECONOMIC_EDGE_UNPROVEN / TRADE_RULES_REJECTED_FOR_PROMOTION**  
**生产变更：NONE**。未修改 V7 / 5s / SSSS / MatrixQuant 自动交易源码、执行仓位、API 密钥、数据库或服务器。

## 0. 可复现证据与治理
- [结果前冻结的 R4-A protocol](PROTOCOL_FROZEN_BEFORE_RESULTS.md)，Commit `85e0d15c5bda8a4393b56ae3dade4425f6f8018d`。这次不做事后调参。
- [独立 Node.js 研究脚本](run_r4_4h_event_study.js)；同一原始 CSV 本地读取重跑：`node research/matrixquant_r4_components/run_r4_4h_event_study.js`（在仓库根目录）。读取上一轮已冻结 `research/matrixquant_crypto_mtf_r2/data/4h_{BTC,ETH,BNB,SOL}_USD.csv`，不联网获取新行情。
- [GitHub Actions Run 37812904430 — PASS](https://github.com/kuashan/siftalpha-research/actions/runs/37812904430)，逐币逐事件的核对日志及 JSON artifact `matrixquant-r4-four-coin-4h-json`（制品有保留期限）。无模拟/真实下单。
- 时间窗：每币5000根连续4小时，从 2024-06-18 20:00:00 UTC 到 2026-09-30 00:00:00 UTC；四币 **20,000根**，0 缺口/重复/无效 OHLC。指标预热250根、最后20根不可计算未来回报：每币4730观测时点，合计18,920。**没有成交量**；Twelve Data USD现货等价行情，非 Binance USDM 合约报价。
- 评估仅为单事件，信号确认在本根收盘；下一根开盘起，计算第5/20根收盘的价格变动以及20根内 MFE/MAE。**未计手续费、滑点、资金费，不计算可交易订单收益。** 不把单事件 positive_rate 当作交易策略的胜率；20根重叠窗口高度相关。

## 1. 原始 529 行 Pine 源码解释（源为 `research/matrixquant_crypto_mtf_r3/ORIGINAL_MatrixQuant_Multi_Factor_Reversal_Analyzer.pine`）

| 组件 | 源码行为与默认设置 | 应如何解释 |
|---|---|---|
| **PAI** | PriceMomentum: `(SMA3(stoch(close,high,low,20))-50)/50`; 波动离散度为 `stdev(close,20)` 的 `stoch20`，两项相乘；默认震荡区 ±5，正负极端区域 ±40 | 描述动量与波动离散度状态；±5 **不是**原作者证明有盈亏优势的成交规则。图上数值归一化为 `(PAI+100)/2` |
| **Wave Trend** | `hlc3 → EMA10 → EMA10(abs deviation) → CI → EMA21`；信号线为主线SMA4；直方图=主线−信号线。常规背离默认直方图、左5右1、前后确认间距5–60 | 评估动量切换与价格/震荡器分歧；历史图背离标记可能使用负 offset 回画，但自动决策只能用 **确认时间** |
| **Gold Zone** | `sqrt(hlc3/(8*4*ln(2)) * sum(log(H/L)^2,8))`，再对该序列计算 Wilder RSI(8)，低于30绘制区域 | 描述**价格区间波动率序列的变化状态**，**不是价格 RSI 低于30=超卖买入**。独立 Pine 值逐根验证尚未进行 |
| **Trend Detector** | OHLC 与close变化结合 volume 加权趋势，输出 `OHLCtrendLine + OhlcTrendStrength / CloseTrendLine + CloseTrendStrength`（源代码运算优先级下的实际表达式） | 在此批 R2 冻结数据中缺少 volume，**不能完整复算**；不得硬塞入规则，也不可把展示区 `90%/99%` 文案解释为命中率 |

指标的四部分**不是已经存在的统一自动交易评分模型**，代码没有完成有证据的组合交易逻辑。

## 2. 第一批 4h 数据：每个事件确认后20根的原始方向

| 事件 | 样本 n (四币汇总) | 第5根平均价变动 | 第20根平均价变动 | 20根上涨占比 |
|---|---:|---:|---:|---:|
| 全部确认时点 baseline | 18,920 | +0.042% | **+0.168%** | 51.51% |
| PAI 上穿 +5 | 593 | -0.117% | **+0.145%** | 48.40% |
| PAI 下穿 -5 | 585 | +0.092% | **+0.521%** | 58.12% |
| WT 主线上穿信号线 | 1,387 | +0.133% | **+0.350%** | 52.42% |
| WT 主线下穿信号线 | 1,387 | +0.143% | **+0.298%** | 52.85% |
| WT 常规看涨背离 **确认** | 258 | -0.060% | **+0.349%** | 49.22% |
| WT 常规看跌背离 **确认** | 292 | +0.009% | **+0.340%** | 52.05% |
| Gold Zone 首次跌入30下 | 759 | +0.201% | **+0.148%** | 52.57% |
| Gold Zone 重新升至30上 | 755 | +0.113% | **+0.338%** | 52.45% |

## 3. 防止四币均值掩盖差异：后20根平均价变动

| 事件 | BTC | ETH | BNB | SOL |
|---|---:|---:|---:|---:|
| 任意时点基准 | +0.198% | +0.137% | +0.231% | +0.106% |
| PAI 上穿 +5 | +0.384% | -0.012% | +0.177% | +0.016% |
| PAI 下穿 -5 | +0.173% | +0.141% | +0.623% | +1.123% |
| WT 金叉 | +0.385% | +0.505% | +0.319% | +0.191% |
| WT 死叉 | +0.309% | +0.353% | +0.326% | +0.206% |
| WT 看涨背离 | -0.195% | +0.995% | +0.579% | +0.101% |
| WT 看跌背离 | +0.370% | +0.961% | +0.023% | +0.128% |
| Gold Zone 跌入30下 | +0.101% | +0.080% | +0.343% | +0.045% |
| Gold Zone 回升30上 | +0.459% | +0.225% | +0.467% | +0.195% |

每个币种 BASE=4730；PAI_UP5 n=149/138/158/148；PAI_DOWN5 n=148/142/145/150；WT_UP n=343/352/339/353；WT_DOWN n=342/353/339/353；WT_BULL_DIV n=67/64/56/71；WT_BEAR_DIV n=76/62/77/77；GOLD_ENTER_LT30 n=176/188/208/187；GOLD_EXIT_GT30 n=175/187/207/186（顺序均 BTC/ETH/BNB/SOL）。

## 4. 解读与证伪（不是交易指令）

1. **PAI +5 升穿并没有显著的方向性一致优势。** 四币 pooled +0.145% 仅略低于全部时点 +0.168%，上涨比例48.4%低于基准51.5%。只看 BTC 的 +0.384% 就推广到四币是样本误读。
2. **PAI 跌破 -5 并不可靠地预言接下来继续下跌。** 20根后四币 pooled 平均 +0.521%，上涨占比58.1%；BNB +0.623%、SOL +1.123%。这可能暗含下跌加速后反弹或市场条件效应，**但不能用这些数据直接倒推“PAI -5 应买入”**。
3. **WT 金叉和死叉后的结果相近。** 金叉 +0.350%、死叉 +0.298%；都没有独立证明具有稳定、可交易的多空分辨力。WT 单独的简单交叉不等于完整趋势策略。
4. **WT 看涨/看跌背离结果方向不稳定**，ETH vs BTC 差异尤其明显；更不能以 WT 看跌背离必清仓、看涨背离必买来处理。
5. **Gold Zone 从30下回升**后的 pooled +0.338% 高于基准 +0.168%，且四币平均均正，但涨幅概率只52.45%且 BTC/ETH/BNB/SOL 基础上涨率不同，**不能宣布它有交易增量**；首先需独立验证 Gold Zone Pine 数值和事件时间，再做无未来数据的条件分组检验。
6. **Trend Detector 暂不能评价**：冻结四币 OHLC 文件完全不含 volume，此外其表达式不是四因素总分；用户的真 TradingView 图表的 Trend Detector 未作为 R3 日志记录，因此其视觉表现更不能等同于已完成精确复刻。
7. 该原始公式中 PAI 的“95%/99%”文字标签来自数值区间直接映射，**不是经过统计验证的上涨/下跌命中概率**。
8. 本报告没有搜索最优阈值，也没有开始多因子组合开发；将 PAI、WT、Gold Zone 的观察结果称为“买卖准确率”是错误的。

## 5. 对现有自动交易代码的处理

**旧 MatrixQuant +5/-5 每次25%、最多100%的自动交易逻辑仍存在于 `feature/5s-crypto-multistrategy-mfra-v1`；本轮没有修改任何代码，也没有实际停用它。** 由于经济价值尚未验证，继续维持 `NOT_APPROVED_FOR_AUTOMATED_TRADING` 的研究治理结论，不建议启动该策略自动下单。5s/SSSS不受影响。

## 6. 下一轮只研究两个具体问题，不要泛化扩展

- R4-B: 优先补 **Gold Zone** 的真实 TradingView 逐根数值 parity（至少同符号同周期，并明确原计算式）及趋势探测器的 volume 数据来源；若拿不到真实同源成交量，Trend Detector 继续 `PENDING`，绝不填假值。
- R4-C（待 R4-B 通过）：利用预先固定的 BTC/ETH/BNB/SOL 各自 4h 分段样本，比较 **PAI 跌破 -5 后反弹**和 **Gold Zone 30上穿** 是否在下跌/震荡/上涨状态中同向出现；加入非重叠事件检验、与持有时间和暴露相同的基准；只有稳定结果再进入完整仓位及手续费策略回测。禁止补更多无证据规则。

R4-A最终：`STATIC_SOURCE_AUDIT=PASS`; `4H_FROZEN_DATA_4X5000_QUALITY=PASS`; `R4_CI_REPLAY=PASS`; `EVENT_STUDY=COMPUTED_EXPLORATORY`; `GOLD_PINE_NUMERIC_PARITY=PENDING`; `TREND_VOLUME_PARITY=BLOCKED_MISSING_VOLUME`; `AUTO_TRADE_PROMOTION=REJECT`.
