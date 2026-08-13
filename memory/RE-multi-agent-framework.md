---
name: engineering-framework
description: 通用工程方法论框架（RE-Framework v2）——逆向/编程通用：模块化结构（core 必装 + re-binary/re-code/swe 可选）、置信度状态机、产物落盘、验证协议引用 Anchorlaw v0.15
metadata:
  type: project
---

# 通用工程方法论框架（RE-Framework v2，BitWarden 方法论 + Anchorlaw 协议）

当用户进行逆向（二进制/代码）或编程相关工作，且目标项目套用了本框架时，遵循以下模块化流程，而非传统流式对话。

**来源:** 《打破传统AI逆向的新思路：多Agent、自主管理上下文》— BitWarden, 看雪学苑 2026.06.18
**验证协议:** [Anchorlaw Protocol v0.15](https://github.com/unknowbug/anchorlaw)（协议引用，不复制）
**框架包:** RE-Framework/（AGENTS.md 入口 + skills/ + spec/ + templates/）

## 模块路由（AGENTS.md 探测器）

| 任务特征 | 模块 | 核心 skill |
|---------|------|-----------|
| .dll/.exe/汇编/IDA/Ghidra/vtable/RTTI/xref/脱壳 | re-binary | re.lift / re.classify / re.trace / re.scout |
| .jar/.class/字节码/反混淆/mapping/mod/Minecraft | re-code | recode.deobfuscate / recode.classmap / recode.behavior / recode.scout |
| 写/改/审代码、协议设计、常规开发 | swe | swe.guide → anchor.*（Anchorlaw） |
| 无法判断 | 询问用户 | — |

只加载匹配模块，不加载不匹配模块；模块可独立安装/卸载。

## 核心铁律

1. **置信度状态机**: 产出默认 `draft` → `candidate`（证据支撑）→ `confirmed`（**仅用户拍板**，AI 永不自己写）
2. **产物落盘**: `.artifacts/`（+ index.yaml）+ `.investigations/`；不许只留对话里
3. **防幻觉**: `@anchor.test` source 必填（trace/memory）；未知用 `@anchor.idk` 显式标注
4. **上下文隔离**: 大任务拆子任务，独立 investigation 目录
5. **模块边界**: 禁止跨模块引用其他领域 skill 正文

## 工作流

Phase 0 架构设计（core.plan，轻/重分档，强制）→ Phase 1 勘探（scout, subagent）→ Phase 2 分析（worker: lift/classify/deobfuscate/classmap）→ Phase 2.5 验证（Anchorlaw: 全功能 test / degraded）→ Phase 3 审查（core.judge, 只出意见）→ 用户拍板 confirmed

## 验证协议（引用 Anchorlaw）

- `@anchor.test` / `@anchor.idk`、source 规则（trace/memory/static）、staleness（90 天）、健康状态
- 噪声卡（noise_cards.json）、降级验证（uncompilable_functions.yaml）、retry cap = evidence saturation（3 轮无新数据层证据，新证据重置；工程修复不计数）
- 三语言等价: Python 装饰器 / TS JSDoc / C++ 行注释

## 知识库

- `knowledge/INDEX.md` 总入口，分析前先查
- builtin/（预置）+ discovered/（AI 自动写入，发现即写）
- **优先级: 错误 > 正确**——错误链条独立存放 `discovered/errors/`（error-<NNN>-<slug>.md），INDEX.md 置顶、详实度最高（现象→诊断→排除→发现全链条），已排除错误不删
- 条目格式: 时间/来源定位/发现阶段/置信度/如何利用

## 如何应用

1. 目标项目部署框架（复制 skills 到 `.reasonix/skills/`，按需模块）
2. 任务开始 → AGENTS.md 探测器路由模块 → core.plan 架构设计 → 用户确认后推进
3. 产物严格遵循 templates/ 的 schema，status 标记，索引维护
4. 多假设 → core.fanout 并行（.bN 候选）+ core.judge 对比 → 用户拍板
5. 中途重大发现/方向变更 → 暂停回架构设计更新，不闷头跑偏
