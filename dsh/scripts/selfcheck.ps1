# selfcheck.ps1 — Maintenance self-check for the RE-Framework DSH project.
#
# Mirrors the framework's self-reference iron rule (spec §1): the framework
# must be able to verify itself. Checks:
#   1. python toolchain availability
#   2. DSH skill manifest validity (naming/frontmatter/set/cross-refs) via tests/test_manifest.py
#   3. installed preset + user-global skills under ~/.dsh: existence/count checks
#      PLUS content reconciliation against install-manifest.yaml (sha256 → 0
#      missing / 0 drift / 0 orphan). Counting directories only proves "17
#      directories exist"; it cannot see a stale, edited or orphaned copy — the
#      same silently-green failure class the preset-row gate eliminates.
#      (Reasonix archived: no validate_manifest.py self-scan anymore)
#   4. plugin tool-schema shape (compiled JSON-Schema parameters) via
#      tests/check_plugin_schema.mjs — a flat spec would reach the LLM without
#      a top-level type and break every session ("Invalid schema ... type: null").
#   5. preset row resolvability via tests/audit_preset_rows.mjs — every `name:` in
#      the composition must resolve against the harness package set; an upstream
#      rename/removal otherwise surfaces only when a session resume fails to mount
#      (2026-09-09 drift: dsh-workflow-worker-thread → dsh-workflow-ptc, see
#      .investigations/dsh-upstream-drift-20260909/报告.md).

$ErrorActionPreference = 'Continue'

$srcRoot = Split-Path -Parent $PSScriptRoot
$fail = 0
# This framework's namespace in the SHARED ~/.dsh/skills tree (Anchorlaw's
# anchor-* skills live there too, so every check is scoped to this prefix).
$skillNamespace = '^(core|re|recode|swe|ref)-'

Write-Host "== RE-Framework DSH self-check =="

# 1. toolchain
Write-Host ""
Write-Host "[1] toolchain"
python --version 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: python not available"; $fail = 1 }

# 2. skill manifest (DSH naming + frontmatter + set + cross-refs; dsh/skills is
#    the single source of truth since the Reasonix format was archived)
Write-Host ""
Write-Host "[2] skill manifests"
python (Join-Path $srcRoot 'tests\test_manifest.py') 2>&1
if ($LASTEXITCODE -ne 0) { $fail = 1 }

# 3. installed artifacts
Write-Host ""
Write-Host "[3] installed artifacts"
$dshHome = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$presetDir = Join-Path $dshHome '.agent-presets\re-framework'
if (Test-Path (Join-Path $presetDir 'agent.cordis.yml')) {
  Write-Host "  OK preset: $presetDir"
} else {
  Write-Host "  FAIL: preset not installed — run scripts/install.ps1"; $fail = 1
}
$presetSkills = Join-Path $presetDir 'skills'
$count = @(Get-ChildItem -Path $presetSkills -Directory -ErrorAction SilentlyContinue).Count
Write-Host "  OK embedded skills: $count directories (expected 17)"
if ($count -lt 17) { Write-Host "  FAIL: expected 17 ref-* skills"; $fail = 1 }
$userSkills = Join-Path $dshHome 'skills'
$userCount = @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match $skillNamespace }).Count
Write-Host "  OK user-global skills: $userCount ref-family directories (expected 17, visible in any session)"
if ($userCount -lt 17) { Write-Host "  FAIL: expected 17 user-global ref-family skills"; $fail = 1 }

# 3b. Content reconciliation against the install manifest (CoreSwap paper study
#     b2 rec.1). The count checks above only prove "17 directories exist" — they
#     cannot see an edited, stale or orphaned copy, so they are the same
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
Test-InstallManifest (Join-Path $presetDir 'install-manifest.yaml') 'preset' $null
Test-InstallManifest (Join-Path $userSkills '.re-framework-manifest.yaml') 'user-global' $skillNamespace
# Global tool group must be WITHDRAWN (user decision 2026-08-15): no
# re-framework-tools-global row in any profile patch, no profile-local plugin
# copy, no legacy ~/.dsh/cordis.patch.yml.
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
    if (Test-Path (Join-Path $profile.FullName 'plugins\re-framework')) {
      Write-Host "  FAIL: profile $($profile.Name) still has plugins\re-framework — re-run install.ps1"
      $globalGone = $false; $fail = 1
    }
  }
}
if ($globalGone) { Write-Host "  OK global tool group withdrawn (tools live on the re-framework preset only)" }
$legacyHomePatch = Join-Path $dshHome 'cordis.patch.yml'
if (Test-Path $legacyHomePatch) {
  Write-Host "  FAIL: legacy ~/.dsh/cordis.patch.yml still present — re-run install.ps1"; $fail = 1
}

# 4. plugin tool-schema shape (compiled JSON-Schema parameters; see check_plugin_schema.mjs)
Write-Host ""
Write-Host "[4] plugin tool schemas"
node (Join-Path $srcRoot 'tests\check_plugin_schema.mjs') 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: plugin tool schemas not compiled JSON Schema"; $fail = 1 }

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
node (Join-Path $srcRoot 'tests\audit_preset_rows.mjs') 2>&1
$presetAudit = $LASTEXITCODE
if ($presetAudit -eq 2) {
  if ($env:DSH_SKIP_PRESET_AUDIT -eq '1') {
    Write-Host "  WARN: preset audit skipped by explicit opt-out (DSH_SKIP_PRESET_AUDIT=1)"
  } else {
    Write-Host "  FAIL: preset audit could not run (harness checkout/js-yaml unavailable)"
    Write-Host "        set DSH_CHECKOUT to the harness checkout, or DSH_SKIP_PRESET_AUDIT=1 to accept the gap"
    $fail = 1
  }
} elseif ($presetAudit -ne 0) {
  Write-Host "  FAIL: unresolvable preset row(s) — upstream renamed/removed a plugin"; $fail = 1
}

Write-Host ""
if ($fail -eq 0) { Write-Host "== ALL CHECKS PASSED ==" } else { Write-Host "== CHECKS FAILED ==" }
exit $fail
