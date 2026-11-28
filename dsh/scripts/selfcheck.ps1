# selfcheck.ps1 — Maintenance self-check for the RE-Framework DSH project.
#
# Mirrors the framework's self-reference iron rule (spec §1): the framework
# must be able to verify itself. Checks:
#   1. python toolchain availability
#   2. DSH skill manifest validity (naming/frontmatter/set/cross-refs) via tests/test_manifest.py
#   3. installed artifacts under ~/.dsh: (a) the BUNDLE is selected in at least one
#      profile's `dsh.profile.bundles` — under DSH >= 0.1.7 that is the only thing
#      that makes a preset exist; (b) the user-global skills are reconciled against
#      the install manifest by sha256 (0 missing / 0 drift / 0 orphan). A directory
#      count only proves "17 directories exist" and cannot see a stale, edited or
#      orphaned copy — the same silently-green failure class the preset-row gate
#      eliminates (2026-09-23: this section checked the legacy directory that
#      nothing reads, so it stayed green while sessions failed to resume).
#      (Reasonix archived: no validate_manifest.py self-scan anymore)
#   4. plugin tool-schema shape (compiled JSON-Schema parameters) via
#      tests/check_plugin_schema.mjs — a flat spec would reach the LLM without
#      a top-level type and break every session ("Invalid schema ... type: null").
#   5. preset row resolvability via tests/audit_preset_rows.mjs — every `name:` in
#      the ACTIVE carrier (the bundle patch `dsh/cordis.patch.yml`) must resolve.
#      Two incidents this gate exists to catch: the 2026-09-09 upstream rename
#      (dsh-workflow-worker-thread → dsh-workflow-ptc) and the 2026-09-23 carrier
#      migration, where the gate did not know the bundle carrier and stayed green
#      while sessions reported `Unknown agent preset`.
#   6. preset TEMPLATE variables via tests/audit_prompt_variables.mjs — every
#      `{{name}}` in the same carrier must be a variable the harness actually
#      registers (persona prefixes/suffixes interpolate strictly at render).
#      Incident this gate exists to catch (2026-10-10): DSH 0.2.x removed the
#      built-in `cwd` prompt variable (upstream 79bd3d8da7), our persona prefix
#      still said `Your working directory is {{cwd}}.`, and every re-framework
#      session failed to assemble — while sections 1-5 stayed green.
#   7. target-module manager + contract guard (spec §5.7) via fixture tests:
#      scripts/target_modules.py (derive / G1-G9 / plan-apply-rollback) and the
#      plugin guard (R1/R3/R5 + audit + REF_GUARD=off); plus the Work Order
#      contract template (spec §4.6) and the Portable-Knowledge index integrity
#      (273 entries / status counts / every rules.md key resolves).
#   8. known regressions via tests/audit_known_regressions.mjs — every already
#      fixed defect ({{cwd}}, backgroundMode, removed subpaths, inject race,
#      desktop direct-install, asar runtime, parseEntryYaml, zero-row silent
#      green, ...) is re-asserted structurally; plus the Anchorlaw reference
#      baseline must agree across spec/persona/README/AGENTS/ref-maintain.
#      Modeled on Anchorlaw 0.27.1 ("gate the fixes instead of remembering them").

$ErrorActionPreference = 'Continue'

$srcRoot = Split-Path -Parent $PSScriptRoot
$fail = 0
# This framework's namespace in the SHARED ~/.dsh/skills tree (Anchorlaw's
# anchor-* skills live there too, so every check is scoped to this prefix).
$skillNamespace = '^(core|re|recode|swe|ref)-'

# Python resolver: Kylin/some Linux distributions ship only `python3`.
$pythonExe = $null
foreach ($candidate in @('python', 'python3')) {
  if (Get-Command $candidate -ErrorAction SilentlyContinue) { $pythonExe = $candidate; break }
}

# ── harness 运行时选择 ──────────────────────────────────────────────────────
# Sections 5/6/7 read the harness's packages and sources. A source checkout can
# use plain `node`; DSH Desktop packs the runtime into resources\app.asar, which
# plain Node's fs cannot read, so those gates must run under
# ELECTRON_RUN_AS_NODE=1 "<app>.exe" (Electron's fs reads asar transparently).
$checkout = if ($env:DSH_CHECKOUT) { $env:DSH_CHECKOUT } else { 'D:\git\deepseek-harness' }
# The running Desktop app exposes its own layout, which beats guessing install
# paths: DSH_NODE_EXECUTABLE is the app exe, and DSH_INSTALL_DIR points INSIDE
# resources\app.asar (…\app.asar\dsh\node_modules\@deepseek-ai\dsh), so it is
# split at "app.asar" rather than used as a directory.
$harnessExe = if ($env:DSH_NODE_EXECUTABLE -and (Test-Path $env:DSH_NODE_EXECUTABLE)) { $env:DSH_NODE_EXECUTABLE } else { $null }
$installDir = $null
if ($env:DSH_INSTALL_DIR -and $env:DSH_INSTALL_DIR -match 'app\.asar') {
  $installDir = $env:DSH_INSTALL_DIR.Substring(0, $env:DSH_INSTALL_DIR.IndexOf('app.asar')).TrimEnd('\', '/')
}
if (-not $installDir) {
  # The Desktop app is not always under %ProgramFiles% (this machine installs it
  # on D:). The running process's own path is the reliable detector.
  $desktopProcess = Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($desktopProcess -and $desktopProcess.Path) {
    $candidate = Join-Path (Split-Path $desktopProcess.Path -Parent) 'resources'
    if (Test-Path (Join-Path $candidate 'app.asar')) { $installDir = $candidate; $harnessExe = $desktopProcess.Path }
  }
}
if (-not $installDir) {
  foreach ($candidate in @(
      (Join-Path $env:ProgramFiles 'DeepSeek Harness\resources'),
      (Join-Path $env:LOCALAPPDATA 'Programs\DeepSeek Harness\resources'))) {
    if ($candidate -and (Test-Path (Join-Path $candidate 'app.asar'))) { $installDir = $candidate; break }
  }
}
$harnessLayout = 'unknown'
if ($harnessExe) {
  $harnessLayout = 'asar'
} elseif (Test-Path (Join-Path $checkout 'packages')) {
  $harnessLayout = 'checkout'
} elseif ($installDir) {
  $candidateExe = Join-Path (Split-Path $installDir -Parent) 'DeepSeek Harness.exe'
  if (Test-Path $candidateExe) { $harnessLayout = 'asar'; $harnessExe = $candidateExe }
}
Write-Host "harness layout: $harnessLayout$(if ($harnessExe) { " ($harnessExe)" })"

# Run a harness/JS gate under the current layout (returns its exit code).
function Invoke-HarnessGate([string]$scriptPath) {
  if ($harnessLayout -eq 'asar') {
    $previous = $env:ELECTRON_RUN_AS_NODE
    $env:ELECTRON_RUN_AS_NODE = '1'
    try { & $harnessExe $scriptPath 2>&1 | Out-Host; return $LASTEXITCODE }
    finally {
      if ($null -eq $previous) { Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue }
      else { $env:ELECTRON_RUN_AS_NODE = $previous }
    }
  }
  & node $scriptPath 2>&1 | Out-Host
  return $LASTEXITCODE
}

Write-Host "== RE-Framework DSH self-check =="

# 1. toolchain
Write-Host ""
Write-Host "[1] toolchain"
if (-not $pythonExe) {
  Write-Host "  FAIL: python not available (tried python, python3)"; $fail = 1
} else {
  & $pythonExe --version 2>&1
  if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: python not available"; $fail = 1 }
}

# 2. skill manifest (DSH naming + frontmatter + set + cross-refs; dsh/skills is
#    the single source of truth since the Reasonix format was archived)
Write-Host ""
Write-Host "[2] skill manifests"
if ($pythonExe) {
  & $pythonExe (Join-Path (Join-Path $srcRoot 'tests') 'test_manifest.py') 2>&1
  if ($LASTEXITCODE -ne 0) { $fail = 1 }
} else { $fail = 1 }

# 3. installed artifacts
Write-Host ""
Write-Host "[3] installed artifacts"
$dshHome = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$userSkills = Join-Path $dshHome 'skills'

# 3a. Bundle selected in at least one profile. Under DSH >= 0.1.7 a preset exists
#     ONLY if its bundle is listed in a profile's ordered `dsh.profile.bundles`;
#     the legacy directory (`~/.dsh/.agent-presets/<id>/`) is read by nothing.
#     Checking that directory (as this section used to) is exactly the
#     silently-green failure class that let "selfcheck green, resume fails"
#     happen on 2026-09-23.
$bundleManifestPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'package.json'
$bundleName = $null
if (Test-Path $bundleManifestPath) {
  try { $bundleName = (Get-Content $bundleManifestPath -Raw | ConvertFrom-Json).name } catch { $bundleName = $null }
}
if (-not $bundleName) {
  Write-Host "  FAIL: cannot read the bundle name from dsh/package.json"; $fail = 1
} else {
  $profilesDir = Join-Path $dshHome 'profiles'
  $selectedIn = @()
  $profileDirs = @()
  if (Test-Path $profilesDir) {
    $profileDirs = @(Get-ChildItem -Path $profilesDir -Directory | Where-Object {
      $_.Name -ne 'node_modules' -and (Test-Path (Join-Path $_.FullName 'package.json'))
    })
  }
  foreach ($pd in $profileDirs) {
    try {
      $pj = Get-Content (Join-Path $pd.FullName 'package.json') -Raw | ConvertFrom-Json
      $bundles = @($pj.dsh.profile.bundles)
      if ($bundles -contains $bundleName) { $selectedIn += $pd.Name }
    } catch { /* 坏 manifest 已在下面报 */ }
  }
  if ($profileDirs.Count -eq 0) {
    Write-Host "  FAIL: no DSH profile found under $profilesDir — the bundle cannot be selected"; $fail = 1
  } elseif ($selectedIn.Count -eq 0) {
    Write-Host "  FAIL: bundle '$bundleName' is not selected in any profile's dsh.profile.bundles — run scripts/install.ps1"; $fail = 1
  } else {
    Write-Host "  OK bundle selected: $bundleName (profile(s): $($selectedIn -join ', '))"
  }
}

$userCount = @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match $skillNamespace }).Count
Write-Host "  OK user-global skills: $userCount ref-family directories (expected 17, visible in any session)"
if ($userCount -lt 17) { Write-Host "  FAIL: expected 17 user-global ref-family skills"; $fail = 1 }

# 3b. Content reconciliation against the install manifest (CoreSwap paper study
#     b2 rec.1). The count check above only proves "17 directories exist" — it
#     cannot see an edited, stale or orphaned copy, so it is the same
#     silently-green failure class the preset-row gate was built to eliminate.
#     These checks prove the CONTENT is what install.ps1 actually wrote.
#     Reconcile a manifest against disk; returns "MISSING/DRIFT/ORPHAN" counters.
function Test-InstallManifest($manifestPath, $label, $namespace) {
  if (-not (Test-Path $manifestPath)) {
    Write-Host "  FAIL: $label install manifest missing — re-run install.ps1"
    $script:fail = 1
    return
  }
  $lines = Get-Content $manifestPath
  $entries = @()
  $cur = $null
  foreach ($line in $lines) {
    if ($line -match '^\s*-\s+id:\s*(.+)$') {
      if ($cur) { $entries += $cur }
      $cur = [ordered]@{ id = $Matches[1].Trim() }
    } elseif ($cur -and $line -match '^\s+target:\s*(.+)$') { $cur.target = $Matches[1].Trim() }
    elseif ($cur -and $line -match '^\s+sha256:\s*(.+)$') { $cur.sha256 = $Matches[1].Trim() }
  }
  if ($cur) { $entries += $cur }

  $missing = 0; $drift = 0
  foreach ($e in $entries) {
    $t = $e.target -replace '/', '\'
    if (-not (Test-Path $t)) { $missing++; Write-Host "    MISSING: $($e.id)"; continue }
    $actual = (Get-FileHash $t -Algorithm SHA256).Hash.ToLower()
    if ($actual -ne $e.sha256) { $drift++; Write-Host "    DRIFT: $($e.id) (content differs from what install.ps1 wrote)" }
  }

  # ORPHAN: a ref-family artifact on disk that the manifest does not know about
  # (= dropped upstream but still installed). Scoped to this framework's
  # namespace so other frameworks' skills in the shared tree are never flagged.
  $orphan = 0
  if ($namespace) {
    $manifestIds = @($entries | ForEach-Object { $_.id })
    foreach ($dir in @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue)) {
      if ($dir.Name -notmatch $namespace) { continue }
      if (Test-Path (Join-Path $dir.FullName '.keep-local')) { continue }   # local override opt-out
      $known = @($manifestIds | Where-Object { $_ -like "skills/$($dir.Name)/*" })
      if ($known.Count -eq 0) { $orphan++; Write-Host "    ORPHAN: $($dir.Name) (installed but not in manifest)" }
    }
  }

  if ($missing -eq 0 -and $drift -eq 0 -and $orphan -eq 0) {
    Write-Host "  OK $label content reconciled: $($entries.Count) artifacts (0 missing, 0 drift, 0 orphan)"
  } else {
    Write-Host "  FAIL: $label unreconciled — $missing missing, $drift drifted, $orphan orphaned (re-run install.ps1)"
    $script:fail = 1
  }
}
Test-InstallManifest (Join-Path $userSkills '.re-framework-manifest.yaml') 'user-global' $skillNamespace
# Global tool group must be WITHDRAWN (user decision 2026-08-15): no
# re-framework-tools-global row in any profile patch, no profile-local plugin
# copy, and the home-level patch layer must not carry our withdrawn row.
$profilesDir = Join-Path $dshHome 'profiles'
$globalGone = $true
if (Test-Path $profilesDir) {
  $profiles = @(Get-ChildItem -Path $profilesDir -Directory | Where-Object {
    $_.Name -ne 'node_modules' -and (Test-Path (Join-Path $_.FullName 'package.json')) })
  foreach ($profile in $profiles) {
    $patchFile = Join-Path $profile.FullName 'cordis.patch.yml'
    if ((Test-Path $patchFile) -and
        ((Get-Content $patchFile -Raw -ErrorAction SilentlyContinue) -match 're-framework-tools-global')) {
      Write-Host "  FAIL: profile $($profile.Name) still has re-framework-tools-global — re-run install.ps1"
      $globalGone = $false; $fail = 1
    }
    if (Test-Path (Join-Path (Join-Path $profile.FullName 'plugins') 're-framework')) {
      Write-Host "  FAIL: profile $($profile.Name) still has plugins/re-framework — re-run install.ps1"
      $globalGone = $false; $fail = 1
    }
  }
}
if ($globalGone) { Write-Host "  OK global tool group withdrawn (tools live on the re-framework preset only)" }
# The home-level patch layer ($DSH_HOME/cordis.patch.yml) is LEGAL DSH state:
# it is applied after every profile layer and may carry other frameworks' rows
# and machine-local settings. Existence is NOT a violation — the judged fact is
# whether it still carries OUR withdrawn row (patch_layer.py, shared with
# install.ps1). A missing file counts as absent.
$homePatchFile = Join-Path $dshHome 'cordis.patch.yml'
$patchLayerPy = Join-Path (Join-Path $srcRoot 'scripts') 'patch_layer.py'
if (Test-Path $homePatchFile) {
  if ($pythonExe) {
    & $pythonExe $patchLayerPy --has-row $homePatchFile --row-id 're-framework-tools-global' 2>&1 | Out-Null
    $homeRow = $LASTEXITCODE
    if ($homeRow -eq 0) {
      Write-Host "  FAIL: ~/.dsh/cordis.patch.yml still carries re-framework-tools-global — re-run install.ps1"
      $fail = 1
    } elseif ($homeRow -eq 1) {
      Write-Host "  OK home-level patch layer exists without our row (legal; other rows are untouched)"
    } else {
      Write-Host "  FAIL: could not inspect ~/.dsh/cordis.patch.yml (patch_layer.py exit $homeRow)"
      $fail = 1
    }
  } else {
    Write-Host "  WARN: home patch exists but python is unavailable; cannot verify its rows"
  }
}

# 4. plugin tool-schema shape (compiled JSON-Schema parameters; see check_plugin_schema.mjs)
Write-Host ""
Write-Host "[4] plugin tool schemas"
$schemaAudit = Invoke-HarnessGate (Join-Path (Join-Path $srcRoot 'tests') 'check_plugin_schema.mjs')
if ($schemaAudit -ne 0) { Write-Host "  FAIL: plugin tool schemas not compiled JSON Schema"; $fail = 1 }

# 5. preset row resolvability (fail-closed; see audit_preset_rows.mjs)
#
# Exit 2 means the audit could not RUN (harness checkout / js-yaml unavailable).
# That is NOT a pass: a gate that silently goes green when it cannot execute is
# the same failure class as the incident it guards against (unresolvable row
# surfacing only on session resume). So exit 2 counts as FAIL unless the operator
# explicitly opts out with DSH_SKIP_PRESET_AUDIT=1 (e.g. a machine with no
# harness checkout that does not install presets at all).
Write-Host ""
Write-Host "[5] preset row resolvability"
$presetAudit = Invoke-HarnessGate (Join-Path (Join-Path $srcRoot 'tests') 'audit_preset_rows.mjs')
if ($presetAudit -eq 2) {
  if ($env:DSH_SKIP_PRESET_AUDIT -eq '1') {
    Write-Host "  WARN: preset audit skipped by explicit opt-out (DSH_SKIP_PRESET_AUDIT=1)"
  } else {
    Write-Host "  FAIL: preset audit could not run (harness unreadable — set DSH_CHECKOUT, or use Electron for an asar install)"
    Write-Host "        set DSH_CHECKOUT to the harness checkout, or DSH_SKIP_PRESET_AUDIT=1 to accept the gap"
    $fail = 1
  }
} elseif ($presetAudit -ne 0) {
  Write-Host "  FAIL: unresolvable preset row(s) — upstream renamed/removed a plugin"; $fail = 1
}

# 6. preset template variables (fail-closed; see audit_prompt_variables.mjs)
#
# Same fail-closed contract as section 5: exit 2 = the audit could not RUN
# (no harness checkout / no js-yaml / no registration point found), which is NOT
# a pass — a gate that goes green when it cannot execute is exactly how a dead
# `{{cwd}}` reference reached a live session. DSH_SKIP_PROMPT_VAR_AUDIT=1 accepts
# the gap explicitly.
Write-Host ""
Write-Host "[6] preset template variables"
$variableAudit = Invoke-HarnessGate (Join-Path (Join-Path $srcRoot 'tests') 'audit_prompt_variables.mjs')
if ($variableAudit -eq 2) {
  if ($env:DSH_SKIP_PROMPT_VAR_AUDIT -eq '1') {
    Write-Host "  WARN: prompt-variable audit skipped by explicit opt-out (DSH_SKIP_PROMPT_VAR_AUDIT=1)"
  } else {
    Write-Host "  FAIL: prompt-variable audit could not run (harness unreadable — set DSH_CHECKOUT, or use Electron for an asar install)"
    Write-Host "        set DSH_CHECKOUT to the harness checkout, or DSH_SKIP_PROMPT_VAR_AUDIT=1 to accept the gap"
    $fail = 1
  }
} elseif ($variableAudit -ne 0) {
  Write-Host "  FAIL: preset template references an unregistered prompt variable — upstream removed/renamed it"; $fail = 1
}

# 7. fixture gates: target-module manager, contract guard, patch layer (spec §5.7)
#
# The manager runs a real project fixture (derive, G1-G9, legacy adoption,
# reassign, failed-apply rollback); the guard runs against a fake Cordis context
# (declared-module, review-at-revision, KB front-matter, audited bypass); the
# patch-layer tests lock the "a patch file is not a violation, a row is" rule
# (PR #2 / 2026-09-18). All local; no harness checkout needed.
Write-Host ""
Write-Host "[7] fixture gates (target modules / contract guard / patch layer / work order / portable index)"
if ($pythonExe) {
  & $pythonExe (Join-Path (Join-Path $srcRoot 'tests') 'test_target_modules.py') 2>&1 | Select-Object -Last 6
  if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: target_modules fixture tests failed"; $fail = 1 }
  & $pythonExe (Join-Path (Join-Path $srcRoot 'tests') 'test_home_patch.py') 2>&1 | Select-Object -Last 2
  if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: patch-layer tests failed"; $fail = 1 }
  & $pythonExe (Join-Path (Join-Path $srcRoot 'tests') 'test_work_order.py') 2>&1 | Select-Object -Last 2
  if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: work-order contract test failed"; $fail = 1 }
  & $pythonExe (Join-Path (Join-Path $srcRoot 'tests') 'test_portable_index.py') 2>&1 | Select-Object -Last 2
  if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: portable index/data test failed"; $fail = 1 }
} else { $fail = 1 }
$guardAudit = Invoke-HarnessGate (Join-Path (Join-Path $srcRoot 'tests') 'test_contract_guard.mjs')
if ($guardAudit -ne 0) { Write-Host "  FAIL: contract-guard tests failed"; $fail = 1 }

# 8. known regressions (fail-closed; see tests/audit_known_regressions.mjs)
#
# Every fixed defect is re-asserted structurally, so a later cleanup cannot
# silently bring it back. Exit 2 = a guard file is missing (cannot judge), which
# must fail like any other unexecutable gate.
Write-Host ""
Write-Host "[8] known regressions"
$regressionAudit = Invoke-HarnessGate (Join-Path (Join-Path $srcRoot 'tests') 'audit_known_regressions.mjs')
if ($regressionAudit -eq 2) {
  Write-Host "  FAIL: known-regression gate could not run (guard file missing)"; $fail = 1
} elseif ($regressionAudit -ne 0) {
  Write-Host "  FAIL: a known regression came back — see the gate output above"; $fail = 1
}

Write-Host ""
if ($fail -eq 0) { Write-Host "== ALL CHECKS PASSED ==" } else { Write-Host "== CHECKS FAILED ==" }
exit $fail
