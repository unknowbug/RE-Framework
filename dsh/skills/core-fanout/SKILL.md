---
name: core-fanout
description: fan-out 并行调度——多互斥假设时主会话并行派多个 worker subagent 各自产出 .bN 候选，judge 对比后用户拍板；只适合互斥假设
whenToUse: 判定树分叉 ≥2 个互斥候选时 MUST 并行 fan-out（DSH 中并行派 subagent 各验一分支，产 .bN），禁止主会话逐个自推
---

# core.fanout — fan-out 并行调度（L2, inline）

> Spec: engineering-framework-v1.md §7 (Fan-out 并行)
> Layer: L2 (Action) — 执行动作（主会话调度手册）
> Execution: inline（主会话作为协调者执行；实际分析由派出的 worker subagent 隔离执行）

## 触发条件（spec §4.5 fan-out 强制触发点）

判定树分叉存在 **≥2 个互斥候选** 即触发——**MUST 并行 fan-out**，禁止主会话逐个自推（自推判断成本远高于派 worker 的隔离成本）：

| 场景 | 级别 |
|------|------|
| 多疑点冲突 / 多互斥假设并存 | **MUST** |
| 同一现象多机制候选（如"这个函数是 CRC32 还是 djb2？"） | **MUST** |
| 旧结论 vs 新证据冲突 | **MUST** |
| 子假设再分叉（候选内部 (a)/(b) 级） | **MUST** |

- ✅ 适合：互斥假设（结果只能有一个成立）
- ❌ 不适合：互补假设（应合并探索而非竞争）
- **自检提示**：主会话深钻到「第二轮仍无定论」时自查是否已分叉——是则立即 fan-out（防 -288 类多候选主会话自推深钻循环）。

## 调度流程

```
主会话（协调者）
  ├── 创建假设 A → WorkerA (subagent, 隔离) → 产物 <name>.b1.yaml
  ├── 创建假设 B → WorkerB (subagent, 隔离) → 产物 <name>.b2.yaml
  └── 创建假设 C → WorkerC (subagent, 隔离) → 产物 <name>.b3.yaml

全部完成后:
  主会话 → Judge（core.judge, subagent）对比所有 .bN → 审查意见
  用户 → 拍板 → 优胜者复制为活跃 <name>.yaml
  被淘汰的 .bN 保留备查（core.version）
```

## Worker 隔离要求

- 每个 Worker **只看自己的假设指令**，不共享其他假设的上下文（防锚定）。
- 写路径隔离：Worker 只写自己的产物文件，不交叉写入。
- 若证据同时支持多个假设 → 不强选，标 `candidate`，等更多证据。

## 汇聚完整性（本框架 §7 要求；对齐 Anchorlaw v0.22 §15.4 PI-2 的**登记状态**）

**性质声明（不得越权）**：Anchorlaw v0.22 把 PI-2 登记为 **unverified**——其前提是判据依赖图**无环**，而该性质是**假设**不是定义的可交付物（自指判据会违反它）；协议要求采用前先做一次**廉价的依赖图枚举**。本节的要求**来源于本框架自身的 §7 并发/版本纪律**（`.bN` 淘汰后仍留审计追溯），**不主张 PI-2 已被验证**，也不要求先做该枚举才执行——两者是不同的事，混同会伪造协议状态。

本框架的 **confluence 要求**（§7）——**N 个候选必须全部被"处置过"**：

- 每个 `.bN` SHOULD 带 `verdict:`（指向裁决记录）**或** `rejected_reason:` / `superseded_by:`
- 判据：`orphan_candidate = { bN | 无 verdict 且无 rejected_reason }`——**非空即列为待处置**（见下）
- 派出了 N 个 worker 却只回来 N-1 个 → 是**待处置**状态，不是"完成了"
- 被淘汰的候选**保留**（core.version：淘汰后仍留审计追溯，不删除）

> **裁决形式**：`orphan_candidate` 非空时，主会话 MUST 显式处置（补 verdict 或声明待办）——**不是静默通过**。但本要求是**框架纪律**，其证据状态是「框架自身 §7 的机械延伸」，**不是**「PI-2 已验证」（对齐 spec §8 诚实声明：不得把方向级结论当已验证公理）。
>
> 实证教训（CoreSwap #160）：**裁决的价值在执行不在打印**——只打印不退出的 gate 使 VOID 轮产物成为下一轮基底。汇聚同理：只描述"全部完成后"是**流程描述**；落到「目录可枚举判定」才是**可检验形式**。

## 输出

- 每个候选 = 独立 `.bN.yaml` 产物（含 status: draft、证据、来源）。
- 决策记录写入 `.investigations/<任务>/`（fan-out 决策 + 对比结论）。
