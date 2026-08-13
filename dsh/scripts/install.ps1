# install.ps1 — Install/sync the RE-Framework DSH project into the DSH runtime.
#
# Source of truth: E:\PYTHON\RE-Framework\dsh
#   preset/agent.cordis.yml + preset/preset.yml   → ~/.dsh/.agent-presets/re-framework/
#   plugins/re-framework-tools.js                 → ~/.dsh/.agent-presets/re-framework/plugins/
#   skills/*                                      → ~/.dsh/.agent-presets/re-framework/skills/
#
# Skills are preset-embedded only (they do NOT sync to ~/.dsh/skills global —
# deliberate: the ref-* methodology skills must not pollute other presets'
# sessions; they are visible only in sessions on the re-framework preset).
#
# Idempotent: safe to re-run after editing any source file. Requires full file
# access to the DSH home (outside the session workspace).

$ErrorActionPreference = 'Stop'

$srcRoot  = Split-Path -Parent $PSScriptRoot
$dshHome  = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$presetDir = Join-Path $dshHome '.agent-presets\re-framework'

Write-Host "== RE-Framework DSH install =="
Write-Host "source : $srcRoot"
Write-Host "preset : $presetDir"

# 1. Preset composition + metadata
New-Item -ItemType Directory -Path $presetDir -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'preset\agent.cordis.yml') -Destination $presetDir -Force
Copy-Item -Path (Join-Path $srcRoot 'preset\preset.yml')       -Destination $presetDir -Force

# 2. Local plugin file (travels with the preset)
New-Item -ItemType Directory -Path (Join-Path $presetDir 'plugins') -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'plugins\re-framework-tools.js') -Destination (Join-Path $presetDir 'plugins') -Force

# 3. Skills: preset-embedded refresh (regenerated from ../skills/ by sync_skills.py)
if (Test-Path (Join-Path $srcRoot 'skills')) {
  $presetSkills = Join-Path $presetDir 'skills'
  Remove-Item -Path $presetSkills -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item -Path (Join-Path $srcRoot 'skills') -Destination $presetSkills -Recurse -Force
}

Write-Host ""
Write-Host "Installed:"
Get-ChildItem -Path $presetDir -Recurse -File | ForEach-Object { Write-Host "  $($_.FullName.Replace($presetDir, 'preset'))" }
Write-Host ""
Write-Host "Next: open a new session on the 're-framework' preset, or run scripts/selfcheck.ps1 to verify."
