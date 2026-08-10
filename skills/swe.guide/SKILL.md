---
name: swe.guide
description: 编程领域入口指引（swe）——常规开发/验证/审查任务的起点：路由到 Anchorlaw 的 anchor.* skill 集与 CLI，零复制；本 skill 只指路不复制协议正文
layer: L0
execution: inline
---

# swe.guide — 编程领域入口（L0, inline）

> Module: swe
> Layer: L0 (Concepts) — 入口指引
> Execution: inline
> 协议正文不在此处——引用 [Anchorlaw v0.13](https://github.com/unknowbug/anchorlaw)，单一事实源。

## 触发场景

任务是编程类（编写/修改/审查代码、协议设计、常规开发、测试），且不是 re-binary / re-code 逆向任务。

## 使用方式

本模块**不复制 Anchorlaw 实现**，通过两种方式引用：

### 执行模式（本模块专属）：主会话为主

**编程任务 = 主会话直接闭环**（spec §4.1/§4.2）：

- 写码 / 重构 / 编译 / 运行 / 调试 / 验证全部在**主会话**内直接执行——工程迭代（改→编译→跑→修）需要即时闭环，隔离执行会阻断迭代（实战项目实证：SearchTree 移植在 subagent 沙箱无编译环境，3 版全崩）。
- **不派 subagent 做核心写码/迭代**；subagent 仅用于隔离审查（独立 code review、独立验证）。
- 与逆向路径相反：逆向是「subagent 分析 + 主会话只执行不解读」，编程是「主会话全流程 + subagent 可选审查」。

### 方式1: Anchorlaw skills（标注/扫描，主会话调用）

从 Anchorlaw 仓库 `.reasonix/skills/` 安装 anchor.* skill 集（`install_source` 或复制），主会话按场景调用：

| 场景 | 调用 anchor skill | 层/执行 |
|------|------------------|---------|
| 写/审 anchor 前语义速查 | `anchor.concepts` | L0, inline |
| 改完代码静态审查 | `anchor.scan` | L1, subprocess |
| scanner 疑似误报 | `anchor.challenge` | L1, inline |
| 实现/重构公开函数后写标注 | `anchor.write` | L2, **inline**（v0.8：主会话直接写） |
| 添加 anchor 后 / CI 失败验证 | `anchor.test` | L2, **inline**（v0.8：主会话直接跑） |
| 运行时失败 / 噪声卡积压 | `anchor.noise` | L3, inline |
| 不可独立编译（RE 场景） | `anchor.degrade` | L2, subprocess |
| 规范起草（流水线 stage 1） | `anchor.scout` | 角色, subprocess |
| 模块实施（流水线 stage 3，Worker） | `anchor.worker` | 角色, subprocess |
| 审查角色（五触发点 + 隔离验收） | `anchor.judge` | 角色, subprocess |

> **流水线（Anchorlaw v0.10/v0.11，域收窄 v0.13）**：编程是**构造型**——Judge 驱动四段流水线：`input contract（已确认需求+规范）→ implementation spec（Scout 起草）→ implementation plan → parallel implementation（Worker 并行）→ delivery`；每段以 Judge 点头终止。**v0.13 域收窄**：该构造性声明仅限 input-contract 域（§11 audit 注册）；**逆向工程明确域外**（探索型）；混合探索-构造任务（如复刻移植）按 §16.1 RE handover 标准——探索部分未收敛不得进入流水线，只为行为模型已稳定的确定子部分调用。
> **执行模式（Anchorlaw v0.8/v0.13 对齐）**：`anchor.write`/`anchor.test` 为 **inline**（收敛任务主会话直接做，与「编程=主会话为主」一致）；`anchor.scan`/`anchor.degrade` 为 subprocess；Scout/Worker/Judge 为流水线角色（subprocess）。本框架在构造域内仍保留主会话为主执行（§15.3 SHOULD 允许 host 自选；spec §4.1 两域对齐）。
> **角色（v0.10 恢复）**：`anchor.scout`/`anchor.worker` 在 v0.10 恢复为编程流水线角色（v0.8 曾移除）；`anchor.judge` 为审查角色。RE-Framework 侧用 `core.worker`/`core.judge` 承担宿主执行者职责。

### 方式2: Anchorlaw CLI（验证执行）

```bash
pip install anchorlaw anchorlaw-scanner     # 一次性安装
anchorlaw-scanner check src/                # 静态扫描（防御性模式/缺 anchor）
# @anchor.test 运行 → anchorlaw test（详见 Anchorlaw 协议 §14.4 CLI Binding）
```

## 产物

- 遵循 core.artifact（.artifacts/ + index.yaml）
- anchor 载体按 Anchorlaw §13 三语言等价：Python 装饰器 / TS JSDoc / C++ 行注释

## 约束

- 本 skill 只指路；Anchorlaw 协议正文（anchor 语义/source 规则/staleness/噪声卡）一律引用原文。
- 与 core 关系：架构设计（core.plan）、审查门（core.judge）对本模块同样适用。
