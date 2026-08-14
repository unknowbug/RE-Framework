# AGENTS.md — RE-Framework dsh/ 子树（DSH 宿主适配层）

> 本目录（`dsh/`）是 **RE-Framework 仓库的 DSH 宿主适配层**：Reasonix 侧（`skills/`、`spec/`、`templates/`、`knowledge-builtin/`、`scripts/`、根 `AGENTS.md`）与 DSH 生态适配（DSH 技能格式、工具插件、agent preset、维护脚本）共存于同一仓库——**单一仓库，双宿主，不分裂**。
> 维护者：DSH agent（RE-Framework maintainer）。每次会话开始必读本文件。

## 〇、开始工作前（每个 session 必做）

1. 确认仓库状态：仓库根即 Reasonix 事实源，本目录（`dsh/`）即 DSH 适配事实源——**单一仓库，无第二份框架副本**。
2. 跑自检确认基线全绿：`pwsh dsh/scripts/selfcheck.ps1`（工具链 / 技能 manifest / 框架自扫 / 安装产物四项）。
3. 若改动涉及框架正文：正文只能改 `../skills/`（Reasonix 规范正文），本目录技能由 `sync_skills.py` 派生 + `tests/test_manifest.py` 逐字节守护。

## 一、本目录定位（一句话）

**RE-Framework 的 DSH（DeepSeek Harness）宿主适配层**——上层 `../skills/` 是宿主无关的技能规范正文；本目录持有 DSH 格式技能（kebab-case + whenToUse 适配）、模型工具插件、agent preset 与维护脚本，并保证与规范正文零漂移。

## 二、目录结构（事实源 vs 安装产物）

| 路径 | 内容 | 角色 |
|------|------|------|
| `skills/` | 17 个 ref-* 技能（16 个 DSH 版 SKILL.md 由 `scripts/sync_skills.py` 从 `../skills/` 生成；`ref-maintain` 为 DSH-only 手写） | **事实源**（改 `scripts/sync_skills.py` 的 ADAPT 映射后重生成） |
| `plugins/re-framework-tools.js` | 5 个模型工具插件（status/validate/install/merge-index/init） | **事实源**（改这里） |
| `preset/agent.cordis.yml` | re-framework agent preset 组合 | **事实源**（改这里） |
| `preset/preset.yml` | preset 显示元数据 | 事实源 |
| `scripts/sync_skills.py` | 技能重新生成器（frontmatter 适配映射所在） | 维护工具 |
| `scripts/install.ps1` | 安装/同步到 DSH 运行时 | 维护工具 |
| `scripts/selfcheck.ps1` | 四项自检 | 维护工具 |
| `tests/test_manifest.py` | 技能 manifest 校验（DSH 命名 + **正文级**上游一致性） | 维护测试 |
| `SYNC.md` | 溯源戳（上次同步的上游 commit + 时间 + 差异） | 溯源记录 |
| `PORT-ASSESSMENT.md` | 移植评估（历史存档） | 历史 |
| **安装产物（勿手改）** | | |
| `~/.dsh/.agent-presets/re-framework/` | 已安装 preset（组合 + plugins/ + skills/） | install.ps1 生成 |
| `~/.dsh/skills/ref-*` | **用户级全局技能**（任何 preset/工作目录的会话按需加载） | install.ps1 同步 |
| `~/.dsh/.agent-presets/re-framework/plugins/` | preset 内嵌工具插件（5 个 ref_*，仅 re-framework preset 会话） | install.ps1 复制 |

**同步纪律（核心铁律）**：所有修改只改本目录事实源，然后跑 `scripts/install.ps1` 重装——安装产物一律视为可再生，禁止手改。技能**正文**不允许在本目录手改——改 `../skills/` 后跑 `sync_skills.py` 重生成，`tests/test_manifest.py` 守护一致性（只允许行尾归一化差异）。

## 三、维护铁律（对应 ref-maintain，DSH 版）

1. **自检全绿**：任何改动必须 `dsh/scripts/selfcheck.ps1` 全绿（第 3 项框架自扫=第一律反身应用：框架的 manifest 校验器必须能校验框架自己）。
2. **单一事实源**：框架正文只存仓库根一份；`../skills/` 是规范份，`dsh/skills/` 是适配份（frontmatter 适配改 `sync_skills.py`，正文由 test_manifest.py 逐字节守护）；`ref-maintain` 是唯一手写例外（DSH-only）。
3. **新能力必须配验证**：新增技能/工具要能通过自检或实测证明，否则标注 Unverified。
4. **命名纪律**：DSH 技能名必须 kebab-case（`core-plan` 而非 `core.plan`）；插件工具名 `ref_*`。
5. **插件持久化纪律**：动态插件（cordis_define 定义）只在当前进程存活——**持久能力必须落成 `plugins/` 文件 + preset 行**，禁止把维护性能力留在动态插件里。
6. **preset 纪律**：`~/.dsh/.agent-presets/re-framework/` 是用户级 preset（由 install.ps1 生成，可再装）；shipped preset（harness 安装目录）一律只读，改动只能以复制派生。
7. **可见性纪律（v2.1 修订，2026-08-15 用户拍板：无 global 工具组）**：技能装**用户级全局**（`~/.dsh/skills/ref-*`）+ preset 内嵌双路径——任何项目会话可加载，不依赖选择 re-framework preset 或工作目录；**工具仅 re-framework preset**（全部 5 个 ref_*）——它们是框架 python 脚本的包装，其他会话用 pwsh 直接跑脚本（`python scripts/install.py / validate_manifest.py / merge_index.py`）；曾尝试的 profile patch global 挂载（`<profile>/cordis.patch.yml` insert 行）已**撤销**（2026-08-15），install.ps1 幂等清理；多框架共存靠前缀命名空间（ref-*/ref_* 与 anchor-*/anchorlaw_*）；**插件 schema 门禁**：install/selfcheck 必跑 tests/check_plugin_schema.mjs（parameters 必须编译后 JSON Schema，扁平 spec 投影给模型无顶层 type → 所有会话崩，2026-08-13 事故教训）。
8. **提交纪律**：提交前自检全绿；**不自动 git 提交**（仓库可能有未提交的人类改动，提交时机由人类决定）。

## 四、与 Reasonix 侧的分工（同一个仓库内）

- **仓库根（`../`）**：框架正文（`spec/engineering-framework-v1.md`）、Reasonix 技能（`skills/`）、模板、预置知识库、Python 脚本、Reasonix 入口 `AGENTS.md`。
- **本目录（`dsh/`）**：DSH 生态适配层（DSH 技能格式、插件、preset、维护脚本），入口为本文件。
- **一致性机制**：`tests/test_manifest.py` 对 `../skills/` 做正文级校验（行尾归一化后逐字节比对）；`SYNC.md` 记录同步溯源；框架正文更新先改仓库根，再跑 `sync_skills.py` 同步本目录适配。
- **边界**：绝不修改 Reasonix 侧任何文件（`../skills/`、`../spec/`、`../templates/`、`../knowledge-builtin/`、`../scripts/`、根 `AGENTS.md`、根 `README.md`）。

## 五、re-framework preset 的人格承诺

使用 re-framework preset 的会话，agent 强制走框架纪律：强初始化（读知识库 → 架构设计待批准 → 预置子角色介入点）→ 任务类型探测器路由（re-binary / re-code / swe）→ Phase 0-3 工作流 → 执行强制链（scout/fan-out/judge/knowledge），`confirmed` 只能由人类授予。scout/worker/judge/fan-out 经 subagent 工具隔离执行（spec §4.5）。

## 六、会话工作目录说明

推荐新会话将工作目录指向本仓库根（`E:\PYTHON\RE-Framework`），加载根 `AGENTS.md`（Reasonix 索引）+ 本文件（DSH 适配维护入口）；preset 选择 `re-framework`。
