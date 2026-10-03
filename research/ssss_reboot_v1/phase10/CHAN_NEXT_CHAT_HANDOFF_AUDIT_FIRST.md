# 新对话续接提醒：独立缠论 Theory-First 审计

状态：**HANDOFF_REQUIRED_AUDIT_FIRST**

写入时间：2026-10-03

仓库：
- `kuashan/siftalpha-research`

当前工作分支：
- `feature/chan-standalone-v2`

写入本提醒前读取到的远端 HEAD：
- `87c61d89ff799ae2dc2a384d1391e242d8917041`

---

## 一、新对话第一件事：先审计，不要继续改代码

新对话开始后必须按顺序执行：

1. `git fetch origin` / 重新读取真实远端：
   `origin/feature/chan-standalone-v2`
2. 读取本文件。
3. 如果真实 HEAD 已经超过本文件记录的 handoff HEAD：
   - 先审计新增 commits；
   - 不得假设这些新增提交已经正确；
   - 不得直接在其上继续修改公式。
4. 读取当前：
   - `integrations/sltd_v7_siftalpha_v1/chan_strategy.py`
   - `integrations/sltd_v7_siftalpha_v1/tests/test_chan_strategy.py`
   - phase10 下所有 Chan audit / diagnostic 文件
   - 对应 GitHub Actions 结果。
5. 先给出审计结论，再决定是否修改。

---

## 二、最高边界：Theory-First，禁止按单股调缠论

用户已经明确锁定：

> 缠论规则必须来自缠论原典、原典后期修订/答疑，以及多个成熟实现和长期归纳的交叉审计。
> 不能因为 ABNB、AAPL、NVDA、ADBE 或任何单只股票没有出现某个买卖点，就修改定义让它出现。
> 股票只能用于验证实现，不能用于定义规则。

规则来源优先级固定：

1. 缠中说禅原典 108 课及后期修订/答疑；
2. 原典内部前后定义的一致性；
3. 多个成熟开源实现的交叉比较：
   - `Vespa314/chan.py`
   - `waditu/czsc`
   - `yijixiuxin/chanlun-pro`
   - `mikonos/chanlun-kline`
4. 大样本结构验证；
5. 单股案例只做实现 QA。

**禁止：**
- “某只股票没有 B1，所以放宽 B1”；
- “B1 数量太少，所以改参数”；
- “B3 太多，所以为了平衡数量人为收紧”；
- 用收益率反向定义一买二买三买；
- 把工程代理定义冒充成原典定义。

---

## 三、独立缠论边界

当前“缠论”必须继续保持**完全独立**：

- 不读取 SLTD BLUE / GRAY / GREEN；
- 不读取 XMA / ZD1 / ZK1 / BS / GZB；
- 不读取 V7 / E / 5s 的买卖逻辑；
- 只允许复用：
  - 行情入口；
  - Web 页面外壳；
  - 通用绘图容器。

目标是开发一套**独立缠论策略/结构引擎**，不是“缠论辅助 V7”。

---

## 四、当前理论链条

当前目标链必须保持：

```
原始K线
→ 包含处理
→ 顶/底分型
→ 笔
→ 特征序列
→ 线段
→ 次级别走势类型
→ 中枢
→ 盘整 / 趋势
→ 盘整背驰 / 趋势背驰
→ B1/B2/B3
→ S1/S2/S3
→ 级别递归 / 多级别
```

严禁跳过结构层，直接用 MACD 背离替代“缠论背驰”。

---

## 五、因果性硬规则

必须继续坚持：

- `anchor_time`：结构在图上的锚点；
- `confirm_time`：第一次真实可确认时间；
- 图可以画在 anchor；
- 信号只能记录在 confirm；
- 若用于交易：确认 K 线收盘后，下一根同周期 K 线开盘执行；
- 必须使用逐 Bar / prefix replay 的 `FIRST_OBSERVED` 思路；
- 不能拿最终历史图的 B/S 倒推“当时已经知道”。

未完成结构必须允许：
- `PROVISIONAL`
- `CONFIRMED`
- `INVALIDATED`

---

## 六、v2.2 不是最终标准版

当前版本只能视为：

`CHAN_V2_2 = CANDIDATE_PENDING_THEORY_AUDIT`

不是最终“标准缠论”。

之前为了修复 B1/B2/S1/S2 做过这些重要调整，新对话必须逐条审计是否符合原典，不能直接默认正确：

### 1. B1 / S1

曾修正：
- 删除自创的 `0.25 × DIF` 硬门槛；
- 不再强制 C 段必须创新高/新低；
- 当前方向是：
  - 必须有严格同级别趋势结构；
  - C 段必须离开最后中枢；
  - 若不创新极值，可直接视为力度更弱；
  - 若创新极值，再比较 B/C 力度。

必须继续核对原典第20、24、27、38等课及后续修订。

### 2. B2 / S2

曾修正：
- 不再强制依赖已出现的标准 B1/S1；
- 因为原典第53课允许“小转大”情况下本级别没有一类点，但二类点仍成立；
- 又加入“创新高/低但形成盘整背驰”仍可形成二类点的候选实现。

这一块必须继续重点审计，不能把“任何结构高低点后的回试”都泛化成二类点。

### 3. B3 / S3

当前方向：
- 离开中枢；
- 第一次次级别回试/回抽；
- 不重新进入中枢。

不要因为数量较多就人为收紧。
但必须审计“离开”和“回抽”是否真的是**完整次级别走势类型**，而不是简单的一笔或代理结构。

---

## 七、当前最重要的理论审计风险

### A. L0 笔级中枢不能冒充原典标准中枢

最近已经有提交专门处理：
- `fix: keep L0 Bi centers diagnostic only`
- `test: forbid formal signals from L0 proxy level`
- `ci: do not require proxy-derived Chan signals`

新对话必须确认：
- L0 笔级 overlap 只能是 diagnostic / proxy；
- 正式 B/S 不得从 L0 proxy 直接产生；
- 原典标准中枢必须基于连续次级别走势类型的重叠。

### B. GG / DD / ZG / ZD 的计算必须继续审计

最近新增：
- `research: freeze Chan Z-movement mapping audit v1`
- `research: add Chan Z-movement structural diagnostic`
- `research: compare current centers with Chan Z-movement invariants`
- `research: audit Chan GG DD against Z-movement subsequence`

必须确认：
- ZG/ZD 来自构成中枢的连续三段次级别走势的重叠；
- GG/DD 的取值范围是否严格符合原典；
- 不能把外围离开段错误纳入中枢 GG/DD。

### C. 线段价格连续性和确认稳定性

最近新增：
- `research: audit standardized line-segment price continuity`
- `research: add confirmed-segment causal stability diagnostic`
- `ci: run confirmed-segment stability diagnostic`

必须审计：
- 标准线段端点是否保持严格连续；
- 已确认线段后续是否还会被不合理重写；
- 如果确认后仍大规模变化，则当前 FIRST_OBSERVED 信号链不可靠。

---

## 八、最近新增提交必须先审计

写本提醒前看到的最近提交链包括：

- `5d62cde4b199d83b415160ae28ed6405632e9085`
  - keep L0 Bi centers diagnostic only
- `dcbdd76c916e118e56d6a6b131a9202bc7894203`
  - forbid formal signals from L0 proxy level
- `ce0291ae41966ce2a0bce754828b9ac0a4372b55`
  - do not require proxy-derived Chan signals
- `63e08cdbdc708d76ed537e5bc4486d5d8efa306b`
  - freeze Chan Z-movement mapping audit v1
- `8dd95124924bbc01292c5dccf186a0b8f6b1a1ad`
  - add Chan Z-movement structural diagnostic
- `ce3ae1b560daf87fe36f2ddde6b866e97e3c5f63`
  - audit Chan Z-movement stream invariants
- `79caf23ea72e17012c4e778328f7371d2e36f0b7`
  - compare current centers with Chan Z-movement invariants
- `08c22052b851601004142f5c38ac15768f83b153`
  - run Chan audit workflow on diagnostic changes
- `470775bd05dcc405313b70cdf80a36dbb32fee16`
  - audit Chan GG DD against Z-movement subsequence
- `6ba9bc9ad65dc4a235434d9ef560b2c58e69a007`
  - audit standardized line-segment price continuity
- `bfd41bda109df0f6aee6aa0fbfee50fd6359eda8`
  - add confirmed-segment causal stability diagnostic
- `87c61d89ff799ae2dc2a384d1391e242d8917041`
  - run confirmed-segment stability diagnostic

**这些提交不能因为名字看起来合理就默认 PASS。**
新对话必须读代码、读输出、给出审计结论。

---

## 九、下一步唯一任务

新对话开始后不要继续扩展新功能。

唯一任务：

> **完成 Chan Theory Canonical Audit（缠论原典标准化审计），并对最近 v2.2 / 后续并行修改做“是否过度修改”审计。**

审计必须输出：

1. 哪些实现与原典一致；
2. 哪些是后期修订支持；
3. 哪些属于合理工程选择；
4. 哪些属于过度扩展 / 应回退；
5. 哪些仍无法确定；
6. 当前代码能否继续称为 v2.2 candidate；
7. 是否需要修改；
8. 如果没有发现过度修改，明确：
   `NO_OVER_MODIFICATION_FOUND`
   然后不要为了“再优化”继续改。

---

## 十、收尾纪律

每个审计项必须有状态：

- `PASS_CANONICAL`
- `PASS_ENGINEERING_CHOICE`
- `NEEDS_REVISION`
- `REJECTED_OVER_MODIFICATION`
- `UNRESOLVED`

本轮最终必须收口为：

- `CHAN_CANONICAL_AUDIT = COMPLETE`
或
- `CHAN_CANONICAL_AUDIT = BLOCKED`

禁止无限追加小项。

---

## 新对话建议直接执行的第一句话

> 先不要继续修改。请读取 `research/ssss_reboot_v1/phase10/CHAN_NEXT_CHAT_HANDOFF_AUDIT_FIRST.md`，重新读取 `feature/chan-standalone-v2` 真实远端 HEAD，并审计 handoff HEAD 之后所有新增提交。然后严格按提醒日志完成 Chan Theory Canonical Audit，重点确认 v2.2 以及最近并行修改有没有偏离缠论原典或出现过度修改。没有问题就明确写 `NO_OVER_MODIFICATION_FOUND`，不要为了单股信号继续调公式。
