# SLTD V7 Universal Sell Study（通用卖出研究）Protocol v1

状态：FROZEN_BEFORE_RUN

## 目的

验证当前 SLTD V7 的 SELL（卖出）覆盖是否存在跨 K 线周期的结构性缺口，并寻找不依赖固定 1D 的通用减仓条件。

本轮不修改正式 V7 12 条规则，不修改仓位管理，不修改 C2。所有候选 SELL 只在独立研究分支中叠加测试。

## 固定执行语义

- 所选周期 K 线结束确认信号；
- 下一根同周期 K 线开盘执行；
- 首次 BUY：25%；
- 后续实际 BUY：每次 +25 个百分点，最高 100%；
- 普通 SELL：卖出当前剩余仓位的 25%；
- SELL 实际执行后 C2 = ARMED；
- 后续实际 BUY 重置 C2；
- C2 条件保持不变：GREEN + High < GZB4；
- NO_CHANGE_MIXED（冲突动作不调整仓位）。

## 时间周期

同一套候选条件直接用于：
- 1h
- 4h
- 1d

不为任何单独周期更换规则含义或参数。

## 股票样本

20 只主流美股，分 4 批，每批 5 只：

B1: ABT, AAPL, MSFT, NVDA, AMD  
B2: AMZN, META, GOOGL, JPM, BAC  
B3: XOM, CVX, LLY, UNH, WMT  
B4: COST, CAT, BA, MA, V

用途：Discovery / Screen（发现与筛选），不是最终 OOS 证明。

## 数据窗口

- 使用当前 SiftAlpha 行情层；
- 1h / 4h：最近约 365 天；
- 1d：先获取完整日线，再截取最近约 365 天用于本轮跨周期一致比较；
- 前段数据仅用于指标与状态 warmup；
- 正式比较窗口：每个 series（股票×周期）最后约 180 个自然日。

## Baseline

当前正式候选 V7 12 条规则：
- 4 BUY
- 4 HOLD
- 2 WAIT
- 2 SELL

当前 SELL：
1. GREEN 4–10 + upper
2. GREEN 11–20 + light_resist

## 候选 SELL

### S1_MATURE_BLUE_UPPER_WICK
BLUE 且 run_age >= 21，首次触达上轨，且为 WICK_ONLY（仅影线上穿）。

含义：成熟蓝色趋势在上轨出现明确拒绝时减仓。

### S2_MATURE_BLUE_UPPER_ANY
BLUE 且 run_age >= 21，出现 upper 事件，不限制 subtype。

含义：更积极测试成熟蓝色的所有上轨事件。

### S3_MATURE_BLUE_WICK_CONFIRM_DOWN
上一根为 BLUE 且 run_age >= 21、upper=WICK_ONLY；当前 K 线收盘低于上一根收盘。

含义：上轨拒绝后，再等一根 K 线确认转弱。

### S4_BLUE_TO_GRAY_UPPER
当前 GRAY，origin=BLUE，run_age <= 5，同时出现 upper。

含义：蓝转灰初期仍在上轨附近时减仓；比旧 V6 的 light_resist 限制更宽。

### S5_BLUE_TO_GRAY_BEARISH
当前 GRAY，origin=BLUE，run_age <= 5，且当前收盘低于上一根收盘。

含义：蓝转灰后的早期价格转弱确认。

### 组合
- C1 = S1 + S4
- C2 = S3 + S4
- C3 = S1 + S5

所有候选 SELL 仍遵守 NO_CHANGE_MIXED；若同一根 K 线同时存在不同动作类别，则不执行。

## 统计

每个候选与 Baseline 比较：

- Total Return
- CAGR
- Max Drawdown
- Calmar
- executed BUY / SELL / C2 数量
- 候选 SELL 触发数量
- 每个周期的 breadth
- 20 股票 × 3 周期总体 breadth
- median / mean ΔReturn
- median / mean ΔMaxDD
- median / mean ΔCalmar

同时记录 candidate SELL 后 5 根 K 线内重新 BUY 的比例，作为“过早卖出/快速打脸”的辅助指标。

## 晋级边界

本轮只允许三类结论：

- ADVANCE_TO_OOS：跨周期多数 series 的 Calmar / MaxDD 改善，且收益损失可接受；
- WATCH：有明显周期依赖或收益/回撤互有得失；
- REJECT_NOT_ADMITTED：整体退化或明显过早卖出。

本轮不得直接写入正式 V7/V8。任何晋级候选必须再跑 fresh-stock OOS。
