---
name: re-classify
description: Class-identify 类结构识别（re-binary）——RTTI 优先 → 用户给起点 → vtable 列虚方法 → thiscall 偏移聚类 → 方法体粗还原；产物 class.yaml
whenToUse: 二进制逆向需还原类/继承/vtable 结构时（RTTI/vtable/聚类识别）
---

# re.classify — Class-identify（L2, subprocess）

> Spec: engineering-framework-v1.md §5.2（class.yaml 通用 schema）
> Module: re-binary
> Layer: L2 (Action) — 执行动作
> Execution: subprocess（隔离）

## 触发场景

二进制逆向中需要还原类结构（继承图、vtable、成员布局、方法归属）。

## 优先级（依次递减）

1. **RTTI 优先**: 搜索 `??_R0?AV` / `??_7` / `.rdata` 中的 type_info。有 RTTI → 整套继承图、类名、虚函数表直接拿到，无需后续步骤。
2. **无 RTTI 时用户给起点**: 用户指定 ctor 或 thiscall 方法地址作为起点，从函数中提取 vtable 引用。
3. **通过 vtable 列虚方法**: 读取 vtable 数组，每槽位一个虚方法地址；粗粒度反编译确认每个地址是否为方法。
4. **thiscall 偏移聚类列非虚方法**: 搜索 vtable 基址附近的调用，按 `[this+N]` 偏移聚类得成员清单。
5. **方法体粗还原**: 汇总所有 `[this+N]` 引用，推断成员类型和语义。

## 产物

- `.artifacts/<binary>/classes/<Name>/class.yaml`（status: draft）
- 每个识别出的方法 → `methods/<name>.yaml` + 可选的 Lift 还原（re.lift）
- 更新 `.artifacts/index.yaml` 主索引

## 函数→类迁移

发现某函数实为类方法时：
1. 在 `classes/<X>/methods/` 写新产物
2. 更新 index.yaml 对应条目（kind: function → method）
3. 更新 class.yaml 方法清单
4. 删除旧 `functions/` 位置（需用户确认，见 core.version）

## 约束

- RTTI 证据与 vtable 内容记录在 class.yaml 的 members evidence 字段，禁止无证据推测成员名。
- 调用约定识别错误是常见坑：thiscall 的 this 在 rcx（x64），确认调用方传参再定签名。
