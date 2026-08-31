# RE-Framework v2 — AGENTS.md（DSH 宿主索引式入口）

> **定位**: 通用工程方法论框架（逆向 + 编程）。**DeepSeek Harness（DSH）是唯一维护宿主**。
> **宿主说明**: 维护入口见 `dsh/AGENTS.md`；DSH 会话探测器见 `dsh/SKILL-MAP.md`；Reasonix 宿主格式已停止维护并归档（`archive/reasonix/`，Fork 可恢复自行迭代）。
> **协议**: `spec/engineering-framework-v1.md`（框架协议）+ [Anchorlaw Protocol v0.20](https://github.com/unknowbug/anchorlaw)（验证协议，协议引用）。

---

## 〇、开始工作前（每个 DSH session 必做，MUST 按序执行）

1. 跑自检确认基线全绿：`pwsh dsh/scripts/selfcheck.ps1`（四段：工具链 / 技能 manifest / 安装产物 / 插件 schema）。
2. 读 `dsh/SKILL-MAP.md`（DSH 探测器）——技能一律按 **kebab 名**加载（`core-plan` 而非 `core.plan`）。
3. 按 SKILL-MAP §〇 执行强初始化：读知识库（`knowledge/INDEX.md`）→ 架构设计待用户确认 → 预置子角色介入点。

## 一、DSH 探测器（标准流程）

详见 `dsh/SKILL-MAP.md` §〇（强初始化三步 / 任务类型路由表 / Phase 0-3 / 执行强制链）。摘要：

- **任务路由**：二进制（.dll/.exe/汇编/IDA/Ghidra/vtable/RTTI/xref/脱壳）→ `re-binary`（`re-scout` → `re-lift`/`re-classify`/`re-trace`）；字节码/源码（.jar/.class/反混淆/mapping/mod 逆向）→ `re-code`（`recode-scout` → `recode-deobfuscate`/`recode-classmap`/`recode-behavior`）；编程（写/改/审代码、协议设计、开发、测试）→ `swe`（`swe-guide` → anchor-*，纯引用 Anchorlaw 已装技能/工具）；无法判断 → 询问用户目标格式。
- **核心铁律**：置信度状态机（`confirmed` 仅用户拍板）、产物必须落盘（`.artifacts/` + `index.yaml`、`.investigations/`）、防幻觉（`@anchor.test` source 必填）、模块边界、上下文隔离。
- **流程**：Phase 0 架构（`core-plan`，强制）→ Phase 1 勘探（scout）→ Phase 2 分析（worker）→ Phase 2.5 验证（Anchorlaw：全功能 test / degraded）→ Phase 3 审查（`core-judge`）→ 用户拍板 `confirmed` → 归档。
- **执行强制链**：judge/scout/fan-out/knowledge 四触发点（详见 SKILL-MAP §〇）。

## 二、维护（DSH 适配层）

- 维护入口：`dsh/AGENTS.md` —— `dsh/skills/` 是技能**单一事实源**（直接改，无上游派生）；四段自检；插件 schema 门禁（2026-08-13 事故教训）。
- 提交纪律：提交前自检全绿；不自动 git 提交（提交时机由用户决定）。

## 三、协议引用

- **框架协议**：`spec/engineering-framework-v1.md`（§1 铁律 / §3 Anchorlaw 引用与升级核对 / §4 工作流 / §5 产物 schema / §6 知识库 / §7 版本管理 / §8 诚实声明）。
- **验证协议**：[Anchorlaw v0.20](https://github.com/unknowbug/anchorlaw)（协议引用，不复制实现）；升级核对见 spec §3 同步契约。
- **Reasonix 归档**：宿主格式（dot 名技能、`.reasonix/skills/` 部署、`install.py`/`validate_manifest.py`）已归档至 `archive/reasonix/`，不再维护；Fork 用户可按 `archive/reasonix/RESTORE.md` 恢复自行迭代。
