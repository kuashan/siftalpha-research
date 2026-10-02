# SLTD V7 · SiftAlpha Web

这是 SLTD V7 冻结候选策略的 SiftAlpha 可运行工程版本。

## 边界

该项目**不重新研究或自动优化策略参数**。研究事实源仍在：
`candidate/sltd-v7-12rules-position-v1`

冻结候选 commit：
`5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`

当前执行层：
- 12 条 SLTD V7 活跃规则
- 首次 BUY 25%
- 后续 BUY 每次 +25 个百分点，上限 100%
- 普通 SELL 每次减当前仓位 25%
- 普通 SELL 实际执行后 C2 状态 = ARMED
- 后续实际 BUY 会重置 ARMED
- ARMED + GREEN + `High < GZB4` -> 下一根所选周期 K 线开盘全部清仓

## Web UI

Web 设计借鉴已完成的 5s crypto 移动端框架，但信息架构按 SLTD 重做：

1. 当前 BUY / HOLD / WAIT / SELL / C2
2. 当前模拟仓位
3. BLUE / GRAY / GREEN + Age / Origin
4. C2 NORMAL / ARMED
5. 最近 300 根 K 线
6. GZB3/GZB4 慢灰带、ZD1/ZK1
7. BLUE / GRAY / GREEN 状态带
8. B / S / X 执行标记
9. 成交量
10. 仓位轨迹
11. 最近信号记录
12. 当前 12 条规则清单

## Runtime（运行时）

只依赖 Python 标准库。

```bash
python app.py
```

服务器使用回环地址 + 自动空闲端口，并在成功 bind 后输出：

```
SIFTALPHA_WEB_URL=http://127.0.0.1:<port>
```

因此不会和另一个 SiftAlpha 项目争抢固定端口。

## K 线边界与行情

策略已经改为 **Bar Close（K 线收盘）契约**，不再写死“日线结束”：

- 用户选择哪个周期，就只用该周期已经结束的 K 线确认 SLTD 信号；
- 当前正在形成的 K 线可以获取/展示，但不会参与正式策略决策；
- 信号在所选周期 K 线结束时确认；
- 订单语义为：下一根同周期 K 线开盘执行；
- 300 根 K 线只限制 Web 显示，不限制策略计算历史。

当前支持：
- 5m
- 15m
- 30m
- 1h
- 4h
- 1d

其中 **1d 是当前已做历史研究验证的周期**；5m / 15m / 30m / 1h 只完成了工程适配，属于实验周期，不能视为已经通过同等级回测。

当前行情层仍使用 Yahoo Finance chart endpoint，并按周期分离：
- completed bars（已结束 K 线）
- forming bar（当前形成中 K 线）

网络成功后写入 runtime cache；短时重复加载优先使用缓存；网络临时失败时可回退到已有缓存。

## 当前阶段

这是第一版工程化 Web / signal runtime（信号运行时）。

当前不会：
- 接真实券商
- 自动下真实订单
- 在运行期间修改冻结规则
