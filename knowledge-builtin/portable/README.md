# Portable Knowledge（框架内置实战知识库）

> **来源**：CoreSwap 项目收尾知识盘点（2026-11-16 冻结）的 **A 类 = 跨项目可复用**条目，
> 原文逐字保留，仅按主题重分 8 卷，共 **273 条**。
> **状态**：条目保留来源里的置信度（多数 `candidate`，部分 `confirmed`）；导入**不改变**任何结论。
> **机器索引**：[`index.yaml`](index.yaml)（key / volume / id / title / status / source）。
> **提炼规则**：[`rules.md`](rules.md)（人工维护，引用条目 key；不具规范效力）。

## 分卷

| 卷 | 文件 | 主题 | 条目 |
|---|---|---|---|
| 01 | `01-validation-and-experiments.md` | 验证与实验设计 | 64 |
| 02 | `02-attribution-and-debugging.md` | 归因与调试 | 76 |
| 03 | `03-toolchain-and-environment.md` | 工具链与环境 | 59 |
| 04 | `04-language-and-compiler-idioms.md` | 语言与编译器惯用法 | 14 |
| 05 | `05-performance-and-concurrency.md` | 性能与并发工程 | 21 |
| 06 | `06-gpu-programming.md` | GPU 编程 | 27 |
| 07 | `07-reverse-engineering-pitfalls.md` | 逆向与反编译工具坑 | 2 |
| 08 | `08-collaboration-and-process.md` | 协作与流程纪律 | 10 |

## 三层吸收（本目录只承担第 1 层）

| 层 | 载体 | 内容 | 约束 |
|---|---|---|---|
| 1. 案例库 | `knowledge-builtin/portable/`（本目录） | 273 条原始实战条目 | 逐字保留；来源冻结；只读参考 |
| 2. 规则摘要 | `rules.md` + 相关技能清单 | 跨条目提炼的检查项，逐条引用 `卷#条目` | 人工维护；`candidate` 条目只能产生**建议**，不得当作规范 |
| 3. 规范条款 | `spec/engineering-framework-v1.md` | 反复验证、跨域成立的 MUST | 需人类确认；`candidate` 永不直接升格 |

## 用法

1. 分析/排查前先读 [`index.yaml`](index.yaml) 的标题与主题，按 `key`（如 `01#12`）定位到卷内条目；
2. 引用格式：`portable/01#12`（卷 01，条目 #12）；同一卷内重复编号以 `~2` 后缀区分（见 `index.yaml`）；
3. 条目是**证据/经验**，不是当前结论：与项目实测冲突时以实测为准，并在项目 `knowledge/` 记录冲突；
4. 想把某条晋升为规则或规范：走 `rules.md` 的引用清单 + 人类确认，不直接改本目录正文。

## 维护

- **不手改**本目录的 8 个卷文件：它们与来源逐字一致，重新导入会覆盖。
- 重新导入：`python scripts/absorb_portable_knowledge.py`（校验 273 条；`--check` 只校验不写盘）。
- 新增来源材料：先追加到 `E:\PYTHON\Portable-Knowledge`，再重跑导入并人工更新 `rules.md`。
- 已知重复/近重复（来源自身标注）：`02#10` 与 `02#10~2` 是不同主题的同号条目；来源提及 `#27≈#172`、`#144≈#146`，本库保留全部、不合并。
