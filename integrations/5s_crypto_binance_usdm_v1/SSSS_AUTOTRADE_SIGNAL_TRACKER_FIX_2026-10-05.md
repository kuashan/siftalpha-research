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


## Binance 执行桥接二次审计

用户真机现象“图表已有 💰，页面仍显示观望，并出现检测异常”不能只解释为信号计算失败。代码审计确认还存在一条执行异常后的 UI 状态保留问题：

- scheduler 已可能生成 `SSSS_BUY_9`；
- 进入 `M3Executor.execute()` 后，如果 Binance SDK / 网络 / 前置账户检查抛异常；
- 旧代码只把 `run_state` 改成 `ERROR`，没有把本次 `decision.signal` 写回 runtime；
- 因此页面仍可能显示上一次的 `HOLD / 观望`，造成“交易程序完全没有识别 💰”的假象。

本轮已修复：

1. **执行异常时保留本次 SSSS decision**
   - `run_state=ERROR` 时，`last_signal` 仍写入本次 `SSSS_BUY_9 / SSSS_EXIT_15`。
   - 但故意保留“决策前”的 `strategy_state`，不把失败事件加入已消费集合。
   - 配合同一 closed bar 重扫，同一个 signal 可以在临时 Binance/SDK 错误恢复后继续重试。

2. **利用 clientOrderId 保证重试幂等**
   - 同一 SSSS signal 使用同一 `clientOrderId`。
   - 重试前先查询本地订单和 Binance 订单。
   - 若第一次请求实际已被 Binance 接收但本地因网络异常未拿到结果，后续轮询优先恢复已有订单，而不是盲目重复下单。

3. **下单链增加逐阶段审计**
   新增：
   - `M3_EXECUTION_DISPATCH`
   - `BINANCE_EXECUTION_STAGE`
   - `BINANCE_ORDER_SUBMIT`

   可以区分：
   - decision 是否已经交给执行器；
   - 是否通过仓位检查；
   - 是否完成 ONE_WAY / ISOLATED 检查；
   - 是否完成杠杆设置；
   - 是否完成下单数量计算；
   - 是否真正调用 Binance `new_order`；
   - Binance 是否返回 `FILLED` 或错误。

4. **杠杆档位查询不再成为单点阻断**
   - 原代码在真正 `new_order` 前强制调用 `max_allowed_leverage()`。
   - Demo leverage bracket 接口若返回缺失/格式异常，会导致订单根本没有送到 Binance。
   - 现在保留原有 leverage-cap 安全检查：**如果 bracket 能正常读取，则仍按上限阻止超额杠杆**。
   - 如果 Demo bracket 本身不可用，则记录 `LEVERAGE_BRACKET_UNAVAILABLE`，继续调用 Binance `set_leverage`，由 Binance 本身作为最终杠杆合法性权威。

## 开源实现对照

本轮同时对照了成熟开源 Binance Futures 实现：

- Hummingbot 的 Binance Perpetual 下单路径直接构造 `symbol / side / quantity / type / newClientOrderId` 后调用订单 API；ONE_WAY 平仓使用 `reduceOnly`。
- Freqtrade 同样把信号/仓位决策与交易所 `create_order` 执行层分开，交易所拒绝由执行层显式抛出和记录。
- Binance 官方 USDⓈ-M SDK 示例支持 ONE_WAY 下使用 `position_side="BOTH"`，并支持 `newOrderRespType=RESULT`；MARKET 订单在 RESULT 模式下应直接返回最终成交结果。

因此当前方向不是改写 SSSS 公式，而是保证：
`SSSS decision -> execution dispatcher -> Binance order submit -> FILLED persistence`
这条链每一段都可观察、可恢复、不可静默丢信号。

## 新增关键回归

新增并锁定：

- SSSS BUY 不依赖 leverage bracket 查询成功也能走到 Binance submit。
- leverage bracket 正常返回时，原有超杠杆阻止规则仍保留。
- 第一次 Binance submit 模拟网络异常时：
  - runtime 显示本次 `SSSS_BUY_9`，而不是旧 HOLD；
  - signal 不被消费；
  - 同一 closed bar 下一轮可以重试；
  - 第二次成功后只产生一次 FILLED 仓位变化。
- Audit 必须出现 `BINANCE_ORDER_SUBMIT stage=REQUEST` 和最终 `stage=RESPONSE status=FILLED`。

最终状态仍是：

**IMPLEMENTED_AND_CI_VERIFIED / DEVICE_VERIFY_PENDING**

只有真机 BNB/SOL 再次出现新 💰，并在 Binance Demo 中实际看到 FILLED、页面仓位 +25%、图表出现 B，才能把本问题标记 CLOSED。
