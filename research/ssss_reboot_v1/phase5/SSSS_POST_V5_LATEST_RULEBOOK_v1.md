# SSSS Post-V5 — 最新操作逻辑规则表 v1

Status: **LATEST ORGANIZED STATE**
Date: 2026-10-02
Source HEAD before organization: b0343e38a12d7455db613503250c21f95c2011b3
V5 window: 2020-01-02..2026-09-30
Representation: FIRST_OBSERVED
XMA: unchanged

---

## 0. 最新总结构

V5 之后，旧的 16 条逻辑重新分层为：

- **正式保留：8 条**
- **V5 晋级：3 条**
- **继续观察：2 条**
- **Mixed：3 条**

因此当前正式操作候选集合为：

> **8 条正式保留 + 3 条 V5 晋级 = 11 条 Active（主动候选）**

此外，V5 全组合扫描又产生了 **5 条新的 discovery（发现）**，
它们全部必须使用未来完全独立的数据再次验证，不能直接加入正式操作集合。

---

# 1. 正式保留的 8 条

## 1. BUY_BLUE_21P_LOWER

逻辑：
- 蓝色
- 持续 21+ 根
- 新的内下轨跌破
- 预期：MID before BD

V5：
- 股票 n=515，69.9%
- 19/20 有资格股票支持
- Crypto n=124，82.3%
- 4/4 支持

状态：
**KEEP_STRONG_CROSS_ASSET**

操作解释：
蓝色长期阶段出现内下轨跌破，仍然是当前最稳健的 BUY 候选之一。

---

## 2. BUY_GRAY_4_10_LIGHT_SUPPORT

逻辑：
- 灰色 4–10 根
- 从上方新接触真正浅灰带
- 预期：SUPPORT_HOLD

V5：
- 股票 n=167，75.4%，19/19 支持
- Crypto n=53，81.1%，4/4 支持

状态：
**KEEP_STRONG_CROSS_ASSET**

---

## 3. BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT

逻辑：
- 最近蓝 -> 灰
- 当前灰色 age <= 5
- 从上方碰浅灰带
- 预期：SUPPORT_HOLD

V5：
- 股票 n=57，75.4%，6/7 支持
- Crypto n=28，85.7%，3/3 支持

状态：
**KEEP_STRONG_CROSS_ASSET**

---

## 4. CONT_BLUE_11_20_UPPER

逻辑：
- 蓝色 11–20 根
- 新的内上轨突破
- 预期：BS before MID

V5：
- 股票 n=86，83.7%，16/17 支持
- Crypto n=20，70.0%，3/3 支持

状态：
**KEEP_STRONG_CROSS_ASSET**

操作解释：
蓝色中段突破内上轨时，内上轨通常不是最终卖点，应优先观察 BS。

---

## 5. SELL_RECENT_BLUE_GRAY_LIGHT_RESIST

逻辑：
- 最近蓝 -> 灰
- 当前灰色 age <= 5
- 从下方碰浅灰带
- 预期：RESIST_HOLD

V5：
- 股票 n=100，76.0%，16/17 支持
- Crypto n=20，85.0%，3/3 支持

状态：
**KEEP_STRONG_CROSS_ASSET**

---

## 6. AVOID_GREEN_11_20_LOWER

逻辑：
- 绿色 11–20 根
- 新的内下轨跌破
- 预期：BD before MID

V5：
- 股票 n=85，78.8%，15/16 支持
- Crypto n=11，81.8%，但 breadth 不足

状态：
**KEEP_STRONG_STOCK**

操作解释：
股票中这是明确的“不要在第一下轨急着接”的情景，优先等待 BD。

---

## 7. CONT_BLUE_4_10_UPPER

逻辑：
- 蓝色 4–10 根
- 新的内上轨突破
- 预期：BS before MID

V5：
- 股票 n=66，81.8%，11/13 支持
- Crypto n=14，85.7%，但 breadth 不足

状态：
**KEEP_STRONG_STOCK**

---

## 8. CONT_RECENT_GRAY_BLUE_UPPER

逻辑：
- 最近灰 -> 蓝
- 当前蓝色 age <= 5
- 新的内上轨突破
- 预期：BS before MID

V5：
- 股票 n=61，70.5%，7/10 支持
- Crypto n=6，100%，但样本不足

状态：
**KEEP_STRONG_STOCK**

---

# 2. V5 正式晋级的 3 条

## 9. BLUE_11_20_LOWER_WICK_ONLY

逻辑：
- 蓝色 11–20 根
- 内下轨仅影线跌破
- 收盘没有跌破 ZD1
- 预期：MID before BD

V5：
- 股票 n=53
- 84.9%
- 12/12 有资格股票支持
- Crypto 样本不足

状态：
**PROMOTE_V5**

操作解释：
这是目前最清楚的“影线假跌破后反弹” BUY 候选之一。

---

## 10. GREEN_11_20_LOWER_CLOSE_BELOW

逻辑：
- 绿色 11–20 根
- 内下轨被收盘真正跌破
- 预期：BD before MID

V5：
- 股票 n=39
- 92.3%
- 8/8 支持
- Crypto 样本不足

状态：
**PROMOTE_V5**

操作解释：
这是 AVOID_GREEN_11_20_LOWER 的强化版。
如果绿色 11–20 不只是影线，而是收盘跌破内下轨，更应该避免第一时间买入。

---

## 11. GREEN_4_10_UPPER

逻辑：
- 绿色 4–10 根
- 新的内上轨突破
- 预期：MID before BS

V5：
- 股票 n=52
- 63.5%
- 8/10 支持
- Crypto 样本不足

状态：
**PROMOTE_V5**

操作解释：
可作为股票中的 SELL / 减仓候选，但强度明显低于前两条新晋级逻辑。

---

# 3. 继续观察的 2 条

## 12. BLUE_11_20_UPPER_CLOSE_ABOVE

逻辑：
- 蓝色 11–20
- 收盘突破内上轨
- 预期：BS before MID

V5：
- 股票 n=41
- 85.4%
- 5/6 支持
- Crypto 7/7，但 breadth 不足

状态：
**WATCH**

判断：
方向仍然很强，但有资格股票只有 6 个，未达到预注册 breadth 门槛。
不应删除，继续观察。

注意：
更宽的 `CONT_BLUE_11_20_UPPER` 已经是正式强规则。
所以这一条的价值主要是判断“收盘突破”是否能进一步提升精度，而不是证明蓝色 11–20 上轨本身。

---

## 13. BLUE_21P_UPPER_FULL_ABOVE

逻辑：
- 蓝色 21+
- 整根 K 线完全站上内上轨
- 预期：BS before MID

V5：
- 股票 n=18
- 18/18 命中
- 但只有 2 个有资格股票
- Crypto 无有效样本

状态：
**WATCH**

判断：
概率很漂亮，但样本过稀，不能晋级。

---

# 4. 三条 Mixed 的最新处理

## 14. BUY_GREEN_21P_LOWER

V5：
- 股票 n=303
- MID before BD 仅 41.9%
- 只有 2/19 股票方向支持
- Crypto 54.7%，Mixed

最新状态：
**WEAKEN / REMAIN_MIXED**

处理：
- 从“潜在通用 BUY”进一步弱化。
- 不应进入主动操作集合。
- 后续除非出现新的明确过滤条件，否则无需优先投入验证资源。

这是三条 Mixed 里最应该弱化的一条。

---

## 15. AVOID_RECENT_GRAY_GREEN_LOWER

V5：
- 股票 n=48
- BD before MID 60.4%
- 5/7 支持
- 股票达到 REPEAT
- Crypto n=11，81.8%，但不足

最新状态：
**REMAIN_MIXED / HIGH-WATCH**

处理：
- 不弱化。
- V5 比 V3 更支持这个方向。
- 但根据预注册规则，旧 Mixed 必须达到 STRONG_REPEAT 才允许晋级，因此暂时继续观察。

---

## 16. SELL_GREEN_21P_UPPER

V5：
- 股票 n=392
- MID before BS 61.0%
- 13/20 支持
- Crypto n=97
- 60.8%，3/4 支持

最新状态：
**REMAIN_MIXED / HIGH-WATCH**

处理：
- 不弱化。
- 股票和 Crypto 都出现约 60% 的重复方向。
- 但没有达到旧 Mixed 晋级所要求的 STRONG_REPEAT。
- 下一轮仍值得保留观察，但不能叫正式 SELL。

---

# 5. V5 新发现的 5 条：是否值得独立验证

结论：

> **五条全部达到 V5 预注册的“新发现”门槛，因此都值得进入下一轮独立验证。**

但优先级不同。

## Priority 1 — NEW_V5_B

**BLUE 21+ + UPPER + CLOSE_ABOVE**

预期：
- BS before MID

V5：
- n=228
- 82.9%
- 20 个有资格股票
- 95% 股票方向支持

评价：
**最高优先级。**

原因：
样本最大、覆盖最广、跨股票一致性最好。
而且它比稀有的 FULL_ABOVE 更实用。

---

## Priority 1 — NEW_V5_E

**GREEN 11–20 + LIGHT_RESIST**

预期：
- 浅灰带压力成立

V5：
- n=88
- 78.4%
- 16 个有资格股票
- 93.75% 支持

评价：
**最高优先级。**

原因：
样本和 breadth 都很充足，有机会补上目前 SELL 侧的结构缺口。

---

## Priority 1 — NEW_V5_A

**GREEN -> GRAY，灰色 1–3 根 + LIGHT_SUPPORT**

预期：
- 浅灰带支撑成立

V5：
- n=48
- 87.5%
- 9 个有资格股票
- 100% 支持

评价：
**高优先级。**

原因：
概率和一致性极强，但样本少于 B / E，因此排在它们之后。

---

## Priority 2 — NEW_V5_D

**GREEN 11–20 + UPPER + WICK_ONLY**

预期：
- MID before BS

V5：
- n=49
- 77.6%
- 8 个有资格股票
- 87.5% 支持

评价：
**值得独立验证。**

意义：
可能把绿色上轨 SELL 逻辑进一步细分成：
影线碰上轨与真正收盘突破是不同结构。

---

## Priority 2 — NEW_V5_C

**GRAY 4–10 + LOWER + WICK_ONLY**

预期：
- MID before BD

V5：
- n=45
- 82.2%
- 9 个有资格股票
- 77.8% 支持

评价：
**值得独立验证，但优先级略低。**

原因：
命中率高，但横向一致性比另外四条弱一些。

---

# 6. Post-V5 最新规则层级

## Tier A — 正式 Active

共 **11 条**：

- 8 条 V3/V5 正式保留
- 3 条 V5 晋级

这是下一版策略开发时可以直接作为“正式候选逻辑集合”的部分。

## Tier B — Watch

共 **2 条**：

- BLUE 11–20 + UPPER + CLOSE_ABOVE
- BLUE 21+ + UPPER + FULL_ABOVE

不进入正式操作集合，但保留统计。

## Tier C — Mixed

共 **3 条**：

- BUY_GREEN_21P_LOWER → **弱化**
- AVOID_RECENT_GRAY_GREEN_LOWER → **高优先观察**
- SELL_GREEN_21P_UPPER → **高优先观察**

## Tier D — New V5 Discovery

共 **5 条**，全部进入下一轮独立验证候选池：

优先顺序：

1. BLUE 21+ + UPPER + CLOSE_ABOVE
2. GREEN 11–20 + LIGHT_RESIST
3. GREEN -> GRAY 1–3 + LIGHT_SUPPORT
4. GREEN 11–20 + UPPER + WICK_ONLY
5. GRAY 4–10 + LOWER + WICK_ONLY

---

# 7. 下一轮研究边界

下一轮不再重测所有历史组合。

只做：

1. 11 条 Active 作为 reference，不重新调参；
2. 2 条 Watch 继续收样本；
3. 2 条高观察 Mixed 做旁路统计；
4. 弱化的 BUY_GREEN_21P_LOWER 不再占主要研究资源；
5. 对 5 条 NEW_V5_DISCOVERY 使用完全独立的新股票 / 新时间数据验证。

不允许：
- 用 V5 原数据再次优化这 5 条新发现；
- 改年龄区间；
- 改 XMA；
- 为了提高命中率临时追加条件。

`SSSS_POST_V5_LATEST_RULEBOOK_v1 = FROZEN_ORGANIZATION`
