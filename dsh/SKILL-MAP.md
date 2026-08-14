# SKILL-MAP — DSH 会话的 RE-Framework 调用接口速查

> **为什么存在**：RE-Framework 根 `AGENTS.md`（Reasonix 探测器）用 **dot 名**引用技能（`core.plan`、`re.scout`、`anchor.*`…）；DSH 会话的技能注册名是 **kebab 名**（`core-plan`、`re-scout`、`anchor-*`…）。DSH 会话按根 AGENTS.md 触发表用 skill 工具加载 dot 名会**找不到技能**（Anchorlaw v0.18 只解决了协议层宿主契约 §16，未解决此名映射——本文件是调用接口桥接，维护者必读）。

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
