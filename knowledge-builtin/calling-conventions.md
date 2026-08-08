# 调用约定速查

> 用途: Scout/Worker 阶段推断调用约定。识别特征 = 传参寄存器 + 栈清理方 + 返回值寄存器。
> 模块: core（re-binary 使用）

## x64 Windows

| 约定 | this 指针 | 参数寄存器（顺序） | 额外参数 | 返回值 | 说明 |
|------|-----------|-------------------|---------|--------|------|
| **fastcall**（默认） | — | rcx, rdx, r8, r9 | 栈（从右往左压） | rax | x64 唯一约定（MSVC/Clang），无 cdecl/stdcall 之分 |
| **thiscall**（C++ 成员函数） | rcx | rdx, r8, r9 | 栈 | rax | this 占 rcx，其余同 fastcall |

- 调用者保存: rax, rcx, rdx, r8-r11, xmm0-xmm5
- 被调用者保存: rbx, rbp, rdi, rsi, r12-r15, xmm6-xmm15
- 栈对齐: 调用前 RSP 必须 16 字节对齐（call 返回地址 8 字节 → 被调函数入口 RSP%16==8）
- 阴影空间 (shadow space): 无论参数是否用寄存器，调用方在栈上预留 32 字节
- **识别**: 函数开头直接使用 rcx/rdx/r8/r9 且不保存 → fastcall；使用 rcx 作为对象基址（`[rcx+off]` 访问）→ thiscall

## x86（32 位）

| 约定 | 参数传递 | 栈清理 | 返回值 | 识别特征 |
|------|---------|--------|--------|---------|
| cdecl | 栈（右→左） | **调用方**清理 | eax（edx:eax 用于 64 位） | `add esp, N` 在 call 之后 |
| stdcall | 栈（右→左） | **被调方**清理（`ret N`） | eax | `ret 8` 等带立即数返回 |
| fastcall | ecx, edx + 栈 | 被调方 | eax | 前两个参数进 ecx/edx |
| thiscall | ecx=this + 栈 | 被调方 | eax | ecx 传 this，`ret N` |
| vectorcall | ecx,edx,xmm0-2 + 栈 | 被调方 | eax/xmm0 | 浮点参数也走寄存器 |

## ARM64 (AAPCS64)

- 参数: x0-x7（整数），v0-v7（浮点/SIMD）；更多参数进栈
- 返回值: x0（v0 浮点）；128 位返回 x0:x1
- 被调用者保存: x19-x29, lr(x30), v8-v15
- 栈 16 字节对齐
- 识别: 函数用 x0 作 this（成员函数），调用前将参数移入 x0-x7

## 特殊变体

- `__vectorcall`: 前 6 个整数参数（rcx,rdx,r8,r9 + 栈）与 6 个向量参数（xmm0-5）用寄存器
- 自定义约定: 反混淆壳/私有 API 常见，需从调用点反向推断

## 常见坑

- x64 下 `stdcall`/`cdecl` 修饰符被忽略——都是 fastcall 寄存器约定
- 间接调用 `call [reg+N]` 不能从指令看出约定——看调用方如何准备寄存器
- 浮点返回值在 xmm0（x64）/ st0（x86 x87）；`__m128` 返回值 x64 用 xmm0，x86 用隐藏指针
