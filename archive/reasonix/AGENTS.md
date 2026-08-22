# RE-Framework v2 — AGENTS.md（索引式入口）

> **定位**: 通用工程方法论框架（逆向 + 编程）。本文件是**探测器 + 索引**——协议铁律正文在对应 skill 里按需加载，不在本文件常驻（对齐 Anchorlaw §14 Agent Skill Manifest + §16 Host Integration）。
> **协议**: `spec/engineering-framework-v1.md`（模块化接口契约）+ [Anchorlaw Protocol v0.18](https://github.com/unknowbug/anchorlaw)（验证协议，协议引用）。
> **旧版**: 原 42KB CLAUDE.md 已归档至 `spec/legacy-claude-v1.md`（v1 历史参考）。
> **DSH 宿主会话（MUST）**: 你是 DeepSeek Harness 环境。本探测器用 dot 名引用技能（Reasonix 规范形），**DSH 会话第一步先读 `dsh/SKILL-MAP.md`**（DSH 探测器：kebab 名路由表 + 强初始化 + Phase 0-3 流程驱动），按它执行标准流程；技能一律按 **kebab 名**加载（`core-plan` 而非 `core.plan`），工具仅 re-framework preset。

---

## 〇、强初始化纪律（每个 session 第一件事，MUST 按序执行，未经完成不得开始实际分析）

初始化三步，顺序固定，每步完成才进下一步（用户不应需要重复提醒——这是框架强制，不是自觉项）：

**STEP 1 — 读知识库**（core.knowledge，先于一切）
- [ ] 查 `knowledge/INDEX.md`（总入口，分析前必查）
- [ ] 读与任务相关的 builtin/discovered 条目（不猜，先查）
- [ ] 知识库无相关条目 → 标注"需外部资料"，让用户决定，不自行编造

**STEP 2 — 规划工作**（core.plan 架构设计）
- [ ] 跑架构设计（轻量 ≤3 要点 / 重量完整文档）
- [ ] 展示给用户确认——**未经用户确认架构，不得开始实际分析**
- [ ] 架构文档落盘 `.investigations/000-架构设计/`

**STEP 3 — 预置子角色介入点**（core.plan 模板「子角色介入点」节，随计划落盘）
- [ ] 规划**全部**子角色（scout/worker/fan-out/judge/knowledge）的介入时机，执行中不临时起意

| 子角色 | 介入时机（触发条件） | 预置方式 |
|--------|---------------------|---------|
| scout（勘探） | 「机制未明」大排查初期 MUST 勘探（禁止直接跳单点定位） | 计划 Phase 1 预置勘探点 |
| worker（分析解读） | 分析/解读/代码交付 | 按任务拆解预置 worker 项 |
| fan-out | 判定树分叉 ≥2 个互斥候选 MUST 并行（禁止主会话自推） | 计划预置分叉点 + .bN 候选 |
| judge（审查） | confirmed 前/重大转向/收尾交付 MUST；candidate 授予 SHOULD | 计划预置 judge 项（节点/级别/审查对象） |
| knowledge（落盘） | 结论性 docs/discovered 写入 MUST subagent 产出草稿 | 每 Phase 末尾预置产出者标注 |

> 三触发点（scout/fan-out/judge）+ knowledge 落盘 = spec §4.5 执行强制链；初始化即预置，执行只核对不补排。

---

## 一、任务类型探测器（模块路由）

| 任务特征 | 模块 | 加载 skill |
|---------|------|-----------|
| 输入为 `.dll/.exe/.so/.bin`、汇编/机器码；提到 IDA/Ghidra/F5/x64dbg/Frida/CheatEngine、vtable、RTTI、xref、脱壳、反调试 | **re-binary** | `re.scout`（勘探）→ `re.lift`（还原）/ `re.classify`（类）/ `re.trace`（动态证据） |
| 输入为 `.jar/.class/.java`、字节码、反混淆/mapping/ProGuard/R8、MCP/Forge/Fabric、mod 逆向、Minecraft | **re-code** | `recode.scout` → `recode.deobfuscate`（映射）/ `recode.classmap`（类层次）/ `recode.behavior`（行为验证） |
| 编写/修改/审查代码、重构、协议设计、常规开发、测试 | **swe** | `swe.guide` → Anchorlaw `anchor.*`（concepts/scan/write/test/noise） |
| 混合任务（逆向产出 → 编程复刻等） | 主模块 + 按需附加 | 各自主模块 skill |
| 无法判断 | 询问用户目标格式 | — |

**加载规则**: 模块内 skill 仍按需加载（不一次性全量）；`runAs: subagent` 的 skill 在隔离子进程执行（Anchorlaw §15）。

---

## 二、核心铁律（简版——正文在 spec §1）

1. **置信度状态机**: 任何产出默认 `draft` → 证据支撑可升 `candidate`；`confirmed` **只有用户拍板**，AI 永不自己写。审查角色只出意见不改 status。
2. **产物必须落盘**: 结果 → `.artifacts/`（+ `index.yaml` 主索引），思维链 → `.investigations/`；不许只留在对话里。
3. **防幻觉**: 每个结论要么可追溯验证，要么 `@anchor.idk` 显式标注；`@anchor.test` 的 source 必填（trace/memory，禁 static），缺失 → 审查直接驳回。
4. **模块边界**: 禁止跨模块引用其他领域模块的 skill 正文（spec §1.6）；模块可独立安装/卸载（spec §2.4）。
5. **上下文隔离**: 任务过大主动拆分子任务，每子任务独立 investigation 目录。

---

## 三、Skill 索引（manifest）

| skill | 层 | 执行 | 模块 | 职责 |
|-------|-----|------|------|------|
| `core.plan` | L0 | inline | core | 架构设计（轻/重分档） |
| `core.artifact` | L1 | inline | core | 产物落盘规范 |
| `core.knowledge` | L1 | inline | core | 知识库生长 |
| `core.version` | L1 | inline | core | 版本管理（.vN/.bN） |
| `core.fanout` | L2 | inline | core | fan-out 并行调度 |
| `core.worker` | role | subagent | core | 分析/解读角色（加载领域动作 skill） |
| `core.judge` | role | subagent | core | 审查门（只出意见） |
| `re.lift` | L2 | subprocess | re-binary | 汇编→C++ 六步还原 |
| `re.classify` | L2 | subprocess | re-binary | 类结构识别 |
| `re.trace` | L2 | subprocess | re-binary | 动态 trace 采集 |
| `re.scout` | role | subagent | re-binary | 只读勘探 |
| `recode.deobfuscate` | L2 | subprocess | re-code | 反混淆/映射 |
| `recode.classmap` | L2 | subprocess | re-code | 类层次/依赖 |
| `recode.behavior` | L2 | subprocess | re-code | 行为验证 |
| `recode.scout` | role | subagent | re-code | 只读勘探 |
| `swe.guide` | L0 | inline | swe | 编程入口（→ Anchorlaw） |

> Anchorlaw 的 `anchor.*`（concepts/scan/challenge/write/test/noise/degrade）随 swe 模块安装，见 `skills/modules/swe.yaml`。
> 模块声明（触发表/依赖/卸载保证）: `skills/modules/{core,re-binary,re-code,swe}.yaml`。

---

## 四、验证协议（引用 Anchorlaw v0.18，不自行维护）

| 接口面 | 章节 | 本框架使用 |
|--------|------|-----------|
| Claim | §13 + §5 | `@anchor.test` / `@anchor.idk`，source 规则（trace/memory/**probe** v0.7/static 仅 idk），source artifact requirement，staleness，健康状态 |
| Knowledge | §14 | 本文件 + skills/manifest（模块化按需加载） |
| Execution | §15 | subagent 角色隔离（scout/worker/judge）；**域收窄（v0.13，保留于 v0.18）**——逆向工程明确协议域外（探索型），构造域接 Anchorlaw 流水线；retry cap = **evidence saturation（v0.13）**：3 轮无新数据层证据（trace/probe）强制回数据层，新证据重置；verification termination gates + **C-gate halted escalation（v0.15）**（3 轮未满足 → halt + 人类裁决，无 Judge 预分类）；执行模式选择（收敛 inline / 发散 MAY subprocess） |
| Host | §16 | 本文件是宿主集成点：触发表 / confirm hook / 产物契约；hosts 自供执行者（本框架用 core.worker/core.judge）；**input-contract 确认标准（v0.14 泛化）**——语义收敛才交接 confirmed input contract（协议中立，不点名 RE framework）；输入契约 = 需求 + 技术约束规范（架构在 stage 1），三协议独立可操作 |

> **升级检查**：Anchorlaw 发新版本后，`git grep 'v0\.[0-9]'` 本仓库核对版本号与引用条款（同步契约详见 spec §3）。当前基线 v0.18。

---

## 五、工作流速览

```
Phase 0 架构设计（core.plan，强制）→ Phase 1 勘探（scout）→ Phase 2 分析（worker）
→ Phase 2.5 验证（Anchorlaw：全功能 test / degraded 声明）→ Phase 3 审查（core.judge）
→ 用户拍板 confirmed → 归档
```

人工 HOOK 点: 架构批准 / 重大方向变更 / 多假设竞争（fan-out）/ confirmed 授予。

**执行强制链**（spec §4.5）: judge 触发点——confirmed 授予前 MUST judge、重大转向（结案重开/根因定论/范围决策）MUST judge、candidate 授予 SHOULD judge、收尾交付 MUST judge（三源核对）；judge 随 todo 计划预置。「编程=主会话直接闭环」不豁免 judge。scout 触发——「机制未明」大排查初期 MUST 勘探（禁止直接跳单点定位）。fan-out 触发——判定树分叉 ≥2 个互斥候选 MUST 并行 fan-out（禁止主会话逐个自推，不因候选小自推）。knowledge 触发——结论性 docs/discovered 写入前 MUST subagent 产出草稿（core.worker），主会话只应用+验证；过程性记录主会话可写。四触发点并列独立：scout（勘探）→ fan-out（分叉）→ judge（审查）→ knowledge（落盘）。

---

## 六、部署

方式A 最小（仅 core）: 复制 `skills/core.*` 到项目 `.reasonix/skills/`。
方式B 标准（core + 所需领域模块）: 复制 `skills/` 下需要的模块 + `templates/` + `spec/`。
方式C 完整（+ Anchorlaw）: 方式B + `pip install anchorlaw anchorlaw-scanner` + 安装 anchor.* skills。

详见 `README.md`。
