# install.ps1 — Install/sync the RE-Framework DSH project into the DSH runtime.
#
# Source of truth: E:\PYTHON\RE-Framework\dsh
#   preset/agent.cordis.yml + preset/preset.yml      → ~/.dsh/.agent-presets/re-framework/
#   plugins/re-framework-tools.js                    → ~/.dsh/.agent-presets/re-framework/plugins/ (preset-embedded)
#   skills/*                                         → ~/.dsh/.agent-presets/re-framework/skills/ (preset-embedded)
#                                                   → ~/.dsh/skills/                             (user-global)
#   global tool mount                                → <profile>/plugins/re-framework/re-framework-tools.js
#                                                   → <profile>/cordis.patch.yml (insert row:
#                                                     re-framework-tools-global)
#
# Visibility design (DSH native layers, no deployment-config changes):
#   - Skills are user-global (~/.dsh/skills/ref-*): any session on any preset
#     and in any working directory can load them on demand. Preset-embedded
#     copies remain for the re-framework preset's full-workbench experience.
#   - Project-side tools (ref_status/ref_init/ref_merge_index/ref_install) are
#     user-global via the PROFILE patch layer
#     (<dshHome>/profiles/<profile>/cordis.patch.yml — the ONLY user patch
#     layer DSH reads; baseUrl = the profile dir, hot-reloaded). ~/.dsh/
#     cordis.patch.yml is NOT read by the host (2026-08-13 Anchorlaw incident
#     finding). The patch row is an `insert` (cordis-plugin-include
#     applyEntryPatches): an id-targeted `{id, config}` row would be treated as
#     an override and silently skipped.
#   - The maintenance tool (ref_manifest_validate) stays preset-only: checking
#     the framework's own manifest has meaning only in the framework workspace.
#
# GATE: never mount a plugin whose tool schemas are not compiled JSON Schema.
# A flat per-property spec is projected verbatim to the LLM without a top-level
# type and breaks EVERY session. The check (tests/check_plugin_schema.mjs) must
# pass before any patch is written.
#
# Idempotent: safe to re-run after editing any source file. Requires full file
# access to the DSH home (outside the session workspace).

param(
  # DSH profile name for the global tool mount. Empty = auto-detect every
  # profile directory under <dshHome>/profiles holding a package.json (never a
  # hard-coded default).
  [string]$Profile = ''
)

$ErrorActionPreference = 'Stop'

$srcRoot  = Split-Path -Parent $PSScriptRoot
$dshHome  = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$presetDir = Join-Path $dshHome '.agent-presets\re-framework'
$userSkills = Join-Path $dshHome 'skills'

Write-Host "== RE-Framework DSH install =="
Write-Host "source      : $srcRoot"
Write-Host "preset      : $presetDir"
Write-Host "user skills : $userSkills (user-global, any session)"

# 0. Cleanup legacy wrong mount (2026-08-13 incident): the previous install
#    wrote ~/.dsh/cordis.patch.yml and ~/.dsh/plugins/re-framework/ — the host
#    never reads that home patch (only profiles/<profile>/cordis.patch.yml),
#    so the rows there are dead config. Remove them so nothing stale lingers.
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

# 1. Preset composition + metadata
New-Item -ItemType Directory -Path $presetDir -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'preset\agent.cordis.yml') -Destination $presetDir -Force
Copy-Item -Path (Join-Path $srcRoot 'preset\preset.yml')       -Destination $presetDir -Force

# 2. Plugin file (preset-embedded)
New-Item -ItemType Directory -Path (Join-Path $presetDir 'plugins') -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'plugins\re-framework-tools.js') -Destination (Join-Path $presetDir 'plugins') -Force

# 3. Skills: preset-embedded refresh + user-global refresh
if (Test-Path (Join-Path $srcRoot 'skills')) {
  $presetSkills = Join-Path $presetDir 'skills'
  Remove-Item -Path $presetSkills -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item -Path (Join-Path $srcRoot 'skills') -Destination $presetSkills -Recurse -Force
  Copy-Item -Path (Join-Path $srcRoot 'skills\*') -Destination $userSkills -Recurse -Force
}

# 4. Global tool mount — DSH reads ONLY a profile's own patch layer
#    (<dshHome>/profiles/<profile>/cordis.patch.yml; baseUrl = profile dir,
#    hot-reloaded). The re-framework plugin row is appended as an `insert`
#    patch so the project-side ref_* tools are available in every session.
#    Profiles: -Profile <name> mounts one profile explicitly; otherwise EVERY
#    profile directory holding a package.json is mounted. No profile found
#    skips the mount with a hint — there is NO hard-coded default profile.
$mountProfiles = @()
if ($Profile) {
  $mountProfiles = @($Profile)
} else {
  $profilesDir = Join-Path $dshHome 'profiles'
  if (Test-Path $profilesDir) {
    $mountProfiles = @(Get-ChildItem -Path $profilesDir -Directory | Where-Object {
      $_.Name -ne 'node_modules' -and (Test-Path (Join-Path $_.FullName 'package.json'))
    } | ForEach-Object { $_.Name })
  }
}

if ($mountProfiles.Count -eq 0) {
  Write-Host "  skip global tools: no DSH profile found under $(Join-Path $dshHome 'profiles')"
  Write-Host "        (create one with 'dsh plugin --profile <name> add <package>', then re-run install.ps1)"
} else {
  node (Join-Path $srcRoot 'tests\check_plugin_schema.mjs') 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "plugin tool-schema check failed - refusing to mount global tools"
  }
  foreach ($profileName in $mountProfiles) {
    $profileDir = Join-Path $dshHome "profiles\$profileName"
    $patchPath = Join-Path $profileDir 'cordis.patch.yml'
    $profilePluginDir = Join-Path $profileDir 'plugins\re-framework'

    # Plugin file travels with the profile (resolved relative to baseUrl = profile dir)
    New-Item -ItemType Directory -Path $profilePluginDir -Force | Out-Null
    Copy-Item -Path (Join-Path $srcRoot 'plugins\re-framework-tools.js') -Destination (Join-Path $profilePluginDir 're-framework-tools.js') -Force

    # Idempotent YAML merge: drop any prior re-framework-tools-global insert
    # row, then append ours (project-side tools only).
    $py = @'
import io, os, yaml
path = os.environ['REF_PATCH_PATH']
try:
    with io.open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
except FileNotFoundError:
    data = None
rows = list(data) if isinstance(data, list) else []
rows = [r for r in rows if not (
    isinstance(r, dict) and any(
        (e or {}).get('id') == 're-framework-tools-global' for e in (r.get('insert') or [])))]
rows.append({'insert': [{'id': 're-framework-tools-global',
                         'name': './plugins/re-framework/re-framework-tools.js',
                         'config': {'tools': ['status', 'init', 'merge_index', 'install']}}]})
out = ('# Managed by install.ps1 - global re-framework tools for this profile '
       '(re-framework-tools-global). Re-run install.ps1 to refresh; do not hand-edit.\n' +
       yaml.safe_dump(rows, allow_unicode=True, sort_keys=False))
with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
'@
    $tmpPy = Join-Path $env:TEMP 'ref-patch-merge.py'
    Set-Content -Path $tmpPy -Value $py -Encoding UTF8
    $env:REF_PATCH_PATH = $patchPath
    python $tmpPy
    $mergeCode = $LASTEXITCODE
    Remove-Item $tmpPy -Force -ErrorAction SilentlyContinue
    Remove-Item Env:REF_PATCH_PATH -ErrorAction SilentlyContinue
    if ($mergeCode -ne 0) { throw "failed to merge profile patch $patchPath" }
    Write-Host "  OK global tools: $patchPath (re-framework-tools-global)"
  }
}

Write-Host ""
Write-Host "Installed:"
Get-ChildItem -Path $presetDir -Recurse -File | ForEach-Object { Write-Host "  $($_.FullName.Replace($presetDir, 'preset'))" }
$userCount = @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(core|re|recode|swe|ref)-' }).Count
Write-Host "  user-global skills: $userCount ref-family directories (expected 17)"
if ($mountProfiles.Count -gt 0) {
  foreach ($profileName in $mountProfiles) {
    Write-Host "  global: $(Join-Path $dshHome "profiles\$profileName\cordis.patch.yml") (re-framework-tools-global)"
  }
}
Write-Host ""
Write-Host "Next: run scripts/selfcheck.ps1 to verify; open a NEW session (or wait for profile hot-reload)"
Write-Host "      and the project-side ref_* tools are available in every session. The maintenance"
Write-Host "      tool ref_manifest_validate stays on the re-framework preset."
