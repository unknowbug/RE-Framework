---
name: core.plan
description: 架构设计（Phase 0 强制前置）——轻量/重量分档决策树、人工 HOOK 点、架构变更纪律；任何工程任务开始前必须先调用本 skill
layer: L0
execution: inline
---

# core.plan — 架构设计（L0, inline）

> Spec: engineering-framework-v1.md §4 (Phase 0)
> Layer: L0 (Concepts) — 决策参考手册
> Execution: inline（主会话内执行，产出架构文档）

## 触发场景

任何工程任务（re-binary / re-code / swe 所有模块）开始实际分析**之前**，必须先过本 skill。

## 决策树

```
用户给出任务
    │
    ├── 轻量判断: 单一函数/小范围/路径明确?
    │   └── YES → 轻量模式:
    │       1. 生成简版架构计划（≤3 个要点）
    │       2. 展示给用户确认
    │       3. 用户点头后直接执行
    │
    └── 重量判断: 多目标/大范围/目标模糊/类层次复杂?
        └── YES → 重量模式:
            1. 与用户讨论: 任务拆解 / 角色分配 / 并行策略 / 人工 HOOK 点
            2. 产出完整架构文档（见下）
            3. 用户批准后才开始执行
```

## 架构文档模板

### 轻量（.investigations/000-架构设计/架构计划.md）

```markdown
---
编号: 000
任务: <一句话描述>
任务类型: <算法还原 | 协议分析 | 定位 | 重构 | 验证 | ...>
模式档位: 轻量
---
## 范围（含明确不做什么）
## 任务拆解（子任务 → 预期产物）
## 验证方式
## judge 预置            # spec §4.5 执行强制链：计划阶段就排 judge 项
  - 收尾交付 MUST judge（三源核对）
  - 各阶段结论 candidate 授予 SHOULD judge
## fan-out 预置          # spec §4.5：多假设场景计划阶段排 fan-out 项
  - 判定树分叉 ≥2 互斥候选 MUST fan-out（.bN 并行），禁止主会话自推
## 知识库更新            # spec §4.5 第四条：每 Phase 末尾的知识库步骤标注产出者
  - 结论性 docs/discovered 写入: subagent 产出草稿（core.worker）+ 主会话应用验证
## 子角色介入点          # 强初始化 STEP 3：全部子角色介入时机预置，执行只核对不补排
  - scout: <机制未明勘探? 是/否 — 是则 Phase 1 勘探（管线地图）>
  - worker: <哪些子任务需要分析解读/代码交付>
  - fan-out: <潜在分叉点: 无 / 列举互斥假设>
  - judge: <收尾 MUST + candidate 授予 SHOULD>
  - knowledge: <结论性落盘 MUST subagent 产出>
```

### 重量（.investigations/000-架构设计/架构设计.md）

```markdown
---
编号: 000
任务: <一句话描述>
任务类型: <...>
模式档位: 重量
状态: 待批准
---
## 1. 全局视图（目标/范围/排除项）
## 2. 角色分配（scout/worker/judge × 子任务）
## 3. 任务拆解 & 依赖图（Phase → 任务 → 依赖）
## 4. 并行执行计划（第一波/第二波...）
## 5. 人工决策 HOOK 点（节点/触发条件/决策内容）
## 6. 风险 & 回退
## 7. judge 步骤预置          # spec §4.5：随计划排 judge 项，不是事后补
   - 节点: <结论/产物> | 级别: MUST/SHOULD | 审查对象: <快照/git diff/验证记录>
   - 节点: 收尾交付 | MUST | 三源核对
## 8. fan-out 步骤预置         # spec §4.5：多假设分叉场景随计划排 fan-out 项
   - 节点: <分叉点> | 候选: <互斥假设 a/b/c> | .bN 并行 | 禁止主会话自推
## 9. 知识库更新               # spec §4.5 第四条：每 Phase 末尾知识库步骤标注产出者
   - 结论性 docs/discovered: subagent 产出草稿（core.worker）+ 主会话应用验证
## 10. 子角色介入点（全部预置，执行不临时起意）   # 强初始化 STEP 3
   - scout:  节点 <X> | 触发: 机制未明勘探 | 产物: .investigations 管线地图
   - worker: 节点 <Y> | 触发: 分析解读/代码交付 | 产物: .artifacts draft
   - fan-out: 节点 <Z> | 候选: <互斥假设 a/b/c> | MUST 并行 .bN
   - judge:  节点 <W> | 级别: MUST/SHOULD | 审查对象: <快照/git diff/验证记录>
   - knowledge: 节点 <V> | 结论性落盘 | subagent 产出 + 主会话应用验证
```

## 约束

- **未经用户确认架构，不得开始实际分析。**
- 执行中发现架构不适用 → **暂停**，回本 skill 更新架构文档，不闷头跑偏。
- 小的方向微调（不改变依赖关系）不需要重新架构；新增范围/目标 → 必须重新评估。
- 探测路由（re-binary / re-code / swe）由 AGENTS.md 探测器完成；本 skill 只负责任务内架构。
