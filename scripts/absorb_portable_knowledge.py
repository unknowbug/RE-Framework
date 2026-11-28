#!/usr/bin/env python3
"""Import the Portable-Knowledge volumes into the framework's builtin layer.

Source: E:\\PYTHON\\Portable-Knowledge (CoreSwap A-class cross-project knowledge,
273 entries, frozen 2026-11-16). The volumes are copied verbatim; this script only
adds a machine index plus a provenance README. Rules distilled from the entries
live in rules.md and are maintained by hand.

Usage:
    python scripts/absorb_portable_knowledge.py            # import/refresh
    python scripts/absorb_portable_knowledge.py --check    # verify only
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

VOLUMES = [
    ("01-验证与实验设计.md", "01", "01-validation-and-experiments.md", "验证与实验设计"),
    ("02-归因与调试.md", "02", "02-attribution-and-debugging.md", "归因与调试"),
    ("03-工具链与环境.md", "03", "03-toolchain-and-environment.md", "工具链与环境"),
    ("04-语言与编译器惯用法.md", "04", "04-language-and-compiler-idioms.md", "语言与编译器惯用法"),
    ("05-性能与并发工程.md", "05", "05-performance-and-concurrency.md", "性能与并发工程"),
    ("06-GPU编程.md", "06", "06-gpu-programming.md", "GPU 编程"),
    ("07-逆向与反编译工具坑.md", "07", "07-reverse-engineering-pitfalls.md", "逆向与反编译工具坑"),
    ("08-协作与流程纪律.md", "08", "08-collaboration-and-process.md", "协作与流程纪律"),
]

ENTRY = re.compile(r"^### #((?:V)?\d+)\s+(.+?)\s*$")
SOURCE = re.compile(r"^>\s*出处[：:]\s*(.+)$")


def status_of(body: str) -> str:
    """Read the confidence from the entry's own 置信度 line.

    Labels vary: `置信度：candidate`, `**置信度**：confirmed`, or
    `**时间/置信度/module**：2609xx，candidate`. Only a bare colon-anchored
    regex misses the latter two and silently turns most entries into
    "unspecified" (the v2.15.0 index reported 3 confirmed while the source had 92).
    """
    for line in body.splitlines():
        if "置信度" not in line:
            continue
        low = line.lower()
        if "confirmed" in low:
            return "confirmed"
        if "candidate" in low:
            return "candidate"
        if "draft" in low:
            return "draft"
        return "unspecified"
    return "unspecified"

EXPECTED_TOTAL = 273


def parse_volume(path: Path, volume_id: str) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    heads = []
    for i, line in enumerate(lines):
        m = ENTRY.match(line)
        if m:
            heads.append((i, m.group(1), m.group(2)))
    entries = []
    seen: dict[str, int] = {}
    for n, (start, entry_id, title) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        body = "\n".join(lines[start:end])
        status = status_of(body)
        source = SOURCE.search(body)
        key = f"{volume_id}#{entry_id}"
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:
            key = f"{key}~{seen[key]}"
        entries.append({
            "key": key,
            "volume": volume_id,
            "id": entry_id,
            "title": title,
            "status": status,
            "source": source.group(1).strip() if source else "",
        })
    return entries


def parse_all(source: Path) -> tuple[list[dict], dict[str, int]]:
    all_entries: list[dict] = []
    counts: dict[str, int] = {}
    for src_name, volume_id, _, _ in VOLUMES:
        path = source / src_name
        if not path.is_file():
            raise FileNotFoundError(f"missing volume: {path}")
        entries = parse_volume(path, volume_id)
        counts[volume_id] = len(entries)
        all_entries.extend(entries)
    if len(all_entries) != EXPECTED_TOTAL:
        raise ValueError(f"expected {EXPECTED_TOTAL} entries, parsed {len(all_entries)}")
    return all_entries, counts


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_readme(counts: dict[str, int]) -> str:
    rows = "\n".join(
        f"| {vid} | `{slug}` | {title} | {counts[vid]} |"
        for _, vid, slug, title in VOLUMES
    )
    return f"""# Portable Knowledge（框架内置实战知识库）

> **来源**：CoreSwap 项目收尾知识盘点（2026-11-16 冻结）的 **A 类 = 跨项目可复用**条目，
> 原文逐字保留，仅按主题重分 8 卷，共 **{sum(counts.values())} 条**。
> **状态**：条目保留来源里的置信度（多数 `candidate`，部分 `confirmed`）；导入**不改变**任何结论。
> **机器索引**：[`index.yaml`](index.yaml)（key / volume / id / title / status / source）。
> **提炼规则**：[`rules.md`](rules.md)（人工维护，引用条目 key；不具规范效力）。

## 分卷

| 卷 | 文件 | 主题 | 条目 |
|---|---|---|---|
{rows}

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
- 新增来源材料：先追加到 `E:\\PYTHON\\Portable-Knowledge`，再重跑导入并人工更新 `rules.md`。
- 已知重复/近重复（来源自身标注）：`02#10` 与 `02#10~2` 是不同主题的同号条目；来源提及 `#27≈#172`、`#144≈#146`，本库保留全部、不合并。
"""


def render_index(entries: list[dict], counts: dict[str, int]) -> str:
    out = [
        "# Generated by scripts/absorb_portable_knowledge.py - do not hand-edit.",
        "schema: portable-knowledge/v1",
        'source: "CoreSwap knowledge/discovered (A-class cross-project only)"',
        'source_frozen: "2026-11-16"',
        f'generated: "{date.today().isoformat()}"',
        f"total: {len(entries)}",
        "volumes:",
    ]
    for _, vid, slug, title in VOLUMES:
        out.append(f"  - id: {q(vid)}")
        out.append(f"    file: {q(slug)}")
        out.append(f"    title: {q(title)}")
        out.append(f"    entries: {counts[vid]}")
    out.append("entries:")
    for e in entries:
        out.append(f"  - key: {q(e['key'])}")
        out.append(f"    volume: {q(e['volume'])}")
        out.append(f"    id: {q(e['id'])}")
        out.append(f"    title: {q(e['title'])}")
        out.append(f"    status: {q(e['status'])}")
        out.append(f"    source: {q(e['source'])}")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=r"E:\PYTHON\Portable-Knowledge")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "knowledge-builtin" / "portable"))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    source = Path(args.source)
    out = Path(args.out)
    entries, counts = parse_all(source)
    if args.check:
        index = out / "index.yaml"
        if not index.is_file():
            print(f"FAIL: no index at {index}")
            return 1
        total = int(re.search(r"(?m)^total: (\d+)$", index.read_text(encoding="utf-8")).group(1))
        if total != len(entries):
            print(f"FAIL: index total {total} != parsed {len(entries)}")
            return 1
        print(f"OK: {len(entries)} entries across {len(counts)} volumes; index total {total}")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    for src_name, vid, slug, _ in VOLUMES:
        shutil.copyfile(source / src_name, out / slug)
    (out / "README.md").write_text(render_readme(counts), encoding="utf-8", newline="\n")
    (out / "index.yaml").write_text(render_index(entries, counts), encoding="utf-8", newline="\n")
    print(f"OK: imported {len(entries)} entries across {len(counts)} volumes -> {out}")
    for _, vid, _, _ in VOLUMES:
        print(f"  {vid}: {counts[vid]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
