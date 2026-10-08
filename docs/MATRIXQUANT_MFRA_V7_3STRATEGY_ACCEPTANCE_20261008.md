# SiftAlpha V7 / 5s Crypto 三策略自动交易接入 — MatrixQuant PAI v1

**状态：IMPLEMENTED · OFFLINE_CI_PASS · ZIP_PUBLISHED · BINANCE_DEMO_LIVE_ACCEPTANCE_PENDING · AUTO_START=NO**

## 范围与基线
- 生产/原始双策略分支：`feature/5s-crypto-multistrategy-ssss-v1`, 起始远端 HEAD `12a0fafd0e3334c3019867eba1bdc03751a5fe83`；该分支**未修改**。
- 新开发/发布分支：`feature/5s-crypto-multistrategy-mfra-v1`。
- 原有 **5s Crypto V1**、**SSSS** 公式、交易执行、原生 SQLite 持仓状态、恢复对账、Binance USDM Demo、ONE_WAY、ISOLATED、per-symbol 策略独立资金、clientOrderId 幂等、成交后 B/X 图表标记、资金和保证金设置保持。
- 新增第三策略 ID `matrixquant_pai`，显示名 **MatrixQuant PAI**。
- 源码中的 © MatrixQuant / MPL-2.0 注释保留。原始 Pine 源文件独立存放在 `integrations/5s_crypto_binance_usdm_v1/strategy/MatrixQuant_original.pine`，未修改原公式。

## MatrixQuant 自动交易规则
- 默认 Pine v6 原始 `Price Action Index`：Stochastic 20 → SMA 3；close 的 population stdev20 再做 stoch20，组合生成原始 PAI。默认禁用 HTF、Laguerre；WT、Gold Zone、背离等**不参与此候选交易条件**。
- **BUY**：上一根已收盘 PAI ≤ +5 且当前已收盘 PAI > +5；如果本策略同币种实际仓位比例不足 100%，就将目标策略资金比例增加 **25 个百分点**，如 0→25→50→75→100。不是每根 PAI 高于 +5 都重复买。
- **SELL**：上一根 PAI ≥ -5 且当前已收盘 PAI < -5；如持仓就全部清仓 100%。
- 信号在当前 K 线**收盘确认**，由现有 scheduler 在下一根 K 线开盘后的轮询执行；下单使用当时 Binance 市价及已有保证金数量算法，并非确保按理论开盘价成交。
- 首次开始/切换策略先建立最新已收盘 K 线 baseline，**不会回放历史信号下单**。
- 单币只能启动一个策略；有策略/交易所持仓、挂单时禁止切换策略；持仓与交易账户对账失败阻止执行。
- 每次 SELL 只调用原有 `reduce-only` 清仓路径；如果 PAI 买入/卖出信号因账户状态阻止，则不得伪造成交；图表 B/X 来自 SQLite 中 Binance 确认 `FILLED` 订单记录。
- 同一个已确认的 K 线由 SQLite `last_closed_bar_open_time` 去重；幂等客户端订单 ID 包含策略前缀 `mfra`、币种、信号 K 线、动作码。因终端失败/传输失败不会自行补出一个假成交。
- 时间周期：3m、5m、15m、1h、2h、4h、6h、12h、1d。每次请求 1000 根已收盘 K 线 + 当前开盘一根；至少 250 根有效已收盘历史。数据缺失、时间不连续不得按伪造的下一根开盘订单执行。
- Binance Demo（非真实资金）自动交易功能已接好，但用户需要**手动连接 Demo、切换策略并点击启动**；本次没有实际触发 Demo API 交易，更没有实盘资金操作。

## UI
- 策略切换列表现为 **5s V1 / SSSS / MatrixQuant PAI**，切换锁保护共用。
- MatrixQuant 显示原始 PAI 曲线专属子面板、PAI 当前已收盘值、资金 25% 阶梯预估、运行状态。
- 蜡烛图 **BUY / SELL** 为 PAI 收盘确认的指标历史信号，不代表下单或成交。图表读取同一批已收盘 Binance OHLC，与自动决策使用的 `evaluate_pai` 函数一致，不读取进行中的 K 线、不使用未来数据。
- 蜡烛图 **B / X** 仍仅代表 Binance Demo 已确认 `FILLED` 的真实订单事件，依然由 SQLite 订单账本独立提供。
- 这两种标记不相互取代。即使 Demo 停止或尚无订单，历史 BUY / SELL 也应显示；若实际成交则在对应执行 K 线上额外显示 B/X。图例已说明各自含义。

## 验证和交付
- `tests/test_multistrategy_mfra.py`：根据用户于 2026-10-08 从 TradingView 免费 Pine Logs 导出的 BTC 4h **400 根 K 线**，预热 250 根、其余 150 根原始 PAI 数值和跨 ±5 信号与 Pine 逐根比对；每个 BUY+25%、上限100%、SELL 全退、优先级、模拟 Binance 买/加/卖、FILLED-B/B/X 存储标记。
- `tests/test_multistrategy_ssss.py`、其余遗留测试以及 M3/M4 regression 同时跑。
- GitHub Actions Run **37791684909**：`SUCCESS`，包括完整测试、原始 SSSS.ftindex SHA256 核验、PAPER import、图表 JS 供应商打包、平铺 ZIP 导入检查。
- 发布文件 `releases/5s-crypto-multistrategy-mfra-v1/5s-crypto-multistrategy-mfra-v1.zip`，大小约 **298,331 bytes**，SHA-256 **`34614dc540e11f2f871a6f8af843c7882426a60ea2f1f37efd565c2df74594a4`**。
- 校验 SHA 文件在同一发布目录。发布无需同步至生产服务器；生产不自动变更。

## 已知边界与后续
- PAI 的 400 根原始数值只核对了 **BTC 4h**，不能宣称已经跨四币所有周期逐根验证。此前 R3 中 1 处 PAI 看跌背离差异不涉及本策略阈值触发。
- 自动单测试主要为 FakeAdapter 模拟已成交情形；尚需用户的独立环境里进行 Binance USDM Demo 真正 API 连通/滑点/订单状态与恢复对账验收。
- 策略不能保证盈利；R2 测试不同时间框架分歧、4h 负收益、日线大回撤；本次改为 25% 分批是新执行政策，与之前 100% 单笔回测的收益率**不可直接等同**。
- 真实交易执行只允许用户自行启动；禁止在生产分支或服务器自行启动、部署或改变持仓。

## 2026-10-08 补充：修复“MatrixQuant 看不到买卖点”
- 根因：最初 UI 只显示 MatrixQuant PAI 曲线与已成交 `B/X`；`strategy_indicator_markers` 对 MatrixQuant 未赋值。没有真实 Demo 订单时，主图就缺少历史买卖点。
- 修复：新增 `matrixquant_strategy.chart_signal_markers(points)`，通过相同的已收盘 `PAIPoint.buy/sell` 将所有 PAI 阈值事件输出为独立的 `MFRA_PAI_BUY / MFRA_PAI_SELL` 指标标记。使用 TradingView 风格的绿色 BUY 上箭头/红色 SELL 下箭头；已成交 B/X 仍单独读取 `store.list_trade_markers`，只有 `FILLED` 才显示。
- 验证：BTC 4h 用户真实 TradingView 400 根数据校验历史信号；关闭 Demo、零订单时仍返回 BUY/SELL；最新尚未收盘 K 线不计算信号；既有 5s/SSSS 及对账基线逻辑保持不变。
- 数据边界：SiftAlpha 图表依据 Binance OHLC 重算阈值，而之前 TradingView 的数据为用户图表数据。两者的价格来源/更新时间不同可能造成个别信号偏差；不表示自动执行已发生。
- 正式状态：`UI_SIGNAL_MARKERS_IMPLEMENTED`；`OFFLINE_CI` 以最新流水线为准；`BINANCE_DEMO_LIVE_ACCEPTANCE` 仍然 `PENDING`，没有部署或自动启动。
