# M3.2 — 四币独立调度

状态：**IMPLEMENTED_AWAITING_CI**

范围：
- 单 Python 进程调度 BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT
- 只调度用户已经启动的币种
- 每个币种独立读取自己的 K 线周期
- 只处理已经确认收盘的 K 线
- 第一次观察只建立 baseline，不追单、不补做已经错过的上一根开盘交易
- 同一根已收盘 K 线只处理一次
- 使用 M3.1 已通过 parity 的冻结 Python 信号引擎
- W3 BUY-C eligibility 按初始 BUY 信号 bar 距离严格计算
- 同 bar C + SELL 保持冻结研究里的先补仓、后清仓动作顺序
- 账户未连接时进入 WAITING_DEMO，不导致主程序崩溃
- 调度异常按币种隔离，不影响其他币种

本小项仍然不下单。
真正的 Binance Demo 下单、幂等 clientOrderId、保证金检查属于 M3.3。
