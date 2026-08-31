#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_cheatsheet.py — 从台账条目 front-matter 机械生成速查表（RE-Framework 压实机制·派生视图模板）

提案来源: CoreSwap knowledge-compaction proposal 3.2（派生视图禁止手维护——
纪律依赖机械生成，同源消除视图失步）。本文件是**框架模板**：项目复制到自己的
scripts/ 下适配（如台账路径、输出列），不要手改生成产物。

用法:
    python gen_cheatsheet.py <ledger_dir_or_file>... [-o output.md]

行为:
    - 扫描给定路径（目录递归或单文件）下的 *.md 台账条目
    - 解析每条的 YAML front-matter（id/status/supersedes/superseded_by/signature/verdict/lesson）
    - 生成速查表 markdown：按 id 排序，含状态标记 + 当前有效结论视图
      （superseded 条目标注"被 <id> 取代"，supersedes 链可机械回答"当前有效结论 + 历史"）
    - 手改生成产物 = 无效操作（下次生成即覆盖）

退出码: 0 = 生成成功; 2 = 参数/IO 错误
"""

import argparse
import re
import sys
from pathlib import Path

# Windows 控制台常为 GBK——状态标记（⚠️/✅/❌/📦）无法编码；stdout 强制 UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

STATUS_MARK = {"open": "⚠️", "closed": "✅", "superseded": "❌", "consolidated": "📦"}


def parse_frontmatter(text):
    """Parse a simple flat YAML front-matter (key: value lines only)."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip("'\"")
    return fm


def collect_entries(paths):
    entries = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files = sorted(path.rglob("*.md"))
        elif path.is_file():
            files = [path]
        else:
            print(f"! skip (not found): {path}", file=sys.stderr)
            continue
        for md in files:
            fm = parse_frontmatter(md.read_text(encoding="utf-8"))
            if "id" not in fm or "signature" not in fm:
                continue  # not a ledger entry (no front-matter contract)
            entries.append(fm)
    return entries


def render(entries):
    by_id = {e["id"]: e for e in entries if e.get("id")}
    lines = [
        "# 错误台账速查表（机械生成，勿手改）",
        "",
        "> 生成: gen_cheatsheet.py（压实机制·派生视图）。手改无效——改条目 front-matter 后重新生成。",
        "",
        "| id | 状态 | 现象签名 | 根因 | 教训 |",
        "|----|------|----------|------|------|",
    ]
    for eid in sorted(by_id):
        e = by_id[eid]
        mark = STATUS_MARK.get(e.get("status", ""), "")
        verdict = e.get("verdict", "")
        if e.get("status") == "superseded" and e.get("superseded_by"):
            verdict = f"~~{verdict}~~ → 被 {e['superseded_by']} 取代"
        lines.append(
            f"| {eid} | {mark} {e.get('status', '')} | {e.get('signature', '')} | {verdict} | {e.get('lesson', '')} |"
        )
    # supersession chain summary (mechanically answerable "current valid conclusion")
    chains = [e["id"] for e in entries if e.get("supersedes")]
    if chains:
        lines.append("")
        lines.append("## Supersession 链")
        for eid in sorted(chains):
            e = by_id.get(eid, {})
            sup = e.get("supersedes", "")
            lines.append(f"- {eid} supersedes {sup}" + (f"（{by_id[sup].get('verdict', '')} → {e.get('verdict', '')}）" if sup in by_id else ""))
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="从台账条目 front-matter 机械生成速查表")
    ap.add_argument("paths", nargs="+", help="台账目录（递归）或条目文件")
    ap.add_argument("-o", "--output", default=None, help="输出 markdown（缺省 stdout）")
    args = ap.parse_args()

    entries = collect_entries(args.paths)
    if not entries:
        print("no ledger entries with front-matter found", file=sys.stderr)
        return 2

    out = render(entries)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8", newline="\n")
        print(f"cheatsheet written: {args.output} ({len(entries)} entries)")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
