# RESTORE — 从存档恢复 Reasonix 工作副本

> 适用对象：Fork 了 RE-Framework 仓库、想基于 **Reasonix 版本**继续迭代的维护者。
> RE-Framework 主仓库已停止维护 Reasonix 宿主格式（仅维护 DSH），本脚本让你一键回到 Reasonix 工作副本。

## 前置

- 已 Fork `github.com/unknowbug/RE-Framework` 并克隆到本地
- 在**仓库根**执行（脚本内所有路径相对仓库根）

## 恢复步骤

```powershell
# 1. 运行恢复脚本（把 archive/reasonix 内容恢复到仓库根）
pwsh archive/reasonix/restore-reasonix.ps1

# 2. 验证恢复结果（应看到以下内容回到仓库根）
#    skills/                          （16 个 dot 名技能 + modules/）
#    AGENTS.md                        （Reasonix 探测器入口）
#    scripts/install.py               （Reasonix 部署器）
#    scripts/validate_manifest.py     （Reasonix manifest 校验器）
#    memory/                          （框架 memory 文件）
#    dsh/scripts/sync_skills.py       （技能同步生成器，从 skills/ 派生 dsh/skills/）
```

## 恢复后

- `skills/` 重新成为技能规范正文事实源，根 `AGENTS.md` 重新成为 Reasonix 探测器入口
- `dsh/skills/` 重新成为派生适配份（由 `dsh/scripts/sync_skills.py` 从 `skills/` 生成）
- 协议正文（`spec/`）、产物模板（`templates/`）、预置知识库（`knowledge-builtin/`）仍在仓库根，可直接使用
- **从此自行迭代**：本存档目录不再更新，你的迭代基于恢复时的状态进行

## 恢复脚本行为

`restore-reasonix.ps1` 执行（幂等，已存在的目标备份为 `.bak`，不静默覆盖）：

1. `archive/reasonix/skills/` → 仓库根 `skills/`
2. `archive/reasonix/AGENTS.md` → 仓库根 `AGENTS.md`
3. `archive/reasonix/README.md` + `README_EN.md` → 仓库根（Reasonix 版文档）
4. `archive/reasonix/scripts/install.py` + `validate_manifest.py` → 仓库根 `scripts/`
5. `archive/reasonix/scripts/sync_skills.py` → 仓库根 `dsh/scripts/`
6. `archive/reasonix/memory/` → 仓库根 `memory/`

> 注意：恢复后仓库根同时存在 DSH 侧（`dsh/`）与 Reasonix 侧（`skills/` 等）——恢复脚本不删除 `dsh/`（双宿主共存，由你决定是否保留 DSH 适配层）。
