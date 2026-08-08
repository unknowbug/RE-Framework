---
name: core.knowledge
description: 知识库生长机制——builtin/discovered 两层 + INDEX.md 入口；发现可复用模式立即写入、分析前先查索引；触发条件与写入格式
layer: L1
execution: inline
---

# core.knowledge — 知识库生长（L1, inline）

> Spec: engineering-framework-v1.md §6
> Layer: L1 (Static) — 静态约定，写入/查询知识库时使用
> Execution: inline

## 触发场景

- 分析/勘探/审查任何阶段**之前**：先查 `knowledge/INDEX.md`
- 发现可复用模式/新知识：立即写入（不拖到"回头再记"）
- 还原工具（IDA F5/反编译器）出现误译：记录修正方法

## 两层结构

```
knowledge/
├── INDEX.md              # 总入口（Agent 遇到问题先查这里）
├── builtin/              # 预置知识（项目自带，一般不改）
└── discovered/           # 项目运行中 AI 自动写入
    ├── compiler-idioms.md          # 编译器/语言惯用法
    ├── f5-bugs.md                  # 还原工具误译模式及修正
    ├── algorithm-fingerprints.md   # 已确认的算法/协议指纹
    └── anti-patterns.md            # 混淆/反逆向手法
```

## 触发条件 → 写入位置

| 触发 | 写入 |
|------|------|
| 编译器/语言特有的代码生成模式 | `compiler-idioms.md` |
| 还原工具明确误译且有修正方法 | `f5-bugs.md` |
| 确认了算法/协议及其常量/特征 | `algorithm-fingerprints.md` |
| 项目特有的混淆/防御手法 | `anti-patterns.md` |
| 跨模块通用结构模式 | 新建 `<topic>.md` 或写入对应文件 |

## 写入格式（每条独立，不合并）

```markdown
## 发现 #<N>: <简短标题>

**发现时间:** <ISO日期>
**发现者:** <scout/worker/judge — 哪个阶段>
**来源定位:** <触发此发现的地址/字节码偏移/源码位置>
**置信度:** <draft | candidate | confirmed>
**module:** <core | re-binary | re-code | swe>

### 观察
<描述观察到的现象>

### 证据
- <位置>: <具体表现>

### 如何利用
- 下次遇到 <条件> → <应用方式>
```

## 约束

- 写入后**同步更新 INDEX.md**（对应分类下加一行链接）。
- 知识条目带 `module:` 字段：跨模块知识标 `core`。
- builtin/ 与 discovered/ 都没有 → 不做猜测，标注"需要查外部资料"，让用户决定。
- 与 Anchorlaw 关系：知识库内容本身不走 anchor 协议，但**知识结论的验证**走——标 draft 的条目是待验证假设。
