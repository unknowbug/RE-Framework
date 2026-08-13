---
name: ref-maintain
description: 维护 RE-Framework DSH 适配层本身（dsh/ 子树）——自检全绿、单一事实源、技能/插件/preset 同步（sync_skills.py / install.ps1）、上游变更镜像（SYNC.md）、提交纪律
whenToUse: 维护 RE-Framework 的 DSH 适配层（dsh/ 子树）时——任何改动前先自检基线、改动后必须自检全绿；上游（../skills/、../spec/）变更后需镜像同步
---

# ref-maintain — RE-Framework DSH 适配层维护（DSH-only）

> 本技能是 **DSH 专属**技能：无 Reasonix 上游对应（../skills/ 中无 ref-maintain），不参与正文漂移校验（test_manifest.py 的 DSH_ONLY 豁免集）。
> 定位：对齐 Anchorlaw 的 anchor-maintain 思路——框架必须能维护自己。
> 适用范围：`dsh/` 子树（skills/、plugins/、preset/、scripts/、tests/、SYNC.md、AGENTS.md）。

## 维护铁律

1. **自检全绿**：任何改动前先跑 `pwsh dsh/scripts/selfcheck.ps1` 确认基线，改动后必须再次全绿（含第 3 项框架自扫 validate_manifest.py——第一律反身应用：框架的 manifest 校验器必须能校验框架自己）。
2. **单一事实源**：
   - 技能**正文**只存在于 `../skills/<dot-name>/SKILL.md`（Reasonix 侧）；`dsh/skills/` 是适配份——**frontmatter 适配改 `dsh/scripts/sync_skills.py` 的 ADAPT 映射表**，重跑 `python dsh/scripts/sync_skills.py` 再生成，禁止手改 `dsh/skills/` 正文。
   - `dsh/skills/ref-maintain/SKILL.md` 是唯一的直接手写例外（DSH-only）。
   - 安装产物（`~/.dsh/.agent-presets/re-framework/`）禁止手改，一律由 `dsh/scripts/install.ps1` 重装生成。
3. **命名纪律**：DSH 技能名必须 kebab-case（`core-plan` 而非 `core.plan`）；插件工具名 `ref_*`。
4. **插件持久化纪律**：动态插件（cordis_define 定义）只在当前进程存活——持久能力必须落成 `dsh/plugins/re-framework-tools.js` + preset 行，禁止把维护性能力留在动态插件里。
5. **preset 纪律**：`~/.dsh/.agent-presets/re-framework/` 是用户级 preset（install.ps1 生成，可再装）；shipped preset（harness 安装目录）一律只读，改动只能以复制派生。
6. **提交纪律**：提交前自检全绿；不自动 git 提交（仓库可能有未提交的人类改动，提交时机由人类决定）。

## 上游变更镜像（升级检查）

- `../skills/`、`../spec/engineering-framework-v1.md` 或 Anchorlaw 协议引用版本（当前基线 v0.17，`git grep 'v0\.[0-9]'` 核对）变更后：
  1. `python dsh/scripts/sync_skills.py` 重新生成 `dsh/skills/`；
  2. 检查 `dsh/tests/test_manifest.py` 的 EXPECTED 集与正文漂移是否仍通过；
  3. 更新 `dsh/SYNC.md`（来源 commit/时间/差异）；
  4. 若涉及新技能：在 sync_skills.py ADAPT 映射与 test_manifest.py EXPECTED 中登记；
  5. `pwsh dsh/scripts/selfcheck.ps1` 全绿。

## 自检命令速查

```powershell
# 1. DSH 技能 manifest + 正文级上游一致性
python dsh/tests/test_manifest.py

# 2. 框架自检（R1-R6 manifest 校验器，spec §2.5 反身应用）
python scripts/validate_manifest.py

# 3. 重新生成 DSH 技能（改过 ADAPT 映射后）
python dsh/scripts/sync_skills.py

# 4. 部署到 DSH 运行时（写 ~/.dsh，需全盘权限）
pwsh dsh/scripts/install.ps1

# 5. 四段总自检（工具链/manifest/自扫/安装产物）
pwsh dsh/scripts/selfcheck.ps1
```

## 约束

- 不改 Reasonix 侧任何文件（`../skills/`、`../spec/`、`../templates/`、`../knowledge-builtin/`、`../scripts/`、根 `AGENTS.md`、根 `README.md`）——上游正文改动属于 Reasonix 工作流，本技能只做镜像与守护。
- 正文漂移由 `dsh/tests/test_manifest.py` 逐字节守护；发现漂移 → 重跑 sync_skills.py，不手改。
