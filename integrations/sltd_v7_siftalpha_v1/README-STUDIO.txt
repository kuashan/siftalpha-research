SLTD V7 · SiftAlpha 项目

入口：
  app.py

运行：
  python app.py

运行后脚本会输出：
  SIFTALPHA_WEB_URL=http://127.0.0.1:<自动端口>

SiftAlpha 检测到该地址并完成 Endpoint Probe 后即可点击“打开”。

默认股票：
  AAPL

可通过环境变量改变默认股票：
  SLTD_SYMBOL=MSFT

本项目：
- Python 标准库即可运行
- 无需 Node
- 无需数据库
- 无需固定端口
- 300 根 K 线仅用于 Web 显示
- SLTD 指标计算使用所选周期的完整已结束 K 线
- K 线周期可选：5m / 15m / 30m / 1h / 4h / 1d
- 正式信号只在所选周期 K 线结束后确认
- 当前形成中的 K 线不参与正式信号
- 确认后的动作在下一根同周期 K 线开盘执行
- 1d 为已验证周期；其他周期当前为实验周期
- 当前仅分析与模拟仓位，不连接真实券商下单

冻结策略：
  SLTD V7 12-rule Candidate v1
  source commit: 5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042

统一仓位策略：
  I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED

Hard Exit：
  C2_FULL_CANDLE_BELOW_SLOW_BAND
