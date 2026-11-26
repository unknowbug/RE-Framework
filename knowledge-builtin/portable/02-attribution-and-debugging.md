---
volume: 02
title: 归因与调试
scope: 残差归因、探针设计、排查顺序、根因定位、坐标/载体核对
source: CoreSwap knowledge/discovered（A 类条目重组，正文原样）
status: draft
---

# 02 · 归因与调试

> 覆盖范围：残差归因、探针设计、排查顺序、根因定位、坐标/载体核对。条目正文自 CoreSwap 知识库原样搬运（A 类 = 跨项目可复用），行首出处可回查原条目。

## 目录

- #9 一次性诊断产物必须有唯一隔离区
- #10 残差三阶段归因法（先分阶段再定位机制）
- #13 探针输出必须先做 sanity check（坐标 bug 造 100% 假象）
- #22 自由参数凑数反模式（乘数须有独立实测来源）
- #25 静态调研结论失真（核生产路径可达性、常量取值源头）
- #27 负向测试是断言生效的唯一证明（且其假阴性更危险）
- #30 边际成本平坦扫描法（摊薄前提不成立即整派出局）
- #33 载具可比性（跨载具残差禁止互引）
- #35 量级核算排除法定位写者
- #38 判读源码语义前必须核 env 默认值方向
- #39 参照自身缺陷辨识（mod≠参照≠mod 错）
- #42 静态机制断言未实测当公理续推（一轮 dump 即证伪）
- #45 同输入异分类：三源隔离法 + 定点直读 + 坐标语义隔离
- #52 确定性区域 dump 载体（代码 diff 唯一变量）
- #53 env 门控默认值当公理 → 强制三查
- #56 新分支禁止落在 catch-all 之后（编译过≠命中）
- #57 哨兵值跨模块传递必须在边界做语义变换
- #61 复算逐位吻合必须先证公式覆盖正确调用点
- #64 未受控观察真值表必须降级标注
- #77 回滚 ≠ 引用面清理（配置/脚本/默认值路径引用）
- #78 代码注释内嵌日期 ≠ 时间戳权威
- #79 「创建期解析 + 运行期注册」类资源必须惰性化
- #81 A=B 恒等不能证明分支生效（两臂可能同走旧路径）
- #84 INFO 级日志 grep 结构性假阴性 + 旁证计数红鲱鱼
- #85 关服瞬间批量同源异常先做时序排除
- #88 生成期探针 = 一次性窗口（在盘 ≠ 会再经过探针）
- #93 注册名子串分发反模式（contains 误捕）
- #94 简报字段名/分类词不进一手源核对不可用
- #101 残差归因「读量放大 vs 单读贵」判别式
- #105 载体偏差：载体全绿对生产故障零判别力
- #110 路径不可达类断言的证明三件套 + 复活出口穷尽
- #113 跨实现搬运锁语义必须成对核对（只搬一半即自锁死）
- #117 迁移引用面「活配置 vs 历史归档」两分
- #120 对外能力声明必须与出货默认门控同源核对
- #125 背压两形态同构不同质（acquire vs CallerRuns）
- #126 工单时间链禁写 mtime 严格序
- #132 跨臂门的分母必须声明语义
- #133 排除法结论的边界（未测候选必须并列）
- #134 结论里的读数必须声明来源性质
- #136 热路径门控化必须盘点被移除的信号
- #137 结论引用的外部锚必须用属主工具自核
- #140 「结论对而解释错」（叙述层事实未核实）
- #143 「单写者不变量」结构性论证模板
- #144 复跑同标签臂必须先归档首轮日志
- #150 形态耦合修复序（事实串行化掩盖下方缺陷）
- #158 机制推演候选分解地基 = 内核输入通道清点
- #160 VOID/GATE 裁决必须非零退出断链
- #161 盘上「数据身份」vs「执行体身份」双身份核对
- #162 汇总交叉的定性必须回原始日志抽样
- #163 门禁只判「存在/数量」= silently-green 门
- #164 多副本安装树的「无脚本覆盖面」（逐副本谁写谁验）
- #165 升级路径的沙箱边界首次碰撞（升级后首跑视为 escalation 窗口）
- #167 逆登记不得为表格好看编造「可还原」
- #172 门禁有效性必须用注入式负向测试自证
- #178 输入 hash 不稳定 ≠ 序列化自由度（须内容级解码）
- #180 探针差异集的空间坍缩（多 chunk 共享邻域读数）
- #182 映射型校验器必须先验值域封闭性（未知值必须 FAIL）
- #183 「前提不可达」静态标注的机械化（事实封闭集+求值器+矛盾检查）
- #186 措辞争议用发射面单轮实证闭合
- #188 打点/判别数据通道必须覆盖全部执行形态
- #189 分段打点的窗标签必须与代码括住的工作一致
- #192 占比门脚本化方向未取反（占比 vs 补数两义）
- #194 CPU 总量收益 ≠ 关键路径收益
- #199 形态门判别器（band × interior 双阈值）
- #202 产物 sha 漂移连锁声明（下游前置全体失效面）
- #203 前置 key 挂起排程（依赖未来判别）
- #204 「值收敛 ≠ 过程确定性」（贴参考实现可放大方差）
- #209 交集 = 各自大小 ⇒ 集合恒等
- #212 引用机械产出须逐字对原文 + 分账和=总数自检
- #214 混杂变量须补「效应方向」论证
- #216 「等待窗口」参数只在持续零散触发形态暴露
- #10 thread_local 缓存与「每 chunk 跨线程」执行模型冲突 → 命中率归零
- #11 spline 树扁平化（递归 shared_ptr 树 → 连续数组 + 非虚采样）
- #12 边界角点复用收益小的根因（缓存构建触发点不集中）
- #13 GPU 驱动编译：编译期常量下标进数据驱动函数 = 常量传播展开陷阱
- #15 GPU 批量加速带宽死局：每点数据量 × 点数是可行性判据

---

### #9 一次性诊断产物必须有唯一隔离区

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #9（A 类）

- **发现时间**：260901-03；**发现者**：1.0.22 发版 session；**来源定位**：`WorldgenRust/src/bin/` 过时诊断 bin 阻塞发版事件 + AGENTS.md 八.13「临时文件唯一区纪律」；**置信度**：candidate（用户已拍板纪律并落地修复，本发现未走 judge）；**module**：workflow / 构建工程。
- **观察**：cargo 只自动编译 `src/bin/` 下所有文件（npm 侧 src 扫描、CMake glob 同族），该目录里积累的一次性诊断 bin 过时后无人维护，却仍参与每次全量构建。1.0.22 发版时 `cargo build --release` 因其中 23 个 bin 仍用旧 `RsSplitter` API（`Aquifer::new` 签名已换 `XoroshiroSplitter`）报 E0308 阻塞发版——而发版产物只需 cdylib（dll），这些 bin 根本不在发版产物内。致灾 = 两因素叠加：①「临时产物位置无约束」（写进明面约定目录）②「构建范围 = 全目录」（约定目录全量自动编译）。
- **证据**：E0308 全部指向 bin 内旧 API 调用；分两批迁出（先 5 个，重建后又暴露一批 → 共 23 个 → `WorldgenRust/src/bin-diag/`，cargo 不扫描该目录）后全量构建 exit 0，发版产物（cdylib）不受任何影响——证明这批 bin 与发版零依赖，纯属「位置无约束 × 全目录构建」的结构性问题。**第二轮才见底**也是证据：首次报错列表只是「先编译失败的那批」，cargo 不会一次报完所有坏 bin——清此类债必须迭代到全绿。
- **如何利用**：
  - **判据一**：任何构建系统的「约定目录 = 自动构建范围」（cargo `src/bin/`、npm 打包器 src 扫描、CMake `file(GLOB)`）都**不要放一次性脚本/诊断程序**——放进去即等于「永久参与构建 + 永久欠维护债」。
  - **判据二**：临时产物必须有唯一隔离区，**靠纪律不如靠机制**——最可靠的隔离是目录选择本身（放构建器不扫的目录），而不是「记得别乱放」；CoreSwap 落地：Python/一次性脚本 → 仓库根 `.tmp/`，Rust 诊断 bin → `WorldgenRust/src/bin-diag/`（要用时 rustc 单编或临时挪入）。`src/bin/` 只保留「随库维护、全量编译必须绿」的正式 bin。
  - **判据三**：发版只需库产物时 `cargo build --release --lib` 可救急，但**全量绿仍保留为发版前检查**——全量构建是过时产物的探测器，全量红即暴露「有产物已脱离维护」。
  - 反模式警示：诊断 bin 与生产代码共享 crate 时，API 演进不会「顺带」修好 bin（无 CI 强制时更不会）——过时是默认轨迹，隔离是唯一低成本对策。
- **同族已知坑**：gradle 换机器/新 shell 直接 `gradle` 不带 `GRADLE_USER_HOME` → native-platform.dll 加载失败（build-tooling.md 发现 #4）——环境类「约定不生效」同族：工具的 home/缓存必须显式指到工作区内。

---

### #10 残差三阶段归因法（先分阶段再定位机制）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #10（A 类）

- **发现时间**：260901-03；**发现者**：nether-save-full session（B1 定论轮）；**来源定位**：`.investigations/nether-save-full/`（residual-interpretation + .b1/.b2 + judge-review）；**置信度**：candidate（三方实验数据实锤，模式层面复用性待下一案例）；**module**：workflow / Minecraft modding / 验证方法。
- **观察**：替换模式（如 cppReplace 只接管 noise+surface，Java carvers/features 仍在替换后地形上运行）下的存档口径残差是**多阶段混合产物**——直接把残差对到单一层（如 surface rule 条件链）会得出错误归因（错误 E6：B1 52k 块大宗互换一度被归因 surface rule 条件链，实为 feature 阶段产物在两种基底地形上的命中/形态差）。正确做法是**三阶段归因**：
  1. **阶段分解**：先分清 noise/surface（替换方 = Rust）与 carvers/features（存续方 = Java）各自贡献，再定位机制；
  2. **消融判别**：`WG_SKIP_SURFACE=1` 重跑——surface 关掉后残差从 93.55% 掉到 55.18% 证明 surface 是实心块主来源；且 blobs 不触发（stone 基底非 netherrack → blackstone=0）反向证明 blobs 是 feature 阶段、依赖 netherrack 基底；
  3. **纯替换方基线**：ctypes 直连 dll（或 rlib 直跑）取得纯 Rust 输出 vs 参照（本轮 77.43%，与存档口径 93.55% 载体不同不可比，§9.7）——分离「替换方自身缺口」与「存续阶段叠加产物」。
- **如何利用**：
  - **判别手段一（消融）**：单阶段开关（如 WG_SKIP_SURFACE）A/B 重跑——残差量级变化 + 依赖块（如 blackstone 依赖 netherrack 基底）是否消失，直接指认产物所属阶段；
  - **判别手段二（直连基线）**：ctypes/FFI 直连替换方库跑同区域——排除 Java 存续阶段干扰，取得替换方独立口径；与 rlib 直跑对拍可顺带验证 FFI 层确定性（本轮 cell 级 0 差异）；
  - **biome/来源分桶**：残差按 biome 列分桶——若差异 100% 落在 vanilla 某列（本轮 basalt_deltas），排除「源分配差」，收窄到「同源产物在不同基底上的表现差」；
  - **同 dll 重跑非确定性容差判据**：存续阶段（Java feature 邻块写入调度）本身非确定——同 dll 两次完整 run 相差 369 块（93.5156%→93.5508%）。**存档口径对齐指标必须声明该容差**：同 dll 重跑块级差 ≤ 百分级（千分位级百分比波动）属调度噪声，不构成实现回归判据；跨口径比较（探针 vs 存档 vs 纯 Rust）一律 §9.7 三要素声明。
  - **实例更新（260902-04）**：basalt per-id −1736（260902-03 run2）vs −1050（本轮 run）——量级一致、数值漂移 ~686 块，落在非确定带宽内，再次佐证本判据：per-id 单值不做回归判据，只看量级/家族归属（B1 家族），跨 run 比较须声明容差。
  - **先消融后归因**：任何「残差 → 某层机制」的归因结论，出手前必须已有至少一个阶段消融或直连基线证据，否则降为 draft（反模式见 E6）。
- **同族模式**：发现 #4（参照数据状态三查 SURFACE vs FULL——参照阶段决定差异构成）是「对照侧」的前置；本发现是「被测侧」（替换模式运行时残差）的阶段归因，两者合用构成替换模式验证的完整口径纪律。

---

### #13 探针输出必须先做 sanity check（坐标 bug 造 100% 假象）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #13（A 类）

- **发现时间**：260902-04（V5 残差排查；实际 2026-09-02 15:45 = 本轮提交簇 git 时间戳锚）；**发现者**：v5-residual session；**来源定位**：`.investigations/v5-residual/finding-mid-260902-04.md`；**置信度**：candidate（数据层证据实锁，judge 有条件 PASS）；**module**：workflow / 验证方法 / 探针工程。

#### 现象

nether 存档残差 35426 mismatch 列，world biome 对比显示 **100% = warped_forest**（vanilla 参照侧 94.4% basalt_deltas + 5.6% soul_sand_valley）——「残差区 biome 全被误判成 warped_forest」的单向假象，指向 biome 分类器/存储填充链（fan-out 候选 .b6）。

#### 根因

**探针自身坐标 bug**：ReadWorldProbe 的 wBiome 查询误用 **chunk 局部 x,z（0-15）**调 `world.getBiome` → 实际查询落在 chunk(0,0) 区域（恰好是 warped_forest）→ 所有行读到同一个错误 biome；vanilla 参照侧用的是世界坐标，正确。两侧坐标系语义不一致 + 错误区恰好恒定，制造了「100% 单向翻转」的假签名——符号级错误（坐标域错用）是结构错，不是精度/概率错。

#### 定位

一步裁决探针逐层收敛（见下简记）：biome 列对比发现 100% warped → 6 维输入对拍（Java BIOME6 vs Rust biome6_dump 逐位一致，两侧数学均判 basalt_deltas，dist 0.119 vs 1.080 非平局）→ storage cell dump（Rust 独立分类器判定与 vanilla 参照一致）→ **整列 storage vs biomeAccess 对比**锁定：读 storage 正确、走 BiomeAccess 的 wBiome 读错误 → 反查 wBiome 坐标来源发现局部/世界坐标混用。

#### 修复

wBiome 改用世界坐标查询（mismatch-nether-run6.csv）：96.3% 残差列 biome 完全一致（basalt→basalt 32817 + ssv→ssv 1306）；biome 真差仅 1303 列（3.7%，ssv↔basalt 边界互换 = 签名 A 降级为次要项）。残差真图景变为「**同 biome（basalt_deltas）下表面规则判定差**」（B1 家族本体）。

#### 教训

- **「对比前先核坐标语义」铁律（AGENTS.md seed 三查 #2）的延伸**：不仅跨工具对比要核坐标语义，**探针自身的每个坐标参数都要核**——探针 bug 比实现 bug 更危险，因为它披着「测量仪器可信」的外衣。
- **探针输出先做 sanity check 再下结论**：对照组/已知区抽查（如「100% 单一值」「全部落在同一区域」这类完美签名本身就是可疑信号——真实世界残差不会是 100% 单向）；100% 一致性签名优先怀疑测量侧而非被测侧。
- 再次验证「符号级错误是结构错」：35426 列 100% warped 不是概率/精度问题，一眼就应归因结构性坐标/索引错。
- 同族：workflow-patterns 发现 #12（对拍对象错级——对拍原文而非解析产物）——两者都是「测量/对拍工具自身失真污染结论」家族。

#### 简记（同轮方法再验证，中价值）：one-step decisive probe 逐层收敛

V5 残差排查中 4 次「一步裁决探针」逐层收敛（biome 列对比 → 6 维输入对拍 → storage cell dump → 整列 storage vs biomeAccess），每步排除一批候选；fan-out worker 静态代码分析与主会话探针数据采集交替（worker 出模板 → 主会话执行不解读 → 原始输出回传）——与发现 #10 三阶段归因法互补：#10 是宏观阶段分解，本条是微观单层内的最小裁决步设计。复用判据：每一步探针设计成「输出只有两种互斥解释」的裁决形态，避免采集后再发散分析。

#### 补充案例（260902-05/06，测量侧三犯清单 + 同族新案例）

同 session 链再证「探针输出先 sanity check」：260902-05「selector 场差 42%/patch 差 64%」整轮假象 = NoiseConfig 维度取错（overworld vs nether）；同轮 BlockProbe FULL 预生成提升 chunk 污染 SURFACE 参照（22.5% 残差假结论，260901-04 结论被取代）；260902-06 CSV 空 4 轮 = RegistryKey 过滤条件恒 false。合并沉淀**测量侧先查三犯清单**（探针零输出/异常完美签名时，先查测量侧再怀疑被测侧）：
1. **wBiome 坐标**：chunk 局部 x,z（0-15）vs 世界坐标混用（#13 原案例）；
2. **NoiseConfig/维度上下文**：探针取的 server 维度对象 ≠ 目标维度（overworld XOROSHIRO vs nether LEGACY）；
3. **pregen 提升 chunk**：预生成邻域导致 getChunk 返回已推进状态，参照口径名不符实（同族：发现 #6 getChunk「至少 N」语义）。

**同族新案例（260902-06）**：`RegistryKey.getValue().toString()` 返回带命名空间全名（`minecraft:the_nether`），与裸路径（`the_nether`）equals 过滤恒 false → CSV 空 4 轮的真根因。同判据扩展：**探针零输出先查两类条件**——①过滤条件（字符串/枚举语义不匹配恒 false）②驱动条件（如 BlobProbe 单独跑无 driver 不生成 nether chunk，COLPROF 空跑一轮——「没数据」先问「chunk 根本没被生成」再问「生成了没读到」）。




#### 补充案例（260902-07，指标盲区 + 行首锚假零输出）

同判据家族两例（b1-downdrill lavaAudit 课题，详见 b1-errors.md E-B1-10/11）：

1. **探针指标盲区**：lavaAudit v1 只记 above=lava 转换，恰好测不到判别「熔岩海缺失」所需的 below=lava 面向（air→lava 转换面）——v1 输出「99.4% 一致」对核心命题零判别力，是「测了且一致」的假安心；v2 加记 lavaSurfY 后一轮实锤两侧 air→lava 面向均为零，直接推翻待测现象的存在。**判据扩展**：设计探针指标先写「要判别命题 P，最小充分证据是什么」再检查指标覆盖，指标名对口 ≠ 覆盖证明（与发现 #12 对拍对象错级同族：测量设计与判别目标脱节）。
2. **行首锚 grep 假零输出**：`^\[LAVAAUDIT\]` 对带日志框架前缀（时间戳/线程名）的 log 行恒零命中 → 误判「探针零输出」。与 260902-06 RegistryKey 命名空间前缀（本发现 #13 补充案例）同属「过滤条件把全部行静默滤掉」家族。**判据扩展**：「零命中」先打印一行原文核对行格式，`^` 行首锚对 log 行默认不可用。

---

### #22 自由参数凑数反模式（乘数须有独立实测来源）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #22（A 类）

- **时间/置信度/module**：260903-10，confirmed（260903-10 用户拍板），通用方法论。
- **来源定位**：qaq1-b1-candidate-260903-10.md §4.2「158 miss × ~4-5 次重建 × 1225 角点 × ~30ns ≈ 26ms」——三处乘数无实测来源，GRID_ARG_SAMPLES=0 反证后整套机制作废（§5 supersedes）。
- **观察（现象）**：凑出的乘积与目标缺口「异常贴合」（26 vs 26.65，残差 <3%）——但机制根本不存在。
- **根因**：把「缺口量级」当约束反推乘数（拟合目标而非解释世界）；每乘数缺独立实测锚点。
- **定位**：决定性计数器（GRID_ARG_SAMPLES 双态增量 0）一击否证。
- **教训/如何利用**：**量级核算每个乘数须有独立实测来源；≥2 个自由参数只算猜想**；「异常贴合」反而是凑数嫌疑信号——机制预测应在自由度小的前提下先出预测后对照。

---

### #25 静态调研结论失真（核生产路径可达性、常量取值源头）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #25（A 类）

- **时间/置信度/module**：260903-11，candidate（judge 两次审查通过），通用方法论。
- **来源定位**：est-opt 包 P1 调研阶段 subagent 结论（G5）与 K3 复核；裁决记录 `.investigations/lossless-accel/est-opt/k3-k2-verdict-260903-11.md`；两次 judge `.investigations/lossless-accel/review-estopt-260903-11.md`。
- **案例①（G5 引用错位）**
  - **现象**：P1 调研 subagent 结论「fill/carver 各自 `Aquifer::new` 不共享」，主会话据此把「跨实例共享」列为优化差距点，差点直接投入实现。
  - **根因（机制）**：调研引用 `worldgen_handle.rs:547` 处 `Aquifer::new` 作证据，但 :547 实为诊断 API `diag_pre_surface_column`（非生产路径）；生产路径 :446 唯一 `Aquifer::new`，:520 carver 复用 `&mut va.aq`——引用行号存在但语义错位，结论在真实调用图上不成立。设计阶段 worker 代码核对推翻。
  - **定位**：设计 worker 对差距点逐条做「生产路径可达性」代码核对（不是重新读一遍结论，而是顺着调用图验证差距点真实可达）。
  - **修复**：原 P1 表述不可改写（§15.4），以 k3-k2-verdict 的 G5 supersedes 记录取代；实现方案按「唯一构造点共享」重定（b1-a est_at 共享）。
  - **教训**：**调研结论的每个「差距点」必须带生产路径可达性核对**——引用行号/调用点存在 ≠ 该点在生产调用图上可达；诊断 API、探针专用路径、死代码都可能是错位来源。下开销实现前先核对，比实现后返工便宜一个量级。
- **案例②（K3 常量记忆错）**
  - **现象**：调研称「Java est 扫描步长 4」（`l -= verticalCellBlockCount`），与 Rust `l -= 8`（aquifer.rs:295）疑似不一致，触发 K3 疑点裁决。
  - **根因（机制）**：凭常见值记忆填写常量——`verticalCellBlockCount = 4 × size_vertical`（GenerationShapeConfig.java:46-48），overworld.json `size_vertical: 2` → **实际步长 8**；「4」是 size_vertical=1 的常见值，不是 overworld 值。
  - **定位**：裁决沿取值链逐环核对：调用点（ChunkNoiseSampler.java:233）→ 计算式（GenerationShapeConfig.java:46-48）→ 数据源头（overworld.json:18）。三环核对后疑点解除（一致，P1 文档「4 步进」为笔误）。
  - **修复**：P1 文档笔误不改原文，由 K3 裁决记录取代标注。
  - **教训**：**引用 Java 常量必须追到取值源头（config/JSON 派生链），禁止凭记忆/常见值填写**；数据驱动的 MC 常量尤其如此——派生链上任何一环（计算式 × JSON 值）换版本即变，「常见值」是最不可靠的引用方式。
- **同族**：#9（跨 session 未验证标注当公理继承）、#17（打印坐标≠采样坐标）——本条补「调研产出消费前」维度：#9 管跨 session 交接，本条管同 session 内调研 subagent → 主会话的交接，判据同为「引用先验证再消费」。


#### 补充案例（260903-12，#25 第三例：静态地图「恰好一致」断言失真——量化算术必须显式做）

- **现象**：scout 地图（est-shared-java-map/java-est-chain.md）#7 断言「Rust heights4 传 +15，量化后恰与 Java (i+1) 角一致」——据此本应触发的 +16 角修正被推迟了一整轮；实际 `+15 >> 2 << 2 = +12 ≠ +16 = +16 >> 2 << 2`，被 P1 运行时逐值对比（est-compare-p13b：敏感 chunk (201,200) java@+16=56 vs shared@+12=48）抓出。judge 复算另发现该断言与地图自身摘录内部自相矛盾（同段先写「60 量化→60 量化不变」，随即又称 +15 量化后一致）。
- **根因（机制）**：静态对拍清单里的「恰好一致」结论靠**直觉合并**产出——两侧参数（+15 vs +16）肉眼「差不多」，量化函数（`(x>>2)<<2`）的等价类边界（15 与 16 分属 +12/+16 两类）没有做显式算术就判了等价。这是 #25 案例①（引用行号语义错位）/②（常量记忆错）之外的第三种失真形态：**函数等价性靠直觉而非计算**。
- **定位**：P1 Java mixin RETURN dump vs Rust WG_EST_DUMP 逐值对比——运行时抓出 +12≠+16；judge 复算（16>>2<<2=16、15>>2<<2=12）一击确认。
- **修复**：verdict 登记「角参数 +15→+16 修正」待办（两臂共有，独立小包）；scout 地图不回改（失真记录保留，§15.4 精神）。
- **教训**：**静态对拍清单里的任何「恰好一致/恰好相同」断言 MUST 做显式算术**（把量化/取整/映射函数套进去逐值算），不能靠直觉合并「差不多的参数」；「一致」断言与自身摘录冲突是失真的廉价检测信号。同族：#25 案例①②、#17（打印坐标≠采样坐标）——同属「静态调研产出消费前先验证」，本条补「函数等价性维度」。

---

#### 补充案例（260903-12，#21 第二次量化实锤：hot/cold 形态差 ~95× + 单价稳定性作 fan-out 免触发判据）

- **现象**：同一段 est 扫描代码（est_price_probe，同 seed 同树），hot 模式（单列重复采样）65/57 ns/iter vs cold 生产形态（顺序新列）5751/5721 ns/iter——**形态差 ~88-100×（judge 复算，取 ~95×）**。同时，跨 session 生产隐含 est 单价稳定：260903-11 `48ms/(7342−1715 iter)≈8.5µs/iter`；本 session `55.6ms/5627 iter≈9.9µs/iter`。
- **如何利用（两条）**：
  1. **「微测外推生产无效」的量化实锤**：#21 主案例差 40×、260903-11 补充案例（working set）差 ~5×、本例同代码 hot/cold 形态差 ~95×——三次独立测得同一结论，量级 40-100×。判据强化：任何微测数字引用到生产前，先问采样形态（遍历方向/列切换/冷热/生命周期）与 working set 是否同构；**「微测 × N ≈ 生产实测」不自洽时永远怀疑形态失配而非实现异常**（与 AGENTS「阶段耗时×批次≈wall」自洽判据同源）。
  2. **跨 session 单价稳定性可作收敛判定依据（fan-out 免触发）**：剩余差归因时，若「生产隐含单价跨 session 稳定」（8.5 vs 9.9µs，±16%），则主机制成本主导且无漂移，次级效应候选（b2 类）不构成与主机制并存的互斥候选 → core.fanout 触发条件（≥2 互斥候选）不满足，**免 fan-out**。本例 judge 复核认可（review-p2-p3-final §C：「作为收敛判定依据使用而非独立证实，符合触发条件」）。注意边界：该判据只免 fan-out，不构成对主机制的独立证实——结论仍需生产实测支撑。
- **证据**：`.investigations/lossless-accel/cmd-output/est-price-p24-260903-12.txt`（hot 65/57ns、cold 5751/5721ns 原始输出）；单价核算见 `.artifacts/lossless-accel/est-l2-defaultflip-p2-260903-12.md` P2.4。

---

### #27 负向测试是断言生效的唯一证明（且其假阴性更危险）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #27（A 类）

- **时间/置信度/module**：260903-15，candidate（judge PASS with should-fix 已清偿），通用方法论。
- **来源定位**：`.investigations/preload-check/`（verdict-preload-check-260903-15.md + preload-check-errors.md E1/E2 + review）；承接发现 #26（260903-14 预加载缺项 panic）。

#### 观察（落地形态）

#26 教训 1 提出的「更优做法：启动期机械校验」本次落地，三层：
1. **机械收集**：`collect_rule_noise_keys(rule)` 对已构建 SurfaceRule 树递归收集运行时会查 sampler 的 key（`collect_noise_keys` 泛化为"任何带 noise 字段的 JSON 节点都收"，不认死类型名）。
2. **引擎调用点清单**：`ENGINE_NOISE_KEYS` 常量**紧邻引擎 get_noise 调用点（place_badlands_pillar 等）就近维护**——引擎路径不在 rule 树内，机械收集覆盖不到，清单是唯一事实源；预加载侧 `use surface_rules::ENGINE_NOISE_KEYS` 引用同一来源，消灭两处硬编码。
3. **启动期断言**：`create_for_dim` 规则构建后断言 `collect_rule_noise_keys(rule) ⊆ 预加载集合`，缺失即 panic 并列出缺失 key——缺项从「数千 chunk 后运行时 expect 爆」提前到「启动 0 chunk 即爆」。

**诚实盲区声明**：机械收集只覆盖 rule 树可遍历到的节点；**代码内嵌的 get_noise 调用点无法机械枚举**（引擎路径）——所以必须有就近维护的清单层，断言只保证「树内全集」，树外靠维护纪律。不能把机械校验当成完备性证明。

#### 判据（负向测试 + 假阴性危险度）

- **负向测试是断言生效的唯一证明**（发现 #20 死参数判据的应用）：删一个 key → 启动必须 panic 且精确报该 key → 恢复 → hash 复验零回归。没有负向测试，"加了断言"与"断言根本没编进二进制"不可区分。
- **负向测试的假阴性比假阳性更危险**：本次 E1（bin-diag 旧 exe）连吃两次"未触发 panic"，若就此下结论「断言生效」，E2（收集循环死循环 bug，恰被第三次真负向测试暴露）会直接带进生产——**假阳性会被绿测量掩盖怀疑，假阴性给出生效证明的错觉**。先核产物新鲜度（时间戳/哈希），再信任何"未触发"。
- 附带战果：E2 死循环（Cond 臂命中 NoiseThreshold 后不前进不退出）正是被真负向测试暴露——状态机循环每臂必须「前进或退出」。

#### 如何利用

- expect 型查表类代码新增时，配套三层：机械收集 + 就近清单 + 启动断言，**同 commit 内完成**（#26 判据 1 的"同步改两处"升级为"机械校验自动覆盖"）。
- 任何启动期断言交付时，负向测试（删 key 必 panic + 产物新鲜度核对）是完成定义的一部分，不是可选验证。
- 同族：#26（问题来源）、#20（自变量真被改变）、#12（哨兵结论配哨兵点验）、#6（产物新鲜度判据）。

---

### #30 边际成本平坦扫描法（摊薄前提不成立即整派出局）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #30（A 类）

- **发现时间**：260904-01。**发现者**：主会话 + worker + judge（GPU (b) 终局判决转化）。**置信度**：candidate（单轮证据，判决本身已 confirmed，方法判据待复用再升）。**module**：通用方法论（立项评估 / 性能方案筛选）。
- **来源定位**：`.investigations/vulkan-gpu-operator/cmd-output/gpu_n_scan-260904-01.txt` + `.artifacts/vulkan-gpu-operator/index.yaml`（p05b-verdict，confirmed）。

#### 观察（现象）

GPU 批量化提案三个候选 (a) 合批 / (b) 全树单 dispatch / (c) 混合，前两轮逐一评估：(a)/(c) 因固定成本出局、(b) 挂起待重估。若 (b) 按候选逐个改造+测量，每轮成本 = 写探针 + 70-100s 管线编译 + 多轮 bench。本轮改为一次 n 扫描（768/6144/49152/196608 点，严格串行）直接测边际成本曲线：四档 per-pt 0.2449→0.2335→0.2323→0.2329 ms，相邻差分 0.2319/0.2322/0.2331 ms/pt——全档平坦（噪声内），批量摊薄不存在。(b) 立项前提（放大批次摊薄 c≈0.233ms/点）被一次实验否决，整派出局；per-chunk 折算 178-188ms vs 判据 <4.5ms 差 ~40×，即使立项亦负收益。

#### 根因（机制）

立项级性能提案通常隐含一个**前提命题**（如「放大批次可摊薄固定/边际成本」「合批可摊薄 fill 开销」），该前提对所有候选共用。逐个候选验证是在验证前提成立后的「下游优化量」，而前提本身一次扫描即可判定：若边际成本对规模不敏感（d(cost)/dn 恒定），任何批次形态的调度/合批改造都无法改变成本本体——前提不成立 → 整派候选连带出局，无需逐个验证。

#### 定位（怎么发现）

n 扫描法：对同一管线按 4 个数量级跨度的批次规模（1/8/64/256 chunk = 768/6144/49152/196608 点）各跑 7 轮取 median，做相邻档差分得边际成本曲线。平坦曲线 = 摊薄前提的直接否证；且 n=6144 档读数与既有历史口径（260903-16 c≈0.233）吻合 <0.3%，廉价完成旧读数结构一致性核验。

#### 修复 / 如何利用（可复用判据）

1. **立项级提案的 kill 判据前置**：评估一派共享同一前提的候选时，先设计一次直接检验前提的扫描实验（成本 ~1 个探针 + 单轮采集），前提被否证则整派出局，比逐个候选验证便宜一个量级。
2. **判据形式**：边际成本曲线全档平坦（差分值落在单档噪声带内）= 摊薄不存在 = 「改调度/批次形态」类提案全部无收益；只有曲线下降才值得进入候选级评估。
3. **顺带收获**：扫描的中间档天然兼做历史读数的结构一致性核验点（同口径单档比对）。
4. 同族：#21（微测样本模式决定缓存命中率——外推前先复刻调用形态）、#22（量级核算乘数须独立实测）、#18（跨 session 数字不可比）。

---

### #33 载具可比性（跨载具残差禁止互引）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #33（A 类）

- **发现时间**：260904-04。**发现者**：探针裁决轮 worker。**置信度**：candidate（两载具残差族实测分族，机制由两路径阶段覆盖差支撑）。**module**：通用方法论（验证可比性 / 残差归因）。
- **来源定位**：260904-04 探针裁决轮（block_probe -features 全程 vs mod cppReplace 存档口径）+ 07 篇「存档口径残差真签名改判」小节。

#### 观察（现象）

同一 seed 同一区域的「残差」在两种载具下分属完全不同的族：block_probe -features 全程路径残差主体 = **ore 矿石族 desync（98.56%）**；mod cppReplace 路径（存档口径）残差主体 = **stone→dirt/sand blob 置换族（99.1526%）**。两族 top 对、y 分布、连通域形态均无交集。

#### 根因（机制）

两载具的**阶段覆盖与拦截面不同**（block_probe 走探针自带全程管线，cppReplace 只拦 populateNoise+buildSurface、features 由 Java 跑）——残差是「本侧实现 × 载具覆盖面」的联合产物，不是被测实现的固有属性；换载具即换残差族。

#### 定位 / 判据

残差分析第一步先声明载具；两载具的残差 top 对表并排无同族对即证不可互引。

#### 教训 / 可复用判据

1. **跨载具残差结论（top 对/占比/签名）禁止互引**——引用他载具残差数字前先核 §9.7 三要素的「载体」一项是否同源。
2. 同族：#10（三阶段归因法——先分阶段再定位机制）、#18（跨 session 基准数字不可直接续推）；本条是 §9.7「载体可比性」在残差归因域的具体化实例。

**#33 补充案例（260907-10）**：diag bin 直读数据目录载体不经 Java remap/SRG 管线 → 生产复跑判别力**结构为零**，§9.7 声明收口——V2（mod namespace AGG 恒等，diag_modns 直读数据目录）与 V3（biome override 分支，Rust+数据层无 SRG 暴露面）生产面不重跑；生产数据目录（mod jar 解压）本就不含 testcontent 数据 → vivo 无触发场景。判据：动生产复跑前先问「该验证路径是否经过生产特有层（remap/SRG/生产数据目录）」——不经 = 复跑零信息，声明收口 + dev 证据维持。本条的生产侧对偶面：**载具不经生产层 = 生产复跑无意义**。来源：.artifacts/forge-prod-e2e-260907-10.md §2。

---

### #35 量级核算排除法定位写者

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #35（A 类）

- **发现时间**：260904-04。**发现者**：探针裁决轮 worker。**置信度**：candidate（核算判据 + 实测零出界）。**module**：通用方法论（排除法 / 量级核算）。
- **来源定位**：260904-04 vein 展宽核算：**ore_dirt 纵向展宽 ≤±5，origin y∈[0,158] 零出界**。

#### 观察（现象）

残差中 **y>200 的 stone→dirt 1362 cell** 需要定位写者。ore_dirt 候选可被纯核算排除：其纵向展宽上限 ±5、origin y∈[0,158]，则写入 y 域上界 = 163，**零出界**——y>200 的 1362 cell 确定非 ore_dirt 所写，无需逐块验证。

#### 根因 / 判据

每个 feature/阶段有可核算的几何包络（origin 域 × 展宽上限）；待归因残差的坐标域落在其包络外即可机械排除，落在包络内只算「未排除」不算「确认」。

#### 教训 / 可复用判据

1. 定位写者优先做**包络核算**（origin 域 + 最大展宽/偏移 → 可写坐标域），一轮算术替代多轮探针；「包络外 = 确定排除」是排除法里少有的确定性判据。
2. 同族：#22（自由参数凑数反模式——乘数要有独立实测来源）；本条是量级核算在「写者定位」上的正向用法（#22 是反例警示）。

---

### #38 判读源码语义前必须核 env 默认值方向

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #38（A 类）

- **发现时间**：260904-06（锚 git 9157191）。**发现者**：fan-out worker b1 误读 + judge R1 取代链捕获（§15.4）。**置信度**：candidate（单轮误读实证，E2' 实测零差佐证修正后口径）。**module**：通用方法论（源码判读纪律 / 判别实验设计；#20 家族）。
- **来源定位**：`.investigations/lossless-accel/fanout-writer-260904-06/b1-surface-oob-writer.md` §9.0-R1（原 §2.1「WG_EST_SHARED 默认关」→ 实际默认开，`=0` 才关；worldgen_handle.rs L559 注释 + L563）+ convergence-260904-06.md。

#### 观察（现象）

b1 worker 依据「变量名含 shared、默认初始化分支在独立重扫路径」推断 WG_EST_SHARED 默认关，E2 实验方案按「=1 反转开启」设计。实际该 env 默认开（env_enabled 语义），`=0` 才关——若按原方案跑 E2，实验臂与默认臂同值，产出「est 路径无差异」的死参数假判别（#20 家族），且方向恰好被主会话执行前核对拦下（R1 取代记录）。

#### 证据

- E2' 按「=0 关」口径重跑：关/开两臂导出 sha256 逐字节相同（2ff71249…）——两路径语义同一为真结论，但默认方向若读反，同一实验会得出「开了也无效」的错误表述并污染后续 est 嫌疑链。

#### 根因（机制）

Rust 侧 `env_enabled("WG_X")` 类开关默认值 = 未设即开，「默认关」直觉来自 CLI flag/feature-gate 惯例；worker 静态判读时以命名直觉替代了对 env 读取 API 语义 + 默认值字面量的核对。#20 判的是「自变量真被改变」，本条补其上游一步：**实验设计者对自变量语义（方向/默认值/反转点）的判读本身要先验证**。

#### 如何利用

1. **A/B env 实验设计前三查（grep 源码，一轮完成）**：① env 读取 API 语义（env_enabled=默认开 / env_var+parse=默认看代码）；② 默认值方向（未设时走哪条路径）；③ 源码注释中的「=0 反转」「legacy, default on」类标注（如 worldgen_handle.rs L511-515 注释模式）。
2. worker 产出含 env 实验模板时，主会话执行前 MUST 核对默认值方向（本轮 R1 即此核对救命）——命令委托契约的「只执行不解读」不含「不核对实验前提」。
3. 家族索引：#20（死参数假判别）/ #32（daemon 吞 env）/ #25（常量追取值源头）/ 本条（env 默认方向判读三查）。

---

### #39 参照自身缺陷辨识（mod≠参照≠mod 错）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #39（A 类）

- **发现时间**：260904-06（锚 git 9157191）。**发现者**：fan-out worker b1（R4→R6 取代链）+ judge。**置信度**：candidate（单轮定点实证：biome 七点同 + vanilla 语义核对）。**module**：通用方法论（残差归因 / 对照基线校验；#16 对照基线归因法的对偶面）。
- **来源定位**：`.investigations/lossless-accel/fanout-writer-260904-06/b1-surface-oob-writer.md` §9.4-R4 → §10.1-R6（C++ -biomeDump (244,-60..-54,244) 七点全 = deep_lukewarm_ocean，与 mod 一致；Java VanillaSurfaceRules 该 biome 地板 = sand）+ convergence-260904-06.md「m3 证伪」。

#### 观察（现象）

(244) 列 gravel→sand 单列差异，第一归因是「mod biome_at 分叉写错」（m3）。证伪路径：C++ -biomeDump 七点 biome 与 mod 全同（deep_lukewarm_ocean）→ 分叉不在 biome 输入；再对 Java vanilla 语义核对：deep_lukewarm_ocean 地板规则命中 mr2(sand)，mod 的 sand 是**正确输出**——是 C++ 参照（block_probe surface.h）在同 biome 下未命中 sand 条目、落到 gravel fallback，**参照自身偏离 vanilla**。

#### 证据

- biome 输入一致性：cpp-biomedump-244col.txt 七点全同；
- 规则分支：surface_rules.rs L1030-1033（warm-ocean StoneDepth-floor → mr2 sand）在 C++ surface.h 未正确命中（R6，C++ 侧缺陷待查）；
- 「mod 输出 = vanilla 正确值」的最终定案留一个廉价实验：vanilla 列对照（writer-verdict 结论 3 已挂新线首实验捎带）。

#### 根因（机制）

对照基线归因法（#16）默认「参照 = 真值」，残差单向归因到 mod。但本项目参照是**自己复刻的 C++ 探针/实现**，它与 mod 一样可能偏离 vanilla——「mod 与参照不同」只证明两实现分叉，方向裁决（谁对）必须引入第三极（Java vanilla 语义/源码）或对参照本身做 vanilla 校验。#16 核「差异是否与 X 相关」，本条核「参照是否有资格当真值」——同一方法的输入端校验。

#### 如何利用

1. **单列/定点差异归因前双问**：① 两臂输入（biome/seed/坐标口径）是否真一致（先排除输入差）；② 参照在该点的输出对 vanilla 语义是否正确（Java 源码/参照表核对）——两问都过才有资格说「mod 错」。
2. C++ 探针的 surface/规则类实现与 Rust 主线是两套代码（#36 执行体不同源），参照缺陷要独立立缺陷单，不随 mod 课题销案。
3. 家族索引：#16（对照基线归因法——本条其对偶面）/ #33（载具可比性）/ #36（执行体不同源）/ #3（块级真相）。

---

### #42 静态机制断言未实测当公理续推（一轮 dump 即证伪）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #42（A 类）

- **发现时间**：260904-06。**发现者**：P-B1-2 判别探针执行中顺藤发现（负值）。**置信度**：candidate（生产 dump + 点采双载体交叉；**布局无关硬数据**，不随布局事故作废）。**module**：通用方法论（机制断言验证纪律）。
- **来源定位**：`.investigations/lossless-accel/incident-layout-260904-06.md`（「仍成立」清单：WG_DBDEBUG 按 y 直印不经 blocks 布局）+ `.investigations/lossless-accel/fanout-curtain-260904-06/p4-reference-check-260904-06.md` Facts #1/#2（读数本身有效，仅其 stones 参照解读作废）。

#### 观察（现象）

「幕帘带 = 0<d≤0.39」作为机制描述贯穿幕帘课题及上游归因，从未对生产执行体实测过 d 值。WG_DBDEBUG 生产密度 dump 一轮实测：列 (195,199) y192-318 密度**全负**（y256-318 = −0.024995，y192-255 = −0.458333），density_probe 点采 %.17g 与生产一致——「0<d」前提当轮证伪。此读数按 y 直印、不经过 .blocks 布局，是布局事故中明确存活的硬数据。

#### 证据

- 生产 dump（`.tmp/p2full/cpp-dbdebug-195-199-260904-06.txt`）与点采（`cpp-fdcol-195-199.txt`）双载体交叉一致；
- 负值量级与 b1 静态理论地板（−0.025/−0.458）逐位吻合——静态推导能预测正确值，恰说明「d 的符号」这类**可实测命题**不该停留在静态描述。

#### 根因（机制）

「0<d」是从 Java 源码静态读出的符号级断言，在课题内被降格为背景描述反复引用，无人把它当「待实测假设」——机制断言的置信度应与证据层匹配：静态读码 ≠ 数据层实测（trace/probe），下游归因把它用成了公理。本案的连带教训：被实测推翻的断言（d>0）与被布局污染的参照解读（131 stone 族）曾共同支撑同一份裁决——断言层与数据层错误会互相掩护，实测硬数据（布局无关载体）是拆穿的关键。

#### 如何利用

1. **判据**：符号级机制断言（「X 带内 d>0」「此路径恒 return」类）进入归因链前 MUST 一次数据层实测（env 门控 dump / 点采探针，一轮以内）；实测与静态读数冲突时以实测为准并回溯引用点。
2. 课题结案/取代时清点：被依赖的机制描述里有几条从未实测过？未实测的逐条标「static-only」再结案。
3. 裁决依赖的硬数据优先选布局/变换无关载体（按 y 直印的 dump、引擎内计数），使裁决对下游读法 bug 免疫。
4. 家族索引：#25（Java 常量追取值源头）/ #17（跨探针对比坐标钉死律）/ #40（布局纪律——同一裁决的另一半教训）/ AGENTS 交接结论验证纪律（§16.3 廉价独立验证的机制断言特例）。

---

### #45 同输入异分类：三源隔离法 + 定点直读 + 坐标语义隔离

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #45（A 类）

- candidate（residual12→13 全链实证）；三子模式：
- 45a 三源隔离法：同 seed 同 pick 同 6d 下 C++/Java/Rust 分类不一致 → 先确认三方距离运算域（定点 vs 浮点）再查采样链（O(1) vs O(链长)，先做便宜的）。配套：穷举语义「数学正确」候选 vs 树遍历语义实际胜者冲突时，穷举语义不可作 ground truth（本例穷举⇒deep_lukewarm，Java/C++ 实际⇒deep_ocean，错的是穷举本身）。
- 45b NoiseValuePoint 无 double getter（全 long 定点字段）；反射 dump 方法表确认签名后取 *Noise() long getter 是唯一直读通道（mnDump 探针 -Pbiome6mnDump=x,y,z）。定性判据：直读值为 4-5 位整数（t=2000）而非 [-1,1] 浮点 → 到手即定点域原值。
- 45c 探针直采 router DF 用 quart 坐标语义（t=0.1121）≠ 生产 biome 链 (px<<2) 块坐标语义（t=0.200032）——打印坐标≠采样坐标，BIOME6 直采值与分类输入不可互比（#17 坐标钉死律新实例：同探针两输出通道语义不同）。破局 = 生产语义路径（MultiNoiseSampler.sample 反射）直读。
- 证据：.investigations/residual13/probeB-h2-260904-13.md + .artifacts/lossless-accel/residual9-verdict-260904-13.md §4.1/§4.3。

---

### #52 确定性区域 dump 载体（代码 diff 唯一变量）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #52（A 类）

- **时间/置信度/module**：260905-06；candidate（idk-7 修复裁决实跑：171,442→118,697，−30.8%）；workflow-patterns / 验证载体设计。

#### 观察
#51 判明跨 run A/B 噪声（241,080）与信号（239,594）同阶后，课题的裁决需求不变、载体必须换。本轮落地的**确定性区域 dump 载体**四要素：

1. **纯实现直接生成整域**——绕开服务器 run 链路（无停服时机/init 时序/完成度自由度，#49/#50/#51 三类噪声源全部物理消除）：`worldgen-core/src/bin-diag/idk7_region_dump.rs`（bin-diag 隔离，不参与默认构建）；
2. **原始 id dump**——同域 chunk 的 block id 原始 dump + **blocks.json 映射 name 域**（对比一律 name 域，v3 口径延续）；
3. **固定参照快照**——对拍 vanilla06 快照（固定文件，不重跑 vanilla），参照侧零随机性；
4. **SHA256 对拍**——dump 文件哈希先行等值判断，不等再逐 chunk diff 定位。

效果：比较两端都是确定产物，**代码 diff 成为唯一变量**——「修复前后残差 171,442→118,697（−30.8%）」这类量级结论首次变得可裁决（§9.7 三要素随行：载体 = region name 域对 vanilla06 快照 / 覆盖面 = 2193 chunks 全域 / 可比性 = 同快照同脚本）。

#### 如何利用
1. **判据**：课题的裁决目标若为「差异量级收敛」（而非「有无回归」），MUST 用确定性载体——纯实现直接生成 + 固定参照快照，两端无运行时随机性；跨 run A/B 只留作回归门（#51）。
2. 适用前提：被验证逻辑可脱离宿主独立驱动（本项目 worldgen feature 管线可纯 Rust 驱动；宿主耦合逻辑仍需实机，届时双采集对拍 #48 家族）。
3. 工具链：`worldgen-core/src/bin-diag/idk7_region_dump.rs` + `.tmp/feature-parity-260905-06/v10_dump_vs_region.py / v11_dump_diff.py / v12_tree_breakdown.py` 脚本链（dump→对拍→diff→按 feature 分解）。
4. 家族索引：#47（golden 逐位不变对照——纯函数内核侧同思想：冻结确定性基线）、#48（双采集对拍——不可冻结输入侧的姊妹模式）、#51（本载体的动机面）。

#### 证据
`.tmp/feature-parity-260905-06/`（v10-v12 脚本 + dumpnew/dumpold 目录）；13 篇 260905-06 小节（草稿）记录裁决数字。

---

### #53 env 门控默认值当公理 → 强制三查

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #53（A 类）

- **时间/置信度/module**：260905-10（实际 2026-09-05）；candidate（dump 哈希两臂全等实锤 + 源码消费点直读）；workflow-patterns / 验证方法论（#37/#20 家族第二犯 → 判据升级）。

#### 现象（现象→根因）
260905-10 采集臂把 `WG_CA_MIN` 当**默认关**设计对照实验（「不设 env = 关闭臂」）。实际 `worldgen_handle.rs:876` 用 `env_enabled`（unset → true）——**默认开**。结果两臂 dump 全等（`region_bee.bin ≡ region_bee_ca.bin`，SHA256 4D216088…C48FD），「对照实验」里自变量根本没被改变，差点把同态双臂读成机制结论。

#### 根因（机制层面）
把交接/上一轮的口头结论（FEA-9「WG_CA_MIN 默认关」）**当公理直接继承**，没有做消费点直读这一廉价独立验证（§16.3 宿主交接验证）。env 门控的默认值方向是**实现细节**（`env_enabled` vs `.is_ok()` 判存在，语义相反：前者 unset→true、后者 unset→false），口头描述层不携带这个信息。

#### 定位（怎么发现的）
行为化哨兵（#37 判据）：两臂 region dump SHA256 必须不同才算开关生效——本轮哈希全等直接暴露；随后源码消费点直读 `worldgen_handle.rs:876` 确认 `env_enabled` 语义。历史：#37（env 判别行为化）已立、260905-09 纪律要点已警告过一次，**此为第二犯**。

#### 修复/规避
判据升级为**强制三查**（缺一不开工）：
1. **源码消费点直读**：`env_enabled`（unset→true）还是 `is_ok()` 判存在（unset→false）——默认值方向只认代码，不认交接文字；
2. **对照声明核对**：对照 NEXT_SESSION/注释/纪律要点里关于该开关的声明，与①冲突即显式记取代（§15.4）；
3. **行为化哨兵**：开关两臂 dump/输出 hash 必须不同，才承认「自变量真被改变」（#37 家族，#20 死参数判据的 env 面）。

#### 教训/判据
1. 「口头/文档结论说默认关」≠「默认关」——env 门控默认值是代码层事实，交接文字层不可信，MUST 直读消费点。
2. 家族索引：#37（env 判别生效证据必须行为化）、#20（死参数制造假判别）、#32（daemon 吞 env 死同值）、#36 补充案例（交接结论廉价验证）——本条为该家族第二犯后的**强制化升级**：从 SHOULD 变 MUST 三查。
3. 两臂 dump 全等本身是强信号：设计为对照的实验得到零差异，先怀疑开关没生效（+门控概率极低如 gate 0.002 两解），再怀疑机制无差异。

#### 证据
`.artifacts/feature-parity/candidate-beehive-260905-10.md` §3（交接口径修正①）；`worldgen_handle.rs:876`（env_enabled 消费点）；`.tmp/feature-parity-260905-10/`（region_bee.bin ≡ region_bee_ca.bin 哈希留痕）。

---

### #56 新分支禁止落在 catch-all 之后（编译过≠命中）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #56（A 类）

- **时间/置信度/module**：260906-04；candidate（panic 日志 + 源码目视双证，修复后 end 分支命中实证）；workflow-patterns / Rust 移植陷阱。

#### 现象（现象→根因）
`create_for_dim("end")` panic：`resolve minecraft:end/sloped_cheese failed: unsupported density type 'minecraft:end_islands'`——而 end_islands 的 match arm 明明已经写好。

#### 根因（机制层面）
新分支被插在 `_ => return Err(...)` **之后**。Rust match 按序匹配，catch-all 先命中。与 Java switch-case 陷阱同类，但 Rust 更隐蔽：编译器对 unreachable pattern 只告警不报错，且 `_ =>` 在前时**新 arm 不算 unreachable**（它是可达的，只是永远轮不到），连告警都没有——完全静默。

#### 定位（怎么发现的）
读 `density_builder.rs` L385-395 目视确认 arm 顺序。无工具成本——但前提是想到「先查顺序」这个方向。

#### 修复
end_islands arm 移到 `_ =>` 之前。

#### 教训/判据
1. **判据（MUST）**：给大 match 加分支时禁止落在 catch-all 之后；PR/review 时对「新增 arm」先 grep catch-all 位置。
2. 「编译过 + warning 不新增」≠「命中」——**新增分支必须有运行时命中证据**（一条日志/一个探针值），首次接入新数据（end.json）时首个端到端 run 即暴露，此例正是首跑 panic 才发现。
3. 家族索引：与 #20（死参数制造假判别）同构——「写了但没生效」的静默失效家族，本条是 match 序位置版。

#### 证据
`.investigations/end-takeover/260906-04-errors.md` E1；`density_builder.rs` L385-395。

---

### #57 哨兵值跨模块传递必须在边界做语义变换

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #57（A 类）

- **时间/置信度/module**：260906-04；candidate（RUST_BACKTRACE 链 + 哨兵定义 grep + 修复后空列 chunk 通过实证）；workflow-patterns / 跨模块边界语义（维度移植通用）。

#### 现象（现象→根因）
benchseed fill 外围 chunk panic：`attempt to subtract with overflow` @ `biome.rs:349`（`block_y - 2`，block_y = i32::MIN）。

#### 根因（机制层面）
`ChunkDensity.surface_height` 的空列哨兵 = i32::MIN（`terrain.rs:241`「无 solid」）。end 外岛空域存在**大量全空气列**——overworld 每列必有基岩，哨兵路径在生产中不可达；end 把它变成了热路径：`o = heightmap + 1` 把 MIN 直接喂进 biome 采样链。Java 语义：WORLD_SURFACE_WG 空列 get = `bottom - 1`（一个有界的合法值），不是 INT_MIN。这是**维度特有路径缺陷**——同一代码在旧维度全对，换维度即炸。

#### 定位（怎么发现的）
`RUST_BACKTRACE=1` 给出 closure 链（build_surface closure$1 → biomeCellKey closure），确认溢出发生在哨兵消费点；grep `surface_height` 定义处见哨兵注释。

#### 修复
在 `fill_terrain_column` 消费点统一映射 `MIN → min_y - 1`（对齐 Java Heightmap 空列语义）。选**消费点边界**而非生产点改哨兵：所有下游消费者（features/placement 等）同样受益，且 MIN 哨兵本身保留「无值」判别能力。

#### 教训/判据
1. **判据（MUST）**：哨兵值跨模块传递前，必须在边界声明语义并做显式变换——下游代码不应当面对裸 INT_MIN 做算术。
2. **新维度接入的固定测试面**：「新维度新地形形态（全空气列/全液体列/超高层列）」是哨兵路径的天然压力测试——新维度首跑 MUST 覆盖空列 chunk，不能只用旧维度坐标烟测。
3. 判错经验：debug profile 下「subtract with overflow」+ 操作数 = 极值 → 先查上游哨兵/未初始化语义，不是先查公式精度。

#### 证据
`.investigations/end-takeover/260906-04-errors.md` E3；`terrain.rs:241`（哨兵定义）、`biome.rs:349`（溢出点）。

---

### #61 复算逐位吻合必须先证公式覆盖正确调用点

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #61（A 类）

- **发现时间/发现者**：260906-06（实际 2026-09-06），core.worker subagent 草稿 + 主会话应用；来源课题 jungle-l J5 基线重采（E10 归属反转）。
- **module**：workflow-patterns / 复算判据覆盖面（#43「逐行对拍必须附覆盖面声明」家族的随机源扩展）
- **现象**：目标 chunk (29,-16) 日志内两条 population 行恒并存（-4568… / -2605…）；popseed_check2.py（java-LCG 复算）逐位命中 -2605，E10 据此判定 -2605 = 正确 seed FEATURES pass、-4568 = 「污染 pass」——归属完全颠倒。统计签名：5×5 forceload pregen 全序列 1154 population 行中 **529/625 chunk 双 pop 并存**——确定性单调用原理上不可能，判据本身必错。
- **根因（机制）**：`setPopulationSeed(worldSeed, x, z)` 在 1.20.1 有**两个调用点、两个不同 baseRandom**：`ChunkGenerator.generateFeatures`（ChunkGenerator.java:344，Xoroshiro128PlusPlusRandom）与 `NoiseChunkGenerator.populateEntities`（NoiseChunkGenerator.java:462，CheckedRandom = 48 位 java LCG）。同 chunk 两个 pass 各产一条 pop。java-LCG 公式命中的是 populateEntities 行，Xoroshiro 公式命中的才是 FEATURES 行——**「逐位吻合」只证明「该公式与某条输出一致」，不证明「该公式对应目标 pass」**。
- **定位（怎么发现的）**：① 双 pop 频次统计（529/625）触发「单调用假设证伪」；② 一手 yarn 源码 grep `setPopulationSeed` 调用点；③ ChunkRandom.next(bits) 基类分流核对（ChunkRandom.java:29-61）；④ Xoroshiro 复刻（pop_feature_xoroshiro.py）对「第一条」pop 逐位命中（-4568734542690011764 @ (464,-256)），与 mega 生成语义一致，交叉印证。
- **教训/判据（MUST）**：
  1. 任何「独立复算逐位比对」类核验（第四查、对拍、指纹比对）**先证公式/复刻覆盖正确的调用点**，再信逐位吻合；同参数不同实现的多次调用是逐位核验的天然盲区。
  2. **双 pop 恒并存（同 chunk 两条 population 行）= 双调用点统计签名**；频次统计（非单例）是零成本的第一道「调用点覆盖面」体检。
  3. 交接结论中的复算判据本身也要过「交接结论验证纪律」——E10 的判据未经调用点核对就续推了多个工作块（#43 家族第三犯面）。
- **证据**：.investigations/jungle-l/260906-06-errors.md E11 + .investigations/jungle-l/j5-baseline-260906-06.md 核心发现 1 + .tmp/jungle-l-260906/pop_feature_xoroshiro.py（源码引证 ChunkGenerator.java:344 / NoiseChunkGenerator.java:462 / ChunkRandom.java:29-61）。

---

### #64 未受控观察真值表必须降级标注

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #64（A 类）

- **发现时间/发现者**：260906-07，V1 复验边界声明 + judge 倾向 2 附议 + 用户实机观察看错自纠；core.worker subagent 草稿 + 主会话应用。
- **module**：workflow-patterns / 观察条件受控性（#17 坐标钉死律的观察侧对偶：坐标钉死 = 输入侧受控，旁观/F3 截图 = 观察侧受控）
- **现象**：原始 11 点「实机真值表」（260906-05）采集时「是否开旁观」未确认/未记录；本轮用户一次未开旁观的目测复验即看错（505 点），后自纠。
- **根因（机制）**：目测（非旁观、无 F3 Targeted Block）对「树有无/归属」判定误差渠道不可封死（远处大树、藤蔓遮挡、chunk 未加载均致漏看/误归属）；未受控观察把**观察器误差**混入**被测系统差异**，交叉表格子级判别力被静默稀释——且与 #65 叠加：该表当时还被误当「Java vanilla 基线」，双重口径失真。
- **如何利用（判据 MUST）**：
  1. 人工观察真值入对照表前，观察条件必须受控并记录（spectator + F3 Targeted Block + 截图含 /seed）；未确认受控的行 MUST 降级标注，不得与受控行同级参与判别。
  2. 「观察误差」候选权重不要先验自判太弱——一次实际失察即可翻案；孤例/疑点优先受控复验一锤定音再谈归因。
  3. 观察侧与输入侧同权受「钉死」纪律约束。
- **证据**：v1-vanilla-client-evidence-260906-07.md 边界节 + judge-verdict-260906-07.md §三（B3 权重回调）+ j5-baseline-260906-06.md（11 点表观察条件未记录）。

---

### #77 回滚 ≠ 引用面清理（配置/脚本/默认值路径引用）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #77（A 类）

- **发现时间/发现者**：260907-07，core.worker subagent 草稿 + 主会话应用。来源课题：260907-06 工作块事故复盘 + 260907-07 修复轮（judge PASS-with-conditions）。
- **module**：workflow-patterns / 回滚撤回完整性（#36「执行体三元组/权威源核对」家族相邻但独立——#36 管「信谁」，本条管「回滚清干净没」）
- **现象**：260907-06 把 Java 改动错误落到外部目录 E:\PYTHON\MC 后执行回滚：`git status` 零改动、源码 grep 零命中——「源码面」回滚干净。但构建配置/脚本里的外部路径引用**全部残留**：gradle.properties `org.gradle.java.home`、run_rust_client.ps1 `JAVA_HOME`×2、build.gradle `hs_err`×2、JniProbe/ReadWorldProbe 默认值——下一轮构建直接失败（"Java home invalid"），事故影响面跨界存活到后续工作块。
- **根因（机制）**：「回滚完整性」被操作化为「源码 diff 消失」，但一次错误改动留下的痕迹不止 git 管理的源码 hunk——**路径类改动会扩散到 git 未跟踪或构建配置层**（gradle.properties/启动脚本/probe 默认参数），这些位置不在「源码回滚」的检查半径内，形成「hunk 零残留 ≠ 状态零残留」的检查盲区。与 #23 补充案例同构：**结论（回滚完成）的声明范围 ≠ 检查的覆盖范围**。
- **定位**：下一轮构建失败（"Java home invalid"）回溯——失败签名直接指向残留的 java home 外部路径，grep `E:\PYTHON\MC` 于配置/脚本层逐处命中。
- **修复**：260907-07 逐一清理残留引用面（gradle.properties×1 / run_rust_client.ps1×2 / build.gradle×2 / JniProbe / ReadWorldProbe → CoreSwap 路径或现役 JDK17 D:\Program Files\Java\jdk-17.0.12）。
- **如何利用（判据 MUST）**：
  1. 任何回滚/撤回动作的完整性检查 = **两层**：① 源码层（git status/diff 零改动）② **引用面层**——grep 撤回涉及的外部路径/旧值于：构建配置（gradle.properties/Cargo.toml/Makefile）、启动/辅助脚本（*.ps1/*.sh）、探针与诊断程序的默认值（DEFAULT_*）、文档交接件（NEXT_SESSION 等）。两层全绿才可声明「回滚完成」。
  2. 涉路径的改动在**落地时**就应登记「引用清单」（改了哪几处路径引用）——回滚时按清单核对，而非事后 grep 碰运气。
  3. 回滚后下一轮开工的首次构建/运行是引用面残留的最廉价探测点——失败即先查残留引用，不先查代码。
- **家族索引**：#36（权威源核对——本条是其回滚场景的姊妹判据）、#23 补充案例（结论声明范围 ≠ 检查覆盖范围）、#24（配置层静默失效家族）。
- **证据**：260907-06 事故回滚记录（git status 零改动 + grep 零命中 vs 构建失败）；260907-07 修复记录 + judge PASS-with-conditions。

---

### #78 代码注释内嵌日期 ≠ 时间戳权威

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #78（A 类）

- **发现时间/发现者**：260907-07，judge N8 观察提炼；core.worker subagent 草稿 + 主会话应用。
- **module**：workflow-patterns / 日期溯源纪律（AGENTS.md §三.5 日期纪律家族——「日期 MUST 取宿主/git 时间戳」的代码域形态）
- **是什么**：jni_bridge.rs 既有注释含「双跑修复 2026-09-08」——晚于该工作块实际日期（git 时间戳锚 2026-09-07 前后）。代码注释里手写的日期可与 git 提交时间戳不吻合（成因未查：预推日期/补写/转录漂移均可），但**权威性排序不变：git 时间戳 > 注释内嵌日期**。
- **如何利用**：任何「某改动发生在何时」的溯源，以 `git log` 为准，注释日期只作线索；发现注释日期与 git 时间戳矛盾 = 日期漂移信号，顺手修正注释（低成本），不据注释日期做任何时序推断。
- **证据**：jni_bridge.rs 注释「双跑修复 2026-09-08」vs 260907 工作块 git 时间戳；judge N8（260907-07）。

### 发现 #10 补充案例（260907-07，第二例）：Rust release 重构建 sha 非确定性——dll sha 基线必须带记录日构建上下文，跨块基线引用前先 rebuild 复核

- **时间/置信度/module**：260907-07；candidate（同源码 rebuild 两轮复现实锤）；workflow-patterns / 同 dll 重跑非确定容差（#10 判据在构建产物 sha 域的形态）。
- **是什么**：同源码 HEAD 干净 `cargo build --release` 两次，worldgen.dll sha 不同：D9085130→DC8FF3A2（260907-06 记录）；260907-07 接线前 rebuild 复现 DC8FF3A2，与 NEXT_SESSION 记录逐位一致，完成跨块交叉验证。Rust release 产物 sha 不具备「同源码 ⇒ 同 sha」性质。
- **如何利用（判据 MUST）**：
  1. 引用历史 dll sha 基线时，**必须连同「记录日 + 构建命令 + 源码 HEAD」上下文一起引用**——裸 sha 无可比性声明（§9.7 三要素在 sha 域的落地）。
  2. 跨工作块做 sha 一致性核验（如发版工单 hash 双重校对前），先在当前环境 **rebuild 一次复核基线**再比对，不直接拿历史 sha 判「不一致=事故」。
  3. 「sha 变了」在 Rust release 域不构成异常信号本身；异常信号 = 同一轮 rebuild 复核后仍与预期不符。
- **家族索引**：#10（同 dll 重跑非确定容差——本条为构建产物 sha 形态）。
- **证据**：260907-06 rebuild 记录（D9085130→DC8FF3A2）；260907-07 rebuild 复核（DC8FF3A2 与 NEXT_SESSION 记录逐位一致）。

---

### #79 「创建期解析 + 运行期注册」类资源必须惰性化

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #79（A 类）

- **时间/置信度/module**：260907-09；candidate（实机数据层证据 + 修复后复现 570 段 + 对照臂双证）；workflow-patterns / 资源生命周期时序（跨语言接线通用）。
- **现象**：真实内容 mod 方块 `testcontent:test_brick` 作 `CORESWAP_DEFAULT_BLOCK` 时，Rust 区块整片地形填成空气；日志 `[BLOCKS] unknown block 'testcontent:test_brick' -> AIR`（创建期一次性打印）。
- **根因**：`WorldgenHandle::create_for_dim` 在**创建期**做 `blocks.id(default_block_name)` 解析，而 mod 方块注册（`wg_register_block_id`，CppBridge.registerModBlocks）发生在 SERVER_STARTED——**晚于 handle 创建**。创建期解析 miss → default_block 落到 AIR 兜底，后续每 chunk 地形填充全部继承空 id。机制层面：名字解析是一次性快照，注册是运行期增量——**跨创建边界的名字解析是时序陷阱**，两侧行为各自正确、组合即错。
- **定位**：env override 行为化日志（smoke7 三维命中证明 env 链通、排除 env 死）+ 全空气 region 直方图（整片 AIR 而非局部缺失 → 指向 default_block 而非 surface/feature 层）→ 创建期 `unknown block` 日志行锁死解析时点。
- **修复**：SurfaceBuilder 增 `default_block_name` 字段，消费点 `default_block_id()` **惰性按名解析（每 chunk 一次，非每块）**；worldgen_handle.rs（fill_terrain_column / diag_pre_surface_column）与 surface_rules.rs（build_surface / place_badlands_pillar）四个消费点改走惰性解析。默认路径（minecraft:stone/netherrack/end_stone）名字创建期已注册，解析结果恒等，零语义扰动（对照臂 `minecraft:coarse_dirt` 同法 570 段落世界双证）。cargo test 7/7。
- **教训/判据**：
  1. 任何「创建期解析 + 运行期注册」组合的资源（id 表/注册表/命名查找），解析必须惰性或可重解析，解析点必须晚于最晚注册时点——不为最晚注册者设计 = 对第一个 mod 内容即坏。
  2. 「先注册后创建」的时序假设要写成结构保证（如 CppBridge.registerModBlocks 排 SERVER_STARTED），并在接线上声明依赖的时序窗口。
  3. 整片统一异常（全 AIR/全 stone）优先怀疑 default/兜底值解析失败，而不是逐层地形逻辑。
- **证据**：.investigations/realmod-e2e/realmod-e2e-260907-09.md（smoke2-12 轮次表）；.tmp/realmod-smoke11/12-260907-09.log；.artifacts/realmod-e2e-260907-09.md §2。

---

### #81 A=B 恒等不能证明分支生效（两臂可能同走旧路径）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #81（A 类）

- **时间/置信度/module**：260907-09；candidate（方法论补案例，因果链已闭合）；workflow-patterns / 判别实验设计（#20/#37 家族）。
- **观察**：260907-05 A 组缺口 2 的「mod settings 路径 vs 短名路径 A=B 逐位恒等 = 零扰动」结论，在本块发现其 A=B 同样兼容「env/覆盖通道整个死了、两臂都走旧路径」——恒等观测无法区分「分支生效且零扰动」与「分支从未生效」。缺口 4 同名 biome override 的实测（修复前 8×8 AGG 恒等 = 覆盖恒被 skip）证实了该 idk 为真缺陷。
- **根因**：A=B 恒等只证明「两臂输出相同」，不证明「被测分支在任一臂中被执行」。自变量（分支是否激活）从未被观测，B 臂的「mod 路径」在 skip 规则下实际退化为 vanilla 路径。
- **如何利用（判据）**：
  1. 分支/覆盖/env 类判别的闭环证据 = **行为化分支日志**（#37：如 `[biome] override load` ×5、`[WGH] env override` ×3）**加上** A/B hash 双向变化（生效臂 AGG ≠ baseline + 恒等副本回归 = baseline），二者缺一不可。
  2. 「自变量真被改变」恒等式自检（#20）在覆盖/分支场景的形态：先证明分支被执行（单边改动使 hash 变），再谈恒等=零扰动。
  3. 见到 A=B 恒等，先问「若分支死了，观测是否同样恒等？」——是则恒等无判别力。
- **家族索引**：#20（死参数假判别）+ #37（env 行为化证据）+ #32（daemon 死同值）家族补案例。
- **证据**：.artifacts/a-group-4-gaps-260907-05.md（原 A=B 交付）vs .artifacts/realmod-e2e-260907-09.md §4（修复后 AGG bea29a995b01b3d3 → 0bfff659653ce8a7 + override load ×5 行为化命中）。

---

### #84 INFO 级日志 grep 结构性假阴性 + 旁证计数红鲱鱼

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #84（A 类）

- **发现时间**：260908-04
- **发现者**：主会话实测（mod-compat 课题 R4/R5 自建客户端轮）
- **来源定位**：`.investigations/mod-compat-260908-02/voxy-debug-260908-03.md` §260908-04 增补·事件1 + `cmd-output/` R4/R5 日志
- **置信度**：candidate
- **module**: workflow

**观察**：判「Connector 未认领 coreswap」的两条依据双双失效——① INFO 级日志 grep「Found valid mod/coreswap」零命中，但 Connector 的认领行 `Found valid mod file coreswap-..._mapped_srg_...jar with {coreswap}` 本身是 **DEBUG 级**；② 「Dependency resolution found 1 candidates」换可认领的版本重跑仍 1 candidates——该计数与认领**无因果**（红鲱鱼）。开 `-Dforge.logging.console.level=debug` 后认领行立现，`.connector` 缓存中两版 `_mapped_srg` 重映射 jar（时间戳）= 装载直证，两版 jar（sha 不同、大小同 1431457）均被正常认领+remap+mixin 注入。

**根因**：日志 grep 是对**日志级别过滤后的视图**做搜索——目标行只存在于 DEBUG 视图时，INFO 级 grep 的零命中是结构保证的假阴性，与「事件未发生」观测上不可区分；旁证计数（candidates）与结论之间无机制因果链时，其「不变」不构成任何方向的证据，但两条独立失效证据叠加会产生强假象（险些触发 fan-out）。

**如何利用（判据）**：
1. **判「某日志事件不存在/未发生」前 MUST 先核目标行的日志级别**（源码/上游文档一手核对），搜索域必须覆盖目标级别；级别未核的零命中只能记「未观测到」，不得记「未发生」。
2. 旁证计数/汇总行（candidates、mods=N、found X）引用前先问「它与结论之间是什么机制因果」——无因果链的数字是红鲱鱼，其变化与不变化都无判别力（#20 死参数假判别的观测侧形态）。
3. 多条证据指向同一否定结论时，逐条验伪而不是加总置信度——证据可各自独立失效。
4. 环境类 mod（Connector/FML）排查默认先开 debug 级日志再 grep，成本远低于误判后的返工。

**家族索引**：#37（行为化证据在场判别——本条为其前置条件：先保证搜索域能看到行为化日志行）；#20（死参数假判别）；#59（文件在但没被读——同属「观测不到 ≠ 不存在」家族的 grep 侧形态）。
- **证据**：`.investigations/mod-compat-260908-02/voxy-debug-260908-03.md`；R4（INFO 级假阴性）vs R5（debug 级认领行 + `.connector` 缓存时间戳）日志对比。

---

### #85 关服瞬间批量同源异常先做时序排除

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #85（A 类）

集成服关闭时（log `Stopping server`/`Stopping singleplayer server` 之后数秒），DH InternalServerGenerator 的 pending chunk 请求批量抛 RuntimeException UNLOADED（本例 34 条全部集中在 12:11:10 一秒内，紧随 12:11:08 关服行）。判据：**时序紧邻关服行 + 同一秒批量 + 同源签名** = 关服取消 pending 任务的预期形态（「请求被取消」属推断非日志直证，Partial 级），先做时序排除再排查，免得把关服副作用误立为独立课题。来源：.artifacts/dh-e2e-verdict-260908-06.md §非阻塞观察（judge N-4 注记）。

---

### #88 生成期探针 = 一次性窗口（在盘 ≠ 会再经过探针）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #88（A 类）

- **时间/置信度/module**：260908-11；candidate（dbg 行确认采样点在 chunk 生成期触发 + 复跑零命中可复现）；workflow-patterns / 探针采集纪律（#19 删 run\world 家族的**生成期探针**形态，#13「探针零输出先查过滤/驱动条件」新分支）。
- **来源定位**：`.investigations/mc-1216-port-260908-11/errors.md` E3；progress-260908-11.md §F2 链级验证。
- **现象**：air 点集 aqdump 复跑（未删 `run\world`）→ `[AQDUMP] done` 但 0 行输出、输出文件未创建；同命令删 world 后正常命中。
- **根因**：aqdump 类探针采样钩在 **chunk 生成期**（worldgen 管线内）；复用已生成世界时 chunk 直接从 region 读盘，根本不重新走生成管线 → 探针窗口已关，零命中是结构性的，不是 bug。
- **定位**：对照删 world 重跑（同 seed）→ 命中恢复；「done 但 0 行 + 文件未创建」= 窗口已关签名。
- **判据/如何利用**：① 生成期探针（worldgen 管线内钩子）**每次采集前必删 `run\world`**，与 seed 三查并列成固定前置；② 「探针零输出」排查树加分支：先问「目标 chunk 会不会重新走生成路径」再查过滤/驱动条件；③ 「在盘」与「会经过探针」是两件事——凡探针挂在过程性管线（生成/加载/写入）上，其可观测窗口 = 该过程实际发生的时刻。
- **证据**：errors.md E3 三段 + progress 记录。

#### 发现 #88 附（同条收编）：E4 驱动开关与数据通道是两个开关（#20 死参数家族变体）

- **时间/置信度/module**：260908-11；candidate；workflow-patterns（#20 补充案例，随 #88 同载体记录）。
- **来源定位**：`.investigations/mc-1216-port-260908-11/errors.md` E4。
- **现象**：`-PaqDumpRust` env 数据通道已配（dbg 行确认生效）但无 AQDUMP 输出、服务器不自动停。
- **根因**：Rust 侧 dump 只打命中点，点区域 chunk 无人加载时无输出；且 forceload pregen + stop 的**驱动**由另一开关 `-PaqDump` sysprop 触发——数据通道生效 ≠ 行为链闭合，缺驱动臂 = 无人触发采样也无人停服。
- **判据**：多开关接线任务先画「开关→行为链」图：**驱动开关（谁触发/谁停止）与数据通道开关（谁记录）分开核对**，各自要有行为化证据；dbg 行只证「通道开」，不证「链闭合」（#81 同族）。新接线通道首跑无 dbg 行则三态（property 未映射/env 未传/点未命中）不可区分——新通道首跑必须先带行为化 dbg（E5，#32/#81 家族）。

---

### #93 注册名子串分发反模式（contains 误捕）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #93（A 类）

- **时间/置信度/module**：260909-02 收编（原始发现 batch 0，修复已落地）；candidate；workflow-patterns / 分发反模式（#56「新分支落 catch-all 后」家族的**分发谓词**对偶形态）。**价值门：高（反模式 + 全量排查法 + 验收面）**。
- **来源定位**：`.investigations/mc-1216-features-takeover/batch0-worker-delivery.md`（误捕面全量排查表 + E 段五段式）+ `scout-b-diff清单.md`。
- **现象**：`contains("ore")` 误捕 `forest_rock`（f-**ore**-st）与 `nether_forest_vegetation` → 走 OreFeatureConfig 解析、配置全错、无告警；placement 侧 `contains("count")` 吸进 `count_on_every_layer`（语义完全不同的 modifier，消费序不同）。
- **根因**：注册名分发用 contains 子串匹配，短高频子串（ore/count）是「子串碰撞富矿」；命中即静默走错分支，catch-all 哨兵收不到（没落 unknown）。
- **定位**：contains 各分支 × 一手注册表（1.21.6 Feature.java:27-121 / PlacementModifierType.java:8-30）全量排查矩阵，逐分支列出误捕全集。
- **修复/判据**：分发一律完整 `== "minecraft:xxx"` 精确匹配 + catch-all 告警；**新增类型时 catch-all 哨兵集合就是回归验收面**（每条已知 type 应在哨兵集合外各归其位）。
- **教训**：任何「按名字符串分发」的映射表接入新数据集时，先做「子串误捕全量排查」（分支谓词 × 数据集 type 全集），再谈逐分支语义正确。
- **证据**：batch0-worker-delivery 误捕面排查表（含 disk/spring/underwater_magma/freeze_top_layer 零误捕对照行）。

---

### #94 简报字段名/分类词不进一手源核对不可用

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #94（A 类）

- **时间/置信度/module**：260909-02 收编（batchA E-1 / batchB E-1 / batchC §四 同族三连）；candidate；workflow-patterns / 简报信息纪律（#90 转抄漂移家族的「简报→parse」形态）。**价值门：高（判错经验：凭记忆字段名写字段 → 恒 miss → 静默全默认值/全灭）**。
- **来源定位**：`.investigations/mc-1216-features-takeover/batchA-worker-delivery.md` §E-1、`batchB-worker-delivery.md` §E-1、`batchC-worker-delivery.md` §四（E-3 教训 + E-4）。
- **要点**：三批独立复犯同型错误——简报凭记忆/旧版混杂给的字段名（「noise_level min/max、half_cost」「count 1..25 非 IntProvider」「selector 分类词」）与 1.21.6 一手 codec 不符（MultifaceGrowthFeatureConfig.java:20-36 / CountConfig.java:9-25 实为 IntProvider 等）；若照写 parse，字段恒 miss → config 全默认值或特征静默全灭，且难察觉。**判据：「先读 codec 再写字段」与「先读文件再写 patch」同级**；引擎目标 1.20.1 有本地 extract 时必须 1.20.1/1.21.6 双版都读（防 1.21.6 独有改动静默混入）。
- **证据**：三份 worker-delivery E 段（含双版行号锚）。

---

### #101 残差归因「读量放大 vs 单读贵」判别式

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #101（A 类）

- **时间/置信度/module**：260909-04；candidate（E4b/E4c 单轮实锤，待复用再升；母课题 confirmed 260909-09）；workflow-patterns / 性能归因。
- **是什么**：残差归因于「缓存/查表类读路径」时，先用两个除法判别形态，再决定治读量还是治单价：① **总成本 ÷ 读数 ≈ 单读价**（本例 44ms ÷ 853k ≈ 51ns/读 = mutex+hash 量级，近下限 → 单读不贵）；② **读数跨臂比值定放大**（on 853k/chunk vs off 7.5k = **114×** → 成本主体是读量放大）；③ per-feature 读数归因（[CA-READS]：seagrass ≈53% + ore/disk/monster_room）确认放大是**语义正确的固有工作**（真实邻值使 feature 不再因 -1 早退），非病态冗余循环 → 结论「不建议治」，省掉一整条 memo 化改造（写失效 + 语义漂移风险）。
- **判据**：单读价已近原语下限 + 放大比由语义差解释 + 归因分布与 feature 工作量同构 → 该残差定性「固有成本」，优化立项前先过这道判别式。
- **证据**：perf-record-260909-04.md 判别链 E4b/E4c 行。

#### §15.4 取代记录：发现 #101 部分证伪——「单读 51ns 近下限」系摊销值非独立单价（260909-06）

- **supersedes**：发现 #101（残差归因「读量放大 vs 单读贵」判别式，260909-04）之判据第 ① 步「总成本 ÷ 读数 ≈ 单读价（51ns = 近下限 → 单读不贵）」；**superseded-by**：本条（260909-06 探针轮）。
- **推翻理由（一行）**：51ns 实为「残差 ÷ 读数」的**摊销推算值**（含 miss 重生成成本摊入 + mutex lock/hash/Arc 同步结构成本），不是独立实测的单读原语价——把它当「近下限」引用即循环论证（残差里混着 miss 重生成，除回读数又得出「单读便宜」）。
- **修正后事实**：memo-review-260909-05 Step 2 判定 1——98% 点级重复读每次都重付 mutex+hash+Arc 同步结构成本，「消每读同步开销」与「读量语义固有」是两层，#101 混层。
- **判据（取代 #101 判据①）**：**摊销单价（总成本÷读数）不得当独立实测单价引用，更不得用它证明「单价低」**——若读数本身被同一残差源放大（如 miss 重生成摊入），商值与「原语下限」的比较无效；独立单价须单独微测（#21 形态：复刻调用形态）或声明摊销口径。
- **范围声明**：#101 判据②（读数跨臂比值 114× 定放大）与③（per-feature 归因同构）未被推翻，继续有效；仅①的单价解释被取代。
- **来源定位**：.investigations/camin-perf/memo-review-260909-05.md §Step 2 + probe-260909-06.md（#101 正文位于本文件 #101 条，原文不改）。

---

### #105 载体偏差：载体全绿对生产故障零判别力

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #105（A 类）

- **时间/置信度/module**：260910-03；candidate（vivo 冻结课题方法论复盘，用户 confirmed 冻结解决）；workflow-patterns / 执行体三元组家族（#36 的数据域扩展，第五形态）。
- **来源定位**：`.investigations/vivo-freeze-260910-03/record.md` 方法论复盘节。
- **现象**：vivo 冻结排查中 dev 服（Chunky 4225 chunks + forceload 1600 覆盖级联区）全绿零异常，双臂 diff 0.015% 干净——但生产客户端稳定复现冻结。多轮载体验证（Chunky/forceload/dump）对根因零判别力，最后在**客户端 Temp blocks.json sha 一查即破**（缓存 = 1.20.1 内容）。
- **根因（机制）**：验证载体与生产载体的**数据通路不同**——dev 服 `-PcppWorldgenDir` 直读权威数据目录，生产客户端走 jar 解压 Temp 缓存。执行体三元组（#36：加载文件/构建产源/构建时间）只覆盖「代码执行体」，不覆盖「数据执行体」：dll 相同 ≠ 数据相同。通路分叉时，验证载体上的一切「全绿」只证明权威数据+代码干净，对生产载体上缓存层引入的故障零判别力。
- **判据（可复用）**：
  1. 生产专属故障（dev 复现不了）排查，第一动作 = 画出**生产载体的真实数据通路**（jar → 解压 → 缓存 → 加载），在通路的每一跳核对，而不是在验证载体上重复加绿。
  2. 数据三元组扩展 #36：① 实际加载的数据文件（从加载代码追路径，不从配置推断）② 数据内容指纹（加载文件 sha vs 权威源 sha）③ 版本归属（数据集是当前版本的）——三者齐才认「跑在正确数据上」。
  3. 签名：「同 dll/同代码 + dev 全绿 + 生产爆」且故障表现指向内容层（错块/错数据）→ 直接查生产缓存指纹，跳过 Chunky/forceload 类载体复现轮次（本案绕路多轮的代价即在此）。
- **家族索引**：#36（执行体三元组——本条为其数据域维度）、#98（修复依赖的数据通路必须生产口径在位）、build-tooling #27 补充案例（本条的错误实体侧）/ #96（加载路径跟实际 run 形态走）。

> **⛔ 数值取代指针（260911-05，§15.4 取代记录，原结论正文不删不改）**：本条 `:1712` 引用的「双臂 diff **0.015%** 干净」系**旧读法**（对拍工具 `payload()` 的 `tag 7` 长度按 **1 字节**读）产物——同载体、同 region 目录、唯一改动 = 该字段 `u1→i4` 的离线复算结果 = **0.0180%**（载体 `.tmp/hang-repro-260910/arms/region-{coreswap,vanilla}`；旧读数归档副本 `.investigations/perf-regression-260910-04/cmd-output/diff-result-historical-260910-03.txt` 与之同 sha256 `c9c0e9a0…`）。**引用该数值的「干净」措辞须按 0.0180% 重述**（「干净」的性质 = 同量级筛选，非零差）。本条**方法论判据（载体重心在数据通路 + 数据三元组）不受影响**——该数值在条内只作旁证。取代链：`.investigations/e5-recompute-260911-05/record-260911-05.md` §3/§4。

---

### #110 路径不可达类断言的证明三件套 + 复活出口穷尽

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #110（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260910-05（实际 2026-09-10 18:4x-19:2x）；主会话（静态链 + 行为化实测）+ judge（独立静态复核 + 复活出口穷尽 + 「其余共享态皆内容中性」增量）；**candidate**（judge PASS-with-conditions，C1-C9 已应用；confirmed 留用户）；workflow-patterns / 机制断言的可证伪化。
- **来源定位**：`.artifacts/perf-closeout-260910-05/verdict-c7-260910-05.md` §1/§1.2/§1.4；同目录 `judge-verdict-c7-260910-05.md` §一.1 + §三 C5/C8；`.investigations/perf-closeout-260910-05/record.md` §1.2/§2.2.1；同目录 `scout-vanilla-crosswrite.md` §3/§4。
- **背景（为什么需要这条判据）**：上游 judge 要求补「跨 chunk 写序会计」以排除 R3 异步化的写丢失竞争假说（judge-verdict-r3-260910-04.md:117-118）。核验发现该假说的**前提为假**：默认阶段掩码使 Rust `apply_features` 整体不执行 ⇒ `pending_cross_writes` 缓冲结构不可达。
- **机制（静态链四要素，每条带 file:line）**：
  1. **默认值来源**：`java-snapshot/pre/CppBridge.java:69-74 resolveStageMask()`（`prop==null || isEmpty` ⇒ `0b011`＝ SKIP_CARVER|SKIP_FEATURES，见 `:71`；`:82/:128/:148` 三处句柄均 `setFlags(handle, resolveStageMask())`）。
  2. **消费侧门控**：`worldgen-core/src/worldgen_handle.rs:669-671`（`let skip_features = flags & FLAG_SKIP_FEATURES != 0 || env WG_SKIP_FEATURES; if !skip_features { self.apply_features(...) }`；`FLAG_SKIP_FEATURES = 1<<1`，`:148-149`）。
  3. **唯一调用点**：全仓 grep `apply_features` = **定义 `:1036` + 调用 `:671`**（无第二入口）；`fill_chunk_blocks` 的生产调用者唯一 = `api.rs:156`（`wg_fill_blocks_multi`），其余调用者全在 `bin/`、`bin-diag/`（诊断程序，不参与 JNI 出货路径）。
  4. **该函数体内唯一生产/消费点**：`pending_cross_writes` 全仓仅四处 —— `:144` 声明 / `:506` 初始化 / `:1053` 消费 / `:1088` 生产（后两者同在 `apply_features` 体 `:1036-1375` 内）；闭包唯一注入点 `:1283`（`octx.pending_cross`，`ca_min` 门控）。
  5. **同族不可达**：`neighbor_terrain`（`:999-1022`）两个调用点 `:1124`/`:1242` 同在 `apply_features` 内 ⇒ **连邻域读快照预取也不执行**。
- **判据三件套（MUST，可复用——「不执行 / 空集」类断言的标准证明结构）**：
  1. **静态链**：默认值来源 → 门控布尔 → 唯一调用点 → 该函数体内唯一生产/消费点；**每一环都要能全仓 grep 到计数**（「唯一」必须显式排除诊断 bin / 测试程序）。
  2. **行为化负对照**：在**出货配置**下打开该路径的专属日志门（本案 `WG_CA_LOG=1`，mask=3）⇒ 该路径的日志行数 = **0**，且该臂**跑满**（本案 `Processed: 4225 chunks (100.00%) Total time: 0:00:39`）——「跑满却零行」才排除了「没跑到」。
  3. **正对照 + 通道证明**：改配置使路径可达（本案 `-Dcoreswap.rust.stages=5`）⇒ 行数 **>0**（本案 1711）——**同时**证明「改配置的通道真送达」：JVM banner `Picked up JAVA_TOOL_OPTIONS: … -Dcoreswap.rust.stages=5`（送达证据）+ 打印出 `stageMask=5` 的取值来自 `CppWorldgen.getFlags(handle)`（**JNI 回读**，即「sysprop → Java 解析 → setFlags → Rust 存值」全链到位）。双通道缺一不可（#37/#81 家族）。
- **复活出口穷尽（judge 增量，MUST 做——只说「这条路径不可达」不够）**：逐项核对**其它**顺序敏感共享可变状态是否也内容中性：① `beardifiers`（`:116` RwLock<HashMap<(chunk)>`>）只按 chunk 键读写（写 `:536`、读己键 `:710/:857`），其**全局清空**出口 `clear_beardifier()`（`:539-540`）的唯一 JNI 函数 `Java_wg_CppWorldgen_clearBeardifier`（`jni_bridge.rs:267`）在 `runtime/1.21.6/java` 全树 grep `clearBeardifier` = **0 命中**（`CppWorldgen.java:78` 只声明 `setBeardifier`）⇒ 全局清空不可达 ⇒ 非顺序敏感内容状态；② `terrain_cache`（`:631-635`）与 `est_l2`（`aquifer.rs:248-288`）为**纯 memo**（命中后 `clone()` 再跑 features，无别名写）；③ `api.rs` 导出面无任何跨写投递/查询通道。⇒ 出货语义下 Rust 侧退化为「**per-chunk 纯函数 + 纯 memo**」，完成序自由度对内容无影响——**这比「该路径不可达」强**（后者只否一条通道）。
- **「不可达」必须写精确（MUST）**：出货语义（mask=3）下不可达 ⇒ **不可在出货配置内测量**（任何会计计数恒 0）；`mask=1/5` 下**可达且可测**（本块正对照臂即证）但**不是出货语义**（`mask=1` = 接管臂、`mask=5` = 本块正对照组合，非接管配置）。⇒ 「不实现会计计数」的理由 = 「前提已证空集 + 实现后只能在不属于出货语义的配置下被验证」，不是「跳过不做」。
- **前置条件登记（未来重启该路径前 MUST 先做，本节即登记载体）**：① 会计不得复用现成全局计数——`CA_PENDING_WRITES`（`:1081` 声明、`:1084` 每 chunk `store(0)`、`:1087` 累加）是**全局 atomic**，23 线程并发下「本 chunk 读数」被跨线程写污染 ⇒ 只能作**量级/上界**（一手日志实测 n=1711、区间 **0-37,893**、中位 1,575；不得读作 per-chunk 精确值）；② 会计口径须新增「**迟到写**（目标已跑 features）/ **已生效** / **终态常驻**」三数，且**按 chunk 或按线程分桶**（thread-local / chunk 作用域）；③ 完整语义分歧面清单 = `scout-vanilla-crosswrite.md` §4 的 A1-A7 + C1/C2（含**越界高度图哨兵 `min_y-1`**——Ore 的 s/t 扫描必然跨界 ⇒ 可达；以及**混合语义**：Java 让位只 redirect `PlacedFeature.generate`，结构件放置段仍在 Java ⇒ 重启后是「Rust features + Java structures」）。
- **家族索引**：#20/#53（默认值当公理——本条是其**证明侧**：默认值决定路径可达性）、#37/#81（生效证据必须行为化——本条给出「**不**生效」的行为化对偶）、#66（同 dll 两种执行语义 / mask 三态）、#42（静态机制断言未实测当公理——本条给出「静态链 + 行为化互证」的模板）、#105/#36（执行体与覆盖面口径）。

---

### #113 跨实现搬运锁语义必须成对核对（只搬一半即自锁死）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #113（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260910-06（实际 2026-09-10 20:16–22:2x，Get-Date 锚定）；主会话（实测 + 自建线程栈看门狗 dump 一手定位）；**candidate**（数据层决定性证据 = 线程栈 dump 内含同一把锁的「持锁帧 + acquire 帧」；同步/异步两臂对照排除竞争变量；修复后两臂跑通且有量级与内容门）——confirmed 留用户；workflow-patterns / 跨实现搬运纪律（build-tooling #8/#47「接线/映射错觉」家族的**锁语义维**）。
- **来源定位**：`runtime/1.20.1/java/.../mixin/NoiseChunkGeneratorMixin.java`（首版含 `wgLockSections`/`wgUnlock` + `whenCompleteAsync` 完成跳回；post 快照已为无外层锁形态）；`.../wg/bench/CppBridge.java`（`writeChunk` → `sec.setBlockState(x, sy, z, st)` 4 参重载）；错误台账 `.investigations/perf-reg-260910-06/errors-260910-06.md` **E1**（含 dump 栈原文与 vanilla 对照 `NoiseChunkGenerator.java:337-346`）；架构计划 `.investigations/000-架构设计/架构计划-260910-06.md` §14.1；判决 `.artifacts/perf-reg-260910-06/verdict-260910-06.md` §2/§4.1/§7.5。
- **现象（错误链）**：Chunky 任务启动后**零进展**，且**同步臂与异步臂都卡**——`[Chunky] Task running for minecraft:overworld. Processed: 0 chunks (0.00%), ETA: 0:00:00, Rate: 0.0 cps, Current: 0, 0`（一手 `cmd-output/results.txt` 的 2 条 STALL 行）；`run\world\region` mca mtime 停在任务起始时刻；**等 40min 不复原**（不是慢，是停）。CPU 两源读数（同量级、窗口不同）：活采样 `0.1s/12s ≈ 0.01 核`（errors E1）与累计 `11-13s / wallgen 204s ≈ 0.05-0.06 核`（`results.txt`）。
- **根因（机制）**：把 vanilla 1.20.1 `NoiseChunkGenerator.populateNoise`(:337-346) 的**外层 sections 锁**照搬进自家接管段，但自家写回路径**自带逐次锁**：`CppBridge.writeChunk:519 sec.setBlockState(x,sy,z,st)` → **4 参重载（`lock=true`）** → `ChunkSection.setBlockState(x,y,z,state,true)` → **`PalettedContainer.swap(x,y,z,value)`（`this.lock(); try{…} finally{ this.unlock(); }`，`:142`）** → `LockHelper.lock()`（`:42`，**非可重入 Semaphore**，`acquire` 阻塞）⇒ 同线程**已持有**该 section 锁时，写回内部再次 `lock()` = **永久 park**（无异常、无日志）。vanilla 能加外层锁，是因为它自己的 fill 持锁后改用 `setBlockState(..., lock=false)`（`swapUnsafe`，**不加内层锁**）——**「外层段锁 + `lock=false` 写」是成对契约**。
- **证据（怎么定位的，可复用）**：
  1. **双臂对照排除竞争变量**：同步臂**也**卡 ⇒「异步分派 / `whenCompleteAsync` 完成跳回」被排除，嫌疑立即收敛到**两臂共有**的新增项（= 外层锁）。此步无需 dump 即成立，是最便宜的第一刀。
  2. **dump 直读阻塞链（决定性）**：沙箱 `jstack`/`jcmd` 全拒访（attach 被拦）⇒ 自建门控看门狗自打线程栈（#114），一次 dump 读出 `Worker-Main-*` `state=WAITING` 且**同一把锁出现两次**：`LockHelper.lock(:42)` ← `PalettedContainer.lock(:45)` ← `PalettedContainer.swap(:142)` ← `ChunkSection.setBlockState(:63)` ← `CppBridge.writeChunk(:519)` ← `fillChunk(:394)` ← …`wgPopulateNoise`。
  3. ⚠️ **证据保全教训**：该 dump 的原始日志在**后续成功复跑时被覆盖**（同文件名），归档仅存 `results.txt` 的 STALL 行 + `CppBridge.java`/`ChunkSection.java`/`PalettedContainer.java`/`LockHelper.java` 的源码级锁链（judge 独立复核过该链）。⇒ **卡死轮日志 MUST 在复跑前另存**（临时产物唯一区纪律的补充：证据优先级高于工作区整洁）。
- **判据（MUST，可复用）**：
  1. **照抄参考实现的「锁语义」前，MUST 先核自家写路径的锁语义与可重入性**——查「我这条路最终调到的写接口带不带锁」；自带锁则**不要**在外层再加，或整段改用 `lock=false` 系列接口（二选一，不可混）。
  2. **判别签名（三件齐）= 两条臂都卡 + CPU ≈ 0（进程原地耗电）+ dump 里同一把锁出现「持锁帧 + acquire 帧」**。这是**单线程非可重入自锁死**，不是 ABBA 互等死锁，更不是性能问题——不要派性能诊断轮次。
  3. **「卡死 ≠ 慢」：先量 CPU 增量 + 进展探针，再谈性能**；驱动 MUST 带**早停探针**（本案 `Processed` 恒 0 超 180s 即落盘诊断并退出，替代 40min 盲等）。
  4. **同族附注（API 形态维）**：搬运同一机制时**同名 API 的形态也可能不同**——1.20.1 `Util.getMainWorkerExecutor()` 返回 `ExecutorService`（`Util.java:229`），1.21.6 才是 `NameableExecutor`/`.named(...)`（照抄 `.named()` 在 1.20.1 编译不过）。⇒ 跨实现搬运核对表 = **锁语义 / 签名 / 参数映射 / API 形态** 四栏，缺任一栏都可能静默或响亮失败。
- **家族索引**：build-tooling #8/#47（映射/接线错觉）、workflow-patterns #107/#108（形态错即性能错——本条为「形态错即卡死」的更强形态）、#100/#102（归因须在真实通路上核对——本条是「卡点根本不是性能」的对照面）、#114（本条定位所依赖的诊断件）；compiler-idioms #24（本条所用锁语义事实的惯用法简条）。

---

### #117 迁移引用面「活配置 vs 历史归档」两分

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #117（A 类）

- **发现时间 / 置信度 / module**：260910-07；candidate（本块四类活引用逐项落地 + 历史归档逐项不改；**E2 实测**暴露「有界静态扫描」漏面）；workflow-patterns / 迁移纪律（**#77「回滚 ≠ 引用面清理」的分界形态**）。
- **来源定位**：架构计划 `架构计划-260910-07.md` §1 D5 + §3「引用更新」行；错误台账 **E2**；落地实例 = `AGENTS.md` §四路径声明、`versions/1.20.1/java/run_rust_client.ps1` 的 `$runJava`、`.tmp/perf-reg-260910-07/run_arms_1201.ps1`（拆 `$run`/`$rd`）、`.gitignore:97-104`。
- **两分清单（本案实际处置）**：
  - **活引用（MUST 改）**：`.gitignore` 规则、`AGENTS.md` 的「现役 Java 权威路径」、工程内脚本（`run_rust_client.ps1` 的 `$runJava`）、**`.tmp/` 一次性驱动脚本的路径推导**、发布契约 / 工单**模板**（新工单须用新路径）；
  - **历史证据（按历史读、MUST NOT 改写）**：`.investigations/**` 归档日志、已发工单（如 `.artifacts/releases/RELEASE-1.0.26/27.md`）、`versions/*/docs` 时间线——**改写 = 篡改证据链**；路径变更点只在**新块文档**里注明（本案判决/计划/本稿即承载）。
- **关键实战判据（本条的核心增量）**：**活引用面不能靠静态 grep 保证完整**。本块事前做了有界扫描（**排除 `.tmp/`、`build`、`.gradle`**）并覆盖了 `.gitignore`/`AGENTS.md`/工程内脚本，**仍漏掉 `.tmp/` 驱动**——它的路径推导**写在变量拼接里**（`$run = "…\runtime\1.20.1\java"` + 处处 `"$run\run\…"`），关键词 grep 也易漏；失败形态是运行时 `FAIL no Done` / `找不到 …\versions\1.20.1\java\run\server.properties`。⇒ **迁移后 MUST 跑一次真实入口（build + run）**，它是最快的兜底（本案一轮即暴露）。
- **修法示例（本案）**：驱动拆**两个路径变量**——`$run`（**工程目录**，交给 gradle 的 workdir）/ `$rd`（**运行环境目录**，给 world / `server.properties` / chunky tasks / region 采集）；「工程目录 + `\run`」的**拼接式推导**在「工程与环境分家」后必然失效（这正是 260910-06 驱动的写法）。
- **家族索引**：#77（回滚 ≠ 引用面清理——引用面扫描）、#90（转抄漂移——历史文档「按历史读」的意义）、AGENTS.md §八.10（目录迁移后全局更新相对引用）、build-tooling #54（同一块迁移的资产侧形态）。

#### #28 补充案例（260910-07，任务书第 6 条·可选，**建议不占新号**）: 迁移/重构后的单点性能离群——先核等价性证据，等价则归因直接闭到环境

> **载体建议**：任务书给的是「compiler-idioms **或** build-tooling 简记」；本稿建议改为**workflow-patterns #28 就近挂靠**，理由：① 内容属**归因纪律**（不是语言/工具惯用法，也不是构建链机制），② #28 已立「并发 bench 污染 / **单点离群先复跑再归因**」，本条是它的**前置一步**，拆到别的文件会割裂判据。若主会话坚持按任务书载体落，同一段正文改挂 **build-tooling 简记（续 #57）**即可，文字可原封搬（见 §E.1-6）。

- **现象（260910-07）**：迁移后**首臂** `oa-r1` 跑出 **66 s**（wallgen 72.2 s、6.58 核、`inflightMax=23`），而 260910-06 同形态家族值为 37-38 s；**复跑同臂** `oa-r2` = **38 s**（wallgen 41.3 s、11.53 核），回到家族值（一手 `.tmp/perf-reg-260910-07/results.txt`）。
- **判据（可复用）**：#28 已立「单点离群**先复跑**再归因」；本条补**前置一步**——**先核等价性证据**：本块 V1 已证迁移前后 jar **逐字节相同**（同 dll、同 seed、同区域）⇒ **「搬位置」不可能改变生成耗时**，离群可直接归因**环境**（当时的并发文件操作 —— 同批在做等价性解包/搬运 —— 或冷 gradle daemon / JIT 预热），复跑只作**确认**而非**定性前提**。反之，**若无等价性硬证据**，离群必须停手先查「重构是否真无影响」，不得先归因环境（那是「结论先行」）。
- **边界**：66/38 s 是**路径回归读数，不是性能实验**——与 260910-06 的性能数字**不可混读**（§9.7；判决 §4.3 已声明）。
- **家族索引**：#28（并发 bench 污染 + 单点离群先复跑）、#51（噪声基线与信号同阶）、#116（本条的等价性证据来源）。

---

---

### #120 对外能力声明必须与出货默认门控同源核对

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #120（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260910-08（事实）；主会话（README 双语一手核对）；**candidate**；workflow-patterns / 文档与门控一致性（#66/#110 家族的**公众文档维**）。
- **来源定位**：`.investigations/perf-release-260910-08/errors-260910-08.md` E6；漂移点 = `README.md:27` / `README.zh-CN.md:28` vs 出厂 `mask=3`（`CppBridge.resolveStageMask()`）+ `worldgen_handle.rs:669-670`/`:832`。
- **观察（错误链要点）**：README 声称主世界「density → aquifer → ore veins → surface rules → carvers → features」全原生；实际出厂默认 `mask=3` 切断 `apply_features` 与 carvers ⇒ **carvers/features 实际由 Java vanilla 执行**。该声明在 260909-03 用户决策（矿物/树/装饰层不接管、保 MOD 兼容）后即过时——门控默认值改了，公众文档没跟着核。修复 = README 双语改措辞（"carvers and features stay vanilla Java for mod compatibility"）+ "How It Works" 段补出厂生效范围。
- **判据（MUST，可复用）**：
  1. 能力声明（README / Release notes / 公告）按「**出货默认门控下实际生效的路径**」写，不按「引擎里有实现」写——mask/ca_min/env 默认值是声明的一部分；
  2. **改门控默认值的 commit MUST 触发一次公众文档核对**（同源 grep：被改门控对应的声称语句），否则文档漂移是静默的；
  3. 与发版联动：Release notes 草稿（RELEASE-CONTRACT §3）引用的性能/能力数字，出单前按 E5/#66 判据同源复核一遍（本块 1.0.28 changelog 即按此口径写：收益归 async 形态、ca_min 微修明写「无性能承诺」）。
- **家族索引**：#66（bench/文档双面的口径同源）、#110（可达性——「有实现」不等于「可达」）、#120 与 RELEASE-CONTRACT §3 联动。

---

### 发现 #102 补充案例（260911-01，#100 缓存家族第四面）: 「只写不读」缓存路径的**写入侧门控**——消费点集合为空 ⇒ 写路径整体短路（连写都不该做）

- **发现时间 / 发现者 / 置信度 / module**：260911-01；主会话（260910-08 可达性核对定位 + 本块 patch/A/B 落地）；**candidate**（A/B 无回归 + 静态构造性论证；judge 意见已入 RELEASE-1.0.28 工单；confirmed 留用户）；workflow-patterns / 缓存三面核对（#100「谁写+谁读」、#102「+clear 波及面」之外的**第四面：写入门控**）。
- **来源定位**：`.investigations/perf-release-260911-01/patch-ca-min-gate-260911-01.md`（patch 三处：flags 提前 load + `skip_features` 同源提取、门控 `ca_min` → `ca_min && !skip_features`、删两处重复声明）；`.investigations/perf-release-260911-01/record-ab-260911-01.md`（4 臂交错 A/B + 判读）；上游 `.investigations/perf-release-260910-08/MANIFEST.md` §4.5。
- **观察**：terrain_cache 的消费点全部在 `apply_features` 邻 chunk 读；出厂 `mask=3` 下 features 关 ⇒ 缓存**只写不读**，每 chunk 纯付 ~393KB `BlockColumn` clone + HashMap insert（cpuSec +1.7%，噪声带内不可判定但机制方向明确）。修复 = 判据化门控：**盘点缓存消费点集合 ⇒ 为空 ⇒ 写路径整体短路**（直算 `fill_terrain_column`，同一函数产物，输出逐位相同——构造性等价）；features 启用路径逐字未动。
- **A/B 判读（口径：同构建态单变量，n=2/臂交错）**：吞吐 post 36.5 s vs pre 35.5 s（~3%，#103 ±10% 带内，不可判差异——本修是「去纯成本」非可测提速，预期内）；maxWs 跨臂摆动（pre 自身 4257 vs 6428 = 1.5×）覆盖组间差，不作结论（#119）；cpuSec 均值 463 vs 464 零差；行为不变性 = 静态构造性论证 + `[WG-CONF]` 两臂逐字段一致（#81），region 逐块对拍未做（Degraded 声明）。
- **判据（可复用）**：
  1. 缓存类路径的三面核对（#100/#102：谁写 / 谁读 / clear 波及面）之后**加第四问：「消费点集合在出货门控下是否为空」**——为空 ⇒ 写侧整体门控短路（`gate = 原开关 && 消费路径可达`），不是只省读；
  2. 门控判定必须与阶段门控**同源提取**（本案 `skip_features` 判法从 `:669` 逐字提取到缓存判定处，消除「缓存按旧 flags 走、features 按新 flags 判」的双判源潜在不一致）；
  3. 等价论证可走构造性路线：skip 模式下 pre-fix 恒走 miss 分支（单次预生成 (cx,cz) 不重复 ⇒ hit 永不触发）= 直算，post-fix 直算同一函数 ⇒ 逐位相同（构造性）；缓存条目本就是同一函数产物（260909-04 E1b 已验证）；
  4. 「无回归门」即可发版的口径见 #121。
- **家族索引**：#100（缓存失效当结论——第一二面）、#102（三面核对——本条加第四面）、#110（可达性核对提供「消费点集合」）、#81（`[WG-CONF]` 行为自证）、#103/#119（吞吐/内存噪声带读法）。

---

### #125 背压两形态同构不同质（acquire vs CallerRuns）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #125（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-03；judge C2（260911-03 subagent judge 抓出措辞混淆）+ 主会话修正；**candidate**；workflow-patterns / 并发背压设计（judge 制度化收益实例）。
- **来源定位**：`.investigations/vivo-stutter-260911-02/exec-mode-result-260911-03.md` 头注（「C2 措辞修正已改代码，行为零变化」）；P1 实现（`maxinflight` 信号量）与 exec 实现（`queue+CallerRunsPolicy`）代码对照。
- **观察**：P1（信号量 `acquireUninterruptibly`）与 exec（有界队列 + `CallerRunsPolicy`）都会「停车道」，表面上都是背压，但延迟性质根本不同：信号量让**调用方线程 park 等待**（不干活，纯等待）；CallerRuns 让**调用方线程亲自执行被拒任务**（干重活）。把两者混称「背压/限流」会掩盖实机延迟表现差异（前者 = 卡顿式停顿，后者 = 主线程被重活拖慢但无 park）。
- **证据**：exec 记录中 `[WG-EXEC] rejectedPolicy=CallerRuns` 与 P1 `[WG-INFLIGHT]` 信号量路径的行为化日志分属两臂；judge C2 指出初稿 javadoc/结论措辞将二者混同，已改代码注释（行为零变化）。
- **如何利用（可复用判据）**：① 声明背压行为 MUST 写明形态：**等待型**（semaphore/future.get，车道 park）vs **代做型**（CallerRuns，车道执行任务），两者对调用方延迟分布的影响不可互换表述；② 选型时按调用方语义定：车道绝不能被拖住做重活 → 等待型或丢弃型；可接受车道偶做重活 → CallerRuns（无 park、无泄漏风险）；③ 混同表述属「同构不同质」家族——行为面相近不等于延迟语义可互换。

### 发现 #81 补充案例（260911-03）：exec 缺省开的「零 env sanity boot 行为化自证」

- **发现时间 / 来源定位 / 置信度**：260911-03；`.investigations/vivo-stutter-260911-02/exec-mode-result-260911-03.md`（缺省开 sanity：零 env boot 命中 `[WG-EXEC] mode=own-pool pool=10` 且无 `[WG-INFLIGHT]` 行 = exec 分支短路信号量路径）；**candidate**。
- **补充点**：#81 判据（行为化分支日志 + hash 双向变化）的「缺省开」特例——验证默认路径生效时，除正日志命中外，还要核**被短路分支的日志缺席**（`[WG-INFLIGHT]` 缺席证明确实走了 exec 而非 P1+exec 双开），双向证据在「缺省开」下同样适用。

---

### #126 工单时间链禁写 mtime 严格序

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #126（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-04；judge subagent N-3（RELEASE-1.0.29 出单审查抓出）+ 主会话应用；**candidate**；workflow-patterns / 发布工单纪律（**#121 判据 3 的措辞级修正形态**；#23 家族第三形态——前两形态是「新鲜度检测域」，本条是「溯源叙述域」）。
- **来源定位**：`.artifacts/releases/judge-verdict-260911-04.md` N-3；`.investigations/vivo-stutter-260911-02/fps-verdict-260911-04.md` §产物（时间先后关系原始写法）。
- **观察**：RELEASE-1.0.29 工单按 #121 判据 3 写时间链「重编 18:55 > 删除 commit（perfprofile 移除 + bump）」，judge 核实 jar mtime = 18:55:17、commit 时间戳 = 18:55:41——**严格序倒挂 24 秒**，断言不成立。
- **根因（机制）**：git commit 是对**已构建产物所在工作树**的落盘动作，正常「构建 → 提交」工作流下 commit 时刻**天然晚于**产物 mtime；同分钟内「构建 → 提交」时，任何「构建时刻 > commit 时刻」的 mtime 严格序断言都结构性不成立——这不是时间链异常（构建物确实来自该 commit 的源状态），是**断言选错了序变量**（拿两个不同域的时间戳比严格序）。
- **判据（可复用）**：
  1. 工单/工单类契约里的时间链**禁止写成 mtime/commit 时间戳的严格序不等式**；措辞用「同分钟、commit 落盘于构建后」这类顺序语义描述，只在跨分钟以上粒度才可写严格序；
  2. 「此构建来自此源状态」的唯一裁决 = **内容指纹**（sha 三元组：jar / jar 内 dll / target dll，重算于重编后，不转录）——mtime 双向都只作旁证（#23 补充案例判据在溯源域同样适用）；
  3. 时间链的证明责任分配：跨块/跨执行体隔离（A/B 窗口 vs 出货构建是否同源）靠指纹；分钟级内先后关系不承载证明责任，不为其写可被挑刺的断言。
- **家族索引**：#121（发布域时间链书面化——本条修正其示例措辞的适用边界）、#23 + #23 补充案例 260905-13（新鲜度域 mtime 不可信——同判据不同域）、#6（mtime 保留）、build-tooling #30（指纹哨兵）。

---

### #132 跨臂门的分母必须声明语义

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #132（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-05；主会话（A2 分母语义声明）+ judge subagent（C3 判 MUST、C12 推翻「85 缺口」解释）；**candidate**；workflow-patterns / 门的分母与期望集口径（**#127/#128 口径家族的「期望集」面**）。
- **来源定位**：`a2-dim-gate-260911-05.md` §2（`:25-27`，分母语义 + 621 差额）/ §5（`:49`）、`record-260911-05.md` §5（`:85`）；judge `review-260911-05.md` C3（`:22`）、C12（`:31`）；原始读数 `results.txt`（全臂 `chunks=4225`、`content=4761/4140`，材料转引）。
- **观察（现象）**：同 seed / 同 center（-48,-11）/ 同 radius 500 / 同工具修订下，**门载体条数** = overworld 4140、nether·end 4761，而 Chunky 报 `Processed = 4225`（全臂相同）。材料早前把差额记成「**Chunky 已处理但无接管行**（差 85）」；judge C12 判**不成立**——期望集不是 Processed 集，且 overworld 相对 nether/end 少的是 **621** 条（多效应**净值**），成因**未查** ⇒ 降为 open。
- **根因（机制）**：把**外部工具报告的处理数**默认成「本门应有的载体条数」，等于假设「工具处理过 ⇒ 本门必有载体行」——而门的载体只覆盖**经接管的 chunk**，与工具的处理集是**两个不同机制的集合**。差额一旦出现，最容易的动作是**为差额编造机制**（「已处理但无接管行」），而不是先核「期望集是不是同一个集合」。
- **判据（可复用）**：
  1. 门类结论 MUST 声明**分母语义**（本案 = **经接管调用数** ≠ Chunky Processed）；表述用「经接管的 4140 条**全部**进指纹门」，不写「4140 / 4225 = 98.0%」这类跨集合比值。
  2. 门判据 MUST 写成**不依赖任何分母**的形式（本案 = 「经接管的全部 chunk 跨臂逐 chunk 同哈希」）；分母只用于表述覆盖面，不参与判据。
  3. 出现未解释差额时，**第一步核期望集是否同一集合**，然后才允许提机制候选；**禁止**用外部工具计数反推机制。
  4. 差额成因未查时按 **open 假设**登记（写明是多效应净值），**不得**写成机制结论；被推翻的解释保留一行 ❌。
- **家族索引**：#127/#128（口径换代后旧基线复算 / 新旧映射非单调——本条为「**期望集口径**」同族）、#111（噪声锚分形态分维度）、#18（跨 session 基准数字不可续推）、#16（对照基线归因法——先分离因素）、#36 家族补充案例（交接结论廉价验证）、build-tooling #53（结构值断言）。

> **#132 补充案例（260913-01，同判据第二实例——「分母语义」的复用实证）**：本块 `chunky center -48 -11` + `radius 160` 时，Chunky 自报 **`Processed: 441 chunks (100.00%)`**（三维一致），而门事件 / 指纹行数 = **625**。**441 与 625 是两个不同机制的集合，不可互相代入**：**441 = Chunky 任务计数**（`radius 160` 覆盖的 chunk 数）；**625 = 经接管的 chunk 数**（含 **spawn 预生成**的邻近 chunk——日志确有 `Preparing start region` / `Preparing spawn area` 早于 `chunky start`）。
> - ⚠️ **表述陷阱（judge SHOULD-2）**：写作「`radius 160` ⇒ 441 chunk / 625 内容行」时，**「⇒」暗示等值**，读者可能误算「625 ≠ 441 = 判据矛盾」。**正确写法 = 两个数各带语义标签、并列不连线**：「Chunky 任务 **441 chunk**（`Processed: 441 chunks` 三维实测）；门事件 / 指纹 **625 行**（含 spawn 预生成 chunk，25×25 网格 `x=[-15,9]` `z=[-13,11]`，实测无缺格）」。
> - **判据复用**（承 #132 本文）：① 门类结论 MUST 声明**分母语义**（本条 = 经接管 chunk 数 ≠ Chunky Processed）；② 判据 MUST 写成**不依赖任何分母**的形式（本条 = 「经接管的全部 625 chunk 跨臂逐 chunk 同 sha」）；③ 出现未解释差额时**第一步核期望集是否同一集合**，然后才允许提机制候选——**禁止**用外部工具计数反推机制。
> - **家族**：#132（本条为第二实例；首例 = 260911-05 的 4140/4761 vs 4225）、#80（spawn 预生成时序——**差额的来源机制**）、#142（本块的覆盖面限定词与该分母语义同源）。

---

### #133 排除法结论的边界（未测候选必须并列）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #133（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-05；主会话（A2 结论初稿）+ judge subagent（C8 判「下游归因」为未测外推）；**candidate**；workflow-patterns / 归因纪律（**#105/#36 的「正向归因缺证据」面**）。
- **来源定位**：`a2-dim-gate-260911-05.md` §4.2（`:44`）与自承不覆盖写回（`:51`）；judge `review-260911-05.md` C8（`:27`）+ §3 A2③（`:46`）。
- **观察（现象）**：A2 前半结论「**nether 的 run 级非确定不来自 Rust 填充层**」在本载体范围内**成立**（指纹跨 run 零差）；初稿续写「⇒ 非确定**在下游 Java carver/feature/装饰层**」。judge C8 判后半为**未测外推**：本载体只覆盖只读 `buf`，**未覆盖写回路径**，也未与 #21 的 region 级口径做 §9.7 可比性声明。处置 = 前半保留，后半降为假设并列出**三个并列未测候选**（Java carver/feature/装饰层、写回路径、存档序列化）。
- **根因（机制）**：排除是**单层否证**（该层在覆盖范围内无差异），而「成因在某处」是**正向归因**，需要该层的**独立证据**。把「不是 A」读成「是 B」= 把否定证据当肯定证据；更严重的是 B 往往**根本不在验证过的候选集里**（写回路径、序列化都没测）。
- **判据（可复用）**：
  1. 排除层结论只能写成「**不在本载体覆盖的层** X」，并**明确覆盖边界**（指纹取点位置、是否覆盖写回路径、是否覆盖下游消费）。
  2. 其他层只登记为**未测候选**，**并列不择一**；「未测候选」的字段 MUST 写出来，否则读者会把排序第一的候选当结论。
  3. 与既有口径（如 region 层读数）对比前先做 §9.7 三要素可比性声明——口径不同 ⇒ 该对比本身无效（#127/#128）。
- **家族索引**：#105（载体偏差）、#36（验证探针与生产执行体不同源）、#42（静态机制断言未实测当公理）、#14 补充案例（门层与被测变更同层）、#127（口径不可比）。

---

### #134 结论里的读数必须声明来源性质

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #134（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-05；主会话（A1a 计时 + A1d 声明）+ judge subagent（C6 判「须声明收益下界」；A1d 诚实性判定「充分」）；**candidate**；workflow-patterns / 测量与读数来源（**#28 测量污染家族的「校验计数器」面**）。
- **来源定位**：`record-260911-05.md` §2（`:22`）、§3 A1a（`:41`）、§3 A1d（`:61`）；judge `review-260911-05.md` C6（`:25`）+ §3 A1d 行（`:43`）。
- **观察（现象）**：① A1a 双臂**均开 `WBCHECK`**（每个空气格一次 `getBlockState`，共 **2.76 亿次**）⇒ `cpuSec 493 → 476` 应读作**含诊断成本的收益下界**；要引用定量数字须关 WBCHECK 重跑。② A1d 的「改前 `nthreads=10`」：judge 全 `.tmp` grep `[WG-THREADS]` 仅两条（**均为改后** dll 的日志）⇒ 旧二进制**无自证行**，改前值**不可实测**，只能按公式推导（`threads_param=-1` → 物理核 12 − 2 = 10）——材料已如实声明为推导。
- **根因（机制）**：① 为证等价性而加的**全格校验计数器**与计时**同 run** ⇒ 计时里含校验成本，量级与格数成正比；② **自证行是改动后才加进代码的** ⇒ 「改前基线」在物理上不可复测，事后只能推导（时间上不可逆）。
- **判据（简记）**：① 凡 A/B 同 run 计时而该 run 另开了**代价量级可观**的校验/诊断（尤其**每格一次**的开销），MUST 把收益读数标为**下界**，并在引用定量数字前**关校验重跑**；② 清理项/改造项凡需「改前值」，MUST 在**改动前**预留自证行或 A/B 开关——事后只能写「**推导值（非实测）**」；③ 共同判据 = **读数的来源性质（实测 / 推导 / 含污染）必须写进结论**。
- **家族索引**：#28（并发 bench 互相污染）、#51/#103（噪声带与只作趋势）、#121（发版门用同构建态 A/B）、#129（判据终态与测量能力）。

---

### #136 热路径门控化必须盘点被移除的信号

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #136（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-05；主会话（A1b 落地）+ judge subagent（C2 指出理由句与改前实现矛盾、生产安全信号丢失未声明）；**candidate**；workflow-patterns / 诊断门控纪律（**#115/#14 补充案例 的「观测载体」面**）。
- **来源定位**：`record-260911-05.md` §3 A1b（`:44-49`）；judge `review-260911-05.md` C2（`:21`）、C10（`:29`）+ §3 A1b 行（`:41`）；实现侧 `CppBridge.java`（材料转引 `:408-410` / `:455-473` / `:366`）。
- **观察（现象）**：原实现里 `[WG-CONTENT]` **已**门控，但 **`buf-all-air` / `buf-sparse` 是无条件 println**，且 nz 全 buffer 扫描（**98,304 读/chunk**）+ nether/end 16 点读回**恒执行**；材料早前的理由句「扫描结果只被门控内打印消费」与**改前代码矛盾**（judge 用 `git show b2b2f26` 复核被删代码发现被删的是无条件 println）。改法：nzBuf 扫描与 16 点读回**整块门控到 `MIXLOG`**，同时保留「Rust 输出全 0」的 **O(1) 短路探测**（`if (buf[0] == 0)` 才扫、遇首个非零即停）；`buf-sparse`（nz<1000）分级诊断随之移除 ⇒ 需声明取舍（需要时用 `-Pmixlog=1` 的 `nz` 字段）。
- **根因（机制）**：「诊断输出」与「生产异常判据」**共用同一条打印/扫描路径**，门控是按**用途标签**（诊断）切的；而其中一部分**无条件**输出实际承载生产侧 sanity（「Rust 输出全 0」= 接管失败/引擎未跑的信号）⇒ 按标签整块门控会**连判据一起关掉**，且关掉是静默的（无告警）。
- **判据（简记）**：① 热路径诊断整块门控前 MUST 盘点「被移除的每一行 / 每一段扫描各自承载什么」，凡承载**生产异常判据**的 MUST 用 O(1)/摊销常数探测保留；② 分级诊断随全量扫描一并移除时 MUST **声明取舍 + 替代读取方式**；③ 改动的**理由句 / javadoc MUST 与被删代码逐行核对**（judge 侧用 `git show <commit>` 复核被删实现）——理由句与实现不符属记录缺陷（C2/C10：`CppBridge.java:366` javadoc 与 `:455-473` 实际门控矛盾）。
- **家族索引**：#115（内容指纹门的取点边界）、#14 补充案例（层名/取点必须入结论）、#118（自证行必须做成硬门禁——同属「观测能力静默消失」）、build-tooling #50（写回根索引时「解析 + 重建」静默丢弃既有内容——同为「写入型工具的静默销毁」）。

---

### #137 结论引用的外部锚必须用属主工具自核

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #137（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260911-05；judge subagent（C9：`git cat-file -t 3c1f9c6` → `fatal: Not a valid object name`）+ 主会话改正；**candidate**；workflow-patterns / 书面化锚点可核性（**#31 证据落盘家族的「引用面」**）。
- **来源定位**：`a2-dim-gate-260911-05.md` §1（`:12`，改正后引 `8d8075a`）；judge `review-260911-05.md` C9（`:28`）；`.artifacts/index.yaml`（A 线四条目 + 分层注释，旧稿实读）。
- **观察（现象）**：A2 记录引「提交 `3c1f9c6`」，judge 执行 `git cat-file -t 3c1f9c6` 得 `fatal: Not a valid object name`；实际修复提交 = **`8d8075a`**（材料已改正）。
- **根因（机制）**：提交号 / 路径这类锚是**从工作过程记忆转录**写出，没有任何机制保证其存在；锚一旦错，下游**无法按锚复核**——「证据不可达」被伪装成「证据已给」（比缺证据更隐蔽）。
- **判据（简记）**：① 结论/记录里的每个外部锚 MUST 用**属主工具**自核一遍（git 对象 → `git cat-file -t` / `git show --stat`；文件 → 实读；日志行 → grep 原文）；② 自核列入收尾检查（成本 = 一条只读命令）；③ 与「数字来自实测、无编造」同族——本条管**引用可核性**。
- **家族索引**：#31（核验证据落盘原始记录）、#12（静态对拍须对拍解析产物）、#110 补充案例其二（共享假设边界）、#25 补充案例（计划期技术断言的静态失真——本条为「引用锚」形态）。

---

### #140 「结论对而解释错」（叙述层事实未核实）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #140（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260913-01；**judge subagent 独立抓出**（judge-260913-01 MUST-1：`Test-Path` + `git ls-files` 两条独立证据复核**叙述层**，而非复核结论本身）+ 主会话全量更正（三处 + 新立 W5 取代链）；**candidate**（源记录 = **confirmed**，用户授予 2026-09-13；本条判据为**新登记**，随源块 confirmed，但本条目自身的二轮实践未做）；workflow-patterns / 判据可核性与解释纪律（**#95「事实前提与结论分开验证」的同族，且更严**——#95 是「前提错结论可对」，本条是「**结论对、前提错也要修**」；#112 预登记读法纪律的「叙述层」形态）。
- **来源定位**：错误台账 `.investigations/d4i-260913-01/errors-260913-01.md` **W5**（五段式 + 速查表）；被更正的三处 = `verify-260913-01.md:85`（§4.1 判错经验块）、`evidence/arm-commands-260913-01.txt:31`（§1 机制段）、`errors-260913-01.md:39`（W3 根因段，**原文保留不改**，见 `:47` 的 §15.4 取代指针）；judge 侧 = `judge-260913-01.md:34`（核对表「§4.1 机制」行 = ❌ 不一致）+ MUST-1 全文 + 发现 A；一手源 = `versions/1.21.6/java/settings.gradle:13`（`include 'content-test'`，本次实读确认）+ `versions/1.20.1/java/content-test/`（目录存在，`git ls-files` = 3 文件）。
- **观察（现象）**：本块 W3 的机制解释（写在 verify §4.1、命令表 §1、台账 W3 **共三处**）称「1.21.6 的 `versions/1.21.6/java/content-test/` 目录**为空**（无 `build.gradle`）」。judge 独立核对后指出：**该目录根本不存在**（`Test-Path` = **False**；`git ls-files` = **0**；对照 1.20.1 同路径 = 3 个已跟踪文件）——**但结论（1.21.6 裸 `runServer` 无双命中）仍然正确**，且由 `gradle --dry-run runServer` 任务图**双向直证**（1.21.6 仅 `:runServer`；1.20.1 = `:runServer` + `:content-test:runServer`）。
- **根因（机制）**：真实机制是 **`include` 与目录存在性解耦** —— `settings.gradle:13` 的 `include 'content-test'` 令 Gradle **自动创建一个空子工程**（`gradle :content-test:tasks` → `BUILD SUCCESSFUL`，能列出 help 任务），**即使该目录在磁盘上不存在、也从未被 git 跟踪**。故「子工程存在但无 `runServer`」**不蕴含**「目录存在但为空」——把「**子工程**」与「**目录**」当成了同一件事，用**未核实的中间实体**去解释一个已由**正确手段**得到的结论。层级错配：任务图（Gradle 名字匹配/插件系统层）与文件系统（磁盘层）是**两个不同层级的证据**。
- **定位（怎么发现的，可复用）**：judge **不是**复核结论（结论已由任务图直证），而是复核**结论的叙述层**——用 `Test-Path`（磁盘层）+ `git ls-files`（VCS 层）**两条独立证据**核对被顺带断言的事实。这与 #137（外部锚 MUST 用属主工具自核）同族，但对象不同：#137 核的是**引用锚**，本条核的是**叙述中顺带断言的事实**。
- **判据（可复用）**：
  1. **「结论正确」不豁免「解释正确」**——判据的**证明手段**正确 ≠ 叙述里的**事实**都经过核实。凡结论正文里出现「因为…（某环境事实）」这类**顺带断言**，该事实 MUST 与结论**分开各自过一手核对**（#95 的加强版：**结论对、前提错也要修**）。
  2. **判别「某任务 / 子工程是否存在」的唯一可靠依据 = 任务图，不是文件系统**（`include` / 插件 / 约定都可能凭空造出任务或子工程）：`gradle --dry-run <task>` 列任务、`gradle :<proj>:tasks --all | grep <task>` 判任务存在性；**禁止**用目录/文件存在性推断构建图（= 用错误层级的证据解释正确层级的结论）。
  3. **同一错误措辞在多处重复 = 转录扩散**（#90 家族）：一处写错后被复制进 verify / 命令表 / 台账。**修正 MUST 全量 grep 三处**——只改一处会留下「同一文档族内自相矛盾」，比原错更贵。
  4. **judge 复核面必须包含「解释数字时顺带断言的事实」**——本项若漏过，错误的机制解释会随 confirmed 一起进知识库，成为下游的**第二个错误前提**（下游可能据此推出「补一个 `build.gradle` 即复现双命中」，而实际与目录无关）。
- **家族索引**：#95（scout 结论的事实前提与结论分开验证——本条为其**加强形态**：结论对、前提错也要修）、#112（预登记读法纪律——本条为「叙述层」形态）、#137（引用锚须属主工具自核——本条为「叙述事实」形态）、#90/#94（转抄失真——本条为同一措辞**多处重复**的扩散面）、#139（计数载体切分——**任务图直证的落地见 build-tooling #62**）、`errors-260913-01.md` W3（原错）/ **W5**（本条）、`errors-260912-02.md` C-17（该机制的首发地，范围已被本条修正）。

---

### #143 「单写者不变量」结构性论证模板

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #143（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260913-02；主会话（A1-A6 结构性论证）+ judge subagent（PASS-with-conditions，J1 措辞修正 + J2 残留边界随转 + J4 在飞闭包边界）；**candidate**（静态 Degraded 论证 + 降级声明，未做并发压测；confirmed 留人类）；workflow-patterns / 并发写路径安全论证（**论证结构模板，不含本块具体判定结果**——判定在 `.investigations/r9b-260913-02/record-260913-02.md`）。
- **来源定位**：`.investigations/r9b-260913-02/record-260913-02.md` §2（A1-A6 表）/ §3.3（§9.7 边界声明）；judge `judge-260913-02.md` J1/J2/J4；vanilla 一手源（1.20.1 yarn，`.tmp/scout-260905-08/mcsrc/`）：`ChunkHolder.java:49`（`futuresByStatus` AtomicReferenceArray 缓存 per-status future）/ `ChunkStatus.java:88-113`（状态任务 `prev.thenApply` 链式有序）/ `ThreadedAnvilChunkStorage.upgradeChunk:637-658`（邻居等待 `getRequiredStatusForGeneration` 前置状态）/ `ServerChunkManager.java:222-223`（主线程经 future 等待，不直读 proto chunk）。
- **模板（四件套，可复用）**——论证「共享结构 X 的写入路径是否并发安全」时按此结构组证据，而非逐点压测：
  1. **唯一写者**：证明「同 (对象, 操作) 至多一个在飞写者」靠**结构性机制**（本案 = `futuresByStatus` 缓存使同 (chunk,status) 二次请求复用同一 future，不二次生成），不靠「调用点看起来只有一个」。
  2. **可见性链**：证明「全部消费者经同一同步边取得对象」（本案 = 所有下游状态任务/存盘链/主线程均从 `futuresByStatus` 同一 future 链取 chunk，`CompletableFuture` 完成语义给 happens-before）——**消费者清单要枚举到「诊断读回」这类容易漏的进程内读者**，且逐类落点（同链任务 / 邻居任务 / 主线程 / 存盘）。
  3. **全称否定断言的残留边界 MUST 显式声明**：凡结论形如「静态排查未发现任何绕过该同步边的消费者」（A5），MUST 附一句「**未来代码不承担证明义务**——新增缓存引用类消费者将静默破坏本断言，届时结论须重开」（judge J2：缓存**实例**与缓存**引用**是两件事，全称否定只覆盖排查时刻的代码形态）。
  4. **在飞生命周期边界**：写者闭包不可取消（对象卸载时在飞任务仍跑完）**不构成**双写者反例，只要卸载后重载走**新实例**（J4：写目标 = 闭包捕获的旧实例，最坏浪费工作）；此边界不预先声明，未来读者会用 unload-mid-flight 当反例重开结论。
- **判据（可复用）**：
  1. 「每 X 单写者」类安全性论证 = 结构四件套（唯一写者机制 / 可见性链 / 残留边界 / 生命周期边界），**缺一件即 Degraded**，且 MUST 声明「静态论证、未压测」降级（§9.7 三要素随附）。
  2. **前置状态 ≠ 目标状态**（J1 修正面）：等待邻居就绪的机制常等待的是 `getRequiredStatusForGeneration` 类**生成用前置状态**，转抄时禁止写成「等待到达目标状态」——机制措辞按源码，不按直觉（#90 家族）。
  3. 老路径自带的并发检测面是否随之消失，见 compiler-idioms `#24 补充案例（260913-02）`（本条 4 之配套 MUST 问句）。
- **家族索引**：#95（前提与结论分开验证——本条是「论证结构」侧）、#42（静态机制断言未实测当公理——本条以「Degraded + 声明」方式合法化静态论证）、compiler-idioms #24 更正（单写者前提的来源块）、#36 家族补充案例第四例（本块交接前提的廉价验证）。

> **#36 家族补充案例（第四例，260913-02，通过形态——首例「验证通过」）**：交接结论（260911-05 K2 条目 D：「bulk 路径锁私有未发布容器 ⇒ 对共享容器零互斥 + 老路径 crash 检测器被移除 + 正确性外移到每 chunk 单写者」）按 §16.3 开工先做**廉价独立验证**：实读 `BulkWb.java`（readPacket / 私有容器构造 / 发布点）与 `CppBridge.java`（分派 / 旧路径）逐行对照 K2 更正条目，**一轮通过，方向继承**。通过形态的两个卫生要点：① 行号在共享化后偏移（如 readPacket :272 vs 历史记录 :265-267）——**声明偏移、机制逐行核对一致**，而非因行号不符整条弃用或静默照抄；② 验证动作只花一轮源码实读，却免掉了「在未验证前提下推整块并发论证」的报废风险（判据复述 `#36` 原文）。证据：`.investigations/r9b-260913-02/record-260913-02.md` §0；judge 复核 = `judge-260913-02.md`（交接链转抄逐点吻合）。

---

### #144 复跑同标签臂必须先归档首轮日志

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #144（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260913-05；主会话（A2 decisive probe 消解 + 证据链声明）+ judge subagent（MUST-1 证据链声明 + SHOULD-2 立条）；**candidate**（源记录 = **confirmed**，用户授予 2026-09-13）；workflow-patterns / 证据链完整性面（覆盖即灭失）+ #80 家族补充案例（spawn 预生成覆盖的 seed 相关形态）。
- **来源定位**：`.investigations/sentinel-260913-05/record-260913-05.md` §「过程记录：A2 首轮零输出」（现象/候选/差分归因全文）+ §「判读结果」A2 行 + judge MUST-1/SHOULD-2；运行台 `.tmp/sentinel-260913-05/run_sentinel_1201.ps1`（.tmp 不入库，路径固定复用 = 覆盖机制本身）。
- **五段式（错误优先）**：
  - **现象**：A2 首轮（1.20.1，seed -987654321098765432，默认 forceload 区 [-8..7]²）`armed=0 / wb=0`，但 Done 达成、`[CppBridge] init seed` 正确、forceload 已 Marked、存档 region 有产物。且首轮原始日志**现已不存在**——复跑同 seed 同路径后 `.tmp` 载体与 `cmd-output/` 副本均为复跑后状态。
  - **根因（机制）**：运行台脚本日志输出路径固定（同臂标签 → 同文件名），复跑**静默覆盖**首轮产物；`.tmp` 不入库 + cmd-output 副本同步覆盖 ⇒ 首轮证据**覆盖即灭失**。现象本身（零输出）另有机制：默认区完全落在 spawn 预生成范围（约 [-10..10]²）内，预生成完成早的 seed 在 Done 后无新区块可生成 → 零写回零 armed 为**预期行为**。
  - **定位**：① 探针零输出先查过滤/驱动条件（#13 家族）：日志 Marked 后至停服零生成活动；`init seed` 正确排除 seed 错位；dll sha 正确排除执行体错位；② 三候选分叉（gate/env 未送达 #32 族 / 接管未跑 / forceload 区 ⊆ spawn 预生成）→ decisive probe（#13 one-step）：同 seed 改远区 `forceload add 2048 2048 2303 2303` 复跑 → `armed=1/wb=576/crash=0`，候选③唯一成立；③ 证据灭失由 judge 三源核对抓出——cmd-output 文件数与 record 清单不符（A2 首轮件缺失）。
  - **修复**：① record 补证据链声明（judge MUST-1 选项②诚实声明）——首轮 `armed=0/wb=0` 不可独立复核，A2 归因结论依赖复跑对照（同 seed 换远区 → 三指标全过）的差分结构，而非首轮日志原文；② 运行台 1216 脚本默认区域改远区（spawn 覆盖外）。
  - **教训**：见下判据 1/2。
- **判据（可复用）**：
  1. **复跑同 seed/同标签臂 MUST 先归档首轮日志再覆盖**——运行台日志路径按臂标签固定 ⇒ 同标签复跑 = 静默覆盖；`.tmp` 载体不入库 ⇒ 覆盖即灭失、现象不可独立复核。归档动作成本一轮 Copy-Item，事后补证据链声明的代价（结论降级为「依赖差分结构归因」）远高于此。**凡 record 引用了某轮日志，该轮日志 MUST 在任何复跑之前已入库**。
  2. **跨 seed 冒烟的默认 forceload 区可能 ⊆ spawn 预生成覆盖（seed 相关）——跨 seed 复用必须用 spawn 覆盖外固定远区域**（本块 = [128..143]² chunk），且**「零写回零 armed + Done 达成 + bridge init 正常 + region 有产物」组合可读作此预期行为的签名而非缺陷**——先做同 seed 换远区 decisive probe（零重跑成本、一步消解）再立案。预生成完成度是 seed 属性 ⇒ 「默认区域」判据在跨 seed 场景天然不可比（#80 的 seed 相关延伸；A1 的 wb=342 = 预生成残留 chunk 在 Done 后经接管生成，同机制正面实例）。
- **家族索引**：#80（spawn 预生成时序——本条为**跨 seed 覆盖面**延伸形态）、#13（探针零输出先查过滤/驱动条件 + one-step decisive probe 方法）、#32（gate/env 未送达——本块被排除候选①）、#139②（计数排除集/良性噪声——suspExc 双来源表述同块实例）、#56（沙箱 JVM attach 拒访良性）、#88（「复跑采集必删 world」的**对偶面**：复跑前先归档上一轮）、#118（判据输入集合可审计——首轮日志属判据输入，灭失 = 判据不可审计）。

---

### #150 形态耦合修复序（事实串行化掩盖下方缺陷）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #150（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260915-01；subagent 草稿 + 主会话应用；candidate（静态对照实锚 + judge 认可「本池最重要的一条耦合声明」；UB 可达性未运行时实证——修复落地时须声明防御性，#150 判据 2 的 C-4 面）；workflow-patterns / 接管架构修复序。
- **来源定位**：候选池 CP-2/CP-3 耦合声明 + W2 §2.2（`.investigations/form-audit-260915-01/p2-w2-light-rows.md`）+ W4-R5-light（同目录 p2-w4）。
- **观察**：CoreSwap 光照 mixin 把全部重活同步内联在调用线程（L1/L2 错配），该串行形态**事实上充当了锁**——`LightEngine.scratch: RefCell`（light/mod.rs:64）本无同步，只因「车道串行化」从未并发进入。而修复 L1/L2（解粘、异步两段）会**立即暴露** RefCell 数据竞争 UB 面（静态推理成立：LIGHT 任务经 FJP 可并行，调用侧无结构性串行保证）。若先做 CP-2 不做 CP-3，等于把一个潜伏正确性问题（错值/崩溃面，且疑似 G3 首载漂移 7× 的未排查共因之一）当场激活。
- **判据（可复用）**：
  1. **修复前盘点「当前形态事实上提供的隐式安全保证」**——凡修复涉及同步性/线程放置/车道归属的改动，先回答「现在的串行形态在替谁挡并发」；答得出的每个隐式保证都须有显式承接物（Mutex / 队列串行 drain / per-thread 隔离）才算修复完备。
  2. **同批判据**：解除串行化的修复与被其掩盖的缺陷修复 MUST 同一批落地（CP-2 与 CP-3 同批）；方向上「防御性修复可先行、解粘不得先行」（Mutex 在串行访问下无竞争，先做兼容；反之即暴露）。
  3. **与 #107 的互补面**：#107 说「接管必须对齐原实现的同步/异步形态，形态错即性能错」；本条补其修复侧——**对齐形态的动作会连带改变并发可达性**，性能修复的变更面 = 形态本身 + 形态此前掩盖的一切。
- **家族索引**：#113（锁语义成对核对——「只搬一半即自锁死」的跨实现搬运形态；本条是「形态改变激活潜伏 UB」的同域另一方向）。

---

### #158 机制推演候选分解地基 = 内核输入通道清点

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #158（A 类）

- 260917-01；.b3 worker 静态推演 + judge §J6 一手源抽验相符；draft（机制候选 M-a'-α/β、M-c 待 P-α/P-β/P-path 探针链，本条只沉淀方法）；workflow-patterns / 机制候选收敛方法（中价值简记）。
- 来源：candidates/.b3-mechanism-candidates-draft.md + judge-review §J6；一手源 = light/mod.rs:182-192（`light_compute(engine, blocks9, out_block, out_sky, out_flags)`）+ ServerLightingProviderMixin.java:211-216/:637-657/:677-697。
- 方法（可复用）：对「X 是否可能依赖自身旧输出（循环依赖/历史依赖）」类机制候选，第一动作是**清点内核的输入通道**——逐参数列出计算入口函数的完整输入面：本案 `light_compute` 签名只有 blocks9（方块输入）+ 局部 scratch，**无任何 stored light 输入** → Rust 内核层循环依赖在签名层结构性排除 → 候选空间立即收窄到「回退 vanilla 子路径」（mixin collect 失败/预检失败/throw 三类回退面各自形态不同：静默填零不回退、fallback+return false 走 vanilla light()、fallback+内联）。排除法写法要点：排除结论必须锚在签名/调用图这类**结构性一手事实**上（file:line），而不是行为推测；每条回退面单独核对「失败后是否消费旧光照态」。
- 家族索引：#36 家族（静态机制断言一手源核对——本条为「用结构性事实做排除」的正例形态）/ #110（不可达路径证明三件套——排除法兄弟方法，#110 证「路径不可达」，本条证「通道不存在」）。

---

### #160 VOID/GATE 裁决必须非零退出断链

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #160（A 类）

- **发现时间/发现者/置信度/module**：260917-03；主会话采集侧（E3 五段式已落台账）+ knowledge subagent 草稿；candidate；workflow-patterns / 采集链路设计（#118 自证硬门家族的「裁决执行」面 + #144/#146 复跑覆盖家族）。
- **来源定位**：`.investigations/k2-noise-anchor-260917-03/k2-noise-anchor-errors.md` E3 + record §1 表 K2-D5-VOID2-partial 行；修复实例 = run_k2.py:112-115（GATE 不过即 `sys.exit(4)` 断链，judge §B4 已核对回写）。
- **五段式（错误优先）**：
  - **现象**：boot1 判 VOID 后链未断，boot2 已带上一轮启动；kill 中断时留下**无 [SELFCERT]/[GATE] 行的半截日志**（归档为 `K2-D5-VOID2-partial.log`，#144/#146 换标签纪律）。
  - **根因（机制）**：采集链是「boot → 判 → 下一 boot 以本轮产物为 prev」结构；GATE 只打印 VOID 不 `exit` 非零 → 链式脚本继续执行下一 boot，**VOID 轮的污染产物（vanilla 形态 81 chunk）成为下一轮对比 prev**——即使下一轮被人工叫停，也已产生不可作数的半截日志与 world 状态。
  - **定位**：日志缺 `[SELFCERT]`/`[GATE]` 行 + java 进程清单核对发现 boot2 在跑（kill 发现延迟是链未断的直接后果）。
  - **修复**：GATE 不过即非零退出（VOID = 断链语义）；脚本已回写 `sys.exit(4)`；半截日志换标签归档不计入。
  - **教训（判据）**：**裁决的价值在执行不在打印**——VOID/GATE 类裁决 MUST 以进程退出码表达（非零即断链），使「裁决 → 下一轮是否启动」由结构保证而非人工盯守；任何「打印了但流程继续」的裁决 = 裁决未生效。
- **家族索引**：#118（自证硬门——本条补「硬门触发后的执行后果」维：VOID 必须断链）；#144/#146（复跑覆盖/换标签——本条为其上游成因：链未断才产生待归档的半截轮）；#145（驱动未生效签名——「无裁决行」同属装置未生效签名族）。

### 三、追加到 knowledge/discovered/workflow-patterns.md（#13 家族补充案例）

#### #13 家族补充案例（260917-03）：零成本日志探针——引用「日志零命中 = 计数为零」前，先核打点节奏覆盖首次发生（P-α 方法）

- **发现时间/置信度/module**：260917-03；candidate；workflow-patterns / 探针零输出判读（#13 家族：探针零输出先查过滤/驱动条件 + 行首锚 grep 假零输出的判读前置维）。
- **来源定位**：`.investigations/k2-noise-anchor-260917-03/p-alpha-result-260917-03.md` + judge-review §A1（打点节奏一手核对成立：`ServerLightingProviderMixin.java:149-159`，`n <= 8 || (n % 256) == 0` 无条件 println，且不受 FormProbe.ON 门控）；应用实例 = P-α 探针（fallback 计数 0 → M-a'-α 排除）。
- **方法（可复用）**：用「日志零命中」作「事件计数为零」的证据前，MUST 核对三件：① **打点节奏覆盖首次发生**——`n<=8 无条件打印`类首发不受节流盲区（若节奏是 `n%256==0` 则首次发生可整段静默，零行 ≠ 零计数）；② **该打点不受其他开关门控**（门控关闭时零行只证门关）；③ **通道覆盖**（stdout/stderr 均并入日志，如采集脚本 `stderr=subprocess.STDOUT`）——三件齐，零行 = 零计数才成立（G17 系采集脚本同参数核对为 judge SHOULD 补档项 A5）。本案 P-α 即凭此以**零新 run 成本**排除 M-a'-α 通道并连带证伪 M-b。
- **家族索引**：#13（探针零输出先查过滤/驱动条件 + grep 假零输出——本条为其「先核打点节奏再引用零命中」判读前置维）；#84（日志级别假阴性——同属「零命中前核打点条件」家族，本条补节流/门控/通道三维）。

---

### #161 盘上「数据身份」vs「执行体身份」双身份核对

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #161（A 类）

- **发现时间/发现者/置信度/module**：2026-09-17（260917-04）；主会话冲突发现 + fan-out b1 worker（4e305749）审计 + judge PASS-with-conditions 复核 + knowledge subagent 草稿；candidate（三源证据一致：时间线 + boot 耗时形态 + 集合亲缘；混杂份额未做块级量化——idk 如实声明）；workflow-patterns / 采集协议设计（#19 世界状态家族 / #118 自证硬门家族 / #157 收敛性探针家族的「world 归属链」前置维）。
- **来源定位**：`.artifacts/c1-c6-260917-04/verdict-260917-04.md` §2（§15.4 取代记录正式文本）+ `.investigations/c1-c6-260917-04/record-260917-04.md` §2（主会话一手核对 run_g3_settle.py rmtree 行为）+ b1 审计（worker 4e305749）；结构性一手事实 = run_g3_settle.py:91-92（每臂开头 rmtree(world)）+ run_g3_run3.py（不删 world 且无 world 身份自证行）+ 260917-01 运行序（G17b-L60 → G17b-D60 → G17c-L3）。
- **五段式（错误优先）**：
  - **现象**：C1R1-L（legacy 干净链，自证全绿）run2→run3 changed = 0，与 verdict-260917-01 已 confirmed 的「legacy 轮次级不收敛（G17c-L3 = 200/9.88%，漂移集换血 48.3%）」直接冲突；而 G17c-L3 当轮自证硬门逐项全绿（lightInit/hook/dll sha 均过）。
  - **根因（机制）**：260917-01 的采集协议是**跨臂复用型**——run_g3_settle.py 每臂开头 rmtree 盘上 world，而后续 run3 脚本（run_g3_run3.py）**不删 world、也不在自证门里核对盘上 world 的归属链**。运行序 G17b-L60 → G17b-D60 → G17c-L3 中，G17b-D60（domain 臂）的 rmtree 把 G17b-L60（legacy 臂）留下的 world 覆盖重建为 domain 世界；G17c-L3 以「同 world 第三 boot」名义启动时，加载的实为 **D60 的 domain world**——其 prev_after（L60 run2 快照）与盘上 world 为跨世界对比，200-changed 度量的是「两个不同世界」，不是 legacy 路径自身的轮次级不收敛。坑的层次有三：① 复用脚本继承了 settle 脚本的「每臂删 world」语义但自己是复用型，两脚本对 world 生命周期的约定不一致；② 自证硬门核对的是**执行体身份**（lightInit/hook/dll sha），没有一项核对**数据身份**（盘上 world 是谁的）——执行体全绿掩盖了数据被换；③ 已 confirmed 的结论 + judge 三源核对（快照/git diff/验证记录）也未覆盖「跨臂 world 归属」这一维——三源核对核的是证据管理面，不是实验设计面。
  - **定位（怎么发现）**：不是复跑 260917-01，而是**本轮干净对照臂（C1R1-L）与历史结论的冲突**触发的——同协议 fresh 链 run1→run2 changed=128（历史 127 吻合，检测力旁证）但 run2→run3 = 0。主会话一手核对采集脚本发现 run_g3_settle.py:91-92 的 rmtree 与复用脚本不删 world 的组合；fan-out b1 worker 做世界归属链审计三源闭环：① 运行序推演（D60 rmtree 在 L3 之前）；② boot 耗时形态（G17c-L3 Done 5.615s = 加载既有 region，非 fresh 生成 ~37s 形态）；③ 集合亲缘旁证（S200∩S166=77 > S200∩S127=63，200-changed 集与 domain 臂集合更亲）。b2 worker 独立排除「本轮 0 为假测量」。
  - **修复**：① §15.4 取代记录（verdict-260917-04 §2）：verdict-260917-01 的 run3 层 legacy 证据及两臂对照叙事被取代，原结论正文不删不改；② 新结论（candidate，n=1 单 seed 单区域）：fresh 同 world 链上 legacy run2 吸收首轮修正后 run2→run3 = 0（收敛），域批同层 = 2（保守带内）；③ 协议面修正方向 = run3 类复用脚本自带 world 归属自证（见判据）。
  - **教训（判据，可复用）**：
    1. **「同 world 第 N 轮」前提必须核盘上 world 归属链，不得凭脚本意图推定**——任何跨 boot/跨臂复用盘上 world 的协议，「本轮加载的 world 是谁生成的」是独立的数据身份问题；判据 = 每臂启动时留 world 身份自证行（如 world 目录创建时间戳 / 上一臂标签 / region 文件指纹三者其一），或协议上保证 world 生命周期单臂封闭（每臂 fresh 或显式声明继承链）。
    2. **每臂 rmtree 的运行序即世界身份链**——复用型协议接入 rmtree 型协议的产物时，MUST 推演一遍「盘上 world 最后被哪一臂写过」；臂序中任何 rmtree 臂都会重置后续所有臂的 world 归属。
    3. **自证门必须含数据身份项，不止执行体身份**——lightInit/hook/dll sha 核「跑的是哪个引擎」，不核「跑在哪个世界上」；两类身份门缺一不可。
    4. **干净对照臂与历史结论冲突 = 最高价值审计触发器**——本错误在已 confirmed + judge 通过的结论上潜伏至下一块对照臂出现才暴露；对照臂结果与历史结论冲突时，第一怀疑对象是历史实验的隐含前提（而非新臂测量错误），b1（历史归属审计）/ b2（新臂真伪审计）双 worker 并行是标准处置。
  - **边界（idk）**：混杂对 G17c-L3 200 的解释份额未做块级量化；G17c-L3 prev_after argv 值无落盘记录（record-260917-01.md:15 为唯一来源）——取代记录生效前提含用户对此单源依赖的知情确认。
- **家族索引**：#19（世界状态残留——本条为其「跨臂 world 覆盖」形态：不是残留干扰测量，是前提对象被整体换掉）/ #118（自证硬门——本条补「数据身份」维）/ #156（执行体形态失传——姊妹条：#156 是引擎身份失传，本条是世界身份失传，合称「双身份核对」）/ #157（round-trip 收敛性判据——本条为其「同 world 前提」的成立条件）/ #144/#146（运行序与标签纪律——本条补「臂序决定 world 归属」维）。


> 260917-05 追加：workflow-patterns 新增**发现 #162（最高价值·错误优先）**（**汇总交叉定性 MUST 回原始日志抽样——「口径解释」未经验证就是新伪差**：主会话机械交叉「inputDiff23=46/46 = packed↔blocks9 ABI 切换」被 verdict worker 10 行日志抽样一票推翻——全日志 bi=blocks9 0 行、46 diff chunk 三 run 均 abi=packed、hash 两两不同、emptySec 恒等；其余交叉数字全部正确。判据：① 汇总交叉产物 = 数字 + 定性，数字可复算继承，**定性 MUST 抽样回原始日志一手验证后才可进 verdict**；② 给异常 diff 安解释前先证解释的存在前提（一个 grep 即证伪）；③ 「跨口径 hash 差集先核口径同质性」保留对偶面——同口径 ≠ 无伪差（本轮 46 即 packed↔packed 同口径真不稳定，定性机制 open 而非套现成解释）；④ 计数恒等 ≠ 集合恒等（emptySec 计数只作必要条件证据），hash 探针输出应随行打印口径要素让日志自证。来源：.artifacts/pbeta-260917-05/verdict-260917-05.md §1 + .investigations/pbeta-260917-05/（judge PASS-with-conditions S1-S5 已应用；candidate，confirmed 留用户）。时间线 → versions/1.20.1/docs/10-timewise-archive.md 260917-05 块。

---

### #162 汇总交叉的定性必须回原始日志抽样

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #162（A 类）

260917-05 追加：workflow-patterns 新增**发现 #162（最高价值·错误优先）**（**汇总交叉定性 MUST 回原始日志抽样——「口径解释」未经验证就是新伪差**：主会话机械交叉「inputDiff23=46/46 = packed↔blocks9 ABI 切换」被 verdict worker 10 行日志抽样一票推翻——全日志 bi=blocks9 0 行、46 diff chunk 三 run 均 abi=packed、hash 两两不同、emptySec 恒等；其余交叉数字全部正确。判据：① 汇总交叉产物 = 数字 + 定性，数字可复算继承，**定性 MUST 抽样回原始日志一手验证后才可进 verdict**；② 给异常 diff 安解释前先证解释的存在前提（一个 grep 即证伪）；③ 「跨口径 hash 差集先核口径同质性」保留对偶面——同口径 ≠ 无伪差（本轮 46 即 packed↔packed 同口径真不稳定，定性机制 open 而非套现成解释）；④ 计数恒等 ≠ 集合恒等（emptySec 计数只作必要条件证据），hash 探针输出应随行打印口径要素让日志自证。来源：.artifacts/pbeta-260917-05/verdict-260917-05.md §1 + .investigations/pbeta-260917-05/（judge PASS-with-conditions S1-S5 已应用；candidate，confirmed 留用户）。时间线 → versions/1.20.1/docs/10-timewise-archive.md 260917-05 块。

---

### #163 门禁只判「存在/数量」= silently-green 门

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #163（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260917-05；主会话执行 B1/B7 时实证 + 上游 v2.6 同步落地，core.worker subagent 起草；**candidate**（本工作区侧 = 内容 sha256 递归对账 `ALL GREEN (17 skills, recursive)` + selfcheck 五段全绿实证；上游侧 = selfcheck 源码自述，非本工作区复现）；workflow-patterns / 门禁设计与安装产物核验（**#105「载体偏差」家族的门禁形态 + #118「自证行硬门禁」的判据语义维**）。
- **来源定位**：`.investigations/pbeta-260917-05/upgrade-execution-record.md` §B1（8 drifted 清单 + `ALL GREEN (17 skills, recursive)` + selfcheck 两段对账报告）+ `.investigations/paper-2608-25512/remaining-after-upgrade.md` §B / §B1（项目级 `.dsh/skills` = 28 个、版本标记 13× v0.20 + 5× v0.21、`§5.6|preconditions|evidence grade|suspend` **零命中**）+ 上游实现 `E:\PYTHON\RE-Framework\dsh\scripts\selfcheck.ps1:56-58`（旧段：`$count -lt 17`）vs `:64-118`（新段：MISSING/DRIFT/ORPHAN 逐件 sha256）。

- **观察（现象）**：项目级 `E:\PYTHON\CoreSwap\.dsh\skills` 的**目录计数一直是「绿」的**（28 个目录，ref-\* 17 + anchor-\* 11，数目从未少过），但内容层面 **8 个 ref-\* 已 drift**（core-artifact / core-fanout / core-judge / core-knowledge / core-plan / re-lift / ref-maintain / swe-guide）——残留 v0.20/v0.21 版本标记、v0.22 新条款关键词（`§5.6` / `preconditions` / `evidence grade` / `suspend`）**零命中**。即：**门是绿的，产物是陈旧的**，且这一状态**无任何机制能发现**，只能靠人手工逐文件 diff/grep 才暴露。上游 v2.6 恰好把 selfcheck 第 3 段从**目录计数**（`$count -lt 17`）升级为**内容对账**（install-manifest.yaml / .re-framework-manifest.yaml 逐件 sha256，报 MISSING/DRIFT/ORPHAN 并非零退出），其源码注释自述这与 preset 行解析门禁是**同一失败类**：*"a gate that silently goes green when it cannot execute is the same failure class as the incident it guards against"*。

- **根因（机制，为什么错）**：**「存在」与「数量」是内容的必要非充分条件**——一个门禁若其判据落在目录存在性/条目计数上，则「产物被替换为旧版本」「产物被局部编辑」「产物被同名占位」三类退化**全部落在判据的盲区**，门恒绿。这不是实现 bug，是**判据语义的层级错配**：被保护对象的真实语义是「产物 = 安装源的内容」，而门问的是「产物 = 若干条目」。与 preset 行解析门禁同构：后者在**无法执行**时静默绿（缺口被吞），前者在**产物不可信**时静默绿（漂移被吞）——共同点是**门的判据没有触达被保护语义本身**，于是门的「绿」只证明门跑了，不证明被保护对象没坏。

- **定位（怎么发现的，可复用）**：① **内容级 grep 反证**——不数目录，直接 grep 新条款关键词（`§5.6` / `preconditions` / `evidence grade` / `suspend`）→ 零命中，而 user-global 侧同一批文件命中，两副本对比一眼看出 drift；② **逐文件 sha256 递归对账**——用显式文件清单（非通配，防混入）做递归 sha 对账，得 `ALL GREEN (17 skills, recursive)`，与 grep 结论互证；③ **核门禁判据本体**——读上游 selfcheck 第 3 段前后版本（`:56-58` 计数 vs `:64-118` 内容对账），确认「绿」的来源是计数而非内容。

- **修复 / 如何利用（判据，MUST）**：
  1. **判据（MUST）**：凡门禁判据只判「存在 / 数量 / 条目数」，**一律按 silently-green 门处理**——补内容对账（逐件 sha256 或内容指纹）后该门才可作结论依据；对外的「全绿」声明 MUST 同时声明**门测的是什么**（数量门 / 内容门），否则「全绿」不构成产物可用证据。
  2. **安装产物核验的正确形态** = `install-manifest.yaml`（source_commit + 逐件 sha256）+ 对账报 MISSING/DRIFT/ORPHAN + **非零退出**——「数量对」只能当**前置必要条件**，不能当结论。
  3. **门禁哲学（跨领域）**：门禁的判据必须触达被保护语义本身；**「门跑了」≠「门守住了」**。同一失败类的两种表现：① 门无法执行 → 静默绿（preset 行解析门禁上游自述）；② 门可执行但判据层级过低 → 静默绿（本条）。
  4. **反向操作提示**：升级门禁时，旧计数门**不要删**——保留为廉价前置（数量不对时连内容都不用查），内容门作为后置强判据；两者**判据域不同、结论强度不同**，MUST 分别声明。

- **家族索引**：#118（自证行硬门禁——「只打印不判定 = 没有门禁」；本条补「判定了但判据层级过低 = 门恒绿」）、workflow-patterns #105（载体偏差——「载体全绿」对真实故障零判别力；本条为其**门禁判据**维）、#27/#50（静默退化/静默销毁家族：退出码 0 + 无警告）、#16/#18/#23（「产物在盘 ≠ 当前语义」家族的门禁形态）、build-tooling #2/#27（marker 语义超载——同属「一个判据承载了它不承载的语义」）。

---

### #164 多副本安装树的「无脚本覆盖面」（逐副本谁写谁验）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #164（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260917-05；core.worker subagent 起草（主会话 B1 复核一手发现 + 手工同步执行）；**candidate**（脚本参数面 = 一手读码实证：RE-Framework install.ps1 无 `-Project` 参数、Anchorlaw `-Project` 只复制 `skills\*` 即 11 个 anchor-\*；项目级 17 ref-\* 副本 = 手工 Copy-Item 完成并内容对账全绿）；workflow-patterns / 部署覆盖面与副本漂移（**#100「谁写谁读」双侧核对家族**的部署副本形态 + **#105「载体偏差」**的副本维）。
- **来源定位**：`.investigations/paper-2608-25512/remaining-after-upgrade.md` §B1「脚本覆盖面实证（本次复核新发现）」（一手定位 = RE-Framework `install.ps1:1-12, 137-146`；Anchorlaw `install.ps1:38-55`）+ 本轮一手复核 `E:\PYTHON\RE-Framework\dsh\scripts\install.ps1`（**函数签名无 `-Project`**，头部注释的安装目标仅 `~/.dsh/.agent-presets/re-framework/` 与 `~/.dsh/skills/` 两处）+ `E:\PYTHON\Anchorlaw\dsh\scripts\install.ps1:22-29, 38-55`（`param([string]$Project)`；`Copy-Item -Path (Join-Path $srcRoot 'skills\*')` = 仅 11 个 anchor-\* 落到 `<proj>/.dsh/skills`）+ `upgrade-execution-record.md` §B1（项目级 17 ref-\* 手工按显式清单 Copy-Item）。

- **观察（现象）**：同一框架/协议的技能产物在本机存在**三份副本树**，但脚本覆盖面**只有两份**：
  | 副本树 | 谁写它 | 谁验它 |
  |---|---|---|
  | `~/.dsh/.agent-presets/re-framework/skills/`（17 ref-\*，preset 内嵌） | RE-Framework `install.ps1`（无参） | selfcheck 第 3 段（preset manifest 内容对账） |
  | `~/.dsh/skills/`（17 ref-\* + 11 anchor-\*，user-global 共享树） | RE-Framework `install.ps1` + Anchorlaw `install.ps1`（无参） | selfcheck 第 3 段（user-global manifest 内容对账，命名空间限定 `^(core\|re\|recode\|swe\|ref)-`） |
  | `<proj>/.dsh/skills/`（**28 个**，Rank 100，本工作区会话最高优先命中） | **anchor-\* 11 个**由 Anchorlaw `-Project` 写；**ref-\* 17 个无任何脚本覆盖** | **无**（不在任何 manifest 的对账范围内） |

  ⇒ 项目级 17 个 ref-\* 副本是**漂移黑洞**：脚本不写它、manifest 不含它、selfcheck 不验它，其陈旧只能靠人肉 grep/对账发现——本轮 8 个 drift 正是这样暴露的（且是被**别的工作**顺带撞见，不是被机制发现）。

- **根因（机制）**：**「脚本可写面」与「运行时可见面」不是同一张地图**。DSH 的技能发现排名是 项目级（Rank 100）> `.agents/skills`（200）> preset 内嵌（300）> 用户级（400）——即**最高优先命中的那一份，恰是脚本从不写的那一份**。两个上游各自只覆盖自己的命名空间（Anchorlaw 管 anchor-\*、RE-Framework 管 ref-\* 但只写 user-global/preset），**没有任何一方对「项目级树」负责**：职责边界按命名空间切，不按副本树切，于是副本树成了职责的补集。更本质的是：项目级副本**不参与任何 manifest 的身份登记**，因此它连「内容对账」这类强门禁都没有输入可用——**没有身份登记就没有对账**（这也说明 A 条的内容对账门只覆盖「有 manifest 的副本」）。

- **定位（怎么发现的，可复用）**：① 读两个 install.ps1 的**参数面**（`param()` 块 + 头部注释的目标清单）→ 一眼看出无 `-Project`；② 读 `-Project` 分支的 `Copy-Item` 源（`skills\*`）→ 只有 anchor-\*；③ 对照运行时副本清单（`Get-ChildItem .dsh\skills -Directory` = 28 个）→ 差集 = 17 个 ref-\*；④ 复核 selfcheck 的 manifest 路径（两条：preset 内、user-global）→ 项目级不在其中。**四步全为读文件，零执行成本**。

- **修复 / 如何利用（判据，MUST）**：
  1. **判据（MUST）**：**多副本部署 MUST 逐副本给出「谁写、谁验」两问**——答不出「谁验」的副本即**漂移黑洞**，必须补（a）纳入某方 manifest 的对账，或（b）在部署脚本中显式声明「手工同步 + 同步后跑内容对账」，或（c）删掉该副本（若其可见性收益不值得维护成本）。**只答「谁写」不足以合规。**
  2. **覆盖面必须按「副本树」核对，不能按「命名空间」核对**——命名空间切分会让副本树成为职责补集（本条实例）；核对动作 = 列出运行时**实际可见**的每一个副本路径，逐个问「哪个脚本写它 / 哪个门验它」。
  3. **手工同步是不可接受的长期形态，但可以是合规的过渡形态**——前提是**同步动作本身有对账**（本例 = 显式文件清单 Copy-Item（禁通配，防混入）+ 递归 sha256 对账），且该对账 MUST 记入执行记录；「手工同步 + 无对账」= 最坏形态（既无自动门，又无一次性验证）。
  4. **副本优先级倒挂是风险放大器**：副本的**可见性排名越高，越容易被消费，越必须被门禁覆盖**（Rank 100 的项目级副本排在第一位，却唯一无门）——部署设计时按「可见性排名」而不是按「写入便利性」分配门禁强度。

- **家族索引**：**#163（silently-green 门——本条为其覆盖面维：内容门只覆盖有 manifest 的副本）**、workflow-patterns #100（「谁写谁读」双侧核对——本条为部署副本的「谁写谁验」形态）、#105（载体偏差——最高优先命中的副本恰是无门的那份）、#77（回滚 ≠ 引用面清理——同属「结构动作的完整性检查」）、#54（目录级规则作用域 MUST 按「里面住了什么」核——同属「作用域/覆盖面必须先枚举再声明」）。

---

### #165 升级路径的沙箱边界首次碰撞（升级后首跑视为 escalation 窗口）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #165（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260917-05；主会话 B1 首次生产调用实测（install 中止 → escalation 后成功），core.worker subagent 起草；**candidate**（一手：失败原文 + escalation 后命令全绿 + 上游源码定位到 `:104-119` 事务备份段）；workflow-patterns 或 build-tooling（**build-tooling #42 tmpdir 家族 / #46 沙箱可用性家族**的「升级引入新环境前提」形态 + AGENTS.md 全局铁律「沙箱 escalation 凡涉及 workspace 外路径，用户一律先拒绝再人工重审」）。
- **来源定位**：`.investigations/pbeta-260917-05/upgrade-execution-record.md` §B1 首条；上游实现 `E:\PYTHON\RE-Framework\dsh\scripts\install.ps1:104-119`（`$patchBackup = "$patchPath.bak-ref-install"` + `Copy-Item` 备份 → 失败时 `Copy-Item $patchBackup $patchPath` 还原 → `throw`）；注释自述动机 = *"The patch file is host-shared state: other frameworks' rows live in it too, so a bad rewrite is not recoverable by re-running this script. Back up first."*（同源 = 论文 §5.2.2 Algorithm 10 transaction 形态）。

- **五段式（错误优先）**：
  - **现象**：`pwsh E:\PYTHON\RE-Framework\dsh\scripts\install.ps1` 首次执行**中止**——写入 `C:\Users\NDark\.dsh\profiles\web\cordis.patch.yml.bak-ref-install` 被 DSH 沙箱拒绝（该路径在 session workspace `E:\PYTHON\CoreSwap` **之外**）；escalation 后同一条命令成功。**注意这个组合**：该脚本**本来就要写 DSH home**（`~/.dsh/.agent-presets/`、`~/.dsh/skills/`，本就在工作区外，历史上从无问题——因为那些写操作此前已在允许面内或以既有方式通过），而**新增的一步备份**落在了一个此前从未被写过的具体路径上，于是首个失败点是**新机制**而不是老命令。
  - **根因（机制）**：**「更安全」的机制会扩大写入面**。事务备份的语义要求「先复制一份到可寻址路径」，这一动作把写入面从「目标文件」扩展到「目标文件 + 备份路径」——而备份路径（`cordis.patch.yml.bak-ref-install`）是**首次出现的新对象**，其父目录/命名的可写性**从未被历史命令验证过**。⇒ 上游把「不可恢复的坏重写」风险换成了「首次运行撞环境边界」风险，**这是一次风险转移而非纯收益**；而转移后的风险**只在首次运行暴露**（一旦备份文件已存在，`Copy-Item -Force` 覆盖同一路径的行为是否仍被拒，取决于是「创建新文件」还是「覆盖已有文件」的沙箱策略，**本块未单独复现，属 idk**）。
  - **定位（怎么发现的，可复用）**：错误文本本身就指名了**新路径**（`.bak-ref-install` 后缀是这次升级新引入的命名）——**判错动作 = 读失败路径，并与「这次升级改了什么」对照**：失败路径里的命名是升级前不存在的 ⇒ 先怀疑新机制而不是老命令的回归。辅证：读上游 `install.ps1:104-119` 确认该段是 v2.6 新增的事务备份段（注释与论文 Algorithm 10 同源）。
  - **修复（处置）**：escalation 后重跑成功（本会话批准面）；**纪律层修复**（本条的真正价值）= 把「升级后的第一次运行」显式列为 **escalation 窗口**：
    1. **升级动作分两步走**：先在一个可 escalation 的窗口里跑**一次**安装脚本（允许首次撞边界），确认新增机制在目标环境可用后，再把「重跑安装脚本」当作例行命令；**不要**把首次运行放在无人值守/批处理链里。
    2. **对上游新增的每一个「更安全」机制，问一句「它新增了哪些写入对象」**——新增的备份/临时/日志/锁文件路径都是新的环境前提，MUST 在升级记录里逐个登记（本条的登记物 = `cordis.patch.yml.bak-ref-install`）。
    3. **失败要中止而非降级**——本例 install 中止是可接受的（宁可停也不要「跳过备份继续改共享 patch 文件」，那正是备份段要防的事）；**升级后的失败模式检查 = 「失败时是中止还是静默降级」**，静默降级的「更安全」机制比没有更危险。
  - **教训（可复用判错经验）**：
    1. **「老命令照跑」不成立**——命令没变，但它依赖的**环境前提变了**（新写入对象）；环境边界类故障在升级窗口的暴露率被系统性低估。判据：**升级后首次运行 MUST 视为需要 escalation 的窗口**，且失败路径里的**新命名**是第一线索。
    2. **沙箱类失败先核「这次多写了什么」**，不要先怀疑权限配置回归（AGENTS.md 全局铁律：「沙箱 escalation 凡涉及 workspace 外路径，用户一律先拒绝再人工重审」——本条是这条护栏的**正常运作实例**，不是事故）。
    3. **同族**：build-tooling #42（JNA tmpdir 拒访——同为「环境前提未被满足」）、#46（沙箱能力必须实测、被拦形态可能是阻塞而非异常）、#153（沙箱 taskkill /I 组级 kill 拒绝——**沙箱能力面是分粒度的**，同一类操作的不同粒度可能一放一拒）；三者共同上位原则：**沙箱能力清单 MUST 实测维护，不凭常识推断**，且**升级动作是刷新该清单的强制时点**。

- **家族索引**：build-tooling #42（tmpdir 环境前提）/ #46（沙箱能力实测）/ #153（沙箱能力粒度）；workflow-patterns #105（环境/载体变化先核，勿按历史结论续推）、#18（跨 session/跨块结论不可直接续推——升级即一次「环境换代」）。

---

### #167 逆登记不得为表格好看编造「可还原」

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #167（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260917-05；主会话执行 B3/B4（§9.8 副作用逆登记 + 判据前置集落地）+ core.worker subagent 起草；**candidate**（本工作区**首个实例**，5 条 effect→inverse 表，其中 2 条为显式不可逆声明；协议条款一手核对 `:950-964`）；workflow-patterns / 验证副作用登记与诚实声明（**#129「判据只有满足/未满足两种终态，写不可判 MUST 先证明测量不可分辨」的 §9.8 对偶面**——本条是「逆只有可寻址/显式不可逆两种终态，禁止伪造中间态」）。
- **来源定位**：`.investigations/pbeta-260917-05/criteria-260917-05.md` 末节「验证副作用与其逆」（5 行表）+ 协议原文 `E:\PYTHON\Anchorlaw\spec\protocol-v0.22.md:950-964`（§9.8 Verification Temporality；关键句 = *"Writing an inverse MUST NOT be fabricated to satisfy the clause: an inverse that does not actually restore the prior state is worse than a declared irreversible effect, because it makes a false claim"*，以及 *"Automatic reversion is forbidden precisely because a failed round's artifacts are the more valuable evidence"*）。

- **观察（现象）**：本轮登记 5 条 in-place / derived 副作用，其中 **2 条如实声明为显式不可逆**，而不是给一个看起来能还原的逆：
  1. **删除 `run/world`（run1 前强制重新生成）** → 逆 = **显式不可逆声明**（world 为生成产物，逆 = 删除，重生成即等价；原 world 无保留价值）；
  2. **改 `server.properties` 的 `level-seed`** → 逆 = 备份件 `server.properties.bak-formprobe`（脚本 `:36-43` 首次运行前创建，可还原）**但附注**：该备份为**首次快照**、非本轮前状态 ⇒ **已声明不可逆面 = 「本轮前的 seed 值未单独留档」**。
  其余 3 条为常规合规形态（derived 产物 identity / 源码 git revert / 覆盖风险由驱动拒绝同标签日志而「机制上不发生」）。

- **根因 / 判据（机制，为什么这样才对）**：逆登记的用途是**让副作用可被 containment 核对**（judge 的三源基线要能查「有没有该登记的逆」），不是让表格齐整。**伪造逆的危害等级高于声明不可逆**：不可逆声明是**诚实的缺口**（下游知道这块没有还原路径，会据此调整处置），伪造的逆是**虚假的保证**（下游以为可还原，实际不能）——协议 rationale 明写其「makes a false claim」，属 §7 行为准则级错误。第 2 条的形态尤其值得记：**「有备份文件」不等于「备份的是本轮前状态」**——备份是在首次运行时创建的快照，之后所有轮次的改动都**不在**它的还原范围内；不把这个边界写出来，备份件就会变成一个**看起来合规、实际部分失效**的逆。

- **定位 / 怎么落地的（可复用操作）**：逐条列出本轮所有会改盘上状态的动作 → 对每条问三问：**① 它改了哪个可寻址对象？② 有没有一个盘上可寻址的逆（归档件路径 / 换标签后的新名 / 环境还原记录）？③ 若没有，缺口具体是什么（写清「哪一段状态无法还原」）？** 第 ② 问答案为「没有」时，**允许**写「显式不可逆 + 理由」，**禁止**用「重生成即等价」「再跑一次就回来了」这类**未经验证的等价性叙事**顶上（除非该等价性本身成立且被声明条件，本条 world 一条即属此类：删除 = 逆，因为对象是纯生成产物——**该理由本身是判据，不是措辞**）。

- **修复 / 如何利用（判据，MUST）**：
  1. **判据（MUST）**：逆登记 MUST NOT 为了让表格好看而编造「可还原」；**不可逆 + 理由 才是合规形态**。每个 in-place 副作用的逆只有两种合法终态——**① 盘上可寻址的逆**；**② 显式不可逆声明 + 具体缺口说明**。中间态（「大致能还原」/「重跑即可」而无条件声明）视为伪造逆。
  2. **逆为独立字段，不得并入 `source=`**（协议明文）：`source` 答「哪份记录背书」，inverse 答「副作用如何被 containment」——**两个不同事实合并会把语义与扫描门一起弄脏**。
  3. **备份件的逆效力 MUST 声明其快照时点**——「备份在首次运行时创建」⇒ 该逆的还原范围 = **首次运行前的状态**，不是「本轮前状态」；不写这一行，逆就是部分失效的。
  4. **禁止自动回退**（协议明文）：失败轮的产物证据价值高于成功轮；**逆是登记义务，不是 runtime 机制**——协议只要求「登记并可寻址」，不要求任何自动回滚。逆的**正确性是作者义务，非 runtime 保证**（协议 rationale 引用论文边界；主会话 A1 判断被 v0.22 原文引用采纳）。
  5. **落地形态（本工作区）**：采集脚本/verdict 增 `inverse` 字段（与 `source=` 并列，不合并）+ 判据 artifact 增 `preconditions:` 字段（key/expected/check，见同批 criteria-260917-05.md 首实例）。

- **家族索引**：**#129（判据终态二分——本条为其 §9.8 对偶面：逆也只有二终态）**、#27/#50（静默退化/静默销毁——伪造逆属另一类静默：**虚假保证**，比静默更坏因为它主动声明）、#143（全称否定断言 MUST 声明残留边界——同属「声明必须把边界写出来」）、#137（引用完整性——逆 = 副作用的引用面）。

---

### #172 门禁有效性必须用注入式负向测试自证

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #172（A 类）

- **发现时间 / 发现者 / 置信度 / module**：2026-09-18（260918-01 B6-1 round 5）；主会话执行双注入实测 + 本 knowledge subagent 起草；**draft**（本轮为**首实例**，两维注入各一次、实测原文在案；分层 = **Partial**——注入式静态实证，未跑 JVM 端到端，见「边界」）；workflow-patterns / 门禁与校验工具设计（**#163「silently-green 门」的操作性补强** + **#27「负向测试是断言生效的唯一证明」同旨**）。
- **来源定位**：`.investigations/b61-260917-06/gate-negative-tests.md` §0（判据来源）/§1（负向测试 A 原文）/§2（负向测试 B 原文）/§3（还原验证）/§5（覆盖面与降级声明）/§6（§9.8 副作用与逆表）；测试脚本 `.tmp/b61-260917-06/negtest_round5.py`（`inject`/`restore` 两模式，`shutil.copyfile` 备份 + 正则删除 + 还原）；门禁实现 `scripts/check_switch_mapping.py:177-198`（per-version 段命中打印）+ `:202-207`（`[OUT-OF-SCOPE]` 打印）+ `:236-240`（`--strict` 退出码）。

- **观察（现象）**：本轮对**同一个 gate 的两个检测维度**各做一次**注入式负向测试**，两个维度**都能真失败**：
  1. **主检测（漏映射 → per-version 缺口 / ORPHAN）**——删除 `versions/1.20.1/java/build.gradle` 中已修复的 `-PsurfaceDumpDim` → `-Dsurfacedump.dim` 映射行（模拟「有人误删」回归）。实测原文：
     ```
     [INJECTED] removed: if (project.findProperty('surfaceDumpDim') != null) run.vmArg "-Dsurfacedump.dim
       surfacedump.dim
       [1.20.1] 声明 127 / 本版(+共享)消费 136 → 缺口 12
       rc=1
     ```
     ⇒ **四项自洽**：声明面 128→127、缺口 11→12、命中项 `surfacedump.dim` 出现在缺口清单、`--strict` rc=1。
  2. **作用域检测（#47：`run.vmArg` 落在接收 `run` 的闭包之外）**——在文件末尾（`benchVmArgs` 闭包**之外**）加一行 `run.vmArg "...-Dscope.violation=1"`。实测原文：
     ```
     [OUT-OF-SCOPE] versions\1.20.1\java\build.gradle:293  if (project.findProperty("scopeViolationTest") != null) run.vmArg "-Ds
       strict rc=1
     ```
     ⇒ **作用域检测可失败** ✅。
  3. **两次注入均逐字节精确还原**：
     ```
     [RESTORED] from .tmp/b61-260917-06/bg-negtest-backup.gradle
     git diff --stat HEAD -- versions/1.20.1/java/build.gradle   → （空）
     CONSISTENT: 125 / [1.20.1] 缺口 11 / [1.21.6] 缺口 21
     ```
     ⇒ 还原**逐字节精确**（`git diff` 为空），gate 回到基线；主会话侧复核亦确认 `git status --porcelain` 为空、基线数字 M1 129 / DEAD 4 / ORPHAN 11 在位。

- **根因 / 判据（机制，为什么这条必要）**：**「门跑过了」与「门能拦住」是两件不同的事实**。门禁的常规运行只产生**绿**这一种输出——而绿是**两种状态**的共同像：① 被保护对象健康；② 门本身失效（判据写错 / 检测维度缺失 / 静默降级 / 覆盖面漏掉该对象）。只跑一次绿**在结构上无法区分二者**（#163：判据只落「存在/数量」的门恒绿，其绿只证明门跑了，不证明被保护对象没坏）。**唯一能把两者分开的动作 = 主动制造一次该门应当捕获的缺陷，观测它是否真的报错并给出非零退出**——即「注入式负向测试」。故：**一个不能失败的 gate 等于没有 gate**；门的**交付物必须包含它「我可失败」的实证**，而不是只有「我跑了」的日志。
  第二层机制（为什么必须注入**每个检测维度各一次**）：门的各检测维度实现路径不同（本 gate 的主检测走集合差 + per-version 段，作用域检测走闭包边界识别 `check_switch_mapping.py:126-141`），**某一维能失败不蕴含另一维能失败**——单点注入只自证了那一条路径。本轮的对称形态（主检测 / 作用域检测各一）是对「覆盖检测维度而非覆盖工具」的落地。
  第三层机制（为什么「精确还原」是判据的必要构成）：负向测试本身是一次 **in-place 副作用**（改的是仓库里被保护的那份文件），若不还原或还原不精确，则「自证门有效」的代价变成「污染被判对象」——此时**后续所有绿都不可信**。故注入的**逆必须可寻址且被验证**（§9.8），判据形态因此是三段而非两段：**注入 → 观测命中 + 非零退出 → 精确还原**。

- **定位 / 方法（怎么做的，可复用）**：
  1. **枚举检测维度**：读门禁实现，列出它声称覆盖的每一类检查（本例 = 主检测 / 作用域 / 命名一致性三族，本轮注入前两族），**逐维**设计注入；
  2. **注入点选「该维度的最小触发」**：主检测 = 删一条**已修复**的映射行（选已修复项的理由：其缺口状态已知，注入后数字变化方向可预测 ⇒ 期望值可预登记，不是事后解释）；作用域检测 = 在闭包外追加一行；
  3. **预登记期望值**：注入前就写下「声明面应 −1 / 缺口应 +1 / 命中项应含该名 / 退出码应为 1」四项——使自证具备**可判伪**性（否则「它报错了」也可能只是别的错）；
  4. **观测**：跑门禁（含 `--strict`），核对四项逐项命中；
  5. **还原并验证还原**：备份件还原 → `git diff` / `git status --porcelain` **为空**→ **重跑门禁回到基线数字**（三步，缺一不足以证「无残留」：diff 空只证字节一致，回基线数字才证运行态一致）；
  6. **登记副作用与逆**（§9.8，见下）。

- **修复 / 如何利用（判据，MUST）**：
  1. **判据（MUST）**：**任何门禁 / 校验工具交付时 MUST 附「我可失败」的实证**。判据形态固定为三段：**① 注入**（制造一个该门应当捕获的缺陷）→ **② 观测**（命中 + 非零退出码，期望值**预登记**）→ **③ 精确还原**（`git diff` 为空 **且** 重跑回基线）。
  2. **每个检测维度各注入一次**——「某一维可失败」不蕴含「其余维可失败」；注入覆盖面 MUST 与门声称的检测维度清单对齐并显式声明未注入的维度（本轮未注入 = 命名一致性维 / DEAD 类注入 / 1.21.6 侧注入，均在 §5 如实声明）。
  3. **退出码是不可省的一项**：门的消费者是**机器**（CI / 批处理 / 下一轮自动化），只打印不退出等于没拦住——这与 #160（VOID/GATE 裁决必须非零退出断链）同源：**判据的可执行后果用退出码表达，不靠人盯守**。
  4. **注入式自证本身是一次 in-place 副作用，逆登记为必备项**（§9.8）：本轮登记的逆 = 备份件 `.tmp/b61-260917-06/bg-negtest-backup.gradle` + 还原后 `git diff` 为空实证 + git 本体可 revert；**测试脚本落唯一临时区 `.tmp/`（不入库）**，属 derived 天然合规。反模式 = 为测门而改被保护文件却**不留可寻址的逆**（下一次「绿」的语义即被污染）。
  5. **与 #163 的关系（明确分工，避免重复记）**：**#163 诊断**（「只判存在/数量的门恒绿」——识别问题），**本条开方**（「注入式负向测试」——固定的证明动作）。两条应合读：#163 说「全绿声明 MUST 同时声明门测的是什么」，本条补「且 MUST 给出该门可失败的实证」。
  6. **落地时机（与本工程 AGENTS.md 的接口）**：新增 / 修改门禁脚本、或门禁新增检测维度时，MUST 同批完成该维度的注入自证；门禁的「交付完成」定义包含「自证记录在案」——本轮实例即 `gate-negative-tests.md` 与门禁 per-version 修复（commit `0b0c7ac`）同批存在。

- **边界（idk / 覆盖面诚实声明）**：
  - **未跑 JVM 端到端**——注入后未实跑 `runServer` 观测行为差异，故分层为 **Partial**，**不得称 Full**；
  - **未测 1.21.6 侧的注入还原**；
  - **未测 DEAD 类注入**（DEAD 与 ORPHAN 共用集合运算路径，风险低——此为**判断**而非实测，属 idk）；
  - **未注入命名一致性维**（#19）。
- **家族索引**：**#163（silently-green 门——本条为其操作性补强：识别 → 证明动作）** / **#27（负向测试是断言生效的唯一证明，且其假阴性比假阳性更危险）** / #160（裁决/门必须以非零退出断链） / #118（自证行硬门——本条为「工具级自证」而非「运行臂自证」） / #167（逆登记 MUST NOT 伪造——本轮逆为备份件 + 双步验证，未伪造）。

---

### #178 输入 hash 不稳定 ≠ 序列化自由度（须内容级解码）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #178（A 类）

- **发现时间 / 发现者 / 置信度 / module**：2026-09-18（260918-05）；CoreSwap 主会话（排查 + judge C1-C3 闭合）+ knowledge subagent 起草；**candidate**（Full 分层：dump 逐字节分类 + palette/storage 解码 + enc 网格逐格还原 + C2 补 len-diff 类逐格直证；judge PASS-with-conditions C1-C3 已闭合；confirmed 留用户）；workflow-patterns / 差异机制判别法。
- **来源定位**：`.investigations/inputdiff23-260918-05/record-260918-05.md`（T1 三阶段分类收敛 + 机制定论）；判据预登记 `.investigations/inputdiff23-260918-05/criteria-260918-05.md`（T1 [DUMP-KINDS] 分类表）。
- **观察**：inputDiff23=46（跨重载输入 hash 差）按 dump 落段分出**三类**：len-diff 25 / sto-only 9 / pal+sto 12——按分类表字面读法正好对应三个互斥序列化自由度候选（空节翻转 / 位打包重排 / palette 序不稳定），触发判据 B「多类并存 MUST fan-out」。逐层下钻后**三类同源收敛**：① len-diff 细化 = empty2==empty3 全成立 → 排除空节翻转，真实形态 = psz 差 + bits 4→5 升级 = palette 条目集差；② enc 网格经各自 palette 还原后逐格比对 → palette 集合相同序不同 + 网格内容确有替换（C2 直证：len-diff 成员 31,-20 = stone→dirt ×29 / deepslate→granite ×20 / air→lava ×17）→ **全部三类都是「真实方块内容差」的下游表现**（palette 序/位流差随内容演化连带产生），非序列化层自由度。
- **判别法（可复用）**：**「跨重载不稳定」类差异的分辨必须逐层下钻到内容级，禁止在字节级分类层停留归因**。分层模板：
  1. **字节级分类**（diff 落段：meta/palette/storage——只产生候选方向，不产生结论）；
  2. **结构解码**（palette/storage 按 NBT 语义还原成条目集——排除「同字节异义」假类）；
  3. **内容级还原**（enc 网格经**各自 palette** 还原后逐格比——每侧用自己的 palette 解自己的位流，判「内容是否真变」的唯一裁决层）。
  表面多类（len-diff/sto-only/pal+sto）在第 3 层收敛为单一因果源头（内容演化）⇒ 互斥机制候选不存在，fan-out 靶对象消失（豁免形态见 #181）。**反模式**：把字节级分类的类数直接当互斥候选数。
- **家族索引**：**#179**（本条的机制面姊妹条——内容差的来源是探针瞬态读数，两条合读 = 判别法 + 因果源）；**#181**（多类并存 fan-out 豁免的收敛出口）；#46（跨实现序列化省略语义不对称——同为「序列化层差异误读」家族，#46 防缺键伪翻转、本条防字节级分类伪多类）。

---

### #180 探针差异集的空间坍缩（多 chunk 共享邻域读数）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #180（A 类）

- **观察**：inputDiff23=46 的 46 个 beta chunk，解码后实际只对应 **3 个唯一「邻 chunk-节」站点**——payload 是 3×3 邻域 × 24 节的读数，多个 beta chunk 共享同一邻 chunk 的同一节，逐 chunk 计数把同一物理站点重复计入。判据 = **邻域型探针的差异集先按唯一站点（邻 chunk 坐标 × 节坐标）去重再谈规模/覆盖面**，否则覆盖面声明（46 chunk 全覆盖 vs 3 站点全覆盖）失真。
- **判错经验**：结果集 21→3 的「丢项」排查中，邻域坐标换算（dz/dx 偏移含 -1）心算出错曾误判集合坍缩为缺陷——**坐标换算 MUST 先写公式再代入**（#23/#24 坐标语义家族的手算形态）。
- **来源定位**：`.investigations/inputdiff23-260918-05/record-260918-05.md` §T2 + §错误台账 3。置信度 candidate。

---

### #182 映射型校验器必须先验值域封闭性（未知值必须 FAIL）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #182（A 类）

- **发现时间 / 发现者 / 置信度 / module**：2026-09-18（260918-06）；CoreSwap 主会话 + knowledge subagent 起草；**candidate**（confirmed 留用户）；workflow-patterns / 门禁与校验器设计。
- **五段式（源 = `.investigations/b63-260918-06/b63-errors.md` E1）**：
  - **现象**：B6-3 比对器负向自检注入 `[LIGHT-PATH] path=ghost-path` 后仍输出 `[OK] ⊆ 声明`、rc=0——门禁判据「注入未知值必须 FAIL」首轮不成立，比对器对未知事件值结构性失明。
  - **根因（机制）**：比对器把「运行时事件 → 声明键」建模为**白名单别名表**（ALIASES）；未知事件值不命中任何别名 ⇒ 触达键集为空 ⇒ 与声明的差集恒空 ⇒ **恒 PASS**。「A=B 恒等不证分支生效」（#81 家族）的比对器形态：校验器的枚举覆盖面本身就是判据的一部分，值域封闭性未校验 ⇒ 校验器对枚举外的输入世界恒绿。
  - **定位**：按门禁纪律做负向测试（判别实验必须验证「自变量真被改变」，#20）时 rc=0 与预期 FAIL 矛盾；读 actual keys=0 定位到「未知值零键」路径。
  - **修复**：比对器加值域封闭校验——`path=`/`abi=` 提取值 ∉ KNOWN_VALUES 枚举 ⇒ 直接产出 `light:event.value:<unknown>:<值>` 键（必不在声明集内 ⇒ UNDECLARED ⇒ FAIL rc=1）；修复后负向 rc=1 / 正向 rc=0 双向复测通过（judge N2 亲手复跑实测注入 `path=legacymystery` → `[FAIL] UNDECLARED` rc=1）。
  - **教训（可复用判据）**：
    1. **「基于映射的校验器」必须先校验值域封闭性，再做映射判定**——白名单别名/事件→键归约器对枚举外世界恒绿 = **silently-green 门（#163）的运行时校验器形态**。
    2. **任何「事件→键」归约器的首条判据 = 未知值必须 FAIL**——负向测试用**枚举外值注入**，不是「已知值缺位」（后者只测漏报不测失明）。
    3. 归约器的**空集路径是恒绿通道**：归约为空键集时「差集为空 = PASS」逻辑失效，空集必须按「有未知输入」处理而非按「无违规」处理。
- **家族索引**：**#163**（silently-green 门本体，本条为其运行时校验器实例）；**#172**（门禁有效性注入式负向测试，本条为其归约器维实例）；**#81**（A=B 恒等不证生效——同根因家族比对器形态）；**#20**（判别实验自变量真被改变）；**#27**（断言生效唯一证明 = 负向测试且其假阴性比假阳性更危险）。
- **来源定位**：`.investigations/b63-260918-06/b63-errors.md` E1 + `.investigations/b63-260918-06/judge-review-260918-06.md` N2/N6/S1 + `.tmp/260918-06/b63_comparator.py`（KNOWN_VALUES 修复形态）。

---

### #183 「前提不可达」静态标注的机械化（事实封闭集+求值器+矛盾检查）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #183（A 类）

- **发现时间 / 发现者 / 置信度 / module**：2026-09-18（260918-07，B6-3 S4 能力演示）；CoreSwap 主会话 + knowledge subagent 起草；**confirmed**（用户授予 2026-09-18，260918-07 块内；judge PASS-with-conditions N1/N2 已应用）；workflow-patterns / 门禁与校验器设计（#182 同族续篇）。
- **观察**：B6-3 light 声明表对 17 个声明域做了「不可达」人工静态标注；judge S4 悬置其中「门控关闭不可达」类——机械检出能力未演示。v2 比对器（`.tmp/260918-07/b63_comparator_v2.py`）以三件套补齐：① **域级前提集**——每个声明域携带 `{key, expected, check}` 外部事实依赖（PRECONDS，缺省域挂总门 `light.rust.armed`，显式无前提域须逐域声明）；② **静态事实求值器**——事实来源双通道（log 行为化自证行 + env/JSON 显式覆盖，覆盖关系逐键标注输出），事实键**封闭集** 6 个，枚举外键 = UNKNOWN-FACT-KEY FAIL（#182 封闭性延续到事实侧）；③ **suspended + 触达矛盾语义**——前提失效域判 `[SUSPENDED]`（状态不自动变更），但**被证据触达的 suspended 域 = SUSPENDED-TOUCHED FAIL**（声明「不可达」与事实「已触达」矛盾 = 机械检出）。
- **证据**（四测预登记 + judge 复跑逐格一致，Partial 层）：POS rc=0（触达 8 ⊆ 声明 17，v1 基线无回归）；**NEG-C rc=0 / suspended 16/17 / touched 0——「生产 mask 下不可达」人工标注被机械复现**（逐键 + failed 前提三元组全量列出）；**NEG-A rc=1 / SUSPENDED-TOUCHED 7 键——该能力具矛盾判别力，非恒绿通道**；NEG-B rc=1（枚举外事实键）。judge PASS-with-conditions（N1 前提漏项 / N2 前提集自身封闭断言）已应用并四测复跑无回归。
- **边界（不外推，中价值简记并入）**：「门控关闭」形态之外仍需人工静态标注——**状态机不可达**（如源码注释自证的 mixin:644，非门控形态）与**结构性不可达**（bin-diag 不在默认构建产物）不在求值器域内；事实键封闭集随接管面扩面**必须先扩集再声明**（本轮仅 light 面封闭）。
- **如何利用（可复用判据）**：凡声明表/门禁携带「某条件下前提不可达」标注，其不可达性可用三件套机械化——封闭事实键集（枚举外即 FAIL，#182）→ 每域前提三元组求值 → 触达矛盾检查（不可达域被触达即机械 FAIL）。标注从「人工静态断言」升级为「负向测试可失败的机械判据」（NEG-A/C 双向堵死恒绿/恒红）；前提集自身也要封闭性断言（PRECONDS 键 ⊆ FACT_KEYS），防 `<missing>` 分支静默 suspended 旁路。
- **家族索引**：**#182**（值域封闭性——本条为其事实侧延续）；**#163**（silently-green 门——NEG-A/C 为其消除形态）；**#172**（注入式负向测试范式）；**#160**（退出码机械断链）。
- **来源定位**：`.investigations/b63-260918-07/record-260918-07.md` + `judge-review-260918-07.md`（§B suspended 语义 / §D N1）+ `.tmp/260918-07/b63_comparator_v2.py`（PRECONDS / evaluate_facts / check_preconds 段）。

---

### #186 措辞争议用发射面单轮实证闭合

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #186（A 类）

- **发现时间 / 发现者 / 置信度 / module**：2026-09-18（260918-09）；CoreSwap 主会话（发射面实测）+ knowledge subagent 起草；**confirmed（用户 2026-09-18 21:2x 拍板，260918-10 回写）**（同轮组内标定 E1 单轮直证 + 预登记判据全部满足无灰区）；workflow-patterns / 行为化验证方法（#170 第二例）+ 判据争议闭合（#184 续篇）。
- **来源定位**：`.investigations/b61-260918-09/record.md`（§2 实测表 / §3 裁决 / §4 §9.7 声明）；闭合对象 = `.investigations/b61-260918-08/record.md` §5.3（dissent 原文：豁免①「A/B 实验专用」扩展读法张力 + 发射面实测列为可选加固）。
- **观察（现象）**：#184 边界栏留有 dissent——bulkwb 本体豁免①依赖「扩展读法」，若按字面严格读可能落 DEFECT（届时仅豁免②缺省权威单腿）；判据文本「任一 vs 合读」措辞分歧亦在案。两方读法各自自洽，纯措辞辩论无裁决终点的迹象。
- **方法（为什么一轮直证能关闭读法分歧，可复用）**：读法分歧的前提是「字面严格读 → DEFECT」分支**可能为真**；该分支携带可观测行为推论（若真按 DEFECT 口径，`-Pbulkwb` 应有映射/应发射）。复用 #170 发射面直证法（init script 在 `runServer` `doFirst` 打印 `t.jvmArgs` 后抛 `StopExecutionException` 跳过服务器启动，12s、零 world/端口副作用、省去 kill java——**省成本哨兵形态**：打印观测点与 260917-06 各哨兵同位，本轮新变体）单轮实测：同轮组内标定（`-Pbulkwblog=1` → `-Dcoreswap.bulkwblog=1` **发射** = 仪器本轮自证有效）下，`-Pbulkwb=1` / `-Pskipair=1` 对应 `-D` **双双缺席** + argfile 复核无隐藏 `-D` + 静态面零映射三线一致 ⇒ 「`-P` 通道对本体消费点**结构性不存在**」——**先例不可跨消费点借用的判据（#184）不是读法分歧，而是发射面事实**；「字面严格读 → DEFECT」分支被行为证据封死（按 DEFECT 补映射 = 把 javadoc 未宣传的缺省权威 flag 改造成 `-P` 通道，恰是既有 confirmed 定性所排除的方向），dissent 关闭、无 §15.4 取代。
- **判据（可复用，MUST）**：
  1. **判据/豁免的措辞读法分歧，先查「分歧各分支是否携带互斥的可观测行为推论」**——有则一轮行为化直证（含同轮组内标定，#170）优先于继续措辞辩论；判据文本维护（如「任一 vs AND」统一）降级为独立低危事项，不再承重。
  2. **直证设计三要素**（本例预登记于 §2 表，执行前写死）：组内标定臂（仪器自证）+ 目标臂缺席观测 + 静态面/argfile 旁路排除；任一不满足 ⇒ 裁决改写并回 fan-out。
  3. **诚实边界**：发射面 = Partial（止于 `t.jvmArgs`，未跑 fork JVM 端到端消费；1.21.6 侧未实测，由门禁 wrapper 捕获面覆盖）——闭合「读法分歧」的直证无须端到端，但分层声明不可省。
- **工具注记（中价值，并入不单列）**：`StopExecutionException` 跳过 `runServer` action 的省成本哨兵形态——`doFirst` 打印发射面后即抛，服务器不启动（12s vs 完整 boot + kill java），无 world/端口副作用（§9.8 仅 gradle 缓存触碰，显式不可逆声明在案）；凡「只需看发射面/配置面、不需 fork JVM 行为」的 gradle 验证均可复用。
- **家族索引**：**#170**（发射面直证法——本条为其第二例复用 + 省成本哨兵变体载体）；**#184**（消费点切分判据——本条为其边界栏 dissent 的行为证据闭合回填，「判据事实化」形态）；**#171**（豁免子句合读——本条闭合其「扩展读法」张力点）；#178 家族精神（分歧的裁决层下钻——本条为「读法层分歧下钻到行为层」形态）。
- **§9.7 口径**：E1（同构建态同轮单变量组内差分）/ S = `t.jvmArgs` 发射面 / 载体 1.20.1 `:runServer`（gradle 8.13）/ Partial / 1.21.6 未跑面显式声明。

---

### #188 打点/判别数据通道必须覆盖全部执行形态

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #188（A 类）

- **发现时间**：260919-01（2026-09-19）
- **module**：workflow / light-domain A1 判别
- **现象**：260917-04 C6 A/B 中，预登记判别「fill+JNI 占比 <30% ⇒ A1 无显著改善」设计用 C6-D 臂内 lightTiming 数据，但 LIGHTPROBE-T per-chunk 计时打点**结构性只覆盖 legacy per-chunk 路径**——domain 臂（域批接管形态）0 行，判别数据通道缺失，正式判别不可达，只能降级声明（verdict-260917-04 §3），下一块（260919-01）整块补通道重采。
- **根因（机制）**：同一逻辑功能存在**多种执行形态**（legacy per-chunk / domain 域批）时，观测打点往往只挂在先实现/先验证的那条路径上；判据预登记时引用的「现成通道」默认了形态覆盖，未做「判据数据键 × 执行形态」覆盖核对——**打点在位 ≠ 判据可达**（260919-01 实测：同载体两臂，legacy 臂 LIGHTPROBE-T=18 行、domain 臂 0 行，通道覆盖完全不同）。
- **定位（怎么发现）**：判据预登记日做 SELFCERT 行为化自证项设计（#81 形态）——「域臂 [LIGHT-DOMAIN] task 行 ≥1」与「LIGHTPROBE-T ≥1」分臂正对照直接暴露 0 行缺口；log grep 计数即可机械发现。
- **修复**：260919-01 在域批任务体补三点计时（fill/native/wb，整块 LIGHT_TIMING 门控 + 行为化正/负对照：门开成功行必带字段、门关字段缺席），并把「判别行在位」写成 SELFCERT 硬门（成功行缺 fillMs= → 臂 VOID 非零退出，#160），正式判别一次通过（P50=0.9835 ≥30% 分支，verdict-260919-01 candidate）。
- **教训（可复用判据）**：
  1. **预登记判据时逐键核对数据通道的执行形态覆盖**：判据引用的每个数据键，回答「它覆盖哪些执行形态？待判形态在其中吗？」——答不出 = 判据 suspended 风险，先补打点再采集。
  2. 打点设计随架构 T1 做**形态覆盖清单**（legacy/domain/未来形态 × 通道键矩阵），不靠「现成通道」默认。
  3. 行为化正/负对照（门开字段必在 / 门关字段必缺）把「打点在位」变成自证硬门，缺位即 VOID 断链——比采集后发现通道缺失便宜一个数量级。
  4. 关联：#162「定性未抽样」是**消费侧**同族（引用通道数据前回原始日志抽样）；本条是**生产侧**前移（采集前核对通道覆盖）。#188 与 #162 合读 = 打点数据的「生产-消费」双侧检查。
- **家族索引**：#162（消费侧形态）、#118/#160（自证硬门 + VOID 断链）、#136（诊断门控整块化）、#81（行为化自证）。

---

### #189 分段打点的窗标签必须与代码括住的工作一致

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #189（A 类）

- **发现时间**：260919-02（2026-09-19）
- **module**：workflow / 性能测量口径（WG_LIGHTPHASE 打点）
- **现象**：第一版打点构建（dll 60abb61b）四臂数据中 `kernel_us` ≈ 86μs，而同 kernel 窗内各 phase 合计 ~23ms——`kernel_us ≪ Σphases`，子段之和远大于母段窗，物理不自洽。
- **根因（机制）**：插桩时窗标签（文档语义：「内核墙钟」）与计时变量实际括住的工作（代码事实：dp-t1 = outv 分配段）脱钩——标签写在打点行里，变量取在代码里，两者没有机械核对。
- **定位（怎么发现）**：数据自暴露——自洽 sanity（子段合计 ≤ 母段窗）一轮抓出；86μs 装不下 23ms 的 phases，矛盾显式到不需要任何工具。第一版四臂数据按 #144/#146 留档不进判定，修正后重编（f1d30ee9）重采。
- **修复**：修正计时窗 → 重编 → R2 四臂重采；判据前置集载明构建替换与读法（陈旧字面 sha 按前提集修正版读，判据冻结不改）。
- **教训（可复用判据）**：
  1. 分段打点**正式采集前** MUST 做自洽性 sanity：**子段合计 ≤ 母段窗、各段之和 ≈ 任务总量**——不自洽即停手修打点，不解读数据。
  2. 窗标签是文档语义、计时变量是代码事实，两者须在插桩 review 时逐窗核对（「这个变量真的括住标签说的那段工作吗」），不靠变量名直觉。
  3. 数据物理不自洽（子段>母段、段和≠总量）是打点层缺陷的最高信噪签名之一——先疑测量口径再疑被测对象。
- **家族索引**：#134（测量口径家族）、#144/#146（失败轮留档 + 禁自动回退）、#188（打点数据通道执行形态覆盖——生产侧姊妹条：#188 管「通道覆盖哪条路径」，本条管「窗内量的是不是标签说的工作」）。

---

### #192 占比门脚本化方向未取反（占比 vs 补数两义）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #192（A 类）

- **发现时间**：260919-03（2026-09-19）
- **module**：workflow / 判据脚本化转录
- **现象**：判据 M1 门原文「inline 回退占比 >30% ⇒ VOID」；采集脚本写成 `coverage > 0.30 → VOID`（coverage = packed 覆盖率 = 1 − 回退占比）。实测 coverage=0.9808（优秀）被判 VOID，触发假 VOID 复采一轮。
- **根因（机制）**：同一数字两义——判据侧的「占比」是回退占比（罚高值），脚本侧变量是补数（罚低值）；搬运时只对了阈值数字（30%↔0.30）未核语义方向，比较未取反。
- **定位（怎么发现）**：VOID 行门名与值并读不自洽（0.98>0.30 触发罚 = 罚错侧）；E1 错误链见 .investigations/a1-b2-260919-03/record-260919-03.md。
- **修复**：脚本改 `coverage < 0.70 VOID / 0.70–0.80 灰区` + 注释；onpk 留档换标签复采 onpk2（#144/#146）。verdict 补 packed_coverage 换算声明（judge S1）。
- **教训（可复用判据）**：
  1. 占比门入脚本 MUST 注释声明「罚哪一侧 + 阈值来自判据哪一行」；**变量是判据量的补数时方向取反最易错**（#90 转抄漂移的脚本形态）。
  2. 开采集前 MUST 用已知优秀值跑一遍**负向测试**（优秀值应 PASS、劣化值应 VOID）——门要能失败（#172）之外还要**罚对侧**；本次缺此步致一轮假 VOID 采集。
- **家族索引**：#90（转抄漂移）、#172（门要能失败——本条补方向正确性维）、#112（判据预登记）、#59（跨语言数值对拍格式差异——同族「形式对语义错」）。

---

### #194 CPU 总量收益 ≠ 关键路径收益

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #194（A 类）

- **发现时间**：260919-05（2026-09-19）
- **module**：workflow / 性能优化立项收益核算（并行任务关键路径面）
- **现象**：C-1a 共享 fill（全域 25 chunk 一趟替代 9 窗各自 fill）CPU 总量削减显著——fill 计算
  81→25 chunk（3.24×）；但端到端域批任务 wall 无实质改善：nativeMs P50 配对比 on1/off1 = 2.179/2.301 =
  **0.947（灰区 0.90-0.95）**、on2/off2 = 2.244/2.208 = **1.016（≥0.95 FAIL）**，两对方向不一致、均落
  run 间噪声带内（off1/off2 = 1.042，自身摆动 ~4%）。J4 性能主判据未满足，按预登记「不作为性能优化计入」。
- **根因（机制）**：共享 fill 消掉的是 **CPU 总量**，不是**关键路径**。旧路 fill = 9 窗各自 ~1.3ms 且
  与其它中心**并行**（关键路径只含一份窗 fill）；新路时序 = copyin(1.15ms) → **全域 fill 4.1ms 单线程
  串行前缀** → 各线程窗准备(1.8ms)+BFS/sky/export 并行——fill 从「并行摊薄的一份」变成「完整落在关键
  路径上的串行段」，串行化抵消了总量削减（phase 账自洽：kernel_us P50 ≈16.6ms vs wall ≈2.2ms，
  ΣCPU/wall ≈ 7.5，同 #107 尺子口径）。与 C-3「拷入降被窗内成本反超」（#191）同族：立项账列了
  消除侧/总量侧，漏了新增/串行化侧对 wall 的作用面。
- **定位（怎么发现）**：无关键路径独立探针，靠 **phase 账自洽**（ΣCPU/wall 比值 + 串行段位置）作机制
  解读——同批 LIGHTPHASE P50 逐段并读（copyin/fill/kernel vs nativeMs wall），共享化前后关键路径构成
  对比直接暴露串行前缀（qualitative 级，record §4 已按 §1.3 声明，judge M2 PASS）。
- **修复**：正确性面全绿（双种子位等价 J1 + 实机零 fallback/degraded + G3 收敛 changed=0/9450），
  代码保留缺省生效（用户拍板）；性能面按 verdict-260919-03 C-3 先例不计入优化收益。
- **教训（可复用判据）**：
  1. **性能优化立项前列账两栏：「CPU 总量面 / 关键路径面」**——域批/批处理任务中新增的串行段
     （单线程前缀/后缀）**直接进关键路径上墙**，总量削减倍数（3.24×）对 wall 收益无传递保证。
  2. 并行化改造的收益判据 MUST 用端到端 wall 配对比（本例 nativeMs P50 配对），不得用被优化段的
     CPU 总量削减作主判据（同 #191「效应代理 ≠ 同量工作」维）。
  3. **phase 账自洽（ΣCPU/wall 比值 + 串行段位置）可作无探针时的机制解读**——但属 qualitative 级
     （§1.3），引用前 MUST 声明「自洽推演、无独立关键路径探针」并重采样原始日志。
- **家族索引**：#191（消除侧/新增侧双侧列账——本条补「并行→串行位置变化」维，合读为立项核算完整
  清单）、#107（ΣCPU/wall 尺子）、C-3（verdict-260919-03，拷入降被窗内成本反超——同构家族）、
  #100（口径可比性）。

---

### #199 形态门判别器（band × interior 双阈值）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #199（A 类）

- **发现时间/发现者**：260919-08，core.worker（档②判别比较器 o1_o3_cmp.py）
- **观察**：档② C1 判别（O1 门）不比「差多少」，比「差在哪」——对两臂 region 光照 nibble 逐 section 求 diff，按几何位置分桶：边界带 vs 内部。读数：diff-nibbles=3,354,675，band=3,340,941（99.59%）≥80%，interior=13,734（0.41%）≤10% → 判据 §2.3 分支 A PASS（来源：.investigations/fix-term-260919-08/cmd-output/o1o3-r3r4-run.log L45-46；verdict-260919-08 §1）。形态与 .b5a 预测（vanilla 增量传播单步 ≤15 → 覆写限于边界带）一致、与「确定性差弥散/跨线程整窗」预测互斥 → 一个机械读数同时完成「支持甲 + 削弱乙 + 削弱 R6」三向判别（verdict §2/§5）。
- **判据/如何利用**：当互斥机制候选对「差异总量」预测相同（都预测有差）但对「差异的**空间/结构形态**」预测不同时，MUST 优先设计形态门（预登记分桶定义 + 双阈值 + 两分支读法写死）而非阈值门——形态维度比数值维度判别力高一个层级。配套：#112 读法预登记写死、#195 判据模板、#196 对照集（形态门同样可被对照集饱和击穿，主集预测须与候选预测互斥才有效）。Y 分布旁证（log L47：Y∈{0..10}∪{252..255} 两端集中）只作旁证不进门。
- **来源**：.artifacts/fix-term-260919-08/verdict-260919-08.md §1-§2、§5；.investigations/fix-term-260919-08/c1-criteria.md §2.3。

---

### #202 产物 sha 漂移连锁声明（下游前置全体失效面）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #202（A 类）

- **观察**：档③ E-3a 最小诊断打点（一个 if 块 + build.gradle 一行）改变 worldgen.dll 字节 → sha 从 cc4e39fe 漂移 → 下游所有以旧 sha 为前置的判据（两臂 SELFCERT 第 3 项等）全体 **premise-expired**（§15.1：前置失效 → suspended + 依赖者标 premise-expired，status 永不自动变更）。该连锁面被设计文档列为 B3 批次最大连锁项（design-260919-08 §3.2 / §5#8；b5 §1.6）。
- **判据**：任何改码动作（含纯诊断打点）落地前 MUST 盘点「以产物 sha/构建身份为 key 的前置集」并申报漂移连锁面；漂移登记 = 新 sha + 漂移原因 + premise-expired 依赖清单，随判据 artifact 一并预登记。与 #78 互补：#78 管**被动漂移**（release sha 非确定）的复核，本条管**主动改码**的前置申报。
- **来源**：design-260919-08.md §3.2、§5#8、§7 选项 B；judge-review-design M4。

---

### #203 前置 key 挂起排程（依赖未来判别）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #203（A 类）

FA-2（写回前重验）设计现在定稿，硬前置 = 档③ E-3a 判出「固化读法成立」（前置写成 `key=c1-e3a-verdict`，前置失效 → suspended，b4 §1-FA-2）；判别出结果即零延迟立项/零延迟弃案（design §3.2.1）。判据：依赖未来判别结果的方案项 MUST 以「设计定稿 + 前置 key 挂起」入库，而非「等结果再设计」（浪费一轮）或「不设前置直接排程」（违 §15.1 判据前置集）。来源：design-260919-08 §3.2；judge-review-design 候选 8。

### 【#150 补充案例（260919-08）】解蔽换形态实例

F-C-C3 解蔽 520 unlit → 「lit 且固化错值」（总错误不降仅换形态）与 F-A 值修复同批 + 唯一合规序 F-A 先 F-C 后。实例见 design-260919-08 §3.1 同批纪律四条（机制全在 #150 本条，此处只留实例指针）。

---

### #204 「值收敛 ≠ 过程确定性」（贴参考实现可放大方差）

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #204（A 类）

- **现象（具体读数）**：B1 主攻包（FA-1+FA-3+FB-2+C3）keep-world n=2 三臂验收（verdict-260919-09）：J1 存在性差 PASS（520 unlit → **0**，两 fix 臂 snap 9450/9450 common、new=0 gone=0）；但 J2 **VOID**——f1×f2 run 间 jitter **6453 → 7660 sections（+18.7%）**、diff-nibbles **3,354,675 → 4,266,861（+27.2%）**；judge 独立复算 chunk 级 f1×f2 值差 **2643 > 2185**，双口径同证 VOID。FB-2（写回后补 propagateLight，使 chunk 边界进入 vanilla 增量传播体系）的「vanilla 原生收敛」预期未兑现为抖动收敛，反而扩张了 run 间非确定面——设计预期的方向**反了**。
- **根因（机制层面）**：预登记判据隐含了「更贴 vanilla 机制 = 更收敛」的直觉等式，但该等式混淆了两个独立轴：**值收敛**（终态值是否对齐 vanilla）与**过程确定性**（多次 run 是否产出同一过程结果）。FB-2 把 chunk 边界从「我方一次性定值」搬进 vanilla 的增量传播体系后，传播的**消化次序/排程**成为 run 级非确定域——每次 run 以不同次序消化传播任务，边界带值差面随之扩张。补的机制本身越「原生」，纳入非确定排程体系的面越大，方差可能被**系统性放大**而非缩小。机制存在性（J4/J5 行为化自证在案）与针对性论断（b2 §2「确定性收敛」）在运行时证据下分离：#201 的三级分账里，② 静态针对性推理被 ③ 运行时 A/B **反向削弱**。
- **定位（怎么发现）**：keep-world n=2 双臂对拍（o1_o3_cmp.py，§9.7 同口径 6453 vs 7660）+ judge 独立复算 chunk 级双口径同证（2643>2185）；O1 形态门机械 PASS（band 99.57%/interior 0.43%）但「门过了总量涨了」即信号——形态没变、量级恶化，说明机制在跑但引入了新非确定源。判据读法注意（judge C-2）：预登记阈值 chunk 级（2185）× 比较器 section 级，口径混写；替代执行必须**同口径替代 + 独立复算双口径同证**，且 verdict 表述须如实为「同口径替代执行」而非「预登记读法机械执行」（口径裁决本身要留痕）。
- **修复（本例处置）**：J2 VOID 触发 PI-1 断链（不自动重跑不自动回退）；FB-2 去留三选项（回退半包 / 档③先判别 / 接受抖动换存在性）留用户拍板，不自动选向。FB-2 设计为「删行即回退、无开关」，回退成本极低——立项时「更贴 vanilla 类修复」默认配低回退成本形态，被本例证明是正确前置。
- **教训（可复用判据）**：① 修复预期立项时 MUST 分「值收敛」与「过程确定性」两轴各自预登记判据——两轴无蕴含关系；「使 X 更贴 vanilla/原生机制」类方案的预期论证，必须回答「该机制内部是否存在 run 级非确定排程/消化次序依赖」，有则「贴原版」本身可放大方差。② 「形态门 PASS + 总量恶化」= 新非确定源签名——形态不变量级变差时先查「新纳入体系的面是否引入排程依赖」，不要按「机制没生效」方向排查。③ 预登记判据口径必须单值化（chunk 级阈值配 chunk 级比较器）；口径混写时的合规替代形态 = 同口径替代基线 + judge 独立复算第二口径，双口径同证才算稳健（本例 VOID 在两口径下均成立，结论未因口径错误翻向）。
- **次级发现（简记，同块）**：
  - **access widener 与 yarn 文本源的嵌套类型访问控制不符**：mapped jar 中嵌套 enum（SLP `Stage`）对非 nest-mate = **private**，yarn 文本源显示包私有——文本源与 jar 实际访问控制不一致，@Invoker 编译期否决（f5-bugs #5 家族「引用源码树参照前核版本」的访问控制维）。**AW（Fabric access widener）是 remap 安全替代**（加宽 Stage 类 + enqueue 4 参方法）；已知边界：Forge+Connector 载体对 AW 的应用未验证（未加宽将 loud IllegalAccessError，非静默，可判别）。教训：mixin accessor 立项前对嵌套类型 MUST 先核 mapped jar 实际访问控制，勿信文本源可见性；方案预检一编即知（compileJava 一轮）。
  - **门禁字符类缺连字符**：check_switch_mapping.py RE_VMARG 不含 `-` → `-D` 名带连字符时声明面截断 ORPHAN 误报（首碰撞 post-finalize）；#163/#156 家族 coverage 形态。修复 = 字符类补 `-`（:74，逆 = 单行 revert）。
- **家族索引**：#201（三级分账——本条为「② 被③反向削弱」首例）、#197（集合恒定 ≠ 值恒定，同「两轴分离」精神）、#67（vanilla features 固有 run 级非确定——传播体系同族非确定源）、#112/#195（判据读法/口径预登记）、#162（无效声明清单）。来源：`.artifacts/fix-term-260919-09/verdict-260919-09.md` + `.investigations/fix-term-260919-09/record-260919-09.md` §6.1 + `review-260919-09-judge.md` #4/#10。candidate。

---

### #209 交集 = 各自大小 ⇒ 集合恒等

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #209（A 类）

- **发现时间/置信度/module**：2026-09-20（260920-03）；**candidate**（judge PASS-with-conditions 已应用；confirmed 留用户）；workflow-patterns / 集合比较证据分级（#162 对偶面，简记）。
- **来源定位**：`.investigations/k2-520-260920-02/t2t3-archive-recompute-260920-03.md` §T2 + 机械读数 `cmd-output/t8_key_membership_260920-03.log`；实例 = t8 三 dump（kd2=kd3=kv=vanilla-r1）key 集：|A|=|B|=|C|=|A∩B∩C|=9450 ⇒ 三集合恒等直接证明。
- **观察/方法**：#162 立了「计数恒等 ≠ 集合恒等」的无效声明红线；本条补其**零成本正向升级**：比较时同时输出**交集大小**——`|交集| == 各自大小` 时集合恒等是**直接证明**（非仅计数证据），成本只多一个 intersection 调用。同批读数：520/520 缺席 chunk 在三 dump 中均 lit（'111'）含 bbox 外 198，kv-only = 0——「南侧成员为 t8 驱动延伸区独有 key」候选被证伪（跨 run/workload 载体差归因，#132 家族）。
- **判据**：跨 dump 集合比较的输出 MUST 至少含 `各集大小 + 交集大小` 两行——两行相等即集合恒等（直接证明级）；不相等时才回退到差集清单。只报各集大小相等而不报交集 = 证据强度自降一档仍按恒等引用 = #162 违例。
- **家族索引**：**#162**（计数恒等 ≠ 集合恒等——本条为其「满足何条件时升格为集合恒等」的操作化对偶面）/ #139②（计数载体切分——同族口径面）。

---

### #212 引用机械产出须逐字对原文 + 分账和=总数自检

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #212（A 类）

- **发现时间/发现者/置信度/module**：2026-09-20（260920-05）；judge N3 MUST 抓出 + verdict/record 双处勘误（已应用）+ knowledge subagent 草稿；**candidate**（勘误不影响判读，confirmed 留用户）；workflow-patterns / 证据转引卫生（#90 家族新位形）。
- **来源定位**：`.artifacts/k2a-fullcov-260920-05/verdict-260920-05.md` §4（勘误后版本）+ judge-review N3 + `.tmp/k2a-260920-05/d1-recompute-out.log:16/:20`（机械原文 `rest=180`）。
- **现象（五段式）**：
  - **现象**：verdict 初稿 §4 子组表写「其余 179（相应差 1）」并声称 198+143+179=520 平移关系；其自己引用的复算产物 d1-recompute-out.log 两处均为 `rest=180`，198+143+180=**521**>520。
  - **根因（机制）**：① 转引自家产物时按「总数 520」反推凑数（179=520−198−143），而非引用产物原文——**分账和≠总数时的正确反应是怀疑划分不交性，不是抹平差 1**；② z=188 带（143，cz==188 精确口径）与框外（198）有 **1 个交点**——三子组是**非不交划分**，和必然 > 520；record 的 142 系 verify_design `zline188_in=142` 框内口径被误标「含框外」（比较器 h1_h2.zline188.members=143 互证全含口径）。
  - **定位（怎么发现）**：judge 独立复算比对 d1-recompute-out.log 原文行号（:16/:20 均 rest=180）+ 划分交集检查——「引用数字与所引产物逐字一致性」审查直接命中。
  - **修复**：verdict §4 按机械值改 143/180 + 显式声明三组非不交划分（交 1 点，521>520）+ record 口径误标勘误登记；三组恢复率任意口径均 1.000，判读不受影响。
  - **教训（可复用判据）**：① **引用机械产出 MUST 逐字引产物原文数字，禁按总数反推/凑平**——「和≠总数」先查划分不交性（非不交划分 MUST 显式声明交集大小），#90 转引错家族的「自家产物」位形：离源越近越易失防；② 引用前后自检「分账和 vs 总数」恒等式，不等即停手对账，禁止静默抹差；③ 同一计数多口径并存时（框内 142 / 全含 143）引用 MUST 带口径限定词。
- **家族索引**：#90（交接转抄漂移——本条为其「转引自家 freshly-generated 产物」新位形）/ #139③（汇总数字回底本复算）/ #23（分解数据每行进证据包）/ #175（机械清单否决转述清单）。

---

### #214 混杂变量须补「效应方向」论证

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #214（A 类）

- **发现时间/发现者/置信度/module**：2026-09-20（260920-05）；design §6 R1 预登记 + verdict §6 如实分析 + judge N4 PASS 复核 + knowledge subagent 草稿；**candidate**（confirmed 留用户）；workflow-patterns / 判别实验混杂处理（#16 对照归因、#68 双通道分解家族）。
- **来源定位**：`.artifacts/k2a-fullcov-260920-05/verdict-260920-05.md` §5/§6 + design-260920-05 §6 R1。
- **观察（现象）**：D-Lag 变体把上臂嫌疑机制（摘票→卸载竞态）回注进判别臂——design 预登记「D1 读数带混杂标注，judge 复核权重降档」。实测 ρ=1.0（520/520 全恢复，逐 chunk ev=wb 行机械复算）后的问题：混杂是否侵蚀读数？**方向性论证成立**：卸载竞态的机制通道（摘票→chunk 卸载→light 之前终止）只能**制造缺席**（wb 行消失），不可能**消灭缺席**；本臂缺席集反而清零（∅ vs 520）——混杂变量只能把 ρ 往低推，**ρ=1.0 是混杂作用下的下界通过**；不存在「lag2 制造假恢复」的通道（恢复证据 = 逐 chunk 实际存在的 ev=wb 行 + N520 全在终态 lit snapshot，观测事实非推断）。配套 D2' 竞态分账：资格丧失类 + UNKNOWN 全零（[WBQ-SUM] 原文逐字机械复核）⇒ 无 GRACE 压缩竞态证据。
- **判据（可复用）**：
  1. **预登记混杂变量时 MUST 附「效应方向」论证**：问一句「混杂若起作用，会把读数往哪个方向推」——混杂方向与实测信号**反向**（本例：混杂只会压低 ρ）则读数效力不降（下界通过）；**同向**（混杂能制造同形信号）才须降权/加对照臂。
  2. **方向性论证的前提是恢复/信号证据为逐点观测事实**（ev=wb 行实际存在），非统计推断——推断型读数无「通道不可能」可论证。
  3. **残余混杂面仍诚实登记**（本例：lag2 滞留窗内「点亮后摘票」时序不可排除，但其正是判别所欲的「覆盖⇒light 被调」，不构成反向解释）——方向性论证不豁免残余面登记。
  4. 混杂标注与方向性结论**并存不互删**：D1 读数保留「含卸载竞态混杂」预登记标注，judge 权重可据方向性分析回升半档（最终权重 judge 定）。
- **家族索引**：#16（对照基线归因——本条为其「混杂方向」预登记维）/ #68（两通道未分解禁单通道归因）/ #24（顺序效应假交互）/ #195（判据预登记）。

---

### #216 「等待窗口」参数只在持续零散触发形态暴露

> 出处：CoreSwap `knowledge/discovered/workflow-patterns.md` · 发现 #216（A 类）

- **时间/置信度/module**：260921-03；candidate（E1 多臂 + stallwatch 栈级证据 + 恢复臂；judge PASS-with-conditions M1/M2/N1-N3 条件已应用，confirmed 留用户）；workflow-patterns / 验证域覆盖面（#82 家族）。

**观察**：光照域批（LIGHT-DOMAIN）的 grace 窗缺省 10000ms——该参数下域批任务在窗口期内不 seal，chunk 光照 future 不完成、chunk 无法 FULL。260914-04 e2e 判据（boot 预生成 wall）**测不出它**：boot 时任务洪峰一次灌满，grace 一次性摊销，wall 差异被淹没。而实机跑图前沿形态（玩家走图持续零散触发）下，每个零散批各吃一个完整 grace 窗 → 前沿区块完成被拖 ≥10s/批，阻塞式消费者（forceload 命令 / 玩家区块发送）全被拖死，帧率正常但「跑图慢到不可用」。三臂实测（同 dll sha cc4e39fe，E1）：A=现役 lightRust+domainbatch 命令阻塞 10-41s/条、144 chunk 至 t+98s；B=仅 lightRust ≤ t+19.3s；C=vanilla 光照 ≤ t+19.6s；F=仅改 grace 250 → 命令 0.5-2.4s、144 ≤ t+20.5s（与 B/C 持平，域批机制保留）。

**证据**：① stallwatch dump 连续 6 次（20:02:58-20:04:14）同栈：主线程 park 于 `ForceLoadCommand.executeChange → ServerWorld.setChunkForced → World.getChunk → ServerChunkManager.getChunk → ThreadExecutor.runTasks`；② A 臂域任务 avgMs 仅 3-25ms（执行不慢）但全部 timedOut、timeout 19→65 单调爬升 = 滞留在等待窗口而非执行慢；③ F 臂单变量（grace 10000→250）恢复持平 = 归因闭合。来源：`.investigations/lane-starvation-260921-03/record-260921-03.md`；日志 `.tmp/lane-260921-03/arm-*.log`。

**如何利用（判据）**：
1. **调度型优化（合批/grace/延迟窗口类）引入的缺省达秒级「等待窗口」参数，其验证载体 MUST 覆盖「持续零散触发」形态**——boot 洪峰载体上窗口被一次性摊销、结构性不可见；「验证域覆盖 = 触发形态 × 时间粒度」（#82 覆盖面判据的触发形态维度）。新调度参数上线前问一句：「用户慢触发形态下，每个触发各吃多长窗口？」
2. **stallwatch dump 一轮定位主线程阻塞点的实战形态**：给阻塞臂加周期 dump（本块 15s 间隔），连续 ≥2 次 dump 同栈即非瞬态阻塞；栈直接给出「谁在 park 等谁」，配合一臂单变量开关即可闭合归因——成本远低于日志计数器推理。
3. **grace 类延迟参数的复测口径必须含「每 chunk 完成延迟」**（前沿触发到 chunk FULL 的延迟），不能只看 boot wall——wall 是吞吐摊销口径，会掩盖逐批等待窗口（同 #83 分母分场景、AGENTS「吞吐均值 vs 每 chunk 耗时混淆」同族）。

**家族索引**：#82（验证域覆盖面——本条为其「触发形态」维度实例）；#83（分母分场景）；#80（验证载体时序判据）。

---

### #10 thread_local 缓存与「每 chunk 跨线程」执行模型冲突 → 命中率归零

> 出处：CoreSwap `knowledge/discovered/algorithm-fingerprints.md` · 发现 #10（A 类）

**发现时间:** 2026-08-11（2026-08-12 根因定论确认）
**发现者:** worker（perf-rework 性能回归调查）
**来源定位:** MC 1.20.1 主世界密度求值缓存（versions/1.20.1/docs/07-block-pipeline.md 2026-08-06 纯算法优化链 FlatCache/Cache2D）+ `.investigations/perf-rework/`（WG_PROFILE/WG_SPLINEDEBUG 实测 2026-08-11/08-12）
**置信度:** confirmed（机制已 WG_PROFILE/WG_SPLINEDEBUG 实测坐实；2026-08-12 根因定论经 judge 通过 + 用户拍板；2026-08-12 修复闭环验证达标（rebuild 216=6.0/chunk、覆盖 36）+ judge 通过 + 用户验收）
**module:** perf

> **2026-08-12 修正（judge 审查要点 4 + 主因升级）**：08-11 实测（rebuild 438,092 / spline 单次 20,598ns）与 08-12 实测（rebuild 36,252 / 单次 1,714ns）差异巨大——两轮测量口径不同（多线程 thrashing 环境粗计数器 vs 单线程精确统计），见「观察」节口径说明；核心指纹结论不变，叠加因素升级为主因机制（H2），见「主因机制」节。

#### 观察
性能优化常引入「局部缓存」把重复计算降为 O(1)（如 8/6 把 spline 采样 34900 → 6250 次/chunk，靠 FlatCache 5×5 网格 + Cache2D 列缓存）。**这类缓存的收益依赖「缓存生命周期 ⊇ 重复访问窗口」**：

- 原设计假设（8/6，单线程串行）：同一 chunk 生成期间大量 spline 采样重复 → per-instance（per-DensityFunction）**thread_local** 缓存命中。
- 当执行模型变为「线程池并行消费 chunk 任务」（每 chunk 可能由不同线程处理、线程跨 chunk 迁移）时，thread_local 缓存与 chunk 生命周期**不匹配**：每线程独立缓存 → 每 chunk 首访即 miss → 命中率归零 → 每次访问都走完整重建路径。

**指纹信号**：缓存重建/失效计数 ≈ 缓存访问总数（命中率≈0），且原 O(1) 路径变成重建热点（单次成本放大一个量级）；伴随「多线程不加速甚至反降」（并行只放大重建并发，不摊薄重复访问）。本次实测（2026-08-11，多线程 8/22 线程 thrashing 环境下计数器）：FlatCache rebuild 438,092 ≈ spline 调用数、Cache2D miss 458,281 次、spline 单次 992ns → 20,598ns、density 阶段 8.5-11.7ms → 670-1000ms/chunk——正是此指纹。

**08-11 vs 08-12 口径说明（judge 审查要点 4）**：两个测量口径不同，不构成矛盾——
- **08-11**：多线程（8/22 线程）thrashing 环境下的粗粒度计数器。每 chunk 跨线程迁移 → 单槽缓存全 miss + 多线程重建并发 → rebuild 计数 ≈ spline 调用数（命中率≈0 的表象）、spline 单次被 thrashing 放大到 20,598ns。
- **08-12**：单线程（-threads 1）WG_SPLINEDEBUG 精确统计，剥离 thrashing 后暴露真实主因结构：rebuild 36,252 次 = 每 chunk ~1007（期望 ~6）→ **168×**；rebuild 仅占 spline 调用（4,695,145 = 130,420/chunk）的 **0.77%**；spline 单次 t1 1,714ns（mt 27,155ns，16× thrashing）。
- **核心结论不变**：thread_local 单槽缓存 vs 跨线程执行模型失配。08-12 数据把放大链精确化为「rebuild 168× × 13.36 spline/miss」的级联（而非 08-11 表象的「rebuild ≈ 访问总数」）。

**主因机制（2026-08-12 定论，H2 新指纹）**：FlatCache 网格构建含**嵌套采样递归**。buildGrid 角点 `i=4`/`j=4` 时 `p.x=(chunkX*4+4)*4=(chunkX+1)*16` 指向**下一 chunk 首列** → 嵌套 spline（continents/erosion/ridges 的 locationFunction FlatCache）收到**邻居 chunk key**（key=(x>>4,z>>4) chunk 级）→ 单槽缓存被污染 → 重建邻居网格 → 递归蔓延（实测 112 chunk = 36 生成 + 76 邻居，含左下对角 (44,-28)）→ rebuild 36,252 = 每 chunk ~1007 vs 期望 ~6（**168×**）→ spline 调用 20× 爆炸（130,420/chunk vs 旧 6,250）。

**H2 指纹信号**：缓存 key 由采样坐标派生（chunk 级），而采样点存在**越出当前上下文范围的角点**（buildGrid i=4/j=4）时，单槽缓存必然收到非本 chunk key → miss + 重建 + 递归蔓延。排查特征 = 重建计数的 chunk 覆盖**超出生成范围**（112 = 36+76 邻居）。**修复（2026-08-12 已实施并闭环）= 当前 chunk 上下文绑定**：thread_local `g_curChunkX/Z` 绑定当前生成 chunk（fillOneChunkCore 入口 RAII 设置、返回恢复 `INT32_MIN`），k/l 相对 startBiomeX 计算，越界 → `delegate.sample(pos)` **直算不重建**——即 Java per-chunk 实例语义（ChunkNoiseSampler.java L836-881：构造时预计算 25 角点、之后纯查表、永不构建邻居网格）的 C++ 模拟。**关键教训：per-chunk 多槽 LRU 不足以根除**（初版 16 槽 LRU 仍为 pos 推导的邻居 key 构建网格，rebuild 仅 36,252→7,318，覆盖仍 112）——必须消除「越界→重建」语义本身；**改循环顺序无效**（块级不触发 spline，H1 非主因）。

#### 证据
- WG_PROFILE（2026-08-11，density 阶段，多线程 thrashing 环境）：spline 单次 992ns → 20,598ns；spline.sample 338 万次；FlatCache rebuild 438,092 次 ≈ spline 调用数；Cache2D miss 458,281 次；density 阶段 670-1000ms/chunk（旧 8.5-11.7ms）
- WG_PROFILE/WG_SPLINEDEBUG（2026-08-12，单线程 -threads 1 精确统计）：spline 4,695,145 次（130,420/chunk，旧 6,250 → **20×**）；FlatCache rebuild **36,252** 次 / 112 chunk（每 chunk ~1007，期望 ~6 → **168×**）；CACHE2D miss 351,536 次（4 个 cacheId，= 14,061 rebuild × 25 角点 ✓）；spline 单次 t1 **1,714ns** / mt **27,155ns**（**16×** thrashing）；放大链 = rebuild 168× × 13.36 spline/miss ✓
- 修复后验证（2026-08-12 终版 ctx，数据 `.investigations/perf-rework/cmd-output/`）：FLATCACHE rebuild **216 = 6.0/chunk**（期望 ~6 完全达标）、覆盖 **36**（蔓延根除）；CACHE2D miss **23,117**（旧 351,536）；SPLINE **3,032/chunk**（SPLINEDEBUG 非 leaf 口径，旧 66,682，回旧基线 6,250 水平；WG_PROFILE 全量 spline.sample **5,906/chunk**）；单线程 wall 6,533→**2,910ms**（2.2×）；bench 单线程 **62.38ms/chunk**（旧 ~181，3×）；8576 **99.9994%** / 3200 **99.9997%** 零退化
- 初版 16 槽 LRU 对照（已弃用）：rebuild 36,252→7,318（203/chunk）、覆盖仍 112（splinedebug_8576_t1_fixed.txt）——多槽只降频率不除「越界→重建」语义
- 吞吐（SURFACE）：07 篇旧基线串行 28.1ms/chunk、并行 49.4ms/16chunk（3.1ms/chunk）→ 2026-08-11 实测单线程 98-182ms/chunk、多线程（8/22）108-239ms/chunk **无加速反降**
- 对照实验排除「本次改造引入」：stash 本次改动（Java 桥重写 + C++ 池改造）后 HEAD 版 block_probe 8×8 仍 10.2s；07 篇基线提交 86e4057 也要 8s → 回归在 8/6 优化链之后积累
- 数据载体：`.investigations/perf-rework/`（requirements-doc.md / static-audit.md / architecture.md / random-seed-sampling.md）+ 10 时间线 2026-08-11 条目 + 07 篇「性能回归实测」小节草稿

#### 如何利用
- **设计缓存前先明确「缓存生命周期 vs 执行模型」是否匹配**：thread_local 只适合「线程内连续消费同一上下文」（如单线程完整生成一个 chunk）；线程池并行 + 任务迁移时，用 **per-chunk 键索引缓存**（缓存随 chunk 生命周期）或按调用上下文显式传入，**不要依赖线程亲和**
- **性能回归排查第一手段 = 缓存计数器**：看 rebuild/miss 与命中之比；命中率≈0 即缓存失效（本次正是靠 WG_PROFILE 计数器坐实）
- **优化计数器要结合真实执行模型验证**：8/6 的 spline 34900 → 6250 次/chunk 是单线程串行模型下的计数，未覆盖多线程并行/线程迁移——「优化后计数器下降」不等于「目标执行模型下收益」
- **git 二分定位引入点**：stash/checkout 旧提交对照（本次 8s 级退化用 stash 实验证明非本次引入，具体引入提交待二分）
- **越界角点指纹（H2，2026-08-12 定论，修复已闭环）**：缓存 key 由采样坐标派生（如 `(x>>4,z>>4)` chunk 级）且采样点可能越出当前上下文范围（buildGrid 角点 i=4 → 下一 chunk 首列）时，单槽缓存必然被邻居 key 污染 → 递归重建蔓延。排查 = 检查重建计数的 chunk 覆盖是否超出生成范围（本次 112 chunk = 36 生成 + 76 邻居实锤）；**修复 = 当前 chunk 上下文绑定**（thread_local 显式传入当前 chunk 键 + 越界直算不重建，模拟 Java per-chunk 实例语义；实测 rebuild 216=6.0/chunk、覆盖 36）——**多槽 LRU 不够**（本次初版 16 槽 LRU 仍为邻居 key 建网格、覆盖仍 112），必须消除「越界→重建」语义
- 跨版本/跨项目通用：任何「局部缓存 + 并行执行」组合都适用此检查

---

### #11 spline 树扁平化（递归 shared_ptr 树 → 连续数组 + 非虚采样）

> 出处：CoreSwap `knowledge/discovered/algorithm-fingerprints.md` · 发现 #11（A 类）

**发现时间:** 2026-08-13
**发现者:** worker（perf-rework 无损优化 Phase 1）
**来源定位:** C++ `versions/1.20.1/cpp/worldgen/src/density.h`（SplineDF → 连续 nodes[]/locations[]/derivatives[]/subIdx[] + sampleNode）+ `.investigations/perf-rework/`（phase1-design.md / review-aae119d.md）
**置信度:** candidate（实测单线程 -24% + judge 逐行核对 Hermite 公式逐位等价 + 零退化落盘；多线程课题未闭合）
**module:** perf

#### 观察
MC 密度函数的 SplineDF（spline 节点）原生是「递归 shared_ptr 子节点树 + 虚调用采样」：每次 `apply` 经 `locationFunction->sample`（虚调用）→ 二分查 locations → `subSplines[k]->sample`（虚调用递归嵌套）→ Hermite 插值，每层 2 次虚指针间接跳转 + 二分，cache miss 高。

扁平化把递归树展开为连续节点数组（nodes/locations/derivatives/subIdx/locationFunctions 池）+ 整数索引，采样改为非虚递归 `sampleNode`。Hermite 插值公式（`lerp(kd,nv,ov)+kd(1-kd)lerp(kd,p,q)`）逐位不变。

**实测**：单线程 density wall 61.7→47.1ms（-23.7%）、吞吐 92.08→71.68ms/chunk（-22.2%）；零退化 8576 99.9994% / 3200 99.9997%。

**关键边界**：扁平化只解决 spline 子树自身的间接寻址 cache miss。多线程 8t 下 density 460.8→478.3ms **不改善**——多线程膨胀根因在 InterpolatedDF::buildGrid 的 1225 角点树遍历**整体**（spline 递归 + FlatCache 查表 + noise 的 cache miss 叠加），不在 spline 递归这一层。要改善多线程 latency 需 **DFC（整个 DF 树扁平化）**，非仅 spline 子树。

#### 证据
- `analyze_stagetimer.py` 现场复跑（n=128）：phase0_baseline density median 61.7 / phase1_splineflat 47.1；[A] threads=1 92.08→71.68
- `regress_8576_aae119d.txt` 3538922/3538944（99.9994%）、`regress_3200_aae119d.txt` 1572860/1572864（99.9997%）零退化
- 8t density median：phase0 460.8 → phase1 478.3（不降反略升，未兑现 phase0-quantify 的「10× 膨胀有望大幅回落」预估）
- judge review-aae119d.md 要点 1：Hermite 公式逐位等价（含 n==1/i<0/i==n−1/min-max 全边界）

#### 如何利用
- 复刻/优化 MC density 树的 spline 时，优先把「递归指针子节点 + 虚调用采样」扁平化为连续数组 + 整数索引 + 非虚采样：单线程 cache miss 立减，收益大且零退化可保（纯布局重排，采样公式逐位不变）。
- 但**别指望子树扁平化解决多线程 latency-bound**：先定位耗时大头在哪一层（用 WG_PROFILE/临时计数器拆 buildGrid 角点采样 vs 块级插值），若大头是「上层树遍历触发 + 多层 cache miss 叠加」（如 InterpolatedDF::buildGrid 1225 角点 × arg->sample），则需整个 DF 树扁平化（DFC）而非局部子树。
- 通用规律：指针链深递归 + 每层虚调用的数据结构，扁平化是低风险高收益的无损优化；但收益上限受「遍历触发点是否集中在该结构」约束——若遍历大头是调用方触发的多层组合，单层扁平化收益有限。

---

### #12 边界角点复用收益小的根因（缓存构建触发点不集中）

> 出处：CoreSwap `knowledge/discovered/algorithm-fingerprints.md` · 发现 #12（A 类）

**发现时间:** 2026-08-13
**发现者:** worker（perf-rework 无损优化 Phase 2）
**来源定位:** C++ `versions/1.20.1/cpp/worldgen/src/density.h`（InterpolatedDF::buildGrid 1225 角点 / FlatCacheDF::buildGrid 5×5=25 角点）+ `.investigations/perf-rework/`（review-aae119d-followup.md §3）
**置信度:** candidate（实测 -1.7% 收益坐实 + 根因机制推演）
**module:** perf

#### 观察
InterpolatedDF 网格 x/z 边界角点（gx=0 列 = 左邻 gx=4 列）与相邻 chunk 坐标重合，phase1-design 预估「x/z 双向边界复用可减 -36% buildGrid 采样 → -28% density」。但实测只做 x 方向左邻列复用（上限 245/1225=20%），density 47.1→46.3ms（-1.7% 接近噪声）、吞吐 71.68→72.06（+0.5% 无改善）。

**根因**：InterpolatedDF::buildGrid 的 1225 角点采样耗时大头**不集中在可跳过的边界角点**，而在「每 chunk 每实例 1 次的 FlatCache buildGrid 构建触发」+「spline 树遍历」：
- FlatCache buildGrid 只在**首个角点**触发一次（其后 24 角点查表命中），跳过 gx=0 列只是把首次触发从 gx=0 移到 gx=1，**省不了这次触发**；
- gx=0 列其余 244 角点是 FlatCache 查表命中（快），跳过省不了多少。

即：边界复用优化了「角点采样次数」这个**错误目标**——真正的耗时是「树遍历触发点」而非「角点数量」。

#### 证据
- 实测：phase2_edgereuse density median 46.3（vs phase1 47.1，-0.8ms）、[A] threads=1 72.06（vs 71.68，+0.5%）——端到端总 wall 反升
- review-aae119d.md 要点 2/3：实现只做 x 方向左邻列（非 x/z 双向）；density -0.8ms 在 min-max 波动（±38ms）内
- review-aae119d-followup.md §3：根因 = FlatCache buildGrid 只在首个角点触发一次，gx=0 列其余 244 角点查表命中

#### 如何利用
- 优化「重复采样」前先拆「每次采样的成本构成」：若某采样点集里只有**首次**采样触发昂贵构建、其余是便宜查表命中，则「减少采样点数量」省不了多少（触发点不随数量减少而消失）——要优化的是「构建触发次数」而非「采样次数」。
- 边界角点复用类优化的收益上限 = 可跳过的采样里「昂贵采样」的比例，不是「采样总数」的比例。本例 245 角点里只有 1 个（首个）是昂贵构建触发，其余 244 是查表命中 → 收益上限远低于「-36% 采样数」的朴素估算。
- 通用规律：缓存/预计算类的「重复计算」里，先用计数器区分「首次构建触发（昂贵）」vs「查表命中（便宜）」的占比，再决定是否值得做「去重复」——若昂贵部分不集中在可跳过的边界，去重复收益必然低于按总数比例的估算。

---

### #13 GPU 驱动编译：编译期常量下标进数据驱动函数 = 常量传播展开陷阱

> 出处：CoreSwap `knowledge/discovered/algorithm-fingerprints.md` · 发现 #13（A 类）

**发现时间:** 2026-08-15
**发现者:** worker（G4 A 方案实施 + A5 减法二分）
**来源定位:** `.investigations/perf-rework/a-plan-ssbo-implementation.md`（A5 节）+ `.investigations/perf-rework/gpu-accel-errors.md` D21/D22 + `.investigations/000-架构设计/架构计划-gpu-spline-fix.md`（001 修订版）；复现数据 `cmd-output/compile_bench-A5-*.txt`
**置信度:** confirmed（2026-08-15 用户拍板：减法二分证据链 + 3 次实测 67.4/71.4/101.8s 均 <120s 达标 + 正确性逐位一致 maxDiff=3.128e-07 + judge 审查通过）
**module:** perf

#### 观察
GPU 驱动编译时间（vkCreateComputePipelines 的 SPIR-V→机器码）对「数据驱动函数」的索引形态极度敏感，两个互相关联的通用模式：

1. **编译期常量下标进数据驱动函数 = 常量传播展开陷阱**：spline_coord 的 `switch(coordType)` 使每个 case 内 `NOISE_SLOT_BASE[0]` 成为编译期常量下标 → 常量传播进 normal_noise（数据驱动函数，参数表在 const 数组）→ `NORMAL_PACK` 读取被静态化 → 驱动逐 case 循环展开（单次调用 +37~75s）。对照：eval_df 里 `NOISE_SLOT_BASE[CA1_T[ci]]`（索引完全动态）→ 驱动放弃展开（快）。**同一批数据、同一个求值函数，仅「索引在编译期是否可解析」的差异 → 编译时间 350.6s vs 37.2s（~10×）级差**。
2. **「编译慢根因结论」有版本域**：D21 在 const 表版实证「动态 node 索引是主因」（固定 node=0 → 903.4→31.0s）；SSBO 化后做同一实验（fixed_node=0）→ 361.0s ≈ full 350.6s（无收益）——**同一个「固定动态索引」实验，const 表版成立、SSBO 版不成立**（SSBO 已把动态索引变成运行时 buffer 读，驱动无从展开，因此固定它也没有额外收益）。

#### 证据
- 减法二分链（DFC_DIAG 诊断开关 + compile_bench 秒级测）：full 350.6s / fixed_node 361.0s（动态 node 索引非 SSBO 版主因）/ coord_const 37.2s（coord 表达式贡献 ~313s）/ coord_slot0 302.3s（排除实例数因素）/ coord_case0 74.8s（1 次 normal_noise 调用 +37s）/ no_spline 17.2s（eval_df 内同函数调用不慢）。
- 修复验证：coordType 运行时查表（`COORD_SLOT_TABLE[coordType]`）+ fold 特例（`if (coordType == 2)`）后，pipeline 编译 350.6s → 67.4s（e2e 内计时）/ 71.4s（compile_bench 单独）/ 101.8s（第 3 次）——3 次均 <120s；正确性逐位一致（maxDiff=3.128e-07 / avgDiff=1.097e-08，seed 8576294172403134396，N=1024）；fp64 次因自动作废（no_old 只省 ~8.5s——fp64 成本是「与 spline 展开的交互效应」）。
- 历史对照：const 表版动态 node 索引 903.4s（D21）→ SSBO 版 350.6s → 查表修复 67.4s；spline 子系统 ~885s → ~50s（-94%）。

#### 如何利用
- **排查 GPU 驱动编译慢时，先查「数据驱动/查表函数的所有索引是否运行时不可解析」**——switch/case 把下标常量化、函数参数折叠成常量、const 数组编译期已知下标，都会触发常量传播 + 展开；把下标改成「运行时查表」让驱动无法静态化，是编译时间分水岭。
- **「固定某索引 / 去掉某子系统的减法二分」是最快定位手段**：一次实验排除一个候选（本次 coord_case0 单次调用定位 +37s），比机制猜测快；配合 DFC_DIAG 类诊断开关 + 秒级编译计时器使用。
- **根因结论必须声明版本域**：凡是「在某结构版本下成立的编译慢根因」（如动态 node 索引），结构改变后（const 表→SSBO/数据 buffer）**必须重新验证，不能直接复用**——「动态索引」在 const 表里是驱动展开的输入，在 SSBO 里已经是运行时读，同一表述指代完全不同的编译行为。
- 跨项目通用：任何 GPU compute shader / OpenCL kernel 的驱动编译时间优化（C2ME 类内核分发、pipeline 预编译分发）都适用「索引可解析性」与「版本域」两条检查。

---

### #15 GPU 批量加速带宽死局：每点数据量 × 点数是可行性判据

> 出处：CoreSwap `knowledge/discovered/algorithm-fingerprints.md` · 发现 #15（A 类）

**发现时间:** 2026-08-15
**发现者:** worker（GPU 块级生成立项 003 I6-I8 实测 → D24 负面结论，perf-rework GPU 集成课题）
**来源定位:** `.investigations/perf-rework/gpu-accel-errors.md` D24 段 + `.investigations/000-架构设计/架构计划-gpu-block-integration.md`（003 结论段）+ `.investigations/perf-rework/i-integration-record.md`（I5-I8）
**置信度:** candidate（「split 全量上传带宽死局」机制由实测坐实——24 chunks 11 分钟未完成 vs CPU 2.5 分钟；通用规律跨项目外推待更多案例验证）
**module:** perf

#### 观察

GPU 引擎算 finalDensity 完整树需要**每个点的全部分解坐标**（`splitTotal=8672` floats/点，CPU 预拆分 double→int32 格点 + float 小数）。同引擎、同 shader，**采样密度直接决定每点数据总量，进而决定可行性**：

- **逐 block 完整树（不可行）**：98304 点/chunk × 8672 × 4B = **3.4GB split 数据/chunk** 需上传；分块 4096（显存限制）→ 24 次 dispatch/chunk × 142MB + readback → 24 chunks × 24 次 = 576 次大上传 = **82GB 数据搬运** → PCIe ~16GB/s → 分钟级。实测 24 chunks **11 分钟未完成 vs CPU 2.5 分钟**（慢 4 倍+）。**GPU 快在「算」（compute throughput），但被「喂数据」（host→device 带宽）完全主导**。
- **网格角点级（可行，22-39x）**：768 点/chunk × 8672 × 4B = **27MB/chunk**——GPU 批量有意义（wg_fill_density 实测 22-39x）。

**核心判据**：**「单点数据量小 + 点量大」是 GPU 批量加速的前提**。每点数据量 × 点数 = 上传总量，超过 PCIe/总线带宽的秒级承载量（~GB/s 级）即带宽死局——与 GPU 算力无关（本次算力 24-32x 充足，卡在喂数据）。

#### 证据

- 实测吞吐（I7）：24 chunks（8576 区域）GPU 逐 block 路径 **11 分钟未完成**（主动终止）；CPU 基线同区域 **2.5 分钟**——GPU 块级路径比 CPU 慢 4 倍+（`cmd-output/` I7 运行记录 + gpu-accel-errors.md D24 段）。
- 带宽账：98304 点/chunk × 8672 floats/点 × 4B = 3.4GB/chunk；分块 4096 → 24 次 × 142MB/次；24 chunks × 24 = 576 次大上传 = 82GB；PCIe ~16GB/s → 分钟级。
- 对照组（I5）：wg_fill_density 网格角点批量 768 点/chunk × 8672 × 4B = 27MB/chunk → **22-39x**（吞吐探针实测落盘 `cmd-output/throughput-I5-*.txt`）——同引擎同 shader，仅采样密度不同，可行性翻转。
- 并发崩溃（P2-4 闭环）：I7 首次运行（无 mutex）`context=wg_fill_blocks_multi/fillOneChunk` `code=0xC0000005`，栈在 nvtfi（NVIDIA 驱动层）；fill() 加 `std::mutex fillMtx` 串行化后无崩溃——**多线程并发 GPU 调用（共享 buffer 上传/dispatch 无互斥）→ 驱动层崩溃，不是返回错误**。
- 回退验证（I8）：默认 CPU 路径 8576 **99.9994%** 零退化（与基线一致）；3200 沿用 99.9997%。

#### 如何利用

1. **GPU 加速可行性先算「每点喂多少数据」，再谈「每点算多少」**：上传总量 = 每点数据量（拆分坐标/特征向量）× 点数。凡每点数据量是 KB 级 × 点数是万级+（如逐 block 98304 点），先做带宽账（总量 ÷ PCIe ~16GB/s），分钟级即不可行——**「单点数据量小 + 点量大」是 GPU 批量加速的前提**；正确形态是「GPU 算网格/角点（点量小）+ CPU 插值/后处理到逐点」（两阶段拆分）。
2. **吞吐探针结论有「采样密度域」**：同一引擎同一 shader 在某采样密度（网格角点 768 点）下实测 22-39x，**不能外推到更高密度（逐 block 98304 点）**——数据量 ∝ 点数，可行性随密度翻转。引用吞吐结论必须声明采样密度域。
3. **多线程并发 GPU 调用必须互斥**：共享 buffer 上传/dispatch 无锁并发 → 驱动层 0xC0000005 进程级崩溃（**不是返回错误**，是崩溃）——GPU 资源并发是硬约束，任何多线程宿主（线程池/自适应并行）接入 GPU 路径 MUST 先加互斥（mutex/串行化），再谈性能。
4. **负面结论也是知识（错误优先原则）**：接线正确（无崩溃、逻辑对）但吞吐不可行时，记录「为什么不可行」（带宽分析 + 数据账）比假装成功有价值——避免后人重复实现同一死局方案；负面结论同样要落五段式错误台账 + 时间线。

---
