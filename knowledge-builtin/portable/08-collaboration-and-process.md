---
volume: 08
title: 协作与流程纪律
scope: 交接、审查门、fan-out、知识库、文档纪律
source: CoreSwap knowledge/discovered（A 类条目重组，正文原样）
status: draft
---

# 08 · 协作与流程纪律

> 覆盖范围：交接、审查门、fan-out、知识库、文档纪律。条目正文自 CoreSwap 知识库原样搬运（A 类 = 跨项目可复用），行首出处可回查原条目。

## 目录

- #1 judge 审查门是强制环节，收敛门 ≠ 自评
- #2 「机制未明」大排查初期先做 scout 勘探
- #7 多疑点冲突必须并行 fan-out
- #60 回归核查走确定性 dump 载体（judge 建议也要廉价预检）
- #73 fan-out worker 交付「让渡清单」
- #86 目测快照（F3 坐标）不可作交接物
- #87 跨版本枚举新增常量静默落 catch-all
- #90 交接清单条目转抄漂移（机制/限定词失真）
- #185 数字型交接 claim 的「合法过期」
- #193 接手第一动作 = git HEAD vs 交接文档交叉核对

---

### #1 judge 审查门是强制环节，收敛门 ≠ 自评

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #1（A 类）

- 发现时间：2026-08-09；来源：CoreSwap -288 课题（14 轮分析全主会话自评，收尾补 judge 抓到 5 项问题）；置信度：确定；module：工作流
- 观察：v0.8 收敛门「主会话直接闭环」被误解为「自评即可」——漏了「+judge 审查门」。自评无法发现自身盲点：-288 的差异构成表不闭合 23%、phase13 归纳失真（「强候选」写成「✅」）、AQF 高位垃圾值未说明、retry cap 超限未记录——全部由补位 judge 抓到
- 如何利用：
  - **confirmed 授予前 MUST judge**（用户提醒才补 = 失败）
  - **重大转向 MUST judge**：结案重开、根因定论（如「C++ 无 bug」）、范围决策
  - **各阶段结论（candidate 授予）也应 judge**
  - **计划阶段就预置 judge 步骤**（todo 列表含 judge 项，不事后补）

---

### #2 「机制未明」大排查初期先做 scout 勘探

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #2（A 类）

- 发现时间：2026-08-09；来源：CoreSwap -288 课题（直接跳单点定位，carvers 晚发现 4+ 轮）；置信度：确定；module：工作流
- 观察：「入口已明」（有 mismatch 明细/坐标）≠「机制未明」（不知道差异来自哪个子系统/阶段）。-288 直接做密度层→aquifer→Beardifier→caves 树单点排查，绕了 4 轮（超 retry cap）才发现含水层 water = **CARVERS 阶段**（NOISE→CARVERS→SURFACE→FEATURE 管线摸底本该第一轮做）
- 如何利用：
  - 机制未明类大排查：初期 MUST scout 勘探（管线阶段/子系统依赖摸底），禁止主会话直接跳入单点定位
  - 勘探产物（.investigations/ 管线地图：MC 生成阶段 NOISE→CARVERS→STRUCTURE→FEATURE→SURFACE + 各阶段负责子系统）作为定位前置
  - 反模式警示：「差在 density 层」这类早期定论，若未先排除后续阶段（carvers/FEATURE）的产物差异，会误导整个排查

---

### #7 多疑点冲突必须并行 fan-out

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #7（A 类）

- 发现时间：2026-08-09；来源：CoreSwap -288 未闭合课题（B3 (a)/(b) 子候选自推多轮 + 04 篇结论冲突）；置信度：确定；module：工作流
- 观察：当判定树分叉出 ≥2 个互斥机制候选时，主会话「逐个自推」看似收敛（每个候选都可线性验证），实际会陷入深钻循环（-288 的 B3 (b) 子候选：splitter 复现→液面链→est→r/s/t 点多轮才收；期间用户两次提醒「派 worker」「启动 judge」）。并行 fan-out 各派一个 worker 验证一个候选，一轮出全部结论，效率量级提升
- 如何利用：
  - **分叉即 fan-out**：判定树出现 ≥2 互斥候选（含子假设再分叉、知识库结论与新证据冲突）→ MUST 并行派 worker（core.fanout 产 .bN），禁止主会话逐个自推
  - 触发场景三：① 同一现象多机制候选（e 翻转/pocket/Beardifier）② 旧结论 vs 新证据冲突（04 篇「Java e=0」vs NOISE-BLK NOISE 阶段 stone）③ 子候选分叉（(a) splitter 差/(b) 液面输入差）
  - **不因「候选小/看起来简单」自推**——自推的判断成本（上下文连续性）远高于派 worker 的隔离成本
  - 三触发点并列独立：scout（机制未明勘探）→ fan-out（多假设分叉）→ judge（结论审查），任一触发即执行
  - 反模式警示：主会话深钻到「第二轮仍无定论」时自查是否已分叉——是则立即 fan-out（AGENTS.md fan-out 强制触发点 2026-08-09 固化）
### 发现 #8」，该文件当前最大为 #7）；
- `knowledge/INDEX.md` 分类入口「工作流模式」行的说明列末尾追加「、接管单阶段后的后续阶段上下文依赖（2026-08-31）」。

---

### #60 回归核查走确定性 dump 载体（judge 建议也要廉价预检）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #60（A 类）

- **发现时间/发现者**：260906-05（实际 2026-09-06），core.worker subagent 草稿 + 主会话应用；来源课题 CONCERN-2 回归闭环。
- **module**：workflow-patterns / 回归核查载体选型（#51/#52 家族第二例 + 判据收敛）
- **现象**：CONCERN-2 存档三臂对拍 1.0.25 vs 1.0.26 = ow 2206 / nether 21511 mismatch（疑似回归），但同 dll 两轮重跑互差 ow 5012 / nether 23025 与信号同阶。
- **根因**：Forge+本环境跨 run Java 装饰层非确定性（OW 差异 top 全为 spruce/pine 树）混入比对对象——载体信噪比不足，对恒等变换类核查原理上不可裁决，非被测代码问题。
- **定位**：先跑廉价预检（同 dll 重跑基线）→ 信号/噪声同阶即判载体不可裁决，切换而非加跑。
- **修复**：纯 Rust 确定性区域 dump（idk7_region_dump ow + concern2_nether_dump nether，固定快照 + SHA256 对拍，无 Java 装饰）→ Rust 跨 run SHA 全等，旧代码 99b8034 vs HEAD 双维度 SHA 全等 → 无回归，证据强于原建议存档 A/B。
- **判据（MUST ×2）**：① 恒等变换类回归核查一律走确定性 dump 载体；仅覆盖装饰层时用存档载体且前置噪声基线（#51）+ chunk 配对差分，信号/噪声同阶即弃比。② judge/交接建议里的「补跑 X 对比」执行前先 ≤一轮廉价预检（如同 dll 重跑）确认载体可裁决性，预检不过先换载体。
- **证据**：.investigations/end-takeover/concern2-regression-verdict-260906-04.md + .tmp/concern2-260906/（三臂基线、ab 脚本、dump SHA、4 server log）；judge review-003 独立重算 SHA 吻合。

---

### #73 fan-out worker 交付「让渡清单」

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #73（A 类）

- **发现时间/发现者**：260907-01，fanout-260907-01 .b1/.b2 实践提炼；core.worker subagent 草稿 + 主会话应用。
- **module**：workflow-patterns / fan-out 交付契约
- **是什么**：各 worker 候选在 §裁决 附**让渡清单**——凡不属本候选解释范围的差异簇，只标「签名 + 量级 + 建议归属桶」，不做解释、不计入本候选账（.b1 例：结构残留→.b2、geode→结构候选、aquifer→11 篇挂起域、grass_block↔dirt 暂挂待 y 分布核查）。主会话收敛时按清单统一分账，judge 核对「无同一块簇被两个桶同时认领」（N-2 通过项）。
- **如何利用**：fan-out 候选模板增列「让渡清单」小节；收敛/审查第一步核让渡清单 ↔ 归属桶一一对应，防候选间越界归因与重复计账。与 #10 三阶段归因（通道归口）互补：#10 管「差归哪个通道」，本条管「候选间谁不许碰哪块账」。
- **证据**：.investigations/jungle-l/fanout-260907-01/.b1/candidate.md（§4 让渡清单）+ convergence.md（air/water 桶归属）+ review-260907-01.md（N-2）。

---

### #86 目测快照（F3 坐标）不可作交接物

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #86（A 类）

- **现象**：上会话以 F3 目测坐标交接「grove 细雪差异现场」三个坐标；本轮双臂对拍复核：仅 (0,131,-7) 复现，(26,128,25)=air（疑眼位坐标，邻域坡面 snow/snow_block），(17,126,14) 邻域无雪——2/3 不可用，若直接按其定位排查将白烧轮次。
- **根因（机制）**：F3 坐标是玩家眼位（眼睛位置，非脚下方块），且为瞬时快照——不随世界落盘，无 seed/坐标/时刻三元组可复现；跨 session 后世界已不可重放至同一观察点。与「探针坐标语义核对铁律」同族：**交接物缺少可复现语义 = 不可比数据**。
- **定位（判错方法）**：region 存档 NBT 直读（本例 block_states 逐块提取）做廉价独立复核（§16.3 交接验证）——复核通过才继承坐标结论，复核不过即弃用（本例弃 2/3）。
- **教训 / 可复用判据**：**任何跨 session 的坐标类交接物 MUST 满足「落盘可复核」三要素之一：① 存档/导出文件内含该坐标数据；② 探针输出行（带 seed）；③ 至少给出 block id + 邻域描述供直读验证。F3 目测/截图类瞬时观察一律标注「不可靠交接物」，消费前 MUST 存档直读复核，不复现即弃。**
- **状态**：✅ 已验证（260908-07 双臂对拍实证，见 .artifacts/grove-powdersnow-verdict-260908-07.md 锚点核查节）

---

### #87 跨版本枚举新增常量静默落 catch-all

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #87（A 类）

- **时间/置信度/module**：260908-10；candidate（行为级双臂对拍闭环 99.8114%→99.9993% + 一手枚举 diff + 全数据集唯一使用者实锤）；workflow-patterns / 跨版本数据驱动移植（**#56「写了但没生效」家族的数据驱动形态**）。
- **来源定位**：`.investigations/mc-1216-port-260908-10/progress-260908-10.md` §P7 根因定位 2-4；`versions/1.21.6/data/mc_src_extract/net/minecraft/world/gen/StructureTerrainAdaptation.java:7-11` vs 1.20.1 同文件 L5-9；`worldgen-core/src/beardifier.rs`（修前 ordinal 映射 `_ => None`；修后 L19-25 枚举 / L210-211 映射）；`.tmp/p7-diff-result-260908-10.txt` vs `.tmp/p7-diff-rust2-260908-10.txt`。
- **现象**：MC 1.21.6 给 `StructureTerrainAdaptation` 新增 `ENCAPSULATE("encapsulate")`（序数 4），1.20.1 只到 `BEARD_BOX`(3)。Rust `beardifier.rs` 的 ordinal→语义映射旧实现写 `_ => None` → 新常量**静默归零**：trial_chambers 结构处密度局部偏低 ≈1.4-2.2，整簇 **11,865 格错位**（64 chunk 区域 6,291,456 格，占 0.19%；27 chunk 有差，前 10 个占 87%）。**编译绿 + 单测全绿**——旧常量 0..3 的覆盖全部通过，缺口不在测试集里。修复后同 seed/同区域重跑 R 臂：**41/6,291,456 = 99.9993%**，原 trial chamber 簇完全消失（残差降为无簇零散近地表点）。
- **根因（机制层面）**：数据驱动移植里，Java 枚举的常量集合本质是**版本数据**，但 Rust 侧把它固化成了「match arm 集合 + catch-all」。catch-all 的语义被选成「无操作」（None / 权重 0）——新常量进入后，行为上等于「结构密度修正被悄悄关掉」，全程无报错、无日志、无告警。这是 #56 的**数据驱动形态**：不是新 arm 落在 catch-all 之后（序问题），而是**新数据值**落进 catch-all 的盲区（集合覆盖问题）——旧 arm 集合覆盖不到新值，且「编译过 + 告警不新增」同样成立。
- **定位（怎么发现的）**：① 双臂 BlockProbe 残差签名 = 簇状 `deepslate→air/water`，机制约束先排除 carver/feature（R 臂 `stageMask=3`，Java carver 两臂同码同 seed）；② 预置 fan-out 双否（b1「1.21.6 AquiferSampler 版本语义变化」REFUTES / b2「Rust aquifer 实现偏离」REFUTES）后回数据层；③ 世界 NBT 直读残差簇 = `minecraft:trial_chambers`（chunk(11,16)，249 children）；④ **一手枚举 diff** 抓到 `ENCAPSULATE`（序数 4）+ 全数据集唯一使用者 `trial_chambers.json`（`"terrain_adaptation": "encapsulate"`，该文件 L145）；⑤ 同点双 dump 68/68 density 符号翻转（vanilla +0.004..+2.215 → stone；Rust −0.0002..−0.05 → 进 aquifer）直证「结构权重归零 → density 被压负」。
- **修复**：`beardifier.rs` 补 `Encapsulate = 4` + q 分支（`min_y/max_y`，不含 `groundLevelDelta`）+ 权重分支 `getMagnitudeWeight(m/2,q/2,n/2)*0.8` + beard file ordinal 4 映射；`get_magnitude_weight` 改 f64 入参（Java 三种调用形态）。语义权威 = 1.21.6 `StructureWeightSampler.java:99/106`（一手实读：L99 `case ENCAPSULATE -> Math.max(0, Math.max(blockBox.getMinY() - j, j - blockBox.getMaxY()))`；L106 `case ENCAPSULATE -> getMagnitudeWeight(m / 2.0, q / 2.0, n / 2.0) * 0.8`）。
- **判据/教训（MUST）**：
  1. **跨版本移植时，Java 枚举类必须逐版本 diff 常量集合**（名字 + 序数 + `asString` 值），把「新增项」当 parity 缺口清单逐项核——枚举/常量表/注册表的新增条目是跨版本缺口的最高发面。
  2. **映射函数的 catch-all 禁止兜底成「无操作」语义**（None/0/忽略）——未识别序数 MUST 告警/断言/panic，把静默变成可观测；若必须兜底，兜底分支必须打一次性日志（带序数与来源）。本条修复后 catch-all 仍在（`_ => TerrainAdaptation::None`，L211），遗留风险已诚实记录，建议加告警。
  3. **「编译绿 + 单测绿」在跨版本枚举面上不构成证据**——旧常量覆盖全过是结构性保证，不是新常量被覆盖的证据。
  4. **数据驱动的「数据」不止 JSON**——代码里硬编码的枚举/常量表同样是版本数据，升级时一并 diff。
  5. 这类缺口的观测签名 = **结构/特性局部区域成簇偏差**（而非随机散点）——见簇先怀疑「某类结构/特性的修正在新版本常量上被静默关掉」。
- **证据**：上述源码/日志路径；`.tmp/p7-diff-result-260908-10.txt`（99.8114%、11865 mismatch、TOP PAIRS deepslate→air 6370 / deepslate→water 3744）；`.tmp/p7-diff-rust2-260908-10.txt`（99.9993%、41 mismatch）；`worldgen-core/src/beardifier.rs` L11-25 头注 + L255-284 三条单测。


### 发现 #16 补充案例（260908-10）：debug profile 栈溢出不是移植缺陷——对照臂归因先分离「构建配置因素」与「被移植版本因素」

- **时间/置信度/module**：260908-10；candidate（双版本同二进制对照臂 + release 臂通过）；workflow-patterns（#16 对照基线归因法的**构建 profile 维度**）。
- **来源定位**：`.investigations/mc-1216-port-260908-10/progress-260908-10.md` §Rust 引擎 × 1.21.6 数据冒烟；`.tmp/p2b-rust-1216-smoke-260908-10.log:2869-2870`（1.21.6 debug 溢出）；`.tmp/p2b-rust-1201-control-260908-10.log:2835-2836`（1.20.1 同二进制同样溢出）；`.tmp/p2b-rust-1216-smoke-rel-260908-10.log:2868`（release 通过）。
- **现象**：Rust 引擎对 1.21.6 数据 debug 运行 `thread 'main' has overflowed its stack` / `error: process didn't exit successfully ... (exit code: 0xc00000fd, STATUS_STACK_OVERFLOW)`；但**同一二进制对 1.20.1 数据同样溢出** → debug 栈帧膨胀是共同原因，**不是 1.21.6 缺陷**。release 臂通过：16 chunk，`min=127.2ms median=135.6ms avg=140.1ms`。
- **根因**：debug profile 关闭优化、栈帧显著膨胀，density 树/树生成等深递归路径对栈深度敏感。「新版本数据 + 溢出」被误读成「新版本移植缺陷」的诱因，是把**构建 profile** 这个变量和**版本**混在同一个臂里（混杂变量未分离）。
- **定位**：对照臂归因（#16 原法）——同一二进制换 1.20.1 数据重跑，溢出同样出现即排除版本因素；再换 release profile 直证是工具/配置因素。
- **修复/判据**：修复 = 诊断 bin 走深递归路径（density 树/树生成）MUST 用 `--release`。判据 = 遇栈溢出先跑对照臂（旧版本数据 / 另一 profile），别急着立「新版本缺陷」课题；栈溢出类结论的措辞 MUST 带 profile 声明（§9.7 可比性：debug 与 release 口径不可互推）。
- **教训**：「异常差异」第一动作是造无 X 的对照（#16 原判据）；本条补**变量维度**：构建 profile / 编译器配置本身是常被忽略的混杂变量，应与数据版本分开单独扫。
- **证据**：上述三个日志路径。


> 260908-11 追加：workflow-patterns 新增**发现 #88**（生成期探针 = 一次性窗口，复跑采集必删 world；E4 驱动开关与数据通道分离并入为 #20 补充案例、E5 并入 #81——新通道首跑必须带行为化 dbg）+ **发现 #89 简记**（spread-replay 低频路径缓存命中主导结构性难采样，降级声明须写明采样失败机制——F2 载体局限）+ **#26 补充案例**（Chunky 载体首次跨版本复用：1.21.6 量化基线 625/3698、terrain=27367/veg=6473，与 1.20.1 基线同构无新家族，水差 y 剖面 F1 域零差；「区域级粗对齐 × 单点级精对齐」双载体范式）+ **#80 补充案例·反向形态**（核验时机必须跟随被核验行产生时机——bridge init 在 Done 后，轮询优于即时断言，FAIL 分支须补杀 java；来源：.investigations/mc-1216-port-260908-11/）。

---

（主会话应用时追加到文件末尾 + INDEX 同步）

---

### #90 交接清单条目转抄漂移（机制/限定词失真）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #90（A 类）

- **时间/置信度/module**：260908-14；candidate（首次取证原文 + 转抄链逐环核对 + 一手源码双源复证，judge PASS-with-conditions 260908-14）；workflow-patterns / 交接与转抄纪律（#16 对照归因、§16.3 宿主交接验证家族的**清单条目转抄**形态）。
- **来源定位**：`.investigations/mc-1216-port-260908-14/w1-scout-spawn-barrier.md`（溯源全链）；首次取证 `.investigations/mc-1216-port-260908-08/diff/w2-chunk-pipeline.md:30/51/64` + `.investigations/mc-1216-port-260908-08/port-list-260908-08.md:15`；失真落点 `.artifacts/mc-1216-port/c1-exemption-list.md:23`；关账记录 `.artifacts/mc-1216-port-260908-14/p6-b3-closeout-260908-14.md`。
- **现象**：B3 条目四天三级转抄后，机制列从「邻居推进 barrier 变了（SPAWN.dependsOn(BIOMES,1)）」漂移为「spawn 区 barrier **放置**」、影响域从「任意 chunk 推进 SPAWN 的调度条件（全管线第 11 阶段）」缩成「spawn 区」——P6 工单因此按假语义挂「运行时探针」，而真实机制下探针**无观测对象**（双臂同走 vanilla Java 调度层）。
- **根因**：转抄是「名词保真、语义不保真」的有损压缩——挂账时只搬运条目名（「SPAWN barrier」六个字两版都读得通），机制/影响域列被后续抄写者按字面联想重写（barrier→放置、SPAWN→出生点）；每环转抄者都无法从上一环载体察觉漂移，因为上一环本身语义完整，漂移发生在**重述**而非**丢失**。
- **定位**：溯源法——沿传播链回溯到**首次取证原文**（w2 源码 diff）+ 交叉核对工单化时自带的裁决性限定词（port-list:15「0→ring-1@BIOMES」）+ 一手源码复证（1.20.1 ChunkStatus.java:182-188 taskMargin=0）；三处一致即裁定位转抄漂移而非机制争议。
- **修复/判据（可复用）**：① **继承清单/台账条目前，机制与影响域列 MUST 溯源到首次取证原文核对**，不信任最近载体（同 §16.3 方向结论廉价独立验证纪律，补齐「名词挂账类条目」缺口）；② 转抄时**禁止改写机制描述措辞**——要么逐字搬运 + 注明来源行号，要么附「原文指针」不重述；③ 带限定词/量化参数的原始措辞（如「0→ring-1@BIOMES」）是最高保真资产，转抄链中**任何环节都不许删**；④ 发现漂移按 §15.4 取代/勘误登记（追加不覆盖），登记时同时修正载体引用路径（本例 p7-verdict 目录名出入同族——转抄引用须逐字复制路径）。
- **教训**：错误台账价值再次实证——若 w2 首证原文未被保留，B3 将按假语义白跑一轮运行时探针（且零差结果会被误读为「验证通过」）；「首次取证载体不可压实删除」与「继承前溯源」是同一纪律的两端。
- **证据**：上列四个文件指针 + `.artifacts/mc-1216-port/p5-verdict-260908-13.md`（P5 覆盖面 + 零消费点 grep）。

---

### #185 数字型交接 claim 的「合法过期」

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #185（A 类）

- **观察**：260918-01 台账记 1.21.6 缺口 **21** 项；260918-08 开工按交接验证纪律廉价重测 = **11**（1.20.1=13）。漂移不是转抄错误：中间各块合法补齐 10 项映射 + 门禁新增 wrapper 捕获（260918-04，消费面 136→138）使 bulkwb/skipair 新显形——旧数字被**两项合法后续工作同时过期**（数据面收窄 + 测量面扩张），且扩张方向可正可负。
- **判据（简记）**：清单型/计数型交接数字（gap 数、覆盖数、基线数）**不溯源、不解释，当场用产出该数的机械工具重测**——静态转写准确的数字 claim 也会因后续工作自然过期（区别于 #90 转抄漂移：那种是写错，这种是写对但过期）；数字对不上时先跑工具再判断漂移方向，实测清单即权威工作清单。
- **来源定位**：`.investigations/b61-260918-08/record.md` §1（前提验证）+ §5.4（漂移链 21→9→11）。
- **家族索引**：#90（转抄漂移）/ #175（机械清单为准——本条为其「数字型 claim」维）。

---

### #193 接手第一动作 = git HEAD vs 交接文档交叉核对

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #193（A 类）

- **发现时间**：260919-04（2026-09-19）
- **module**：workflow / 会话交接与事实源对账
- **现象**：NEXT_SESSION.md「下轮第一 hook」停在 260919-02，而 git HEAD 显示 260919-03 已全量
  执行完（C-3+C-4 实现 → 裁断 → 知识库，96a8b9a）——若按交接指示直接开工，会对已完成的
  260919-03 目标重开（重复劳动/方向冲突）。
- **根因（机制）**：NEXT_SESSION 是**换界时点的快照**而非实时事实源；上工作块收尾未同步重写交接
  文档，快照落后实际进度一个块。接手方把交接里的「下轮第一 hook」当公理直接续推，未做 STEP 1
  交接结论验证纪律规定的廉价独立验证（对 git HEAD 核对，成本一轮以内）——qualitative 类交接
  claim 未重采样原始事实源（§1.3）。
- **定位（怎么发现）**：接手例行动作——NEXT_SESSION 指示与 `git log` HEAD 并读，时间线断裂处
  即漂移信号；以 git HEAD 为权威锚（不可变、带时序戳）。
- **修复**：按当前最新状态重写 NEXT_SESSION（交接文档唯一权威），并以 git HEAD 为准重建开工点；
  双 verdict confirmed 由用户 ask_user_question 拍板后回写。
- **教训（可复用判据）**：
  1. **接手第一动作 = git HEAD vs NEXT_SESSION 交叉核对**（发现/readme 类指示一律先对账再执行）；
     不一致时 git HEAD 为权威，先修交接再开工——交接修复优先级高于新任务。
  2. 「下轮第一 hook」类指示性内容是**交接 claim 不是事实**：指针类（进行到哪/下一步做什么）
     MUST 对账（git log / 产物存在性），方向类才走 ≤1 轮廉价独立验证（STEP 1 纪律）。
  3. 交接漂移的检测签名 = 指示指向的产出物在 git HEAD 中**已存在或已被超越**——见此签名即停，
     禁止按指示续推（同 M14/M11 家族：假设当公理 = 绕圈根因，本条是其交接侧形态）。
- **家族索引**：AGENTS STEP 1 交接结论验证纪律（M14/M11 三犯复盘——本条补「进度指针漂移」维）、
  §1.3 交接 claim 证据分级（qualitative 重采样）、#137（anchor 类属主工具自核——同族「原始事实源
  优先」）、AGENTS 知识库铁律 4（NEXT_SESSION 唯一权威 + 只在换 session 前更新——漂移根因即
  违反此条）。

---
