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
- ARMED + GREEN + `High < GZB4` -> 下一可用开盘全部清仓

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

## 行情

当前第一版使用 Yahoo Finance daily chart endpoint：
- 日线 OHLCV
- 默认从 2010-01-04 获取，给 XMA / EMA 足够 warmup
- 网络成功后写入项目内 runtime cache
- 短时重复加载优先使用缓存
- 网络临时失败时可回退到已有缓存

Web 显示最多 300 根 K 线；策略计算不受 300 根限制。

## 当前阶段

这是第一版工程化 Web / signal runtime（信号运行时）。

当前不会：
- 接真实券商
- 自动下真实订单
- 在运行期间修改冻结规则
