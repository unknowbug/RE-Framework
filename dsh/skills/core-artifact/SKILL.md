---
name: core-artifact
description: 产物落盘规范——.artifacts/（结果+index.yaml 主索引）与 .investigations/（思维链）的目录约定、schema 速查、索引更新纪律；产物不得只留在对话里
whenToUse: 任何产物需要落盘或索引时——.artifacts/（index.yaml 主索引 + 类/方法/函数产物）与 .investigations/（思维链）的规范与格式
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

## 副作用边界与逆登记（spec §5.6，Anchorlaw v0.22 §9.8）

落盘动作本身可能是**副作用**，不只是"写出一个产物"。落盘时 MUST 判断并声明：

| 副作用类型 | 判据 | 要求 |
|---|---|---|
| **derived**（新命名产物 / 新临时目录） | 逆 = 恒等（丢弃即可） | 自动合规，无需登记 |
| **in-place**（覆盖既有日志 / **原地重建 `index.yaml`** / 改门控默认值 / 污染共享执行体） | 逆**非**恒等 | MUST 登记**可寻址的逆**（归档件路径 / 换标签后的新名 / env 还原记录）**或**显式不可逆声明及原因 |
| **界外**（写 `~/.dsh/`、生成运行环境、`.tmp`） | 宿主共享 / 无独占控制 | MUST 在产物内标注「界外副作用：<位置> \| 补偿：<动作或 idk>」 |

- **只登记不执行**：MUST NOT 自动回退——失败轮的产物是**更有价值的证据**。
- 逆指针是**独立字段**，MUST NOT 塞进 `@anchor.test` 的 `source=` 串（`source` 答"哪份记录支撑声称"，逆答"副作用如何被收容"）。
- 造一个**并不真正恢复**先前状态的逆，比诚实声明不可逆更糟（虚假声称，违反 §1.3）。
- **`index.yaml` 原地重建是高风险 in-place 副作用**：重建式写入会**静默丢弃白名单外字段**——重建前 MUST 先备份（`ref_merge_index` 已有冲突保护，但重建路径不止它一条）。
