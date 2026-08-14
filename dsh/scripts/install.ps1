# install.ps1 — Install/sync the RE-Framework DSH project into the DSH runtime.
#
# Source of truth: E:\PYTHON\RE-Framework\dsh
#   preset/agent.cordis.yml + preset/preset.yml      → ~/.dsh/.agent-presets/re-framework/
#   plugins/re-framework-tools.js                    → ~/.dsh/.agent-presets/re-framework/plugins/ (preset-embedded)
#   skills/*                                         → ~/.dsh/.agent-presets/re-framework/skills/ (preset-embedded)
#                                                   → ~/.dsh/skills/                             (user-global)
#
# Visibility design (per user decision 2026-08-15 — NO global tool group):
#   - Skills are user-global (~/.dsh/skills/ref-*): any session on any preset
#     and in any working directory can load them on demand (methodology works
#     in any project, e.g. CoreSwap, with the standard tool set).
#   - Tools live ONLY on the re-framework preset (all five, config.tools full):
#     they are thin wrappers over the framework's python scripts, which any
#     session can also call directly via pwsh (python scripts/install.py ...).
#     The earlier profile-patch global mount (re-framework-tools-global in
#     <profile>/cordis.patch.yml) is removed by this script, so no other
#     session carries the extra tool group.
#
# GATE: never ship a plugin whose tool schemas are not compiled JSON Schema.
# A flat per-property spec is projected verbatim to the LLM without a top-level
# type and breaks EVERY session (2026-08-13 Anchorlaw incident). The check
# (tests/check_plugin_schema.mjs) runs before the plugin is copied anywhere.
#
# Idempotent: safe to re-run after editing any source file. Requires full file
# access to the DSH home (outside the session workspace).

$ErrorActionPreference = 'Stop'

$srcRoot  = Split-Path -Parent $PSScriptRoot
$dshHome  = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$presetDir = Join-Path $dshHome '.agent-presets\re-framework'
$userSkills = Join-Path $dshHome 'skills'

Write-Host "== RE-Framework DSH install =="
Write-Host "source      : $srcRoot"
Write-Host "preset      : $presetDir"
Write-Host "user skills : $userSkills (user-global, any session)"

# 0. Schema gate: never copy a plugin whose tool schemas are not compiled JSON
#    Schema (a flat spec would break every session once mounted anywhere).
node (Join-Path $srcRoot 'tests\check_plugin_schema.mjs') 2>&1
if ($LASTEXITCODE -ne 0) {
  throw "plugin tool-schema check failed - refusing to install"
}

# 1. Cleanup legacy wrong mounts (2026-08-13 incident + 2026-08-15 reversal):
#    a) ~/.dsh/cordis.patch.yml — the host never reads it (only
#       profiles/<profile>/cordis.patch.yml).
#    b) ~/.dsh/plugins/re-framework/ — wrong location.
#    c) re-framework-tools-global insert rows in every profile patch — the
#       global tool group is withdrawn per user decision; skills stay global.
$legacyHomePatch = Join-Path $dshHome 'cordis.patch.yml'
if (Test-Path $legacyHomePatch) {
  $legacyContent = Get-Content $legacyHomePatch -Raw -ErrorAction SilentlyContinue
  if ($legacyContent -match 're-framework-tools-global') {
    Remove-Item $legacyHomePatch -Force
    Write-Host "  - removed legacy ~/.dsh/cordis.patch.yml (host does not read it)"
  }
}
$legacyPlugins = Join-Path $dshHome 'plugins\re-framework'
if (Test-Path $legacyPlugins) {
  Remove-Item $legacyPlugins -Recurse -Force
  Write-Host "  - removed legacy ~/.dsh/plugins/re-framework/ (wrong location)"
}

# 1c. Withdraw the global tool row from every profile patch (idempotent):
#     drop any re-framework-tools-global insert row, keep everything else
#     (e.g. anchorlaw-tools-global), and delete the profile-local plugin copy.
$profilesDir = Join-Path $dshHome 'profiles'
$profiles = @()
if (Test-Path $profilesDir) {
  $profiles = @(Get-ChildItem -Path $profilesDir -Directory | Where-Object {
    $_.Name -ne 'node_modules' -and (Test-Path (Join-Path $_.FullName 'package.json'))
  })
}
foreach ($profile in $profiles) {
  $patchPath = Join-Path $profile.FullName 'cordis.patch.yml'
  if (Test-Path $patchPath) {
    $py = @'
import io, os, yaml
path = os.environ['REF_PATCH_PATH']
with io.open(path, encoding='utf-8') as f:
    data = yaml.safe_load(f)
rows = list(data) if isinstance(data, list) else []
kept = [r for r in rows if not (
    isinstance(r, dict) and any(
        (e or {}).get('id') == 're-framework-tools-global' for e in (r.get('insert') or [])))]
if len(kept) != len(rows):
    out = yaml.safe_dump(kept, allow_unicode=True, sort_keys=False)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print('removed')
else:
    print('absent')
'@
    $tmpPy = Join-Path $env:TEMP 'ref-patch-withdraw.py'
    Set-Content -Path $tmpPy -Value $py -Encoding UTF8
    $env:REF_PATCH_PATH = $patchPath
    $result = python $tmpPy 2>&1
    $mergeCode = $LASTEXITCODE
    Remove-Item $tmpPy -Force -ErrorAction SilentlyContinue
    Remove-Item Env:REF_PATCH_PATH -ErrorAction SilentlyContinue
    if ($mergeCode -ne 0) { throw "failed to withdraw patch row from $patchPath" }
    if ($result -match 'removed') {
      Write-Host "  - withdrew re-framework-tools-global from $patchPath"
    }
  }
  $profilePluginDir = Join-Path $profile.FullName 'plugins\re-framework'
  if (Test-Path $profilePluginDir) {
    Remove-Item $profilePluginDir -Recurse -Force
    Write-Host "  - removed $profilePluginDir (profile-local plugin copy)"
  }
}

# 2. Preset composition + metadata
New-Item -ItemType Directory -Path $presetDir -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'preset\agent.cordis.yml') -Destination $presetDir -Force
Copy-Item -Path (Join-Path $srcRoot 'preset\preset.yml')       -Destination $presetDir -Force

# 3. Plugin file (preset-embedded)
New-Item -ItemType Directory -Path (Join-Path $presetDir 'plugins') -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'plugins\re-framework-tools.js') -Destination (Join-Path $presetDir 'plugins') -Force

# 4. Skills: preset-embedded refresh + user-global refresh
if (Test-Path (Join-Path $srcRoot 'skills')) {
  $presetSkills = Join-Path $presetDir 'skills'
  Remove-Item -Path $presetSkills -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item -Path (Join-Path $srcRoot 'skills') -Destination $presetSkills -Recurse -Force
  Copy-Item -Path (Join-Path $srcRoot 'skills\*') -Destination $userSkills -Recurse -Force
}

Write-Host ""
Write-Host "Installed:"
Get-ChildItem -Path $presetDir -Recurse -File | ForEach-Object { Write-Host "  $($_.FullName.Replace($presetDir, 'preset'))" }
$userCount = @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(core|re|recode|swe|ref)-' }).Count
Write-Host "  user-global skills: $userCount ref-family directories (expected 17)"
Write-Host ""
Write-Host "Next: run scripts/selfcheck.ps1 to verify. ref-* skills are user-global (any session);"
Write-Host "      the ref_* tools exist ONLY on the re-framework preset (python scripts remain callable"
Write-Host "      directly via pwsh in any session: python scripts/install.py, validate_manifest.py, ...)."
