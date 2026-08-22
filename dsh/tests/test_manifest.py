"""test_manifest.py — validate the 17 ref-* skill manifests for DSH.

DSH requirements (dsh-skill-filesystem):
  - name must match /^[a-z0-9]+(?:-[a-z0-9]+)*$/ (kebab-case)
  - description is required
Optional: whenToUse (string). Unknown fields are ignored by DSH.

Since the Reasonix host format was archived (archive/reasonix/, 2026-08-21),
dsh/skills/ is the SINGLE skill source of truth — this check validates the DSH
manifests themselves (naming, frontmatter shape, expected set) and the
cross-reference map (every dot-name reference in a body must resolve to a
skill in this set via ADAPT, or be an Anchorlaw external interface); no
upstream cross-check remains.

Exit code 0 = pass; 1 = any check failed.
"""

import re
import sys
from pathlib import Path

SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DOT_REF = re.compile(r"`([a-z]+\.[a-z]+)`")
FILE_EXT_BLACKLIST = (".yaml", ".txt", ".md", ".json", ".yml", ".py")  # 正则误匹配过滤

# This file lives at <repo>/dsh/tests/test_manifest.py
ROOT = Path(__file__).resolve().parent.parent          # <repo>/dsh
SKILLS_DIR = ROOT / "skills"                            # single skill source of truth

# dot-name -> kebab-name（技能正文内的规范名引用解析表；与 dsh/SKILL-MAP.md 映射一致）
ADAPT = {
    "core.plan": "core-plan",
    "core.artifact": "core-artifact",
    "core.knowledge": "core-knowledge",
    "core.version": "core-version",
    "core.fanout": "core-fanout",
    "core.worker": "core-worker",
    "core.judge": "core-judge",
    "re.lift": "re-lift",
    "re.classify": "re-classify",
    "re.trace": "re-trace",
    "re.scout": "re-scout",
    "recode.deobfuscate": "recode-deobfuscate",
    "recode.classmap": "recode-classmap",
    "recode.behavior": "recode-behavior",
    "recode.scout": "recode-scout",
    "swe.guide": "swe-guide",
}
EXPECTED = set(ADAPT.values()) | {"ref-maintain"}


def parse_frontmatter(text: str) -> tuple[dict, str]:
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


def main() -> int:
    failures = []
    warnings = []

    if not SKILLS_DIR.is_dir():
        failures.append(f"skills dir missing: {SKILLS_DIR}")
        print("\n".join(failures))
        return 1

    found = set()
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        md = skill_dir / "SKILL.md"
        name = skill_dir.name
        if not md.is_file():
            failures.append(f"{name}: missing SKILL.md")
            continue
        text = md.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        found.add(name)

        # name
        if fm.get("name") != name:
            failures.append(f"{name}: frontmatter name '{fm.get('name')}' != dir name '{name}'")
        if not SKILL_NAME.match(name):
            failures.append(f"{name}: not kebab-case (DSH rejects it)")

        # description
        desc = fm.get("description")
        if not desc:
            failures.append(f"{name}: missing required description")

        # whenToUse optional: must be a string when present
        wtu = fm.get("whenToUse")
        if wtu is not None and not isinstance(wtu, str):
            failures.append(f"{name}: whenToUse must be a string")

        # Reasonix-era frontmatter fields must not appear (archived format)
        for legacy in ("kind", "runAs", "layer", "execution"):
            if legacy in fm:
                warnings.append(f"{name}: legacy Reasonix frontmatter field '{legacy}' present")

    # completeness
    missing = EXPECTED - found
    if missing:
        failures.append(f"missing skills: {sorted(missing)}")
    extra = found - EXPECTED
    if extra:
        failures.append(f"unexpected skills: {sorted(extra)}")

    # cross-reference map: every `dot.ref` in a body must resolve via ADAPT to
    # a skill in this set, or be an Anchorlaw external interface (anchor.*)
    refs = set()
    for skill_dir in SKILLS_DIR.iterdir():
        md = skill_dir / "SKILL.md"
        if md.is_file():
            _, body = parse_frontmatter(md.read_text(encoding="utf-8"))
            refs |= set(DOT_REF.findall(body))
    for ref in sorted(refs):
        if ref.startswith("anchor."):
            continue  # Anchorlaw external interface (protocol reference)
        if ref.endswith(FILE_EXT_BLACKLIST):
            continue  # file extension, not a skill reference
        if ADAPT.get(ref) is None or ADAPT[ref] not in EXPECTED:
            failures.append(f"reference '{ref}' has no DSH counterpart "
                            f"(expected '{ADAPT.get(ref) or ref.replace('.', '-')}' in the skill set)")

    if warnings:
        print(f"WARN ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"OK: {len(found)} ref skills valid (dsh/skills is the single source of truth)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
