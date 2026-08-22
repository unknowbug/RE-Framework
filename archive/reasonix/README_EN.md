# RE-Framework v2 — Generic Engineering Methodology Framework (Reverse Engineering + Programming)

> **[English](README_EN.md) | [中文](README.md)**

> Built on the methodology of *A New Approach to AI Reverse Engineering: Multi-Agent, Self-Managed Context* (BitWarden, Kanxue Forum, 2026.06.18),
> engineered, skill-ified, and sub-agent-ified: **a domain-agnostic core + on-demand domain modules**, covering binary reverse engineering, code reverse engineering, and general programming.
> Verification protocol: references [Anchorlaw Protocol v0.18](https://github.com/unknowbug/anchorlaw) (MIT, protocol reference — no implementation copied).
> **Dual-host support (v2.1)**: Reasonix (deploy to `.reasonix/skills/`) + **DeepSeek Harness** (`dsh/` subtree, `re-framework` preset).

---

## What changed in v2 (vs v1)

| Dimension | v1 (single 42KB file) | v2 (modular framework) |
|-----------|----------------------|------------------------|
| Entry point | CLAUDE.md fully loaded | AGENTS.md detector → load only the matching module by task type |
| Domains | Binary reverse engineering only | `core` (generic) + `re-binary` (binary RE) + `re-code` (bytecode/Minecraft RE) + `swe` (programming) |
| Verification | Referenced Practify (dead link) | References Anchorlaw v0.18 (single source of truth) |
| Dynamic tracing | Missing | `re.trace` / `recode.behavior` (anchor source data) |
| Knowledge base | Empty TODO | Real quick-reference entries (calling-conventions/cpp-abi/common-patterns/assembly-reference/anti-re) |
| Sub-agents | Role concept | Subagent role contracts (scout/worker/judge, aligned with Anchorlaw §15) |

## Hosts

| Host | How it consumes the framework | Status |
|------|-------------------------------|--------|
| **Reasonix** | `scripts/install.py` deploys `skills/` into a project's `.reasonix/skills/` (version-stamped, uninstallable); root `AGENTS.md` is the detector | v1/v2 native |
| **DeepSeek Harness (DSH)** | `dsh/` subtree: 17 `ref-*` skills + 5 `ref_*` model tools + `re-framework` agent preset; see `dsh/README.md` | v2.1 (2026-08-14) |

## Repository layout

```
RE-Framework/
├── AGENTS.md                  # Detector entry: task-type router + skill trigger table (replaces v1 CLAUDE.md)
├── README.md / README_EN.md   # This documentation (中文 / English)
├── spec/
│   ├── engineering-framework-v1.md   # Core protocol (iron rules + modular interface contract + Anchorlaw reference)
│   └── legacy-claude-v1.md           # v1's original 42KB CLAUDE.md (historical archive)
├── scripts/                   # Engineering shell
│   ├── validate_manifest.py   # Manifest validator (spec §2.5 R1-R6)
│   └── install.py             # Install/upgrade/uninstall (version-stamp tracked)
├── skills/                    # Skill reference implementations (shipped to projects' .reasonix/skills/)
│   ├── core.plan|artifact|knowledge|version|fanout|judge   # Generic layer (mandatory)
│   ├── re.lift|classify|trace|scout                        # re-binary module
│   ├── recode.deobfuscate|classmap|behavior|scout          # re-code module
│   ├── swe.guide                                           # swe module (→ Anchorlaw)
│   └── modules/{core,re-binary,re-code,swe}.yaml           # Module declarations (triggers/deps/uninstall guarantees)
├── templates/                 # Artifact schemas (language-agnostic: address/bytecode-offset/class-name locators)
├── knowledge-builtin/         # Built-in knowledge base (calling-conventions/cpp-abi/...)
├── memory/                    # Memory files (optional)
└── dsh/                       # DSH host adaptation (17 skills + 5 tools + re-framework preset + maintenance scripts)
```

## Core iron rules (condensed; full text in spec §1)

1. **Confidence state machine** — every artifact starts `draft` → evidence-backed `candidate`; `confirmed` is granted **only by the human**, never by the AI. Reviewers give opinions, never change status.
2. **Artifacts must be persisted** — conclusions → `.artifacts/` (with `index.yaml`), reasoning chains → `.investigations/`; never chat-only.
3. **Anti-hallucination** — every claim is either traceably verified or explicitly marked `@anchor.idk`; `@anchor.test` requires a `source` (trace/memory, never static).
4. **Module boundaries** — no cross-module skill-body references (spec §1.6); modules install/uninstall independently (spec §2.4).
5. **Context isolation** — split oversized tasks; one investigation directory per subtask.

## Modules

| Module | Scope | Dependencies | Default |
|--------|-------|--------------|---------|
| `core` | Confidence/artifacts/planning/review/knowledge base | none | ✅ mandatory |
| `re-binary` | Assembly/machine code/vtable/RTTI/xref/trace | IDA/Frida/x64dbg/CheatEngine + Anchorlaw degraded | optional |
| `re-code` | Bytecode/deobfuscation/class-hierarchy/behavior (e.g. Minecraft) | decompiler + JVM/toolchain + Anchorlaw | optional |
| `swe` | General development/verification/review | anchorlaw CLI + anchorlaw-scanner | optional |

Each module ships: skill set + trigger table + dependency declaration + uninstall guarantee (`skills/modules/*.yaml`, spec §2).

## Quick start

### Reasonix (classic) — 3 steps

```bash
# Step 1 — deploy (pick modules)
python RE-Framework/scripts/install.py <your-project> --modules core            # minimal
python RE-Framework/scripts/install.py <your-project> --modules core,re-binary  # binary RE
python RE-Framework/scripts/install.py <your-project> --modules core,re-code    # code RE
python RE-Framework/scripts/install.py <your-project> --modules core,swe        # programming
python RE-Framework/scripts/install.py <your-project> --modules core,re-binary,re-code,swe --docs  # full + Anchorlaw
pip install anchorlaw anchorlaw-scanner

# upgrade: re-run install.py (detects stamp) · uninstall: --uninstall · validate: validate_manifest.py
```

```text
Step 2 — initialize the project skeleton:
  "帮我初始化这个工程项目的基础目录结构" → creates .artifacts/, .investigations/, knowledge/ + index.yaml

Step 3 — start working:
  the AGENTS.md detector routes dll → re-binary, jar → re-code, code-writing → swe, then runs Phase 0 architecture design.
```

### DeepSeek Harness (DSH) — v2.1

```powershell
# 1. Install the re-framework preset into the DSH runtime (skills preset-embedded only)
pwsh dsh/scripts/install.ps1

# 2. Open a new session on the 're-framework' preset with this repo root as the working directory
#    → 17 ref-* skills + 5 ref_* tools (status/validate/install/merge-index/init)
#    + Phase 0-3 workflow persona with the enforcement chain (scout/fan-out/judge/knowledge)

# 3. Self-check (toolchain / skill-manifest zero-drift / framework self-scan R1-R6 / installed artifacts)
pwsh dsh/scripts/selfcheck.ps1
```

See `dsh/README.md` for details; source-of-truth & sync discipline in `dsh/AGENTS.md`.

## Verification protocol (referenced, not maintained here)

All verification/execution/integration semantics reference [Anchorlaw v0.18](https://github.com/unknowbug/anchorlaw) — single source of truth:

- **Claim** (§13 + §5): `@anchor.test` / `@anchor.idk`, source rules (trace/memory/probe; static only for idk), source-artifact requirement, staleness, health states.
- **Knowledge** (§14): this framework's AGENTS.md + skill manifest follow the modular on-demand-loading model.
- **Execution** (§15): subagent role isolation (scout/worker/judge); domain narrowing (v0.13, retained in v0.18) — reverse engineering is explicitly **out of protocol domain** (exploratory), construction domain follows the Anchorlaw pipeline; retry cap = evidence saturation (3 rounds without new data-layer evidence force a return to the data layer); C-gate halted escalation (v0.15); execution-mode selection (convergent inline / divergent may subprocess).
- **Host** (§16): AGENTS.md as the host integration point; confirm hook (`confirmed` only by the human); input-contract confirmation criterion (v0.14, semantic convergence, protocol-neutral).

**Upgrade check** (spec §3): after a new Anchorlaw release, run `git grep 'v0\.[0-9]'` and verify every cited clause. Current baseline: **v0.18** (checked 2026-08-15; §5/§9/§12/§13/§14/§15/§16 all retained; v0.16 = Go/Java comment-form registration + Rust unsupported by design; v0.17 = parse-error marker, comment-form downgrade to annotation-extraction only, P7-P10 optional reliability patterns; v0.18 = DSH host adaptation registered as the first full §16 Host Integration implementation — same host family as this framework). Note the co-evolution: v0.17 changes include outcomes of a "§12 challenge (Reasonix/Go audit)" — feedback from this ecosystem has flowed back into the protocol.

## Update log

| Version | Date | Content |
|---------|------|---------|
| v2.1 | 2026-08-14 | **DSH host adaptation** (new `dsh/` subtree: 17 `ref-*` skills with zero body drift + `ref-maintain`, 5 `ref_*` tools, `re-framework` preset — Reasonix side untouched, dual-host coexistence); **Anchorlaw reference upgraded v0.15 → v0.17** (clause check all retained; Go/Java registration, Rust unsupported, parse-error, comment-form downgrade, P7-P10 optional); error-ledger knowledge mechanism (`discovered/errors/`, error-over-correct priority) |
| v2.0 | 2026-08 | Modular rewrite: core + re-binary + re-code + swe, AGENTS.md detector, Anchorlaw protocol reference (see the v2-vs-v1 table above) |
| v1.0 | 2026-06 | Single-file 42KB CLAUDE.md (BitWarden methodology) → archived as `spec/legacy-claude-v1.md` |

## Methodology source

- Original article: *A New Approach to AI Reverse Engineering: Multi-Agent, Self-Managed Context* (BitWarden, Kanxue Forum, 2026.06.18)
- Verification protocol: [Anchorlaw Protocol v0.18](https://github.com/unknowbug/anchorlaw) (MIT; formerly Practify)
