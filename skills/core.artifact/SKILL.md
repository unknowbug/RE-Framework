---
name: core.artifact
description: 产物落盘规范——.artifacts/（结果+index.yaml 主索引）与 .investigations/（思维链）的目录约定、schema 速查、索引更新纪律；产物不得只留在对话里
layer: L1
execution: inline
---

# core.artifact — 产物落盘（L1, inline）

> Spec: engineering-framework-v1.md §1.2, §5
> Layer: L1 (Static) — 静态约定，审查产物格式时使用
> Execution: inline

## 触发场景

- worker/scout 产出分析结果需要落盘时
- judge 审查产物是否满足落盘契约时
- 任何"结果要不要写文件"的判断

## 目录约定

```
<project>/
├── .artifacts/              # 分析结果（模块通用，按产物类型组织）
│   ├── index.yaml           # 主索引（必须维护，spec §5.1）
│   ├── classes/<Name>/      # 类产物（class.yaml + methods/）
│   │   └── methods/<name>.yaml
│   ├── functions/           # 未归类函数
│   ├── cross_refs/          # 跨引用（xref_<NNN>.yaml）
│   ├── types/               # 提取的结构体/类型定义
│   └── uncompilable_functions.yaml   # 降级声明（spec §5.5）
└── .investigations/         # 思维链（任务简报/假设/发现/结论）
    └── <任务>/
        ├── 任务.md
        ├── 假设*.md / 发现*.md
        ├── cmd-output/           # 命令委托的原始输出落盘（spec §4.3）
        │   └── <NNN>.txt
        └── 结论.md
```

## 产物契约（对齐 Anchorlaw §15.2）

每次 worker/scout/judge 产出必须同时满足：
1. **落盘**: 产物写入 `.artifacts/` 或 `.investigations/`
2. **索引更新**: 新产物同步写入 `index.yaml`（`entries` 加一行）
3. **状态标记**: `status: draft | candidate`（AI 绝不写 confirmed）

三者缺一 = 产物契约未满足，judge 驳回。

## schema 速查（完整版见 spec §5）

- **index.yaml**: `schema_version / project / module / entries[]`（entries 含 id/path/kind/status）
- **class.yaml**: `class_name / locator / status / members[] / methods[]`
- **method/function.yaml**: `name / locator / status / signature / return_type / anchor_path / uncertain_areas[] / dependencies[]`
- **xref.yaml**: `编号 / 状态 / 从 / 到 / 关系类型 / 证据`

locator 语言无关：虚拟地址（re-binary）/ 字节码偏移或类全名（re-code）。

## 约束

- 分析结果、思维链**不许只留在对话里**。
- 产物归属模块记录在 index.yaml 的 `module` 字段——模块卸载不影响已落盘产物。
- 删除/移动产物需用户确认（见 core.version）。
