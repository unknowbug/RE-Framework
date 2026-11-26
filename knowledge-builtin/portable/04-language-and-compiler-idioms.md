---
volume: 04
title: 语言与编译器惯用法
scope: 整数语义、类型腐蚀、门控死锁、语言级坑
source: CoreSwap knowledge/discovered（A 类条目重组，正文原样）
status: draft
---

# 04 · 语言与编译器惯用法

> 覆盖范围：整数语义、类型腐蚀、门控死锁、语言级坑。条目正文自 CoreSwap 知识库原样搬运（A 类 = 跨项目可复用），行首出处可回查原条目。

## 目录

- #4 MSVC `long` = 32 位（LLP64）→ `long bestCost = INT64_MAX` 截断
- #8 JSON 布尔字段经 `as_f64` 读取恒 false
- #9 跨 session 未验证标注三查（当公理继承则整链作废）
- #10 半开区间 `rev().step_by()` 复刻含两端递减循环的 off-by-one
- #11 诊断门控 flag 在初始化器内唯一置位 = 鸡生蛋死锁
- #13 文档口径与一手源码失准 → 以文档为依据前先核源码
- #14 负值经无符号 parse 静默 clamp（opacity:-1 → 0）
- #15 位打包标量域「部分位判零」陷阱
- #16 JSON 字段「类型形态枚举不全」静默腐蚀
- #18 复刻 Java long 算术一律 `wrapping_*`（debug 溢出 = 免费审计器）
- #22 跨语言 id 域可在注册时对齐 ⇒ 同域化优于运行时映射表
- #25 给逐字复制的类加头注释也会改变 `.class` sha（LineNumberTable）
- #26 读 sysprop 的 `static final` 不是编译期常量（`<clinit>` + C2 折叠）
- #28 Python `d[k()] = f()` RHS 先求值——解析器 bug 伪装成数据 malformed

---

### #4 MSVC `long` = 32 位（LLP64）→ `long bestCost = INT64_MAX` 截断

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #4（A 类）

**发现时间:** 2026-08-08
**发现者:** worker（SearchTree 移植 3 版迭代）
**来源定位:** Windows LLP64 ABI（long 4 字节 / long long 8 字节；Linux LP64 下 long 8 字节）+ MultiNoiseUtil.SearchTree 移植
**置信度:** confirmed（crash 复现 + 改 long long 后修复）
**module:** re-code / swe

#### 观察
`long bestCost = INT64_MAX` 在 MSVC（Windows LLP64）下 `long` 是 **32 位**，`INT64_MAX` 截断为 -1 → 后续 `bestCost > cost` 恒 false → 分支选择逻辑全错（bestBatches 恒空 → makeBranch throw → 崩溃）。Java `long` / Linux 代码里 long 常被当 64 位，直接搬到 MSVC 就会踩。

#### 证据
- SearchTree 移植 v1 空指针崩溃、v2 异常崩溃（makeBranch throw），v3 定位 `long bestCost = INT64_MAX` 为根因
- 改 `long long`（64 位）后 (812,73,-337) forest→badlands 修复、8576 24→22 mismatch

#### 如何利用
- **MSVC 下 64 位整数一律用 `long long` / `int64_t`，不用 `long`**（`int64_t` 在 MSVC 就是 long long）
- 移植 Java long / Linux 源码时 grep `INT64_MAX`、`INT64_MIN`、`0x7FFFFFFFFFFFFFFF` 赋值给 long 的代码
- Java `long` → C++ `int64_t`/`long long`（不是 long）

---

### #8 JSON 布尔字段经 `as_f64` 读取恒 false

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #8（A 类）

- **发现时间**：260902-03；**发现者**：core.worker 草稿（soul-v4v5 课题 .b2-soul fan-out 裁决）+ 主会话应用；**来源定位**：`.artifacts/.b2-soul/v4-eval-conflict.md` + `.investigations/soul-v4v5/v4-fix-verification.md`（修复位置 `WorldgenRust/src/surface_rules.rs` parse_surface_cond 三处 + `parse_bool_field`）；**置信度**：candidate（三级数据层证据实锤，confirmed 待用户拍板）；**module**：re-code / swe（数据驱动解析器 / 跨语言 JSON 语义）。
- **观察**：自定义 JSON 包装层若按标量分型提供 API（`as_f64` / `as_bool` / `as_str` 各只对同型返回 Some），则 `x.as_f64().map(|f| f != 0.0).unwrap_or(false)` 读布尔字段**恒得 false 且无任何告警**——不是兼容读取，是静默语义腐蚀。Java `GsonHelper.getAsBoolean(json, key, false)` 是 bool 优先/缺省 false 的类型感知读取，两端 API 语义不等价，直译即错。本例：surface_rule 三处布尔字段（add_surface_depth/add_stone_depth）恒 false → soul 分支条件 `sdb ≤ 1+0+surface_depth` 退化为 `sdb ≤ 1` → 分支该进未进穿透兜底，nether 存档对齐被压 2.20pp（94.42%→96.62% 修复）。
- **证据**：nether.json L293 `"add_surface_depth": true`（布尔）vs 解析产物树 dump 实测 `asd=false`（soul-tree-repro，8 处假阴性中 3 处为真阳性翻转）；定点 3260,1,3200（sdb=2, surface_depth=3）`2 ≤ 1+0+0`=false 复现 applied=256，修复后 `2 ≤ 1+0+3`=true → applied=258 与 V3 语义推演逐位一致；生产 180 点 dump netherrack 103→71；存档 94.4241%→96.6215%/96.5866%（seed B，4×4@3200,3208，存档口径）。
- **如何利用**：
  - **规则**：分型标量 API 下读布尔一律 `as_bool().or_else(|| as_f64().map(|f| f != 0.0)).unwrap_or(false)`（类型感知 + 数字 0/1 兼容 + 缺省 false），禁止「万能 as_f64 转 bool」；移植/翻译 Java 数据驱动解析器时，逐字段核对 Gson getXxx 的类型容忍面与目标语言 API 的分型行为是否等价。
  - **签名**：「条件永远不成立但无任何告警」+ 解析期零 WARN（读取成功返回 false，不是解析跳过）——凡「分支看起来存在却从不进入」先 dump 解析产物核对布尔字段；与发现 #7 同族（都是「单维度/单分支未覆盖即潜伏」的解析器坑）。
  - 交叉引用：对拍方法教训见 workflow-patterns 发现 #12（对拍解析产物而非 JSON 原文——本发现的假阴性正是被 #12 缺口掩盖的）。

---

### #9 跨 session 未验证标注三查（当公理继承则整链作废）

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #9（A 类）

- **发现时间**：260902-07；**发现者**：core.worker 草稿（b1-downdrill H1 环1 证伪复盘）+ 主会话应用；**来源定位**：`.investigations/b1-downdrill/b1-errors.md` E-B1-9 + `facts-260902-06/07.md`；**置信度**：candidate（数据层实锤：LAUIDMAP 权威映射一轮推翻定案候选，judge PASS，confirmed 待用户拍板）；**module**：workflow / re-code（MC 注册表 / 交接纪律）。
- **观察**：MC 探针输出 raw block/state id（如 COLPROF `99|0->19319`）时，若首次出现未同时输出 id→方块映射，session 内凭数值直觉赋语义（「19319 大数≈新块≈lava」「5854≈netherrack」）后写入事实链，下一 session 即当公理直接续推——实测 Java STATE_IDS 权威映射：**19319=blackstone、5854=basalt**（lava=96、netherrack=5850），「熔岩海缺失」机制链环 1 整环证伪、修复方案作废。标注从「未验证解释」升格为「事实」只发生在文档传递里，不在数据里。
- **证据**：`[LAUIDMAP]`（探针启动时遍历 Registries.BLOCK/STATE_IDS 打印映射）vanilla 轮一轮实锤；LAVAAUDIT v2 全扫 11,443 公共列 air→lava 面向两侧均为零；COLPROF 10 列 diff 真相 = V 黑石底(y=99) vs C 玄武岩底(y=100~104)，两侧均实心。验证成本一轮，此前整条五环机制链与回归判据全部改写。
- **如何利用**：
  - **标注三查（与 seed 三查同级的开工检查项）**：① 探针输出的 raw id/枚举/魔法数**首次解释前必须先建立 id→语义映射**（探针打印 LAUIDMAP 类映射，禁止数值范围直觉命名）；② 标注跨 session 传递 MUST 带「已验证/未验证」标记，未验证标注续用前先做廉价独立验证（≤ 一轮，§16.3 宿主交接验证）；③ 机制链逐环追问「这一环的输入标注是谁验证的」——环 1 错则整链作废，越早核实越便宜。
  - **判据**：「机制链自洽 + 量级对得上」不能替代输入标注核实——自洽的链条建在错误标注上时全链同样自洽（本例黑石/玄武岩材质差同样能解释转换面漂移现象）。

---

### #10 半开区间 `rev().step_by()` 复刻含两端递减循环的 off-by-one

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #10（A 类）

- **发现时间**：260903-13；**发现者**：core.worker 草稿（lossless-accel off-scan+cornerfix 课题）+ 主会话应用；**来源定位**：commit 3e2e67d + `.artifacts/lossless-accel/off-scan-cornerfix-verdict-260903-13.md` + `.investigations/lossless-accel/review-offscan-cornerfix-260903-13.md`（Rust 侧 `WorldgenRust` est 扫描；Java 侧 forge official sources `NoiseChunk.java:174` `computePreliminarySurfaceLevel`）；**置信度**：confirmed（修复后两臂四臂 hash 完全一致 f2b1a3932c6e589e + Java 角列 256/256 0 diff，judge PASS，260903-13 用户拍板）；**module**：re-code / swe（跨语言循环移植）。

#### 观察

Java `for(l=top; l>=bottom; l-=step)` 是**含两端**的递减扫描；移植 Rust 时写成 `(bottom..top_exclusive).rev().step_by(step)` 会引入**两个独立的错位**：① 半开区间上端使 rev 首点 = top−1（本例 319 vs Java 320）；② 下端 exclusive 使下界端点语义差（本例 Java 扫到 −64 含端）。首点差与下界包含性是**两个独立参数**，只对齐其一修不完整。

#### 证据

- 本例签名：修复前 off 臂 est 角列对 Java **恒差 −1**（64/64 全偏、delta 恒 −1，含 c0 原点角——规整性系统偏移而非随机差）；敏感角 (201,200) 值 55 vs Java 56。
- 修复（扫描对齐「首点值 + 下界包含性」）后：两臂四臂 hash 完全一致（`f2b1a3932c6e589e`）；Java est 角列 off/shared 各 256/256 一致 0 diff。

#### 如何利用

- **判据**：跨语言移植递减扫描循环时，必须显式对齐**「首点值」+「下界包含性」两个独立参数**，逐一与 Java 源码核对（`l>=bottom` 含端 vs Rust `..` 半开），禁止凭「看起来等价」直译。
- **签名**：结果相对参照**恒差固定小量（如 −1）且全样本规整偏移** = 扫描/索引 off-by-one 类错位，优先核对循环端点语义，不是精度/随机性问题。
- 等价复刻形态：Java `for(l=top; l>=bottom; l-=step)` → Rust `(bottom..=top).rev().step_by(step)`（含端 RangeInclusive），并核对 `top−bottom` 可被 step 整除时的末点行为。
- 交叉引用：workflow-patterns #25（静态调研/直译结论失真——本例 +15 角参数即其第三例实例）；compiler-idioms 发现 #7（锚换算端点 off-by-one 同族：端点语义 inclusive/exclusive 是跨语言移植的第一易错点）。

---

### #11 诊断门控 flag 在初始化器内唯一置位 = 鸡生蛋死锁

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #11（A 类）

- **现象**：WG_AQDUMP 门控零输出，stderr 连 `[AQDUMP] enabled` 行都没有——门控从未激活，且无任何报错。
- **根因**：worker 草稿把唯一置位点写在初始化器里：`aqdump_hit` 先查 `AQDUMP_ON`（false）才初始化 points/激活门控——flag 永远 false，初始化永远不发生。
- **定位**：stderr 无 enabled 行 → 顺门控生命周期静态走查首次调用路径，发现置位点在死分支内。
- **修复**：改为 env **存在性** `OnceLock` 先判（env 存在 → 门控激活），与初始化解耦。
- **教训**：诊断门控的设计模式——**激活判据（env 存在性）与数据初始化必须分离，激活判据不得依赖被它门控的初始化器**；上机前静态走一遍「首次调用路径」（谁第一个读 flag、flag 在哪置位、可达吗）。与「死参数制造假判别」（workflow-patterns #20）同族：门控没生效 ≠ 机制无差异。

---

### #13 文档口径与一手源码失准 → 以文档为依据前先核源码

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #13（A 类）

- **发现时间**：260904-10　**置信度**：candidate
- **观察**：docs/06 L62/L94 记 surface default 判定「==stone」，一手 SurfaceBuilder.java L181-183 实为「非空非流体」。.b4 候选曾以 docs 口径推出「需改码」，P0 核对证伪——Rust/C++ 本就与一手一致，无需改。
- **判据**：docs/主题篇是二手转述，作为**修复依据**（要动代码）前必须对一手源码核对；作为排查线索使用则无需——判据 =「这个口径要花钱（改码）吗？要则一手核对」。
- **处置**：docs/06 追加修正小节（不覆盖原文）；本条仅记录判据。

---

### #14 负值经无符号 parse 静默 clamp（opacity:-1 → 0）

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #14（A 类）

- **发现时间**：260905-03；**发现者**：core.worker 草稿（light-opt 课题顺藤）；**来源定位**：`worldgen-core/src/light/mod.rs:121-125`（18 个 opacity:-1 条目实测 clamp）；**置信度**：candidate（代码位置 + 条目数实证；与光照残差无关，语义有损待修）；**module**：re-code / 数据驱动解析。

#### 观察/根因
light_data.json 中 18 个条目 opacity 为 -1（语义：不透明度哨兵/负值语义），经 `parse_u8_field` 的 u8 解析路径被静默 clamp 为 0——解析零告警，但语义有损（-1 的语义与 0 完全不同）。与发现 #8（JSON 布尔字段经 as_f64 恒 false）同家族：**「宽收窄/带符号转无符号的标量 parse API 静默腐蚀语义」**——#8 是布尔收窄，本条是符号性收窄，共同点是解析成功返回值 + 零告警。

#### 如何利用
- **签名**：「条件/数值看起来解析成功但下游行为异常、日志零 WARN」→ dump 解析产物核对原始 JSON 值与解析后值逐字段差（#12 姿势：对拍解析产物而非输入原文）。
- **规则**：负值语义字段禁止直接 u8 parse——先 parse i64 再显式映射负值语义（clamp 前必须有「负值是否合法」的显式判定）。
- 交叉引用：#8（布尔恒 false，同族第一例）。

---

### #15 位打包标量域「部分位判零」陷阱

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #15（A 类）

- **现象**：光照优化 round2 air 快路径首轮实现只判 `id 位 == 0` 即跳过查表 + col_max 写；合成 golden 用例（id=0 + luminance=15，即打包值 `15<<24`）立即 FAIL——该值是合法光源（ABI = raw id 低 24 位 | luminance 高 8 位），却被快路径当空气吞掉，光照输出静默错。
- **根因**：对**位打包标量**做类别判断时，把「某字段为零」误当「整个字为零」——`id==0` 不蕴含 `v==0`，高位还可能携带其他字段。字段判断与全字判断的语义混淆，且静默（不崩溃、只错输出）。
- **定位**：合成 golden 逐位对照门（workflow-patterns #47）一轮即捕获——合成用例专门构造「id=0 + luminance>0」边界输入，真实数据用例反而可能覆盖不到。
- **修复**：快路径判据改为**判全字 `v==0`**（且 `table[0]==(0,0)`），任何非零位都回退完整查表路径。修复后 4 用例 golden 全等 PASS。
- **教训/判据**：① 对位打包值做类别快路径，**必须判全字为零，或显式声明并验证「其余位必为零」的不变量**。② 与 #8（布尔经 as_f64 恒 false）、#14（负值经 u8 parse 静默 clamp）同家族：**「标量跨域/跨表示的静默语义腐蚀」**——共同点 = 解析/判断「成功」且零告警。③ 合成边界用例（构造字段间取值组合）是 golden 用例集的必备成分，纯真实数据可能永远不触发该分支。
- 交叉引用：#8、#14（同族）。

---

### #16 JSON 字段「类型形态枚举不全」静默腐蚀

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #16（A 类）

- **发现时间**：260905-12；**发现者**：core.worker 草稿（feature-parity patch_grass 内联修复课题）+ 主会话应用；**来源定位**：`.investigations/feature-parity/260905-12-patch-grass-inline-fix.md` + `worldgen-core/src/placement.rs`（PlacedFeature::parse_inline）/ `feature_loader.rs`（generate_configured/generate_nested）git diff；**置信度**：candidate（修复前后基线对照实锤，judge/confirmed 待走）；**module**：re-code / swe（数据驱动解析器 / 跨语言 JSON 语义）。

#### 观察/根因
patch_grass 系 **24 个内联点位**（18 个 patch_*.json + 6 个 flower*.json random_patch/flower 系 configured feature，patch_berry_bush/patch_cactus/patch_grass_jungle/patch_large_fern 等）的 `feature` 字段是**内联 configured feature 对象**（Java 语义 = `Holder.direct`，无 id 直发），不是 id 字符串。`parse_inline` 只按字符串形态解析（`as_str().unwrap_or("")`）→ 内联对象静默变**空串 id** → 运行时 `generate_nested("")` → placed/configured cache 双 miss → 空 id 告警 ×N（该参照区 miss=8766）。解析期零告警——与 #8（布尔 as_f64 恒 false）、#14（负值 parse_u8 clamp）同家族：**JSON 字段类型形态枚举不全 = 静默语义腐蚀家族**。#8 是布尔收窄、#14 是符号性收窄，本条是「字段值可能是复合对象而 parse 只支持标量形态」的**结构性**收窄；共同点 = 解析「成功」返回 + 零告警，语义已损失。

#### 证据
- 修复前 features_probe release × recheck 参照（6×6）miss=8766 / match 94.99%；修复后 miss=0 / match 94.78%（stash/pop 单变量基线对照，同 seed 同参照同二进制载体）。
- 修复 = `PlacedFeature` 增 `inline_configured: Option<Box<ConfiguredFeature>>`（Box 断 CF→PlacedFeature→CF 递归环）；parse_inline 对 object 形态直接 `ConfiguredFeature::parse("", obj)` 持有实体；generate 侧 inline Some 时直发、优先于 id 查 cache（对齐 Java Holder.direct 直发非查表语义）。

#### 如何利用
- **判据（形态枚举全覆盖）**：数据驱动解析器对「id 引用型」字段（placement/configured 的 `feature`、`config` 内嵌等）必须显式枚举**全部三形态**——① id 字符串（查表）② 内联对象（直接解析持有，Holder.direct 语义）③ 缺失（才允许告警/缺省）。只写 `as_str().unwrap_or("")` 一种读法 = 隐含假设「永远是字符串」，移植 Java 时先核对 `Holder` 的 direct/reference 双形态。
- **判据（空 id = 解析层缺陷签名）**：运行时 miss 告警必须带 id 内容检查——**空 id/空串 key 的 miss 是解析层缺陷签名，不是运行时层问题**（运行时层缺 key 应是有名 id）；见空串 miss 先回解析层 dump 产物，不查 cache 实现。
- 交叉引用：#8（布尔恒 false，同族第一例）、#14（负值 clamp，同族第二例）、workflow-patterns #12（对拍解析产物而非 JSON 原文——本例假阴性同样被该缺口掩盖）。

---

### #18 复刻 Java long 算术一律 `wrapping_*`（debug 溢出 = 免费审计器）

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #18（A 类）

- **发现时间**：260906-04；**置信度**：candidate（panic 行号定位 + 修复后 debug/release 同语义实证）；**module**：re-code / Rust↔Java 算术语义。

#### 观察/根因
fill 大坐标 chunk（100,100）时 panic `attempt to multiply with overflow` @ `chunkrandom.rs` 的 `set_population_seed`/`set_carver_seed`。Java long 乘法天然回绕（JLS 语义，静默取低位）；Rust debug profile 算术溢出即 panic。`next_long()` 可取满 i64 域，`chunk_x * l` 超域是必然事件——此前 overworld/nether 未炸只因测试 chunk 坐标小。release profile 静默回绕，语义碰巧与 Java 一致，缺陷被掩盖。

#### 修复
三处 `*`/`+` 改 `wrapping_mul`/`wrapping_add`——位模式与 Java 完全一致，非行为变更。

#### 如何利用
1. **判据（MUST）**：复刻 Java long/int 算术一律 `wrapping_*`——使 debug/release 同语义，不依赖 profile 巧合。判据适用面：种子派生、hash 组合、坐标×大常量（`x * 3129871` 类，AGENTS.md 易错点清单既有条目）。
2. **正向利用（判错经验）**：新维度大坐标/新 seed 派生链首跑**必须先过 debug profile**——debug 溢出断言等价于免费的「Java 回绕点审计器」，逐个 panic 点就是一处需要 wrapping 的位置；release 只会静默吞掉。
3. 交叉引用：compiler-idioms #4（MSVC long=32 位——同一「Java long 语义在系统语言侧不成立」家族的 C++ 面）。

#### 证据
`.investigations/end-takeover/260906-04-errors.md` E2；`chunkrandom.rs` set_population_seed/set_carver_seed。

---

### #22 跨语言 id 域可在注册时对齐 ⇒ 同域化优于运行时映射表

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #22（A 类）

- **发现时间**：260907-08；**发现者**：core.worker subagent 草稿（源材料：.artifacts/jni-blockid-fix-260907-08.md）；**置信度**：candidate（cargo test 7/7 + runServer round4 显式 id 对齐实机 PASS；「映射表必然更差」未做反向对照，泛化边界见如何利用）；**module**：re-code / 跨层 id 域设计（#21 的设计侧姊妹条）。
- **来源定位**：worldgen-core/src/blocks.rs `register_with_id` / api.rs `wg_register_block_id(handle, name, java_raw_id)`；本工作块候选 B 的方案取舍（显式 id 注册取代 Java↔Rust id 映射表）。
- **观察/根因**：原问题 = Rust 内部动态分配 id 与 Java raw id 域错位，写回 `Registries.BLOCK.get(id)` 无对齐保证；映射表方案在运行时维护「rust_id ↔ java_raw」对应，但这引入**第二真相源**（两侧各有一套 id + 一张映射，映射本身成为新的出错面）。显式 id 注册把对齐动作前移到注册时：`wg_register_block_id` 直传 java_raw_id，Rust 内部 id 与 Java raw id **同域**，写回直查即对齐，映射层整个消除。
- **如何利用（判据）**：
  1. 跨语言/跨模块 id 传递的设计取舍顺序：先问「两侧 id 域能否在注册/边界构造时同域化」——能则显式对齐（单真相源），运行时映射表是退而求其次（第二真相源要付同步/漂移/调试成本）。
  2. 泛化边界：前提是「注册时可拿到权威侧 id 且域无碰撞」（本轮靠 #21 的 vanilla 表后位置判据保证）；id 域无法对齐（如两侧密度函数序号各自派生）时映射表仍是合法方案——判据是**消除映射机会优先**，不是「映射表禁用」。
  3. 显式 id 与动态分配并存时的语义配套：id 被占拒绝 / 越界拒绝 / 成功推进 next_id（显式 id 后动态分配不回退碰撞）——三条件缺一即埋新错位。
- **证据**：round4 `[BLOCKS-REG] testmod:aligned_probe java_raw=1003 rust_id(overworld=1003 nether=1003 end=1003)` 三句柄对齐 + `register_with_id_semantics` 测试（对齐/冲突拒绝/越界拒绝/next_id 推进）；.tmp/verification-260907-08.log。

---

### #25 给逐字复制的类加头注释也会改变 `.class` sha（LineNumberTable）

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #25（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260912-01；主会话（Wave 2 共享化实施中实测）+ scout-judge（C2 要求逐条声明调试属性类差异）+ 本波 judge（**C4 即本条的正向实例**）；**confirmed**（用户授予 2026-09-12 15:52；judge 已做 = PASS-with-conditions、C1–C9 已响应，record §4.7.7；record §6 已回填）；compiler-idioms / 类文件调试属性与字节锚（**#24 的「类文件结构」邻接面**）。
- **来源定位**：`record-260912-01.md` §4.6（`:161-168` 构建三态表——`post1`（含头注释）→ **`post2` = V1b 判定基线**，隔离差异恰 2 条 = `CoreSwapFixHelper` + `StallWatch`；1.20.1 侧 `:184`「`StallWatch` 逐字复制后条目 sha 全等；**曾因加 1 行头注释导致行号位移 ⇒ 删注释恢复字节锚**」；`:178/180/182/200/201` 各「仅调试属性（`LineNumberTable`）」条目 + `javap -c -p` 输出完全相同的判定）+ **§4.7.7（C4 条 `:305`：注释修补保行数 ⇒ 类字节不变）**；证据 = `evidence/post1-vs-post2-1.20.1.txt`、`evidence/post3-vs-post4-{1.20.1,1.21.6}.txt`。
- **现象（语义/机制）**：把一个类**逐字复制**进共享源后条目 sha 全等；**加 1 行头注释**（如「本文件自 1.20.1 共享化而来」）后该条目 sha **改变**，而 `javap -c -p` 输出**完全相同**（指令集未变）——差异全在调试属性。
- **根因（机制）**：javac 为指令生成 `LineNumberTable`（源码行号 → 字节码偏移），**行插入使其后所有源码行号 +1** ⇒ 每条指令的 start line 整体位移，类文件的属性表字节随之变化（常量池/指令不变）。⇒ 「注释不影响产物」对**需要字节锚**的场景**不成立**。
- **定位（怎么发现的）**：对拍同一类的**条目级 sha** 与 `javap -c -p`（不带 `-l`）输出——sha 变而 javap 输出完全相同 ⇒ 差异只在调试属性（`LineNumberTable`）；`javap -v`/`-l` 可见行号变化。
- **判据（可复用）**：① 需要**字节锚**（V1-strict 等价门 / 跨树条目级 sha 比对）的「逐字复制」文件 **MUST NOT 加头注释、MUST NOT 做纯格式调整**——出处/血统写在 **README + commit message**；② 判「仅调试属性差异」MUST 用 `javap -c -p`（该输出不含 `LineNumberTable`），并在声明里写「仅调试属性」而非「等价」；③ 反向利用：**想故意零字节差异**时，行号是必须冻结的变量之一（与空白、导入顺序并列）；④ 与「注释级改动 jar 逐字节相同」（build-tooling #56 / #116 等价性门的一环）**不矛盾**——那是**不加/删行**的注释改动，本条是**增删行**的注释改动，两者结论不同、MUST 分开表述；⑤ **正向对偶（本波 judge C4 实例）**：若必须改注释，则**保持总行数不变**（逐行替换）⇒ 其后代码行号不变 ⇒ `LineNumberTable` 不变 ⇒ 类字节不变（`ChunkTiming.java` javadoc 修补实测 `post4` ≡ `post3`、差异 0，两版 jar sha 相同 —— `evidence/post3-vs-post4-*.txt`）；⑥ **V1b 判定基线 MUST 声明是否含头注释态**（本波 `post1` 含注释、`post2` 删注释后才是判定基线；判定基线选错会把「行号位移」当成 Java 面差异 —— judge C6）。
- **家族索引**：workflow-patterns #116（全量条目级 sha256 等价门）、workflow-patterns #138（V1b 声明粒度：仅调试属性 vs 指令级）、build-tooling #56（UP-TO-DATE 假绿——注释级改动的另一半）、f5-bugs（javap 不可信点）、build-tooling #61（javap 对拍陷阱）。

---

### #26 读 sysprop 的 `static final` 不是编译期常量（`<clinit>` + C2 折叠）

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #26（A 类）

- **发现时间 / 发现者 / 置信度 / module**：260913-03；judge（隔离 subagent SHOULD-1）+ 主会话复核；**candidate**（confirmed 留用户）；compiler-idioms / Java 门控与常量语义（诊断门控家族 #11/#98 的措辞纪律面）。
- **来源定位**：`java-core\src\main\java\wg\bench\BulkWb.java`（`SENTINEL = System.getProperty("coreswap.bulkwbsentinel") != null`）；`.investigations/000-架构设计/架构计划-260913-03-R9b并发加固.md` judge SHOULD-1 段。
- **机制（为什么）**：`System.getProperty(...)` 是方法调用，**非常量表达式** ⇒ javac 不内联、该字段不是 JLS 编译期常量 ⇒ `if (!SENTINEL) return;` 之后的代码**不会**被编译期剔除（Java「条件编译」只对 `static final` = 常量表达式字面量成立）。实际保证链 = `<clinit>` 恰一次求值 + C2 JIT 运行期折叠 ⇒ 门关成本 = 每 chunk 一次方法调用 + 一次分支，可忽略但**不是零指令**。
- **判错经验（可复用）**：① 「门关零开销」类性能声明，机制名 MUST 与实际保证链一致——「compile-time 消除」vs「clinit 单赋值 + 运行期折叠」是不同声明，后者才成立；② 确需编译期消除须用 `static final boolean = <常量表达式字面量>`（构建期生成常量类/常量注入），接受其代价；③ 自查：对声称「编译期消除」的门，javap 看 `<clinit>` 与分支是否还在字节码里。
- **家族索引**：#11（诊断门控初始化器唯一置位）、#25（类文件常量面——同属「编译期常量直觉不可靠」）、workflow-patterns #98 家族（诊断门控 chunk 级一次）、#120（公众声明与门控同源核对——同一「措辞与机制对齐」纪律）。**验证分层 = Degraded**（静态 JLS 语义论证 + javap 自查法，未做专门字节码实验）。

---

### #28 Python `d[k()] = f()` RHS 先求值——解析器 bug 伪装成数据 malformed

> 出处：CoreSwap `knowledge/discovered/compiler-idioms.md` · 发现 #28（A 类）

- **现象**：比较器第 1 轮 `IndexError: index out of range` 于 `u1()`（o1o3-r3r4-run.log L4-25）；修复后第 2/3 轮 `[VOID] malformed 75.1323%`——r3 臂 7100/9450 chunk 全部 `truncated NBT at offset 47 need 28531 have 2911`，且**不同 chunk 同一锚点同一 need-have 数值**（L29/L34，c(3,-32)/c(4,-32)/c(5,-32) 三例全同）。
- **根因**：手写 NBT 解码器使用 `d[r.s_()] = payload(r, tt)` 形态——Python dict 赋值**先求值 RHS**（`payload` 推进光标 r.p）再求值 key（`r.s_()` 读长度/字符串字段）→ key 读到 payload 消费后的错误光标 → 解码器**全局错位**。配对坑（同文件 `_i8`）：读长度字段时光标不推进 → 后续 payload 从错误起点读 → 段静默丢失截断。两者都伪装成「region 文件坏了」，实际数据 ok=9450/9450 完好。
- **定位**：第 1 轮 traceback 指向 u1 越界（解析器层非数据层）；「不同输入同一 need-have」签名排除随机损坏、锁定解析器确定性 bug；修好后 P14 双臂 gap=0.0000% / hash_mismatch=0/9450 与历史 t8_b5_r3_audit.py 0/9450 互验背书。
- **修复**：赋值语句拆分求值序（先 key 后 payload，显式临时变量固定顺序）+ 修 `_i8` 光标推进；最终版 sha 前 8 位 A044031A 通过。
- **教训**：① 复合赋值 `d[k()] = f()` 求值顺序（RHS→key）在带副作用（光标推进）的解析器上下文是活性陷阱——解析器代码禁把带副作用表达式内联进复合赋值；② 「malformed 高但 need-have 数值恒定」= 解析器 bug 签名不是数据 bug——**先疑解析器再疑数据**，独立既有解析器互验一步定责；③ 与 #151（漏读长度前缀）、#159（region NBT 手写三坑，build-tooling）同族：手写二进制解析器失真全部伪装成「数据坏」。
- **来源**：o1o3-r3r4-run.log L4-49（三轮原文）；judge-review-verdict-260919-08 C-N1 备注栏；verdict-260919-08 §1。

---
