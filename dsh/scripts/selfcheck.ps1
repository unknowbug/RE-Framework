# selfcheck.ps1 — Maintenance self-check for the RE-Framework DSH project.
#
# Mirrors the framework's self-reference iron rule (spec §1/§2.5): the
# framework must be able to verify itself. Checks:
#   1. python toolchain availability
#   2. DSH skill manifest validity (naming/frontmatter/upstream body-drift) via tests/test_manifest.py
#   3. framework self-scan: scripts/validate_manifest.py against the repo root (R1-R6)
#   4. installed preset + embedded skills presence under ~/.dsh

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
$globalPlugin = Join-Path $dshHome 'plugins\re-framework\re-framework-tools.js'
if (Test-Path $globalPlugin) {
  Write-Host "  OK global plugin: $globalPlugin"
} else {
  Write-Host "  FAIL: global plugin missing"; $fail = 1
}
$patchPath = Join-Path $dshHome 'cordis.patch.yml'
if ((Test-Path $patchPath) -and (Get-Content $patchPath -Raw -ErrorAction SilentlyContinue) -match 're-framework-tools-global') {
  Write-Host "  OK home patch row: re-framework-tools-global"
} else {
  Write-Host "  FAIL: home patch missing re-framework-tools-global row"; $fail = 1
}

Write-Host ""
if ($fail -eq 0) { Write-Host "== ALL CHECKS PASSED ==" } else { Write-Host "== CHECKS FAILED ==" }
exit $fail
