# SKILL-MAP — RE-Framework DSH 探测器 + 调用接口速查

> **定位（v2.1 升级）**：本文件是 DSH 会话的**探测器 + 调用接口桥接**。根 `AGENTS.md`（Reasonix 探测器）用 **dot 名**引用技能（`core.plan`、`re.scout`…），DSH 会话的技能注册名是 **kebab 名**（`core-plan`、`re-scout`…）——DSH 会话按根 AGENTS.md 的 dot 名加载技能会**找不到技能**（Anchorlaw v0.18 只解决协议层宿主契约 §16，未解决此名映射）。**DSH 会话（任何 preset、工作区根 = 本仓库）应先读本文件，再按 §〇 走标准流程。**

## 〇、DSH 探测器（标准流程驱动，MUST 按序执行）

> 对应根 AGENTS.md 的 Reasonix 版流程，但技能名全部用 **kebab 形**（DSH 可加载名）。执行中提到的技能一律按 §一 映射表加载。

**强初始化三步**（每个 session 第一件事，未经完成不得开始实际分析）：

1. **STEP 1 — 读知识库**（先于一切）：查 `knowledge/INDEX.md` + 相关 builtin/discovered 条目；无相关条目 → 标注"需外部资料"，让用户决定，不自行编造。（对应 `core-knowledge`）
2. **STEP 2 — 规划工作**：跑架构设计（`core-plan`：轻量 ≤3 要点 / 重量完整文档），展示给用户确认——**未经用户确认架构，不得开始实际分析**；架构文档落盘 `.investigations/000-架构设计/`。
3. **STEP 3 — 预置子角色介入点**：在计划中预置全部子角色（scout/worker/fan-out/judge/knowledge）的介入时机（`core-plan` 模板），执行只核对不补排。

**任务类型探测器**（路由到模块，技能按 §一 kebab 名加载）：

| 任务特征 | 模块 | 加载技能（kebab） |
|---------|------|------------------|
| 二进制（.dll/.exe/.so/.bin、汇编、IDA/Ghidra/Frida、vtable、RTTI、xref、脱壳、反调试） | re-binary | `re-scout`（勘探）→ `re-lift` / `re-classify` / `re-trace` |
| 字节码/源码（.jar/.class/.java、反混淆/mapping/ProGuard/R8、mod 逆向、Minecraft） | re-code | `recode-scout` → `recode-deobfuscate` / `recode-classmap` / `recode-behavior` |
| 编写/修改/审查代码、协议设计、常规开发、测试 | swe | `swe-guide` → anchor-*（`anchor-concepts`/`anchor-scan`/`anchor-write`/`anchor-test`/`anchor-noise`…） |
| 混合任务 | 主模块 + 按需附加 | 各自主模块技能 |
| 无法判断 | 询问用户目标格式，不猜 | — |

**Phase 流程**：Phase 0 架构设计（`core-plan`，强制）→ Phase 1 勘探（`re-scout`/`recode-scout`，subagent）→ Phase 2 分析（worker 加载领域动作技能）→ Phase 2.5 验证（Anchorlaw 全功能 test / degraded）→ Phase 3 审查（`core-judge`，只出意见）→ **用户拍板 `confirmed` → 归档**。

**执行强制链**（四条触发点，MUST/SHOULD 分层）：judge（`core-judge`）——confirmed 授予前 / 重大转向 / 收尾交付 MUST，candidate 授予 SHOULD，随 todo 计划预置；scout——「机制未明」大排查初期 MUST 勘探（禁止直接跳单点定位）；fan-out——判定树分叉 ≥2 个互斥候选 MUST 并行（`subagent` 工具派 .bN）；knowledge——结论性 docs/discovered 写入前 MUST subagent 产出草稿。**`confirmed` 只能由人类授予**。

## 一、技能名映射（DSH 会话一律用右列 kebab 名）

| 模块 | dot（Reasonix 规范名 / 根 AGENTS.md 触发表） | kebab（DSH 技能名，skill 工具按此加载） |
|------|----------------------------------------------|------------------------------------------|
| core | `core.plan` / `core.artifact` / `core.knowledge` / `core.version` / `core.fanout` / `core.worker` / `core.judge` | `core-plan` / `core-artifact` / `core-knowledge` / `core-version` / `core-fanout` / `core-worker` / `core-judge` |
| re-binary | `re.lift` / `re.classify` / `re.trace` / `re.scout` | `re-lift` / `re-classify` / `re-trace` / `re-scout` |
| re-code | `recode.deobfuscate` / `recode.classmap` / `recode.behavior` / `recode.scout` | `recode-deobfuscate` / `recode-classmap` / `recode-behavior` / `recode-scout` |
| swe | `swe.guide` | `swe-guide` |
| DSH-only | — | `ref-maintain` |

**Anchorlaw 接口**（swe 模块路由目标，同为 kebab，用户级全局）：`anchor.concepts`→`anchor-concepts`、`anchor.scan`→`anchor-scan`、`anchor.challenge`→`anchor-challenge`、`anchor.write`→`anchor-write`、`anchor.test`→`anchor-test`、`anchor.noise`→`anchor-noise`、`anchor.degrade`→`anchor-degrade`、`anchor.scout`→`anchor-scout`、`anchor.worker`→`anchor-worker`、`anchor.judge`→`anchor-judge`、`anchor.maintain`→`anchor-maintain`。

## 二、调用规则

1. **DSH 会话**：用 skill 工具按 **kebab 名**加载（`core-plan` 而非 `core.plan`）。根 AGENTS.md 的 dot 名触发表是 Reasonix 规范形，先查本表映射。
2. **Reasonix 会话**：按根 AGENTS.md 触发表用 dot 名（规范正文在 `../skills/<dot-name>/SKILL.md`）。
3. **角色技能**（scout/worker/judge）：DSH 中经 subagent 工具隔离执行——按技能正文的角色契约派发子代理（core-worker / core-judge / re-scout / recode-scout / 以及 anchor-* 角色）。
4. **正文等价**：DSH 技能正文 = Reasonix 技能正文（sync_skills.py 逐字节守护），语义等价，只有名字不同——按 kebab 名加载即是加载同一份方法论。

## 三、工具与脚本（ref_* 仅在 re-framework preset；其他会话 pwsh 直跑）

| 能力 | re-framework preset 工具 | 任何会话直接调用（pwsh） |
|------|--------------------------|--------------------------|
| 框架自检（R1-R6，spec §2.5） | `ref_manifest_validate` | `python scripts/validate_manifest.py` |
| 部署模块到项目（.reasonix/skills） | `ref_install` | `python scripts/install.py <target> --modules core,re-binary,...` |
| 并行 worker 索引合并（§5.1） | `ref_merge_index` | `python scripts/merge_index.py <project>` |
| 项目骨架初始化（.artifacts/.investigations/knowledge） | `ref_init` | （脚本内联于插件，等价目录创建） |
| 环境/技能状态 | `ref_status` | — |

**约定**：re-framework preset 会话内做框架动作**优先用 ref_* 工具**（封装了脚本路径解析与会话 cwd 语义）；其他会话直接用 pwsh 跑脚本——工具与脚本等价，不重复封装。

## 四、DSH 会话加载点（工作区 AGENTS.md）

- 工作区根 = RE-Framework：加载根 `AGENTS.md`（Reasonix 探测器，dot 名）+ 本文件（DSH 桥接，kebab 名）。
- 工作区 = 其他项目（如 CoreSwap）：项目自己的 AGENTS.md 是运行时宿主；需要 RE 方法论时按本表 kebab 名加载技能（技能用户级全局可见，无需指向本仓库）。

## 五、维护

- 技能改名/新增：改 `scripts/sync_skills.py` ADAPT 映射 + 本表 + `tests/test_manifest.py` EXPECTED。
- 工具变更：同步本表第三节；插件 schema 门禁见 `tests/check_plugin_schema.mjs`。
- Anchorlaw 版本升级核对：spec §3 同步契约 + `dsh/SYNC.md` 变更日志。
