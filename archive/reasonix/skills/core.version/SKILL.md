---
name: core.version
description: 版本管理——活跃版 .yaml / 历史 .vN / fan-out 候选 .bN 的命名与升级流程；禁止未确认删除旧产物
layer: L1
execution: inline
---

# core.version — 版本管理（L1, inline）

> Spec: engineering-framework-v1.md §7
> Layer: L1 (Static) — 静态约定
> Execution: inline

## 触发场景

- 产物需要更新/修订时（旧版改名留档）
- 多假设并行探索产出候选分支时（配合 core.fanout）
- 收尾清理、评审历史时

## 命名规则

| 后缀 | 含义 | 何时使用 |
|------|------|---------|
| `<name>.yaml` | 当前活跃版本（主文件） | 最新有效结论 |
| `<name>.vN.yaml` | 时间线历史版本 | 旧主文件升级时改名，N 递增 |
| `<name>.bN.yaml` | fan-out 候选分支 | 多假设并行探索，每假设一个 .bN |

## 升级流程

```
旧主文件改名 .vN           # 保留历史
    ↓
新候选确认为活跃            # 用户拍板后
    ↓
复制为 .yaml               # 成为主文件
```

## 约束

- **禁止在没有用户确认的情况下删除旧产物**。
- `.vN` 历史保留（审计追溯）；`.bN` 淘汰后仍保留（不删，供对比）。
- 收尾时"清理多余的候选文件"= 把 .bN 从活跃位置移出，不是删除。
- 版本变更需同步更新 `.artifacts/index.yaml` 的 entries（core.artifact 契约）。
