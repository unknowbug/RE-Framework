---
volume: 05
title: 性能与并发工程
scope: 并行度、缓存、调度、内存、吞吐/延迟口径
source: CoreSwap knowledge/discovered（A 类条目重组，正文原样）
status: draft
---

# 05 · 性能与并发工程

> 覆盖范围：并行度、缓存、调度、内存、吞吐/延迟口径。条目正文自 CoreSwap 知识库原样搬运（A 类 = 跨项目可复用），行首出处可回查原条目。

## 目录

- #18 跨 session 基准数字不可直接续推
- #21 微测基线样本模式决定缓存命中率（外推差 40×）
- #24 多臂顺序 bench 顺序效应造假交互（须 chunk 粒度交错）
- #28 并发 bench 互相污染（性能 bench 必须串行）
- #29 一次性 bench 探针自带头注时间戳
- #82 性能负面结论必须核对验证域覆盖面
- #83 性能分母分场景（延迟 vs 吞吐可差一个数量级）
- #89 可观测窗口被缓存主导 → 降级声明须写采样失败机制
- #100 「缓存失效当结论」：必须核对谁写谁读两侧接线
- #102 缓存 clear-all 惩罚的落点核对
- #107 同步接管阻塞单车道调度器（并行度塌成 1）
- #109 臂无关「每 chunk 线程时间」尺子
- #114 沙箱禁 attach 时「门控看门狗自打线程栈」
- #119 JVM 峰值内存 ≠ 存活集（须固定堆或读 GC live-set）
- #122 并发度 = 调用方池宽（引擎线程参数是死参数）
- #124 「先量后改」（优化被测量推翻的例子）
- #131 跳过型写回优化等价判据须用精确谓词
- #135 优化池条目的成立前提必须一手源核对
- #147 减法归因前必须有分段直接计时（余项小可能是余项没测）
- #187 读写并发义务判定先核读者门字段级内存语义
- #190 并发 stderr 诊断行须容忍交错残缺（残缺率门双档）

---

### #18 跨 session 基准数字不可直接续推

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #18（A 类）

- **时间/置信度/module**：260903-08，candidate（judge 建议通过），re-code/swe 通用。
- **来源定位**：lossless-accel P-C1 端到端三方对比（pc1-e2e-260903-08.md）；判别证据 = fair_comparison_corrected.txt:3-4 自注（08-29 Rust 侧为「无树花」口径）。
- **观察**：08-29 结论「Rust 45.48 < Java 55，反快 1.2×」被后续 session 引用为「Rust 比 Java 快」的默认前提；同日同机同 region 重测（Rust 含 features 完整管线）实为 Rust 72-77ms vs Java 33ms——**慢 2.2×**，方向完全反转。根因不是哪次测错了，而是两次 Rust 侧 stage 覆盖不同（无树花 vs 全管线），历史数字无口径标注或标注未随结论流转，续推时口径失配。
- **判据**：① 引用历史基准结论前第一动作 = 核对 stage 覆盖/口径标注与当前对比口径是否一致（§9.7「与既有口径可比性」的历史方向应用）；② **缺标注的历史数字一律视为不可比**，不得作为方向性前提续推（交接结论验证纪律的基准数字特例：假设不当公理，历史数字不当基线）；③ 采新基准时把口径自注写进产物文件本身——标注随数据走，不随会话记忆走（本例 fair_comparison_corrected.txt 自注救了归因）。
- **同族**：§9.7 三要素、#14（阶段同源性）、#17（坐标维度对位）——本条补「历史结论跨 session 续推维度」。连锁开问题：Q-PD1（Rust features/carver 段 vs Java 差距大头，独立排查）。（📌 260903-09 更新：Q-PD1 已闭合，方向假设被 supersedes——大头实为 aquifer 段，见 .artifacts/lossless-accel/qpd1-attribution-260903-09.md。）

---

### #21 微测基线样本模式决定缓存命中率（外推差 40×）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #21（A 类）

- **时间/置信度/module**：260903-10，confirmed（260903-10 用户拍板），通用方法论。
- **来源定位**：Q-AQ1 归因（qaq1-attribution-260903-10.md）；错误基线 = qaq1-initdensity_cost 探针「随机 y + 交替列」实测 initial_density 0.089µs/sample（F5），真实 est 扫描形态 3557ns/sample（qaq1_b1_coldpath A 段）——差 40×，整套「est 只值 0.66ms」推论作废。
- **观察（现象）**：同一 DensityFunction 树、同 seed 同 region，两种采样模式测出 40× 单价差；错误基线与冷态实测 26.65ms 直接矛盾（0.65ms vs 26.65ms），矛盾被正确用作怀疑信号。
- **根因**：微测的遍历方向/列切换模式/缓存冷热/生命周期与热路径不同构——「随机」模式命中 Cache2D/y 无关缓存，est 扫描每 chunk 换列全冷、且 base_3d_noise（old_blended，24 octave）无任何缓存全价执行。
- **定位**：量级矛盾（核算 vs 实测）触发怀疑 → 决定性探针（qaq1_b1_coldpath）按热路径同构形态重测。
- **教训/如何利用**：**单点微测外推热路径成本必须复刻调用形态**（遍历方向/列切换/冷热/生命周期）；「量级核算与实测差 10×+」第一怀疑形态失配而非测量噪声。同族：#17（坐标钉死）、#20（自变量生效）——本条补「采样形态同构」维度。
- **补充案例（260903-11，working set 维度）**：est-opt 包微测复刻了调用形态（est 逐列冷扫描）仍得出 2117ns/iter 上界，生产冷路径实际单价 ≈11µs/iter（差 ~5×）——签名：**e2e 实测收益（−48ms/chunk）超微测上界（15.5ms）**。差异不在调用形态而在 **working set**：生产树共享 Arc + 大缓存集（Cache2D/邻居表/共享 sampler），独立树微测的缓存足迹远小于生产；微测虽「形态同构」但「内存环境不同构」。教训补全：微测外推需复刻**调用形态 + working set（共享结构/缓存集/生命周期）**两者；「e2e 收益 > 微测上界」是 working set 失配的强签名，以生产实测为准、不反推机制定论。

---

### #24 多臂顺序 bench 顺序效应造假交互（须 chunk 粒度交错）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #24（A 类）

- **时间/置信度/module**：260903-10，confirmed（260903-10 用户拍板），通用方法论。
- **来源定位**：qaq1-b2-candidate-260903-10.md；v1 顺序执行 aquifer×carver 2×2 四臂，round2 全臂 +8~13% 漂移下出现物理不可能的负交互（C|Aoff 22.97ms > C|Aon 10.62ms——carver-on-Air 每点工作应严格更少）；v2 chunk 粒度交错 ×3 轮 ×median 稳定 ±0.5ms。
- **观察（现象）**：同进程顺序跑多配置，机器漂移/缓存状态系统性偏向后跑的臂；差值中出现违反物理约束的读数。
- **根因**：顺序执行的臂序与时间相关漂移卷积；「负交互」= 漂移伪影。
- **定位**：物理约束违反签名（工作量少的配置反而更贵）→ 怀疑测量设计而非机制。
- **教训/如何利用**：**≥2 臂差分 bench 必须 chunk 粒度交错 + 多轮 + median**；「物理不可能读数」是测量设计 bug 的强签名，先修测量再谈机制。同族：#19（世界状态）、AGENTS 测量污染铁律——本条补「臂序漂移」维度。

---

### #28 并发 bench 互相污染（性能 bench 必须串行）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #28（A 类）

- **发现时间**：260903-16。**发现者**：主会话 + judge。**置信度**：candidate（干净三臂复跑定案，judge 审查通过）。**module**：通用方法论（bench 设计）。
- **来源定位**：`.investigations/vulkan-gpu-operator/shared-arm-errors.md` E1。

#### 观察（现象）

default 37.67ms vs l2-only 27.50ms 两臂对比中，「shared 臂 +10ms」被解读为实现固有开销并立项归因课题。事后发现 pc_e2e 与 gpu_mt_wall_retest（含 70-100s Vulkan 管线编译 + 412 次 GPU fill）后台并发运行——GPU 负载同样吃 CPU（驱动/JIT/管线编译），直接污染 CPU 侧 bench。干净三臂复跑（default 28.46 / l2-only 27.50 / qpd1 FULL 25.87）证明原「+10ms 固有开销」不存在，归因课题整体作废。

#### 根因（机制）

① 任何「只吃 GPU」的负载并非真正互斥——Vulkan 管线编译、驱动层工作、JIT 都消耗 CPU，与 CPU 侧 bench 争抢核心；② 「min 不变 median 变重」签名被当成「实现尾部开销」的证据——但该签名**对外源间歇抢占同样成立**（抢占拉高中位数、不动最优样本），不具区分力；③ 证据饱和前未做并发排除即进入机制归因。

#### 定位（怎么发现）

复跑排除法：单点离群在机制上找不到解释 + 同臂其他口径不 corroborate → 按判据先复跑再归因；串行环境重跑三臂后差异消失，锁定外源污染。

#### 修复 / 如何利用（可复用判据）

1. **任何性能 bench 必须串行**：background job 运行期间不得跑另一条 bench，包括表面「只吃 GPU」的负载（Vulkan 管线编译/驱动/JIT 同样吃 CPU）。
2. **「min 不变 median 变重」不具归因力**：既符合实现尾部开销也符合外源间歇抢占——归因前先排除并发/环境因素。
3. **复跑触发判据**：单点离群 + 机制上找不到解释 + 同臂其他口径不 corroborate = 先复跑再归因（复跑成本远低于一个作废的归因课题）。
4. 同族：#24（多臂顺序漂移——本条补「跨进程并发」维度）、#21/#22（量级矛盾/凑数反模式）、AGENTS 测量污染铁律。

---

### #29 一次性 bench 探针自带头注时间戳

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #29（A 类）

- **发现时间**：260903-16。**发现者**：judge CONCERN 转化。**置信度**：candidate。**module**：通用方法论（诊断工具卫生 / bin-diag 规范）。
- **来源定位**：`.investigations/vulkan-gpu-operator/shared-arm-errors.md` E1 定位过程——judge 指出并发重叠论证只能靠事后过程重建时序，「永远带保留」。

#### 观察（现象）

bin-diag 一次性 bench 探针（gpu_mt_wall_retest 等）输出只有数据、无进程启动时刻；事后怀疑并发污染时，只能人工重建「哪个 job 何时启动、与 bench 窗口是否重叠」——每个环节都是推断，judge 对重叠论证只能给 CONCERN，无法一锤定音。

#### 根因（机制）

一次性诊断工具默认「跑完即弃」，没把**自身的运行时刻**当作输出数据的一部分；而 bench 归因恰恰依赖时序证据（是否与后台负载重叠）。缺失的时间戳使时序证据永久处于可争议状态。

#### 修复 / 如何利用

一次性 bench/诊断探针运行时**自带时间戳头注**：进程入口 `Instant::now()` 打印一行启动时刻（建议附单调钟起点），使时序复核变成日志实录。成本一行代码，收益 = 并发/污染类争议从「论证」降级为「查日志」。同族：#9（一次性产物隔离区）——本条补「一次性产物的时间可溯性」维度。

---

### #82 性能负面结论必须核对验证域覆盖面

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #82（A 类）

- **发现时间**：260908-02
- **发现者**：scout-a + judge（GPU 介入点重勘探课题）
- **来源定位**：`.investigations/gpu-reentry-260908-02/scout-a-cpu-cost-profile.md` §二 + `convergence-main-260908-02.md` §一 + `.investigations/perf-rework/gpu-accel-errors.md`（D24/D25/D27 无 aquifer 条目，grep 确认）
- **置信度**：candidate
- **module**: workflow

**观察**：GPU 加速课题（260908-01 verdict，confirmed）三次否决（D24 逐块 fill 带宽死局 / D25 interp 角点结构不兼容 / D27 攒批摊销封顶 13%）的验证对象**全部集中在 density/interp 底座**——仅占 Rust FULL 62ms 的 ~23%（14.4ms/chunk）。而占 ~60% 的最大单阶段 aquifer（~35-37ms/chunk）**从未进入任何一次 GPU 课题验证域**（gpu-accel-errors.md 无 aquifer 条目）。一轮成本分布重勘探（scout-a）即发现「全线不可行」的问题定义漏掉了最大头，且 C2ME 有 AQUIFER_PREFILL 等 aquifer GPU kernel 的存在性先例从未被评估。

**证据**：scout-a §二 GPU 课题评估覆盖标注表（aquifer/surface/carver/biome/feature 全部 ❌ 从未评估）；convergence §一三源交叉事实 1；judge review-convergence §审查点 1 确认引用准确、无取代冲突（重勘探落在原 verdict 留白③内）。

**如何利用（判据）**：宣布「X 路线全线不可行 / 问题域无解」类**全域性负面结论**前，MUST 先盘点**成本/问题分布表**（各子项占比 × 各子项是否在已验证样本内），确认被否样本对全集的覆盖面；占比大头未被覆盖时，负面结论的表述 MUST 限定到已验证子域（「noise/density 管线现引擎形态」而非「GPU 加速不可行」），余下子域显式留白。本例的否决记录 D24/D25/D27 本身无错——错的是「verdict 范围外的读者/后续会话把『density 线路否决』读成『GPU 路线全线否决』」。同构于发现 #36（排除结论禁止跨执行体迁移）的「跨验证域」形态：排除结论 = 只对被验证子域成立。

---

### #83 性能分母分场景（延迟 vs 吞吐可差一个数量级）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #83（A 类）

- **发现时间**：260908-02
- **发现者**：addendum-denominator 实测 + judge（GPU 介入点重勘探课题）
- **来源定位**：`.investigations/gpu-reentry-260908-02/addendum-denominator-c2me-260908-02.md` §A + `review-convergence-260908-02.md` C2b/C3b + `review-phase0-260908-02.md` J3
- **置信度**：candidate（两端口径各有独立实测；四臂差分法本身实测成立）
- **module**: workflow

**观察**：同一阶段（aquifer）同一天同一 seed 的两次实测，口径差 **35×**：单 chunk **冷态延迟 35-37ms/chunk**（qpd1_stage_bench 隔离 bench）vs **暖区吞吐差分 1.02ms/chunk**（estopt_mt_bench T=10 四臂差分：WITH 7.43 − NO 6.41；T=1 差分 9.70，9.70/10≈0.97≈1.02 交叉自洽）。门槛核算用哪个分母直接翻转结论：暖区分母下 GPU 门槛回到 ~1ms 预算级（D27 同款，难）；冷区分母下门槛 ~1×（易）——GPU 的真实机会窗口在冷路径（世界加载/离线首遍），不在暖区稳态。此外门槛核算必须含**固定/互斥成本**（dispatch/readback 非零且结论绑定 kernel 形态不可迁移；与 CPU 多线程管线并存的 mutex 串行化开销——D24 P2-4 实锤），只比 kernel 单价 vs CPU 单价的对比式是漏项（judge 两轮同一意见 C3b/J3）。

**证据**：addendum §A 四臂表（256 chunks，seed 同，暖区口径）；qpd1_stage_bench 冷态口径；交叉自洽验证 9.70/10 ≈ 1.02（并行扩展良好、无严重串行瓶颈）；review-phase0 J3 必改条件。

**如何利用（判据）**：① **核算优化回本门槛时，分母 MUST 绑场景**——延迟敏感场景（单 chunk 冷态）用延迟分母，吞吐摊销场景（多线程稳态）用吞吐差分分母，混用口径会高估/低估优化空间一个数量级（#18「跨 session 数字不可比」的**同 session 跨口径**形态，§9.7 具体化）。② **四臂差分法**（同 T 下 WITH/NO 某阶段 × 多档 T，各臂 chunk 粒度交错——#24 顺序效应判据同用）是采集「某阶段多线程摊销分母」的廉价方法，无需逐阶段探针。③ GPU/异步加速的 gate 对比式 = 端到端成本（kernel + dispatch + readback + 与宿主管线互斥）× 规模 vs 对应场景 CPU 口径，缺任何一项即 gate 无效。

**#53 补充案例**（260908-02，⚠️ 未结案待验）：estopt_mt_bench 运行时 `$env:WG_EST_L2` 已清空仍显示 `l2=true`——疑似该开关默认开（与 #53 原例方向相反的镜像形态：**「清空 env ≠ 恢复默认值预期」**，默认值方向必须消费点直读确认，env 清空本身不构成任何方向的证据）。待 api.rs 直读钉死后回填结案。来源：`.investigations/gpu-reentry-260908-02/addendum-denominator-c2me-260908-02.md` 注记 1 + `phase0-architecture-260908-02.md` §五③。

---

### #89 可观测窗口被缓存主导 → 降级声明须写采样失败机制

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #89（A 类）

- **时间/置信度/module**：260908-11；candidate（四轮多形态点集一致 + 机制解释明确）；workflow-patterns / 验证载体局限（简记，中价值）。
- **来源定位**：`.artifacts/mc-1216-port-260908-11/verdict-f1f2-chunky-260908-11.md` §F2 降级声明；progress-260908-11.md §F2。
- **现象**：F2 探针 spread-replay 路径的字段级手算对拍多轮未达成：164 地表柱点 / 1408 深部网格点全 density>0 早退、144 空气点 / 28 水洞点走链但**缓存命中主导**，几乎采不到 replay（扩散重算）行。
- **机制**：aquifer 链字段在首算后缓存，后续查询命中缓存即返回——replay 行只在缓存 miss 且需扩散重算时出现，正常采样集里占比趋零；「点集选在哪」不能改变这一结构性占比（早退点集连链都不进）。
- **如何利用**：① 验证目标落在低频路径（如 spread-replay）时，先评估该路径在可用采样形态下的**可采性**，不可采就 early 声明降级（静态对齐 + 旁证），不要多轮硬采（本轮四轮即达证据饱和）；② 降级声明不只写「未达成」，要写**为什么采不到**（缓存命中主导/早退主导），下个块才不会重走同一死路；③ 跨执行体旁证（Rust 自算链 fl/decision 与 vanilla 缓存真值逐点一致）是 spread 路径不可采时的可接受替代证据等级。

#### #26 补充案例（中价值简记，260908-11）：Chunky 区域级载体首次跨版本复用——1.21.6 量化基线 + 与 1.20.1 基线同构确认

- **时间/置信度/module**：260908-11；candidate（1089 chunk/臂全量 + 与 confirmed 基线同构判定）；workflow-patterns（#26 Chunky 载体的跨版本泛化首证）。
- **来源定位**：`.artifacts/mc-1216-port-260908-11/verdict-f1f2-chunky-260908-11.md` §Chunky。
- **要点**：Chunky-Fabric-1.4.40（Modrinth，game_versions 明确含 1.21.6，sha256 `4dd5430e…a70c2`）；协议同 #26：runServer 同实例对称双臂（vanilla=`-PcppVanilla=true` / coreswap=stageMask=3），seed 三查 ✓，center(464,-248) radius 256 → 1089 chunks/臂。**结果**：3698 chunk-slot 全 common、625 有差、terrain=27,367 / veg=6,473 / air=0；家族构成（blob 石 ~6.3k each / 水+海草下游 2.6k / mineshaft 结构件）与 1.20.1 confirmed 基线（chunky-trial-260906-09：113k terrain/3025 chunk）**同构，无新差异家族**；水差 y 剖面全部落 y=32-63 近海面，F1 域（y≤-54）零差。
- **如何利用**：① 载体跨版本可行性首次实锤——新 MC 版本区域级验证直接复用同协议；② 区域量化结果作 1.21.6 残差基线锚（0.0256% terrain 口径），后续块对比不必重跑建立基线；③ 「同构判定」（家族构成逐项对上 + 无新家族）+「单点位精确对齐由高精度载体（BlockProbe 99.9993%）承担」是「区域级粗对齐 × 单点级精对齐」双载体的组合范式；④ Chunky 口径与 BlockProbe 口径不可互比（§9.7，#33）。

#### #80 补充案例（260908-11，反向形态）：核验时机必须跟随被核验行的产生时机——Done 后 init，即时断言 FAIL 误报

- **时间/置信度/module**：260908-11；candidate（30s 轮询后稳定命中）；workflow-patterns（#80/#69 时序家族的核验侧反向形态）。
- **来源定位**：`.investigations/mc-1216-port-260908-11/errors.md` E6。
- **现象**：coreswap 臂 `Done (4.952s)` 后立即 grep `[CppBridge] init` → 空 → FAIL 退出（且 FAIL 分支未杀 java，残留进程）。
- **根因**：BenchMod/CppBridge 初始化是惰性的，init 行在 Done 之后若干秒才打印；「以 init 行时间戳作接管生效判据」是 #69 原判据，本条是反向：**核验早于 init 行产生**——被核验事件与查询时刻错序，即时断言结构性误报。
- **判据/如何利用**：① 核验脚本先确认「被核验行在日志流的哪个时刻产生」（可早可晚于 Done），查询时机跟随产生时机，**逐秒轮询带超时**（如 30s）优于即时断言；② FAIL 分支必须补资源清理（杀 java），否则误报还留残留进程污染下一轮；③ 判「核验失败」前先区分「事件未发生」与「事件尚未发生」。

---

### #100 「缓存失效当结论」：必须核对谁写谁读两侧接线

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #100（A 类）

- **时间/置信度/module**：260909-04（实际 2026-09-09 17:32 起）；candidate（E1 零改善证伪 + E1b 回收 ~72% 双向实证，judge PASS-with-conditions 条件已应用，用户 confirmed 260909-09）；workflow-patterns / 性能归因（缓存接线域）。
- **来源定位**：`.investigations/camin-perf/{scout-map,perf-record}-260909-04.md`；载体 = `worldgen-core/src/bin-diag/camin_bench.rs`（WG_CA_MIN on/off 双臂）。
- **现象**：WG_CA_MIN 翻默认开后 +125%（bench 口径）。scout C1 静态勘探判定「主管线不回填 terrain_cache → 地形列全量重算 ~2×」——行号证据真实存在（fill_chunk_blocks 从不 insert cache），机制模型自洽。
- **证伪**：E1 按原模型修复（主管线回填 cache）→ **297.4ms，零改善**。真根因是反向缺口：**主管线不读缓存**——读路径（neighbor_terrain）早已把前向邻 chunk 算过并入缓存，管线侧无条件第二次算地形（每 chunk 地形双算）。E1b 改成「管线缓存优先命中 + 未命中回填」→ 289→177.9ms（+125%→+35%），回收 ~72%，三轮行为 hash 逐位不变。
- **根因（机制）**：scout 的静态证据「写侧缺失」是真的，但它不是成本来源——成本在「读侧绕过缓存」。缓存优化的成本模型必须由**两侧接线**共同决定：谁写（回填）× 谁读（命中路径是否真走缓存）。单看一侧的「缺失」即可构成一个证据真实、机制自洽、却完全无效的修复方案。
- **定位（怎么发现的）**：判别实验 E1（scout 自己预置的首选实验）零改善 → 立即证伪原模型 → 回读通路地图发现读路径已回填 → 重述根因为「不读缓存」→ E1b 一步验证回收大头。证据饱和推进：E1 → E1b → E2b（WG_CA_CAP 256/2048 差 <2% 排除 clear-all 雪崩）→ WG_SKIP_FEATURES 分解（残差全在 features 段）。
- **教训/判据（MUST）**：
  1. **缓存类性能课题，归因前 MUST 同时核对「谁写、谁读」两侧接线**——写侧缺失 ≠ 成本来源，读侧绕过才是常见真根因；单侧修复可能完全无效（本例 E1 = 0 改善）。
  2. **静态勘探结论（含行号实锚）也只是候选**——预置判别实验零改善即是证伪信号，立即回数据层重述模型。
  3. 判别顺序红利：scout 把 E1 列为「单点改动直接检验最大候选」的首选实验，使证伪成本 = 一轮 bench。
- **家族索引**：#21（微测形态失配）、#25 案例①（静态结论生产路径可达性核对——本条为其缓存域形态）、#98（修复在生产口径下真生效——本条补「修复方向本身要对」的上游面）。
- **证据**：perf-record-260909-04.md 判别链表（基线 289.1/128.5 → E1 297.4 零改善 → E1b 177.9 → hash 三轮 6908dbfc…/115641b8… 全等）。

---

### #102 缓存 clear-all 惩罚的落点核对

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #102（A 类）

- **时间/置信度/module**：260909-06（实际 2026-09-09 21:51 起）；candidate（CAP 256/2048/65536 三轮配对交错 + B3a 快照双臂 hash 逐位不变 + 交错 ×3 实证；待复用再升）；workflow-patterns / 性能归因（缓存接线域）。
- **来源定位**：.investigations/camin-perf/probe-260909-06.md；载体 = bin-diag camin_bench（WG_CA_CAP 臂 + B3a 3×3 Rc 快照）。
- **观察**：features 侧 per-read 同步消除（B3a 快照：快照命中零锁零 hash）只消 per-read 同步成本（~2%），**不消 clear-all 惩罚**——clear-all 惩罚打在**主管线缓存优先读路径**（#100 的 fill_chunk_blocks 缓存命中读被 clear 波及，命中失效→地形重算），两臂数据实锤：B3a@256 vs B3a@2048 交错 ×3 仍差 ~11%（171.5/169.2/174.0 vs 152.9/153.2/154.0）。容量杠杆（CAP 2048 等效无 clear-all）与快照杠杆（per-read 去同步）各治一路，互补。
- **证据**：CAP 256→2048 稳定 ~10% 增益（三轮交错方向一致）；2048≈65536（更大无增益）；B3a 单独仅 ~2%（三轮全赢但小）；恒等式自检 cap256−cap2048=3.5s ≈ 34 interior miss 差 × 112ms fill 单价。
- **判据（MUST）**：缓存类优化立项/验收 MUST 核对三面：**谁写（回填）+ 谁读（命中路径）+ clear/失效波及面（失效打在哪条读路径上）**——只治命中侧同步或只治写侧，clear 波及的另一条读路径照旧付费。#100「两侧接线」判据的第三面延伸。
- **家族索引**：#100、#101（被取代后其②③残效）、#47（行为不变 hash 门）。

---

### #107 同步接管阻塞单车道调度器（并行度塌成 1）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #107（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260910-04（实际 2026-09-10）；主会话（实测）+ b1 fan-out worker（一手源码静态推导）；**candidate**（数据层实测成立：chunk 级计时双跑一致 + Σ/wall 93% + 池缩放反向旁证；「单车道 busy/inFlight 直接计数」未做 ⇒ 机制命名部分 = **Degraded（静态一手源码，未跑车道占用探针）**，故机制命名建议 candidate 并保留 b1 @idk）；workflow-patterns / 性能结构归因 + 接管形态。
- **来源定位**：`.artifacts/perf-regression-260910-04/verdict-260910-04.md`（candidate，§1 定量闭环 / §2 证据链）；`.investigations/perf-regression-260910-04/record.md` §2.4-§2.5；`.artifacts/perf-regression-260910-04/candidates/b1-choreography.md`（一手源码 file:line 全表）；b2（写回副作用候选）= REFUTED（≤3.7ms/chunk = 0.37% 周期）。
- **现象（错误链）**：1.21.6 生产 5.15× 回归（4225 chunks：vanilla 52s vs coreswap 268s，5.15×；处理臂含历史 per-chunk 日志成本，见本课题错误台账 `perf-regression-errors.md` 的 E6 口径修正）。chunk 级计时：`mixin=51.0ms [jni=47.2 write=3.5 hmap=0.22 scan=0.08 beard=0.04]`、`carve=1.3ms`、`feat=3.1ms`（≈55.4ms/chunk），而同一 Worker-Main 线程「上次接管返回 → 本次接管开始」的 `gap=948ms/chunk`（占周期 95%）；进程 CPU 仅 **1.27-1.7 核 / 24**（vanilla 同仪器 **4.93 核**），线程绝大多数 parked。
- **根因（机制）**：MC 1.21.6 的 worldgen 推进只有**一条车道**——`SimpleConsecutiveExecutor("worldgen")`（`ServerChunkLoadingManager.java:192,196`）+ `ChunkTaskScheduler` **同时只允许 1 个 entry 在飞**（下一个 entry 必须等当前 entry 的 task 全部跑完才 `poll`；`ChunkTaskScheduler.java:44-84`，`pollOnUpdate` 门只在单车道 dispatcher 内读写）。vanilla 在 `NoiseChunkGenerator.populateNoise` 里 `supplyAsync(..., Util.getMainWorkerExecutor().named("wgen_fill_noise"))`（`NoiseChunkGenerator.java:326-353`）把同量级重活甩给 23 线程池，**车道任务只做 µs 级调度**（pending future 就是「把 worker 还回池」的 yield 点）。我们的 mixin 在 `populateNoise` **HEAD** 同步做完 `feedBeardifier + fillChunk + writeChunk` 并返回**已完成** future（`runtime/1.21.6/java/src/main/java/wg/bench/mixin/NoiseChunkGeneratorMixin.java:76-113`）⇒ `ChunkLoader.load` 的 `getNow(null)` 永远非 null ⇒ 同一次车道任务里把整条链（含区域内邻居）一路同步跑完 ⇒ **任何时刻全世界最多 1 个接管在执行**，与线程池大小无关。
- **证据（怎么定位的）**：① **Σ ≈ wall**：Σ(接管 mixin 232.4 + carve 5.4 + features 11.4) = **249.2s** vs 实测 wall 270.3s（Chunky Total 264s）→ 92.2%（**同批同 run** `ct1-inflight-r2`；早次 run 口径 269.1s/290.3s=92.7% 同向）（vanilla 侧 Σ 17.0s vs 60.1s = 28%，重活在池里）；若机制错，coreswap 的 Σ 应 ≪ wall（如 <60%）——b1 的证伪测试① PASS。② **池大小反向旁证**：coreswap `-PcoreswapThreads=1` = 279s（比 234s **更慢**）→ 线程 spawn/池容量不是限流点；vanilla 池 23→4 时 52s→**76s**（**池敏感**），两臂方向相反。③ 算术闭合：4225 × ~55ms ≈ 232s，与 instrument-off 臂 234s 同阶（**推断性归因**，非「wall 就是结构下限」的等式；judge C2 限定）。④ b2（写回语义副作用）REFUTED：可归因项 ≤3.7ms/chunk（0.37%），后续 stage 逐条核对 ≈0（光照不读高度图、4 张高度图必被 FEATURES 重建、post-processing 方向为负、序列化只由内容决定）。
- **判据（MUST，可复用）**：
  1. **性能回归先算「被串行化执行点内的工作量之和」vs wall**——比值 ≈1 即并行度塌陷（本案 93%）；这比逐段优化/逐项排除有效得多：它一次给出「瓶颈在结构不在算力」的定量闭环。
  2. **「线程池大小调参无效 + CPU 占用极低 + 线程大量 park」= 单车道症状三联**（本案：`-PcoreswapThreads=1` 反而更慢 / 1.27-1.7 核 / gap 948ms）。三联齐出时不要再去查 CPU 侧（引擎算力、全局锁、JNI 拷贝）——它们在这条链上**不可观测**（并发恒为 1，锁不会被争用）。
  3. **接管类优化必须对齐原实现的「同步/异步形态」，不能只对齐语义正确性**——我们语义上完全正确（hash 哨兵逐位同），但把本该异步卸到池里的重活同步留在了唯一的串行车道上，形态错即性能错。接管评审 MUST 附一栏「原实现在哪条车道/哪个池上执行、我们的接管点是否保持同样的 yield 形态」。
  4. 反向护栏：Σ≈wall 只证「车道饱和」，不排除上游限流（`ThrottledChunkTaskScheduler maxConcurrentChunks=4`，`ChunkLevelManager.java:49-56`，b1 @idk 未验证）——宣布结构定论前 SHOULD 补车道 busy/inFlight 直接计数（b1 建议测量 2；若 R3 后 wall 仍远高于 vanilla，优先查此）。
- **家族索引**：#83（性能分母/结构场景——本条为「瓶颈在并行结构不在算力」形态）、#100/#102（性能课题归因必须在真实通路上核对多面——本条补「执行位置：哪条车道/哪个池」为性能结构面）、#28（性能 run 串行测量纪律）、#36/#98（执行体与生效口径——本条为「执行位置」维）、新 #109（臂无关尺子）。


#### 发现 #107 修复验证（260910-04 追加）：异步化把并行度从 1 恢复到 23

- **时间 / 发现者 / 置信度 / module**：260910-04（实际 2026-09-10；异步臂 `r3-r1` 日志时间戳 18:13，同步臂 `r3sync-r1` 18:15-18:20，背靠背同批）；主会话（实测，同构建态单变量 A/B + 并发度直读 + 逐块对拍门）；**candidate（同批 A/B + 直证；confirmed 留人类）**；workflow-patterns / 接管形态修复验证（#107 的修复侧）。
- **来源定位**：
  - 修复点 = `runtime/1.21.6/java/src/main/java/wg/bench/mixin/NoiseChunkGeneratorMixin.java:57-58`（`WG_FILL_POOL = Util.getMainWorkerExecutor().named("coreswap_fill_noise")`）+ `:145-149`（同步/异步二选一：`SYNCFILL ? completedFuture(work.get()) : supplyAsync(work, WG_FILL_POOL)`）；A/B 开关映射 `runtime/1.21.6/java/build.gradle:134-135`（`-Psyncfill=1` → `-Dcoreswap.syncfill=1`，默认异步）；并发度仪器 `runtime/1.21.6/java/src/main/java/wg/bench/ChunkTiming.java:27-40`（`inflightEnter/Exit` 原子计数）。
  - 机器可读逐臂记录 = `.tmp/perf-reg-260910-04/results.txt` 第 10-12 行（`r3-r1` / `r3sync-r1` / `vanilla1216-r1`）。
  - 异步臂完整日志 = `.investigations/perf-regression-260910-04/cmd-output/r3-async-r1.log`（第 147 行 `[CHUNKTIME] n=4608` 末行；第 148 行 Chunky `Total time: 0:00:42`；第 139 行 `Rate: 102.7 cps`）。
  - 同步臂完整日志 = `.tmp/perf-reg-260910-04/logs/r3sync-r1.log`（第 165 行 `[CHUNKTIME] n=4608` 末行；第 167 行 `Total time: 0:04:39`）——⚠️ **未归档到 `.investigations/`**（见诚实边界 3）。
  - 逐块对拍工具 = `.tmp/hang-repro-260910/diff_arms.py`；三臂 region 归档 = `.investigations/perf-regression-260910-04/cmd-output/region-{r3,r3sync,vanilla-260910-04}/`；历史双臂基线原文 = `.tmp/hang-repro-260910/diff-result.txt:74`。
  - 上游定责 = `.artifacts/perf-regression-260910-04/verdict-260910-04.md` §3 R3（candidate，待用户 confirmed）。
- **数据（同构建态 A/B，带 run 标识）**：

| 臂 | run id | 接管形态 | Chunky Total | wallgen | serverCpu | 派生核数 | `inflight max` | 每 chunk 线程周期（armAgnostic featInterval，末次报告） | 每 chunk 接管段（mixin） |
|---|---|---|---|---|---|---|---|---|---|
| **r3** | `r3-r1` | **异步**（提交 `coreswap_fill_noise` 池，默认） | **0:00:42（42s）** | 50.1s | 543 | **10.8 核** | **23** | **242.52ms**（n=4411） | 103.47ms〔jni 96.81 / write 6.19 / hmap 0.42 / beard 0.03〕 |
| **r3sync** | `r3sync-r1` | **同步**（`-Dcoreswap.syncfill=1`，同 dll sha `abd7d889…`） | **0:04:39（279s）** | 280.3s | 375 | **1.34 核** | **1** | **1413.65ms**（n=4416） | 53.87ms〔jni 50.19 / write 3.38 / hmap 0.21 / beard 0.02〕 |
| vanilla | `vanilla1216-r1` | 原版（`wgen_fill_noise`） | **0:00:52（52s）** | 60.1s | 316 | 5.26 核 | （无仪器） | （无仪器） | （无仪器） |

  - 派生核数 = `serverCpu / wallgen`（同表两列相除：543/50.1 = 10.84；375/280.3 = 1.34；316/60.1 = 5.26）；三臂同 seed `417950215108767439`、同 region **4225 chunks**（逐臂 `Processed: 4225 chunks` 核对一致）、同 dll sha `abd7d8893d22e030`。
  - **唯一变量 = 同步/异步形态**：**279s / 42s = 6.64×**；R3 后 coreswap 反超 vanilla：**52s / 42s = 1.24×**；并发度直读 **inflight max 23 vs 1**；每 chunk 线程周期 **1413.65 / 242.52 = 5.83×**（与 wall 比 6.64× 同阶自洽）。
  - **同一 Σ/wall 判据（#107/#108）在修复前后翻转**：`r3sync` 末次报告 Σ = sumMixin 248.3 + sumCarve 6.0 + sumFeat 12.2 = **266.5s / wallgen 280.3s = 95.1%**（≈ #107 定责时的 92.2%，即开关确实复现了「车道饱和」旧形态）；`r3` Σ = 476.8 + 7.4 + 15.8 = **500.0s / wallgen 50.1s = 9.98**（≈ 派生核数 10.8）⇒ 同一把尺子从 ≈1 翻到 ≈10-23 量级**（Σ/wall 是核数当量；线程数直读仍是 `inflight max`）。同线程间隔 `gap` 亦从 1224.00ms（`r3sync` 末行）降到 94.58ms（`r3` 末行）。
  - 口径备注：末次报告 n=4411/4416 > region 4225 chunks（+4.4%/+4.5%）——接管计含区域边界外邻 chunk 重生成，属既有语义；sumMixin 是**线程时间之和**（池内多线程累加），不是 wall，勿与 wall 混用。
- **行为等价门结果（全域逐块普查，非零容忍）**：三臂 region 全量逐 chunk 逐 section 对拍（工具 `diff_arms.py`，分母 = 共同 chunk 内「两侧 section 并集」的方块数，故每对分母随 section 存在性微移；`375,554,048 − 375,549,952 = 4,096 = 恰 1 个 section`）：

| 对拍对 | 差异方块 | 分母 | 占比 |
|---|---|---|---|
| r3 vs vanilla | 44,921 | 375,554,048 | **0.0120%** |
| r3 vs r3sync | 45,948 | 375,554,048 | **0.0122%** |
| r3sync vs vanilla | 41,809 | 375,554,048 | **0.0111%** |
| 历史双臂基线（260910-04 前，同作业线上） | 56,214 | 375,549,952 | **0.0150%** |

  ⇒ 三对差值 **0.0111-0.0122% 与历史基线 0.0150% 同量级且不高于它**：R3 **未引入超出既有 run 级非确定的额外内容差**（管线本身有 run 级非确定，历史双臂即非零）。⇒ 门是**同量级门**，不是零容忍门。
- **推广判据（MUST，可复用）——「接管类优化 = 把重活从被串行化的执行点搬到工作池」的验证三件套**：
  1. **① 同构建态单变量 A/B（形态开关，背靠背）**：把旧形态**保留为开关**而不是删掉（本案 `-Dcoreswap.syncfill=1`），同 dll sha / 同 seed / 同 region / 背靠背各 1 run ⇒ 差异唯一变量 = 同步/异步形态。禁止用「改前历史数字 vs 改后数字」代替（跨批 ±20% 摆动带会淹没或伪造结论，#103/#108）。
  2. **② 并发度直读（in-flight 计数：1 → N）**：在被搬动的重活**进出点各加一次原子计数**（本案 `ChunkTiming.inflightEnter/Exit`，随 `-Dcoreswap.chunktime` 门控），直接读出「同时刻在飞数」与历史峰值。判据 = 旧形态**恒为 1**（结构证明）、新形态达到池并发数（本案 **23** = 该池并发线程数）。这是「搬成功了」的**直接证据**，不要只靠 wall 推断。
  3. **③ 行为等价门（逐块对拍，与既有 run 级噪声基线同量级即可，非零容忍）**：逐 chunk 逐 section 全量对拍，判据 = 新形态差值 **≤ 既有 run 级非确定基线**（本案三对 0.0111-0.0122% ≤ 0.0150%）。**零容忍是错的门**——本管线有 run 级非确定（历史双臂同配置即 0.015%），零容忍会产生假阴性并逼出无意义的「逐位对齐」轮次。参考量级：介于噪声基线与基线 1.5× 之间需查；超出量级即拒收。
  - **附加结构证据**：搬动成功后，**同一 Σ(被搬出执行点内工作)/wall 判据应翻转**（本案 0.95 → 9.98）；**arm-agnostic 同尺复核**（#109 的 featInterval 1413.65 → 242.52ms = 5.83×）与 wall 比同阶 ⇒ 三路（wall / 直读并发 / 同尺周期）互证。
- **陷阱（MUST）**：**重活进池后「每 chunk 段内延迟」会上升，不得读成回归**——本案接管段 mixin 53.87 → **103.47ms**（jni 50.19 → 96.81ms），因为同池 23 并发争用；而 wall 反降 6.64×。判据只看 wall / 吞吐，段内数字此时测的是「池内争用下的段延迟」，与单车道时的段延迟**不同物**（同族：吞吐均值 vs 每 chunk 延迟分离铁律）。
- **诚实边界（缺口，不夸大）**：
  1. **同配置 run-to-run 基线对本块未采集**：只有「同构建态同步 1 run vs 异步 1 run」这一对 A/B；按本项目跨 run ±20% 摆动带（#108：234s vs 283s），**6.64× 远超摆动带 ⇒ 方向可信，但幅度是单对读数**；要量级置信区间 SHOULD 补同批 ABBA ≥3 对。
  2. 三臂逐块对拍数字（44,921 / 45,948 / 41,809）**已落盘**（`cmd-output/diff-r3-vs-vanilla.txt` / `diff-r3-vs-r3sync.txt` / `diff-r3sync-vs-vanilla.txt`，18:30 入 MANIFEST）；门可复现（region 三臂归档 + 同归档 `diff_arms.py`）。
  3. 归档链**已补齐**（260910-04 18:30）：同步臂 `cmd-output/r3sync-r1.log`、异步臂 `r3-async-r1.log`、`results.txt`（12 行含 R3 两行）、含 R3 臂定义的 `run_arms2.ps1`、`diff-result-historical-260910-03.txt`、三臂 region `.mca` 全量 sha 均已入 `MANIFEST-sha256.txt`（83 条）。
  4. **worldgen 车道自身的 busy/inFlight 计数仍未做**（#107 判据 4 / b1 @idk）：本块 `inflight` 计的是**接管段在飞数（池侧）**，不是车道占用；「车道已不再是限流点」由 wall（42s ≤ vanilla 52s）与并发 23 推断，仍属推断（上游限流线未排除）。
  5. vanilla 对照臂 `vanilla1216-r1`（52s）**未开** `-Dcoreswap.chunktime`；仪器化对照是 `vt1-r1`（53s，serverCpu 296 → 4.93 核）。跨臂每 chunk 段内数字**不可**与 coreswap 臂直接比（仪器不对称）。
  6. **数字差异标注**：同步形态「每 chunk 线程时间 1325ms」出自 R3 **之前**的 ct1 臂（#109 / verdict §2.3）；本块同步臂**自身日志末值 = 1413.65ms**（+6.7%，同量级）。本条的 A/B 一律引用后者（同 run 同批自洽），1325ms 保留为历史读数，两者不混用。
- **家族索引**：#107（主条——本条为其修复验证）、#108（Σ/wall 判据使用要点——本条给出判据在同一课题上的**翻转**形态）、#109（臂无关尺子——本条补同 build A/B 对）、#103/#51/#18（噪声带 / 跨 run 绝对值不可引）、#83（性能分母 / 结构场景）、#100/#102（归因须在真实通路上核对多面）。

> **⛔ 数值取代（260911-05，§15.4 取代记录，原结论正文不删不改）**——本条 `:1766-1771` **行为等价门表**、`:1773` **结论句**、`:1777` **判据③ 实例数字**全部系**旧读法**产物；规范读法（`.investigations/e5-recompute-260911-05/diff_arms_fixed.py`，唯一改动 = `tag 7` 长度字段 `u1→i4`）同载体复算（旧 → 新，载体 `.tmp/hang-repro-260910/arms/`）：
> - `r3 vs vanilla` 44,921 / 375,554,048 / **0.0120%** → 150,702 / **786,825,216** / **0.0192%**
> - `r3 vs r3sync` 45,948 / 375,554,048 / **0.0122%** → 135,986 / **786,825,216** / **0.0173%**
> - `r3sync vs vanilla` 41,809 / 375,554,048 / **0.0111%** → 155,818 / **786,825,216** / **0.0198%**
> - 历史双臂基线 56,214 / 375,549,952 / **0.0150%** → 141,533 / **786,825,216** / **0.0180%**
> ⇒ **结论修正（关键）**：`:1773`「三对差值 … 与历史基线 0.0150% 同量级且**不高于它**」在新口径下**不成立**——三对 0.0173-0.0198% 中，跨形态对（0.0173%）仍 ≤ 复算基线（0.0180%），但**跨实现两对反超基线 0.0012-0.0018pp**；故「**R3 未引入超出既有 run 级非确定的额外内容差**」这一**因果指认失效**（量级仍同阶）。`:1777` 判据③ 的**门性质（同量级筛选门、非零容忍、参考量级区间）仍成立**，但其**实例数字与「≤ 基线」读法**须改为「同量级 + **基线须同口径复算** + 锚分形态/分维度」（见 #111 取代条）。取代链：`record-260911-05.md` §3/§4。

---

### #109 臂无关「每 chunk 线程时间」尺子

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #109（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260910-04；主会话（实测，`-Dcoreswap.chunktime=1` 的 featInterval）；**candidate**（单 region 单会话口径）；workflow-patterns / 测量手法。
- **手法**：在**两侧都会经过**的方法（本案 `ChunkGenerator.generateFeatures` HEAD）打同线程间隔点，测「同一线程两次到达该点的间隔」= 该线程的**周期**。本案 coreswap **1325ms**（完整 run；早次 run 1422ms，跨 run 漂 ±7-12%）vs vanilla **299ms**（比值 **4.4×**），与 wall 比 283/53 = **5.34×** 同阶自洽。
- **价值**：这是**臂无关**的尺子——不依赖阶段计时探针（避开多线程探针污染铁律）、不依赖两臂载体/阶段口径一致；它天然包含「排队 + 执行」，测的是线程周期而非 CPU 成本，正好与「并行度」这一待测量同构。
- **陷阱**：① 它测的是周期不是成本——两臂同期比同阶**不能**反推「谁算得多」（要算量另配计数器）；② 间隔点必须选两侧共有的方法（选错成只在一侧经过的点，比值即无意义）；③ 与 wall 比值对照时须声明 wall 口径（Chunky Total vs 生成段）。
- **家族索引**：#107/#108、#83（分母）、#103（噪声）。


#### 发现 #83/#51 家族补充案例（260910-04）: 驱动参数「看起来设置了但无效」——Chunky 1.4.40 无 `chunkradius` 子命令，实际一直用默认 radius 500 方块 = 4225 chunks；脚本自述的「已设置」不构成生效证据

- **发现时间 / 发现者 / 置信度 / module**：260910-04；主会话（回显核对 + 逐臂 chunk 数核对）；**candidate**（实测回显 + 4225 逐臂核对一致）；workflow-patterns / 口径纪律（#83 分母口径 + #51 跨 run 可比性）。
- **现象**：驱动脚本历来自述并 echo「chunkradius=56」，历史文档/交接一并转述「chunkradius=56 → 4225 chunks」；实际 Chunky 1.4.40 **无 `chunkradius` 子命令**（回显 `Incorrect argument`），区域一直是**默认 radius 500 方块 = 4225 chunks**（逐臂核对一致）。
- **根因（机制）**：口径声明来自**驱动脚本自述**而非**被测程序回显**——脚本把「我发了这条命令」当「参数生效」；Chunky 对未知子命令不中断脚本、只回一行 `Incorrect argument`，脚本自己的 echo 文案遂成第二真相源，并被下游继续转抄（scout 成本图 `pipeline-cost-map.md` §0 亦照抄失真措辞）。
- **判据（MUST）**：① **口径声明（region 规模/采样范围/参数集）MUST 来自被测程序回显或日志，不能来自驱动脚本自述**；脚本自己 echo 的「已设置」文案零证据力（与 #37/#81「生效证据必须行为化」同族）。② 转述历史口径前先核被测程序回显（#90 转抄漂移家族——失真措辞会跨文档存活）。③ 本例各臂都吃同一默认值故**基线仍可比**（4225 逐臂一致）；**若只有部分臂受影响，就会直接变成假差异**（#20/#53「默认值当公理」的风险面）——这正是此类口径失真必须记录而非「无害」的原因。
- **家族索引**：#83（性能分母分场景——本条为「分母口径被脚本自述污染」形态）、#51（跨 run 可比性——同默认口径才可比）、#37/#81（生效证据行为化）、#20/#53（默认值当公理）、#90（转抄漂移）。

---

### #114 沙箱禁 attach 时「门控看门狗自打线程栈」

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #114（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260910-06；主会话（一手实测：attach 全拒 + 看门狗 dump 一步读出阻塞链）；**确定**（本机沙箱复现 + 应用成功一次）；workflow-patterns / 停滞定位手法（build-tooling #46 的**方法侧**配对条）。
- **来源定位**：`runtime/1.20.1/java/.../wg/bench/StallWatch.java`（59 行；post 快照 + `SHA256SUMS.txt` 登记 sha256）；挂点 = `CppBridge.init` 末尾 `StallWatch.start()`；栈解析件 `cmd-output/parse_stallwatch.py`；应用实例 = errors E1 的 `[STALLWATCH]` 段。
- **手法**：`-Dcoreswap.stallwatch=<秒>`（**默认完全关**：启动读一次 prop，未设即 return ⇒ 生产零成本）；打开后起 daemon 线程（名 `coreswap-stallwatch`），每 N 秒把 `Thread.getAllStackTraces()` **全量**打 stdout（前缀 `[STALLWATCH]`，逐线程含 `name/id/state/daemon` + 每帧 `at`），随 gradle 日志落盘即可 grep；幂等启动（`started` volatile + `synchronized` 守卫）；dump 段整体 `catch (Throwable ignored)`——**看门狗自身绝不打断主流程**。
- **价值**：沙箱禁 attach（`jstack`/`jcmd` exit 1，build-tooling #46）时「卡死」类故障本**没有观测面**；自打栈把线程栈变成**日志内证据**——本案一次 dump 即读出阻塞链，成本比反复猜机制低一个量级（对照：纯日志/`chunky progress` 只能判「停」，不能判「为什么停」）。
- **陷阱 / 纪律**：① 默认关 + 间隔可调（诊断门控纪律，同 #11 家族：不得改生产语义与成本）；② **间隔即成本**——全线程栈 dump 在重并发下不便宜，按等待窗口取值（本案 30s），不要 1s 级常开；③ dump 是**瞬时快照**，单次可能打偏 ⇒ 与 #106「双 dump 间隔观察」配合：两帧同点 = 钉死，帧在移动 = 进展崩塌（另一态）；④ 输出走 stdout 需独立前缀与既有噪声区分。
- **家族索引**：build-tooling #46（沙箱 attach 拒访——本条为其**方法侧**配对）、workflow-patterns #106（双 dump 三态观察法——本条为其在禁 attach 环境的落地通道）、#113（本条能力的首个应用实例）。

---

### #119 JVM 峰值内存 ≠ 存活集（须固定堆或读 GC live-set）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #119（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260910-08（事实，自查拦截未外泄）；主会话（交替复跑自证 + 固定堆判定实验）；**candidate**（机理 + 判定性实验；confirmed 留用户）；workflow-patterns / 性能指标语义（#83 分母分场景的**内存指标维**）。
- **来源定位**：`.investigations/perf-release-260910-08/errors-260910-08.md` E4；`MANIFEST.md` §5（内存探针全表）。
- **现象（错误链，五段式）**：
  - **现象**：单对测量得 1.0.28 `maxWs ≈ 5973 MB` vs 1.0.27 `2713 MB`——看似「1.0.28 多占 3.3 GB」的内存回归。
  - **根因（机制）**：JVM `WorkingSet`/`PrivateMemory` 峰值 = **G1 堆高水位**（未设 `-Xmx` 时 JVM 默认 MaxHeap 12.7GB），由分配节奏与 GC 时机决定，**不是存活集**——同 dll 同配置交替复跑 4 次：`6505 / 4666 / 2984 / 5976 MB`，**同配置自身摆动 1.7×**，单对差值毫无判别力。
  - **定位**：不轻信单对读数，做**交替复跑**（1028/1027/1027/1028）——组内摆动 ≥ 组间差 ⇒ 指标语义存疑；再查 `build.gradle` 未设 `-Xmx` ⇒ 高水位解释成立。
  - **修复/判定**：改**固定堆判定**——`-Xmx2G` 两臂：1.0.28 = 36 s / 469 cpuSec / 峰值 3043 MB，1.0.27 = 35 s / 469 cpuSec / 2223 MB ⇒ 两引擎在玩家常用堆档下均满速跑完，**无阻塞性内存回归**；两臂峰值差仍在已证摆动带内（n=1/臂）**不作等价结论**（只作「无阻塞证据」）。
  - **教训**：拿单对峰值差说事 = 用堆高水位冒充存活集。
- **判据（MUST，可复用）**：
  1. 内存回归判定 MUST 用固定 `-Xmx`（判定「常用堆档下能否满速跑完」）或 GC 日志 live-set，**禁止**直接引用无界堆的 WorkingSet 峰值；
  2. 任何内存指标对比前 MUST 先测**同配置 run-to-run 摆动带**（本机该指标 1.5–1.7×）——组间差被组内摆动覆盖 ⇒ 不作结论（与 #51「噪声基线前置」同构，#119 是其在内存维的实例）；
  3. 「无阻塞证据」与「等价结论」分开写：n=1/臂只能支持前者。
- **家族索引**：#51（噪声基线与信号同阶）、#103（±10% 噪声带——本条为内存维同构）、#83（指标绑场景）、#64（未受控观察降级——单对读数不结论）。

---

### #122 并发度 = 调用方池宽（引擎线程参数是死参数）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #122（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-02 提出、260911-03 成文（exec 模式验证后补）；主会话（javap 直读 + 超订曲线 + exec 三臂实测）；**candidate**；workflow-patterns / 并发性能测量（#20 死参数家族的并发域形态）。
- **来源定位**：`.investigations/vivo-stutter-260911-02/{f2-phase1-cost-split.md, vanilla-facts-javap.md}`；`.investigations/vivo-stutter-260911-02/exec-mode-result-260911-03.md`；NEXT_SESSION 纪律要点 3。
- **观察**：vivo 卡顿课题中，引擎侧线程参数（spawn 线程数）在 vivo 集成路径上是**死参数**——引擎只 spawn 空转线程，真实 fill 并发由**调用方池宽**（vivo/调用方的共享执行器池宽）决定。按引擎参数调并发/读并发会得出与实际无关的结论；超订曲线（`-XX:ActiveProcessorCount` 2/8/12/16）实际量的是调用方侧并发上限的效果。
- **证据**：javap 直读 vanilla 三层映射确认调用形态同构（共享池提交）；同一引擎 dll 在不同调用方池宽下 wall/fill 差异显著，而引擎自身线程参数任何取值都不改变行为（参数只 spawn 不参与调度）。
- **如何利用（可复用判据）**：① 测量/归因并发性能前，第一步画「谁把任务提交进哪个池」的调用方地图，引擎线程参数只作死参数排除项；② 判别实验改「线程数」类参数前先核参数真实消费点（#20 恒等式自检的并发实例）；③ 引擎向多宿主交付时，真实并发模型写在调用方契约里，不写在引擎构造参数里。

---

### #124 「先量后改」（优化被测量推翻的例子）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #124（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-03（260911-02 发生、本块成文）；主会话（F2 Phase 1 成本拆分 + 后续 exec 决策）；**candidate**；workflow-patterns / 性能优化决策流程（AGENTS.md 端到端性能铁律的流程面实例）。
- **来源定位**：NEXT_SESSION 纪律要点 1 + 开工点 4；`.investigations/vivo-stutter-260911-02/f2-phase1-cost-split.md`；`.investigations/vivo-stutter-260911-02/exec-mode-result-260911-03.md`。
- **观察**：vivo 卡顿的直觉修法是优化写回（F2，跳空气等）。动手前先做成本拆分测量：写回面总上限 6.5%（分项 6.2%/0.4%/0.1%），拿不到需要的量级；而测量同时把争用面指到共享池 → 转 exec 模式（fill 整体搬自有池），同 run 族 wall −12.5%。
- **证据**：F2 成本拆分四段数据（scan/write/height/fill 占比）；exec 三臂对照表（40s→35s，fill 102.8→70.1 ms/chunk）。
- **如何利用（可复用判据）**：① 任何性能优化动手前先做**成本拆分**（各段占 wall 比例），上限核算 < 目标量级即放弃该方向，把预算转给测量指向的面；② 「上限核算」与「端到端对比铁律」配套：上限否决是免写码的端到端推演；③ 本条与既有「诊断代码不入热路径」等判据同属「测量先行」家族——测量不仅验证优化，还**毙掉**优化。

---

### #131 跳过型写回优化等价判据须用精确谓词

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #131（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-05；主会话（A1a 实施 + 三维补跑）+ judge subagent（C4 指出维度覆盖、C5 指出谓词弱于前提）；**candidate**（源记录 = candidate，条件已应用；confirmed 留人类）；workflow-patterns / 等价性判据与证据形态（**#115/#116 的「跳过型优化」面**）。
- **来源定位**：`record-260911-05.md` §3 A1a（`:26-42`，三维表 `:33-37`）；judge `review-260911-05.md` C4（`:23`）、C5（`:24`）+ §3 A1a①/②/③（`:37-39`）；**落盘代码（旧稿实读）**：`versions/1.20.1/java/src/main/java/wg/bench/CppBridge.java:541-543`（`SKIPAIR` A/B 开关）／`:600-603`（严格谓词 `!sec.getBlockState(x, sy, z).isOf(Blocks.AIR)` + 注释转引 vanilla 参照 `Heightmap.java:53`）／`:645`（`[WB-CHECK] air_skipped=…` 输出）。
- **观察（现象）**：`a1-skipair0`（旧形态，逐格写含空气）vs `a1-skipair1`（新形态，跳过空气）双臂 `air_skipped = 276,171,456`、`stale_nonair = 0`；judge C4 指出校验臂只覆盖 overworld 而 `writeChunk` 三维共用 ⇒ 主会话补跑 `wb-ow/wb-n/wb-e` 三维（`air_skipped` 2.76 亿 / 1.95 亿 / 1.55 亿，`stale_nonair` **全 0**），把「单维实证 + 机制外推」升为**三维实证**。判据谓词最初写 `!isAir()`，judge C5 判为**弱于所需前提**，改为 `!isOf(Blocks.AIR)`。
- **根因（机制）**：被跳过的写是「写 `minecraft:air` **默认态**」，而 `isAir()` 是**语义类**谓词——它把 `cave_air`（blocks.json 730）/ `void_air`（729）也算「空气」。持这两类状态的格子**旧形态会被改写成 air、新形态不会** ⇒ 用 `isAir()` 时这类格**不进违例计数**，等价性证明出现**系统性漏计**（漏计的正是需要被发现的格子）。**判据谓词必须精确等于「被跳过的写实际要写入的值」**，不能用「写值所属语义类」。
- **定位（怎么发现的）**：judge 拿项目自带 vanilla 参照 `Heightmap.java:53`（用 `isOf(Blocks.AIR)`）与实现侧对照，指出谓词弱于前提；`blocks.json` 的 730/729 给出被漏计的具体 id。
- **修复（处置）**：谓词改 `!isOf(Blocks.AIR)`（已落盘）；三维复测仍全 0；`-Dcoreswap.skipair=0` 保留旧形态开关（**常量折叠 ≠ 生产零分支**：生产路径新增每格一次 `id==0` 判断，judge I4）。
- **判据（可复用）**：
  1. 跳过型优化的等价性前提 = 「被跳过的格子当前**恰等于**将要写入的状态」——谓词 MUST 用与写值**同域**的精确比较（vanilla 参照亦用 `isOf(Blocks.AIR)`），**禁止** `isAir()` 这类宽于写值的语义类谓词；漏计方向是**把违例算成通过**（假阴性）。
  2. **等价证据形态 = 前提全格实证**：对**每一个被跳过的格子**做一次违例计数并要求 = 0（本案 `stale_nonair`），**全格、不抽样**；可在「写回后指纹」不可得时承载 Full 层证据（本案写回后 post-write hash 尚未做，即用前提全格实证替代）。
  3. **共用写路径 ≠ 覆盖证据**：`writeChunk` 三维共用代码，但校验臂只跑一维时 MUST 声明「单维实证 + 机制外推」（附外推依据 = 三维 mixin 均 `populateNoise` HEAD cancel，`NoiseChunkGeneratorMixin` 279/333/364）**或补跑**——「补跑一轮」通常是最便宜的外推→实证升级手段。
  4. **无隔离 A/B 的清理项，其输出中立性由「跨构建内容指纹全等」承载**：A1d（clamp 清理）未做单变量隔离 A/B，证据 = A1d **前**构建（`dd3b645f`，size 2457088）与 A1d **后**（`838e8979`，size 2457600）逐 chunk 指纹全等（#116 的「跨执行体等价」形态；「免重建历史基线」的替代获取方式见 #76）。
  5. vanilla 机制依据（judge 独立核对 `ChunkSection.java:60-93` + `PalettedContainer.java:158-162`）：`ChunkSection.setBlockState` 只在 `isAir` 变化时增减 `nonEmptyBlockCount`；`PalettedContainer.swap` 同值时写回**同一 palette index** ⇒ 对「当前即 air 默认态」的格子写 air 是语义 no-op（机制指纹 → algorithm-fingerprints #25）。
- **家族索引**：algorithm-fingerprints #25（本条机制指纹）、#23（同 section 两套计数语义）、compiler-idioms #6（raw id vs state id 双域——谓词精确性同族）、#115/#116（等价性门与指纹载体）、#42（静态机制断言未实测当公理）、#110（前提/可达性登记）、#14 补充案例（门层）。

---

### #135 优化池条目的成立前提必须一手源核对

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #135（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-05；主会话（A1c 一手源核对）+ 用户裁决（HOOK-2 放弃实施）；**candidate**（用户已裁决弃项；判据本身未经二轮实践）；workflow-patterns / 优化立项纪律（**#25 静态调研结论失真家族 + #110 可达性家族**）。
- **来源定位**：`record-260911-05.md` §3 A1c（`:51-56`）；一手源 = `.tmp/scout-260905-08/mcsrc/net/minecraft/world/Heightmap.java:37-71`（材料转引，未复读）；`.artifacts/index.yaml`（主会话登记「A1c 前提被 vanilla `Heightmap.java:37-71` 证伪（本就单遍）→ 用户裁决不实施」，旧稿实读）。
- **观察（现象）**：优化池条目「**6 张高度图全量重扫**」被一手源证伪——vanilla `populateHeightmaps` **本就单遍**：每列 (x,z) 只做**一次**下行扫描，6 个类型的谓词**在同一次扫描内**逐个匹配并移除（`objectListIterator` + `back(i)`）。⇒ 残余优化只能是「读 `buf`（raw id）替代 `chunk.getBlockState`」，但 `Heightmap.set` private、storage final ⇒ 外部写入须反射或自实现位打包；该项成本 = 0.42ms/chunk = **0.4%**（f2 成本拆分，**上一工作块数值、本块未复核**）⇒ **代价与风险 > 收益**，用户裁决放弃，记「已评估·不实施」（❌ 前提被证伪）。
- **根因（机制）**：优化池条目通常来自**二手机制描述**（「6 张各扫一遍」= 描述者的机制假定），立项时未与一手源核对；一旦该假定不成立，条目追求的收益**基础整体消失**。
- **判据（简记）**：① 优化池条目进入实施前 MUST 一手源核对**其成立前提**（核「被优化的机制是否真如描述那样工作」，不是核收益数字）；② 前提被证伪 ⇒ 记「**已评估·不实施**」+ 残余项 + 成本/风险核算，**不许默默丢弃**；③ 弃项记录同时防止下一轮把同一描述重新立项；④ 「成本拆分数值来自更早工作块、本块未复核」须随引用声明（#18/#134）。
- **家族索引**：#25（静态调研结论失真）、#110（可达性证明三件套）、#110 补充案例（优化不可达 ≠ 优化失败）、#42、#124（先量后改）。

---

### #147 减法归因前必须有分段直接计时（余项小可能是余项没测）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #147（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260914-04；worker（probe-verdict）+ 主会话探针实测 + judge §15.4 取代指示；candidate；workflow-patterns / 性能归因方法（#134/#102 家族延伸）。
- **来源定位**：`.investigations/light-round3-260914-04/probe-verdict-260914-04.md` §1 + record §1；被证伪结论 = 12-lighting.md L94（round2 减法口径「Java 段≈0.15ms/chunk」，§15.4 取代）。
- **现象/根因**：round2 由 e2e 减法推出「Java 收集/JNI 侧开销已基本消除」（3.5s ≈ 内核份额预测 ⇒ 余项记 ≈0.15ms/chunk）；round3 分段探针直接计时 = **collect 4.5ms/chunk，30×**——减法余项被「预测吻合」锁死，实际上内核份额预测本身有偏差、余项被吸收进「吻合」里。对价模型重算（ON 7.3 = collect 4.5 + native 2.8 vs vanilla ~5.6，gap 1.73ms×2025≈3.5s）双锚自洽。
- **判据（可复用）**：**减法余项（e2e 总量 − 已计量段）在用作优化排序/裁剪依据（「X 段已消除，下一头在 Y」）之前，MUST 对该段做一次分段直接计时探针**——减法的「吻合」只约束总量，不约束分账；「预测吻合 ⇒ 余项≈0」是把分辨率不足当结论（#102 量级核算 + #134 减法归因家族的**授权门槛**形态）。成本 = 一个分段计时探针（本例 ThreadLocal 累计/均值即可），远小于按错误分账排错的优化序。
- **家族索引**：#134（减法归因口径）/ #102（量级核算排除法）——本条为其 MUST 前置条件；#22（自由参数凑数——「吻合」作证据的反面形态）；#128（口径纪律：串行 per-chunk vs e2e wall）。

---

### #187 读写并发义务判定先核读者门字段级内存语义

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #187（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260918-10；主会话（scout R1-R9 读者清单 + T2 三候选收敛）+ fan-out worker（.b1/.b2/.b3，其中 .b2 自证伪）；**candidate→confirmed（2026-09-18 用户授予）**（Degraded 全静态一手源对拍 + 双树 sha256 7/7 对账；judge PASS-with-conditions 条件已应用）；workflow-patterns / 并发读侧义务判定（**论证判据，不含本块具体判定结果**——判定在 `.investigations/r9b-light-260918-10/record.md`）。
- **来源定位**：`.investigations/r9b-light-260918-10/record.md` §1（三候选收敛裁决）/ §2（mcsrc 版本疑点消解）；候选件 `.b1-candidate-hb-covered.md`（成立）/ `.b2-candidate-real-gap.md`（不成立·自证伪，本条反面教训来源）/ `.b3-candidate-vanilla-isomorph.md`（成立·限缩形态）；一手源锚点：`ProtoChunk.java:42`（`private volatile ChunkStatus status`——读者门语义的整个支点）、`ChunkStatus.java:361-362`（volatile 守卫读 + setStatus = volatile release 写，doWork 后的 thenApply 内）、`ServerLightingProviderMixin.java:303-318`（读者 = 裸引用 :307 + `getStatus().isAtLeast(FEATURES)` 门 :313）、`ChunkLightProvider.java:72-77`（vanilla 读者连门都没有）。
- **判据（可复用）**：
  1. **读者×写者并发义务判定，先核读者门的字段级内存语义，再谈 future join 论证**——「读者拿裸引用 + 轮询 status 门、不 join writer future」的形态**看似在 #143 的 future 链可见性论证之外**，实则该 volatile status 字段**独立构成 release/acquire HB 对**（写者 plain 写 → setStatus volatile 写 = release；读者 volatile 读 = acquire，Mixin:313；门过即 NOISE 段全部 plain 写可见，含 BulkWb :205-209 换容器+计数）。**⚠️ 传递边要点（防简化版误用，judge MUST 级意见）**：release/acquire 是**逐写逐读配对**——读者 acquire 的是「最近一次 volatile 写」（如 FEATURES），不是写者那次（NOISE）；跨 status 传播 MUST 由一条显式传递边承载（本案 = `ChunkStatus.java:361` 的 **volatile 守卫读**：下一 status 写者写前必先 volatile 读 status ⇒ synchronizes-with 前序 release、继承其全部 plain 写；或 CompletableFuture 依赖链），任一即足。**无守卫读变体上「volatile 门即 HB」不自动成立**——套用本判据前必须找到那条传递边。**反面教训（错误优先）**：本例 .b2 候选以「status 普通写且无同步边 ⇒ 不 join future = 无 HB」立「真缺口说」，一轮一手源实读即自证伪——前提里「普通写」不成立（ProtoChunk.java:42 volatile，两棵参照树逐字一致）。**判错方法：见到「轮询门」先 grep 门所读字段的声明（volatile / CAS / 普通），这一轮 grep 成本远低于在「无 HB」前提下推整条缺口论证。**若字段确为普通写，才轮到 future join / 池共享 / 票调度等次级承载机制排查。
  2. **「检测面盲区 ≠ 正确性缺口」**：sentinel 类在飞检测器对某类参与者（本案读者）零覆盖，只说明「重叠不可观测」（检测覆盖缺口），不构成存在 data race 的证据——两者 MUST 分开裁决。本例读者不登记 SENTINEL_ACTIVE（BulkWb.java:97-102 只登记写者） ⇒ 检测面盲区（OQ-4），而正确性由判据 1 的 volatile 门闭合；加固选项（读者登记 / future join）从「义务修复」降级为 SHOULD 级可观测性增强，且「volatile 化」一臂实为无操作（字段已是 volatile）。混淆两者的代价 = 给不存在 race 的形态立项修 race（.b3 曾滑向此）。
  3. **同构义务的新站点 ≠ 零新增面**：CoreSwap mixin 新增读者站点（R1/R2）替换 vanilla 同职责槽位（LIGHT status 站），获取途径同构（同一 ChunkProvider 裸引用通道）且门更严（vanilla 传播读无门，ChunkLightProvider.java:72-77）——成立形态 =「同构义务的新站点 + 写者等价替换」，**不独立于判据 1 的 HB 论证**；读者读面扩展处（如 packed 路径 writePacket 迭代容器内部，Mixin:358）的闭合仍依赖门内无并发写者论证，不能由「同构」一词带过（.b3 §4② 限缩）。
- **家族索引**：#143（「单写者不变量」四件套——本条是其「可见性链」件对**读者形态**的扩展：#143 论证消费者走同一 future 链，本条论证消费者不碰 future 链时 volatile 门独立承载 HB）、#36 家族（交接前提廉价验证精神面——.b2 自证伪即「前提先过一轮一手核对」的正面执行）、#90 家族（机制措辞按源码不按直觉——「volatile 字段轮询门」读作「无同步边」即直觉错误）。

---

### #190 并发 stderr 诊断行须容忍交错残缺（残缺率门双档）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #190（A 类）

- **发现时间**：260919-02（2026-09-19）
- **module**：workflow / 诊断输出通道解析
- **现象**：并发臂日志中 `[LIGHTPHASE]` 行被其他诊断行（FP-FILL/FP-LIGHT）从字节流中间切入，产生缺 key 的残缺行（R2-on1 5/457=1.09% / on2 19/457=4.16% / on3 8/457=1.75%）；提取脚本按全 key 校验直接 KeyError 崩溃（现场样本 R2-on1 log:6991/9354/10193/10235）。
- **根因（机制）**：并发多线程写 stderr 无行原子性保证，交错产生**结构性残缺行**是输出通道的固有形态而非数据缺陷；解析器隐含假设「每行要么完整要么不存在」，该假设在并发 stderr 下不成立。
- **定位（怎么发现）**：KeyError 崩溃暴露 → 回查原日志行号确认残缺行的物理交错形态。
- **修复**：判据追补残缺行条款（§3.7）：解析器按全 key 校验 + 残缺率门双档——**≤5% 如实报告继续判定 / >5% 整臂 VOID**；条款 commit 080d6e7 时序实证早于全部采集日志（追补先于数据被消费）。实测 on2 4.16% 贴线通过，idk-4 登记复跑 VOID 预案。
- **教训（可复用判据）**：
  1. 并发 stderr 诊断行的解析器 MUST 按全 key 校验且**不因残缺行崩溃**——残缺行计入统计（剔出数据面、进入判定面），裸 KeyError 既废整臂采集也不给出「还能不能信」的判据。
  2. 残缺率门（报告/VOID 双档）把「输出通道质量」变成判定面的一部分；阈值**随判据预登记**（时序先于数据），防事后挑臂。
  3. 贴线臂（如 4.16% vs 5%）MUST 登记复跑预案与支撑臂独立性，不留悬置。
- **家族索引**：#162（消费侧定性回原始日志抽样——本条是解析器侧预登记形态）、#112（判据与采集同批/时序锚）、#154（判据分支覆盖灰区声明——贴线登记形态）、#160（VOID 断链——>5% 即 VOID 非零退出）。

---
