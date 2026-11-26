---
volume: 07
title: 逆向与反编译工具坑
scope: 反编译误译、映射、反射污染
source: CoreSwap knowledge/discovered（A 类条目重组，正文原样）
status: draft
---

# 07 · 逆向与反编译工具坑

> 覆盖范围：反编译误译、映射、反射污染。条目正文自 CoreSwap 知识库原样搬运（A 类 = 跨项目可复用），行首出处可回查原条目。

## 目录

- #1 javap/反编译输出不可直接信任
- #5 引用反编译/源码树作参照前必须核版本/DataVersion

---

### #1 javap/反编译输出不可直接信任

> 出处：CoreSwap `knowledge/discovered/f5-bugs.md` · 发现 #1（A 类）

**发现时间:** 2026-08-08
**发现者:** worker（CoreSwap 逆向方法论）
**来源定位:** AGENTS.md 二、逆向方法论
**置信度:** confirmed
**module:** re-code

#### 观察
javap 输出的字节码反编译（及混淆 jar）仅供参考，**Java 源码（yarn mappings + sources jar）才是权威**——混淆/优化会使 javap 输出与真实逻辑偏差（签名、常量折叠、异常表）。

#### 证据
- CoreSwap 全程以 yarn mappings + sources jar 为准还原，逐位对齐通过（3200 100%）

#### 如何利用
- 还原前先确认权威源（源码/mapping）；javap 只用于交叉验证，不一致时以源码为准

---

### #5 引用反编译/源码树作参照前必须核版本/DataVersion

> 出处：CoreSwap `knowledge/discovered/f5-bugs.md` · 发现 #5（A 类）

- **发现时间**：260905-03；**发现者**：core.worker 草稿（light-opt round-trip 判据设计）；**置信度**：candidate（实测矛盾 + 源码树版本疑点，judge 待走）；**module**：re-code / 源码参照核验。

#### 观察
设计「存档 round-trip 光照不变」判据时，参照 `.tmp/net` Mojang 源树中 isLightOn 的序列化写入逻辑，得出「存档应有 isLightOn 键」的预期。实测 vanilla/rust 双侧存档**全量无 isLightOn 键**（口径：2025 chunk 全量 NBT 键扫描）——预期与实测矛盾；回查发现 `.tmp/net` 源树疑非 1.20.1（其 isLightOn 写入与 1.20.1 实测行为不符）。

#### 根因
反编译/源码树是**某一版本**的快照，参照前若不核版本（DataVersion / build 元数据），会把别的版本的序列化行为当成当前版本事实——与「javap 不可直接信任」同族：问题不在源码假，在「拿错版本的真源码」。

#### 教训/如何利用
1. **判据**：任何反编译/源码树被引用为行为参照前，第一步核其版本锚（DataVersion、gradle/loom 元数据、路径内版本号），与课题目标版本一致才可引用。
2. **源码 vs 实测矛盾时以实测为准**，并回查源码树版本——这本身就是版本错位的判别签名。
3. 家族索引：本文件 #1（javap 不可信——静态产物需版本锚）、compiler-idioms #13（docs 口径先一手源码核对——本条为「源码先核版本」对偶面）。

---
