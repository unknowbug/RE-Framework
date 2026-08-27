---
name: ref-maintain
description: 维护 RE-Framework DSH 适配层本身（dsh/ 子树）——自检全绿、单一事实源（dsh/skills 直接维护）、技能/插件/preset 同步（install.ps1）、Anchorlaw 协议升级核对（SYNC.md）、提交纪律
whenToUse: 维护 RE-Framework 的 DSH 适配层（dsh/ 子树）时——任何改动前先自检基线、改动后必须自检全绿；Anchorlaw 协议版本或 spec 变更后需升级核对
---

# ref-maintain — RE-Framework DSH 适配层维护

> 定位：对齐 Anchorlaw 的 anchor-maintain 思路——框架必须能维护自己。
> 适用范围：`dsh/` 子树（skills/、plugins/、preset/、scripts/、tests/、SYNC.md、AGENTS.md、SKILL-MAP.md）。
> 单一事实源：`dsh/skills/` 是技能唯一事实源（2026-08-21 Reasonix 归档后直接维护）；技能正文内的 dot 名是规范引用，按 `dsh/SKILL-MAP.md` §一 映射到 kebab 名加载。
> 接口速查：DSH 会话按 `dsh/SKILL-MAP.md`（DSH 探测器 + dot→kebab 映射 + ref_* 工具/脚本对照）调用。

## 维护铁律

1. **自检全绿**：任何改动前先跑 `pwsh dsh/scripts/selfcheck.ps1` 确认基线，改动后必须再次全绿（四段：工具链 / 技能 manifest / 安装产物 / 插件 schema——第 4 项防 2026-08-13 事故复发）。
2. **单一事实源**：技能正文**直接改 `dsh/skills/<name>/SKILL.md`**（无上游派生；Reasonix 归档 `archive/reasonix/` 不参与同步，恢复走其 RESTORE.md）；`tests/test_manifest.py` 守护 manifest 形态（命名/frontmatter/技能集/交叉引用）。
3. **命名纪律**：DSH 技能名必须 kebab-case（`core-plan` 而非 `core.plan`）；插件工具名 `ref_*`。
4. **插件持久化纪律**：动态插件（cordis_define 定义）只在当前进程存活——持久能力必须落成 `dsh/plugins/re-framework-tools.js` + preset 行，禁止把维护性能力留在动态插件里。
5. **preset 纪律**：`~/.dsh/.agent-presets/re-framework/` 是用户级 preset（install.ps1 生成，可再装）；shipped preset（harness 安装目录）一律只读，改动只能以复制派生。
6. **schema 门禁（2026-08-13 事故教训）**：`ctx.tools.register()` 不编译 parameters——必须传**编译后 JSON Schema**（`{type:'object', properties, required}`）；扁平 spec 投影给模型无顶层 type → 所有会话崩。install.ps1 复制插件前与 selfcheck 第 4 项都强制跑 `tests/check_plugin_schema.mjs`（fail closed）。
7. **可见性现状（2026-08-15 用户拍板 + 2026-08-21 迁移）**：技能**用户级全局**（`~/.dsh/skills/ref-*`，任何会话按需加载）+ preset 内嵌双路径；工具**仅 re-framework preset**（3 个 ref_*：status/merge_index/init——manifest_validate/install 随 Reasonix 归档退役）；**无 global 工具组**——install.ps1 幂等清理 profile patch 残留（re-framework-tools-global insert 行）。
8. **提交纪律**：提交前自检全绿；不自动 git 提交（仓库可能有未提交的人类改动，提交时机由人类决定）。

## Anchorlaw 协议升级核对

- Anchorlaw 协议引用版本（当前基线 v0.19，`git grep 'v0\.[0-9]'` 核对）或 `spec/engineering-framework-v1.md` 变更后：
  1. 对照 Anchorlaw changelog 核对 spec §3 同步契约（条款保留/版本基线/同源双写）；
  2. 更新 `dsh/SYNC.md`（来源 commit/时间/差异）；
  3. 若涉及技能正文语义：直接改 `dsh/skills/` 对应技能，并在 `tests/test_manifest.py` 的 ADAPT/EXPECTED 中同步（改名/新增时）；
  4. `pwsh dsh/scripts/selfcheck.ps1` 全绿。

## 自检命令速查

```powershell
# 1. DSH 技能 manifest（命名/frontmatter/技能集/交叉引用；dsh/skills 单一事实源）
python dsh/tests/test_manifest.py

# 2. 部署到 DSH 运行时（写 ~/.dsh，需全盘权限）
pwsh dsh/scripts/install.ps1

# 3. 四段总自检（工具链 / 技能 manifest / 安装产物 / 插件 schema）
pwsh dsh/scripts/selfcheck.ps1
```

## 约束

- **不改归档区** `archive/reasonix/`（Reasonix 宿主格式已停止维护；Fork 恢复走其 RESTORE.md）。
- 框架核心文件（`../spec/`、`../templates/`、`../knowledge-builtin/`、`../scripts/merge_index.py`）按需引用不复制。
- manifest 形态由 `dsh/tests/test_manifest.py` 守护；发现违规 → 按提示改 `dsh/skills/` 对应技能，不绕过校验。
