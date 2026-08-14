# selfcheck.ps1 — Maintenance self-check for the RE-Framework DSH project.
#
# Mirrors the framework's self-reference iron rule (spec §1/§2.5): the
# framework must be able to verify itself. Checks:
#   1. python toolchain availability
#   2. DSH skill manifest validity (naming/frontmatter/upstream body-drift) via tests/test_manifest.py
#   3. framework self-scan: scripts/validate_manifest.py against the repo root (R1-R6)
#   4. installed preset + user-global skills + profile-patch global tools under ~/.dsh
#   5. plugin tool-schema shape (compiled JSON-Schema parameters) via
#      tests/check_plugin_schema.mjs — a flat spec would reach the LLM without
#      a top-level type and break every session ("Invalid schema ... type: null").

$ErrorActionPreference = 'Continue'

$srcRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $srcRoot
$fail = 0

Write-Host "== RE-Framework DSH self-check =="

# 1. toolchain
Write-Host ""
Write-Host "[1] toolchain"
python --version 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: python not available"; $fail = 1 }

# 2. skill manifest (DSH naming + upstream body-drift)
Write-Host ""
Write-Host "[2] skill manifests"
python (Join-Path $srcRoot 'tests\test_manifest.py') 2>&1
if ($LASTEXITCODE -ne 0) { $fail = 1 }

# 3. framework self-scan (validate_manifest.py against the repo root, spec §2.5)
Write-Host ""
Write-Host "[3] framework self-scan"
python (Join-Path $repoRoot 'scripts\validate_manifest.py') 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: framework manifest errors"; $fail = 1 }

# 4. installed artifacts
Write-Host ""
Write-Host "[4] installed artifacts"
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
$userCount = @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(core|re|recode|swe|ref)-' }).Count
Write-Host "  OK user-global skills: $userCount ref-family directories (expected 17, visible in any session)"
if ($userCount -lt 17) { Write-Host "  FAIL: expected 17 user-global ref-family skills"; $fail = 1 }
$globalPatchOk = $false
$profilesDir = Join-Path $dshHome 'profiles'
if (Test-Path $profilesDir) {
  $profiles = @(Get-ChildItem -Path $profilesDir -Directory | Where-Object {
    $_.Name -ne 'node_modules' -and (Test-Path (Join-Path $_.FullName 'package.json')) })
  foreach ($profile in $profiles) {
    $pluginFile = Join-Path $profile.FullName 'plugins\re-framework\re-framework-tools.js'
    $patchFile = Join-Path $profile.FullName 'cordis.patch.yml'
    $patchOk = (Test-Path $pluginFile) -and (Test-Path $patchFile) -and
      ((Get-Content $patchFile -Raw -ErrorAction SilentlyContinue) -match 're-framework-tools-global')
    if ($patchOk) {
      Write-Host "  OK global tools: $($profile.FullName) (re-framework-tools-global)"
      $globalPatchOk = $true
    } else {
      Write-Host "  FAIL: profile $($profile.Name) missing global tool mount (plugin + insert row)"
      $fail = 1
    }
  }
  if ($profiles.Count -eq 0) {
    Write-Host "  WARN: no DSH profile found under $profilesDir — global tools not mounted"
  }
} else {
  Write-Host "  FAIL: no profiles dir under $dshHome"; $fail = 1
}
# Legacy wrong mount must be gone (host never reads ~/.dsh/cordis.patch.yml)
$legacyHomePatch = Join-Path $dshHome 'cordis.patch.yml'
if (Test-Path $legacyHomePatch) {
  Write-Host "  FAIL: legacy ~/.dsh/cordis.patch.yml still present (host does not read it) — re-run install.ps1"; $fail = 1
}

# 5. plugin tool-schema shape (compiled JSON-Schema parameters; see check_plugin_schema.mjs)
Write-Host ""
Write-Host "[5] plugin tool schemas"
node (Join-Path $srcRoot 'tests\check_plugin_schema.mjs') 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: plugin tool schemas not compiled JSON Schema"; $fail = 1 }

Write-Host ""
if ($fail -eq 0) { Write-Host "== ALL CHECKS PASSED ==" } else { Write-Host "== CHECKS FAILED ==" }
exit $fail
