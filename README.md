# RE-Framework v2 — 通用工程方法论框架（逆向 + 编程，模块化）

> 基于《打破传统AI逆向的新思路：多Agent、自主管理上下文》(BitWarden, 看雪学苑 2026.06.18) 的方法论内核，
> 工程化、Skills化、SubAgents化拆分升级：**领域无关核心 + 按需加载领域模块**，从二进制逆向到代码逆向到常规编程全兼容。
> 验证协议继承 [Anchorlaw Protocol v0.6](https://github.com/unknowbug/anchorlaw)（MIT，协议引用，不复制实现）。

---

## v2 核心变化（相对 v1）

| 维度 | v1（42KB 单文件） | v2（模块化框架） |
|------|------------------|-----------------|
| 入口 | CLAUDE.md 全量加载 | AGENTS.md 探测器 → 按任务类型只加载匹配模块 |
| 领域 | 仅二进制逆向 | `core`（通用）+ `re-binary`（二进制逆向）+ `re-code`（代码逆向/Minecraft）+ `swe`（编程） |
| 验证协议 | 引用 Practify（已死链） | 协议引用 Anchorlaw v0.6（单一事实源） |
| 动态 trace | 缺失 | `re.trace` / `recode.behavior`（anchor source 数据来源） |
| 知识库 | 空壳 TODO | 真实速查条目（calling-conventions/cpp-abi/common-patterns/assembly-reference/anti-re） |
| 子代理 | 角色概念 | subagent 角色契约（scout/worker/judge，对齐 Anchorlaw §15） |

## 包结构

```
RE-Framework/
├── AGENTS.md                  # 索引式入口：任务类型探测器 + skill 触发表（替代 v1 CLAUDE.md）
├── README.md                  # 本文件
├── spec/
│   ├── engineering-framework-v1.md   # 核心协议（铁律 + 模块化接口契约 + Anchorlaw 引用）
│   └── legacy-claude-v1.md           # v1 原 42KB CLAUDE.md 归档（历史参考）
├── skills/                    # Skill 参考实现（分发到项目 .reasonix/skills/）
│   ├── core.plan|artifact|knowledge|version|fanout|judge   # 通用层（必装）
│   ├── re.lift|classify|trace|scout                        # re-binary 模块
│   ├── recode.deobfuscate|classmap|behavior|scout          # re-code 模块
│   ├── swe.guide                                           # swe 模块（→ Anchorlaw）
│   └── modules/{core,re-binary,re-code,swe}.yaml           # 模块声明（触发表/依赖/卸载保证）
├── templates/                 # 产物 schema（语言无关：地址/字节码偏移/类全名定位）
├── knowledge-builtin/         # 预置知识库（calling-conventions/cpp-abi/...）
└── memory/                    # Memory 文件（可选）
```

## 快速开始（3 步）

### 第1步：部署（按需选择模块）

```bash
# 方式A 最小（仅 core 通用层）——所有工程任务的基础
#   复制 skills/core.* + templates/ + spec/ 到目标项目

# 方式B 标准（core + 目标领域模块）
#   逆向二进制  → 再加 skills/re.* + skills/modules/re-binary.yaml
#   逆向代码    → 再加 skills/recode.* + skills/modules/re-code.yaml
#   编程        → 再加 skills/swe.guide + skills/modules/swe.yaml

# 方式C 完整（+ Anchorlaw 验证协议）
pip install anchorlaw anchorlaw-scanner
#   并从 Anchorlaw 仓库安装 anchor.* skills（.reasonix/skills/）
```

### 第2步：初始化项目骨架

在项目目录下启动，说「帮我初始化这个工程项目的基础目录结构」——自动创建 `.artifacts/`、`.investigations/`、`knowledge/` 和初始 `index.yaml`。

### 第3步：开始工作

给出任务，AGENTS.md 探测器自动路由到匹配模块（dll → re-binary；jar → re-code；写代码 → swe），走 Phase 0 架构设计后推进。

## 模块化用法（核心特性）

**只使用需要的模块**：框架是接口不是内容仓库——不装 `re-binary`，二进制逆向流程完全不加载；不装 `swe`，Anchorlaw 也不被强依赖。

```bash
# 例1: 只做代码逆向（如 Minecraft mod）
#   core + re-code → recode.deobfuscate / classmap / behavior / scout

# 例2: 只做编程
#   core + swe → swe.guide → anchor.*（Anchorlaw）

# 例3: 全都要
#   core + re-binary + re-code + swe
```

每个模块自带：skill 集 + 触发表 + 依赖声明 + 卸载保证（详见 `skills/modules/*.yaml` 与 spec §2）。

## 与 Anchorlaw 的关系

- **协议引用**：`@anchor.test` / `@anchor.idk`、source 规则、staleness、噪声卡、降级验证（uncompilable_functions.yaml / retry cap）——全部指向 [Anchorlaw v0.6](https://github.com/unknowbug/anchorlaw)，本框架不复制实现。
- **双向可用**：Anchorlaw 是语言无关的验证协议（Python/TS/C++ 三语言等价）；re-binary 走 degraded 路径，re-code / swe 走全功能路径。
- 历史渊源：v1 引用的 Practify 即 Anchorlaw 前身（仓库已 rename），本框架与 Anchorlaw 同源。

## 部署验证

启动后说「我有个 dll 想逆一下」→ 应路由到 re-binary（re.scout）；说「帮我逆一下这个 jar 的混淆映射」→ 应路由到 re-code（recode.deobfuscate）；说「帮我写个函数」→ 应路由到 swe（swe.guide）。

## 方法论来源

- 原文：《打破传统AI逆向的新思路：多Agent、自主管理上下文》（BitWarden，看雪学苑 2026.06.18）
- 验证协议：[Anchorlaw Protocol v0.6](https://github.com/unknowbug/anchorlaw)（MIT，由 Practify 更名而来）
