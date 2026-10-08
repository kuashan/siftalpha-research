# 5s 独立服务器模块 — M1 审计与部署设计（功能保留版）

日期：2026-10-08（JST）
说明：本版纠正此前“不允许 API Key / 禁止 HTTP POST / 只读 PAPER / 禁止模拟下单”等不当限制。**这些限制全部撤回**。本轮只纠正设计文档，不改策略源码、不构建、不部署、不启动交易。

## 0. 用户授权边界

- 5s 是用户自主控制的交易系统。**服务器独立部署不能以安全之名擅自禁用或删改已有功能**。
- 现有功能须保留：Binance Demo（模拟交易）账户连接及凭据录入、策略启停、自动模拟买卖、撤单、恢复对账、保证金操作、紧急平仓、网页设置与所有原有合法 HTTP POST。
- PAPER、DEMO、TESTNET 的实际行为由原代码和用户配置决定；不得硬编码 `FIVES_MODE=PAPER` 或一律清空 API Key/Secret，阻断用户选择的 Demo 交易。
- 安全边界作用于**防止密钥泄露、阻断未经授权访问、避免部署时意外并行实例/重复下单、核对目标环境**，而不是剥夺用户正常交易操作。
- 当前已审源码没有 LIVE 实盘接入实现，不得宣称已经支持 LIVE，也不得因本次部署擅自增加真实资金交易能力。后续是否开发、启用 LIVE 由用户单独决定。
- 不允许代理擅自改动交易信号、仓位计算、订单映射或原本冻结的 5s/SSSS 策略逻辑。

## 1. 版本与证据

- GitHub 候选事实源：`kuashan/siftalpha-research` 的 `feature/5s-crypto-multistrategy-ssss-v1`。
- 已审源代码不可变 commit：`7db2f6eb7eb8d12bddf63810564faa2b8a4c325e`。
- 程序路径：`integrations/5s_crypto_binance_usdm_v1/`。
- 尚未与 Oracle 原 5s Workspace/ZIP 的文件清单及 SHA256 比对；因此候选 commit **不代表已经证明与现有运行版本一致**。
- 服务器旧实例状态、持久化数据、实际容器参数、私网路由尚未现场核验，不得猜测 PASS。

## 2. 已审源码事实

| 范围 | 代码依据 | 结论 |
| --- | --- | --- |
| Web 启动 | `app.py`：`main(host="127.0.0.1", port=0)`；入口直接 `main()` | 外部部署启动包装显式调用 `app.main(host="0.0.0.0", port=8080)`，不修改策略 |
| 运行环境 | `requirements.txt` 锁 `binance-sdk-derivatives-trading-usds-futures==17.5.0`；现有 CI Python 3.11 / Node 22 / `lightweight-charts@5.2.1` | 保留 CI 回归和依赖构建；新增 ARM64 镜像包装 |
| SSSS 原件 | 由 `strategy/SSSS.ftindex.b64` 还原，SHA256 `25f8c56075c0021dd2d0567401d37def25d6a9b895f139b3a8a9abc376fecaa7` | 保留字节级校验，不修改公式 |
| 现有 CI | `.github/workflows/5s-crypto-multistrategy-ssss-v1.yml` 做策略回归与 ZIP 打包 | 目前没有已核实的独立 5s ARM64 OCI 镜像构建流程；需要新增部署包装 |
| 模式配置 | `config.py` 实际读取 `FIVES_MODE`，接受 PAPER/DEMO/TESTNET；其他值回退 PAPER | 按用户选择运行，不得用 `MODE=PAPER` 等无效变量强行约束 |
| Demo 连接 | `runtime_testnet_session.py`、`app.py` 接受用户提供的 DEMO 凭据，且 `POST /testnet-connect` 能连接/校验模拟账户 | 这是已有核心功能，必须保留，不能用“空 API Key”作为永久运行规则 |
| 自动交易 | `engine/scheduler.py`、`engine/execution.py` 通过 DEMO 适配器执行已启用的策略；缺凭据时状态 `WAITING_DEMO` | 有效 Demo 凭据应允许用户在模拟交易账户实际下单 |
| Web 表单 | `app.py` 保留 `/symbol-action`、`/symbol-strategy`、`/testnet-connect`、`/reconcile`、`/cancel-strategy-orders`、`/emergency-flatten` 等 POST | **禁止全局阻断 HTTP POST**；要以私网/鉴权保护控制界面 |
| 持久化 | `config.py` 的 `FIVES_DB_PATH`，`storage.py` SQLite | 建议独立持久化 volume `/data`，不随镜像重建丢失状态 |
| 健康检查 | `GET /` 返回 UI；`GET /api/status` 含外部行情探测 | 使用仅确认 Web 可用的无交易副作用健康检查，不把行情供应商短暂失败当成容器退出 |

## 3. M2 独立构建与运行方案（尚未执行）

1. **版本固定**：先对照 Oracle Workspace/ZIP 与源码 commit 的文件列表及哈希，明确实际 5s 运行版本。不要上传真实密钥、.env、SQLite、历史订单。
2. **最小部署包装**：只新增独立启动包装 / Dockerfile / Compose / GitHub Actions 构建工作流；不得修改策略算法、原本的交易接口或 UI 功能。
3. **端口**：Web 包装固定 `0.0.0.0:8080`，容器本身不绑定公网端口；通过 WireGuard、私网反向代理及访问鉴权提供控制台。
4. **模式与交易**：完整保留 PAPER、Binance DEMO/TESTNET 原有能力。使用 `FIVES_MODE` 和原应用已有 Demo 账户连接机制；凭据通过用户指定的受控密钥机制/私网表单输入，不写入镜像、GitHub、日志、公开配置。仅做环境识别，**不阻断模拟交易请求**。
5. **存储**：SQLite 位于独立受控 `/data` volume，配置 `FIVES_DB_PATH=/data/5s_crypto_v1.db`。制定数据库备份、恢复与切换方案；未经用户批准不重置现有状态。
6. **构建**：GitHub Actions 先跑现有回归测试，再生成 `linux/arm64` GHCR 镜像，提供固定源 SHA、run ID、digest 和回滚方案。Oracle 仅拉取镜像，不直接从源码 docker build。
7. **双实例**：旧 5s 在切换期间保持停机或明确隔离，避免两个实例对同一 Demo 账户同时下单；这是部署冲突防护，不是禁用 5s 功能。旧实例仅在新部署通过且用户同意后清理。
8. **用户自主控制**：配置、连接 Demo、选择策略、启动/停止自动交易均由用户经受保护的私网 UI 执行；自动化代理不得擅自代替用户切换交易环境或启用策略。
9. **收尾**：M1 审计、M2 镜像构建、M3 私网部署与 Demo 交易完整功能验证，每阶段 PASS/BLOCKED/CLOSED；不因单个错误无限增设适配器。

## 4. M1 Completion Gate（调整后的真实要求）

- `SOURCE_AUDIT=PARTIAL_GITHUB_SOURCE_ONLY`：已核对源码，仍需 Oracle 版本匹配。
- `ENTRYPOINT_DEFINED=PASS_DESIGN_ONLY`：已明确 `app.main(host="0.0.0.0", port=8080)`，尚未实现包装。
- `TRADING_CAPABILITY_PRESERVED=PASS_DESIGN_ONLY`：方案明确不屏蔽 Demo 连接、POST 或自动模拟交易，仍需未来镜像验证。
- `DEMO_TRADING_BOUNDARY=PASS_DESIGN_ONLY`：目标限定为当前已有的 Binance Demo/Testnet 实现，未实际部署验证。
- `PERSISTENCE_BOUNDARY=PASS_DESIGN_ONLY`：已明确 `/data`，尚未现场验证。
- `PRIVATE_ACCESS_BOUNDARY=PASS_DESIGN_ONLY`：已明确 WireGuard/私网访问，尚未现场验证。
- `OLD_INSTANCE_NOT_RUNNING=UNVERIFIED_ORACLE`：需核对旧资源状态与自动重启行为。
- `BUILD_INPUT_IMMUTABLE=BLOCKED_WORKSPACE_MISMATCH_UNKNOWN`：候选 commit 固定，但未与 Oracle 工作区比对。


## M1 现场审计收口（2026-10-08）

本节记录本次只读审计的最终事实，并覆盖前文中尚未完成的占位状态。M1 仅完成审计、边界确认和构建方案；没有开始 M2 构建，也没有进行 Oracle 部署或交易动作。

### 源码与制品一致性

- `REMOTE_HEAD=968999119a4e4ff1ad53c0dd1b625f4593025b3e`；目标分支与该提交比较结果为 `identical`。
- `SOURCE_COMMIT=7db2f6eb7eb8d12bddf63810564faa2b8a4c325e`，作为策略源码不可变输入；分支 HEAD 为后续文档提交。
- 用户提供 ZIP 的 SHA-256：`7e71c46d4b92afa972f899249aa665d7c568753a29edee93dfb4a795b8c1e157`。
- ZIP 路径遍历检查通过，未发现符号链接；发现的 `__pycache__` 仅作为本地生成物，不能进入私有源码仓库或正式构建上下文。
- GitHub 固定源码提交的 19 个受跟踪源文件与 ZIP 的 Git blob SHA 全部一致。ZIP 中的 lightweight-charts vendor 文件属于现有 CI 生成依赖，不属于该源提交中的策略源码。
- Oracle immutable workspace revision 为 `e61ef33ee85bf67cbbd4009bd3d91948477f878b858815d8ea209d484d33f2ae`；去除 `__pycache__` 后与 ZIP 均为 21 个文件，规范化树哈希为 `93531c7f17785a9e1e3559e5030262e10bdc2fcd56f17b7fcac92189f7c73f58`。结论：`WORKSPACE_SOURCE_MATCH=PASS`。

### 运行能力与交易边界

- 入口是 `app.py`；当前默认 `main(host="127.0.0.1", port=0)`。M2 只增加非策略启动包装，调用 `app.main("0.0.0.0", 8080)`，不改策略源码。
- requirements 仅包含 `binance-sdk-derivatives-trading-usds-futures==17.5.0`；现有 CI 使用 Python 3.11。Oracle 主机为 ARM64（`aarch64`），运行时 Python 为 3.12.3，M2 镜像将以 CI 固定的 Python 3.11 作为可复现构建输入。
- `FIVES_MODE` 支持 `PAPER`、`DEMO`、`TESTNET`；Demo/Testnet 凭据通过环境变量或现有 `/testnet-connect` 流程加载。现有调度、下单、撤单、恢复对账、紧急平仓及四个交易对逻辑均在源码中保留。没有在本次审计中输出、上传或提交任何密钥，也没有发送订单。
- 现有合法控制面接口（包括 symbol action、strategy、testnet-connect、reconcile、cancel-strategy-orders、emergency-flatten）已核对存在；M2 不得通过安全包装删减这些既有能力，也不得把 Demo 强制改成 PAPER。
- Oracle 当前没有运行中的 5s 容器，也没有 5s systemd unit；Coolify 中唯一旧 5s Application 为 `lmhifd5qwbuzdhqwxhbe5yeq`，状态为 `exited:unhealthy`。因此当前没有已知自动交易实例。旧实例自动部署/自动启动开关未由当前 API 响应暴露，记录为 `OLD_INSTANCE_AUTOSTART=UNVERIFIED`，M2 切换前必须再次确认。
- 代码默认数据库路径为 `data/5s_crypto_v1.db`；当前 immutable workspace 未发现数据库、日志或交易记录。M2 运行时必须显式设置 `FIVES_DB_PATH=/data/5s_crypto_v1.db`，仅挂载独立 `/data`，不得覆盖或重置既有数据。
- Oracle `wg0` 已存在并使用 `10.77.0.1/24`；宿主机 8080 当前无监听。M2 使用现有 WireGuard 私网访问，不新增公网 host port。

### M2 最小构建方案（仅方案，未执行）

1. 在私有仓库中保留现有策略目录与现有测试；只新增部署包装文件，不改 `engine/`、`strategy/`、`exchange/`、`app.py` 的交易逻辑。
2. 新增 ARM64 可构建的 Dockerfile，基于 Python 3.11 的多架构基础镜像，并在 M2 锁定基础镜像 digest；安装现有 requirements，复制策略源码和只读前端 vendor，使用独立 entrypoint 调用 `app.main("0.0.0.0", 8080)`。
3. 新增 image-only Compose：镜像以不可变 digest 引用；独立服务名和网络；仅挂载 `/data`; 不发布公网端口；私网访问通过现有 Coolify/WireGuard 路径完成。凭据只通过运行时 secret/environment 注入。
4. 新增 GitHub Actions：先运行现有 Python/Node/策略/UI 测试，再以 `linux/arm64` 构建并推送 GHCR；记录源 Commit、Run ID、镜像 digest 和测试结果。Oracle 只 pull 固定 digest，不在服务器编译源码。
5. 回滚使用上一枚已验收镜像 digest 与其独立 `/data` 配置；部署前保存运行配置，切换失败只恢复旧镜像，不删除 workspace、数据库或其他项目。旧实例在新实例通过完整验收前保持不变，但必须避免同一账户出现两个自动交易运行者。

### M1 结论

本阶段已完成源码、用户 ZIP、Oracle workspace、旧运行资源、交易能力保留边界和 ARM64/GHCR 构建方案审计。结论为：可以进入 M2，但 M2 尚未开始；旧实例自动启动设置仍需在 M2 前置检查中确认。



## M2 构建执行结果（2026-10-08）

- `M2_CI_RUN=37726219374`
- `M2_CI_RESULT=PASS`
- 构建源提交：`790c7bd06ff961527d9fe75196d145cd2eea9a5a`
- Python 基础镜像在 CI 中按 digest 解析：`python:3.11-slim-bookworm@sha256:0a310eeecf4e1f5a0743f9a6520c90c88d089c903ca5fd283f501e3a805f5f89`
- ARM64 镜像：`ghcr.io/kuashan/5s-crypto-multistrategy-ssss-v1:sha-790c7bd06ff961527d9fe75196d145cd2eea9a5a`
- 镜像平台：`linux/arm64`
- 镜像 digest：`sha256:8354ee4019234e8da6ba2a38578575b61cb17c279a7a9b1ce83ee6aac569b622`
- CI 已通过现有 SSSS 回归、冻结策略校验、UI contract、PAPER import、M2 packaging contract、Compose interpolation/source boundary 和 Docker Buildx ARM64 构建。
- 本阶段没有访问 Oracle、Coolify、Docker 主机或交易实例；没有注入或输出任何 API 凭据。


```ini
REMOTE_HEAD=790c7bd06ff961527d9fe75196d145cd2eea9a5a
SOURCE_COMMIT=7db2f6eb7eb8d12bddf63810564faa2b8a4c325e
SOURCE_AUDIT=PASS
WORKSPACE_SOURCE_MATCH=PASS
ENTRYPOINT_DEFINED=PASS_DESIGN_ONLY
TRADING_CAPABILITY_PRESERVED=PASS_AUDIT_ONLY
DEMO_TRADING_BOUNDARY=PASS_AUDIT_ONLY
PERSISTENCE_BOUNDARY=PASS_DESIGN_ONLY
PRIVATE_ACCESS_BOUNDARY=PASS_DESIGN_ONLY
OLD_INSTANCE_NOT_RUNNING=PASS
OLD_INSTANCE_AUTOSTART=UNVERIFIED
BUILD_INPUT_IMMUTABLE=PASS

DOCKERFILE_PLAN=PASS
COMPOSE_PLAN=PASS
GITHUB_ACTIONS_PLAN=PASS
GHCR_IMAGE_PLAN=PASS
ROLLBACK_PLAN=PASS

M2_CI_RUN=37726219374
M2_CI_RESULT=PASS
M2_SOURCE_HEAD=790c7bd06ff961527d9fe75196d145cd2eea9a5a
M2_IMAGE=ghcr.io/kuashan/5s-crypto-multistrategy-ssss-v1:sha-790c7bd06ff961527d9fe75196d145cd2eea9a5a
M2_IMAGE_DIGEST=sha256:8354ee4019234e8da6ba2a38578575b61cb17c279a7a9b1ce83ee6aac569b622
M2_PLATFORM=linux/arm64

STRATEGY_CODE_MODIFIED=NO
TRADING_FUNCTIONS_DISABLED=NO
ORACLE_DEPLOYMENT=NOT_STARTED

M1=PASS/CLOSED
M2=PASS/CLOSED
M3=NOT_STARTED

FIRST_BLOCKER=OLD_INSTANCE_AUTOSTART_UNVERIFIED_BEFORE_M3
STOP_AND_WAIT=YES
```

## M3 Oracle 部署与验收结果（2026-10-08）

- 旧 Coolify Application `lmhifd5qwbuzdhqwxhbe5yeq` 保留，状态为 `exited:unhealthy`，无运行容器；未配置自动部署，未修改旧资源。
- 新建独立 Coolify Docker Image Application：`v7xgbs1bqydpsaujrniqhiaf`，名称 `5s-crypto-multistrategy-ssss-v1-m3`。
- 镜像固定为 `ghcr.io/kuashan/5s-crypto-multistrategy-ssss-v1@sha256:8354ee4019234e8da6ba2a38578575b61cb17c279a7a9b1ce83ee6aac569b622`，Oracle ARM64 匿名 manifest 拉取通过。
- 仅暴露容器端口 `8080`，未配置 host port；容器连接 `coolify` 网络，数据使用独立 `/data` named volume。
- 首次运行使用 `FIVES_MODE=PAPER`，未注入 Binance API key/secret；未执行交易。
- Private URL `http://5s-crypto-multistrategy-ssss-v1-m3.10.77.0.1.sslip.io` 经 `10.77.0.1:80` 返回 HTTP 200。
- Coolify 生命周期验收：Stop、Start、Restart 均通过；Restart 后容器仍为 running，旧应用、SiftAlpha Web、Production Agent、WireGuard、Xray、Docker 和 Cockpit 未修改。
- 回滚快照：`/var/lib/siftalpha-web/m3-rollback-20261008T043740Z`。

```ini
OLD_INSTANCE_NOT_RUNNING=PASS
OLD_INSTANCE_AUTOSTART=NO
ORACLE_DEPLOYMENT=PASS
M3_APPLICATION_UUID=v7xgbs1bqydpsaujrniqhiaf
M3_IMAGE_DIGEST=sha256:8354ee4019234e8da6ba2a38578575b61cb17c279a7a9b1ce83ee6aac569b622
M3_PRIVATE_HTTP=200
M3_STOP=PASS
M3_START=PASS
M3_RESTART=PASS
M3_PERSISTENCE=PASS
M3_PUBLIC_HOST_PORT=NO
M3_TRADING_MODE=PAPER
M3_API_KEYS_INJECTED=NO
M3=PASS/CLOSED
FIRST_BLOCKER=NONE
STOP_AND_WAIT=YES
```

## 5. Codex 本阶段只读盘点

- 核对当前真实远端 HEAD、新提交与原 5s Workspace 对应版本，避免错误镜像源。
- 只读核对原程序和 UI 的 DEMO/TESTNET 交易操作、凭据注入与环境绑定，报告真实功能，不删除。
- 只读核对旧 Coolify 实例、数据库与私网状态；不要未经授权修改交易状态。
- 识别独立部署需要新增的最小文件及严格测试项，不修改现有策略代码。
- 交付审计报告后 `STOP_AND_WAIT=YES`，不提前构建、运行或发交易指令。

**本文件替代先前的全局 POST 禁止、空 API Key、只读 PAPER 强制约束。**


## 2026-10-09 三策略 MFRA 镜像更新与 Oracle 部署记录

本记录对应用户确认的三策略版本提交 `17b46fc0404dea3e26308f4eb1675581360272ce`。该提交本身为文档收尾提交；随后仅增加了 ARM64 workflow 的 MFRA 分支触发与三策略 CI 断言修正，未修改交易策略或运行逻辑。

```ini
REPOSITORY=kuashan/siftalpha-research
BRANCH=feature/5s-crypto-multistrategy-mfra-v1
USER_FUNCTIONAL_COMMIT=17b46fc0404dea3e26308f4eb1675581360272ce
DEPLOY_SOURCE_COMMIT=b2adcdc9521b6b1cc6644152287980cd716e07b3

ARM64_CI_RUN=37805279934
ARM64_CI_RESULT=PASS
ARM64_PLATFORM=linux/arm64
ARM64_IMAGE=ghcr.io/kuashan/5s-crypto-multistrategy-ssss-v1
ARM64_IMAGE_DIGEST=sha256:98b1cd730cdc74bcfd282d6a77ad1d715a7a1eb15c9548bb5e389ad1c01b7fb9

COOLIFY_APPLICATION_UUID=v7xgbs1bqydpsaujrniqhiaf
COOLIFY_DEPLOYMENT_UUID=cfmhgjavl9itb79rsursgudo
COOLIFY_DEPLOYMENT_STATUS=finished
COOLIFY_IMAGE_READBACK=PASS

ROLLBACK_PATH=/var/lib/siftalpha-web/5s-mfra-deploy-b2ad-20261008T160619Z-before-arm64
PRIVATE_URL=http://5s-crypto-multistrategy-ssss-v1.10.77.0.1.sslip.io
PRIVATE_HTTP=200
MFRA_UI=PASS
SSSS_UI=PASS
TRADING_ACTIONS_EXECUTED=NO
NEW_COOLIFY_APPLICATION=NO
STRATEGY_CODE_MODIFIED=NO
```

部署只更新了既有 Coolify Application 的镜像 digest；没有新建 Application，没有执行交易、策略启停或账户操作。