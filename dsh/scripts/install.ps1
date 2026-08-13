# install.ps1 — Install/sync the RE-Framework DSH project into the DSH runtime.
#
# Source of truth: E:\PYTHON\RE-Framework\dsh
#   preset/agent.cordis.yml + preset/preset.yml      → ~/.dsh/.agent-presets/re-framework/
#   plugins/re-framework-tools.js                    → ~/.dsh/.agent-presets/re-framework/plugins/ (preset-embedded)
#                                                   → ~/.dsh/plugins/re-framework/               (user-global mount)
#   skills/*                                         → ~/.dsh/.agent-presets/re-framework/skills/ (preset-embedded)
#                                                   → ~/.dsh/skills/                             (user-global)
#   home patch                                       → ~/.dsh/cordis.patch.yml (row: re-framework-tools-global)
#
# Visibility design (DSH native layers, no deployment-config changes):
#   - Skills are user-global (~/.dsh/skills/ref-*): any session on any preset
#     and in any working directory can load them on demand. Preset-embedded
#     copies remain for the re-framework preset's full-workbench experience.
#   - Project-side tools (ref_status/ref_init/ref_merge_index/ref_install) are
#     user-global via the home patch (~/.dsh/cordis.patch.yml, applied to every
#     profile, hot-reloaded): usable from any project session — they operate on
#     session-workspace data + read-only framework sources, so the sandbox
#     (read outside workspace allowed, write limited to workspace) does not
#     block them.
#   - The maintenance tool (ref_manifest_validate) stays preset-only: checking
#     the framework's own manifest has meaning only in the framework workspace.
#
# Idempotent: safe to re-run after editing any source file. Requires full file
# access to the DSH home (outside the session workspace).

$ErrorActionPreference = 'Stop'

$srcRoot  = Split-Path -Parent $PSScriptRoot
$dshHome  = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$presetDir = Join-Path $dshHome '.agent-presets\re-framework'
$userSkills = Join-Path $dshHome 'skills'
$globalPlugins = Join-Path $dshHome 'plugins\re-framework'
$patchPath = Join-Path $dshHome 'cordis.patch.yml'

Write-Host "== RE-Framework DSH install =="
Write-Host "source      : $srcRoot"
Write-Host "preset      : $presetDir"
Write-Host "user skills : $userSkills (user-global, any session)"
Write-Host "global tools: $globalPlugins + home patch $patchPath"

# 1. Preset composition + metadata
New-Item -ItemType Directory -Path $presetDir -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'preset\agent.cordis.yml') -Destination $presetDir -Force
Copy-Item -Path (Join-Path $srcRoot 'preset\preset.yml')       -Destination $presetDir -Force

# 2. Plugin file: preset-embedded + user-global mount
New-Item -ItemType Directory -Path (Join-Path $presetDir 'plugins') -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'plugins\re-framework-tools.js') -Destination (Join-Path $presetDir 'plugins') -Force
New-Item -ItemType Directory -Path $globalPlugins -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'plugins\re-framework-tools.js') -Destination (Join-Path $globalPlugins 're-framework-tools.js') -Force

# 3. Skills: preset-embedded refresh + user-global refresh
if (Test-Path (Join-Path $srcRoot 'skills')) {
  $presetSkills = Join-Path $presetDir 'skills'
  Remove-Item -Path $presetSkills -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item -Path (Join-Path $srcRoot 'skills') -Destination $presetSkills -Recurse -Force
  Copy-Item -Path (Join-Path $srcRoot 'skills\*') -Destination $userSkills -Recurse -Force
}

# 4. Home patch: user-global project-side tools row (idempotent)
$patchRow = @"
- id: re-framework-tools-global
  name: ./plugins/re-framework/re-framework-tools.js
  config:
    tools:
      - status
      - init
      - merge_index
      - install
"@
if (-not (Test-Path $patchPath)) {
  $header = @"
# dsh home patch — user-level composition rows applied to EVERY profile (hot-reloaded on edit).
# Managed rows: do not hand-edit the generated blocks; re-run install.ps1 to refresh.

"@
  Set-Content -Path $patchPath -Value ($header + $patchRow) -Encoding UTF8
  Write-Host "  + created $patchPath with re-framework-tools-global row"
} else {
  $content = Get-Content $patchPath -Raw
  if ($content -match 're-framework-tools-global') {
    Write-Host "  OK home patch already has re-framework-tools-global (idempotent)"
  } else {
    Add-Content -Path $patchPath -Value $patchRow -Encoding UTF8
    Write-Host "  + appended re-framework-tools-global row to $patchPath"
  }
}

Write-Host ""
Write-Host "Installed:"
Get-ChildItem -Path $presetDir -Recurse -File | ForEach-Object { Write-Host "  $($_.FullName.Replace($presetDir, 'preset'))" }
$userCount = @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(core|re|recode|swe|ref)-' }).Count
Write-Host "  user-global skills: $userCount ref-family directories (expected 17)"
Write-Host "  global plugin: $globalPlugins\re-framework-tools.js"
Write-Host "  home patch: $patchPath"
Write-Host ""
Write-Host "Next: open a new session (any preset) in any project — ref-* skills load on demand and the"
Write-Host "      project-side ref_* tools are available (hot-reloaded via the home patch). The"
Write-Host "      maintenance tool ref_manifest_validate stays on the re-framework preset."
Write-Host "Verify: scripts/selfcheck.ps1"
