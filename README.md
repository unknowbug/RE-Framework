# RE-Framework v2 — 通用工程方法论框架（逆向 + 编程，模块化）

> **[English](README_EN.md) | 中文**

> 基于《打破传统AI逆向的新思路：多Agent、自主管理上下文》(BitWarden, 看雪学苑 2026.06.18) 的方法论内核，
> 工程化、Skills化、SubAgents化拆分升级：**领域无关核心 + 按需加载领域模块**，从二进制逆向到代码逆向到常规编程全兼容。
> 验证协议继承 [Anchorlaw Protocol v0.17](https://github.com/unknowbug/anchorlaw)（MIT，协议引用，不复制实现）。
> **双宿主支持（v2.1）**：Reasonix（`.reasonix/skills/` 部署）+ **DeepSeek Harness**（`dsh/` 子树，re-framework preset）。

---

## v2 核心变化（相对 v1）

| 维度 | v1（42KB 单文件） | v2（模块化框架） |
|------|------------------|-----------------|
| 入口 | CLAUDE.md 全量加载 | AGENTS.md 探测器 → 按任务类型只加载匹配模块 |
| 领域 | 仅二进制逆向 | `core`（通用）+ `re-binary`（二进制逆向）+ `re-code`（代码逆向/Minecraft）+ `swe`（编程） |
| 验证协议 | 引用 Practify（已死链） | 协议引用 Anchorlaw v0.17（单一事实源） |
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
├── scripts/                   # 工程外壳
│   ├── validate_manifest.py   # manifest 校验器（spec §2.5 R1-R6 实现守护）
│   └── install.py             # 安装/升级/卸载器（版本戳追踪）
├── skills/                    # Skill 参考实现（分发到项目 .reasonix/skills/）
│   ├── core.plan|artifact|knowledge|version|fanout|judge   # 通用层（必装）
│   ├── re.lift|classify|trace|scout                        # re-binary 模块
│   ├── recode.deobfuscate|classmap|behavior|scout          # re-code 模块
│   ├── swe.guide                                           # swe 模块（→ Anchorlaw）
│   └── modules/{core,re-binary,re-code,swe}.yaml           # 模块声明（触发表/依赖/卸载保证）
├── templates/                 # 产物 schema（语言无关：地址/字节码偏移/类全名定位）
├── knowledge-builtin/         # 预置知识库（calling-conventions/cpp-abi/...）
├── memory/                    # Memory 文件（可选）
└── dsh/                       # DSH 宿主适配层（DeepSeek Harness：17 技能 + 5 工具 + re-framework preset + 维护脚本）
```

## 快速开始（3 步）

### 第1步：部署（按需选择模块）

推荐用安装器（自动复制 + 版本戳追踪 + 可卸载）：

```bash
# 方式A 最小（仅 core 通用层）——所有工程任务的基础
python RE-Framework/scripts/install.py <你的项目目录> --modules core

# 方式B 标准（core + 目标领域模块）
python RE-Framework/scripts/install.py <你的项目目录> --modules core,re-binary   # 逆向二进制
python RE-Framework/scripts/install.py <你的项目目录> --modules core,re-code     # 逆向代码/Minecraft
python RE-Framework/scripts/install.py <你的项目目录> --modules core,swe         # 编程

# 方式C 完整（+ Anchorlaw 验证协议）
python RE-Framework/scripts/install.py <你的项目目录> --modules core,re-binary,re-code,swe --docs
pip install anchorlaw anchorlaw-scanner
#   并从 Anchorlaw 仓库安装 anchor.* skills（.reasonix/skills/）

# 升级: 重新运行 install.py（检测版本戳提示覆盖）
# 卸载: python RE-Framework/scripts/install.py <你的项目目录> --uninstall
# 校验: python RE-Framework/scripts/validate_manifest.py
```

也可手动复制 `skills/` 下需要的模块到项目 `.reasonix/skills/`（无版本追踪，不推荐）。

### 方式D：DSH（DeepSeek Harness）宿主（v2.1 起）

```powershell
# 1. 安装 re-framework preset 到 DSH 运行时（技能 preset 内嵌，不污染其它会话）
pwsh dsh/scripts/install.ps1

# 2. 新建会话选择 re-framework preset，工作目录指向本仓库根
#    → 17 个 ref-* 技能 + 5 个 ref_* 工具（status/validate/install/merge-index/init）
#    + Phase 0-3 工作流与执行强制链（scout/fan-out/judge/knowledge）人格

# 3. 自检（工具链 / 技能 manifest 正文零漂移 / 框架自扫 R1-R6 / 安装产物）
pwsh dsh/scripts/selfcheck.ps1
```

详见 `dsh/README.md`（事实源与同步纪律见 `dsh/AGENTS.md`）。

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

- **协议引用**：`@anchor.test` / `@anchor.idk`、source 规则、staleness、噪声卡、降级验证（uncompilable_functions.yaml / retry cap）——全部指向 [Anchorlaw v0.17](https://github.com/unknowbug/anchorlaw)，本框架不复制实现。
- **双向可用**：Anchorlaw 是语言无关的验证协议（Python/TS/C++/Go/Java 注释类语言）；re-binary 走 degraded 路径，re-code / swe 走全功能路径。
- **DSH 侧同步**：`dsh/` 适配层同步引用 v0.17，正文零漂移由 `sync_skills.py` + `tests/test_manifest.py` 守护。
- 历史渊源：v1 引用的 Practify 即 Anchorlaw 前身（仓库已 rename），本框架与 Anchorlaw 同源；v0.17 变更含「§12 challenge（Reasonix/Go audit）」回流（parse-error 分类修正 + 注释类语言降级），详见 spec §3 同步契约。

## 部署验证

启动后说「我有个 dll 想逆一下」→ 应路由到 re-binary（re.scout）；说「帮我逆一下这个 jar 的混淆映射」→ 应路由到 re-code（recode.deobfuscate）；说「帮我写个函数」→ 应路由到 swe（swe.guide）。

## 更新记录

| 版本 | 日期 | 内容 |
|------|------|------|
| v2.1 | 2026-08-14 | **DSH 宿主适配层（新增 `dsh/` 子树）**：17 个 ref-* 技能（16 个正文零漂移适配 + ref-maintain 维护技能）+ 5 个 ref_* 工具 + `re-framework` agent preset（Phase 0-3 工作流 + 执行强制链人格），Reasonix 侧零改动双宿主共存；**Anchorlaw 引用升级 v0.15 → v0.17**（§5/§9/§12/§13/§14/§15/§16 条款核对全部保留；Go/Java 注释类语言注册、Rust 明确不支持、parse-error 标记、注释类语言降级仅注解提取、P7-P10 可选模式，详见 spec §3）；错误账本知识机制（错误 > 正确 优先级，`discovered/errors/` 独立存放） |
| v2.0 | 2026-08 | 模块化重构：core + re-binary + re-code + swe 四模块、AGENTS.md 探测器、Anchorlaw 协议引用（见上表 v2 核心变化） |
| v1.0 | 2026-06 | 单文件 42KB CLAUDE.md（BitWarden 方法论）→ 归档 `spec/legacy-claude-v1.md` |

## 方法论来源

- 原文：《打破传统AI逆向的新思路：多Agent、自主管理上下文》（BitWarden，看雪学苑 2026.06.18）
- 验证协议：[Anchorlaw Protocol v0.17](https://github.com/unknowbug/anchorlaw)（MIT，由 Practify 更名而来）
