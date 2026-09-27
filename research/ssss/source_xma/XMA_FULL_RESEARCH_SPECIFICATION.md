# Source-XMA Full Research Specification
## XMA 几何结构 + 三色带状态 + HYS2 + 正交辅助因子完整研究说明

Status: MASTER RESEARCH SPECIFICATION  
Version: v1.0  
Date: 2026-09-28  
Branch: `research/source-xma-walkforward`

---

## 1. 研究目标

本研究不是继续堆叠技术指标，而是首先把 Source-XMA 本身拆解为一套可验证的价格结构语言，再判断哪些辅助变量能够提高这些 XMA 事件的可靠性、仓位质量与退出质量。

核心问题分为四层：

1. **XMA 本体是否已经包含可重复的买点、确认点、持有点、减仓点、退出点？**
2. **三色带颜色与颜色迁移是否能改变同一几何事件的含义？**
3. **HYS2 是否能对某些纯 XMA 事件提供额外确认，而不是制造新的噪声？**
4. **成交量结构、Volume Profile、Market Breadth、VIX、情绪等正交变量，能否只在它们真正有信息优势的场景下提高策略质量？**

最终目标不是得到“指标越多越好”的组合，而是建立：

```text
XMA STRUCTURE
→ XMA STATE
→ XMA EVENT
→ EVENT CONFIRMATION
→ POSITION LIFECYCLE
```

---

## 2. 不可违反的研究原则

### 2.1 XMA 是研究基线

SSSS + ADKBY-E 视为一个统一 Source-XMA 系统。

研究主线使用原始 XMA，不以 DEMA / EMA 替换原始 Source-XMA。

### 2.2 必须 Point-in-time（点时）计算

对日期 / K 线 `t`：

1. 只允许使用 `t` 以及之前已经存在的数据；
2. 重新计算当时右端的 XMA；
3. 保存该时点的 first-observed XMA；
4. 推进到下一根 K 线；
5. 未来 K 线对过去 XMA 的重绘，不得回写过去交易判断。

禁止：

```text
先用完整历史计算一次 XMA
→ 再回头读取过去日期的重绘值
→ 当成当时真实可见值
```

### 2.3 当前 K 线满足交易条件，信号属于当前 K 线

不机械等待下一根 K 线才认定信号。

如果只有日线 OHLCV：
- 使用 current-bar close proxy 作为同 K 线执行代理；
- 必须明确其不是精确的盘中首次成交时刻。

如果有分钟数据：
- 使用 First Tradable Price After Confirmation；
- 即完整条件第一次成立之后的第一个可交易价格。

### 2.4 减仓、退出、空仓、做空是四件不同的事

任何高位、卖出样式、顶部样式、HYS2 火焰山顶、FIVEGZ 绿色状态都不能自动等价于开空。

做空必须由独立证据产生。

### 2.5 不相信显示文字，只相信实际公式与真实结果

包括但不限于：
- 清仓
- 抄底
- 主升
- 逃顶
- 重仓
- 轻仓

文字只作为作者注释。

研究依据是：
- 实际布尔条件；
- 实际轨道位置；
- 实际颜色状态；
- 实际状态迁移；
- 实际点时数据结果。

---

## 3. Source-XMA 核心结构

### 3.1 快 XMA 白色轨道

Source-XMA 的快结构核心：

- `ZK1 = GZB10`：快通道上边界
- `ZD1 = GZB11`：快通道下边界

这两条线是研究中必须逐日保存的 fast white rails。

### 3.2 慢结构

慢结构由加权高低价经过 EMA90 形成：

- `GZB3`
- `GZB4`

再形成外部结构边界：

- `GZB8`
- `GZB9`

三色带状态本质上由 fast channel 相对 slow structure 的空间关系决定。

### 3.3 外侧 60 周期轨道

Source-XMA 还包含 60 周期双 XMA 派生的更外侧轨道：

- `BS`
- `BD`

这些轨道与用户在富途图上看到的外侧粗轨道颜色必须做 **visual-to-formula mapping**。

重要：
源码 COLOR 名称和用户实际富途界面的视觉颜色不一定可靠对应，因此研究数据库保存：
- 公式变量名
- 实际数值
- 实际界面颜色标签
而不是只保存“红线 / 绿线”。

### 3.4 中间白色轨道

用户实际富途图中还观察到一条较细的白色中间轨道。

当前研究不得在未核对精确 Source-XMA 版本前擅自把它等同于某一个变量。

候选包括：
- fast midpoint；
- slow-band 中轴；
- 其他未显式输出变量。

该映射属于 Phase 0 必须解决的问题。

---

## 4. 三色带不是装饰，而是核心 State（状态）

Source 状态公式：

```text
GZB12:
GZB11 >= GZB9
AND
GZB10 >= GZB8

GZB13:
GZB10 <= GZB8
AND
GZB11 <= GZB9

GZB14:
GZB11 >= GZB9
AND
GZB10 <= GZB8
```

研究解释：

- `UP_STATE / GZB12`：
  fast channel 整体相对 slow structure 上移；
- `DOWN_STATE / GZB13`：
  fast channel 整体相对 slow structure 下移；
- `RANGE_STATE / GZB14`：
  fast channel 被包含在 slow structure 内部；
- `EXPANSION_STRADDLE`：
  fast lower < slow lower 且 fast upper > slow upper，
  即 fast channel 同时从上下两侧扩张出去。

EXPANSION_STRADDLE 是三色公式没有完整覆盖的第四种几何状态，必须单独记录。

---

## 5. 颜色迁移比单日颜色更重要

每根 K 线必须记录：

- 当前状态；
- 前一状态；
- 当前状态持续天数；
- 状态转换速度；
- 是否发生跳变；
- 状态变化发生在轨道事件之前还是之后。

重点研究路径：

```text
DOWN -> RANGE
RANGE -> UP
DOWN -> RANGE -> UP

UP -> RANGE
RANGE -> DOWN
UP -> RANGE -> DOWN

DOWN -> UP
UP -> DOWN
```

研究重点不是简单地说：

```text
某颜色 = 买
某颜色 = 卖
```

而是研究：

```text
同一个价格/轨道事件
在不同状态和状态迁移下
是否具有不同的后续分布
```

---

## 6. XMA Geometry（几何）主研究对象

### 6.1 Lower Confluence Zone
下方轨道共振区

用户观察假设：

当 K 线进入外侧下轨与下白色 fast rail 靠近 / 相交的区域时，后续上涨概率可能提高。

研究不得直接把它定义为买点。

必须按状态分组：

- UP_STATE + Lower Confluence
- RANGE_STATE + Lower Confluence
- DOWN_STATE + Lower Confluence
- EXPANSION_STRADDLE + Lower Confluence

分别统计。

还要区分 K 线行为：

- 只用 low 触碰；
- 影线刺穿；
- 实体进入；
- close 跌破；
- close 重新收复；
- 整根 K 线位于轨道外；
- 次根 K 线是否重新站回。

候选研究标签：
`XMA-LCZ-R`
Lower Confluence Zone Reversal。

### 6.2 Upper Confluence Zone
上方轨道共振区

用户观察假设：

当 K 线达到 / 超过外侧上轨与上白轨共振区域后，容易形成阶段顶部。

必须与 trend rail-ride 分开：

- UP_STATE + 上轨贴轨：
  可能是趋势延续；
- UP_STATE -> RANGE + 上方共振：
  可能是衰竭；
- RANGE + 上方共振：
  可能是区间顶部；
- DOWN + 上方共振：
  可能是反弹衰竭。

候选标签：
`XMA-UCZ-E`
Upper Confluence Zone Exhaustion。

### 6.3 Fast Midline Reclaim / Loss

研究：
- 下方极端后收复中白线；
- 上方延伸后跌回中白线；
- 收复 / 失守时三色带状态；
- 是否是 Probe -> Confirm 的关键分界。

### 6.4 Outer Rail Ride

识别：
- 多根 K 线持续贴近外上轨；
- fast rail 同向上升；
- band 未明显转弱；
- 价格未重新跌回内部。

目的：
避免将强趋势中的上轨贴行误判成顶部。

### 6.5 Compression -> Expansion

研究：
- fast channel 宽度收缩；
- slow structure 宽度收缩；
- 上下轨距离趋近；
- 三色带进入 RANGE；
- 后续出现向上 / 向下扩张。

目标：
识别趋势启动前的压缩结构。

### 6.6 Rail Rejection / Reclaim

任何轨道触碰都拆为：

- TOUCH
- PIERCE
- CLOSE_THROUGH
- RECLAIM
- REJECT
- FULL_BAR_OUTSIDE

不能把“碰到轨道”当成单一事件。

---

## 7. XMA 事件数据库字段

每一根 K 线至少保存：

### Price
- open
- high
- low
- close
- volume

### Fast XMA
- ZK1
- ZD1
- fast midpoint
- fast width
- fast slope

### Slow structure
- GZB3
- GZB4
- GZB8
- GZB9
- slow width
- slow slope

### Outer rails
- BS
- BD
- 与 fast rails 的距离

### Band state
- GZB12 / GZB13 / GZB14 / EXPANSION_STRADDLE
- rendered color
- previous state
- days in state
- transition type

### Candle geometry
- low-to-lower-fast distance
- high-to-upper-fast distance
- low-to-outer-lower distance
- high-to-outer-upper distance
- close relative to all rails
- wick/body penetration depth

### Rail geometry
- fast lower ↔ outer lower gap
- fast upper ↔ outer upper gap
- gap change
- convergence rate
- divergence rate

---

## 8. HYS2 的研究定位

HYS2 不是新的交易核心。

定位：
`AUXILIARY CONFIRMATION CANDIDATE`

### 8.1 HYS2 主要拆分对象

#### A. 15-bar oscillator family

核心：
- O00
- L1
- L2
- L3

研究：
- L1 / L2 bull cross
- L1 / L2 bear cross
- oscillator depth
- cross 发生在 XMA 哪个几何事件中

#### B. ★共振

已拆解的实际含义：

```text
L1 上穿 L2
+ MACD histogram 上升
+ L2 < 45
```

它不是“火焰山共振”。

研究用途：
判断某些 XMA Lower Confluence / Midline Reclaim 是否具有额外反转确认。

#### C. 火焰山底

研究：
- 是否在 XMA lower confluence 前出现；
- 是否与 down->range / range->up 配合；
- 是否提高反转后的 MFE；
- 是否减少失败 Probe。

#### D. 火焰山顶

不得直接等同于顶部 / 做空。

原因：
历史研究中它在强突破阶段也会持续出现。

研究用途：
- extension warning；
- profit-protection context；
- exhaustion candidate。

### 8.2 HYS2 市场档位

`SCQH = 0/1/2` 的 A 股 / 美股 / Crypto 分支只作为作者预设。

不得假设作者参数就是正确市场参数。

后续必须分开比较：
- 原始市场档位；
- 标准化版本；
- 跨市场共用参数。

---

## 9. FIVEGZ5SE 的研究定位

FIVEGZ5SE 不再作为主交易系统。

定位：
`DIAGNOSTIC STATE ENGINE`

保留研究字段：
- Trend state
- Capital state
- Momentum state
- Acceleration state
- Anomaly state
- total state score
- state delta
- improving dimensions
- deteriorating dimensions

显示文字：
- 清仓
- 抄底
- 主升
- 逃顶
不进入交易定义。

它最主要用于回答：
**当 XMA 几何事件成功 / 失败时，内部五维颜色状态通常怎样变化？**

只有长期证明存在增量价值后，才允许重新影响仓位。

---

## 10. 正交辅助变量

辅助变量的原则：

```text
不能创造 XMA 原始事件
只能描述 / 验证 / 风险化该事件
```

### 10.1 Volume Structure

研究内容：
- RVOL
- 上涨放量
- 回撤缩量
- Signed Volume
- accumulation
- distribution
- breakout participation

优先用途：
`BREAKOUT QUALITY`

不再采用：
`成交量好 => 自动多加 20% 仓位`

重点研究：
- 是否提高 XMA breakout 成功率；
- 是否能识别 failed breakout；
- 是否能减少低质量 probe。

### 10.2 Volume Profile

研究对象：
- POC
- VAH
- VAL
- HVN
- LVN
- price acceptance / rejection

优先用途：
`LOCATION MAP`

重点：
- XMA breakout 上方是否存在高成交量阻力；
- XMA lower confluence 是否靠近价值区下沿；
- 上轨延伸是否发生在 LVN 快速区；
- XMA exit 是否发生在重新跌回 Value Area 之后。

日线版本只叫：
`Daily Volume Profile Proxy`

精确 Volume Profile 必须使用分钟 / 更细粒度 volume-at-price。

### 10.3 Market Breadth

研究：
- advancing %
- % above MA20 / MA50 / MA200
- new high / new low
- sector breadth

作用：
`MARKET PARTICIPATION CONTEXT`

不能直接生成交易。

重点判断：
- 个股突破是否孤立；
- 是否属于 broad risk-on；
- 是否属于 narrow mega-cap rally。

### 10.4 VIX

研究：
- VIX level
- VIX change
- VIX acceleration
- VIX relative to moving baseline

作用：
`RISK REGIME CONTEXT`

不得简单定义：
`VIX > x => 不买`

重点研究：
- XMA lower reversal 在 panic-expanding vs panic-falling 环境差异；
- breakout 在 stress regime 中的失败率；
- rail-ride 在 VIX 上升期是否更脆弱。

### 10.5 Sentiment

暂列二级研究。

必须满足：
- 可靠时间戳；
- 发布时间早于交易决定；
- 不使用收盘后新闻解释盘中信号；
- 防止 Look-ahead。

---

## 11. 股票与 Crypto 分轨

### Stocks

优先：
```text
XMA Geometry
+ Three-Color State
+ Volume Structure
+ Volume Profile
+ Breadth
+ VIX
```

HYS2 / FIVEGZ 为辅助观察。

### Crypto

优先：
```text
XMA Geometry
+ Three-Color State
+ Volume Profile
+ Crypto Breadth
```

后续候选：
- Funding Rate
- Open Interest
- Liquidations
- Stablecoin flow
- BTC dominance

股票和 Crypto 可以共享 XMA 结构语言，
但辅助变量不要求共享同一参数。

---

## 12. 交易生命周期研究

策略不是一次性 BUY / SELL。

候选生命周期：

```text
NO_POSITION
→ WATCH
→ PROBE
→ CONFIRMED
→ TREND_HOLD
→ EXTENDED
→ DETERIORATING
→ REDUCE
→ EXIT
→ REARM
```

研究重点：
- 哪个 XMA Geometry 事件允许从 WATCH -> PROBE；
- 哪个颜色迁移允许 PROBE -> CONFIRMED；
- 何时属于 rail-ride，应该 HOLD；
- 何时 upper confluence + color decay 应 REDUCE；
- 哪种 midline loss / state transition 应 EXIT。

仓位大小由“证据成熟度”决定，
不是由“指标数量”线性相加决定。

---

## 13. 统计评价体系

每一个 XMA 几何事件都必须做 Event Study。

至少记录：

### Forward return
- +1 bar
- +3 bars
- +5 bars
- +10 bars
- +20 bars

### MFE / MAE
- Maximum Favorable Excursion
- Maximum Adverse Excursion

### Event quality
- hit rate
- median forward return
- trimmed mean
- payoff ratio
- failure rate
- time-to-confirm
- time-to-failure

### Conditional groups
按以下条件分别统计：
- band state
- band transition
- asset class
- volatility regime
- volume context
- Volume Profile location
- breadth context
- VIX context
- HYS2 confirmation

不能只报告总体平均收益。

---

## 14. 消融实验

研究必须按层增加信息：

```text
A. XMA Geometry only
B. A + Three-Color transition
C. B + HYS2
D. B + Volume Structure
E. B + Volume Profile
F. B + Breadth
G. B + VIX
H. 仅将经过单项验证的辅助做有限组合
```

禁止直接：
`XMA + HYS2 + FIVEGZ + Volume + Profile + Breadth + VIX`
然后根据最终收益挑最好参数。

每个新增因素分类为：
- HELPFUL
- NEUTRAL
- HARMFUL
- INCONCLUSIVE

---

## 15. 研究阶段

### Phase 0 — Visual / Formula Mapping

完成：
- 精确映射用户富途截图中的每一条轨道；
- 三色显示颜色 ↔ GZB12/13/14；
- 中间细白线的公式来源；
- 外绿/红粗轨 ↔ BS/BD 实际映射。

完成标准：
每条可见线都有唯一公式变量和数值记录。

### Phase 1 — Pure XMA Geometry Discovery

只用：
- XMA rails
- K line
- three-color state

不使用外部变量决定交易。

目标：
建立 Geometry Event Dictionary。

### Phase 2 — Geometry Event Study

对每种事件统计：
- forward returns
- MFE / MAE
- success / failure
- state conditioned result

完成标准：
知道哪些形态具有重复性，哪些只是视觉错觉。

### Phase 3 — XMA Lifecycle State Machine

把有效几何事件组合成：
- watch
- probe
- confirm
- hold
- reduce
- exit

### Phase 4 — HYS2 Confirmation Study

HYS2 只验证已存在的 XMA event：
- 是否提高成功率；
- 是否降低失败率；
- 是否改变最佳仓位。

### Phase 5 — Orthogonal Confirmation Study

逐项测试：
- Volume
- Volume Profile
- Breadth
- VIX
- Sentiment

### Phase 6 — Forward Validation

Discovery 规则冻结后，
进入未用于调参的新时间窗口。

发现问题只能：
- 记录；
- 建立 v2；
- 从下一窗口生效。

不能回改旧窗口。

### Phase 7 — Portfolio

只有单标的逻辑稳定以后才进入：
- one shared capital pool
- sector exposure
- correlation
- cross-symbol competition
- portfolio drawdown。

---

## 16. 多标的研究池

Stocks discovery pool：
- ABT
- ARM
- ORCL
- AAPL
- AMZN
- INTC
- MSFT
- NVDA
- GOOGL
- META
- JPM
- XOM

Extended candidates：
- AMD
- AVGO
- TSLA
- WMT
- COST
- UNH

Crypto：
- BTC
- ETH
- BNB
- SOL

不能因为某规则只在一只强趋势股票上赚钱就提升为核心规则。

---

## 17. 资金约定

Discovery 单标的研究：
- nominal starting capital = $10,000 / symbol
- fractional shares / units
- commission assumption must be explicit
- slippage assumption must be explicit

这只是为了比较不同标的上的机制。

正式 Portfolio 阶段：
- 只使用一个共享资金池；
- 不允许把多个独立 $10,000 sleeve 的收益相加后称作单一账户收益。

---

## 18. GitHub 研究记录要求

每轮必须至少留下：

```text
PROTOCOL_FROZEN_BEFORE_RUN.md
SOURCE_MANIFEST.md
DATA_PROVENANCE.md
EVENT_DEFINITIONS.md
OBSERVATIONS.csv
DECISIONS.csv
PAPER_TRADES.csv
FEATURE_SNAPSHOTS.csv
EVENT_STUDY.csv
FACTOR_ABLATION.csv
REVISIONS.csv
RESEARCH_LOG.md
FINAL_REPORT.md
visual_report.html
```

每次规则改变记录：
- previous version
- new version
- reason
- effective date
- whether change is discovery or validation
- old results remain unchanged

---

## 19. 防止无限循环开发的收尾规则

每一个大阶段必须可以 CLOSED。

一个阶段满足以下条件即可结束：

1. 研究对象定义冻结；
2. 数据来源和 SHA / version 记录完成；
3. 测试窗口固定；
4. 结果完整输出；
5. 失败案例记录；
6. 不再在同一窗口继续调参数；
7. 候选结论归类为：
   - KEEP
   - DROP
   - OBSERVE
   - REVISE_NEXT_WINDOW
8. GitHub Research Log 写入 CLOSED / NEXT。

不能因为结果不够漂亮而无限重新优化同一个窗口。

---

## 20. 当前研究假设

以下全部只是待验证假设：

### H1
Lower rail confluence 在 RANGE -> UP 或 DOWN -> RANGE 状态转换中，比静态 DOWN_STATE 下更可能产生有效反转。

### H2
Upper rail confluence 本身不是顶部；
Upper Confluence + UP -> RANGE transition 比单纯超上轨更可能是有效衰竭信号。

### H3
持续 UP_STATE + outer rail ride 是趋势延续，而不是卖出。

### H4
Volume Structure 最适合确认 breakout quality，而不是线性增加仓位。

### H5
Volume Profile 最适合解释位置与持有 / 减仓，而不是直接产生买卖信号。

### H6
HYS2 resonance 在 XMA lower confluence / midline reclaim 后，可能提高反转确认质量。

### H7
HYS2 fire-top 在强趋势中可能只是 extension，不应作为自动做空信号。

### H8
Breadth 与 VIX 更适合作为 regime context，而不是直接下单条件。

### H9
FIVEGZ 的 raw color transitions 可能具有诊断价值，但显示文字没有研究优先权。

---

## 21. 当前优先顺序

研究优先级正式定为：

```text
1. XMA 可视轨道精确映射
2. 三色带 State / Transition
3. K线 × 多轨道 Geometry
4. 纯 XMA Event Study
5. XMA Lifecycle
6. HYS2 selective confirmation
7. Volume Structure
8. Volume Profile
9. Breadth / VIX
10. FIVEGZ diagnostic comparison
11. Crypto-specific derivatives data
12. Portfolio integration
```

---

## 22. 最终研究哲学

本项目不追求：

```text
更多指标
= 更高胜率
= 更高仓位
```

追求的是：

```text
XMA 告诉我们：
价格结构发生了什么。

三色带告诉我们：
这个结构正处于什么状态、如何迁移。

HYS2 / Volume / Volume Profile / Breadth / VIX 告诉我们：
这个 XMA 事件的外部或内部质量如何。

仓位管理告诉我们：
当前证据成熟到什么程度。
```

最终策略必须尽量简单、可解释、点时可执行、跨标的可重复，并且能够明确解释每一次：
- 为什么买；
- 为什么加；
- 为什么继续持有；
- 为什么减；
- 为什么退出；
- 为什么不做空。
