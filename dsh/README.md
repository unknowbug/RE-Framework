# RE-Framework — DSH Host Adaptation (`dsh/`)

**RE-Framework v2（逆向 + 编程通用工程方法论框架）的 DSH（DeepSeek Harness）宿主适配层。**

本子树位于 RE-Framework 仓库内，与 Reasonix 侧（`skills/`、`spec/`、`templates/`、`knowledge-builtin/`、`scripts/`）共存——**同一框架，单一仓库，双宿主适配不分裂**。由 DSH agent（RE-Framework maintainer）维护。

## 这是什么

把 RE-Framework 的四大能力搬进 DSH 并持续维护：

| 能力 | DSH 形态 |
|------|----------|
| 17 个方法论技能（core/re-binary/re-code/swe 四模块 + ref-maintain） | `skills/` → preset 内嵌（`customSkillDirs`） |
| 框架自检 / 部署 / 索引合并 / 骨架初始化 | 模型工具 `ref_manifest_validate` / `ref_install` / `ref_merge_index` / `ref_init` / `ref_status` |
| Phase 0-3 工作流 + 执行强制链（scout/fan-out/judge/knowledge） | agent preset `re-framework`（人格 + subagent 隔离） |
| 正文零漂移守护 | `sync_skills.py`（生成）+ `tests/test_manifest.py`（校验）+ `SYNC.md`（溯源） |

## 快速开始

```powershell
# 1. 安装/同步到 DSH 运行时（用户级 preset，技能仅 preset 内嵌）
pwsh dsh/scripts/install.ps1

# 2. 自检（工具链 / 技能 manifest / 框架自扫 / 安装产物）
pwsh dsh/scripts/selfcheck.ps1
```

装完后新建会话时选择 **re-framework** preset（工作目录指向仓库根 `E:\PYTHON\RE-Framework`），即可使用 5 个 `ref_*` 工具和 17 个 `ref-*` 技能。

## 目录结构

```
dsh/
├── skills/                # 17 个技能事实源（16 个由 sync_skills.py 生成；ref-maintain 手写）
├── plugins/               # 工具插件事实源（re-framework-tools.js，5 个 ref_* 工具）
├── preset/                # agent preset 组合源（agent.cordis.yml + preset.yml）
├── scripts/               # sync_skills.py（重生成）/ install.ps1（部署）/ selfcheck.ps1（自检）
├── tests/                 # test_manifest.py（DSH 命名 + 正文级上游一致性校验）
├── SYNC.md                # 与 Reasonix 侧的同步溯源戳
├── PORT-ASSESSMENT.md     # 移植评估（历史存档）
└── AGENTS.md              # DSH 维护入口（agent 每会话加载）
```

## 维护约定

- **单一事实源**：框架正文只存仓库根；技能正文规范份在 `../skills/`，本目录只允许 frontmatter 适配（改 `scripts/sync_skills.py` 后重生成）
- **只改事实源**（`skills/` 生成器、`plugins/`、`preset/`），然后跑 `scripts/install.ps1` 重装
- 安装产物（`~/.dsh/.agent-presets/re-framework/`）禁止手改
- 改动后必须 `scripts/selfcheck.ps1` 全绿（含正文级一致性校验）
- 技能仅 preset 内嵌（不装用户级全局）——ref-* 方法论技能不污染其它 preset 的会话

## 依赖

- Python 3.x（脚本仅 stdlib；`merge_index.py` 需 PyYAML）
- 验证协议引用 [Anchorlaw v0.15](https://github.com/unknowbug/anchorlaw)（协议引用，不复制实现；swe 模块可选装 anchorlaw CLI）
