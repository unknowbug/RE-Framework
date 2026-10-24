# AGENTS.md — RE-Framework dsh/ 子树（DSH 宿主适配层）

> 本目录（`dsh/`）是 **RE-Framework 仓库的 DSH 宿主适配层**：框架协议（`spec/`）、产物模板（`templates/`）、预置知识库（`knowledge-builtin/`）与 DSH 生态适配（DSH 技能、工具插件、agent preset、维护脚本）共存于同一仓库——**单一仓库，DSH 唯一维护宿主**；Reasonix 宿主格式已归档（`archive/reasonix/`）。
> 维护者：DSH agent（RE-Framework maintainer）。每次会话开始必读本文件。

## 〇、开始工作前（每个 session 必做）

1. 确认仓库状态：仓库根即框架协议/方法论文档事实源，本目录（`dsh/`）即 DSH 适配事实源——**单一仓库，无第二份框架副本**；`archive/reasonix/` 为只读归档（不再同步）。
2. 跑自检确认基线全绿：`pwsh dsh/scripts/selfcheck.ps1`（七段：工具链 / 技能 manifest / 安装产物 / 插件 schema / preset 行解析门禁 / preset 模板变量门禁 / 目标模块 + 守卫 fixture 门禁）。
3. 若改动涉及技能正文：**直接改本目录 `skills/`**（单一事实源，无上游派生），`tests/test_manifest.py` 守护 manifest 形态。

## 一、本目录定位（一句话）

**RE-Framework 的 DSH（DeepSeek Harness）宿主适配层**——`dsh/skills/` 是技能**单一事实源**（kebab-case + whenToUse）；本目录还持有模型工具插件、agent preset 与维护脚本。

## 二、目录结构（事实源 vs 安装产物）

| 路径 | 内容 | 角色 |
|------|------|------|
| `skills/` | 17 个 ref-* 技能（kebab-case + whenToUse，**单一事实源**，直接维护） | **事实源**（改这里） |
| `plugins/re-framework-tools.js` | 3 个模型工具插件（status/merge-index/init；manifest_validate/install 随 Reasonix 归档退役）+ **契约守卫**（R1/R3/R5，deny-only，`REF_GUARD=off` 自救并审计） | **事实源**（改这里） |
| **`cordis.patch.yml`** | **agent preset 声明（ACTIVE carrier，DSH >= 0.1.7）**——preset 是 bundle patch 里的一条 `@deepseek-ai/dsh-agent-preset` 声明行；preset 的全部行在 `config.plugins[]` 内 | **事实源**（改这里） |
| `package.json` | bundle 身份（包名 `@dsh-external/dsh-re-framework` + `dsh.bundle.patch` + `exports["./plugin"]` + `engines.dsh`）；安装步骤以依赖形式把它装进 profile | **事实源**（改这里） |
| `locale/plugin/*.json` | 子路径插件的界面显示文本（`meta.title` / `meta.description`）——0.2.0 起不再读 `<subpath>/package.json` | **事实源**（改这里） |
| `assets/plugin.svg` | 子路径插件的图标（导出为 `./plugin/icon`） | **事实源**（改这里） |
| ~~`preset/`~~ | **已于 2026-09-23 删除**——DSH 0.1.7 起 preset 载体换成 bundle patch，该目录**无任何代码读取**（上游原话 "Nothing reads that directory any more"）。旧分支/旧文档若提到它，那是迁移前形态 | —（已不存在） |
| `scripts/install.ps1` | 安装/同步到 DSH 运行时（校验 bundle → 跑行门禁 → 技能装用户级 → `dsh plugin --profile <p> add <bundle>`） | 维护工具 |
| `scripts/selfcheck.ps1` | 七段自检（工具链 / 技能 manifest / **bundle 选中 + 产物对账** / 插件 schema / preset 行解析门禁 / preset 模板变量门禁 / 目标模块 + 守卫 fixture 门禁） | 维护工具 |
| `scripts/target_modules.py` | **目标模块管理**（spec §5.7）：`derive`（构建文件/hints 推导）/ `verify`（G1-G9）/ `plan`→`apply`（事务 + 回滚）/ `repair`；产出 `target-modules.yaml` + 守卫用 `state.json` + `_migrations/<rev>/` | 维护工具 |
| `tests/test_manifest.py` | 技能 manifest 校验（DSH 命名 + frontmatter + 技能集 + 交叉引用） | 维护测试 |
| `tests/check_plugin_schema.mjs` | 插件工具 schema 门禁（parameters 必须编译后 JSON Schema；2026-08-13 事故） | 维护测试 |
| `tests/audit_preset_rows.mjs` | preset 行解析性门禁（fail-closed）——镜像上游 `classifyRowSpecifier()` 四分类，并覆盖**两种载体 + 三条递归路径**（`insert[]` / `config[]` / `config.plugins[]`），缺一即漏检。两次事故：2026-09-09 上游改名（`dsh-workflow-worker-thread` → `dsh-workflow-ptc`）；**2026-09-23 载体迁移**（旧门禁不认识 bundle patch、不走 `config.plugins[]`，于是**全绿而 resume 报 `Unknown agent preset`**——递归 1/3 即该事故的修复本体）。另含本 bundle 自引用识别（裸包名子路径 → 用本仓库 `package.json` 的 exports 校验**且**要求目标文件存在） | 维护测试 |
| `tests/audit_prompt_variables.mjs` | preset **模板变量**门禁（fail-closed）——镜像上游 `interpolate()` 的扫描规则，校验生效载体里每个 `{{name}}` 都是 harness **当前注册**的提示词变量（注册集合由扫描 harness 的 `systemPrompt.variable('<name>')` 注册点得出，跳过 tests 以免白名单被测试变量污染）。**2026-10-10 事故**：DSH 0.2.x 移除内建 `cwd` 提示词变量（工作目录改走 `working-directory:current` 运行时上下文），persona prefix 里的 `{{cwd}}` 让 re-framework 会话在组装期直接抛错——行门禁看不见（行能解析、包能挂载，**变量却已死**） | 维护测试 |
| `tests/test_target_modules.py` | 目标模块 fixture 测试：derive → G1-G9 逐条反证 → adopt-legacy → reassign（候选降级）→ 失败 apply 回滚 → repair | 维护测试 |
| `tests/test_contract_guard.mjs` | 契约守卫测试（fake Cordis ctx）：R1 未声明模块 / R3 无评审 candidate / R5 缺 front-matter / 审计 / `REF_GUARD=off` 自救 | 维护测试 |
| `SYNC.md` | 溯源戳（上次同步的上游 commit + 时间 + 差异） | 溯源记录 |
| `SKILL-MAP.md` | **DSH 探测器 + 调用接口速查**（kebab 名路由表 + 强初始化/Phase 0-3 流程驱动 + dot→kebab 映射 + ref_* 工具/脚本对照；根 AGENTS.md 的 DSH 指引行指向这里，DSH 会话先读） | 接口桥接 + 流程驱动文档 |
| **安装产物（勿手改）** | | |
| `<profile>/package.json` 的 `dsh.profile.bundles` | **preset 的存在性由这里决定**（DSH >= 0.1.7）：bundle 未进该有序列表 = preset 不存在 | `dsh plugin --profile <p> add <dsh 目录>`（install.ps1 调用） |
| `~/.dsh/skills/ref-*` | **用户级全局技能**（任何 preset/工作目录的会话按需加载；含 `.re-framework-manifest.yaml`） | install.ps1 同步 |
| ~~`~/.dsh/.agent-presets/re-framework/`~~ | **已死目录**——DSH 0.1.7 起没有任何代码读它（本机 `packages/ apps/ vendor/` 下 grep `.agent-presets` 零代码命中）；install.ps1 不再写入 | ⚠️ 遗留物，可删 |

**载体迁移（2026-09-23，DSH 0.1.7）**：preset 载体由「目录 `$DSH_HOME/.agent-presets/<id>/`」改为「bundle patch 的 `@deepseek-ai/dsh-agent-preset` 声明行」。三处语义差异：① `config.plugins[]` 内的行**不做路径锚定**，本地插件须用**裸包名子路径**（`@dsh-external/dsh-re-framework/plugin`）；② preset 子树的 `baseUrl` 是 **profile 目录**而非 bundle，技能根须经已安装包解析（`createRequire(baseUrl).resolve('<pkg>/package.json')`）；③ 装/选中走 `dsh plugin --profile <p> add <dsh 目录>`。

**安装产物具备身份（2026-09-17 起）**：`install.ps1` 生成 `.re-framework-manifest.yaml`（`source_commit` + `bundle_name` + `selected_in_profiles` + 每件 `sha256`），`selfcheck.ps1` 第 3 段据此**内容对账**（MISSING / DRIFT / ORPHAN 三态，非零退出），并**另检 bundle 是否被某 profile 选中**。**计数检查降为二级断言**——只数目录证明不了内容一致，那是与 preset 行门禁同类的"静默变绿"失败模式。同时 `install.ps1` 清理**本框架命名空间内**的上游已删技能（**绝不触碰 `anchor-*` 等其他框架技能**，`~/.dsh/skills` 是多框架共享树）；profile patch 改写前先备份（失败即 restore）。

**同步纪律（核心铁律）**：所有修改只改本目录事实源，然后跑 `scripts/install.ps1` 重装——安装产物一律视为可再生，禁止手改。技能正文直接在本目录 `skills/` 改（单一事实源），`tests/test_manifest.py` 守护 manifest 形态与交叉引用。

## 三、维护铁律（对应 ref-maintain，DSH 版）

1. **自检全绿**：任何改动必须 `dsh/scripts/selfcheck.ps1` 全绿（七段：工具链 / 技能 manifest / 安装产物 / 插件 schema / preset 行解析门禁 / preset 模板变量门禁 / 目标模块 + 守卫 fixture 门禁）。
2. **单一事实源**：`dsh/skills/` 是技能唯一事实源（直接维护；Reasonix 归档 `archive/reasonix/` 不参与同步）。
3. **新能力必须配验证**：新增技能/工具要能通过自检或实测证明，否则标注 Unverified。
4. **命名纪律**：DSH 技能名必须 kebab-case（`core-plan` 而非 `core.plan`）；插件工具名 `ref_*`。
5. **插件持久化纪律**：动态插件（cordis_define 定义）只在当前进程存活——**持久能力必须落成 `plugins/` 文件 + preset 行**，禁止把维护性能力留在动态插件里。
6. **preset 纪律（2026-09-23 载体迁移后）**：preset 的**存在性 = bundle 被某 profile 的 `dsh.profile.bundles` 选中**（由 `install.ps1` 调 `dsh plugin --profile <p> add <dsh 目录>` 完成；DSH >= 0.1.7）。旧的 `~/.dsh/.agent-presets/re-framework/` 目录**已死**——没有任何代码读它，本脚本不再写入，**不要再把它当作"装好了"的证据**。shipped preset（harness 安装目录）一律只读，改动只能以复制派生。
7. **可见性纪律（v2.1 修订，2026-08-15 用户拍板：无 global 工具组）**：技能走**双路径**——① preset 内的 `skill-filesystem customSkillDirs` 从 **bundle 包内**解析 `skills/`（经 `createRequire(baseUrl).resolve('<pkg>/package.json')`，因 preset 子树 `baseUrl` 是 profile 目录）；② 用户级全局 `~/.dsh/skills/ref-*`（任何 preset/工作目录的会话按需加载）。**工具仅 re-framework preset**（3 个 ref_*：status/merge_index/init——manifest_validate/install 依赖的 Reasonix 脚本已随 2026-08-21 归档退役；其他会话用 pwsh 直接跑脚本：`python scripts/merge_index.py <project>`）；曾尝试的 profile patch global 挂载（`<profile>/cordis.patch.yml` insert 行）已**撤销**（2026-08-15），install.ps1 幂等清理；多框架共存靠前缀命名空间（ref-*/ref_* 与 anchor-*/anchorlaw_*）；**插件 schema 门禁**：install/selfcheck 必跑 tests/check_plugin_schema.mjs（parameters 必须编译后 JSON Schema，扁平 spec 投影给模型无顶层 type → 所有会话崩，2026-08-13 事故教训）。
8. **提交纪律**：提交前自检全绿；**不自动 git 提交**（仓库可能有未提交的人类改动，提交时机由人类决定）。

## 四、与框架核心及归档的关系（同一个仓库内）

- **仓库根（`../`）**：框架协议（`spec/engineering-framework-v1.md`）、产物模板（`templates/`）、预置知识库（`knowledge-builtin/`）、索引入口（根 `AGENTS.md`，DSH-first）、`scripts/merge_index.py`（ref_merge_index 工具依赖，保留）、`archive/reasonix/`（Reasonix 归档，只读）。
- **本目录（`dsh/`）**：DSH 生态适配层（DSH 技能单一事实源、插件、preset、维护脚本），入口为本文件。
- **一致性机制**：`tests/test_manifest.py` 守护 `dsh/skills/` 自身（命名/frontmatter/技能集/交叉引用）；`SYNC.md` 记录变更溯源；Reasonix 归档 `archive/reasonix/` 不参与任何同步。
- **边界**：不修改归档区 `archive/reasonix/`（恢复走其 RESTORE.md）；框架核心文件（`../spec/`、`../templates/`、`../knowledge-builtin/`、`../scripts/merge_index.py`）按需引用不复制。

## 五、re-framework preset 的人格承诺

使用 re-framework preset 的会话，agent 强制走框架纪律：强初始化（读知识库 → 架构设计待批准 → 预置子角色介入点）→ 任务类型探测器路由（re-binary / re-code / swe）→ Phase 0-3 工作流 → 执行强制链（scout/fan-out/judge/knowledge），`confirmed` 只能由人类授予。scout/worker/judge/fan-out 经 subagent 工具隔离执行（spec §4.5）。

## 六、会话工作目录说明

DSH 自动加载的是**工作区根的 `AGENTS.md`**（DSH-first 索引，2026-08-21 迁移后：MUST 先读 `dsh/SKILL-MAP.md` 再走标准流程）；`dsh/AGENTS.md`（本文件）只在操作涉及 `dsh/` 目录内文件时按目录加载。**DSH 环境维护本仓库时，以本文件为维护准则**（技能名/部署/触发表一律 kebab 名 DSH 形态；技能正文内的 dot 名是规范引用，按 `SKILL-MAP.md` §一 映射）。推荐：工作目录指向本仓库根（`E:\PYTHON\RE-Framework`）跑 re-framework preset 会话，或直接在本目录内工作以触发本文件加载。
