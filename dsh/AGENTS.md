# AGENTS.md — RE-Framework dsh/ 子树（DSH 宿主适配层）

> 本目录（`dsh/`）是 **RE-Framework 仓库的 DSH 宿主适配层**：框架协议（`spec/`）、产物模板（`templates/`）、预置知识库（`knowledge-builtin/`）与 DSH 生态适配（DSH 技能、工具插件、agent preset、维护脚本）共存于同一仓库——**单一仓库，DSH 唯一维护宿主**；Reasonix 宿主格式已归档（`archive/reasonix/`）。
> 维护者：DSH agent（RE-Framework maintainer）。每次会话开始必读本文件。

## 〇、开始工作前（每个 session 必做）

1. 确认仓库状态：仓库根即框架协议/方法论文档事实源，本目录（`dsh/`）即 DSH 适配事实源——**单一仓库，无第二份框架副本**；`archive/reasonix/` 为只读归档（不再同步）。
2. 跑自检确认基线全绿：`pwsh dsh/scripts/selfcheck.ps1`（四段：工具链 / 技能 manifest / 安装产物 / 插件 schema）。
3. 若改动涉及技能正文：**直接改本目录 `skills/`**（单一事实源，无上游派生），`tests/test_manifest.py` 守护 manifest 形态。

## 一、本目录定位（一句话）

**RE-Framework 的 DSH（DeepSeek Harness）宿主适配层**——`dsh/skills/` 是技能**单一事实源**（kebab-case + whenToUse）；本目录还持有模型工具插件、agent preset 与维护脚本。

## 二、目录结构（事实源 vs 安装产物）

| 路径 | 内容 | 角色 |
|------|------|------|
| `skills/` | 17 个 ref-* 技能（kebab-case + whenToUse，**单一事实源**，直接维护） | **事实源**（改这里） |
| `plugins/re-framework-tools.js` | 3 个模型工具插件（status/merge-index/init；manifest_validate/install 随 Reasonix 归档退役） | **事实源**（改这里） |
| `preset/agent.cordis.yml` | re-framework agent preset 组合 | **事实源**（改这里） |
| `preset/preset.yml` | preset 显示元数据 | 事实源 |
| `scripts/install.ps1` | 安装/同步到 DSH 运行时 | 维护工具 |
| `scripts/selfcheck.ps1` | 四段自检（工具链 / 技能 manifest / 安装产物 / 插件 schema） | 维护工具 |
| `tests/test_manifest.py` | 技能 manifest 校验（DSH 命名 + frontmatter + 技能集 + 交叉引用） | 维护测试 |
| `SYNC.md` | 溯源戳（上次同步的上游 commit + 时间 + 差异） | 溯源记录 |
| `SKILL-MAP.md` | **DSH 探测器 + 调用接口速查**（kebab 名路由表 + 强初始化/Phase 0-3 流程驱动 + dot→kebab 映射 + ref_* 工具/脚本对照；根 AGENTS.md 的 DSH 指引行指向这里，DSH 会话先读） | 接口桥接 + 流程驱动文档 |
| **安装产物（勿手改）** | | |
| `~/.dsh/.agent-presets/re-framework/` | 已安装 preset（组合 + plugins/ + skills/） | install.ps1 生成 |
| `~/.dsh/skills/ref-*` | **用户级全局技能**（任何 preset/工作目录的会话按需加载） | install.ps1 同步 |
| `~/.dsh/.agent-presets/re-framework/plugins/` | preset 内嵌工具插件（3 个 ref_*，仅 re-framework preset 会话） | install.ps1 复制 |

**同步纪律（核心铁律）**：所有修改只改本目录事实源，然后跑 `scripts/install.ps1` 重装——安装产物一律视为可再生，禁止手改。技能正文直接在本目录 `skills/` 改（单一事实源），`tests/test_manifest.py` 守护 manifest 形态与交叉引用。

## 三、维护铁律（对应 ref-maintain，DSH 版）

1. **自检全绿**：任何改动必须 `dsh/scripts/selfcheck.ps1` 全绿（四段：工具链 / 技能 manifest / 安装产物 / 插件 schema）。
2. **单一事实源**：`dsh/skills/` 是技能唯一事实源（直接维护；Reasonix 归档 `archive/reasonix/` 不参与同步）。
3. **新能力必须配验证**：新增技能/工具要能通过自检或实测证明，否则标注 Unverified。
4. **命名纪律**：DSH 技能名必须 kebab-case（`core-plan` 而非 `core.plan`）；插件工具名 `ref_*`。
5. **插件持久化纪律**：动态插件（cordis_define 定义）只在当前进程存活——**持久能力必须落成 `plugins/` 文件 + preset 行**，禁止把维护性能力留在动态插件里。
6. **preset 纪律**：`~/.dsh/.agent-presets/re-framework/` 是用户级 preset（由 install.ps1 生成，可再装）；shipped preset（harness 安装目录）一律只读，改动只能以复制派生。
7. **可见性纪律（v2.1 修订，2026-08-15 用户拍板：无 global 工具组）**：技能装**用户级全局**（`~/.dsh/skills/ref-*`）+ preset 内嵌双路径——任何项目会话可加载，不依赖选择 re-framework preset 或工作目录；**工具仅 re-framework preset**（3 个 ref_*：status/merge_index/init——manifest_validate/install 依赖的 Reasonix 脚本已随 2026-08-21 归档退役；其他会话用 pwsh 直接跑脚本：`python scripts/merge_index.py <project>`）；曾尝试的 profile patch global 挂载（`<profile>/cordis.patch.yml` insert 行）已**撤销**（2026-08-15），install.ps1 幂等清理；多框架共存靠前缀命名空间（ref-*/ref_* 与 anchor-*/anchorlaw_*）；**插件 schema 门禁**：install/selfcheck 必跑 tests/check_plugin_schema.mjs（parameters 必须编译后 JSON Schema，扁平 spec 投影给模型无顶层 type → 所有会话崩，2026-08-13 事故教训）。
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
