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
> 协议正文不在此处——引用 [Anchorlaw v0.6](https://github.com/unknowbug/anchorlaw)，单一事实源。

## 触发场景

任务是编程类（编写/修改/审查代码、协议设计、常规开发、测试），且不是 re-binary / re-code 逆向任务。

## 使用方式

本模块**不复制 Anchorlaw 实现**，通过两种方式引用：

### 方式1: Anchorlaw skills（安装后直接调用）

从 Anchorlaw 仓库 `.reasonix/skills/` 安装 anchor.* skill 集（`install_source` 或复制），主会话按场景调用：

| 场景 | 调用 anchor skill | 层 |
|------|------------------|-----|
| 写/审 anchor 前语义速查 | `anchor.concepts` | L0 |
| 改完代码静态审查 | `anchor.scan` | L1 |
| scanner 疑似误报 | `anchor.challenge` | L1 |
| 实现/重构公开函数后写标注 | `anchor.write` | L2 |
| 添加 anchor 后 / CI 失败验证 | `anchor.test` | L2 |
| 运行时失败 / 噪声卡积压 | `anchor.noise` | L3 |
| 不可独立编译（RE 场景） | `anchor.degrade` | L2 |

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
