# SYNC.md — DSH 适配层与 Reasonix 侧的同步溯源戳

> 本文件记录 `dsh/` 子树与框架规范正文（`../skills/`、`../spec/`）的同步状态。
> 采用框架自身的可追溯纪律（spec §1.3）：每一次同步都记录来源、时间与差异，可审计。

## 初始同步（2026-08-14）

- **来源**：`../skills/*/SKILL.md`（16 个 Reasonix 规范技能）；基线 = 工作区当前状态（HEAD `b00f033` + 3 个未提交改动文件：`skills/core.knowledge/SKILL.md`、`spec/engineering-framework-v1.md`、`memory/RE-multi-agent-framework.md`——未提交改动属于人类工作区，作为同步基线如实记录，未整理未提交）
- **动作**：正文 1:1 复制（`dsh/scripts/sync_skills.py` 生成）→ frontmatter 适配（dot → kebab-case 改名、新增 `whenToUse`、移除 Reasonix 专有 `kind`/`runAs`/`layer`/`execution` 字段）
- **正文漂移**：0（生成器逐字节复制 + `tests/test_manifest.py` 以正文级比对守护，允许 CRLF→LF 归一化差异）
- **新增**：`ref-maintain`（DSH-only 维护技能，无上游对应，测试豁免漂移检查）
- **适配映射**（frontmatter 变更汇总）：

| 技能 | frontmatter 变更 |
|------|------------------|
| 全部 16 个 | `name` 由 dot 改 kebab（`core.plan` → `core-plan`）；新增 `whenToUse`（模块触发表触发场景）；移除 `kind`/`runAs`/`layer`/`execution`（层/执行信息保留在正文引用块） |
| core-worker / core-judge / re-scout / recode-scout | `whenToUse` 注明 DSH 中经 subagent 工具隔离执行（对应 spec §4.1-4.3 角色隔离） |

## 同步规则（维护者必读）

1. **技能正文改动**：只允许发生在 `../skills/`（Reasonix 规范正文）。改后重跑 `python dsh/scripts/sync_skills.py`，再确认 `python dsh/tests/test_manifest.py` 通过，然后更新本文件差异记录。
2. **frontmatter 适配改动**：改 `dsh/scripts/sync_skills.py` 的 ADAPT 映射表（dash-name / whenToUse），重跑生成器，并在此文件登记变更。
3. **框架语义更新**：先改 `../spec/engineering-framework-v1.md`，再同步技能正文与 DSH 适配；Anchorlaw 引用版本核对用 `git grep 'v0\.[0-9]'`（当前基线 v0.17）。
4. **新增技能**：在 `sync_skills.py` ADAPT 与 `tests/test_manifest.py` EXPECTED 中登记；DSH-only 技能登记进 DSH_ONLY。

## 变更日志

| 日期 | 来源 | 内容 | 正文漂移 |
|------|------|------|----------|
| 2026-08-14 | 工作区 HEAD b00f033 + 3 未提交文件（初始同步） | 16 技能 DSH 化移植（kebab 改名 + whenToUse）+ 新增 ref-maintain + 5 工具 + re-framework preset | 0 |
| 2026-08-14 | Anchorlaw v0.15 → v0.17 升级核对（协议仓库 spec changelog） | 基线版本升级：AGENTS.md / spec §3 / README / memory / templates / 技能正文（swe.guide / re.lift）v0.15 → v0.17；spec §3 新增 v0.16/v0.17 条款核对（Go/Java 注册、Rust 不支持、parse-error、注释类语言降级、P7-P10）+ 同源双写（Reasonix/Go audit 回流）；swe-guide CLI 注明注释类语言仅注解提取 | 0（生成器同步） |
| 2026-08-14 | Anchorlaw HEAD 4931a1c 复核 | 协议仍 v0.17（无新版本，基线不变）；HEAD 新提交 = dsh project-level install mode（`-Project`，Reasonix 式项目级部署）+ anchor.maintain 正文修正（移除易变测试计数，不在本框架路由表）——均不影响引用条款 | 0 |
| 2026-08-14 | 可见性设计修订（用户需求） | 技能：preset-only → **用户级全局**（~/.dsh/skills/ref-*）+ preset 内嵌双路径；工具分层：项目侧（status/init/merge_index/install）用户级全局，维护工具（manifest_validate）仅 preset；插件支持 config.tools 子集注册（两处不重叠） | 0 |
| 2026-08-15 | 全局挂载修复（2026-08-13 Anchorlaw 事故复盘落地） | **挂载位置/形态修正**：`~/.dsh/cordis.patch.yml`（宿主不读）→ `<dshHome>/profiles/<profile>/cordis.patch.yml`（唯一用户补丁层，insert 形态）；插件 `~/.dsh/plugins/` → `<profile>/plugins/re-framework/`；install.ps1 增加旧错误挂载清理 + profile 自动扫描（-Profile 可指定）+ 挂载前 schema 门禁（tests/check_plugin_schema.mjs）；**工具 parameters 扁平 → 编译后 JSON Schema**（5 个工具，扁平 spec 会让所有会话崩）；selfcheck 增第 5 项 schema 校验；preset 注释/persona 硬编码路径与 v0.15 残留清理 | 0 |
