#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_skills.py — Regenerate dsh/skills/ from the canonical Reasonix skills.

Single source of truth discipline (mirrors Anchorlaw dsh/ SYNC.md):
  - The canonical skill BODIES live only in ../skills/<dot-name>/SKILL.md
    (Reasonix side of this repository). DSH adaptations must never drift
    from them: this script copies each body verbatim (LF-normalized) and
    rewrites ONLY the frontmatter (kebab-case name + whenToUse).
  - The frontmatter adaptation map (dash-name + whenToUse) lives HERE.
    Edit the map, re-run this script, then run tests/test_manifest.py.
  - ref-maintain is a DSH-only skill (no upstream counterpart); it is
    authored directly at dsh/skills/ref-maintain/SKILL.md and exempt from
    the body-drift check (test_manifest.py knows the DSH_ONLY set).

Usage:
    python dsh/scripts/sync_skills.py [--dry-run]

Exit code: 0 = regenerated; 1 = error.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # <repo>/dsh
CANON = ROOT.parent / "skills"                          # Reasonix canonical skills
OUT = ROOT / "skills"                                   # DSH-format skills

# dot-name -> (dash-name, whenToUse)
ADAPT = {
    "core.plan": (
        "core-plan",
        "任何工程任务（re-binary / re-code / swe 所有模块）开始实际分析之前，Phase 0 强制前置——轻量/重量分档架构设计，未经用户确认架构不得开始分析",
    ),
    "core.artifact": (
        "core-artifact",
        "任何产物需要落盘或索引时——.artifacts/（index.yaml 主索引 + 类/方法/函数产物）与 .investigations/（思维链）的规范与格式",
    ),
    "core.knowledge": (
        "core-knowledge",
        "分析/勘探/审查任何阶段之前先查 knowledge/INDEX.md；出现任何错误/失败、发现可复用知识或流程反模式时立即写入（错误账本优先）",
    ),
    "core.version": (
        "core-version",
        "产物更新/多假设竞争需要版本管理时——.vN 时间线历史、.bN fan-out 候选分支；禁止无用户确认删除旧产物",
    ),
    "core.fanout": (
        "core-fanout",
        "判定树分叉 ≥2 个互斥候选时 MUST 并行 fan-out（DSH 中并行派 subagent 各验一分支，产 .bN），禁止主会话逐个自推",
    ),
    "core.worker": (
        "core-worker",
        "需要隔离分析/解读原始数据或阶段产物并产出 .artifacts draft 时（DSH 中经 subagent 工具隔离执行，只返回最终答案+产物引用）",
    ),
    "core.judge": (
        "core-judge",
        "confirmed 授予前/重大转向/收尾交付 MUST、candidate 授予 SHOULD 时（DSH 中经 subagent 工具隔离执行，只出审查意见不改 status）",
    ),
    "re.lift": (
        "re-lift",
        "二进制逆向需高精度还原函数/方法时（汇编→C++ 六步流程；禁止直接信任单一反编译输出如 IDA F5）",
    ),
    "re.classify": (
        "re-classify",
        "二进制逆向需还原类/继承/vtable 结构时（RTTI/vtable/聚类识别）",
    ),
    "re.trace": (
        "re-trace",
        "二进制逆向需动态观测/验证分支、采集 anchor source 数据（trace/memory）时",
    ),
    "re.scout": (
        "re-scout",
        "「机制未明」大排查初期 MUST 只读勘探（入口/xref/依赖摸底，禁止直接跳单点定位；DSH 中经 subagent 工具隔离执行）",
    ),
    "recode.deobfuscate": (
        "recode-deobfuscate",
        "代码逆向需反混淆/映射还原时（ProGuard/R8/mapping/类名与方法名还原）",
    ),
    "recode.classmap": (
        "recode-classmap",
        "代码逆向需梳理类层次/依赖图时（类关系/继承/引用结构还原）",
    ),
    "recode.behavior": (
        "recode-behavior",
        "代码逆向需行为验证时（运行时 hook → trace source 证据，对应 Anchorlaw 全功能验证路径）",
    ),
    "recode.scout": (
        "recode-scout",
        "代码逆向「机制未明」初期 MUST 只读勘探（入口/依赖/粗略分类；DSH 中经 subagent 工具隔离执行）",
    ),
    "swe.guide": (
        "swe-guide",
        "任务是编程类（编写/修改/审查代码、协议设计、常规开发、测试）且非逆向时——入口指引路由到 Anchorlaw anchor.* 技能集（零复制）",
    ),
}

# DSH-only skills: dash-name -> description (authored directly, no upstream)
DSH_ONLY = {
    "ref-maintain": "维护 RE-Framework DSH 适配层本身——自检全绿、技能/插件/preset 同步（sync_skills.py / install.ps1）、上游变更镜像（SYNC.md）、提交纪律（对齐 anchor-maintain 思路）",
}


def parse_frontmatter(text):
    """Return (frontmatter dict, body) for this repo's SKILL.md shape."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip("'\"")
    return fm, text[end + 4:]


def body_of(text):
    _, body = parse_frontmatter(text)
    return body.replace("\r\n", "\n").strip()


def main():
    dry = "--dry-run" in sys.argv
    failures = []

    if not CANON.is_dir():
        failures.append(f"canonical skills dir missing: {CANON}")
        print("\n".join(failures))
        return 1

    generated = []
    for dot_name, (dash_name, when_to_use) in sorted(ADAPT.items()):
        canon_md = CANON / dot_name / "SKILL.md"
        if not canon_md.is_file():
            failures.append(f"canonical missing: {canon_md}")
            continue
        text = canon_md.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        desc = fm.get("description", "")
        body = body_of(text)
        out_dir = OUT / dash_name
        out_md = out_dir / "SKILL.md"
        if not dry:
            out_dir.mkdir(parents=True, exist_ok=True)
            content = (
                "---\n"
                f"name: {dash_name}\n"
                f"description: {desc}\n"
                f"whenToUse: {when_to_use}\n"
                "---\n"
                "\n"
                f"{body}\n"
            )
            out_md.write_text(content, encoding="utf-8", newline="\n")
        generated.append(f"{dot_name} -> {dash_name}")

    for dash_name, desc in sorted(DSH_ONLY.items()):
        out_md = OUT / dash_name / "SKILL.md"
        if not out_md.is_file() and not dry:
            failures.append(f"DSH-only skill missing (author it directly): {out_md}")
        else:
            generated.append(f"(DSH-only) {dash_name}")

    if failures:
        print("\n".join(failures))
        return 1

    print(f"OK: {len(generated)} skills{' (dry-run)' if dry else ' regenerated'}:")
    for g in generated:
        print(f"  - {g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
