# FIVEGZ5SE Pruned Mechanism Families v1

Status: **CLASSIFICATION_COMPLETE**

Date: 2026-09-29

Starting HEAD:
`2d816182c94a5046ff6fc03fe28021113fb0cc80`

## Scope

Input:
- 34 retained BUY rules
- 27 retained SELL rules
- AMZN 2023-2025 development evidence only

This step performs **mechanism classification, not additional pruning**.

Original formula operation prompts are not used.

W1/W3/W5 path information remains part of the classification logic.

## Buy mechanism families

### B-F1 — 弱势中的趋势先拐
- 成员：10
- V2：BUY_A
- 代表规则：B001
- 代表条件：`trend.net5<0 AND trend.slope3>0 AND trend.neg5>=3 AND accel.neg3>=2`
- 家族候选平均 10 日结果：5.21%
- 家族平均匹配增量：3.38 pp
- 平均样本数：17.2
- 机制：W5/当前仍弱，但趋势 W1/W3 已开始改善；典型早期反转。

### B-F2 — 资金先修复
- 成员：6
- V2：无
- 代表规则：B005
- 代表条件：`capital.slope3>0 AND capital.slope5<0 AND momentum.neg5>=3 AND accel.net1>0`
- 家族候选平均 10 日结果：5.07%
- 家族平均匹配增量：5.00 pp
- 平均样本数：17.2
- 机制：资金 W3 已改善，但 W5 或动能背景仍弱；资金领先价格/动能修复。

### B-F3 — 资金走弱、加速先修复的背离反转
- 成员：10
- V2：BUY_B
- 代表规则：B004
- 代表条件：`capital=GRAY AND capital.net1<0 AND accel.slope3>0 AND anomaly=GRAY`
- 家族候选平均 10 日结果：4.88%
- 家族平均匹配增量：4.09 pp
- 平均样本数：17.1
- 机制：资金仍恶化，但加速 W3/W5 提前回升，形成跨维度背离。

### B-F5 — 中性区恢复
- 成员：4
- V2：无
- 代表规则：B007
- 代表条件：`trend=GRAY AND capital.net3>0 AND capital.pos3>=2 AND capital.slope5>0 AND anomaly=GRAY`
- 家族候选平均 10 日结果：4.82%
- 家族平均匹配增量：5.43 pp
- 平均样本数：17.3
- 机制：趋势/资金/异动处于中性区，资金、动能或加速出现持续恢复。

### B-F6 — 多维复合恢复
- 成员：4
- V2：无
- 代表规则：B077
- 代表条件：`capital.slope3>0 AND momentum.net1>0 AND accel.neg5>=3`
- 家族候选平均 10 日结果：4.50%
- 家族平均匹配增量：3.30 pp
- 平均样本数：16.8
- 机制：多个维度共同改善，未被单一领先维度完全解释。

## Sell mechanism families

### S-F1 — 趋势先弱、动能仍强
- 成员：4
- V2：无
- 代表规则：S003
- 代表条件：`trend.net5<0 AND momentum>=L AND accel.pos3>=2 AND accel.slope5<0 AND accel.pos5>=3`
- 家族候选平均 10 日结果：-2.42%
- 家族平均匹配增量：-3.58 pp
- 平均样本数：19.8
- 机制：趋势已转弱，但动能/加速仍保持强势；属于表面强、趋势先坏。

### S-F2 — 加速衰减/高位失速
- 成员：3
- V2：无
- 代表规则：S019
- 代表条件：`trend.net5<0 AND accel.pos3>=2 AND accel.slope5<0 AND accel.pos5>=3 AND anomaly=GRAY`
- 家族候选平均 10 日结果：-2.11%
- 家族平均匹配增量：-2.68 pp
- 平均样本数：20.3
- 机制：加速仍处高位或过去持续偏多，但 W3/W5 斜率开始下行。

### S-F3 — 资金先恶化的内部背离
- 成员：12
- V2：SELL_B
- 代表规则：S031
- 代表条件：`capital.slope5<0 AND momentum>=L AND anomaly.net1<0`
- 家族候选平均 10 日结果：-2.03%
- 家族平均匹配增量：-2.66 pp
- 平均样本数：17.5
- 机制：资金 W3/W5 转弱，而动能、加速或多维表面仍强。

### S-F4 — 异动过热/强势末端
- 成员：4
- V2：SELL_C
- 代表规则：S026
- 代表条件：`accel.net3>0 AND accel.pos3>=2 AND anomaly.net3>0 AND bullbars3>=2`
- 家族候选平均 10 日结果：-2.08%
- 家族平均匹配增量：-3.43 pp
- 平均样本数：20.8
- 机制：异动持续上升且市场仍偏多，历史上更像末端过热而非新起点。

### S-F5 — 广泛强势后的失败延续
- 成员：1
- V2：SELL_A
- 代表规则：S006
- 代表条件：`trend=GRAY AND accel.pos5>=3 AND bullbars3>=2`
- 家族候选平均 10 日结果：-2.07%
- 家族平均匹配增量：-5.76 pp
- 平均样本数：15.0
- 机制：前期多维持续偏多，但趋势回落/走弱，形成强势后的失败延续。

### S-F8 — 多维复合衰减
- 成员：3
- V2：无
- 代表规则：S037
- 代表条件：`trend.net3<0 AND capital>=L AND momentum.slope5>0`
- 家族候选平均 10 日结果：-1.93%
- 家族平均匹配增量：-3.96 pp
- 平均样本数：22.0
- 机制：多个维度共同恶化，未被单一领先机制完全解释。

## V2 placement

Current V2 is preserved and mapped into the mechanism taxonomy:

- BUY-A -> B-F1 / 弱势中的趋势先拐
- BUY-B -> B-F3 / 资金走弱、加速先修复的背离反转
- SELL-A -> S-F5 / 广泛强势后的失败延续
- SELL-B -> S-F3 / 资金先恶化的内部背离
- SELL-C -> S-F4 / 异动过热/强势末端

## Interpretation rule

A family name is explanatory, not a new trading signal.

The family itself is not promoted just because its average return looks strong.
Promotion still requires rule-level statistical evidence and later untouched
validation.

## Next step

The next valid step is **family-level comparison**:
1. measure event overlap between family representatives;
2. identify which families add genuinely new opportunities beyond V2;
3. test each family separately on the same AMZN development framework;
4. only then decide which families deserve a new V3 candidate path.

Closure:

`FIVEGZ5SE_PRUNED_MECHANISM_CLASSIFICATION_V1 = COMPLETE`
