# x64 汇编参考

> 用途: Lift（步骤1-4）与 Scout 阶段的指令模式识别。
> 模块: core（re-binary 使用）

## lea 指令歧义（高频坑）

x64 下 lea 两种完全不同的用途：
1. **取地址**: `lea rax, [rip+0x12345]` — 加载全局变量/常量地址（RIP 相对）
2. **乘加运算**: `lea rax, [rdx+rdx*4]` — 等价 rax = rdx*5（纯算术）

区分方法:
- 含 `rip` 相对寻址 → 取地址
- 源寄存器是数据寄存器（非 rbp/rsp/rip）→ 可能是算术
- 结合上下文: 后面是 dereference → 取地址；后面是比较/返回 → 算术
- 常见乘法捷径: `lea rax,[rax+rax*8]` = *9，`lea rax,[rax+rax*4]` = *5，`lea rax,[rcx+rcx*2]` = *3

## 间接调用模式

| 模式 | 含义 |
|------|------|
| `call [rax+8]` | 虚函数调用（rax = 对象，+8 = vtable 槽位偏移） |
| `call [reg]` / `call qword ptr [reg]` | 函数指针调用 |
| `call rax`（寄存器直接） | 尾调用/回调（值来自之前的 mov 或函数返回值） |
| `jmp [rax+N]` | thunk 跳转 / 虚函数尾调用 |

虚调用识别: `mov rax,[rcx]`（取 vfptr）→ `call [rax+N]`；N 除以 8 得槽位序号。

## 栈帧识别

- 传统帧: `push rbp; mov rbp,rsp; sub rsp,N`（调试/老代码）
- 现代 MSVC: 无 rbp——`sub rsp,N` 直接开帧，用 `[rsp+X]` 访问局部（N 常含 32 阴影空间对齐）
- 栈变量: `mov [rsp+X]` / `lea rax,[rsp+X]`
- 参数（溢出区）: `[rsp+0x28+]`（return addr 之上 + 阴影空间）
- 帧指针省略（FPO）判断: 函数无 `push rbp` 但频繁用 `[rsp+N]` → FPO

## 常见编译器优化模式

- **除法乘法逆元**: `mov rax,rcx; imul rax,<magic>; shr rax,<n>` — 整数除法被替换为乘法+移位（magic = 2^k/除数）。识别: imul 后紧跟 shr/sar
- **模运算**: 逆元 + 乘 + 减（x - floor(x/d)*d）
- **循环展开**: 连续重复同一组指令多次 + 剩余项处理（余数循环）
- **尾调用优化**: `jmp` 代替 `call+ret`（栈复用）
- **强度削减**: 循环内 `lea` 代替乘法；指针步进
- **位域**: `shr/shl/and` 组合读写位域

## switch 跳转表

```
cmp edx, <case_count-1>
ja default_label           ; 超出范围
lea rax, [rip+jumptable]
movsxd rax, dword ptr [rax+rdx*4]   ; 取表项
add rax, jumptable_base
jmp rax
```
- 密集 case → 跳转表（表中是偏移或地址）；稀疏 case → 二分比较链（`cmp; jl/jg` 树）
- 识别: 相对基址的 `[table+idx*4]` + `jmp rax`

## SEH/异常处理特征

- x64: 无栈展开指令在函数内——`RUNTIME_FUNCTION`/`.pdata` 描述，函数开头无异常指令
- 识别异常函数: `.pdata` 段存在 + `__CxxFrameHandler` 引用（`??_L`/`__CxxFrameHandler4`）
- 有 `__try/__except` 的函数通常引用 `__C_specific_handler` 或 `__CxxFrameHandler`

## TLS 访问模式

- `call __security_cookie` / `mov rax, gs:[0x58]`（x64 的 TEB.StackBase 附近）——**不是**栈保护就是 TLS 基址
- 栈保护 (GS): 函数开头 `mov rax, [rip+__security_cookie]` + 结尾 `xor rax, [rsp+N]` + `jne __report_gsfailure`
- TLS 变量: `mov rax, gs:[0x58]; mov rax, [rax+<tls_index*8+off>]` 模式

## 快速判断清单

| 看到 | 推断 |
|------|------|
| `mov [rcx],rax; lea rax,[rip+vtbl]` | 构造中设置 vptr |
| `test rax,rax; jz` | 空指针检查（防御性或逻辑分支） |
| `cmp eax,<n>; ja` + 表跳转 | switch |
| `imul rax,<magic>; shr` | 除法优化 |
| `gs:[0x58]` | TLS 或 GS cookie 相关 |
| `movzx` + 查表 | 字节处理（S盒/字符转换） |
