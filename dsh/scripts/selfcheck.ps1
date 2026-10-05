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
# copy, and no re-framework-tools-global ROW in ~/.dsh/cordis.patch.yml.
#
# The home-level patch file is LEGAL DSH STATE and is judged by its ROW, never
# by its existence: it is the home-level user patch layer (applied after every
# profile layer, therefore outranking it) and it carries other frameworks'
# rows plus machine-local settings. Before the 2026-09-18 fix this check failed
# on mere existence and install.ps1 answered by deleting the whole file.
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
# The home-level layer is judged by the ROW, not the file. patch_layer.py
# --has-row is read-only (never writes) and shares its row grammar with
# install.ps1, so the gate and the cleanup cannot disagree.
$homePatchFile = Join-Path $dshHome 'cordis.patch.yml'
$patchLayerPy = Join-Path (Join-Path $srcRoot 'scripts') 'patch_layer.py'
if (Test-Path $homePatchFile) {
  # Capture output WITHOUT a pipeline: `python ... | Out-Null` leaves
  # $LASTEXITCODE from the pipeline, not from python (measured: it reported 2
  # instead of 1). Assign the call so the exit code is python's own.
  $hasRowOut = python $patchLayerPy --has-row $homePatchFile --row-id 're-framework-tools-global' 2>&1
  $hasRow = $LASTEXITCODE
  if ($hasRow -eq 0) {
    Write-Host "  FAIL: ~/.dsh/cordis.patch.yml still carries the re-framework-tools-global row — re-run install.ps1"; $fail = 1
  } elseif ($hasRow -eq 1) {
    Write-Host "  OK home-level patch layer present but without our row (legal: other frameworks' rows + machine-local settings live there)"
  } else {
    Write-Host "  FAIL: could not judge the home-level patch layer (patch_layer.py exit $hasRow)"; $fail = 1
  }
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
