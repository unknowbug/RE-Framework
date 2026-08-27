# RE-Framework — DSH Host Adaptation (`dsh/`)

**RE-Framework v2（逆向 + 编程通用工程方法论框架）的 DSH（DeepSeek Harness）宿主适配层。**

本子树位于 RE-Framework 仓库内，与 Reasonix 侧（`skills/`、`spec/`、`templates/`、`knowledge-builtin/`、`scripts/`）共存——**同一框架，单一仓库，双宿主适配不分裂**。由 DSH agent（RE-Framework maintainer）维护。

## 这是什么

把 RE-Framework 的四大能力搬进 DSH 并持续维护：

| 能力 | DSH 形态 |
|------|----------|
| 17 个方法论技能（core/re-binary/re-code/swe 四模块 + ref-maintain） | `skills/` → **用户级全局 `~/.dsh/skills/`**（任何 preset/工作目录的会话按需加载）+ preset 内嵌（re-framework 完整工作台） |
| 5 个工具（status/validate/install/merge-index/init） | 仅 re-framework preset（`ref_*` 工具是框架 python 脚本的包装；其他会话用 pwsh 直接跑脚本） |
| Phase 0-3 工作流 + 执行强制链（scout/fan-out/judge/knowledge） | agent preset `re-framework`（人格 + subagent 隔离） |
| 正文零漂移守护 | `sync_skills.py`（生成）+ `tests/test_manifest.py`（校验）+ `SYNC.md`（溯源） |

## 可见性设计（v2.1 修订，2026-08-15 用户拍板：无 global 工具组）

- **技能用户级全局**：17 个 ref-* 装到 `~/.dsh/skills/`，任何会话（任何 preset、任何工作目录）按需加载——方法论在任何项目（如 CoreSwap）用标准工具集即可执行；与 Anchorlaw 的 anchor-*（同样用户级全局）命名空间独立（ref-*/anchor-*），互不冲突。技能是纯指令，加载不触碰工作区外文件，无沙箱问题。
- **工具仅 preset**：全部 5 个 `ref_*` 工具只在 re-framework preset 会话出现——它们是框架 python 脚本（install.py / validate_manifest.py / merge_index.py）的便利包装，其他会话直接用 pwsh 跑脚本即可，无需全局工具组。
- **权限边界**（实测）：跨工作区**读**放行、**写**仅限会话工作区——项目侧操作（读框架源 + 写目标项目工作区内）pwsh 直接可跑。

## 快速开始

```powershell
# 1. 安装/同步到 DSH 运行时（preset + 用户级技能）
pwsh dsh/scripts/install.ps1

# 2. 自检（工具链 / 技能 manifest / 框架自扫 / 安装产物 / 插件 schema）
pwsh dsh/scripts/selfcheck.ps1
```

装完后，**任何 preset 会话**（standard 等）都能在技能目录看到 17 个 ref-* 技能按需加载；选 **re-framework** preset 另有完整工作台（人格 + 5 个 `ref_*` 工具）。工作目录指向项目本身（如 `E:\PYTHON\CoreSwap`）即可，无需指向本仓库。

## 目录结构

```
dsh/
├── skills/                # 17 个技能事实源（16 个由 sync_skills.py 生成；ref-maintain 手写）
├── plugins/               # 工具插件事实源（re-framework-tools.js，config.tools 控制注册子集）
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
- 安装产物（`~/.dsh/.agent-presets/re-framework/`、`~/.dsh/skills/ref-*`、`<profile>/plugins/re-framework/`、`<profile>/cordis.patch.yml` 的 re-framework-tools-global insert 行）禁止手改
- 改动后必须 `scripts/selfcheck.ps1` 全绿（含正文级一致性校验 + 第 5 项插件 schema 校验）
- 多框架共存：技能/工具命名空间按框架前缀隔离（ref-*/ref_* 与 anchor-*/anchorlaw_*）；插件文件按框架子目录存放（`<profile>/plugins/<framework>/`）；`<profile>/cordis.patch.yml` 是唯一用户级工具登记点（insert 形态），可查可控；**工具 parameters 必须编译后 JSON Schema（挂载前跑 tests/check_plugin_schema.mjs）**

## 依赖

- Python 3.x（脚本仅 stdlib；`merge_index.py` 需 PyYAML）
- 验证协议引用 [Anchorlaw v0.19](https://github.com/unknowbug/anchorlaw)（协议引用，不复制实现；swe 模块可选装 anchorlaw CLI）
