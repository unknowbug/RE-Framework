# RE-Framework v2 — 通用工程方法论框架（逆向 + 编程，DSH 宿主）

> 基于《打破传统AI逆向的新思路：多Agent、自主管理上下文》(BitWarden, 看雪学苑 2026.06.18) 的方法论内核，
> 工程化、Skills化、SubAgents化拆分升级：**领域无关核心 + 按需加载领域模块**，从二进制逆向到代码逆向到常规编程全兼容。
> **DeepSeek Harness（DSH）是唯一维护宿主**（2026-08-21 起；Reasonix 宿主格式已归档至 `archive/reasonix/`，Fork 可恢复自行迭代）。
> 验证协议继承 [Anchorlaw Protocol v0.24](https://github.com/unknowbug/anchorlaw)（MIT，协议引用，不复制实现）。

---

## 快速开始（DSH）

```powershell
# 1. 安装到 DSH 运行时（一次安装）
pwsh dsh/scripts/install.ps1
#    → 用户级全局技能：17 个 ref-* 装到 ~/.dsh/skills/（任何 preset/工作目录的会话按需加载）
#    → re-framework preset：完整工作台（人格 + 3 个 ref_* 工具：status/merge_index/init）

# 2. 在任意项目（如 E:\PYTHON\CoreSwap）工作区开会话（任何 preset）
#    → ref-* 技能开箱即用，cwd 在项目、产物落项目、本仓库零污染
#    → 需要框架工作台人格时再选 re-framework preset

# 3. 自检（工具链 / 技能 manifest / 安装产物 / 插件 schema / preset 门禁 / 目标模块 + 守卫）
pwsh dsh/scripts/selfcheck.ps1

# 4. 目标模块化（大型工程建议；spec §5.7）
python scripts/target_modules.py <项目> derive   # 推导目标模块 → 分区产物/代码/知识
python scripts/target_modules.py <项目> verify   # G1-G9 门禁
```

**DSH 会话标准流程**：根 `AGENTS.md`（DSH-first 索引）→ 先读 `dsh/SKILL-MAP.md`（DSH 探测器：强初始化 / 任务路由 / Phase 0-3 / 执行强制链）→ 按 **kebab 名**加载技能执行。

## 架构

```
RE-Framework/
├── AGENTS.md                  # DSH-first 索引（自动加载入口）
├── spec/                      # 框架协议（铁律/工作流/产物/知识库/版本）+ Anchorlaw v0.24 引用
├── dsh/                       # DSH 宿主适配层（唯一维护区）
│   ├── skills/                # 17 个 ref-* 技能（单一事实源，直接维护）
│   ├── SKILL-MAP.md           # DSH 探测器（强初始化/路由/Phase 0-3/执行强制链 + dot→kebab 映射）
│   ├── plugins/re-framework-tools.js   # 3 个 ref_* 模型工具 + 契约守卫（R1/R3/R5）
│   ├── cordis.patch.yml       # agent preset 声明（ACTIVE carrier）
│   ├── scripts/install.ps1 + selfcheck.ps1 + gen_cheatsheet.py   # 安装 + 七段自检 + 压实派生视图生成模板
│   ├── tests/                 # test_manifest / check_plugin_schema / audit_preset_rows / audit_prompt_variables / test_target_modules / test_contract_guard
│   └── AGENTS.md              # DSH 维护入口
├── templates/                 # 产物 schema（语言无关）
├── knowledge-builtin/         # 预置知识库
├── scripts/merge_index.py     # 并行索引合并（ref_merge_index 依赖）
├── scripts/target_modules.py  # 目标模块管理：derive / verify G1-G9 / plan→apply→rollback / repair（spec §5.7）
└── archive/reasonix/          # Reasonix 宿主格式归档（只读，RESTORE.md 可恢复）
```

## 目标模块化（v2.12，spec §5.7）

**要解决的问题**：大型工程里，不同子系统（renderer / netcode / gameplay；Java 包 / .NET 命名空间 / 源码构建单元）的结论会混在同一棵扁平产物树（`classes/`、`functions/`、`cross_refs/`）里——找不到"这条结论属于谁"，同一事实被两处重复推导，合并时冲突。框架以前只有**领域模块**（core / re-binary / re-code / swe），没有**目标程序自己的模块**这一层。

**做法**：按目标程序自身的模块管理**产物、代码与知识**；模块来自目标证据，不是人工列清单。

### 核心概念

- **目标模块 ≠ 领域模块**：前者是程序的子系统（如 `netcode`），后者是框架打包单元（`re-binary`）。索引里分别用 `target_module` 与 `module`，不混用。
- **边界是假设，不是事实**：每条边界带证据（构建文件 / RTTI / 命名空间 / section / 包）与 `confidence`（derived / converged / disputed / confirmed）；拿不到证据的产物进 `unassigned/`——**未分配是一等公民，允许长期存在**，不硬塞。
- **评审与确认绑定「模块 + 修订」**：模块结构或归属一变，`candidate | confirmed` 自动回 `draft`（原状态记 journal），因为旧评审不再适用于新归属——与 Anchorlaw 的 proof applicability 同源。

### 落盘布局

```
<project>/.artifacts/
├── target-modules.yaml        # 模块地图：revision + 每模块边界证据/provides/requires/历史
├── target-modules.state.json  # 契约守卫读取的机器态（脚本生成，禁止手改）
├── index.yaml                 # 每条带 target_module / module_revision
├── modules/<id>/              # 产物：classes/ functions/ xrefs/ conclusions/
│   └── reviews/<rev>.md       # judge 对该模块该修订的审查记录（G8 依据）
├── unassigned/                # 未分配桶（一等公民）
├── _migrations/<rev>/         # plan.json + journal.json + backup/（修正可审计、可回滚）
└── _audit/guard.jsonl         # 契约守卫的拒绝/绕过审计
```

代码落 `work/<id>/`（`config.code_root` 可配，空白工作区首次启动提示设置）；知识落 `knowledge/discovered/modules/<id>/`，跨模块经验进 `shared/`（`modules: [a,b]` 回指，不复制两份）。

### 工作流

1. **`derive`**：从 `package.json` workspaces / `Cargo.toml` workspace / `pom.xml` modules / `--hints` 文件推导模块，生成地图、目录与索引。
2. **产物写 `modules/<id>/`**，同步 `index.yaml`（`target_module` + `module_revision`）。
3. **`verify`**：跑 G1-G9；红了按提示修（遗留平铺目录用 `plan adopt-legacy` → `apply` 迁入 `unassigned/`）。
4. **judge 审模块**：scope = `module:<id>@<rev>`，产出 `reviews/<rev>.md`；`candidate` 必须有它（G8 / 守卫 R3）。
5. **修正**：边界/归属错 → `plan`（reassign / split / merge / rename / demote / quarantine）→ `apply`（事务：备份 + journal，失败逆序回滚）。
6. **`repair`**：从磁盘重建 index/state（守卫/旁路改动后的兜底）。

### 门禁 G1-G9（fail-closed）

| 门禁 | 判定 |
|---|---|
| G1 | 归属唯一、无跨模块重复内容 |
| G2 | 每个 active 模块至少有 1 条边界证据（禁止拍脑袋模块） |
| G3 | 未分配计数（地图 vs 磁盘）一致 |
| G4 | 索引条目 `module_revision` 与地图一致 |
| G5 | 无孤儿模块目录；retired 模块不得持有产物 |
| G6 | `provides` 全局唯一、`requires` 可解析 |
| G7 | 每个已应用修订都有 `plan.json` + `journal.json` |
| G8 | `candidate/confirmed` 模块必须有当前修订的 `reviews/<rev>.md` |
| G9 | 不得有 `modules/`、`unassigned/` 之外的散落产物 |

### 契约守卫（动作前拒绝，DSH `fs-observation-policy` 同款）

守卫在 `write`/`edit` 执行前判定，拒绝时给**一行可执行恢复**（稳定错误码）：

| 规则 | 触发 | 错误码 |
|---|---|---|
| R1 | 写入未声明的模块目录 | `REF_MODULE_UNDECLARED` → `ref_modules derive` 或写 `unassigned/` |
| R3 | 无当前修订评审就写 `status: candidate/confirmed` | `REF_REVIEW_MISSING` → 先派 `core-judge`（scope=module:<id>） |
| R5 | 知识条目缺 `signature/verdict/lesson/status` | `REF_KB_FRONTMATTER` → 补齐 front-matter |

自救：`REF_GUARD=off`（守卫空转，**每次绕过写审计**）；绕过期间的越界写入由 G1-G9 在下次运行时发现，`repair` 修复。守卫只覆盖工具调用，`pwsh` 直写属于已知旁路——不假装全覆盖。

### judge 的边界

**judge 审模块，不审全局**：大型工程的全局不可审，judge 只审一个模块（该模块产物 + 义务状态 + 门禁结果），产出 `reviews/<rev>.md`；全局只有 G8 做机械覆盖检查。**模块大到一次审不完 → 拆模块**，粒度由此可判。跨模块的横切行为建 `integration-<feature>` 模块单独审，而不是扩大 judge 视野。

### 命令速查

```powershell
python scripts/target_modules.py <project> derive [--hints modules.yaml]
python scripts/target_modules.py <project> status [--json]
python scripts/target_modules.py <project> verify [--json]          # G1-G9
python scripts/target_modules.py <project> plan reassign --from A --to B --files f.yaml
python scripts/target_modules.py <project> apply <plan.json>        # 失败自动回滚
python scripts/target_modules.py <project> repair
```

**验证状态**：fixture 测试全过（G1/G5/G6/G8/G9 逐条反证、迁移回滚、守卫 R1/R3/R5、`REF_GUARD=off` 审计）；**真实大工程尚未试跑**——spec §9 标 `CONJECTURE`，推导准确率待实战记录。

## 技能清单（17 个，kebab 名，DSH 加载用右列）

| 模块 | 技能（kebab） | 职责 |
|------|--------------|------|
| core | `core-plan` / `core-artifact` / `core-knowledge` / `core-version` / `core-fanout` / `core-worker` / `core-judge` | 架构设计 / 产物落盘 / 知识库 / 版本管理 / fan-out / 分析角色 / 审查角色 |
| re-binary | `re-lift` / `re-classify` / `re-trace` / `re-scout` | 高精度还原 / 类结构 / 动态 trace / 只读勘探 |
| re-code | `recode-deobfuscate` / `recode-classmap` / `recode-behavior` / `recode-scout` | 反混淆映射 / 类层次 / 行为验证 / 只读勘探 |
| swe | `swe-guide` | 编程入口（→ Anchorlaw，纯引用） |
| DSH-only | `ref-maintain` | DSH 适配层维护 |

## 与 Anchorlaw 的关系（纯引用式安装，零复制）

| 依赖层 | 方式 |
|--------|------|
| 协议 | spec §3 引用条款（单一事实源，升级核对见同步契约） |
| 技能 | `swe-guide` 路由引用 `anchor-*`（由 Anchorlaw 宿主 install.ps1 装到用户级全局，RE 零复制） |
| 工具 | `anchorlaw_*`（Anchorlaw 插件提供，RE 引用） |
| CLI | `anchorlaw` / `anchorlaw-scanner`（pip 包，Anchorlaw 侧装） |

## 归档说明

- **Reasonix 宿主格式**（dot 名技能、`.reasonix/skills/` 部署、`install.py`/`validate_manifest.py`）自 2026-08-21 停止维护，归档至 `archive/reasonix/`（含 RESTORE.md + restore-reasonix.ps1，Fork 用户可一键恢复自行迭代）。
- 框架核心（`spec/`、`templates/`、`knowledge-builtin/`、`scripts/merge_index.py`）保留，DSH 技能正文引用它们。

## 更新记录

| 版本 | 日期 | 内容 |
|------|------|------|
| v2.12 | 2026-10-24 | **目标模块化 P1（按程序自身的模块管理产物/代码/知识）**：新增 spec **§5.7** + `scripts/target_modules.py`（`derive` 从构建文件/hints 推导模块 → `verify` G1-G9 → `plan`/`apply` 事务修正 → `repair`）+ **契约守卫**（`ctx.tools.guard`，deny-only，R1 未声明模块 / R3 无评审 candidate / R5 缺 front-matter；`REF_GUARD=off` 自救并审计到 `_audit/guard.jsonl`）。**核心机制**：产物落 `.artifacts/modules/<id>/`、未分配桶 `unassigned/` 一等公民、`index.yaml` 增 `target_module`/`module_revision`；修正走 `_migrations/<rev>/{plan,journal,backup}`，失败按 journal 逆序**回滚**；迁移使 `candidate|confirmed` 回 `draft`（评审绑定模块+修订，journal 记原状态）；规范变更走 revision + 历史保留。**无人化**：自评估推进（候选→对抗检验→沙箱模拟→选择→apply→决策日志），只在 B1-B4 彻底阻塞时给人一页摘要；**judge 审模块不审全局**（scope=`module:<id>@<rev>`，产 `reviews/<rev>.md`，模块超一次审查带宽即拆）。**技能增量**：core-plan（Phase 0 模块分解 + judge 预置）、core-artifact（目录/索引/修正/守卫）、core-knowledge（`modules/<id>/` + `shared/` 分区）、core-judge（模块级 scope 与评审记录）。**验证**：`tests/test_target_modules.py`（derive/G1-G9 反证/adopt-legacy/reassign/回滚/repair）+ `tests/test_contract_guard.mjs`（R1/R3/R5/审计/bypass），接入 selfcheck **第 7 段**（六段 → 七段）；全部通过。**未验证**：真实大工程上的推导准确率（spec §9 标 CONJECTURE）。 |
| v2.11 | 2026-10-24 | **DSH 0.2.1-rc.3 删除 `./list-agents` 子路径（行门禁在维护时拦下）**：上游 `4df09d37d5`（"register shared control tools together"；升级指南 `docs/upgrade-guide/v0.2.1-rc.1/subagent-control-tools/guide.md` §Migration 3）把 `send_message` / `interrupt_agent` / `list_agents` 一起注册进 `@deepseek-ai/dsh-tool-subagent-control` 的**主入口**，独立的 `./list-agents` 子路径导出被删除。本 bundle 的 `tool-subagent-list-agents` 行因此解析为空（`ERR_PACKAGE_PATH_NOT_EXPORTED`）→ 新会话的 preset 挂载会失败；**自检第 5 段（行门禁）在维护时即变红**（28 行 → 1 行不可解析），不再是"开新会话才发现"。**修复**：删该行；`list_agents` 仍由 `tool-subagent-control` 行提供——与官方 standard preset 一致（上游同期删掉了同一行；控制行现在禁用会同时禁用三个工具，隐藏单个工具请用工具限制）。**时间线核实**：rc.2（v2.10 基线 `687f282e`）该导出**仍在**（`git show 687f282e:packages/subagent/tool-subagent-control/package.json` 含 `./list-agents`），移除提交在 rc.2 之后才合入 → 属**新的上游漂移**，不是 v2.10 漏检。**未采纳（待人类拍板）**：官方 standard preset 同期把 spawn 行由 `modelSelectionSettings: true` 改为 `modelSelection: true` + `modelDiscovery: true`；本 bundle 与 Anchorlaw 均未启用 → re-framework 会话暂无 `list_subagent_models` 与子代理模型选择，属**能力面差异**（非故障）。**实测**：行门禁 27 行 0 不可解析；模板变量门禁绿；六段自检全绿；Anchorlaw v0.25（`ccd9105`）做同一修复（27 行）。 |
| v2.10 | 2026-10-17 | **DSH 0.2.x 适配收尾 + Anchorlaw 引用 v0.24**：(1) 删 4 处 `backgroundMode`——`@deepseek-ai/dsh-tool-subagent` 已移除该键，Schemastery 静默丢弃、**从未生效**；行门禁看不见这类"配置键已死"（与 `{{cwd}}` 同族）。(2) spawn 行补 `agentPreset: re-framework` + `allowedAgentPresets: [re-framework]`——0.2.x 用 preset 组合子代理，**两者必须同时给**，否则抛错；**fork 行不加**（`capabilities.agentPreset: false`，加了抛 "independent agent preset"）。(3) `engines.dsh: >=0.2.0 <0.3.0`（新版按 engines 独自判定兼容性）。(4) 子路径显示元数据：补 `./plugin/locale/*.json` + `./plugin/icon`（0.2.0 起不再读 `<subpath>/package.json` 取显示文本）。(5) **Anchorlaw v0.23 → v0.24**：纯宿主适配，§5/§9/§12/§13/§14/§15/§16 **逐节 diff 全为 0**，只升引用版本、无语义迁移。**实测**：`dsh --profile web --help` exit 0 零告警；重复 `install.ps1` exit 0（`already-installed` 只影响 Host API/agent 工具，不影响 CLI `add`）；六段自检全绿。**未验证**：新会话端到端 resume（需重启 Host） |
| v2.9 | 2026-10-10 | **DSH 0.2.x 移除 `cwd` 提示词变量 + 模板变量门禁**：上游按升级指南 `docs/upgrade-guide/v0.2.1-alpha.1/working-directory/guide.md` §Migration 1 删除循环内建的 `{{cwd}}` 提示词变量（提交 `79bd3d8da7` 删掉 `packages/core/agent-loop/src/index.ts` 的 `variable('cwd', …)` 行），工作目录改由 `dsh-working-directory` 的 `working-directory:current` **运行时上下文**提供。**事故**：本 bundle 的 persona prefix 仍写 `Your working directory is {{cwd}}.`，而 persona 模板**渲染期严格解析** → re-framework preset 的会话在组装期（模型请求之前）直接抛 `unknown prompt variable "{{cwd}}" in section "deployment:persona-prefix"; registered variables: provider, model`。**根因（门禁盲区）**：第 5 段行门禁只证明「行能解析、包能挂载」，看不见**模板变量已死**——用真实 harness 的 `renderPrompt()` 复现证实（旧文本抛错、新文本通过）。**修复**：① `cordis.patch.yml` persona prefix 去掉 `{{cwd}}` 子句（改为指向运行时上下文，模型仍拿得到工作目录）；② 新增 fail-closed 门禁 `tests/audit_prompt_variables.mjs`（镜像上游 `interpolate()` 扫描规则；注册集合由扫描 harness 的 `systemPrompt.variable('<name>')` 注册点得出，跳过 tests 防白名单污染；**扫不到注册点即 exit 2 = FAIL**），接入 `selfcheck.ps1` 第 [6] 项，可用 `DSH_SKIP_PROMPT_VAR_AUDIT=1` 显式接受缺口；**实测反证**：把 `{{cwd}}` 放回夹具即变红（同时报畸形变量名），错 checkout 走 exit 2。自检 五段 → 六段 |
| v2.8 | 2026-09-23 | **preset 载体迁移（目录 → bundle patch）+ 门禁盲区修复**：上游 DSH 0.1.7 把 agent preset 的载体由 `$DSH_HOME/.agent-presets/<id>/` 目录换成 **bundle patch 里的 `@deepseek-ai/dsh-agent-preset` 声明行**（旧目录无代码读取）。**事故**：`re-framework` preset 在 0.1.7 下不存在 → 会话 resume 报 `Unknown agent preset`。**根因（门禁盲区，已复现证实）**：行门禁 `rowNames()` 只走 `Array.isArray(row.config)`，既不认识 bundle 载体、也不走 `config.plugins[]` → **门禁全绿而运行时报错**（用旧门禁跑新载体：`0 reference(s)` 却判 "All preset rows resolvable"）。**修复**：① 门禁补**两种载体 + 三条递归路径**（`insert[]`/`config[]`/`config.plugins[]`，注释标"勿删"），默认目标改为**生效载体**、载体缺失即 FAIL，新增 **bundle 自引用识别**（exports 校验**且**要求目标文件存在）；**实测 0 → 28 行**。② `install.ps1` 重写为「校验 bundle → 先跑行门禁 → 技能装用户级 → `dsh plugin --profile <p> add <dsh 目录>`」；修掉一个 PowerShell 陷阱（`-Profile` 与 `foreach ($profile …)` **大小写不敏感同名**被覆盖 → 改名 `-ProfileName`）。③ `selfcheck.ps1` 第 3 段由"对账**死目录**"改为**检 bundle 是否被 profile 选中** + 用户级 sha256 对账（manifest v2）。④ 删除 `dsh/preset/` 与死目录（经人类确认）。⑤ `dsh/AGENTS.md` 事实源改为 `cordis.patch.yml`（报告 §5.1 指出的误导点，该文件每会话必读） |
| v2.7 | 2026-09-23 | **Anchorlaw 引用 v0.22 → v0.23 升级核对（纯引用版本号，协议核心零变化）**：v0.23 = **DSH 0.1.7 preset 载体迁移**，属 §16 宿主适配范围。**独立复核协议自述**（*"the protocol core is unchanged"*）：§5/§9/§12/§13/§14/§15/§16 **逐节 diff 全为 0**；标题集合 92=92；**全文真实差异共 5 处**（LCS 比对实测）：版本头发布说明 +20 行 / v0.18 条目 supersession 注记 +5 行 / v0.18 DSH changelog 表行 1 行 / §8 Maturity 表行 1 行 / §11 audit 表行 1 行——后三处均为**表格行文本更新，非条款正文**。**方法论坑**：逐节 diff 的归一化必须**同时**把新旧两个版本号归到同一占位符，否则条款标题里字面的旧版本号会伪装成差异。**对宿主的实质影响**：preset 载体由目录改为 **bundle patch 声明行**、`config.plugins[]` 行不做路径锚定（须裸包名子路径）、preset 子树 `baseUrl` 是 **profile 目录**、anchor-* 技能改用户级全局、**项目级安装模式被撤回**。→ 本框架**不依赖**项目级安装，故该撤回不影响既有安装语义；载体迁移影响 dsh 适配层（已临时修复，**正式升级待办**见 `.investigations/dsh-preset-bundle-migration/报告.md` §6）。**引用升级 34 处**（33 处已跟踪 + 1 处生效载体），含**生效载体 `cordis.patch.yml` 的 persona**（该文件当时未被 git 跟踪，`git grep` 扫不到——枚举时必须补 `git status`） |
| v2.6 | 2026-09-17 | **Anchorlaw v0.22 实质条款升级 + CoreSwap 论文研究吸收**：(1) 引用 v0.21 → **v0.22**——v0.22 新增**五条款**（§9 +37 行 / §14 +34 行 / §15 +75 行），**本次是实质升级非纯版本号**；五条款全部落地（§9.8 副作用边界与逆登记 → spec §5.6 + core-artifact；§15.4 判据前置集 → spec §4.5 + core-judge；§9.7.1 等价档位 → re-lift；§15.4 PI-1 halt 终态性 → spec §4.5 + core-fanout 汇聚完整性；§14.7 引用完整性 → spec §3 检查动作）。(2) **安装产物具备身份**——`install.ps1` 写 sha256 manifest，`selfcheck.ps1` 第 3 段从「数目录」升级为**内容对账**（MISSING/DRIFT/ORPHAN），并补两个既有真空洞：用户级 orphan 残留清理（限本框架命名空间，**绝不误删 `anchor-*`**）+ profile patch 改写前备份。(3) 新增触发点产物门 `audit_trigger_coverage.mjs`（**只判"触发后有无产物"，不判"该不该触发"**；实测误报率 **1.1%**）。(4) 交接声明证据等级（numeric 可继承 / qualitative 须回原始日志 / anchor 须属主自核），**限定语义性交接**避免过度工程 |
| v2.5 | 2026-09-17 | **Anchorlaw 引用 v0.20 → v0.21 升级核对**：v0.21 为**宿主适配层进展登记**（preset 能力面对齐 + fail-closed preset 行解析门禁），**协议核心逐字节未变**——比对方法：`protocol-v0.20.md` 与 `protocol-v0.21.md` 正文（changelog 之前）归一化版本号后逐行 diff，唯一差异为版本头部发布说明 16 行；§5/§9/§12/§13/§14/§15/§16 逐节零差异，§11/§16 零差异，**§8 Maturity 表行数不变**（仅 Host Integration 行文本补 v0.21 说明）。**纯引用版本号升级，无语义迁移**。详见 spec §3 新增核对行 + `dsh/SYNC.md` |
| v2.4 | 2026-09-09 | **上游 DSH 漂移修复 + 能力面对齐**：(1) 上游把 `@deepseek-ai/dsh-workflow-worker-thread` 改名为 `@deepseek-ai/dsh-workflow-ptc`（旧目录已不再是包）——preset 仍引用旧名，导致 **preset 挂载失败、会话无法创建/恢复**（`failed to mount`）；`id`+`name` 随上游改名，`config` 不变。(2) 能力面对齐官方 standard preset（31 行）：补 5 行——`command-goal`、`present`（启用）、`tool-ralph`、`tool-subagent-codex`、`tool-subagent-claude-code`（按上游默认 disabled，启用需在 Profile 装对应 Bundle）→ **ours 32 = official 31 + 本地 `re-framework-tools`，缺口 0**。(3) 新增 fail-closed 门禁 `tests/audit_preset_rows.mjs` 并接入 `selfcheck.ps1` 第 [5] 项——preset 任一行不可解析即自检变红，不再等用户 resume 报错（2026-09-09 漂移事故，`.investigations/dsh-upstream-drift-20260909/报告.md`）。(4) 同日第二轮：**preset 行 specifier 解析语义对齐上游**（`classifyRowSpecifier()` 四分类 + 包名自 harness base 向上走查；错基准 fail-closed） |
| v2.3 | 2026-08-21 | **知识库压实机制**（吸收 CoreSwap knowledge-compaction 提案，借鉴 DSH compaction）：条目结构化 front-matter（id/status/supersedes/superseded_by/signature/verdict/lesson，对齐 Anchorlaw v0.20 §15.4 supersession 链）、派生视图禁止手维护（`gen_cheatsheet.py` 机械生成）、压实 pass（每 10 条或课题结案，簇合并为原则 + consolidated 原文保留）；**§4.5 第五条强制触发点**（交接结论验证 ≤1 轮 + 闭合点三态切换建议 MUST + 污染信号触发分离落盘，对齐 v0.20 §16.3）；Anchorlaw 引用 v0.19→v0.20 |
| v2.2 | 2026-08-21 | **DSH 唯一宿主迁移**：Reasonix 归档（`archive/reasonix/`）、`dsh/skills/` 变单一事实源、工具 5→3（ref_manifest_validate/ref_install 随 Reasonix 退役）、根 AGENTS.md 重写 DSH-first、spec 标注归档、安装简化（单一 install.ps1）、对 Anchorlaw 纯引用式安装（零复制）；知识记录价值门（P1/P2/P3）；Anchorlaw 引用 v0.18→v0.19（验证协议定位澄清） |
| v2.1 | 2026-08-14~15 | DSH 适配层（`dsh/` 子树）、技能用户级全局、工具 preset-only、Anchorlaw 引用 v0.15→v0.17→v0.18、SKILL-MAP DSH 探测器、错误账本强化 |
| v2.0 | 2026-08 | 模块化重构（Reasonix 时代，已归档） |
| v1.0 | 2026-06 | 单文件 42KB CLAUDE.md（BitWarden 方法论，已归档） |
