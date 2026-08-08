# C++ ABI 速查（重点 MSVC x64）

> 用途: Class-identify 阶段识别类布局、vtable、继承关系。
> 模块: core（re-binary 使用）

## MSVC x64 对象与 vtable 布局

- **单继承**: vfptr 位于对象偏移 0x00（第一个虚函数指针）；vtable 内按声明顺序排列虚函数
- vtable 地址引用: 构造函数中 `lea rax, [rip+vtable]` + `mov [rcx], rax`（或 `mov [rcx+off], rax`）
- 虚函数**第一个槽位**通常是析构函数变体（`??_7<Class>@@6B@` 指向的表）
- x64 下 vtable 槽位为 8 字节 qword；x86 为 4 字节

## RTTI 结构（MSVC）

| 符号模式 | 含义 |
|---------|------|
| `??_7<C>@@6B@` | vftable 符号 |
| `??_R0?AV<C>@@@8` | type_info 对象（`_R0` 后跟修饰名） |
| `??_R1?A@...` | RTTIBaseClassDescriptor |
| `??_R4<C>@@6B@` | RTTICompleteObjectLocator |
| `.?AV<C>@@` | 类名修饰片段（含类名可读） |

定位: `.rdata` 段搜索 `??_R0?AV` 前缀 → 得到完整类名 → 反查 vftable。
有 RTTI 时整棵继承图、类名、虚函数表直接拿到（re.classify 优先级 1）。

## 多重继承

- 每个基类有自己的 vfptr（对象内多个 vtable 指针）
- this 指针调整: 派生类方法访问第二个基类成员时需 `sub rcx, <偏移>`（thunk）
- 交叉调用时 thunk 调整 this 再跳转: `lea rax, [rcx+off]` / `jmp` 模式
- 识别: 同一对象偏移 0x00 与 0x08 各有一个指向不同 vtable 的指针

## 虚继承

- vbptr（虚基类指针）指向虚基类表；虚基类偏移在表中（负偏移表示相对 vbptr）
- vbtable 首项通常是 0，第二项是 vbptr 到虚基类的偏移
- MSVC: 虚基类通常放在对象尾部

## 构造/析构序列

- 构造函数: 基类构造 → 成员构造 → 函数体；每个构造点先设 vptr（多段构造时 vptr 会多次赋值）
- 析构函数: 函数体 → 成员析构 → 基类析构；同样 vptr 逐步改回各基类表
- 含虚析构的类通常有两个析构（scalar deleting destructor 与 vector deleting destructor）——vtable 里槽位常见

## MSVC 名称修饰（简化）

- 类: `?<Name>@@`（`?Animal@@`）
- 方法: `?<method>@<Class>@@QEAA...`（x64 用 `QEAA` 段表示 public member function）
- 修饰含返回类型与参数类型编码——看到 `@@Q` 基本可确认是成员函数

## 识别速记

```
mov rax, [rcx]      ; 读 vfptr
call [rax + N*8]    ; 虚调用 → 槽位 N
lea rax, [rip+x]    ; 载 vtable 地址
mov [rcx], rax      ; 写 vptr（构造中）
```

## 常见坑

- 优化构建可能省略 vptr 的中间赋值（只设最终表）——不能靠"设了几次 vptr"判断继承深度
- 空基类优化 (EBO) 会让成员偏移非直观
- 64 位下 `[rcx+off]` 的 off 是对象内偏移；虚调用 `[rax+N*8]` 的 N 是槽位序号
