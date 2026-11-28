#!/usr/bin/env python3
"""Portable-Knowledge data-integrity test.

Guards the two defects found on 2026-11-28:
  * the importer must read the entry's own 置信度 line (the v2.15.0 index
    reported 3 confirmed while the source has 92);
  * every key cited by rules.md must exist in index.yaml (4 keys had the wrong
    volume prefix).

Also checks that P01-P40 exist and that the non-GPU rules were merged into at
least one skill checklist.
"""

from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
PORTABLE = ROOT / "knowledge-builtin" / "portable"
SKILLS = ROOT / "dsh" / "skills"

failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        failures.append(f"{name}{(': ' + detail) if detail else ''}")


def main() -> int:
    index = yaml.safe_load((PORTABLE / "index.yaml").read_text(encoding="utf-8"))
    rules = (PORTABLE / "rules.md").read_text(encoding="utf-8")

    entries = index.get("entries") or []
    check("total entries", index.get("total") == 273 and len(entries) == 273, str(len(entries)))
    check("volumes", len(index.get("volumes") or []) == 8)

    status = {}
    for entry in entries:
        status[entry["status"]] = status.get(entry["status"], 0) + 1
    check("confirmed count", status.get("confirmed") == 92, str(status))
    check("candidate count", status.get("candidate") == 120, str(status))
    check("draft count", status.get("draft") == 6, str(status))
    check("unspecified count", status.get("unspecified") == 55, str(status))

    keys = [e["key"] for e in entries]
    check("unique keys", len(keys) == len(set(keys)))

    cited = set(re.findall(r"`(\d{2}#[^`]+)`", rules))
    check("cited keys exist", cited <= set(keys), str(sorted(cited - set(keys))))
    check("cited count", len(cited) == 77, str(len(cited)))

    labels = set(re.findall(r"\*\*\[(P\d{2})\]\*\*", rules))
    check("P01-P40 present", labels == {f"P{i:02d}" for i in range(1, 41)}, str(len(labels)))

    text = "\n".join(p.read_text(encoding="utf-8") for p in SKILLS.glob("*/SKILL.md"))
    for code in [f"P{i:02d}" for i in list(range(1, 35)) + [38, 39, 40]]:
        if code not in text:
            failures.append(f"rule {code} is not merged into any skill")
    for code in ("P35", "P36", "P37"):
        if code in text:
            failures.append(f"GPU rule {code} must stay out of skills until the GPU pass")

    # Contract/spec consistency: §5.8 exists, index fragments are allowed, and the
    # artifact templates carry the producer the work order requires.
    spec = (ROOT / "spec" / "engineering-framework-v1.md").read_text(encoding="utf-8")
    check("spec 5.8 present", "### 5.8 等价性证据形态阶梯" in spec)
    check("spec index fragments", "index-entry.yaml" in spec)
    for name in ("class.yaml", "function.yaml", "method.yaml", "xref.yaml", "index.yaml"):
        body = (ROOT / "templates" / name).read_text(encoding="utf-8")
        check(f"{name} producer field", "producer" in body)

    if failures:
        print(f"FAIL ({len(failures)}):")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("OK: 273 entries, 92 confirmed / 120 candidate / 6 draft / 55 unspecified; 77 cited; P01-P40 present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
