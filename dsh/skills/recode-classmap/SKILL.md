---
name: recode-classmap
description: 类层次与依赖还原（re-code）——继承/接口/组合图、事件系统（订阅-发布）、调用依赖追踪；产物 class.yaml（locator=类全名）与依赖图
whenToUse: 代码逆向需梳理类层次/依赖图时（类关系/继承/引用结构还原）
---

# recode.classmap — 类层次与依赖还原（L2, subprocess）

> Spec: engineering-framework-v1.md §5.2（class.yaml 通用 schema）
> Module: re-code
> Layer: L2 (Action) — 执行动作
> Execution: subprocess（隔离）

## 触发场景

- 需要理解目标代码的整体结构（类图、包结构、模块边界）
- 需要定位某个行为的实现链（事件 → 处理器 → 业务逻辑）
- Minecraft 场景：理解 mod 与游戏核心的交互面、事件订阅关系

## 工作流

1. **类图构建**: 继承/接口实现/组合关系 → 层次图（工具：javap、IDE 结构导出、静态分析器）
2. **事件系统梳理**: 订阅-发布关系（事件类 → 订阅者 → 触发点），记录事件名与处理链
3. **依赖追踪**: 方法调用链、字段引用图——从目标入口下钻到实现
4. **聚类与标注**: 按职责聚类（框架类/工具类/业务类/数据类），每类标推测职责
5. **产出**: class.yaml（members 含证据）+ 依赖图文档

## 产物

- `.artifacts/<project>/classes/<Name>/class.yaml`（status: draft，locator = 类全名）
- `.investigations/<任务>/classmap.md`（类图文字描述：层次/事件/依赖链）
- 方法级细节 → `methods/<name>.yaml`（配合 Anchorlaw anchor 载体）

## 约束

- 成员/方法归属必须有源码或字节码证据（evidence 字段），禁止凭空推测。
- 事件系统梳理要区分「订阅注册点」与「触发点」，两者都要有定位。
- 与 re-binary 的 re.classify 区别：本 skill 面向字节码/源码（类全名定位），re.classify 面向机器码（地址定位）——产物 schema 相同（core 语言无关设计）。
