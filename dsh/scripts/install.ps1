# install.ps1 — Install/sync the RE-Framework DSH bundle into the DSH runtime.
#
# DSH >= 0.1.7: an agent preset is a `@deepseek-ai/dsh-agent-preset` declaration
# row carried by a BUNDLE PATCH. The legacy directory form
# (`$DSH_HOME/.agent-presets/<id>/`) is read by NOTHING — upstream:
# "Nothing reads that directory any more"
# (packages/preset/agent-preset/skills/editing-cordis-compositions/SKILL.md).
#
# Source of truth: E:\PYTHON\RE-Framework\dsh  (this subtree IS the bundle package)
#   dsh/package.json                                 → bundle identity (`dsh.bundle.patch`)
#   dsh/cordis.patch.yml                             → the preset declaration (ACTIVE carrier)
#   dsh/plugins/re-framework-tools.js                → addressed by bare package subpath
#                                                      (`@dsh-external/dsh-re-framework/plugin`)
#   dsh/skills/*                                     → served from the bundle via
#                                                      skill-filesystem customSkillDirs
#                                                    → copied to ~/.dsh/skills/ (user-global)
#
# What this script does:
#   1. verifies the bundle package (package.json + the patch it names)
#   2. runs the preset-row gate BEFORE installing (a bundle whose rows do not
#      resolve installs cleanly and then fails at session creation — the
#      2026-09-23 incident)
#   3. copies the ref-* skills to the user-global root
#   4. installs/selects the bundle in every target profile with
#      `dsh plugin --profile <p> add <bundle dir>` (pnpm dependency + the profile's
#      ordered `dsh.profile.bundles`)
#
# Visibility design (per user decision 2026-08-15 — NO global tool group):
#   - Skills are user-global (~/.dsh/skills/ref-*): any session on any preset
#     and in any working directory can load them on demand (methodology works
#     in any project, e.g. CoreSwap, with the standard tool set).
#   - Tools live ONLY on the re-framework preset (three: status/merge_index/
#     init — manifest_validate/install were retired with the Reasonix archive,
#     2026-08-21; merge_index.py stays at the repo root for ref_merge_index).
#     The earlier profile-patch global mount (re-framework-tools-global in
#     <profile>/cordis.patch.yml) is withdrawn by this script (idempotent
#     cleanup), so no other session carries the extra tool group.
#
# GATE: never ship a plugin whose tool schemas are not compiled JSON Schema.
# A flat per-property spec is projected verbatim to the LLM without a top-level
# type and breaks EVERY session (2026-08-13 Anchorlaw incident). The check
# (tests/check_plugin_schema.mjs) runs before anything is installed.
#
# Idempotent: safe to re-run after editing any source file. Requires full file
# access to the DSH home (outside the session workspace).

param(
  # DSH profile to install the bundle into. Empty = auto-detect every profile
  # directory under <dshHome>/profiles holding a package.json (never a hard-coded
  # default).
  #
  # NOTE: this is `-ProfileName`, NOT `-Profile`. PowerShell variable names are
  # case-INSENSITIVE, and the legacy-cleanup loop below uses `$profile` as its
  # iterator — a `$Profile` parameter would be silently overwritten by that loop
  # (observed: the installer then passed a full directory path as the profile
  # name and `dsh` rejected it).
  [string]$ProfileName = ''
)

$ErrorActionPreference = 'Stop'

$srcRoot  = Split-Path -Parent $PSScriptRoot
$dshHome  = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$userSkills = Join-Path $dshHome 'skills'
# This framework's skill namespace in the SHARED ~/.dsh/skills tree. Only names
# matching this prefix are ever refreshed or cleaned; other frameworks'
# (e.g. Anchorlaw's anchor-*) skills are left untouched.
$skillNamespace = '^(core|re|recode|swe|ref)-'

Write-Host "== RE-Framework DSH bundle install =="
Write-Host "bundle      : $srcRoot"
Write-Host "dshHome     : $dshHome"
Write-Host "user skills : $userSkills (user-global, any session)"

# 0. Schema gate: never copy a plugin whose tool schemas are not compiled JSON
#    Schema (a flat spec would break every session once mounted anywhere).
node (Join-Path $srcRoot 'tests\check_plugin_schema.mjs') 2>&1
if ($LASTEXITCODE -ne 0) {
  throw "plugin tool-schema check failed - refusing to install"
}

# 1. Cleanup legacy wrong mounts (2026-08-13 incident + 2026-08-15 reversal):
#    a) ~/.dsh/cordis.patch.yml — this IS legal DSH state: it is the home-level
#       user patch layer, applied after every profile's own layer
#       (@deepseek-ai/dsh-app-boot README: "applied after every bundle layer
#       (per-profile first, then the home-level file, which therefore outranks
#       it)"). It also carries other frameworks' rows and machine-local
#       settings, so this script NEVER deletes the file: if it still holds the
#       withdrawn re-framework-tools-global row, only THAT ROW is removed and
#       every other byte is kept (2026-09-18 fix; before that the whole file was
#       deleted, which could destroy a machine's shared configuration).
#    b) ~/.dsh/plugins/re-framework/ — wrong location.
#    c) re-framework-tools-global insert rows in every profile patch — the
#       global tool group is withdrawn per user decision; skills stay global.
#
#    Row-level logic lives in ONE place (scripts/patch_layer.py, row id passed
#    in) and is shared with selfcheck.ps1, so the gate and the cleanup cannot
#    disagree again. patch_layer.py writes atomically, only when the row is
#    actually present, and it takes the .bak-ref-install backup itself.
$rowId = 're-framework-tools-global'
$patchLayerPy = Join-Path $srcRoot 'scripts\patch_layer.py'
$homePatch = Join-Path $dshHome 'cordis.patch.yml'
if (Test-Path $homePatch) {
  $result = python $patchLayerPy --remove-row $homePatch --row-id $rowId --backup 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "failed to withdraw $rowId from $homePatch (nothing was written; see the message above)"
  }
  if ($result -match 'removed') {
    Write-Host "  - withdrew $rowId from $homePatch (row only; other rows, comments, BOM and line endings kept)"
  }
}
$legacyPlugins = Join-Path $dshHome 'plugins\re-framework'
if (Test-Path $legacyPlugins) {
  Remove-Item $legacyPlugins -Recurse -Force
  Write-Host "  - removed legacy ~/.dsh/plugins/re-framework/ (wrong location)"
}

# 1c. Withdraw the global tool row from every profile patch (idempotent):
#     drop any re-framework-tools-global insert row, keep everything else
#     (e.g. anchorlaw-tools-global, plus comments, BOM and line endings), and
#     delete the profile-local plugin copy. Same primitive as the home layer.
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
    $result = python $patchLayerPy --remove-row $patchPath --row-id $rowId --backup 2>&1
    if ($LASTEXITCODE -ne 0) {
      throw "failed to withdraw $rowId from $patchPath (nothing was written; see the message above)"
    }
    if ($result -match 'removed') {
      Write-Host "  - withdrew $rowId from $patchPath"
    }
  }
  $profilePluginDir = Join-Path $profile.FullName 'plugins\re-framework'
  if (Test-Path $profilePluginDir) {
    Remove-Item $profilePluginDir -Recurse -Force
    Write-Host "  - removed $profilePluginDir (profile-local plugin copy)"
  }
}

# 2. Bundle package: verify it, then gate the preset rows BEFORE anything installs.
#
#    DSH >= 0.1.7 carries an agent preset as a `@deepseek-ai/dsh-agent-preset`
#    declaration row inside a BUNDLE PATCH (dsh/cordis.patch.yml). The legacy
#    directory form (~/.dsh/.agent-presets/re-framework/) is read by NOTHING —
#    upstream: "Nothing reads that directory any more"
#    (packages/preset/agent-preset/skills/editing-cordis-compositions/SKILL.md).
$bundleDir = $srcRoot
$bundleManifestPath = Join-Path $bundleDir 'package.json'
if (-not (Test-Path $bundleManifestPath)) { throw "bundle manifest missing: $bundleManifestPath" }
$bundleManifest = Get-Content $bundleManifestPath -Raw | ConvertFrom-Json
$bundleName = $bundleManifest.name
$patchRel = $bundleManifest.dsh.bundle.patch
if (-not $bundleName) { throw "$bundleManifestPath declares no name" }
if (-not $patchRel) { throw "$bundleManifestPath declares no dsh.bundle.patch" }
$bundlePatchPath = Join-Path $bundleDir $patchRel
if (-not (Test-Path $bundlePatchPath)) { throw "bundle patch missing: $bundlePatchPath" }
Write-Host "  OK bundle: $bundleName  patch: $patchRel"

#    The row gate runs BEFORE install: a bundle whose preset rows do not resolve
#    installs cleanly and then fails at session creation — exactly the 2026-09-23
#    incident (gate green, `Unknown agent preset` on resume).
node (Join-Path $srcRoot 'tests\audit_preset_rows.mjs') 2>&1
if ($LASTEXITCODE -ne 0) { throw "preset row gate failed - refusing to install" }

# 3. Skills → user-global root (visible in every session, on any preset, in any
#    project). The preset ALSO serves them from the bundle via skill-filesystem
#    customSkillDirs, so this copy is the second visibility path, not the only one.
if (Test-Path (Join-Path $srcRoot 'skills')) {

  # 4a. Orphan cleanup in the user-global tree, RESTRICTED to this framework's
  #     namespace ($skillNamespace). ~/.dsh/skills is SHARED with other
  #     frameworks (Anchorlaw's anchor-* skills live there), so a blanket clean
  #     would delete another project's skills. Remove is therefore limited to
  #     directories matching the ref-family prefix that no longer exist upstream;
  #     anything outside the prefix is never touched.
  #
  #     Residual (accepted) risk: a user's OWN directory that happens to be named
  #     core-*/re-*/recode-*/swe-*/ref-* and is not one of our skills would also be
  #     removed. That is bounded to this framework's declared namespace — the same
  #     namespace we own and refresh on every install — and is the documented cost
  #     of automating orphan cleanup. To opt a directory out, rename it outside the
  #     namespace or keep a marker file (see below).
  if (Test-Path $userSkills) {
    foreach ($dir in @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue)) {
      if ($dir.Name -notmatch $skillNamespace) { continue }
      if (Test-Path (Join-Path $dir.FullName '.keep-local')) {
        Write-Host "  - kept local override (marker .keep-local): $($dir.Name)"
        continue
      }
      if (-not (Test-Path (Join-Path $srcRoot "skills\$($dir.Name)"))) {
        Remove-Item -Path $dir.FullName -Recurse -Force
        Write-Host "  - removed orphan user-global skill: $($dir.Name) (dropped upstream)"
      }
    }
  }

  New-Item -ItemType Directory -Path $userSkills -Force | Out-Null
  Copy-Item -Path (Join-Path $srcRoot 'skills\*') -Destination $userSkills -Recurse -Force
}

# 5. Install manifest: give the installed artifacts an identity so "installed"
#    becomes a mechanically checkable fact rather than a re-run-and-hope
#    (CoreSwap paper study b2 rec.1; the same fail-closed philosophy as the
#    preset-row gate). selfcheck section [3] reconciles against this file.
$sourceCommit = '<unknown>'
try {
  $commit = git -C $srcRoot rev-parse HEAD 2>$null
  if ($LASTEXITCODE -eq 0 -and $commit) { $sourceCommit = $commit.Trim() }
} catch { $sourceCommit = '<unknown>' }   # non-git source: declare, never fail-open silently
$installedAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')

$manifestTargets = @()
foreach ($f in @(Get-ChildItem -Path $userSkills -Recurse -File -ErrorAction SilentlyContinue |
                 Where-Object { $_.Name -notlike '.re-framework-manifest.yaml' })) {
  $dirName = Split-Path (Split-Path $f.FullName -Parent) -Leaf
  if ($dirName -notmatch $skillNamespace) { continue }
  $rel = $f.FullName.Substring($userSkills.Length).TrimStart('\').Replace('\', '/')
  $manifestTargets += [pscustomobject]@{ id = "skills/$rel"; target = $f.FullName; sha256 = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.ToLower() }
}

# 4. Install/select the bundle in every target profile. pnpm adds the dependency
#    and the plugin manager's reconcile() appends the entry to the profile's
#    ordered `dsh.profile.bundles` (@deepseek-ai/dsh-plugin-manager operations.ts).
#    This REPLACES the old directory copy: "selected in dsh.profile.bundles" is
#    what makes a preset exist under DSH >= 0.1.7.
$profilesDir = Join-Path $dshHome 'profiles'
$targetProfiles = @()
if ($ProfileName) {
  $targetProfiles = @($ProfileName)
} elseif (Test-Path $profilesDir) {
  $targetProfiles = @(Get-ChildItem -Path $profilesDir -Directory | Where-Object {
    $_.Name -ne 'node_modules' -and (Test-Path (Join-Path $_.FullName 'package.json'))
  } | ForEach-Object { $_.Name })
}

$selectedIn = @()
if ($targetProfiles.Count -eq 0) {
  Write-Host "  skip: no DSH profile found under $profilesDir"
} else {
  $dshCmd = Get-Command dsh -ErrorAction SilentlyContinue
  if (-not $dshCmd) {
    throw "dsh not found on PATH - the bundle is installed through 'dsh plugin --profile <p> add <dir>'"
  }
  foreach ($profileName in $targetProfiles) {
    dsh plugin --profile $profileName add $bundleDir
    if ($LASTEXITCODE -ne 0) { throw "failed to install the bundle into profile '$profileName'" }
    $selectedIn += $profileName
    Write-Host "  OK bundle installed + selected in dsh.profile.bundles (profile: $profileName)"
  }
}

function Write-InstallManifest($path, $roots, $targets) {
  $sb = New-Object System.Text.StringBuilder
  [void]$sb.AppendLine('schema_version: 2')
  [void]$sb.AppendLine("# Auto-generated by install.ps1 - do not hand-edit (regenerated on install).")
  [void]$sb.AppendLine("source_root: $($roots -replace '\\', '/')")
  [void]$sb.AppendLine("source_commit: $sourceCommit")
  [void]$sb.AppendLine("installed_at: $installedAt")
  [void]$sb.AppendLine("bundle_name: $bundleName")
  [void]$sb.AppendLine("bundle_patch: $($patchRel -replace '\\', '/')")
  [void]$sb.AppendLine("selected_in_profiles: [$(($selectedIn | ForEach-Object { "'$_'" }) -join ', ')]")
  [void]$sb.AppendLine('artifacts:')
  foreach ($t in ($targets | Sort-Object id)) {
    [void]$sb.AppendLine("  - id: $($t.id)")
    [void]$sb.AppendLine("    target: $($t.target -replace '\\', '/')")
    [void]$sb.AppendLine("    sha256: $($t.sha256)")
  }
  Set-Content -Path $path -Value $sb.ToString() -Encoding UTF8
}

$userManifest = Join-Path $userSkills '.re-framework-manifest.yaml'
Write-InstallManifest $userManifest $srcRoot $manifestTargets
Write-Host "  wrote install manifest: $($manifestTargets.Count) artifacts @ $sourceCommit"

Write-Host ""
Write-Host "Installed:"
Write-Host "  bundle : $bundleName ($bundleDir)"
if ($selectedIn.Count -gt 0) { Write-Host "  selected in profile(s): $($selectedIn -join ', ')" } else { Write-Host "  selected in profile(s): (none - no DSH profile found)" }
$userCount = @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match $skillNamespace }).Count
Write-Host "  user-global skills: $userCount ref-family directories (expected 17)"
Write-Host ""
Write-Host "Next: run scripts/selfcheck.ps1 to verify; open a NEW session (or wait for the"
Write-Host "      profile hot-reload) and pick the 'RE-Framework' agent preset."
