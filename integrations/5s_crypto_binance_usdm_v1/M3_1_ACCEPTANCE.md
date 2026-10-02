# M3.1 — 冻结信号引擎一致性

状态：**IMPLEMENTED_AND_VERIFIED**

目标：
把研究阶段冻结的 5s-crypto V1 三买三卖信号引擎从 JavaScript 逐公式移植为纯 Python，作为后续 SiftAlpha / Binance Demo 自动调度的唯一运行时信号实现。

冻结来源：
- `research/ssss/source_xma/experiments/fivegz5se_cross_symbol/fivegz5se_v1_engine.js`
- `research/ssss/source_xma/experiments/staged_entry_crypto_study/fivegz5se_staged_entry_experiment_v1.js`
- `research/ssss/source_xma/experiments/three_buy_three_sell_refinement_v1/refinement_compute_helpers_v1.js`
- `research/ssss/5S_CRYPTO_V1_BASELINE.md`

本轮实现：
- Trend / Capital / Momentum / Acceleration 四维基础状态
- Anomaly 第五维状态
- W1 / W3 / W5 net、slope、positive-count 特征
- BUY-A / BUY-B / BUY-C
- SELL-A / SELL-B / SELL-C
- onset（首次出现）语义
- 纯 Python，无 pandas / numpy 运行依赖

一致性门禁：
CI 使用冻结 JavaScript 原文件和 Python 新实现，对同一确定性 OHLCV fixture 逐根比较：
- 五维状态
- BUY active
- SELL active
- BUY onset
- SELL onset

只要任一根 K 线不一致，M3.1 即失败，不允许进入 M3.2。

本轮不包含：
- 调度循环
- 自动下单
- 仓位变更
- 实盘
- 策略优化


CI evidence:
- Run: 36826589155
- Frozen JS/Python signal parity: PASS
- Full unit test suite: PASS
- Compile: PASS
