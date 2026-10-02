# SLTD V8 Universal Sell Study R1 Protocol

状态：PROTOCOL_FROZEN_BEFORE_RUN

## 目标

验证 SLTD V7 当前卖出覆盖是否过窄，并寻找可以跨 K 线周期复用的通用卖出条件。

核心原则：
- 不修改 12 条 V7 基线规则；
- 不修改 25% 加仓/减仓、NO_CHANGE_MIXED、C2 Hard Exit；
- 只在研究分支追加候选 SELL 规则；
- 所有周期统一采用“当前 K 线结束确认，下一根同周期 K 线开盘执行”；
- 候选规则必须在 1h / 4h / 1d 上用相同语义测试。

## 基线

V7 Candidate B：
- source commit: 5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042
- 12 active rules
- ordinary SELL = 当前仓位的 25%
- ordinary SELL executed -> C2 ARMED
- later executed BUY -> C2 NORMAL
- C2: ARMED + GREEN + High < GZB4 -> next selected-bar open full exit

## R1 股票池（20）

AAPL, MSFT, NVDA, AMZN, META,
TSLA, WMT, COST, ABT, LLY,
UNH, JPM, BAC, V, CAT,
XOM, NEE, PLD, IBM, DIS

覆盖科技、消费、医疗、金融、工业、能源、公用事业、REIT。

## 时间周期

- 1h
- 4h
- 1d

4h 沿用当前 App 的定义：从 1h 常规交易时段数据按交易日聚合；完整 4 小时块 + 收盘前尾段。

## 数据窗口

共同正式评估区间：
- 2025-02-03 .. 2026-09-30

预热：
- 1h/4h 请求约 700 天小时线，用正式期前数据仅做指标预热；
- 1d 从 2020-01-02 起取日线，用正式期前数据仅做指标预热。

正式期统一从空仓开始，避免不同候选在预热阶段形成不同历史仓位。

## 候选 SELL

BASE：
- 当前 V7 两条 SELL，不新增规则。

S1_MATURE_BLUE_UPPER_WICK：
- BLUE
- run_age >= 21
- upper = true
- upper_subtype = WICK_ONLY
含义：成熟蓝色趋势首次/再次触达上轨但收盘退回轨内，视为高位拒绝，减仓 25%。

S2_MATURE_BLUE_UPPER_ANY：
- BLUE
- run_age >= 21
- upper = true
含义：成熟蓝色趋势任何上轨事件均减仓。用于证伪“上轨即卖”。

S3_BLUE_TO_GRAY_TRANSITION：
- GRAY
- origin = BLUE
- run_age = 1
含义：蓝色趋势刚转灰色，结构首次降级时减仓。

S4_BLUE_TO_GRAY_UPPER：
- GRAY
- origin = BLUE
- run_age <= 10
- upper = true
含义：蓝转灰后的前 10 根中出现上轨压力才减仓。

S5_WICK_PLUS_TRANSITION：
- 同时加入 S1 + S3。

S6_WICK_PLUS_GRAY_UPPER：
- 同时加入 S1 + S4。

S7_TRANSITION_PLUS_GRAY_UPPER：
- 同时加入 S3 + S4。

所有新增 SELL 仍进入原有动作分类；若同一根 K 线同时存在其他动作类别，则继续执行 NO_CHANGE_MIXED，不人为提升 SELL 优先级。

## 评价指标

每个 symbol × timeframe × variant：
- Total Return
- CAGR
- Max Drawdown
- Calmar
- Turnover
- BUY executions
- SELL executions
- C2 hard exits
- Invested-bar ratio

候选 SELL 时机诊断：
- 卖出信号后 3 / 5 / 10 根 K 线的 forward close return
- 中位数越低，代表卖出后价格越倾向继续下跌；
- 同时结合收益/回撤，避免只因为过度交易而得到表面“卖得早”。

## R1 晋级原则

不以单只 ABT 定论。

候选进入 R2 独立验证，至少需要：
1. 相对 BASE，在 3 个周期中至少 2 个周期的 median Calmar 改善；
2. 所有 60 个 symbol×timeframe 单元中，Calmar 改善比例 > 50%；
3. 聚合 median MaxDD 不恶化；
4. 聚合 median Total Return 不出现明显负向牺牲；
5. 卖出后 5/10 bars forward return 不能显示明显系统性“卖飞”。

R1 只负责筛选，不直接修改正式 V7。
