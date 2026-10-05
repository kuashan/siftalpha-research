# SSSS 自动交易信号追踪修复（2026-10-05）

状态：**IMPLEMENTED_PENDING_DEVICE_VERIFY**

## 续接基线

- 分支：`feature/5s-crypto-multistrategy-ssss-v1`
- 用户给出的续接 HEAD：`42261d12bb2973ca38c13678ba54f23d46187091`
- 远端核对结果：该提交与分支当时真实 HEAD 完全一致，ahead=0 / behind=0。
- 原始 `SSSS.ftindex` 不修改；SHA256 继续锁定为：
  `25f8c56075c0021dd2d0567401d37def25d6a9b895f139b3a8a9abc376fecaa7`

## 审计结论

HEAD 前已经存在第一版“新图标事件追踪器”：

- `19a6887...`：追踪新出现的 SSSS 图标事件。
- `b1de579...`：持久化 tracker state。
- `883272f...`：执行新出现的 SSSS 信号。
- 后续提交增加了事件键加固与状态/Audit 诊断。

因此本轮没有重新实现一套平行逻辑，而是在现有实现上继续审计。

## 已确认的结构漏洞

虽然第一版 tracker 会比较完整 1000 根已收盘 K 线中的图标集合，但 scheduler 仍有旧门禁：

`latest_open_time <= previous_open_time -> 直接跳过`

这会造成：

1. 某根 K 线刚收盘后，scheduler 第一次取数并计算。
2. 随后 Binance/行情源对同一根已收盘 K 线的 OHLC 返回最终修订值，`open_time` 不变。
3. 网页重新请求并重算完整 SSSS，因此可以第一次显示新的 💰 / 💥。
4. scheduler 因 `open_time` 没有推进而跳过，永远没有再次比较事件集合。

这个漏洞不依赖“XMA 一定漂移”的假设；它是调度条件自身导致的同一收盘 K 线数据修订漏检。

## 本轮修改

### 1. SSSS 同一已收盘 K 线允许重新检测

- 5s Crypto V1 仍保持原来的“新 bar 才计算”语义。
- SSSS 即使 `latest_open_time == previous_open_time` 也允许重新进入 `analyze_ssss()`。
- 相同 1000 根输入会命中现有缓存；输入 OHLC 发生变化时 fingerprint 改变，才重新执行指标。
- 没有新事件时不会每秒写 HOLD/Audit，避免数据库无意义增长。
- 真正的新事件仍由持久化 `seen_icon_events` 判定，同一事件不会重复下单。

### 2. 新增持久化 SSSS 信号事件账本

新增 SQLite 表 `ssss_signal_events`，唯一键为：

- symbol
- timeframe
- signal_bar_open_time
- icon_id（9 / 15）

保存：

- `first_detected_time`
- `last_detected_time`
- `detection_bar_open_time`
- `status`
- `execution_bar_open_time`
- `execution_time`
- `binance_order_id`
- `result`

历史基线图标记录为 `BASELINE`，不补历史订单。

新事件根据执行结果记录为：

- `FILLED`
- `BLOCKED`
- `ERROR`
- `IGNORED_NO_ACTION`
- `SUPPRESSED_BY_EXIT`

### 3. /api/status 增强调试

`/api/status` 新增：

`ssss_signal_events`

每个币种返回最近 20 条结构化 SSSS 信号事件；不包含 API Secret。

原有 `diagnostics` 继续返回：

- `SCHEDULER_ERROR`
- `M3_EXECUTION_BLOCKED`
- `SSSS_BAR_DECISION`
- `SSSS_BAR_EXECUTION`
- `SSSS_SIGNAL_BASELINE`

因此真机再次出现“检测异常”时，可以直接区分：

- 指标/行情/调度异常；
- 已发现信号但执行失败；
- Binance BLOCKED；
- 已 FILLED。

## 回归测试要求

必须覆盖：

1. baseline 历史 💰 / 💥 不补单。
2. 新 bar 上出现 💰 → +25%。
3. 新 bar 上出现 💥 → 全清。
4. 旧 K 线上第一次新出现 💰 → 仍执行。
5. 同一 signal 消失再出现 → 不重复执行。
6. **同一个 latest closed bar 的 open_time 不变，但 OHLC 被修订后首次产生 💰 → 必须执行。**
7. FILLED 后才产生 B/X。
8. 事件账本保存 first_detected / signal bar / execution bar / Binance order id / result。

## CLOSED 边界

本轮代码和 CI 即使全部 PASS，也只能标记：

**IMPLEMENTED_AND_CI_VERIFIED / DEVICE_VERIFY_PENDING**

在 BNB/SOL 真机实际再次出现新 💰，并确认 Binance Demo 自动成交且图表出现 B 之前，不得宣称自动交易问题 CLOSED。
