# RE-Framework v2

> **A general engineering methodology framework for reverse engineering + programming.** DeepSeek Harness (DSH) is its only maintained host.
> Verification semantics reference [Anchorlaw Protocol v0.27.1](https://github.com/unknowbug/anchorlaw) (protocol reference; no implementation copied).

RE-Framework is not a prompt collection. It turns evidence-driven analysis and implementation into an executable flow: read the knowledge base → design the architecture → scout → analyze → verify → independent review → human confirmation → archive. The framework maintains itself: skills, preset, tools and self-checks live in this one repository, and every change must pass fail-closed gates.

## What it prevents

| Common failure | Constraint |
|---|---|
| Conclusions live only in chat and are lost | Artifacts must land in `.artifacts/` / `.investigations/`, with the index updated |
| AI self-evaluates and bad conclusions get promoted | `confirmed` is granted only by a human; judge reviews independently |
| Competing hypotheses are reasoned in one head | Mutually exclusive hypotheses MUST fan-out; branches stay isolated with `.bN` candidates |
| Big projects pile artifacts by "domain" | Artifacts/code/knowledge are partitioned by the **target program's own modules** (spec §5.7) |
| Subagents are anonymous and untraceable | Work Order contract + DSH name + `producer` (spec §4.6) |
| Line counts masquerade as "equivalence" | Equivalence evidence ladder E1/E2/E3 (spec §5.8) |
| The same failure returns | Error ledger first + 273 field cases + a known-regressions gate |

## Core mechanics

- **Evidence first**: `@anchor.test` needs a traceable source (trace/memory/probe); static inference goes to `@anchor.idk`.
- **Role isolation**: scout / worker / judge / fan-out run as subagents; the main session orchestrates and executes, never replaces analysis or self-review.
- **Enforced chain**: judge (before confirmation / pivot / delivery), scout (mechanism unknown), fan-out (≥2 exclusive hypotheses), knowledge (conclusion persistence) — planned up front, only checked during execution.
- **Target modularity**: modules come from build files/RTTI/namespaces; artifacts, code and knowledge are placed per target module; corrections go plan→apply→rollback.
- **Collaboration contract**: every delegation carries a Work Order; the Lead is the only root-index writer; task completion ≠ conclusion confirmation.
- **Knowledge growth**: the error ledger outranks correct conclusions; `knowledge-builtin/portable/` holds 273 field cases and 40 distilled rules.

## Quick start (DSH)

Prerequisites: Python 3.x; Node.js ≥ 24.22.3 (a DSH requirement).

```powershell
# 1. Install/sync: bundle → every profile, 17 skills → user-global
pwsh dsh/scripts/install.ps1

# 2. Self-check (eight sections, must be green)
pwsh dsh/scripts/selfcheck.ps1

# 3. Open a session in any project (ref-* skills load in any preset)
#    Pick the re-framework preset when you want the full workbench persona
```

DSH Desktop (Electron / `app.asar`) is covered by the same install; restart Desktop and choose RE-Framework in a new session. See [dsh/README.md](dsh/README.md).

## Install from the DSH plugin market

RE-Framework is packaged as a DSH bundle: the repository-root `package.json` declares `dsh.bundle.patch`.

```powershell
# Source install (available through Plugin Hub now; requires DSH >= 0.2.0)
dsh plugin --profile web add github:unknowbug/RE-Framework

# npm install (2.20.0 is published; the in-app plugin center needs npm)
dsh plugin --profile web add @unknowerror/dsh-re-framework
```

- **Plugin Hub category**: Skills & Agents (agent) → subagents / skill packs; not Development & Operations.
- **Compatibility**: DSH `>=0.2.0 <0.3.0`; the same bundle works in Desktop and CLI; restart and open a new session after install.
- **Permissions**: workspace file read/write, subprocess (python scripts), subagent tools; no network requests, no credentials outside the workspace.
- **License**: MIT (see [LICENSE](LICENSE)).

## Architecture

```
RE-Framework/
├── AGENTS.md                  # DSH-first index (auto-loaded entry)
├── package.json               # DSH bundle entry (Plugin Hub / npm packaging)
├── LICENSE                    # MIT
├── spec/                      # Framework protocol (§1-§9; §4.6 contract, §5.7 modules, §5.8 evidence ladder)
├── dsh/                       # DSH host adaptation (the only maintained area)
│   ├── skills/                # 17 ref-* skills (single source of truth)
│   ├── SKILL-MAP.md           # DSH detector: init / routing / Phase 0-3
│   ├── plugins/               # 3 ref_* tools + contract guard (R1/R3/R5)
│   ├── cordis.patch.yml       # agent preset declaration (bundle-patch carrier)
│   ├── scripts/               # install / selfcheck / patch_layer / target_modules
│   └── tests/                 # row/variable/regression/work-order/portable/guard tests
├── templates/                 # Artifact schemas + agent-work-order.yaml
├── knowledge-builtin/         # Built-in knowledge; portable/ = 273 field cases + rules.md
├── scripts/                   # merge_index.py / absorb_portable_knowledge.py
├── CHANGELOG.md / CHANGELOG_EN.md   # Release history (README no longer carries it)
└── archive/reasonix/          # Reasonix host format archive (read-only)
```

## Modules and skills

| Module | Skills (kebab names) | Entry |
|---|---|---|
| core | `core-plan` `core-artifact` `core-knowledge` `core-version` `core-fanout` `core-worker` `core-judge` | every task |
| re-binary | `re-scout` `re-lift` `re-classify` `re-trace` | binaries/assembly/IDA/Ghidra/vtable/RTTI |
| re-code | `recode-scout` `recode-deobfuscate` `recode-classmap` `recode-behavior` | bytecode/source/deobfuscation/mods |
| swe | `swe-guide` → Anchorlaw `anchor-*` | write/modify/review code, tests |
| maintenance | `ref-maintain` | maintain this DSH adaptation |

17 skills in total; the `re-framework` preset adds three `ref_*` tools (status / merge_index / init) and the contract guard. Skills are visible to any preset session; tools exist only inside the re-framework preset.

## Document map

| Question | Read |
|---|---|
| Framework rules (iron rules/workflow/artifacts/knowledge/versioning) | [spec/engineering-framework-v1.md](spec/engineering-framework-v1.md) |
| DSH maintenance (install/self-check/preset/Desktop) | [dsh/AGENTS.md](dsh/AGENTS.md) |
| How a session starts and routes | [dsh/SKILL-MAP.md](dsh/SKILL-MAP.md) |
| Release history and version naming | [CHANGELOG_EN.md](CHANGELOG_EN.md) |
| 273 field cases and 40 rules | [knowledge-builtin/portable/README.md](knowledge-builtin/portable/README.md) |
| Artifact templates | [templates/README.md](templates/README.md) |

## Maintenance and versioning

- The **single source of truth** for skills is `dsh/skills/`; installed artifacts are regenerable. Re-run `install.ps1` after edits; never hand-edit `~/.dsh`.
- Every change must pass all eight self-check sections; gates are fail-closed (unable to run counts as failure).
- Versioning: release `X.Y.Z`, where `Z` is a FIX (no new spec file); the protocol version is separate (currently v1). Full rules and history: [CHANGELOG_EN.md](CHANGELOG_EN.md).

## License

MIT. See [LICENSE](LICENSE).

## Archive

The Reasonix host format (dot-named skills, `.reasonix/skills/`, `install.py`/`validate_manifest.py`) stopped being maintained on 2026-08-21 and is archived under `archive/reasonix/` (RESTORE.md included). The framework core (`spec/`, `templates/`, `knowledge-builtin/`, `scripts/merge_index.py`) remains.
