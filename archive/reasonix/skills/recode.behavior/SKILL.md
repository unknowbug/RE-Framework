---
name: recode.behavior
description: 行为验证（re-code）——代码逆向的运行时证据采集：日志/hook/测试执行 → anchor 的 behavior source 数据；与 re-binary 的 re.trace 对应
layer: L2
execution: subprocess
---

# recode.behavior — 行为验证（L2, subprocess）

> Spec: engineering-framework-v1.md §1.3（防幻觉——source 必须可追溯）
> Module: re-code
> Layer: L2 (Action) — 执行动作
> Execution: subprocess（隔离）

## 触发场景

- 需要为 `@anchor.test` 提供运行时证据（代码逆向的 trace 等价物）
- 静态读码无法确定的行为（分支条件、异常路径、时序依赖）
- 反混淆/还原结论需要行为验证支撑

## 证据采集方式

| 方式 | 用途 | 示例 |
|------|------|------|
| 日志/hook | 观测方法入参出参、调用顺序 | 注入日志探针、AOP hook |
| 测试执行 | 可编译场景的直接验证 | 单元测试跑 @anchor.test |
| 运行时工具 | 字节码级观测 | JVM 调试器、BTrace/Arthas、Frida（Android） |
| mod 运行环境 | Minecraft 场景 | 游戏内行为观测、事件断点 |

### 命令委托模式（subagent 沙箱无 shell 时）

re-code 分析 subagent 无执行环境时（spec §4.3），行为采集走**命令委托**：

1. subagent 提交命令模板（如 gradle 测试命令、日志采集脚本）给主会话
2. 主会话执行，**不解读**（只执行不解读原则）
3. 原始输出落盘 `.investigations/<任务>/cmd-output/<NNN>.txt`
4. subagent 读取落盘输出并解读，转换为 behavior source 数据

## behavior source 格式

代码逆向的 trace 数据按 Anchorlaw §5.5 格式沉淀，载体标注 `behavior`（归入 trace 类，注明观测方式）：

```
behavior:<class>.<method>#<id>, input=<args>, output=<result> observed <ISO8601>
```

规则（与 re.trace 一致）：
- 每条 `@anchor.test` 必须有 ≥1 条行为记录支撑
- 无法覆盖的路径 → `@anchor.idk`
- 观测必须记录输入/输出/时间——不可凭空编造

## 产物

- `.investigations/<任务>/behavior-<NNN>.md`（原始观测：方法/输入/输出/环境）
- 汇总 → 更新对应产物的 anchor 载体

## 约束

- 行为观测是证据不是结论；异常行为（未按预期走）也要记录。
- 环境差异（游戏版本/mod 加载顺序/平台）标注在观测记录中。
- 可编译产物优先走 Anchorlaw 全功能验证（test 直接跑），行为观测用于覆盖编译测试覆盖不到的场景。
