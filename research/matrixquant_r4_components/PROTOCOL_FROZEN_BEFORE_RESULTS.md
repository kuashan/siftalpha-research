# MatrixQuant R4-A: 原公式组件审计与四币 4h 事件研究（结果前冻结）
Date: 2026-10-09. Status: PROTOCOL_FROZEN_BEFORE_RESULTS.

## 目的与范围
只研究 **MatrixQuant 原始公式各模块的独立信息含量**，不是修改或推广买卖策略。严格禁止修改/部署 5s、SSSS、MatrixQuant 交易引擎。冻结 R2 数据仅用于探索，禁止宣称未触及的 OOS 或 Binance USDM 实盘适用性。

## 事实与原公式
原文件 `research/matrixquant_crypto_mtf_r3/ORIGINAL_MatrixQuant_Multi_Factor_Reversal_Analyzer.pine`，保留默认参数：
- PAI = ((SMA3(Stoch20(C,H,L)) - 50)/50) × Stoch20(population stddev20(C))，原始阈值 ±5。±5 是震荡区间上下边界，非买卖指令；在图上 PAI 被转换为 (raw+100)/2。
- Wave Trend: HLC3、EMA10、偏差 EMA10、CCI 风格复合指数、EMA21 主线、SMA4 信号，WT hist=main-signal；普通背离以 hist 为源，左5右1、5-60 根间距。
- Gold Zone: `PriceVolatility(hlc3,8) = sqrt(hlc3/(8×4×ln2)×sum(log(H/L)^2,8))`，然后计算该序列的 Wilder RSI(8)。Gold Zone低于30 **并非价格 RSI 超卖**；测试低于30与重新站上30（从≤30到>30）的事件。不擅自改原公式为 ATR/标准 Parkinson 波动率。
- Trend Detector: 原代码使用 volume 加权 OHLC/close 趋势；冻结源文件无 volume，无法测定原模块完整数值。不得以价格动量代理替代、不得伪造结果。
- 只用默认不开启 HTF/Laguerre 的公式。不能用 PAI 的顶底背离作为主交易结论：此前 400条 TradingView 4h 记录尚有一处 PAI 看跌背离差异，未解决。

## 数据
`research/matrixquant_crypto_mtf_r2/data/4h_{BTC,ETH,BNB,SOL}_USD.csv`；每币5000行，4h，冻结自 Twelve Data USD 现货等价源，不是 Binance USDM。四币各自独立；无 volume；先校验日期升序、连续、不重复、OHLC合法。
每币指标预热250根，排除最后20根，预计每币可比较4730个候选确认时点。只做4h第一批，不用15m、1h、1d跨频挑选胜者。

## 预定义单事件观察（不建策略、不调阈值）
A: PAI cross above +5 (up-break)
B: PAI cross below -5 (down-break)
C: WT main cross above signal (turn-up)
D: WT main cross below signal (turn-down)
E: WT regular bullish divergence **confirmation bar**
F: WT regular bearish divergence **confirmation bar**
G: Gold Zone RSI crosses **below 30**
H: Gold Zone RSI crosses **above 30** from ≤30
基准是同币同时间窗所有具备20根未来K线的确认时点。A/B原旧策略仅为对照，不预设“买卖”；Gold Zone方向未知。

## 独立检验的指标
确认发生在 bar i 收盘，观察起点 i+1 开盘，未来第5 / 第20根 K 线收盘的 **无费率现货等价价格收益**；也记录 20根内 MFE=(maxHigh/entryOpen−1)、MAE=(minLow/entryOpen−1)、正收益占比及分位/均值。分别报告四币样本量 n、收益、基础概率；总体只作描述，不因为绝对收益较高就推荐上杠杆。
事件可能重叠，horizon20的事件收益 **高度相关，不是独立交易胜率**；无匹配风险、牛熊状态、费用、真实 OOS、组合/成交序列，严格不能推断盈利能力。
输出层次：公式语义审计→数据有效性→组件样本量→方向性/增量信息→下一次应证伪的问题。暂不加入任何多因子组合规则，因子选择须经后续稳定性证伪与执行级回测。

## PASS / PENDING 定义
- 静态公式解释可以 PASS；独立数值 Pine parity 仅 PAI/WT 在 BTC 4h 150根确认，Gold Zone/Trend Detector 为 PENDING；
- 事件结果 COMPUTED 不表示经济有效性、交易可用或盈利；
- 新自动下单策略: REJECTED / 不启动，不改变旧版本仓库和服务器。
