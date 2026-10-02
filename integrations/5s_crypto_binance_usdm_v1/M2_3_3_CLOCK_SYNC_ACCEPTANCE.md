# M2.3.3 Binance 服务器时间自动校准 — 2026-10-01

状态：**IMPLEMENTED_AND_VERIFIED**

问题：
Binance 签名接口返回 -1021，表示客户端签名时间戳超出服务器允许窗口。

修复：
- 在真实签名调用前，通过官方 USDⓈ-M Futures SDK 的公开 server time 接口读取币安服务器时间。
- 使用一次网络往返的本地起止时间中点估算 clock offset（时钟偏移）。
- 将偏移量应用到官方 SDK 的毫秒时间戳生成器。
- 偏移仅存在于当前 Python 进程，不修改手机或 Alpine 系统时钟。
- 5 分钟内复用校准结果，之后自动重新校准。
- 原有 Demo Trading、动态 Web 端口、中文 UI、安全凭据边界全部保留。

策略逻辑、资金逻辑和信号规则未修改。
