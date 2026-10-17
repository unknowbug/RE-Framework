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

# 3. Self-check (toolchain / skill manifest / installed artifacts / plugin schemas)
pwsh dsh/scripts/selfcheck.ps1
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
│   ├── plugins/re-framework-tools.js   # 3 ref_* model tools
│   ├── cordis.patch.yml       # agent preset declaration (ACTIVE carrier)
│   ├── scripts/install.ps1 + selfcheck.ps1 + gen_cheatsheet.py   # install + 6-item self-check + compaction derived-view template
│   ├── tests/                 # test_manifest.py + check_plugin_schema.mjs + audit_preset_rows.mjs + audit_prompt_variables.mjs
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
