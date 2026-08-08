# 常见反逆向手法（识别与绕过）

> 用途: Scout 阶段发现异常（花指令/壳/自解密）时查阅。
> 模块: core（re-binary 使用）

## 花指令（Junk Code）

- **垃圾字节**: 真实指令间插入不执行的字节（`jmp` 跳过、`call` 后跟垃圾）
- **不透明谓词**: 恒真/恒假条件（`test eax,eax; jz` 但 eax 已知非零）包裹死代码
- **死代码**: 永远不会执行但混淆反汇编器的指令
- 识别: 反汇编出现跳到指令中间（`jmp +1`）、异常的分支不落点、大量未引用指令
- 绕过: 用线性扫描反汇编器（Ghidra 较 IDA 稳健）、跟随实际控制流重写、去花脚本（识别 jmp 垃圾模式）

## 壳（Packer）

| 壳 | 入口特征 |
|----|---------|
| UPX | 段名 `.UPX0/.UPX1`，入口 pushad/popad 模式，压缩段 |
| ASPack | 段名 `.aspack`，入口 stub 循环解压 |
| VMProtect | 大量虚拟指令（无 x86 语义的 handler 循环），`.vmp0/.vmp1` 段 |
| Themida | `.themida` 段，多态 stub + 反调试 |

- 通用识别: 入口点（EP）不在正常代码区、段权限 RWX、导入表极小（IAT 被重定向）、EP 处是解压循环
- 绕过: 转储（dump）OEP（内存中解压后 dump）+ 修复 IAT；或用执行追踪（re.trace）记录解压后行为

## 字符串加密

- **运行时解密**: 字符串表在 `.rdata/.data` 呈乱码，DllMain/初始化函数中逐段 XOR/解码
- 识别: 大量"乱码"字符串 + 初始化函数中有循环 XOR（`xor byte ptr [reg+idx], imm8`）
- 绕过: 动态调试在解密后下断点 dump（re.trace）；或写脚本静态模拟解密逻辑
- **哈希字符串**: 不存明文，运行时计算哈希后比较（API 名用 `GetProcAddress` + 哈希查表）——识别: 调用方比较常量哈希而非字符串

## 控制流平坦化（OLLVM 风格）

- **特征**: 基本块被压平为一个分发器循环：状态变量 + switch 分发 + 大量 `mov [rsp+X], state; jmp dispatcher`
- 识别: 函数极长、大量基本块跳转到同一 dispatcher、每个块入口先更新状态变量
- 绕过: 符号执行（angr 等）重建 CFG；人工恢复：把状态变量赋值映射回原分支

## 反调试

| 技术 | 特征 | 绕过 |
|------|------|------|
| `IsDebuggerPresent` | 导入表含该 API；`test eax,eax; jnz` | patch 返回值/调用点 |
| `NtGlobalFlag` | 读 PEB+0x68 检查 0x70 掩码（`mov eax,gs:[0x60]; mov eax,[eax+0x68]`） | 修改标志/patch 比较 |
| `PEB.BeingDebugged` | PEB+0x02 读取 | patch |
| 时间差检测 | 连续 `rdtsc` 或 `GetTickCount` 差值超阈值 | patch/跳过 |
| 硬件断点检测 | 读 `Dr0-Dr3`（`GetThreadContext`） | 用软件断点 |
| 自调试/反附加 | `CreateProcess` 带 DEBUG_PROCESS 标志 | patch |

## 导入表混淆

- **动态解析**: 不依赖 IAT——运行时 `LoadLibrary/GetProcAddress`（API 名常被加密或哈希）
- 识别: 函数内 `LoadLibraryA` + 字符串/哈希查找 + `call rax`
- 绕过: 在解析调用点下断点记录解析结果（re.trace）；恢复 IAT 时把这些调用识别为 API

## 虚拟机保护（高级）

- **特征**: vm_entry 跳板（保存寄存器到 VM 上下文）→ handler 循环（每个虚拟指令一个 handler）→ vm_exit（恢复上下文返回）
- 识别: 巨大的 handler 表 + 寄存器保存/恢复块（大量 `mov [ctx+off], reg`）
- 绕过（实践中难）: 记录 handler 语义（DBVM watch / 执行 trace）重建虚拟指令流；或纯行为分析（不还原 VM，只看输入输出）

## 反虚拟化/反沙箱（常见于恶意样本与商业保护）

- 检测 VM 指令（`in al,dx` / hypervisor 特征）、沙箱痕迹（驱动名、进程名）、交互性（等待用户输入）
- 识别: 大量环境探测 API（`GetSystemFirmwareTable`、`cpuid` 检查）
- 绕过: 环境仿真匹配真实环境；patch 探测分支

## 方法论提醒

- 先判断壳/加密层**再**进入详细分析（re.scout 应把"是否有保护层"列为首要检查项）
- 识别到的手法立即写入 knowledge/discovered/anti-patterns.md（core.knowledge）
- 花指令/平坦化严重影响静态分析时 → 用动态 trace（re.trace）绕开静态混淆
