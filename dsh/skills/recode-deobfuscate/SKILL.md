---
name: recode-deobfuscate
description: 反混淆与映射还原（re-code）——混淆字节码（ProGuard/R8/自定义）→ 语义名：映射表建立、批量重命名、语义恢复；Minecraft 场景的 mapping 工作流
whenToUse: 代码逆向需反混淆/映射还原时（ProGuard/R8/mapping/类名与方法名还原）
---

# recode.deobfuscate — 反混淆与映射还原（L2, subprocess）

> Spec: engineering-framework-v1.md §5（locator = 类全名/签名）
> Module: re-code
> Layer: L2 (Action) — 执行动作
> Execution: subprocess（隔离）

## 触发场景

- 目标是混淆代码（.jar/.class，ProGuard/R8/自定义混淆器）
- 需要建立 obfuscated ↔ deobfuscated 名称映射（如 Minecraft 的 Mojang mappings / MCP / Yarn / Fabric intermediary）
- 反编译输出是 `a.b.c.A` 这类混淆名，需要恢复语义名

## 工作流

1. **输入准备**: 反编译输出（CFR/Vineflower/JD 等）+ 现有映射（官方 mapping 文件、社区 mapping、ProGuard `mapping.txt`）
2. **映射表建立**: 构建 obfuscated → deobfuscated 映射表（类/方法/字段三级），来源标注在每条映射条目
3. **批量重命名**: 按映射表应用重命名——类、方法、字段引用**全部**同步更新（防悬挂引用）
4. **语义恢复**: 无法从映射直接得到的名称，依据使用上下文推断（字段类型、方法行为、调用关系），标注推测名
5. **一致性检查**: 重命名后无未解析引用（编译级验证）+ 映射表与产物双向可追溯

## 产物

- `.artifacts/<project>/mappings/<name>-mapping.yaml`（映射表：obfuscated / deobfuscated / source / status）
- 重命名后的类产物（class.yaml / method.yaml，locator = 类全名/签名）
- 映射无法覆盖的区域 → `@anchor.idk`（如"此字段语义未知，疑似缓存标志"）

## 约束

- 映射表条目必须有来源（官方映射 / 社区映射 / 上下文推断），推断条目标 `candidate`。
- 批量重命名后必须做**引用完整性检查**（编译或符号解析），否则视为未完成。
- Minecraft 专用：优先用官方/社区 mapping 而非自行猜测；版本间 mapping 不通用（版本号记录在产物）。
- 交付代码/映射前过 **subagent 写码强制自检清单**（spec §4.4：类型宽度/move 拷贝/异常路径/对拍点/自检声明）——类型宽度尤其注意 Java long=64 位 vs 目标语言差异。
- **order-dependence 标注**（spec §1.3）：还原/移植涉及排序/缓存/平局/tie-break/遍历序（如 Minecraft 生物群系判定平局、ThreadLocal 缓存依赖查询序列）时，@anchor 描述 MUST 标注 order-dependence + 验证「确定性 + 查询序列对齐」。
