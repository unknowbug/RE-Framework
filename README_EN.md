# RE-Framework v2 — Generic Engineering Methodology Framework (Reverse Engineering + Programming, DSH Host)

> [English](README_EN.md) | [中文](README.md)

> Built on the methodology of *A New Approach to AI Reverse Engineering: Multi-Agent, Self-Managed Context* (BitWarden, Kanxue Forum, 2026.06.18),
> engineered, skill-ified, and sub-agent-ified: **a domain-agnostic core + on-demand domain modules**, covering binary reverse engineering, code reverse engineering, and general programming.
> **DeepSeek Harness (DSH) is the only maintained host** (since 2026-08-21; the Reasonix host format is archived under `archive/reasonix/`, fork-restorable).
> Verification protocol: references [Anchorlaw Protocol v0.24](https://github.com/unknowbug/anchorlaw) (MIT, protocol reference — no implementation copied).

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

# 3. Self-check (toolchain / skill manifest / installed artifacts / plugin schemas / preset gates / target modules + guard)
pwsh dsh/scripts/selfcheck.ps1

# 4. Target modularity (recommended for large projects; spec §5.7)
python scripts/target_modules.py <project> derive   # derive target modules -> partition artifacts/code/knowledge
python scripts/target_modules.py <project> verify   # gates G1-G9
```

**Standard DSH-session flow**: root `AGENTS.md` (DSH-first index) → read `dsh/SKILL-MAP.md` first (DSH detector: init discipline / task routing / Phase 0-3 / enforcement chain) → load skills by **kebab name**.

## Architecture

```
RE-Framework/
├── AGENTS.md                  # DSH-first index (auto-loaded entry)
├── spec/                      # Framework protocol (iron rules/workflow/artifacts/knowledge/versioning) + Anchorlaw v0.24 reference
├── dsh/                       # DSH host adaptation (the only maintained area)
│   ├── skills/                # 17 ref-* skills (single source of truth, edited directly)
│   ├── SKILL-MAP.md           # DSH detector (init/routing/Phase 0-3/enforcement chain + dot→kebab map)
│   ├── plugins/re-framework-tools.js   # 3 ref_* model tools + contract guard (R1/R3/R5)
│   ├── cordis.patch.yml       # agent preset declaration (ACTIVE carrier)
│   ├── scripts/install.ps1 + selfcheck.ps1 + gen_cheatsheet.py   # install + 7-item self-check + compaction derived-view template
│   ├── tests/                 # test_manifest / check_plugin_schema / audit_preset_rows / audit_prompt_variables / test_target_modules / test_contract_guard
│   └── AGENTS.md              # DSH maintenance entry
├── templates/                 # Artifact schemas (language-agnostic)
├── knowledge-builtin/         # Built-in knowledge base
├── scripts/merge_index.py     # Parallel index merge (ref_merge_index dependency)
├── scripts/target_modules.py  # Target-module manager: derive / verify G1-G9 / plan→apply→rollback / repair (spec §5.7)
└── archive/reasonix/          # Reasonix host format archive (read-only, RESTORE.md restorable)
```

## Target modularity (v2.12, spec §5.7)

**Problem it solves**: in a large project, conclusions from different subsystems (renderer / netcode / gameplay; Java packages / .NET namespaces / build units) pile up in one flat artifact tree (`classes/`, `functions/`, `cross_refs/`): nobody can tell which conclusions belong to which subsystem, the same fact gets derived twice, and merges conflict. The framework used to have only **domain modules** (core / re-binary / re-code / swe) and no layer for **the target program's own modules**.

**Approach**: manage **artifacts, code and knowledge** by the target program's own modules; modules come from target evidence, not from a hand-written list.

### Concepts

- **Target module ≠ domain module**: the former is a program subsystem (`netcode`), the latter a framework packaging unit (`re-binary`). The index keeps them apart as `target_module` and `module`.
- **A boundary is a hypothesis**: every boundary carries evidence (build file / RTTI / namespace / section / package) and `confidence` (derived / converged / disputed / confirmed). Artifacts without evidence go to `unassigned/` — **first-class and allowed to persist**, never force-fitted.
- **Reviews bind to module + revision**: when the module structure or an artifact's module changes, `candidate | confirmed` drops back to `draft` (the previous status is recorded in the journal), because the old review no longer applies to the new ownership — the same applicability rule as Anchorlaw.

### Layout

```
<project>/.artifacts/
├── target-modules.yaml        # module map: revision + per-module boundaries/provides/requires/history
├── target-modules.state.json  # machine state read by the contract guard (generated; never hand-edited)
├── index.yaml                 # each entry carries target_module / module_revision
├── modules/<id>/              # artifacts: classes/ functions/ xrefs/ conclusions/
│   └── reviews/<rev>.md       # judge review for this module at this revision (G8)
├── unassigned/                # first-class unassigned bucket
├── _migrations/<rev>/         # plan.json + journal.json + backup/ (auditable, reversible)
└── _audit/guard.jsonl         # guard denials and bypasses
```

Code lands in `work/<id>/` (`config.code_root` is configurable; an empty workspace asks on first run); knowledge lands in `knowledge/discovered/modules/<id>/`, with cross-module lessons in `shared/` (`modules: [a,b]` back-references, no duplication).

### Workflow

1. **`derive`** from `package.json` workspaces / `Cargo.toml` workspace / `pom.xml` modules / a `--hints` file; it writes the map, the directories and the index.
2. **Write artifacts to `modules/<id>/`** and keep `index.yaml` in sync (`target_module` + `module_revision`).
3. **`verify`** runs G1-G9; fix what it reports (legacy flat trees go through `plan adopt-legacy` → `apply` into `unassigned/`).
4. **judge reviews one module**: scope = `module:<id>@<rev>`, writing `reviews/<rev>.md`; `candidate` requires it (G8 / guard R3).
5. **Corrections**: wrong boundary or ownership → `plan` (reassign / split / merge / rename / demote / quarantine) → `apply` (transactional: backup + journal, reverse rollback on failure).
6. **`repair`** rebuilds index/state from disk (recovery after bypasses).

### Gates G1-G9 (fail-closed)

| Gate | Check |
|---|---|
| G1 | unique ownership, no duplicate content across modules |
| G2 | every active module has at least one boundary with evidence |
| G3 | unassigned counts (map vs disk) agree |
| G4 | every index entry's `module_revision` matches the map |
| G5 | no orphan module directories; retired modules hold no artifacts |
| G6 | `provides` unique, `requires` resolvable |
| G7 | every applied revision has `plan.json` + `journal.json` |
| G8 | `candidate/confirmed` modules have `reviews/<rev>.md` for the current revision |
| G9 | no stray artifacts outside `modules/` and `unassigned/` |

### Contract guard (deny before the action, same shape as DSH `fs-observation-policy`)

Evaluated before `write`/`edit`; a denial carries a one-line recovery and a stable code:

| Rule | Trigger | Code |
|---|---|---|
| R1 | write into an undeclared module directory | `REF_MODULE_UNDECLARED` → `ref_modules derive` or write `unassigned/` |
| R3 | `status: candidate/confirmed` without a review at this revision | `REF_REVIEW_MISSING` → invoke `core-judge` (scope=module:<id>) |
| R5 | knowledge entry missing `signature/verdict/lesson/status` | `REF_KB_FRONTMATTER` → add the front-matter |

Self-rescue: `REF_GUARD=off` (guard idles, **every bypass is audited**); out-of-bounds writes are still found by G1-G9 on the next run and fixed by `repair`. The guard only sees tool calls — `pwsh` writes are a known bypass, not a claimed coverage.

### What judge does not do

**Judge reviews modules, not the global whole**: a large project's global state is not reviewable; judge reviews one module (its artifacts + obligation state + gate results), writes `reviews/<rev>.md`, and the global side gets only G8's mechanical coverage check. **A module too large for one review pass must be split** — that is how granularity is decided. Cross-cutting behavior becomes an `integration-<feature>` module reviewed on its own instead of widening judge scope.

### Commands

```powershell
python scripts/target_modules.py <project> derive [--hints modules.yaml]
python scripts/target_modules.py <project> status [--json]
python scripts/target_modules.py <project> verify [--json]          # G1-G9
python scripts/target_modules.py <project> plan reassign --from A --to B --files f.yaml
python scripts/target_modules.py <project> apply <plan.json>        # failed applies roll back
python scripts/target_modules.py <project> repair
```

**Verification status**: fixture tests pass (G1/G5/G6/G8/G9 counter-cases, migration rollback, guard R1/R3/R5, audited `REF_GUARD=off`); **not yet run on a real large project** — spec §9 marks it `CONJECTURE`, and derivation accuracy is waiting for field data.

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
| v2.12 | 2026-10-24 | **Target-modularity P1 (manage artifacts, code and knowledge by the program's own modules)**: new spec **§5.7** + `scripts/target_modules.py` (`derive` from build files/hints → `verify` G1-G9 → `plan`/`apply` transactional correction → `repair`) + a **contract guard** (`ctx.tools.guard`, deny-only: R1 undeclared module / R3 candidate without a review at this revision / R5 missing KB front-matter; `REF_GUARD=off` self-rescue, audited to `_audit/guard.jsonl`). **Core mechanics**: artifacts land in `.artifacts/modules/<id>/`; `unassigned/` is first-class; `index.yaml` entries carry `target_module`/`module_revision`; corrections run through `_migrations/<rev>/{plan,journal,backup}` and **roll back** in reverse journal order on failure; moving an artifact downgrades `candidate|confirmed` to `draft` (reviews bind to module+revision; the journal records the previous status); boundary changes bump a revision and keep history. **Unmanned loop**: self-adjudication (candidates → adversarial checks → sandbox simulation → choose → apply → decision log), escalating only on hard blocks B1-B4 with a one-page digest; **judge reviews modules, not the global whole** (scope = `module:<id>@<rev>`, writes `reviews/<rev>.md`; a module too large for one review pass must be split). **Skill deltas**: core-plan (Phase 0 module decomposition + judge presets), core-artifact (layout/index/correction/guard), core-knowledge (`modules/<id>/` + `shared/` partitioning), core-judge (module scope and review records). **Verified**: `tests/test_target_modules.py` (derive / G1-G9 counter-cases / adopt-legacy / reassign / rollback / repair) + `tests/test_contract_guard.mjs` (R1/R3/R5 / audit / bypass), wired as self-check section 7 (six → seven sections); all pass. **Not verified**: derivation accuracy on a real large project (spec §9 marks it CONJECTURE). |
| v2.11 | 2026-10-24 | **DSH 0.2.1-rc.3 removed the `./list-agents` subpath (row gate caught it at maintenance time)**: upstream `4df09d37d5` ("register shared control tools together"; guide `docs/upgrade-guide/v0.2.1-rc.1/subagent-control-tools/guide.md` §Migration 3) now registers `send_message`, `interrupt_agent` **and** `list_agents` together in the `@deepseek-ai/dsh-tool-subagent-control` **main entry**, deleting the standalone `./list-agents` export. Our `tool-subagent-list-agents` row therefore resolved to nothing (`ERR_PACKAGE_PATH_NOT_EXPORTED`) and would have broken the preset mount for new sessions; **self-check section 5 (row gate) went red at maintenance time** (28 rows → 1 unresolvable) instead of surfacing only when a session fails to start. **Fix**: the row is gone; `list_agents` stays available through the `tool-subagent-control` row — matching upstream's own standard preset, which deleted the same row (disabling the control row now disables all three tools; use tool restrictions to hide a single one). **Timeline check**: at rc.2 (the v2.10 baseline `687f282e`) the export **still existed** (`git show 687f282e:packages/subagent/tool-subagent-control/package.json` lists `./list-agents`), and the removal merged after rc.2 — so this is **new upstream drift**, not a v2.10 miss. **Not adopted (human decision pending)**: the official standard preset also replaced the spawn row's `modelSelectionSettings: true` with `modelSelection: true` + `modelDiscovery: true`; neither this bundle nor Anchorlaw enables them, so re-framework sessions have no `list_subagent_models` / per-child model choice — a **capability-surface difference**, not a failure. **Measured**: row gate 27 rows, 0 unresolvable; prompt-variable gate green; six-section self-check green; Anchorlaw v0.25 (`ccd9105`) made the same fix (27 rows). |
| v2.10 | 2026-10-17 | **DSH 0.2.x adaptation follow-ups + Anchorlaw reference v0.24**: (1) dropped the four `backgroundMode` keys — `@deepseek-ai/dsh-tool-subagent` no longer has it, Schemastery silently discarded them, so they never took effect; the row gate cannot see this "dead config key" class (same family as `{{cwd}}`). (2) the spawn row gains `agentPreset: re-framework` plus `allowedAgentPresets: [re-framework]` — 0.2.x composes subagents from a preset and **both must be given together** or it throws; the fork row must NOT carry them (`capabilities.agentPreset: false`, otherwise "independent agent preset"). (3) `engines.dsh: >=0.2.0 <0.3.0` (compatibility is decided by engines alone). (4) subpath display metadata: added `./plugin/locale/*.json` and `./plugin/icon` (since 0.2.0 a subpath plugin no longer reads `<subpath>/package.json` for display text). (5) **Anchorlaw v0.23 → v0.24**: pure host adaptation, §5/§9/§12/§13/§14/§15/§16 **differ by zero lines**, so only the reference version moves. **Measured**: `dsh --profile web --help` exits 0 with no warnings; re-running `install.ps1` exits 0 (`already-installed` affects only the Host API / agent tool, not the CLI `add`); the six-section self-check is green. **Not verified**: end-to-end session resume (needs a Host restart) |
| v2.9 | 2026-10-10 | **DSH 0.2.x removed the `cwd` prompt variable + a template-variable gate**: upstream followed its upgrade guide (`docs/upgrade-guide/v0.2.1-alpha.1/working-directory/guide.md` §Migration 1) and deleted the loop's built-in `{{cwd}}` prompt variable (commit `79bd3d8da7` removed the `variable('cwd', …)` row from `packages/core/agent-loop/src/index.ts`); the working directory now arrives as the `working-directory:current` **runtime-context** entry from `dsh-working-directory`. **Incident**: this bundle's persona prefix still said `Your working directory is {{cwd}}.`, and persona templates interpolate **strictly at render**, so every re-framework session failed during assembly (before any model request) with `unknown prompt variable "{{cwd}}" in section "deployment:persona-prefix"; registered variables: provider, model`. **Root cause (a gate blind spot)**: section 5 only proves "rows resolve and packages mount" — it cannot see a **dead template variable**. Reproduced with the real harness `renderPrompt()` (old text throws, new text passes). **Fixes**: (1) the `{{cwd}}` clause is gone from the `cordis.patch.yml` persona prefix (it now points at the runtime context, so the model still learns the directory); (2) a new fail-closed gate `tests/audit_prompt_variables.mjs` (mirrors upstream `interpolate()`'s scanning rules; the registered set is derived by scanning the harness for `systemPrompt.variable('<name>')` registration points, skipping tests so test-only names cannot pollute the allowlist; **finding no registration point exits 2 = FAIL**) is wired into `selfcheck.ps1` as section [6], with `DSH_SKIP_PROMPT_VAR_AUDIT=1` as the explicit opt-out; **counter-evidence measured**: restoring `{{cwd}}` in a fixture turns it red (and also flags malformed names), and a wrong checkout exits 2. Self-check: 5 sections → 6 |
| v2.8 | 2026-09-23 | **Preset-carrier migration (directory -> bundle patch) + gate blind-spot fix**: upstream DSH 0.1.7 replaced the agent-preset carrier — a preset is no longer `$DSH_HOME/.agent-presets/<id>/` but a **`@deepseek-ai/dsh-agent-preset` declaration row inside a bundle patch** (nothing reads the legacy directory). **Incident**: `re-framework` ceased to exist under 0.1.7, so session resume failed with `Unknown agent preset`. **Root cause (a gate blind spot, reproduced)**: the row gate's `rowNames()` walked only `Array.isArray(row.config)` — it knew neither the bundle carrier nor `config.plugins[]` — so the gate reported "All preset rows resolvable" while the preset was unloadable (replaying the old gate against the new carrier: `0 reference(s)`, exit 0). **Fixes**: (1) the gate now covers **both carriers and three recursion paths** (`insert[]` / `config[]` / `config.plugins[]`, marked do-not-delete), defaults to the **live carrier** and fails when it is missing, and recognises the **bundle's own package** (validates the `exports` key *and* that the exported file exists); **measured 0 -> 28 rows**. (2) `install.ps1` rewritten to verify the bundle, run the row gate first, copy skills to the user-global root, then `dsh plugin --profile <p> add <dir>`; a PowerShell trap was fixed (the `-Profile` parameter collided case-insensitively with `foreach ($profile ...)` and was overwritten — renamed `-ProfileName`). (3) `selfcheck.ps1` section 3 no longer reconciles the **dead** directory; it checks the **bundle is selected** in a profile and reconciles the user-global skills by sha256 (manifest v2). (4) `dsh/preset/` and the dead installed directory deleted (human-confirmed). (5) `dsh/AGENTS.md` names `cordis.patch.yml` as the fact source (the misleading pointer the report flagged; that file is read every session) |
| v2.7 | 2026-09-23 | **Anchorlaw reference v0.22 → v0.23 re-check (pure version bump; protocol core unchanged)**: v0.23 is the **DSH 0.1.7 preset-carrier migration**, i.e. §16 host-adaptation scope. **The protocol's own claim was independently re-checked** (*"the protocol core is unchanged"*): §5/§9/§12/§13/§14/§15/§16 **differ by zero lines**; the heading set is 92 = 92; there are **five** real differences (measured with an LCS diff): the version-header release note (+20 lines), the supersession note on the v0.18 entry (+5), and three single-line table-row edits (the v0.18 DSH changelog row, the §8 Maturity row, the §11 audit row) - the last three are table text, not clause bodies. **Methodology trap**: a section diff must normalize **both** version strings to the same placeholder, or a clause heading that literally reads the old version masquerades as a difference. **Substantive impact on hosts**: the preset carrier becomes a **bundle-patch declaration row**, rows inside `config.plugins[]` are not path-anchored (a bare package subpath is required), the preset subtree's `baseUrl` is the **profile directory**, the anchor-* skills move to the user-global root, and the **project-level install mode is withdrawn**. This framework does **not** rely on project-level install, so the withdrawal leaves its install semantics intact; the carrier migration does affect the dsh adaptation layer (temporarily fixed; the **formal upgrade TODO** is in `.investigations/dsh-preset-bundle-migration/报告.md` §6). **34 references bumped** (33 tracked + 1 active carrier), including the persona in the **active carrier `cordis.patch.yml`** — that file was untracked at the time, so `git grep` cannot see it: reference enumeration must also cover `git status` |
| v2.6 | 2026-09-17 | **Anchorlaw v0.22 substantive clause upgrade + CoreSwap paper-study absorption**: (1) reference v0.21 → **v0.22** — v0.22 adds **five clauses** (§9 +37 lines, §14 +34, §15 +75), so this is a **substantive upgrade, not a bare version bump**; all five are landed (§9.8 side-effect boundary and inverse registration → spec §5.6 + core-artifact; §15.4 criterion preconditions → spec §4.5 + core-judge; §9.7.1 equivalence tiers → re-lift; §15.4 PI-1 halt-is-terminal → spec §4.5 + core-fanout convergence completeness; §14.7 reference integrity → spec §3 check action). (2) **Installed artifacts gain an identity** — `install.ps1` writes a sha256 manifest and `selfcheck.ps1` section 3 upgrades from counting directories to **content reconciliation** (MISSING/DRIFT/ORPHAN); two pre-existing holes closed: orphan cleanup in the user-global tree (scoped to this framework's namespace, **never touching `anchor-*`**) and a backup before rewriting the profile patch. (3) New trigger-coverage gate `audit_trigger_coverage.mjs` (**judges "is there an artifact after a trigger", not "should it have triggered"**; measured false-positive rate **1.1%**). (4) Handoff claim evidence grades (numeric inheritable / qualitative must re-sample the raw log / anchor must be self-checked with its owner tool), **scoped to semantic handoffs** to avoid over-engineering |
| v2.5 | 2026-09-17 | **Anchorlaw reference v0.20 → v0.21 re-check**: v0.21 is a **host-adaptation progress record** (preset capability parity + fail-closed preset-row resolvability gate) with the **protocol core byte-identical** — method: line-by-line diff of the `protocol-v0.20.md` and `protocol-v0.21.md` normative bodies (before the changelog) after normalizing the version string; the only difference is the 16-line release note in the version header; §5/§9/§12/§13/§14/§15/§16 differ by zero lines, §11/§16 by zero, and the §8 Maturity table keeps the same row count (only the Host Integration row's text is amended). Clauses §5/§9/§12/§13/§14/§15/§16 all retained — **a pure version-reference bump, no semantic migration**. See the new re-check row in spec §3 and `dsh/SYNC.md` |
| v2.4 | 2026-09-09 | **Upstream DSH drift fix + capability-surface alignment**: (1) upstream renamed `@deepseek-ai/dsh-workflow-worker-thread` → `@deepseek-ai/dsh-workflow-ptc` (old directory no longer a package) — the preset still referenced the old name, so preset mount failed and sessions could not be created/resumed (`failed to mount`); `id`+`name` renamed to follow upstream, `config` unchanged. (2) Capability surface aligned to the official standard preset (31 rows): added 5 rows — `command-goal`, `present` (enabled), `tool-ralph`, `tool-subagent-codex`, `tool-subagent-claude-code` (disabled per upstream default; enabling needs the matching Bundle in the Profile) → **ours 32 = official 31 + local `re-framework-tools`, gap 0**. (3) New fail-closed gate `tests/audit_preset_rows.mjs` wired into `selfcheck.ps1` as section [5] — any unresolvable preset row now fails the self-check instead of surfacing only on session resume (2026-09-09 drift incident, `.investigations/dsh-upstream-drift-20260909/报告.md`). (4) Same-day second round: **preset row specifier resolution semantics aligned to upstream** (`classifyRowSpecifier()` four-way classification + package names resolved by an upward walk from the harness base; a wrong base is fail-closed) |
| v2.3 | 2026-08-21 | **Knowledge-base compaction** (absorbing the CoreSwap knowledge-compaction proposal, borrowing DSH compaction): structured entry front-matter (id/status/supersedes/superseded_by/signature/verdict/lesson, aligned with Anchorlaw v0.20 §15.4 supersession chain), derived views must not be hand-maintained (`gen_cheatsheet.py`), compaction pass (every 10 entries or topic closure, cluster-merge into principles + consolidated originals kept); **§4.5 fifth mandatory trigger** (handover conclusion verification ≤1 round + three-state session-switch advice MUST + contamination-signal separation, aligned with v0.20 §16.3); Anchorlaw v0.19→v0.20 |
| v2.2 | 2026-08-21 | **DSH-only host migration**: Reasonix archived (`archive/reasonix/`), `dsh/skills/` single source of truth, tools 5→3 (ref_manifest_validate/ref_install retired with Reasonix), root AGENTS.md rewritten DSH-first, spec annotated, simplified install (single install.ps1), pure-reference Anchorlaw install (zero copy); knowledge value gate (P1/P2/P3); Anchorlaw v0.18→v0.19 (verification-scope clarification) |
| v2.1 | 2026-08-14~15 | DSH adaptation (`dsh/` subtree), user-global skills, preset-only tools, Anchorlaw v0.15→v0.17→v0.18, SKILL-MAP DSH detector, error-ledger hardening |
| v2.0 | 2026-08 | Modular rewrite (Reasonix era, archived) |
| v1.0 | 2026-06 | Single 42KB CLAUDE.md (BitWarden methodology, archived) |
