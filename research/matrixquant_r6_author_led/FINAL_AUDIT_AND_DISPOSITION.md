# MatrixQuant R6 — 原作者理论驱动的两套参数股票回测：最终结论
2026-10-09
STATUS: PROTOCOL_FROZEN_BEFORE_RESULTS / COMPUTED / DISCOVERY_WINNER_FAILED_REPLICATION / ALL_RULES_REJECTED_FOR_TRADING / CLOSED

## 1. 源和设计
- 实际读到官方 TradingView 开源说明：https://www.tradingview.com/script/m82RL973/ 。原作者的建议信息包括 Trend Detector 负责趋势背景、Gold Zone 负责波动压缩提醒、PAI 和 WaveTrend 负责入场时机，避免把 Gold Zone 低于30当成必涨信号。作者文字是研究假说，不是经过审计的交易绩效。
- 原始 Pine 文件保留在 `research/matrixquant_crypto_mtf_r3/ORIGINAL_MatrixQuant_Multi_Factor_Reversal_Analyzer.pine`。
- 上一轮 R4/R5 已关闭，沿用独立 R6 分支。原始研究协议（早于计算结果冻结）：`PROTOCOL_FROZEN.md`，commit `f14093553a13e66345517996a43d4917d1e55d87`。
- 输入为先前归档的20只美股1D Twelve Data数据（R4原始快照 `research/matrixquant_stock_extreme_20261009/raw_batch_01/02/03.json`），每股2197行，合计43940。取2018–2019作预热、2020–2023探索、2024–2026年8月历史复核。历史后段不是事前未知OOS，切勿夸大。
- 入场当根收盘确认、**下一根开盘**执行；单边摩擦0.15%，单股全仓/现金，允许小数股，无卖空和杠杆，分红未计入，数据是否复权尚未独立认证。
- 实测6种逻辑A–F×2套参数，阈值提前写入协议并冻结（不是事后搜索大量阈值）。

## 2. 参数对比
- MODIFIED (用户版)：PAI Stochastic14/SMA3; STD(C,21) Stoch14；WT EMA10/10/21，Laguerre g=.08开启，MA4信号；Trend OHLC13/Close21；Gold 8/8。
- ORIGINAL (作者默认)：PAI Stochastic20/SMA3; STD(C,20) Stoch20；WT EMA10/10/21，Laguerre关闭，MA4信号；Trend OHLC8/Close20；Gold 8/8。
- 仍计算原始作者公式实际 `TRENDVAL=OHLCtrendLine+OhlcTrendStrength/CloseTrendLine+CloseTrendStrength`，而非私自修正成加权平均；零分母采用无效跳过保护，禁止编造值。
- 绘图改色不影响信号。

## 3. 提前固定六套交易规则
- A_PAI: PAI(raw)向上突破+5入场；PAI<-5离场。
- B_PAI_TREND: PAI上破+5且趋势值>50入场；PAI<-5或趋势<50离场。
- C_ALIGN: 趋势>50、PAI>+5、WT主线>信号线三个条件首次齐备入场；PAI<-5或趋势<50离场。
- D_GOLD: 最近五根内Gold<30、趋势>50并上升、PAI上破+5入场；同B离场。
- E_WT_CROSS: 趋势>50且PAI>+5时，WT主线上穿信号线入场；PAI<-5或趋势<50离场。
- F_SLOW_EXIT: 同C入场，但仅趋势<50并且PAI<-5时离场。
- 无 ATR/止损/其他指标附加规则，无无限迭代开发。

## 4. 最关键检验：2024–2026年8月复核期
表内是每只股票累计收益的**标准偶数样本中位数**；每股本金独立，绝不能冒充实际一篮子投资组合收益。
| 逻辑 | 改良参数收益中位 | 改良版胜过暴露匹配基准 | 原始参数收益中位 | 原版胜过暴露匹配基准 |
|---|---:|---:|---:|---:|
| A_PAI | 23.89% | 4/20 | 34.47% | 7/20 |
| B_PAI_TREND | 4.56% | 6/20 | 0.11% | 3/20 |
| C_ALIGN | 6.91% | 3/20 | 10.91% | 5/20 |
| D_GOLD | -2.71% | 4/20 | 3.15% | 6/20 |
| E_WT_CROSS | 5.70% | 8/20 | 2.67% | 7/20 |
| F_SLOW_EXIT | 27.54% | 5/20 | 38.74% | 7/20 |

所谓暴露匹配被动基准：在同一个起始时刻只把与该策略实际持仓时间占比相同的资金买入该股票，其余留现金，持有到窗口末端。这只是粗略控制现金占比，**没有**真正做到每天和策略相同风险暴露；对比结果有限制。
本次12套模型在较晚时期全部少于半数股票跑赢这个更保守的比较对象（最好仅8/20），更谈不上稳定跨股票/时间段获利。

## 5. 唯一训练期筛选出的候选 E（MODIFIED）
在2020–2023探索期按预先固定的排序（先每股是否胜过风险暴露相近的被动基准，再收益差中位、回撤等）唯一选择E：
- 2020–2023：策略收益中位 15.82% vs matched 12.39%；匹配基准超额收益中位 +1.91个百分点；12/20股票优于基准，已平仓245次，交易胜率44.49%。
- 2024–2026：策略收益中位 +5.7% vs matched +12.33%；匹配基准超额收益中位 -11.33个百分点；仅8/20优于基准，已平仓176次，已平仓交易胜率35.8%；持仓比例中位 17.51%；最大回撤中位 -17.61%（匹配被动基准回撤按已实现暴露估计见JSON）。
- 全期间：策略收益中位 +24.78% vs matched +36.62%；0/20股票跑赢100%持仓长持，8/20优于matched；交易胜率41.04%。
- 训练期胜过12/20只并不意味着经过12种候选挑选后的可靠概率；较晚时期负超额表现直接否定其晋级。

## 6. 为什么不继续增加因子？
- 单纯PAI方向穿越(+5/-5)交易频繁，作者原始参数在较晚窗口下中位+34.47%，改良版+23.89%，都低于各自暴露匹配的被动持有。
- 最复杂三因子同向（C_ALIGN）并未提升已完成交易胜率和风险调整后的表现。
- Gold Zone 加入方向过滤器（D_GOLD）也没有提供稳定独立优势。
- 往同一个已见过的数据集加入更多规则会形成调参过拟合，且无新高质量OOS数据证伪；本轮停止，不强行宣布最佳实盘策略。

## 7. 复现材料与已知限制
- `run_r6.js`：独立、无远端行情调用的Node.js复现。
- `RESULTS_REPRODUCIBLE.json`：原始逐股明细/12组×3期间完整数据；20股代码与数据无意外OHLC、重复、成交量为零或>45%相邻跳变。
- 2026-10-09做了同一轮技术修订：最初脚本将20股偶数排序中的第11只当作“中位数”，已修正为第10、11只算术平均，并重新运行同步结果，候选排名和失败结论没有改变。
- 每个回测片段终点有未平仓部位时以最后收盘估值并估计退出手续费，但不计入已完成交易胜率；不允许将右侧“90%”标签解释为历史胜率。
- 数字为**研究复算**，不代表与通达信或原始TradingView逐根严格Pine parity认证；包含模拟滑点，未实盘/仿真成交验收；不代表各币种或A股。
- 此前已观察同一历史数据，2024–2026并非真正holdout；此阶段不做交易晋级。

## 8. 正式结论
DISCOVERY_SELECTION=MODIFIED/E_WT_CROSS； HISTORICAL_REPLICATION=FAIL。
ALL_SIX_RULES_X_TWO_PARAMETER_SETS=REJECTED_FOR_TRADING； NO_AUTOTRADE_CHANGES；SOURCE_INDICATORS_UNCHANGED。
R6 status: CLOSED — no robust trading edge discovered.
如需下一次独立研究，先获取与通达信同源的逐根值校验并选全新时间或市场的真正未见样本；冻结决策规则之前禁止再从本批历史挑选新因素、阈值或扩大参数网格。
