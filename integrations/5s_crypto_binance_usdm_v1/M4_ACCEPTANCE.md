# M4 — 恢复、对账与联合真机验收

状态：**CLOSED / PASS**

验收日期：**2026-10-02**

## 最终结论

M3 + M4 已完成 SiftAlpha + Binance Demo 联合真机验收。

用户确认：

`M3_M4_REAL_DEVICE_ACCEPTANCE = PASS`

因此：

`M3 = CLOSED`

`M4 = CLOSED`

`5S_CRYPTO_V1_BINANCE_DEMO_INTEGRATION_ROUND = CLOSED`

## 已实现并纳入验收范围

- API 凭据仍只保存在当前 Python 进程内；重启后需要重新连接 Demo。
- 重新连接成功后自动执行 M4 Recovery（恢复对账）；未通过前自动交易门禁关闭。
- 每个币种独立对账，单币种异常不会阻止其他已通过对账的币种。
- 本地 SQLite 已成交订单账本与 Binance Demo 当前持仓数量进行一致性校验。
- 程序在订单提交后、状态落库前异常退出时，可通过固定 clientOrderId 查询 Binance 并恢复订单状态。
- 本策略遗留未成交订单可自动清理；非本策略订单不会被擅自取消，而是阻止对应币种自动交易。
- 发现空头、未知外部仓位、订单账本/远端持仓不一致时进入 RECOVERY_BLOCKED。
- 恢复成功后以最近一根已收盘 K 线重新建立 baseline，不追补停机期间已错过的历史开盘成交。
- PnL、资金费、手续费可从 Binance Demo 刷新。
- Web 提供“重新对账”“取消本策略挂单”“紧急平仓”三个独立控制。
- 紧急平仓只作用于选定币种，同时停止该币种策略，不影响其他币种。
- LIVE 入口仍然锁定。

## 联合测试 UI 可视化

- 页面品牌标题：`5s crypto v 1`
- 顶部显示 Demo 连接状态与恢复对账状态
- 账户余额 / 可用资金 / 策略资金 / 总盈亏在移动端保持一行四列
- BTC / ETH / BNB / SOL 币种切换保持一行四列
- 每个币种显示 K 线蜡烛图 + 成交量柱状图
- 图表周期读取该币种保存的 timeframe
- 图表固定显示最近 300 根，仅用于可视化
- Scheduler 历史读取窗口仍独立保持 220 根默认值
- 图表 B/S 标记来自 M3_SIGNAL_BAR 真实策略信号审计记录
- 交易设置支持展开 / 收起

## 冻结边界

本次收口只更新验收状态与文档。

未修改：
- 5s-crypto V1 冻结信号公式
- 60% 初始仓位规则
- W3 BUY-C 补至 100% 规则
- SELL-A / SELL-B / SELL-C 全退规则
- 自动执行语义
- Recovery / Reconciliation 代码逻辑
