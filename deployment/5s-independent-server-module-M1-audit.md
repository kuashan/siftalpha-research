# 5s 独立服务器模块 — M1 源码审计与构建方案（先验只读版）

日期：2026-10-08（JST）
目标：将 5s-crypto-multistrategy-ssss-v1 从 SiftAlpha Web ZIP / Workspace 执行链路迁移为 Oracle ARM 上独立管理的容器模块；本轮只审计与设计，不构建、不部署、不启动交易。

## 0. 冻结与证据边界

- 候选源码唯一事实源：私有仓库 `kuashan/siftalpha-research`，分支 `feature/5s-crypto-multistrategy-ssss-v1`。
- 本轮审计使用不可变源码提交：`7db2f6eb7eb8d12bddf63810564faa2b8a4c325e`。
- 路径：`integrations/5s_crypto_binance_usdm_v1/`。
- 该仓库的源代码快照 **尚未经 Oracle 现有 5s Workspace 哈希比对**；不能在比对之前声称此 commit 就是服务器运行版本。
- 无 Oracle 连接可供本次直接执行只读盘点，因此旧实例状态、持久化数据库、既有运行参数、真实文件清单、数据目录、容器状态暂标 **UNVERIFIED**。
- 未修改交易策略、未创建 Docker 构建文件、未构建镜像、未运行服务器脚本。

## 1. 已核对的源码事实

| 范围 | GitHub 源码证据 | M1 结论 |
| --- | --- | --- |
| 入口 | `app.py` 行 944–975：`create_server(host="127.0.0.1", port=0)`，`main(host="127.0.0.1", port=0)`，入口 `main()` | 需要外部启动包装固定 `0.0.0.0:8080`；不可只执行 `python app.py` |
| 运行依赖 | `requirements.txt` 当前仅锁 `binance-sdk-derivatives-trading-usds-futures==17.5.0`；CI 使用 Python 3.11、Node 22；浏览器 JS 由 GitHub workflow npm pack `lightweight-charts@5.2.1` 提供 | GitHub 构建应产出包含 vendor 资源的完整镜像，Oracle 只 pull |
| 静态/策略资产 | `strategy/SSSS.ftindex.b64` 在 CI 还原为原始 `SSSS.ftindex`，校验 SHA256 `25f8c56075c0021dd2d0567401d37def25d6a9b895f139b3a8a9abc376fecaa7` | 打包时严格复用验证流程，不改策略公式 |
| GitHub workflow | 存在 `.github/workflows/5s-crypto-multistrategy-ssss-v1.yml`，负责测试与 ZIP 构建；**不存在已证实的 5s ARM64 容器镜像 workflow** | `M2` 需要新增“部署包装 + 容器构建工作流”，不是从零创建项目测试 |
| DB | `config.py` 的 `FIVES_DB_PATH` 默认为 `data/5s_crypto_v1.db`；`storage.py` 使用 SQLite | 目标通过 `FIVES_DB_PATH=/data/5s_crypto_v1.db` 将 SQLite 与临时/程序文件分离 |
| 模式 | `config.py` 读取 `FIVES_MODE=PAPER`；只接受 PAPER/DEMO/TESTNET，其他值回退 PAPER | 裸 `MODE=PAPER` 不生效；`LIVE_TRADING=NO`、`API_KEY_EMPTY=YES` 不是现有源码强制门禁 |
| 交易连接 | `app.py` 提供 `POST /testnet-connect`，可通过网页向进程注入 DEMO 凭据；`strategy_scheduler.start()` 随 `app.main()` 启动；scheduler 在无凭据时返回 `WAITING_DEMO` | **只清空环境凭据并不足够**：首次运行需要禁止任意通过 HTTP 输入凭据/交易写入 |
| Web 端点 | `GET /` 返回 UI；`GET /api/status` 含外部行情探测 | 健康检查优先 GET `/`，避免依赖外部交易所可用性 |
| 资金/执行 | `engine/execution.py` 和 `exchange/binance_usdm_testnet.py` 含下单逻辑；`engine/paper.py` 提供 exposure preview | PAPER 无密钥并不等于已经具备完整纸面撮合/自动纸面交易；本轮不得宣称策略 PAPER 收益验证 |

## 2. 最小交付架构（M2 预案，不在 M1 实现）

1. **输入固定**：先让 Oracle 只读导出 `app.py`、`requirements.txt`、`config.py`、核心策略文件及现有打包清单的 SHA256/文件目录；与上述 GitHub commit 比对，确定确切唯一的版本。不能复制 .env、密钥、SQLite、订单日志到 GitHub。
2. **独立源码归档**：建议使用单独的私有 5s deployment 仓库/明确路径，继承已经验证的原始代码与 CI，提交不可变 source commit；不得把 `siftalpha-crypto` 其他项目自动当作此应用。
3. **GitHub Actions**：旧的 Python 单元测试、JS/Python parity、SSSS 原件 SHA256 校验和前端 vendor 构建复用；新增 ARM64 Docker Buildx，发布到 GHCR，记录 run ID、源 commit、OCI digest、SBOM/制品校验（如果现有工具支持）。
4. **启动包装**：通过独立的 entrypoint/server wrapper 固定 `app.main(host="0.0.0.0",port=8080)` 或等价的只读包装；不改 `app.py` 交易算法。启动前要求 `FIVES_MODE=PAPER`，所有 DEMO/TESTNET Key/Secret 为空，`LIVE_TRADING=NO`，`API_KEY_EMPTY=YES`，**由包装明确执行并验证**，不得把这几个标志当作旧程序天然支持的安全机制。
5. **首次运行硬安全**：在安全包装/路由层拒绝全部 HTTP POST（尤其 `/testnet-connect`、`/symbol-action`、`/emergency-flatten`），或提供同等经验证的不可绕过隔离；容器不得注入凭据、不得访问交易下单通道。用新建空数据库，旧交易状态不自动迁移。即便无 API Key，应用初始化也会启动 scheduler，因此需要在没有密钥的前提下验证没有任何 order submit 路径可用。
6. **存储**：唯一定义的持久化目录为 `/data`，数据库 `/data/5s_crypto_v1.db` 及 SQLite journal/WAL（如有）；日志写 stdout/stderr，由 Coolify 采集，凭据不落盘；源代码与镜像只读；明确备份/恢复演练、volume owner、迁移边界。
7. **访问**：容器端口 8080 仅暴露在受控 Docker 私网，host 不绑定公网端口；通过现有 WireGuard/私网路由访问，服务与代理 ACL 防止外部及其他不受信任容器绕过。Docker 非 root、无特权、不挂 docker.sock、限制内存/CPU、禁止 host network。确认认证/读写隔离。
8. **实例互斥**：旧 Coolify 5s 必须 STOPPED，自动部署/自动重启已禁用且有只读证据；不得在旧 5s 仍运行或可能自动启动时创建新的 active 交易进程。M3 通过且另行批准后再清理旧实例。
9. **部署分工**：GitHub Actions 构建并推送 digest-pinned `linux/arm64` OCI image；Oracle/Coolify 只拉取和启动；不通过 SiftAlpha ZIP/Source-Git，不在 Oracle 上 docker build。
10. **收尾边界**：M1 源码与现场事实审计 + 设计，M2 GitHub 构建镜像，M3 Oracle 私网部署和生命周期验收；任何 Gate 失败立即停止，不增开新机制。

## 3. M1 完成门禁（截至本次只读源码审计）

- `SOURCE_AUDIT=PARTIAL_GITHUB_SOURCE_ONLY`：已读源码，但 Oracle 工作区尚未核验。
- `ENTRYPOINT_DEFINED=PASS_DESIGN_ONLY`：已确认 `0.0.0.0:8080` 的外部包装调用；尚未生成/验证包装文件。
- `PAPER_SAFETY_BOUNDARY=BLOCKED_DESIGN_PENDING_VALIDATION`：网页凭据输入 / 状态恢复 / POST 与 scheduler 交互需验证拒绝。
- `PERSISTENCE_BOUNDARY=PASS_DESIGN_ONLY`：/data SQLite 已定义，旧 DB 迁移策略/真实权限未验。
- `PRIVATE_ACCESS_BOUNDARY=PASS_DESIGN_ONLY`：不暴露公网，WireGuard/代理 ACL 现场未验。
- `OLD_INSTANCE_NOT_RUNNING=UNVERIFIED_ORACLE`：必须读取 Coolify 资源状态和自动启动设置。
- `BUILD_INPUT_IMMUTABLE=BLOCKED_WORKSPACE_MISMATCH_UNKNOWN`：候选 commit 固定，但未与现有 5s Workspace 哈希对照。

```ini
M1=IN_PROGRESS_AUDIT
M2=NOT_STARTED
M3=NOT_STARTED
ORACLE_DEPLOYMENT=NOT_STARTED
STRATEGY_CODE_MODIFIED=NO
DOCKER_IMAGE_BUILT=NO
SERVER_MODIFIED=NO
STOP_AND_WAIT=YES
```

## 4. Codex 只读审计补齐内容（不得自动进入 M2）

只读盘点且隐藏所有凭据值：

- 确认现有 5s Workspace 完整目录、脚本哈希、ZIP 导入记录，与上方不可变 commit/Release ZIP 的一致性。
- 记录 Python / Node 版本、实际启动方式、当前配置字段和值的**安全布尔判定**（不要打印真实密钥）。
- 记录 DB 路径、权限、大小、持久化配置及其安全迁移或不迁移方案；不得接触用户交易状态用于测试。
- 记录旧 5s Coolify UUID（历史候选：`sfcfnzk2ia38saplhgzpw9dv`）、运行状态、自动启动/自动部署/重启策略；没有实际查询证据不能标 PASS。
- 检查 5s 实际版本 HTTP POST 是否支持通过网页注入 API Key，确认单纯空环境变量不能代表运行时强制无凭据。
- 确认同机既有服务占用、ARM64、私网网络和路由，不做端口绑定或容器启动。
- 给出最小新增文件清单和逐项门禁，首次部署限定为只读 PAPER 无交易实例。
- 报告仍缺少的证据，输出 `STOP_AND_WAIT=YES`。

## 5. 重要否定边界

禁止宣称当前 M1 已 CLOSED；禁止将 Docker 镜像构建的缺失等同于 5s 原有应用不能运行；禁止将 PAPER 与可执行模拟下单混淆；禁止发布含 .env、keys、真实交易数据的构建上下文；禁止同时运行新旧交易实例。
