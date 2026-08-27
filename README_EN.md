# RE-Framework v2 — Generic Engineering Methodology Framework (Reverse Engineering + Programming, DSH Host)

> [English](README_EN.md) | [中文](README.md)

> Built on the methodology of *A New Approach to AI Reverse Engineering: Multi-Agent, Self-Managed Context* (BitWarden, Kanxue Forum, 2026.06.18),
> engineered, skill-ified, and sub-agent-ified: **a domain-agnostic core + on-demand domain modules**, covering binary reverse engineering, code reverse engineering, and general programming.
> **DeepSeek Harness (DSH) is the only maintained host** (since 2026-08-21; the Reasonix host format is archived under `archive/reasonix/`, fork-restorable).
> Verification protocol: references [Anchorlaw Protocol v0.19](https://github.com/unknowbug/anchorlaw) (MIT, protocol reference — no implementation copied).

---

## Quick start (DSH)

```powershell
# 1. Install into the DSH runtime (one-shot)
pwsh dsh/scripts/install.ps1
#    → user-global skills: 17 ref-* into ~/.dsh/skills/ (loadable from any session/preset/workspace)
#    → re-framework preset: full workbench (persona + 3 ref_* tools: status/merge_index/init)

# 2. Open a session in any project (e.g. E:\PYTHON\CoreSwap) on any preset
#    → ref-* skills work out of the box; cwd stays in the project, artifacts land there,
#      this repository stays untouched
#    → choose the re-framework preset when you want the full workbench persona

# 3. Self-check (toolchain / skill manifest / installed artifacts / plugin schemas)
pwsh dsh/scripts/selfcheck.ps1
```

**Standard DSH-session flow**: root `AGENTS.md` (DSH-first index) → read `dsh/SKILL-MAP.md` first (DSH detector: init discipline / task routing / Phase 0-3 / enforcement chain) → load skills by **kebab name**.

## Architecture

```
RE-Framework/
├── AGENTS.md                  # DSH-first index (auto-loaded entry)
├── spec/                      # Framework protocol (iron rules/workflow/artifacts/knowledge/versioning) + Anchorlaw v0.19 reference
├── dsh/                       # DSH host adaptation (the only maintained area)
│   ├── skills/                # 17 ref-* skills (single source of truth, edited directly)
│   ├── SKILL-MAP.md           # DSH detector (init/routing/Phase 0-3/enforcement chain + dot→kebab map)
│   ├── plugins/re-framework-tools.js   # 3 ref_* model tools
│   ├── preset/                # re-framework agent preset
│   ├── scripts/install.ps1 + selfcheck.ps1   # install + 4-item self-check
│   ├── tests/                 # test_manifest.py + check_plugin_schema.mjs
│   └── AGENTS.md              # DSH maintenance entry
├── templates/                 # Artifact schemas (language-agnostic)
├── knowledge-builtin/         # Built-in knowledge base
├── scripts/merge_index.py     # Parallel index merge (ref_merge_index dependency)
└── archive/reasonix/          # Reasonix host format archive (read-only, RESTORE.md restorable)
```

## Skills (17, kebab names)

| Module | Skills (kebab) | Purpose |
|--------|----------------|---------|
| core | `core-plan` / `core-artifact` / `core-knowledge` / `core-version` / `core-fanout` / `core-worker` / `core-judge` | architecture / artifacts / knowledge / versioning / fan-out / worker role / judge role |
| re-binary | `re-lift` / `re-classify` / `re-trace` / `re-scout` | lift / class-identify / dynamic trace / recon |
| re-code | `recode-deobfuscate` / `recode-classmap` / `recode-behavior` / `recode-scout` | deobfuscation / classmap / behavior / recon |
| swe | `swe-guide` | programming entry (→ Anchorlaw, pure reference) |
| DSH-only | `ref-maintain` | DSH adaptation maintenance |

## Relationship with Anchorlaw (pure-reference install, zero copy)

| Dependency layer | How |
|------------------|-----|
| Protocol | spec §3 cites the clauses (single source of truth; upgrade check per sync contract) |
| Skills | `swe-guide` routes to `anchor-*` (installed user-global by the Anchorlaw host install.ps1; RE copies nothing) |
| Tools | `anchorlaw_*` (provided by the Anchorlaw plugin; RE references) |
| CLI | `anchorlaw` / `anchorlaw-scanner` (pip packages, installed on the Anchorlaw side) |

## Archive note

- The **Reasonix host format** (dot-name skills, `.reasonix/skills/` deployment, `install.py`/`validate_manifest.py`) stopped being maintained on 2026-08-21 and is archived under `archive/reasonix/` (with RESTORE.md + restore-reasonix.ps1 for fork maintainers).
- Framework core (`spec/`, `templates/`, `knowledge-builtin/`, `scripts/merge_index.py`) stays; DSH skill bodies reference them.

## Update log

| Version | Date | Content |
|---------|------|---------|
| v2.2 | 2026-08-21 | **DSH-only host migration**: Reasonix archived (`archive/reasonix/`), `dsh/skills/` single source of truth, tools 5→3, root AGENTS.md DSH-first, simplified install, pure-reference Anchorlaw; knowledge value gate (P1/P2/P3); Anchorlaw v0.18→v0.19 (verification-scope clarification) |
| v2.1 | 2026-08-14~15 | DSH adaptation (`dsh/` subtree), user-global skills, preset-only tools, Anchorlaw v0.15→v0.17→v0.18, SKILL-MAP DSH detector, error-ledger hardening |
| v2.0 | 2026-08 | Modular rewrite (Reasonix era, archived) |
| v1.0 | 2026-06 | Single 42KB CLAUDE.md (BitWarden methodology, archived) |
