---
name: re.lift
description: Lift 高精度还原（re-binary）——汇编→C++ 六步流程：骨架/机械翻译/签名/优化/语义折叠/anchor 提取；禁止直接信任单一反编译输出（如 IDA F5）
layer: L2
execution: subprocess
---

# re.lift — Lift 高精度还原（L2, subprocess）

> Spec: engineering-framework-v1.md §1.3（防幻觉）, Anchorlaw §9（degraded verification）
> Module: re-binary
> Layer: L2 (Action) — 执行动作
> Execution: subprocess（隔离）

## 触发场景

二进制逆向中需要高精度还原某函数/方法（不允许直接把 F5 反编译输出当答案时）。

## 六步流程

**步骤1 — 骨架还原**: 识别控制流壳（if/while/for/switch/do-while），条件和函数体用占位符。重点：反编译器常把 do-while 还原成 while，需回汇编确认。

**步骤2 — 逐行机械翻译**: asm → C 伪代码，变量名直接用寄存器名，不做任何优化。每行汇编对应一行 C 注释。

**步骤3 — 签名草稿**: 从调用方视角推断调用约定（cdecl/stdcall/fastcall/thiscall）、参数个数类型、返回值。标记待修正。

**步骤4 — 优化**: 约定寄存器识别 / 折叠中间寄存器 / 内存操作分类（栈变量 vs 堆对象 vs 全局）/ lea 指令处理（取地址 vs 算术）。**同步提取测试向量**（含数据来源——强制字段）：
- 来源格式: `trace:<binary>!<function>#<id>, offset=0x<addr>, <reg>=<val> observed <ISO时间>`
- 记录无法覆盖的分支 → 将成为 @anchor.idk

**步骤5 — 语义折叠**: 识别算法模式（CRC/哈希/加密/压缩等）/ 改有意义变量名 / 修正签名 / 标注置信度低的区域。

**步骤6 — anchor 载体**: 按 [Anchorlaw v0.18](https://github.com/unknowbug/anchorlaw) 协议产出 `@anchor.test` / `@anchor.idk`：
- 每个明确可验证的输入→输出对 → `@anchor.test`（source 必填，trace/memory）
- 每个无法确定的行为边界 → `@anchor.idk`（具体到可验证条件，source 可 static）
- 缺 source 的 @anchor.test → 视为凭空编造，judge 直接驳回
- **验证记录落盘**（spec §1.3）：source 引用的验证记录同步落盘 `.investigations/<任务>/regression-record.md`（条目 + 命令 + 输出摘要）——让 judge 能核对「验证真的跑过」，而不是事后补证
- **order-dependence 标注**（spec §1.3）：还原点涉及排序/缓存/平局/tie-break/遍历序时，@anchor 描述 **MUST 标注 order-dependence**，并验证「确定性 + 与参照实现查询序列对齐」（实战项目实证：C++ 线性 find 平局取首个 vs Java 树序遍历取另一值，且平局结果依赖查询序列）

## 产物

- `.artifacts/<binary>/classes|functions/.../<name>.cpp`（还原源码，status: draft）
- 对应的 anchor 载体文件（Python `_anchors.py` / 等效）
- 无法独立编译时 → `.artifacts/uncompilable_functions.yaml` 声明（Anchorlaw §9.3）

## 约束

- 产物默认 `draft`；验证走 Anchorlaw（全功能 test / degraded 声明）。
- **retry cap 区分**（spec §4）：≤3 次只约束**逆向假设的验证轮次**（同一假设验证失败 → 换方向/回勘探取新 trace）；**工程修复/代码迭代不计数**（可迭代至正确）。
- 交付代码前过 **subagent 写码强制自检清单**（spec §4.4：类型宽度/move 拷贝/异常路径/对拍点/自检声明），结果附在交付物。
- 不确定部分显式标注 `@anchor.idk`，不许闷在注释里。
