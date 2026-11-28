# RE-Framework v2

> **逆向工程 + 编程的通用工程方法论框架**，DeepSeek Harness（DSH）是唯一维护宿主。
> 验证语义引用 [Anchorlaw Protocol v0.27.1](https://github.com/unknowbug/anchorlaw)（协议引用，不复制实现）。

RE-Framework 不是一组提示词，而是把"证据驱动的分析与实现"固化成可执行流程：先读知识库 → 架构设计 → 勘探 → 分析 → 验证 → 独立审查 → 人类确认 → 归档。框架本身能维护自己：技能、preset、工具和自检都在同一个仓库里，任何改动都必须通过 fail-closed 门禁。

## 它解决什么问题

| 常见失效 | 框架的约束 |
|---|---|
| 结论只留在对话里、下一轮就丢 | 产物必须落 `.artifacts/` / `.investigations/`，索引同步 |
| AI 自评自证、错误结论升格 | `confirmed` 只能由人类授予；judge 独立审查 |
| 多假设混在一起自推 | 互斥假设 MUST fan-out，分支隔离、`.bN` 候选可追溯 |
| 大工程产物按"领域"堆在一起 | 按**目标程序自身的模块**分区（spec §5.7） |
| 子代理各自为政、无法追责 | Work Order 契约 + DSH name + `producer`（spec §4.6） |
| 用行数/计数冒充"等价" | 等价性证据形态阶梯 E1/E2/E3（spec §5.8） |
| 反复踩同类坑 | 错误账本优先 + 273 条跨项目实战案例库 + 已知回归门禁 |

## 核心机制

- **证据优先**：`@anchor.test` 必须有可追溯 source（trace/memory/probe）；静态推断只能进 `@anchor.idk`。
- **角色隔离**：scout / worker / judge / fan-out 都是 subagent；主会话只编排与执行，不替代分析或自审。
- **强制触发链**：judge（确认前/重大转向/收尾）、scout（机制未明）、fan-out（≥2 互斥假设）、knowledge（结论落盘）——预置在计划里，执行只核对。
- **目标模块化**：模块来自构建文件/RTTI/命名空间等证据；产物、代码、知识按目标模块归位，修正走 plan→apply→rollback。
- **协作契约**：每次委派携带 Work Order（范围/交付/验收/停止条件），Lead 单写根索引，任务完成 ≠ 结论确认。
- **知识生长**：错误账本优先于正确结论；`knowledge-builtin/portable/` 保存 273 条跨项目实战案例与 40 条提炼规则。

## 快速开始（DSH）

前置：Python 3.x；Node.js ≥ 24.22.3（DSH 要求）。

```powershell
# 1. 安装/同步：bundle → 每个 profile，17 个技能 → 用户级全局
pwsh dsh/scripts/install.ps1

# 2. 自检（八段，必须全绿）
pwsh dsh/scripts/selfcheck.ps1

# 3. 在任意项目开会话（任何 preset 都能加载 ref-* 技能）
#    需要完整工作台人格时，选 re-framework preset
```

DSH Desktop（Electron / `app.asar`）由同一轮安装覆盖；安装后需**重启 Desktop** 并在新会话选择 RE-Framework。详见 [dsh/README.md](dsh/README.md)。

## 从 DSH 插件市场安装

RE-Framework 已按 DSH Bundle 规范打包，仓库根 `package.json` 声明 `dsh.bundle.patch`：

```powershell
# 源码安装（Plugin Hub 当前可用；需要 DSH >= 0.2.0）
dsh plugin --profile web add github:unknowbug/RE-Framework

# npm 安装（包发布后可用；插件中心的展示需要 npm 包）
dsh plugin --profile web add @dsh-external/dsh-re-framework
```

- **Plugin Hub 分类**：Skills & Agents（agent）→ 子智能体 / 技能包；不是 Development & Operations。
- **兼容**：DSH `>=0.2.0 <0.3.0`；Desktop 与 CLI 同一 bundle；安装后重启并新开会话。
- **权限**：工作区文件读写、subprocess（python 脚本）、subagent 工具；不发网络请求，不读取工作区外凭据。
- **许可证**：MIT（见 [LICENSE](LICENSE)）。

## 架构

```
RE-Framework/
├── AGENTS.md                  # DSH-first 索引（自动加载入口）
├── package.json               # DSH bundle 入口（Plugin Hub / npm 打包）
├── LICENSE                    # MIT
├── spec/                      # 框架协议（§1-§9；§4.6 协作契约、§5.7 目标模块、§5.8 等价性阶梯）
├── dsh/                       # DSH 宿主适配层（唯一维护区）
│   ├── skills/                # 17 个 ref-* 技能（单一事实源）
│   ├── SKILL-MAP.md           # DSH 探测器：强初始化 / 路由 / Phase 0-3
│   ├── plugins/               # 3 个 ref_* 工具 + 契约守卫（R1/R3/R5）
│   ├── cordis.patch.yml       # agent preset 声明（bundle patch 载体）
│   ├── scripts/               # install / selfcheck / patch_layer / target_modules
│   └── tests/                 # 行/变量/回归/工作单/便携索引/契约守卫测试
├── templates/                 # 产物 schema + agent-work-order.yaml
├── knowledge-builtin/         # 预置知识；portable/ = 273 条实战案例 + rules.md
├── scripts/                   # merge_index.py / absorb_portable_knowledge.py
├── CHANGELOG.md / CHANGELOG_EN.md   # 发布历史（README 不再承载）
└── archive/reasonix/          # Reasonix 宿主格式归档（只读）
```

## 模块与技能

| 模块 | 技能（kebab 名） | 入口 |
|---|---|---|
| core | `core-plan` `core-artifact` `core-knowledge` `core-version` `core-fanout` `core-worker` `core-judge` | 所有任务 |
| re-binary | `re-scout` `re-lift` `re-classify` `re-trace` | 二进制/汇编/IDA/Ghidra/vtable/RTTI |
| re-code | `recode-scout` `recode-deobfuscate` `recode-classmap` `recode-behavior` | 字节码/源码/反混淆/mods |
| swe | `swe-guide` → Anchorlaw `anchor-*` | 编写/修改/审查代码、测试 |
| 维护 | `ref-maintain` | 维护本框架的 DSH 适配层 |

共 17 个技能；`re-framework` preset 另挂 3 个 `ref_*` 工具（status / merge_index / init）与契约守卫。技能对任意 preset 的会话可见；工具只在 re-framework preset 内。

## 文档导航

| 想知道 | 读 |
|---|---|
| 框架规范（铁律/工作流/产物/知识/版本） | [spec/engineering-framework-v1.md](spec/engineering-framework-v1.md) |
| DSH 维护规则（安装/自检/preset/Desktop） | [dsh/AGENTS.md](dsh/AGENTS.md) |
| 会话怎么开始、怎么路由 | [dsh/SKILL-MAP.md](dsh/SKILL-MAP.md) |
| 发布历史与版本命名 | [CHANGELOG.md](CHANGELOG.md) |
| 273 条实战案例与 40 条规则 | [knowledge-builtin/portable/README.md](knowledge-builtin/portable/README.md) |
| 产物模板 | [templates/README.md](templates/README.md) |

## 维护与版本

- 技能**单一事实源**是 `dsh/skills/`；安装产物一律可再生，改完跑 `install.ps1`，不要手改 `~/.dsh`。
- 任何改动必须 `selfcheck.ps1` 八段全绿；门禁 fail-closed，不可执行按失败处理。
- 版本：发布版 `X.Y.Z`，`Z` = FIX（不产生新 spec 文件）；协议版本独立（当前 v1）。完整规则与历史见 [CHANGELOG.md](CHANGELOG.md)。

## License

MIT。见 [LICENSE](LICENSE)。

## 归档

Reasonix 宿主格式（dot 名技能、`.reasonix/skills/`、`install.py`/`validate_manifest.py`）自 2026-08-21 停止维护，归档在 `archive/reasonix/`（含 RESTORE.md，可自行恢复迭代）。框架核心 `spec/`、`templates/`、`knowledge-builtin/`、`scripts/merge_index.py` 保留。
