---
volume: 06
title: GPU 编程
scope: Vulkan compute：精度、布局、编译、内存、验证
source: CoreSwap knowledge/discovered（A 类条目重组，正文原样）
status: draft
---

# 06 · GPU 编程

> 覆盖范围：Vulkan compute：精度、布局、编译、内存、验证。条目正文自 CoreSwap 知识库原样搬运（A 类 = 跨项目可复用），行首出处可回查原条目。

## 目录

- #V1 FP32「大数整体精度」与「小数精度」必须分离（int32+float 拆分）
- #V2 结构放大系数决定精度需求（放大链推出 float 硬上限）
- #V3 fp64 是 Vulkan 1.1 core，但 `shaderFloat64` 必须显式启用
- #V4 maintainPrecision 折叠语义（floor≠trunc）+ 可在 GPU 内实时做
- #V5 坐标喂 GPU 的架构分岔（CPU 预拆分 vs GPU 实时算）
- #V6 驱动编译发生在每机器/每驱动首次，pipeline cache 机器绑定
- #V7 编译期常量下标进数据驱动函数 = 常量传播展开陷阱
- #V8 驱动编译时间 = f(函数数, 单函数体复杂度) 双维度
- #V9 「编译慢根因」结论有版本域（结构变后必须重验）
- #V10 预编译二进制分发（C2ME 实证 / VK_KHR_pipeline_binary）
- #V11 减法二分定位编译慢（诊断开关 + 秒级计时器）
- #V12 GLSL/SPIR-V 禁止递归 → 树/图求值必须显式栈或编译期展开
- #V13 显式栈的「返回地址」与「父帧恢复点」是两套状态
- #V14 数据驱动 = 解释器形态，表达式展开必然指数膨胀（100×）
- #V15 插值必须两阶段（角点预填充 + 插值），单 pass 8 角点内联 = 展开爆炸
- #V16 数据布局决定算法可行性（冗余实例 vs 共享 delegate + 每点坐标）
- #V17 SSBO + host-visible/coherent + descriptor set 标准数据通道
- #V18 显存限制 → 分块 batch 只治标（数据量 = 每点数据 × 点数）
- #V19 带宽死局判据（上传总量 ÷ PCIe 带宽 = 分钟级即不可行）
- #V20 GPU 越界读 const 数组也 TDR（不是读 garbage 而是卡死）
- #V21 多线程并发 dispatch 必须互斥（否则驱动层崩溃）
- #V22 create/destroy 配对 + 每个 VkResult 全查
- #V23 设备初始化必须枚举守卫（无 GPU/无 family/无内存类型显式报错）
- #V24 GPU vs CPU 参照逐位对拍（批量 e2e + 分量探针，先分量后总值）
- #V25 吞吐探针必须带 diff 抽查（只测时间 = 只能发现慢不能发现错）
- #V26 模拟器复现 GPU 错值 = 生成器+解释器共同 bug（先做「GPU 特有 vs 共同」二分）
- #V27 单域验证是盲区制造机（逐位一致只证明被覆盖的域）

---

### #V1 FP32「大数整体精度」与「小数精度」必须分离（int32+float 拆分）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V1（A 类）

**发现时间:** 2026-08-13（课题 D1/A1；2026-08-15 汇编）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` A1（coord_precision_probe 对比实验）
**置信度:** confirmed（实测：整体 float 化误差 2.2e-1 → int32+float 拆分后 1.6e-7）
**module:** gpu

#### 观察
float 是**相对精度**（尾数 2^-23 × 数值量级）。噪声采样（Perlin/grad/fade）的核心输入是坐标的**小数部分**；当坐标被 maintainPrecision 折叠到 ~2^24 量级（如 16777216.5）后整体转 float，ulp=2，`16777216.5 → float` 直接丢掉 0.5 的小数——噪声完全错乱。通用规律：**大坐标下的 GPU 采样，必须把「整数部分」（用于精确 hash）与「小数部分」（用于 grad/fade 插值）分两个量表达**，不能整体进 float。

#### 证据
- 折叠后坐标 16777216.5 整体 float 化 → 噪声误差 2.2e-1（翻方块级）；
- int32 整数 + float 小数拆分（小数 ~1e-7 精度）→ 误差降到 1.6e-7。

#### 如何利用
- 任何「大坐标 + 需要小数精度」的 GPU 采样（噪声、体素、空间哈希）：坐标拆 `int32 整数格点 + float 小数偏移` 两通道传/存；
- 折叠（mod 2^25 之类）必须在**整数域**做，别在 float 域整体折叠后再取小数；
- 判错经验：采样值量级错乱且与「坐标折叠」同现 → 先查 float 是否吃掉了大数小数位，不是查噪声公式。

---

### #V2 结构放大系数决定精度需求（放大链推出 float 硬上限）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V2（A 类）

**发现时间:** 2026-08-13（课题 D1/A2）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` A2（diag_interpolated.py 逐 octave 诊断）
**置信度:** confirmed（实测：FP32 误差 1.03e-2；GPU fp64 误差 3.2e-16 逐位一致）
**module:** gpu

#### 观察
某些算法结构（如噪声叠加 `l += sample(coord×o)/o; o/=2`，r=0..15）会用 `1/o=2^r` **放大高 octave 的坐标精度需求**：r=15 时要求 ~2^-35 的坐标精度，而 float 尾数只有 2^-23。此时「坐标拆分」救不了——拆分只是把小数精度固定在 float 尾数上限内，**超不出 float 硬上限**。判定精度需求不能只看「坐标大小」，要看**结构放大系数**（这里 /o 把需求放大 2^15 倍）。

#### 证据
- `/o` 放大链：r=15 单 octave 贡献误差 1.9e-4，40 octave 累积 1.02e-2（翻方块）；
- 改 GPU fp64 → 误差 3.2e-16（double 机器精度，逐位一致）。

#### 如何利用
- 选 FP32 方案前先数「结构里有没有放大系数」：凡存在 `1/o`、`×2^k`、级联缩放，把每级的坐标精度需求乘进去，超过 2^-23 就是 float 死路；
- 精度预算表：坐标量级 → 所需尾数位数 → 对比 float(24)/double(53) 硬上限；
- 判错经验：**「之前 FP32 可行」的结论只对「没有放大链的结构」成立**——同族算法（如无 /o 的 NormalNoise vs 有 /o 的 InterpolatedNoiseSampler）精度特性完全不同，迁移前必须重验。

---

### #V3 fp64 是 Vulkan 1.1 core，但 `shaderFloat64` 必须显式启用

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V3（A 类）

**发现时间:** 2026-08-14（课题 E4/P2-2）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` E4；`.investigations/perf-rework/review-003-d23-integration.md` P2-2
**置信度:** confirmed（编译宏不存在报错 + 审查记录在案）
**module:** gpu

#### 观察
fp64 在 Vulkan 1.1 起是 **core feature**，不是扩展：`VK_KHR_SHADER_FLOAT64_EXTENSION_NAME` 这类扩展宏**不存在**，也没有扩展名可启用；必须在 `VkPhysicalDeviceFeatures` 里置 `shaderFloat64 = VK_TRUE` 并传入 `VkDeviceCreateInfo.pEnabledFeatures`，否则使用 double 的 shader 无法创建设备/pipeline。

#### 证据
- 代码里引用 `VK_KHR_SHADER_FLOAT64_EXTENSION_NAME` 编译不过（宏不存在）；fp64 是 `VkPhysicalDeviceFeatures.shaderFloat64`；
- 审查记录 P2-2：`shaderFloat64` 未显式启用的遗留项（靠目标机器恒有 GPU 兜底，低危但属缺陷）。

#### 如何利用
- 写任何用 double 的 Vulkan shader：设备创建时 `VkPhysicalDeviceFeatures features = {}; features.shaderFloat64 = VK_TRUE;` 并启用（先 `vkGetPhysicalDeviceFeatures` 确认支持）；
- OpenCL/CUDA 对照：OpenCL 的 double 需要 `cl_khr_fp64` 扩展（C2ME 的 .cl 直接用 double 但依赖扩展宏）；跨 API 移植时逐个核对 fp64 的启用方式不同。

---

### #V4 maintainPrecision 折叠语义（floor≠trunc）+ 可在 GPU 内实时做

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V4（A 类）

**发现时间:** 2026-08-13（课题 A4）+ 2026-08-15（C2ME 对照）
**发现者:** worker（CoreSwap GPU 密度引擎课题 + C2ME 调研）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` A4；C2ME `c2me_opencl_ext_math.cl` L117-119（`math_octave_maintainPrecision`）
**置信度:** confirmed（实测：负数差 1 → 折叠值差 2^25；C2ME 源码对照）
**module:** gpu

#### 观察
噪声坐标折叠 `v - floor(v/3.3554432E7 + 0.5) * 3.3554432E7`（3.3554432E7 = 2^25）是 Java `maintainPrecision` 语义。三个通用坑：
1. **floor ≠ trunc**：C++ `(long)(v/2^25+0.5)` 向零截断，GLSL `floor` 向下取整——v 为负且 v/2^25+0.5 < 0 时两者差 1，折叠值差 2^25；
2. 折叠在 GPU 内用 double **实时算**是可行的（C2ME 就是每个采样点现场 `math_octave_maintainPrecision`，不做 CPU 预拆分）；
3. 折叠的数学式本身可当语义锚点：`floor(x/2^25 + 0.5) * 2^25` 是四舍五入到 2^25 网格。

#### 证据
- shader 用 `floor`、C++ 参照用 `(long)` → 负数坐标时折叠值差 2^25（diff 量级 2^25）；
- C2ME `.cl` L117-119：`return value - math_floor(value / 3.3554432E7 + 0.5) * 3.3554432E7;`（GPU 内 double 实时折叠，与 CPU 预拆分路线形成对照——见 #V5）。

#### 如何利用
- 移植任何折叠/取整语义（floor/ceil/trunc/round-half-*）MUST 核对负数分支：`floor(x+0.5)`（向下）≠ `trunc(x+0.5)`（向零）≠ `round(x)`（向零+half-even）；
- 折叠公式当可复现锚点写进测试（正/负/边界各一例）；
- 精度预算允许时，GPU 内 double 实时折叠省掉「CPU 预拆分 + 全量上传」（C2ME 路线，见 #V5）。

---

### #V5 坐标喂 GPU 的架构分岔（CPU 预拆分 vs GPU 实时算）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V5（A 类）

**发现时间:** 2026-08-15（课题 D24/D25 + C2ME 对照）
**发现者:** worker（CoreSwap GPU 密度引擎课题 + C2ME 调研）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D24/D25；C2ME `c2me_opencl_ext_math.cl` L1181-1197（`sample_int32_ctx`）
**置信度:** confirmed（两侧实测：8672 floats/点 vs 每点 {x,y,z} int32 三坐标）
**module:** gpu

#### 观察
把「每点需要哪些坐标/参数」喂给 GPU 有两种截然相反的架构：
- **CPU 预拆分**：CPU 把每个采样点需要的全部分解坐标算好上传（CoreSwap 的 split 数据 = 8672 floats/点）——每点数据量巨大，带宽主导（见 #V19 带宽死局）；
- **GPU 实时算**：每点只传原始 3 个 int32 坐标（`sample_int32_ctx {x,y,z}`），折叠/拆分/精度处理全部在 kernel 内 double 实时算（C2ME 路线）——每点数据量极小，算力换带宽。

数据量差异：8672 floats ≈ 34KB/点 vs 3 int32 = 12B/点（约 2800 倍）。这是**带宽架构的分岔口**：CPU 预拆分把「算的活」变成「传的活」，在「每点数据量 × 点数」超过总线带宽时直接判死刑（D24 实证）；GPU 实时算把「传的活」留在 GPU 算力上，前提是 kernel 内能拿到足够精度的中间计算（double/fp64，见 #V3/#V4）。

#### 证据
- D24：逐 block 完整树需 splitTotal=8672 floats/点，98304 点/chunk → 3.4GB/chunk 上传 → 24 chunks 11 分钟未完成 vs CPU 2.5 分钟；
- C2ME：`sample_int32_ctx` 每点仅 `const int32_t x, y, z` + 采样标志，kernel 内 `math_octave_maintainPrecision` 等 double 实时算（L1181-1197 + L117-119）。

#### 如何利用
- 设计 GPU compute 数据流时先回答：**「每点喂什么」**——能传原始坐标让 GPU 实时推的，绝不 CPU 预展开成大表；
- 预拆分的适用场景只有「拆分结果真需要 CPU 侧复用/参照」；纯 GPU 求值场景，预拆分是带宽自杀；
- 折中：网格/角点级预拆分（点量小，如 768 点/chunk）可行，逐点级预拆分（点量大，98304）不可行（见 #V18/#V19）。

### 二、内核编译时间（驱动 SPIR-V→机器码）

---

### #V6 驱动编译发生在每机器/每驱动首次，pipeline cache 机器绑定

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V6（A 类）

**发现时间:** 2026-08-14（课题 G6）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` G6（实测 corner 70s / 单 shader 580s）
**置信度:** confirmed（实测 + 机制明确）
**module:** gpu

#### 观察
SPIR-V → 驱动机器码（`vkCreateComputePipelines`）**不发生在开发者机器上**——发生在最终用户的机器上，且 pipeline cache 是机器/驱动绑定的：同一台机器第二次命中缓存，换机器/换 GPU/换驱动版本首次必现。对「发布给用户的程序」（mod/游戏/工具），GPU 编译时间是**每个用户首次启动的硬成本**，70s 不可接受（进度条也撑不起）。

#### 证据
- 单 corner shader pipeline 编译实测 ~70s、整 shader ~580s（开发机）；
- 机制：驱动 SPIR-V→机器码 + LLVM 级寄存器分配，随 shader 规模超线性（见 #V8）；
- C2ME 对照：同样面临内核编译问题，用预编译二进制分发解决（见 #V10）。

#### 如何利用
- 发布 GPU compute 程序前把「首启编译时间」当一等公民指标：目标秒级（拆小函数 + 数据驱动，见 #V8）或按设备分发预编译二进制（见 #V10）；
- 测量口径：`vkCreateComputePipelines` 单独计时（glslc 前端只占 0.2s，瓶颈全在驱动），并注明「换机器首启必现」。

---

### #V7 编译期常量下标进数据驱动函数 = 常量传播展开陷阱

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V7（A 类）

**发现时间:** 2026-08-15（课题 D22/A5）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/a-plan-ssbo-implementation.md` A5；`.investigations/perf-rework/gpu-accel-errors.md` D22
**置信度:** confirmed（实测 350.6s → 67.4-101.8s，3 次均 <120s 达标；完整论证见 algorithm-fingerprints 发现 #13，此处不重写）
**module:** gpu

#### 观察
数据驱动函数（参数表在 const 数组/查表求值）对「索引在编译期是否可解析」极度敏感：`switch(coordType)` 使 case 内 `TABLE[0]` 成为**编译期常量下标** → 驱动常量传播进查表函数 → 表读取被静态化 → 逐 case **循环展开**（单次调用 +37~75s）。对照：索引完全动态（`TABLE[CA1_T[ci]]`）时驱动放弃展开（快）。**同一批数据、同一个求值函数，仅「索引是否可静态化」的差异 → 编译时间 ~10 倍级差**（350.6s vs 37.2s）。

#### 证据
- A5 减法二分表：full 350.6s / coord_const 37.2s（coord 表达式贡献 ~313s）/ coord_case0 74.8s（1 次 normal_noise 调用 +37s）/ no_spline 17.2s；
- 修复：`int slot = COORD_SLOT_TABLE[coordType];` 运行时查表（索引运行时不可解析）+ fold 特例 → 67.4s/71.4s/101.8s；正确性逐位一致（maxDiff=3.128e-07 不变）。

#### 如何利用
- 排查驱动编译慢：先扫「数据驱动/查表函数的所有索引是否编译期可解析」——switch/case 常量下标、函数参数被折叠成常量、const 数组编译期已知下标，全都会触发常量传播 + 展开；
- 修复手段：把下标改成**运行时查表**（小 const 表间接一层）让驱动无法静态化；
- 判错经验：编译慢**先量化再猜**——spirv-dis 数 Opcode/查表结构、减法二分定位子系统，比「怀疑 fp64/内联/递归」快得多（fp64 只占 2% 指令也被误判过）。

---

### #V8 驱动编译时间 = f(函数数, 单函数体复杂度) 双维度

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V8（A 类）

**发现时间:** 2026-08-14（课题 D5/G1/G2/G3）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D5/G1/G2/G3（pipe_bench 计时 + check_func_sizes.py）
**置信度:** confirmed（多组实测对照）
**module:** gpu

#### 观察
驱动编译时间是**两个正交维度**的乘积，只优化其一无效：
- 单函数体（巨型展开表达式）：noodle 44 函数 × 1.6KB → 2.4s；corner 29 函数 × 8.5KB body → 70s（**函数体 5 倍 → 编译 30 倍**）；interp 8 角点内联 68KB → >10min；
- 函数数（每实例/每节点一函数）：300 个小函数（body ≤307 chars）仍 >10min——嵌套调用图照样超线性爆炸。

**目标形态：每类型一函数 + 数据表**（镜像 Java 解释器：「一个类服务所有实例，数据在 JSON/buffer」）。经验目标：函数数 ≤ ~50、单函数体 ≤ ~1.6KB（noodle 44×1.6KB=2.4s 已验证秒级）。

#### 证据
- G1：factor 122 函数 >10min（interp_5 角点巨型表达式 68KB）；noodle 44 函数 1.88s；
- G2：拆 8 corner shader（各 29 函数）corner 仍 70s（body 8567 字符）；
- G3：normal_noise 数据驱动 139→1 函数后仍 >10min（interp 68KB 未拆）；
- D5：节点函数化 300 函数（body 全小）仍 >10min → 函数数爆炸。

#### 如何利用
- 生成/手写 GPU shader 时把「函数数」和「单函数体」当预算：函数数 ≤50、body ≤1.6KB 是秒级编译的经验边界；
- 表达式展开式生成器（每实例复制父表达式）必爆炸——**数据驱动 = 每类型一个函数 + 数据表**，节点数据（操作数/参数引用）放 buffer/SSBO（见 #V14/#V17）；
- 优化编译时间先量化两个维度（数函数数 + 量 body 大小），再决定动哪边。

---

### #V9 「编译慢根因」结论有版本域（结构变后必须重验）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V9（A 类）

**发现时间:** 2026-08-15（课题 D21 vs D22）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D21/D22；完整论证见 algorithm-fingerprints 发现 #13，此处不重写
**置信度:** confirmed（同一实验两版本结论相反，实测）
**module:** gpu

#### 观察
D21 在 const 表版实证「动态 node 索引是编译慢主因」（固定 node=0：903.4→31.0s）；SSBO 化后做**同一实验**（fixed_node=0）→ 361.0s ≈ full 350.6s（无收益）——「固定动态索引」的结论**只在 const 表版成立**：SSBO 已把动态索引变成运行时 buffer 读，驱动无从展开，固定它也没有额外收益。**同一表述（「动态索引」）在不同存储形态下指代完全不同的编译行为**。

#### 证据
- const 表版：903.4s 基线 / fixed_node 31.0s（D21）；
- SSBO 版：350.6s 基线 / fixed_node 361.0s（无收益，D22）。

#### 如何利用
- 引用任何「编译慢根因」结论（自己的或别人的）前，先核对**当时的存储形态版本**（const 表/SSBO/数据 buffer/内联展开）是否与当前一致；
- 结构重构（const→SSBO、函数化→数据驱动）后，编译时间根因结论 MUST 重跑减法二分验证；
- 顺带教训：fp64「次因」也是交互效应——const 表版 fp64 成本 310s，SSBO+查表版只剩 ~8.5s（fp64 成本本质是「与展开的交互」），**成本归因必须跟着结构版本走**。

---

### #V10 预编译二进制分发（C2ME 实证 / VK_KHR_pipeline_binary）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V10（A 类）

**发现时间:** 2026-08-14（课题 G4 + C2ME 调研）
**发现者:** worker（CoreSwap GPU 密度引擎课题 + C2ME 调研）
**来源定位:** C2ME `ShaderCacheManager.java` L68/78/208（`config/c2me-shader-delivery/*.tar.zst` + `clCreateProgramWithBinary`）；`.investigations/perf-rework/gpu-accel-errors.md` G4
**置信度:** candidate（C2ME OpenCL 侧实测可用；VK_KHR_pipeline_binary 为对应机制，本课题未实测）
**module:** gpu

#### 观察
「预编译二进制不能跨机器」是错误判断——C2ME 实证可以：预编译内核二进制随 mod 打包分发（`config/c2me-shader-delivery/*.tar.zst`），加载时 `clCreateProgramWithBinary` **秒级**，失败才兜底现场编译。Vulkan 对应机制 = `VK_KHR_pipeline_binary`（按设备型号/驱动版本分发 pipeline 二进制）。用户侧 70s 现场编译只有在「没带缓存的新 GPU」才发生，可接受。

#### 证据
- C2ME：`ShaderCacheManager` 扫描 `config/c2me-shader-delivery/` 下 `*.tar.zst`（L78），`clCreateProgramWithBinary` 加载（L208），失败回退现场编译；
- C2ME 同时把内核拆成 7 个独立程序（ESTIMATE_SURFACE/AQUIFER_PREFILL/NOISE_KERNEL/FLAT_CACHE_PREFILL/INTERPOLATOR_PREFILL/BIOME_MULTINOISE/arena）——按模块拆程序 + 预编译缓存组合使用。

#### 如何利用
- 发布 GPU compute 程序：优先「预编译二进制随包分发 + 现场编译兜底」（开发侧随便慢，用户侧秒级）；
- 按设备型号/驱动版本分桶管理二进制（如不同 GPU 厂商/架构一个桶），哈希校验防陈旧缓存；
- 分发侧做不到时，编译时间必须根治到秒级（#V7/#V8 两条）。

---

### #V11 减法二分定位编译慢（诊断开关 + 秒级计时器）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V11（A 类）

**发现时间:** 2026-08-15（课题 D21/D22/A5）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/a-plan-ssbo-implementation.md` A5（DFC_DIAG 诊断开关 + compile_bench）；gpu-accel-errors.md D21/D22
**置信度:** confirmed（6 变体减法表 + 3 次达标实测）
**module:** gpu

#### 观察
驱动编译慢的主因定位要用**「子系统减法二分」**：诊断开关（如 `DFC_DIAG=fixed_node/coord_const/coord_case0/no_spline`）+ 秒级编译计时器（compile_bench 单独测 `vkCreateComputePipelines`），每个变体一次编译计时，一次实验排除一个候选。while 栈、二分循环、switch 都被逐一排除后才锁定「动态 node 索引」（D21）→ 再被 A5 修正为「coordType 常量下标」（D22）。

**关键陷阱**：最小实验 shader 必须复刻真实结构的「数据驱动动态分派」特征——只复刻「循环+分支+const 数组」会得 0.0s **假阴性**（switch 56 case 简单 body = 0.0s，真实结构里同样结构却爆）。

#### 证据
- D21 表：full 903.4s / no_old 591.8s / no_spline 17.6s / spline 固定 node=0 31.0s / 56 函数+switch >12min / switch 56 case 简单 body 0.0s；
- D22/A5 表：full 350.6s / fixed_node 361.0s / coord_const 37.2s / coord_slot0 302.3s / coord_case0 74.8s / no_spline 17.2s。

#### 如何利用
- 建编译时间回归环境：诊断开关（生成器里做 feature flag）+ 独立计时工具（只测 vkCreateComputePipelines，glslc 前端另计）；
- 减法二分纪律：每轮只切一个子系统/特征，编译时间变化即归因；候选按「成本贡献」排序切（先切最大嫌疑）；
- 最小复现 shader 必须保留嫌疑特征（动态分派/查表/巨型展开），删掉特征的重现无意义；
- 编译计时 3 次取口径（e2e 内 vs 单独工具差 ~4s 属测量噪声），达标判定用多次测量的最差值。

### 三、shader 结构与数据布局

---

### #V12 GLSL/SPIR-V 禁止递归 → 树/图求值必须显式栈或编译期展开

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V12（A 类）

**发现时间:** 2026-08-14（课题 D4/D11）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D4/D11（glslc 报错原文）
**置信度:** confirmed（glslc `Recursion detected` 两次实证）
**module:** gpu

#### 观察
GLSL/SPIR-V 链接阶段**禁止递归**，两条铁律：
1. 直接递归/相互递归都被拒：`spline_eval(...) calling spline_val_at(...)` → `Recursion detected`，前向声明（prototype）不解决；
2. 检测是**符号级**的：两个函数互相调用**即使运行时路径不可能递归**（delegate 树已确认无嵌套 interp）也报错——`eval_df → interp_0 → eval_df` 符号环即拒。

解决形态：① **显式栈循环**（栈数组 + while 模拟后序，1 个函数）；② **编译期展开**（Python 侧递归内联，非 GLSL 递归，但代码膨胀）；③ 符号环拆分——「含 X 节点」和「不含 X 节点」的求值函数拆成两个（`eval_df` 含 interp / `eval_df_base` 不含）。

#### 证据
- D4：spline 数据驱动（spline_eval ↔ spline_val_at 相互递归）glslc 报 `Recursion detected: spline_eval(...) calling spline_val_at(...)`；前向声明后仍报；
- D11：`Recursion detected: eval_df calling interp_0`（delegate 运行时无嵌套 interp 仍报）→ 拆 eval_df/eval_df_base 解决；
- 显式栈帧形态（D21/A5）：`帧 {node, i, coord, stage, v0, v1}`，栈深 32。

#### 如何利用
- 任何树/图结构（样条、表达式树、嵌套求值）上 GPU：**默认显式栈**，别写递归（连「看起来不可能递归」的相互调用也会被符号级检测拒）；
- 生成器侧递归展开可以（Python/C++ 侧），shader 侧禁止——把「递归展开」和「运行时递归」分清；
- 数据驱动解释器里，按「节点类型子集」拆分求值函数避免符号环（含 X / 不含 X 两个版本）。

---

### #V13 显式栈的「返回地址」与「父帧恢复点」是两套状态

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V13（A 类）

**发现时间:** 2026-08-15（课题 D23 sim 双坑 + judge P1-1）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D23 修复段（dbg_full_sim 两坑）
**置信度:** confirmed（两坑均复现并修复，sim vs 递归参照 1344 组合 0 mismatch）
**module:** gpu

#### 观察
把递归求值改写成显式栈（while + 栈数组）时，「返回地址」与「父帧恢复点」是**两套独立状态**：
- **返回地址（outSlot）**：子帧完成后把结果写回哪个槽——压子帧时各设一次；
- **父帧恢复点（stage）**：父帧当前等到哪个子值（如 stage 1=等 v1、stage 2=Hermite、stage 6/7=边界外推）——压子帧时设一次。

两个典型 bug：① 压边界子帧时把 `outSlot[sp] = -1` 清掉本帧自己的返回地址 → 深层嵌套完成时结果不回填祖父帧；② 子帧完成回填时**无条件** `stageStack[ps>>1] = 2` 覆盖父帧恢复点 → 跳过 stage 1（v1 求值）→ v1 恒 0 → Hermite 用错值。**回填只写数据槽，绝不顺带改父帧 stage**。

#### 证据
- sim（Python 显式栈移植）两坑：outSlot 被 -1 覆盖 → 深层递归不回填；回填覆盖 stage → 跳 v1 求值 → v1Stack 恒 0 → Hermite 用 0；
- 修复后：sim eval_df(784,160,-408) = -0.458333333 ✓；sim vs e2e 全量对拍 maxDiff=5.7e-9；显式栈 vs 递归参照 1344 组合 0 mismatch；
- GPU while 栈（stage 4/5 直接 outVal 回填）无此问题——佐证「回填只写数据」纪律。

#### 如何利用
- 显式栈移植检查清单：① 压帧时 outSlot 与 stage **各设一次**（互不覆盖）；② 回填代码**只写数据槽**，不碰 stage/outSlot；③ 边界/特殊路径用显式 stage（等边界 v0 / 等边界 vn），不重载普通 Hermite 状态；
- 判错经验：显式栈结果「某个子值恒 0 / 深层递归错」→ 先查回填是否覆盖了父帧恢复点或返回地址。

---

### #V14 数据驱动 = 解释器形态，表达式展开必然指数膨胀（100×）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V14（A 类）

**发现时间:** 2026-08-14（课题 G5/D10/D12）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` G5（Java 612 行 vs 展开 76338 行）/ D10（879 节点数据展开）/ D12（结构共享 vs 参数实例化）
**置信度:** confirmed（行数对比 + 实测编译时间）
**module:** gpu

#### 观察
生成 GPU 求值代码有两种形态，膨胀机制完全不同：
- **表达式展开**：每实例/每层把父表达式完整复制 → 嵌套越深膨胀越大（Java 原版 Spline 314 + DoublePerlin 116 + InterpolatedNoise 182 = ~612 行，展开成 76338 行 = **~125 倍**）；
- **解释器/数据驱动**：一个求值函数 + 数据表（树结构/参数在数据里），代码量 = 类型数而非实例数。

**「每实例数据」和「每实例代码」一样爆炸**：D10 把树序列化成节点数组（879 节点 = 8 角点 × ~93 节点各自独立序列化）——数据驱动只解决「函数数」，不解决「数据量」。真正根治 = **结构共享**：delegate 树只序列化一份，坐标/参数运行时传（D12：结构与参数实例化分离——树拓扑全局共享，noise 的 splitBase/坐标按采样点运行时查表，即 Java「一个类 + 实例字段」）。

#### 证据
- G5：Java 原版三文件 ~612 行 vs 生成 final_density.comp 76338 行（约 100-125 倍）；
- D10：df_nodes=879（5 interp × 8 角点 × ~93 节点）→ 编译 >60min；结构去重到唯一 + 角点坐标运行时传 → 目标 ~19 个节点；
- D12：splitBase 编译期常量 vs 共享 delegate 树 → 必须运行时查表（noise 实例数组 + 角点索引）。

#### 如何利用
- 生成器正确形态 = **镜像解释器**：每类型一个函数 + 数据表（操作数/参数/坐标引用全在 buffer）；
- 去重要到「结构唯一」：同一结构被 N 个采样点/角点复用 → 只存一份 + 每点参数；
- 判错经验：生成代码膨胀到「函数数/行数 × 10+」→ 先查是不是「每实例复制父表达式」或「每角点复制子树」；
- 结构共享与参数实例化必须显式分离（一个是布局，一个是运行时数据），混在一起必然索引错位。

---

### #V15 插值必须两阶段（角点预填充 + 插值），单 pass 8 角点内联 = 展开爆炸

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V15（A 类）

**发现时间:** 2026-08-14（课题 G3/G4 + C2ME 对照）
**发现者:** worker（CoreSwap GPU 密度引擎课题 + C2ME 调研）
**来源定位:** C2ME `OpenCLCGen.java` L442-556（`df_interpolator_buffer_prefill_*`）；`.investigations/perf-rework/gpu-accel-errors.md` G3/G4
**置信度:** confirmed（实测 interp 68KB → 编译 >10min；C2ME 两阶段为正解参照）
**module:** gpu

#### 观察
三线性/网格插值的 GPU 实现有两种：
- **单 pass 8 角点内联**（每个采样点把 8 个角点的整棵 delegate 树内联进表达式）：角点表达式 = 8 × 完整 delegate 树展开 → 68KB 级巨型函数体（interp_0/5 = 69868 字符）→ 驱动编译 >10min，且是「展开式生成器」的最后一块硬骨头；
- **两阶段网格预填充**（C2ME 正解）：生成 `df_interpolator_buffer_prefill_<name>`，按 cell 网格 dispatch（global size = `(cellCountX+1, cellCountZ+1, cellCountY+1)`），**每工作项只算 1 个角点**的 delegate 采样写入 interpolator buffer；主内核只读 buffer 做三线性。角点采样表达式 = 1 次 delegate 调用（几十字节），无巨型展开。

#### 证据
- G3：normal_noise 数据驱动后仍 >10min——interp_0/5 = 69868 字符（8 角点 × init 树全展开：152 y_clamped + 288 spline_eval + 592 normal_noise 调用）；
- C2ME `OpenCLCGen.java` L461-477：prefill kernel 按 `get_global_id` = cell 相对坐标，每工作项 `df_address_interpolator_buffer(...)` 写 1 个角点值；L539-556：`df_interpolator_buffer_prefill_kernel` 循环调用各 interpolator prefill；
- C2ME 编译时间对照：拆 7 个独立内核程序 + 预编译二进制分发（#V10）。

#### 如何利用
- 任何「网格角点 + 插值」模式（体素、地形、采样器）的 GPU 实现：**角点计算与插值拆两阶段**——角点 prefill 内核（每工作项一角点）+ 插值内核（只读 buffer）；
- 单 pass 内联是编译时间地雷，即使角点表达式看起来「不大」（8 倍 + 树深幂次放大）；
- 插值内核保持「小代码 + 数据」，角点数量由 buffer 承载。

---

### #V16 数据布局决定算法可行性（冗余实例 vs 共享 delegate + 每点坐标）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V16（A 类）

**发现时间:** 2026-08-15（课题 D25 + C2ME 对照）
**发现者:** worker（CoreSwap GPU 密度引擎课题 + C2ME 调研）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D25；`.investigations/000-架构设计/架构计划-gpu-block-integration.md` 003 结论段
**置信度:** confirmed（sim 决定性排除：方案 C maxDiff=8.7e-2；角点等价性差 2.7e-1）
**module:** gpu

#### 观察
GPU shader 的数据布局有两种噪声组织方式，决定「能不能用任意坐标求值」：
- **角点分组冗余实例**（本课题生成器现状）：同一噪声按 8 角点复制 8 份（`continentalness@c0..c7`，参数完全相同，仅 key 带角点后缀），**每实例的拆分数据绑定固定角点坐标**——内容树无法用「该坐标的拆分」算任意点；
- **共享 delegate + 坐标参数**（CPU/C2ME 语义）：一份 delegate 结构 + 每点坐标参数（`make_sample_int32_ctx` 传 x/y/z）——任意点可求值。

D25 实证：想让 GPU 算「内容树在任意网格角点的值」→ 结构不兼容（实例绑定固定角点坐标）→ 方案 C 不可行（maxDiff=8.7e-2）。**带宽可优化（#V19），但「实例绑定固定坐标」的结构无法用「每点坐标」求值**——布局是算法可行性的硬约束。

#### 证据
- sim 验证：interp_N（8 角点 delegate + 插值）== 完整树 maxDiff=0（唯一正确形式）；corner=0 角点 vs 8 角点 delegate 差 2.7e-1；
- 实例分配：corner 偏移 = 同参数 8 副本，split 行按角点坐标拆分（corner 0-7 同坐标 range 1.6e-1~3.1e-1）；
- C2ME 对照：`sample_int32_ctx` 共享 delegate + 每点 int32 坐标（L1181-1197）——C2ME 从不生成角点冗余实例，所以任意点可求值。

#### 如何利用
- 设计 GPU 内核前先查**数据布局的可变性**：「实例/表项是否绑定固定坐标/参数」——绑定固定坐标的结构 = 只能算固定点集，不能当通用求值器；
- 同参数多实例（8 份副本）是「坐标参数化」的退路信号：重构为共享实例 + 每点参数即恢复任意点求值（工程量中等）；
- 判错经验：方案「语义正确但结构不可行」→ 先查数据布局（实例粒度/绑定关系），再查算法，布局错误是根因级。

### 四、内存与带宽

---

### #V17 SSBO + host-visible/coherent + descriptor set 标准数据通道

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V17（A 类）

**发现时间:** 2026-08-14（课题 I1）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/vulkan-proto/vulkan_runtime.h`（VkRuntime 全文件）；`.investigations/perf-rework/i-integration-record.md` I1
**置信度:** confirmed（组件化后 e2e maxDiff=3.128e-07 与内联版逐位一致）
**module:** gpu

#### 观察
Vulkan compute 的实用数据通道形态（验证可用）：**全部数据走 storage buffer（SSBO）**，descriptor set layout 声明 N 个 `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` binding（0..N-1，shader 未用的 binding 留占位合法）；内存选 **host-visible | host-coherent**（`vkMapMemory` + memcpy 上传/读回，免显式 flush/invalidate）；每次 dispatch = 单 command buffer（bind pipeline → bind descriptor set → dispatch）+ 单 fence 等待完成。简化模型：所有 buffer 对 CPU 可见，逻辑上「上传 → dispatch → 读回」。

#### 证据
- vulkan_runtime.h：12 binding storage buffer layout（binding 2 删了 OriginBuf 但 layout 保留 12 项与 shader 声明兼容——未用 binding 合法）；
- 内存类型选择：遍历 `req.memoryTypeBits & (HOST_VISIBLE | HOST_COHERENT)`（L75）；
- dispatch：256 work items/组（`(n+255)/256`），单 command buffer + fence（L105-122）；
- I1 验证：e2e 改组件后 maxDiff=3.128e-07 / avgDiff=1.097e-08 与内联版逐位一致。

#### 如何利用
- 新 Vulkan compute 项目直接套此骨架：SSBO 全数据 + host-visible+coherent + descriptor set + 单 command buffer/fence；
- 大 buffer 才考虑 device-local + staging（带宽敏感时，见 #V19）；小/中数据 host-visible 简单可靠；
- 注意：GLSL buffer 块**成员名与实例名不能相同**（`{float valBuf[];} valBuf;` → `valBuf[x]` 歧义报「not of type array」）——用无实例名块声明。

---

### #V18 显存限制 → 分块 batch 只治标（数据量 = 每点数据 × 点数）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V18（A 类）

**发现时间:** 2026-08-15（课题 D24）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D24（分块 4096 点 batch fill）
**置信度:** confirmed（实测 24 次 dispatch/chunk × 142MB/次）
**module:** gpu

#### 观察
GPU 显存有限，大点集必须分块 batch（如 4096 点/块，24 次 dispatch/chunk）。**分块解决「显存装不下」，不解决「总上传量」**——上传总量 = 每点数据量 × 点数，与块大小无关（24 次 × 142MB = 3.4GB/chunk 一点没少）。分块只改变吞吐形态（批量大小/延迟），带宽死局依旧（见 #V19）。

#### 证据
- 98304 点/chunk × 8672 floats/点 = 3.4GB/chunk；分块 4096 → 24 次 × 142MB + readback；
- 24 chunks × 24 次 = 576 次大上传 = 82GB 搬运 → 分钟级（11 分钟未完成）。

#### 如何利用
- 先算总上传量再谈分块：分块参数只优化「每批多大」，总量超带宽预算（见 #V19 判据）就直接换架构（#V5：GPU 实时算 / 网格级）；
- batch 大小按显存余量 + 带宽时延积选，别按「整块一次传」设计。

---

### #V19 带宽死局判据（上传总量 ÷ PCIe 带宽 = 分钟级即不可行）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V19（A 类）

**发现时间:** 2026-08-15（课题 D24）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D24；完整论证见 algorithm-fingerprints 发现 #15，此处不重写
**置信度:** confirmed（实测：GPU 逐 block 路径 11 分钟未完成 vs CPU 2.5 分钟）
**module:** gpu

#### 观察
**「单点数据量小 + 点量大」是 GPU 批量加速的前提**。GPU 快在「算」（compute throughput），但被「喂数据」（host→device 带宽，PCIe ~16GB/s）完全主导时：上传总量 = 每点数据量 × 点数，超过带宽秒级承载量（GB/s 级）即带宽死局——与 GPU 算力无关（本课题算力 24-32x 充足，卡在喂数据）。判据：`每点数据量 × 点数 ÷ 带宽 → 分钟级` = 方案死刑。

#### 证据
- 逐 block 完整树：98304 点/chunk × 8672 × 4B = 3.4GB/chunk → 82GB 总搬运 → GPU 11 分钟未完成 vs CPU 2.5 分钟（慢 4 倍+）；
- 对照（网格角点级）：768 点/chunk × 8672 × 4B = 27MB/chunk → 22-39x（同引擎同 shader，仅采样密度不同，可行性翻转）；
- 吞吐结论有「采样密度域」：网格角点实测的 22-39x 不能外推到逐 block（数据量 ∝ 点数）。

#### 如何利用
- 立项 GPU 加速先做**带宽账**：每点数据量（拆分坐标/特征向量）× 点数 ÷ PCIe ~16GB/s，分钟级即不可行；正确形态 = GPU 算网格/角点（点量小）+ CPU 插值/后处理到逐点（两阶段拆分）；
- 引用吞吐结论必须声明采样密度域；
- 判错经验：GPU 加速「接线正确但极慢」→ 先算上传总量，别查算力/内核优化。

---

### #V20 GPU 越界读 const 数组也 TDR（不是读 garbage 而是卡死）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V20（A 类）

**发现时间:** 2026-08-14（课题 D15/D16）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D15（val 数组 local memory 溢出）/ D16（const 数组越界读）
**置信度:** confirmed（两次独立 TDR 实证 + 二分定位）
**module:** gpu

#### 观察
GPU 上两类内存陷阱都会导致 `VK_ERROR_DEVICE_LOST`（TDR，Windows 事件日志 nvlddmkm 153）：
1. **局部大数组 + 循环内动态索引**：glslang 为每个动态索引访问路径复制数组副本（`float val[158]` → 10 个 indexable 副本/函数）→ local memory 指数膨胀（12.6KB/work item）→ spill 到全局内存 → kernel 极慢 → TDR。修复：**活跃分析/槽位复用**（像寄存器分配一样：值最后被引用后即弃，贪心分配槽位，val[158]→val[19]，152B/work item）；
2. **越界读 const 数组**（索引 = 实例/槽位错位，如 NORMAL_PACK[456..] 超 152×3）→ 也 TDR，**不是只读 garbage**——凡「索引 = 实例/槽位」必须与参数表索引**严格同源**（两类索引——全量含占位 vs 纯序号——被混用即错位）。

#### 证据
- D15：val[158] → SPIR-V 里 `OpVariable %_ptr_Function__arr_float_uint_158` 出现 20 次（eval_df_base 10 + eval_df 10）；槽位复用后 219KB→144KB SPIR-V，kernel 无 TDR；
- D16：slot base=152 + corner → 实例 152..159 而 NORMAL_PACK 仅 152 项 → 越界 → TDR；修复（参数表按全量索引生成 + 占位 0）后 kernel 0.043s；
- 附带：glslc -O 也超时 2min+——大数组+循环+动态索引的组合让前端优化器也爆炸。

#### 如何利用
- 数据驱动解释器的 val 栈 MUST 做活跃分析/槽位复用（贪心：`max_parent[i]` = 引用 i 的最大父索引，i 在 [i, max_parent[i]] 活跃），不要 `val[N]` 直写；
- 「索引 = 实例/槽位」的地方，参数表长度与实例集合**同源生成**（含占位的全量序号 vs 纯序号，任何一侧用错即错位）；加完整性断言（表长 == 实例数 × 每实例参数数）；
- 判错经验：kernel「卡死/DEVICE_LOST」先查 ① 局部数组副本膨胀（spirv-dis 数 OpVariable）② 越界读（索引与表是否同源）——用「功能二分」（逐函数替换常量测 kernel 时间）定位比猜快；
- 排查用 1 work item 空数据 kernel（秒级判别死循环/极慢），别直接跑大批量。

### 五、并发与资源管理

---

### #V21 多线程并发 dispatch 必须互斥（否则驱动层崩溃）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V21（A 类）

**发现时间:** 2026-08-15（课题 P2-4/D24）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D24（I7 崩溃现场）；`.investigations/perf-rework/review-003-d23-integration.md` P2-4
**置信度:** confirmed（崩溃复现 + mutex 修复闭环）
**module:** gpu

#### 观察
宿主多线程（线程池/自适应并行）**并发调用同一个 GPU 运行时**（共享 buffer 上传/dispatch/queue）→ **进程级崩溃** `0xC0000005`，调用栈在驱动层（NVIDIA `nvtfi`），**不是返回 VkResult 错误**——是崩溃。修复：`std::mutex` 串行化 GPU 调用（fill() 加 `fillMtx`）。GPU 资源并发是**硬约束**（shared buffer + queue + command pool 都不是线程安全的），不是「可能有问题」。

#### 证据
- I7 首次运行（无 mutex）：`context=wg_fill_blocks_multi/fillOneChunk`，`code=0xC0000005`，栈在 nvtfi（NVIDIA 驱动层）——block_probe 默认 -threads 自适应多线程并发调 `fill()`；
- fill() 加 `std::mutex fillMtx` 串行化 → 无崩溃（P2-4 闭环）。

#### 如何利用
- 任何多线程宿主接 GPU 路径：**MUST 先加互斥再谈性能**（每个 VkRuntime 一把 mutex，或 per-thread 独立 runtime/buffer）；
- 崩溃形态识别：驱动层栈 + 0xC0000005 进程崩溃 = 资源并发问题（不是 shader 逻辑错、不是 OOM）；
- 注意互斥串行化会把并发收益吃掉（本课题正确性解决但吞吐更劣化）——设计时把「GPU 调用天然串行」计入架构（GPU 批量接口一次调用处理大批量，避免逐小任务频繁加锁）。

---

### #V22 create/destroy 配对 + 每个 VkResult 全查

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V22（A 类）

**发现时间:** 2026-08-14（课题 I1 封装 + judge 审查）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/vulkan-proto/vulkan_runtime.h`（VKRT_CHECK + destroy()）；`.investigations/perf-rework/review-003-d23-integration.md`（「资源配对/错误检查达标」）
**置信度:** confirmed（审查通过 + 长期稳定运行）
**module:** gpu

#### 观察
Vulkan 没有 GC，资源纪律两条：
1. **每个 vkCreate* 都有配对的 vkDestroy***（buffer→memory、pipeline→pipeline layout→descriptor set layout→device→instance 逆序释放；command pool/fence 每次用完销毁）；descriptor pool 按需创建并登记统一销毁；
2. **每个返回 VkResult 的调用全查**：`VKRT_CHECK(fn)` 宏（`if (_r != VK_SUCCESS) { fprintf(stderr, "%d at %s:%d (%s)", ...); exit(1); }`）——驱动错误是返回值不是异常，不查就吞掉，后续全崩且无从定位。

#### 证据
- vulkan_runtime.h：VKRT_CHECK 包住所有 vkCreate*/vkMapMemory/vkQueueSubmit/vkWaitForFences/vkEndCommandBuffer（L13-15）；destroy() 逆序释放（L128-138）；descriptor pool 记录在 `m_pools` 统一销毁；
- judge 审查：I1「资源配对/错误检查达标」。

#### 如何利用
- 新 Vulkan 工程：每个创建调用配一个销毁（RAII 或显式配对表），启动时 VKRT_CHECK 式全查 + 错误现场（文件:行+调用名）打印；
- 失败即停（exit）比吞错继续好——Vulkan 状态机一旦出错，后续调用行为未定义；
- 长生命周期程序：跟踪每帧创建的 descriptor pool/command buffer 的销毁，防泄漏积累。

---

### #V23 设备初始化必须枚举守卫（无 GPU/无 family/无内存类型显式报错）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V23（A 类）

**发现时间:** 2026-08-15（课题 review-003 P3-1）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/vulkan-proto/vulkan_runtime.h` init()；`.investigations/perf-rework/review-003-d23-integration.md` P3-1
**置信度:** candidate（现状为低危遗留；通用规律由代码审查推演）
**module:** gpu

#### 观察
常见教学级初始化代码缺三类守卫：① `phys[0]` 直接取（无物理设备时越界）；② compute family 找不到时 `m_computeFamily` 停在 UINT32_MAX 继续用（`vkGetDeviceQueue(UINT32_MAX)` 未定义行为）；③ host-visible+coherent 内存类型找不到时用 UINT32_MAX 当索引（vkAllocateMemory 失败才被 VKRT_CHECK 兜底 exit）。P3-1 审查记录：**无 GPU/compute family/合适内存类型守卫（VKRT_CHECK 兜底 exit）——低危（目标机器恒有 GPU）**。对「发布给任意机器」的程序，这就是崩溃/UAF 级缺陷。

#### 证据
- vulkan_runtime.h L33-41：`phys[0]` 无空检查；compute family 循环后无「未找到」分支；L75 内存类型 `ti=UINT32_MAX` 兜底交给 VKRT_CHECK；
- review-003 P3-1：守卫缺失记录在案（低危，靠目标机器恒有 GPU 兜底）。

#### 如何利用
- 初始化按序守卫：`vkEnumeratePhysicalDevices` 为空 → 明确报「无 GPU」；遍历 queue family 无 `VK_QUEUE_COMPUTE_BIT` → 报「无 compute 能力」；内存类型无 host-visible+coherent → 报「无合适内存类型」（或降级 device-local + staging 路线）；
- 守卫失败给出可读信息 + 优雅降级（CPU 回退），不要 exit(1)/UB；
- 判错经验：程序在无 GPU/无驱动机器上崩或 UB → 先查初始化枚举的守卫，VKRT_CHECK 兜底只能保证「出错的时机」，不能保证「出错的现场可读」。

### 六、验证方法论

---

### #V24 GPU vs CPU 参照逐位对拍（批量 e2e + 分量探针，先分量后总值）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V24（A 类）

**发现时间:** 2026-08-14~15（课题 I1/D17）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/i-integration-record.md` I1；gpu-accel-errors.md D17（ref_probe）；a-plan-ssbo-implementation.md 验证表
**置信度:** confirmed（e2e maxDiff=3.128e-07 / avgDiff=1.097e-08 与参照逐位一致，N=1024）
**module:** gpu

#### 观察
GPU 引擎正确性的主载体 = **与独立参照实现逐点对拍**（不是自比对、不是只跑通）：e2e 批量采样（1024 点）逐点比 GPU 输出 vs CPU 参照（DensityBuilder），maxDiff=3.128e-07 / avgDiff=1.097e-08（float 舍入级）。**先分量后总值**：ref_probe 用参照侧 registry 分量探针逐分量采样（factor/sloped/entrances/when_out），分量对拍比只比最终值快得多——某分量量级不对立即定位到该分量链，不用整树猜。

#### 证据
- e2e：maxDiff=3.128e-07 / avgDiff=1.097e-08（seed 8576294172403134396，N=1024；TOP 差异点 i=1004 pos=(44,-49,0) 同点位同值）——SSBO 化/查表修复后**逐位一致**（基线不变）；
- 分量：ref_probe factor=3.950000048 / sloped=12.690109836 / entrances=0.569083105（D17 修复后与参照逐位对齐）；
- D17 定位：正是分量探针发现 factor=6.3（应 3.95）/ sloped=27.14（应 12.69）→ 锁定 spline 陈旧索引。

#### 如何利用
- 新 GPU 引擎建立「批量对拍 e2e + 分量探针」双载体：e2e 给总质量，分量探针给定位速度；
- 参照必须独立（第三方实现/原版），不能与生成器同源（同源产物同错，见 #V26）；
- 判定标准用「maxDiff 在 float 舍入级（~1e-7）+ 分量逐位对齐」，并保留 TOP 差异点坐标供回归对比。

---

### #V25 吞吐探针必须带 diff 抽查（只测时间 = 只能发现慢不能发现错）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V25（A 类）

**发现时间:** 2026-08-15（课题 I5/D23）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D23（gpu_throughput_probe 16/64 chunks）；i-integration-record.md I5
**置信度:** confirmed（吞吐对比顺带 diff 才暴露 D23）
**module:** gpu

#### 观察
性能/吞吐对比探针**默认带逐点 diff 抽查**：I5 的 gpu_throughput_probe 测 16/64 chunks 吞吐时顺带做同点 diff，才暴露 GPU 引擎在 e2e 验证域外系统性错值（maxDiff 2.02e-01/4.45e-01，量级级差异）——**若只测时间，GPU 24-32x 就「达标」了，错值无人知晓**。凡新引擎/新路径的性能对比，diff 是正确性的免费抽查，必须带上。

#### 证据
- I5：1/4 chunks maxDiff 1.04e-06/1.33e-06 正常；16/64 chunks maxDiff 2.02e-01/4.45e-01（e2e 域外错值）——同探针带 diff 才定位到 (784,160,-408) 单点；
- D23 决定性单点：gpu=0.045303289 vs cpu=-0.458333333（diff 5.036e-01）。

#### 如何利用
- 任何性能探针模板加一段：随机/代表性点 GPU vs 参照 diff 输出（覆盖多 chunk、多 cell、多 y 层——见 #V27）；
- 吞吐结论必须注明「正确性抽查口径」（测了哪些域/哪些 diff），不能只报倍数；
- 判错经验：性能对比「加速比达标」时先问「diff 抽查做了没」——速度达标 + 值全错是最危险的假通过。

---

### #V26 模拟器复现 GPU 错值 = 生成器+解释器共同 bug（先做「GPU 特有 vs 共同」二分）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V26（A 类）

**发现时间:** 2026-08-15（课题 D23）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D23（sim_single_point.py + dbg_full_sim.py）
**置信度:** confirmed（sim=GPU=0.045303285 完全一致，根因确认为共同逻辑 bug）
**module:** gpu

#### 观察
GPU shader 由生成器产出时，**Python 复刻解释器（sim）与 GPU 同源**：sim 能精确复现 GPU 错值（sim=GPU=0.045303285）＝**生成器+解释器共同逻辑 bug**，不是 GPU kernel/驱动特有。定位顺序：
1. **先做「GPU 特有 vs 共同逻辑」二分**：sim 能复现 → 直接排除 GPU kernel/驱动层（省掉 kernel 级排查）；
2. **sim 只能证明「生成器产物内部一致」，必须与第三方参照对拍**（DensityBuilder / registry 分量探针）才能发现生成器级错误——本次 sim=GPU=0.045 正是「同源错误」的体现（参照 sloped=-2.664 vs GPU/sim -0.0165，差 160 倍立即定位链）。

#### 证据
- sim_single_point.py：对 (784,160,-408) 复刻解释器 = 0.045303285，GPU = 0.045303289（完全一致）；CPU 参照 = -0.458333；
- 分量对拍：参照 sloped=-2.664 / factor=4.524 vs GPU/sim sloped 角点值 -0.0165（差 160 倍，结构性错）→ 根因收敛 spline 链；
- 修复后 (784,160,-408) gpu=-0.458333343（diff 9.9e-9），e2e 零回归。

#### 如何利用
- 建「模拟器复刻解释器」作为 GPU 调试工具（读 e2e dump/同源数据）——定位速度比跑 GPU 快几个量级；
- 发现 sim=GPU 的错值时：共同逻辑 bug 方向（生成器/解释器），别再查驱动/内存；发现 sim≠GPU 时才是 kernel 特有方向；
- **任何 sim/生成器自洽结论都要配第三方参照对拍**——内部一致 ≠ 正确；
- 判错经验：「模拟对了但 GPU 错 / 模拟 GPU 一起错」都是二分信号，先问「有没有第三方参照」再深挖。

---

### #V27 单域验证是盲区制造机（逐位一致只证明被覆盖的域）

> 出处：CoreSwap `knowledge/discovered/vulkan-gpu-programming.md` · 发现 #V27（A 类）

**发现时间:** 2026-08-15（课题 D23；同类 C12/D14）
**发现者:** worker（CoreSwap GPU 密度引擎课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D23（e2e 验证域盲区）/ C12（maxDiff=0 假象）；完整论证见 algorithm-fingerprints 发现 #14，此处不重写
**置信度:** confirmed（e2e 域 3.128e-07 全过、域外错 0.5，实测）
**module:** gpu

#### 观察
**「单域逐位一致 ≠ 全域正确」**：e2e 验证域（x≤63, y∈[-64,-49], z≤4 = chunk 0 的 cy=0 cell）maxDiff=3.128e-07 全过，域外 (784,160,-408) 错 0.5——被覆盖的域证明不了未覆盖的域。两类盲区陷阱：
1. **「执行不到」类分支**（边界外推、嵌套边界、极端坐标域）：只在特定坐标域触发，单域永远测不到；
2. **常数分支吸收差异 = 假正确**：采样点落在常数分支（range_choice 阈值外、y≥256 无地形层）时误差被吸收（C12 maxDiff=0 假象、D23 y≥256 全对）——「大体正确」的错觉。

配套纪律：**完整性断言随规模变化重验**（D14/D23：每个实例的 splitBase 都有 split 行，139→200 实例后未重跑 → noodle_ridge_b 漏检查未被发现）。

#### 证据
- e2e 域（x≤63, y∈[-64,-49], z≤4）全过 vs (784,160,-408) gpu=0.045 vs cpu=-0.458（diff 5.036e-01）；
- 错误域模式：z-scan 中 cz≤1 对 / cz≥2 错；y-scan 中 y=-64 对 / y∈[-56,248] 错 / y≥256 对（常数分支 -0.02499 吸收差异 = 假正确）；
- C12：采样点恰在 range_choice when_in_range 常数分支 → e2e maxDiff=0.000e+00 假象；改采样覆盖阈值两侧 → maxDiff=5.053e-07。

#### 如何利用
- 验证覆盖设计 MUST 跨域：多 chunk（含 chunk 0 外）/ 多 cell（cy≥1、cz≥2）/ 多 y 层（**含常数分支层**——常数分支吸收差异是假正确）；
- 「maxDiff=0 / 逐位一致」先怀疑「采样点是否覆盖有效路径」，再信「完全对齐」；
- 边界分支（外推、区间跨越）用跨域采样专门覆盖——y 相关语义差先怀疑「分支切换」（跳变点是强线索），不是噪声本身；
- 结构规模变化（实例/节点数）后 MUST 重跑完整性断言（生成器产物 = shader + CPU 侧同批噪声，缺一批就是漏遍历）。

---

### 附：GLSL/SPIR-V 语法与工具速查（源：gpu-accel-errors.md E 系列 + D18 + C/D 系列）

> 与上述「发现」不同，本条目不展开观察/证据，只列可复用的语法/工具坑（每条 = 坑 + 一句正解）。

| 坑 | 正解 |
|---|---|
| `input`/`out` 是 GLSL 保留字 | 不能作参数名/buffer 变量名，改用 `v`/`outBuf` |
| C 风格转型 `(double)x` 报错 | GLSL 用构造函数式 `double(x)`（`(double)x` 需 GL_NV_explicit_typecast） |
| float 字面量 `0f` 非法 | 保证小数点（`0.0f`）；`:.17g` 格式化 0.0 会输出 `0` |
| 常量字面量类型（如 `1.0e-7f` vs `1.0e-7`） | double 场景要 `double(1.0e-7f)` 对齐原版 float 常量，不能写 `1.0e-7` |
| GLSL 先声明后使用 | 生成器显式管理函数依赖序；跨函数引用多时**全部前向声明**（不依赖注册顺序） |
| 递归注册函数 idx 冲突 | 「先占位（idx,None）再回填 body」，idx 分配与 body 生成解耦 |
| 生成表达式位移优先级 | `<<` 优先级低于 `*`/`+`：`(x>>2)<<2 * 0.25` 被解析成 `(x>>2)<<(2*0.25)`——位移片段 MUST 加括号 |
| `#pragma DontInline` 无效 | glslang 不识别该 pragma（SPIR-V 无 DontInline）；要改 FunctionControl 必须 spirv-dis → 手改 OpFunction（bit1=0x2）→ spirv-as 重汇编 |
| glslc -O 超时 | 大 const 数组+循环+动态索引让前端优化器也爆炸——生成代码用默认优化或 -O0，结构上做「小而多函数/小数据」 |
| minimal 复现脚本 replace 静默失败 | 二分测试必须基于**生成器直接输出**（改生成器+重生成），replace 锚点不匹配 = 测旧产物（假结论）；脚本 assert 替换成功 |
| spv/exe 陈旧版本 | 复制/重跑前用 sha256 或 Length 核对产物版本（copy 到错误目录会静默用旧 spv） |
| uint32_t 下溢 | `(i % 32) - 16` 里 i 是 uint32 → 下溢 2^29；先 `(int)(i % 32)` 再减 |

---
