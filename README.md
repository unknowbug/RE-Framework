# RE-Framework v2 — 通用工程方法论框架（逆向 + 编程，DSH 宿主）

> 基于《打破传统AI逆向的新思路：多Agent、自主管理上下文》(BitWarden, 看雪学苑 2026.06.18) 的方法论内核，
> 工程化、Skills化、SubAgents化拆分升级：**领域无关核心 + 按需加载领域模块**，从二进制逆向到代码逆向到常规编程全兼容。
> **DeepSeek Harness（DSH）是唯一维护宿主**（2026-08-21 起；Reasonix 宿主格式已归档至 `archive/reasonix/`，Fork 可恢复自行迭代）。
> 验证协议继承 [Anchorlaw Protocol v0.18](https://github.com/unknowbug/anchorlaw)（MIT，协议引用，不复制实现）。

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

# 3. 自检（工具链 / 技能 manifest / 安装产物 / 插件 schema）
pwsh dsh/scripts/selfcheck.ps1
```

**DSH 会话标准流程**：根 `AGENTS.md`（DSH-first 索引）→ 先读 `dsh/SKILL-MAP.md`（DSH 探测器：强初始化 / 任务路由 / Phase 0-3 / 执行强制链）→ 按 **kebab 名**加载技能执行。

## 架构

```
RE-Framework/
├── AGENTS.md                  # DSH-first 索引（自动加载入口）
├── spec/                      # 框架协议（铁律/工作流/产物/知识库/版本）+ Anchorlaw v0.18 引用
├── dsh/                       # DSH 宿主适配层（唯一维护区）
│   ├── skills/                # 17 个 ref-* 技能（单一事实源，直接维护）
│   ├── SKILL-MAP.md           # DSH 探测器（强初始化/路由/Phase 0-3/执行强制链 + dot→kebab 映射）
│   ├── plugins/re-framework-tools.js   # 3 个 ref_* 模型工具
│   ├── preset/                # re-framework agent preset
│   ├── scripts/install.ps1 + selfcheck.ps1   # 安装 + 四段自检
│   ├── tests/                 # test_manifest.py + check_plugin_schema.mjs
│   └── AGENTS.md              # DSH 维护入口
├── templates/                 # 产物 schema（语言无关）
├── knowledge-builtin/         # 预置知识库
├── scripts/merge_index.py     # 并行索引合并（ref_merge_index 依赖）
└── archive/reasonix/          # Reasonix 宿主格式归档（只读，RESTORE.md 可恢复）
```

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
| v2.2 | 2026-08-21 | **DSH 唯一宿主迁移**：Reasonix 归档（`archive/reasonix/`）、`dsh/skills/` 变单一事实源、工具 5→3（ref_manifest_validate/ref_install 随 Reasonix 退役）、根 AGENTS.md 重写 DSH-first、spec 标注归档、安装简化（单一 install.ps1）、对 Anchorlaw 纯引用式安装（零复制） |
| v2.1 | 2026-08-14~15 | DSH 适配层（`dsh/` 子树）、技能用户级全局、工具 preset-only、Anchorlaw 引用 v0.15→v0.17→v0.18、SKILL-MAP DSH 探测器、错误账本强化 |
| v2.0 | 2026-08 | 模块化重构（Reasonix 时代，已归档） |
| v1.0 | 2026-06 | 单文件 42KB CLAUDE.md（BitWarden 方法论，已归档） |
