---
name: re.trace
description: 动态 trace 采集（re-binary）——通过调试器/追踪工具获取寄存器与内存快照，产出 anchor 的 source 数据（trace:...）；本框架 @anchor.test 的数据来源
layer: L2
execution: subprocess
---

# re.trace — 动态 trace 采集（L2, subprocess）

> Spec: engineering-framework-v1.md §1.3（防幻觉——source 必须 trace/memory）
> Module: re-binary
> Layer: L2 (Action) — 执行动作
> Execution: subprocess（隔离）

## 触发场景

- 需要为 `@anchor.test` 提供 `trace:` 类型 source 数据时
- 静态分析无法确定的行为（间接调用目标、分支覆盖、浮点精度）需要运行时观察时
- Lift 验证失败（retry cap 超限）后需要回采新证据时

## 工具链（宿主 MCP 集成）

| 工具 | 用途 | 能力 |
|------|------|------|
| IDA/Ghidra MCP | 静态+动态结合 | 反汇编、xref、trace 窗口 |
| x64dbg/Frida MCP | 动态调试 | 断点、寄存器快照、内存读写 |
| CheatEngine MCP | 内存/执行追踪 | 硬件断点、DBVM watch、结构剖析 |

> 无 MCP 时的降级：用宿主 shell 调 CLI（如 frida-trace）/ 日志注入，产出格式不变。

### 命令委托模式（subagent 沙箱无 shell 时）

分析 subagent 无 shell / 只读白名单拦截可执行程序时（spec §4.3），trace 采集走**命令委托**：

1. subagent 提交命令模板（`命令 + 参数 + 期望输出`）给主会话
2. 主会话执行，**不解读**（只执行不解读原则）
3. 原始输出落盘 `.investigations/<任务>/cmd-output/<NNN>.txt`
4. subagent 读取落盘输出并解读，转换为 trace source 数据

> 例: subagent 提交 `block_probe -biomeDump 812 73 -337` → 主会话执行落盘 → subagent 解读输出 → 产出 `source="probe:block_probe!SURFBIOME#003"`

## trace → anchor source 转换

每次观测记录后，按 Anchorlaw §5.5 格式沉淀为 source 字段：

```
trace:<binary>!<function>#<id>, offset=0x<addr>, <reg>=<val>, <mem>=<val> observed <ISO8601>
```

规则：
- 每条 `@anchor.test` 必须有 ≥1 条 trace 记录支撑
- 无法覆盖的分支 → 记录为 `@anchor.idk`（source 可标注 static）
- trace 观测必须记录偏移（观测点）与时间戳——不可凭空编造

## 产物

- `.investigations/<任务>/trace-<NNN>.md`（原始观测记录：断点位置、寄存器/内存快照、时间）
- 汇总 trace 数据 → 更新对应产物的 anchor 载体（re.lift 步骤6）

## 约束

- trace 是**证据采集**不是结论：观察到的行为变化（如分支未走通）也要记录，不掩盖。
- 动态环境差异（优化开关/ASLR）标注在观测记录中。
- 禁止用 trace 伪造覆盖：没观测到的路径就是没观测到，写 @anchor.idk。
