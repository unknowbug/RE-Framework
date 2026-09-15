#!/usr/bin/env bash
# install.sh — Install/sync the RE-Framework DSH project into the DSH runtime
# (Linux / macOS; bash twin of install.ps1 for hosts without PowerShell, e.g.
# a Kylin office desktop).
#
# Source of truth: <repo>/dsh
#   preset/agent.cordis.yml + preset/preset.yml  → $DSH_HOME/.agent-presets/re-framework/
#   plugins/re-framework-tools.js                → $DSH_HOME/.agent-presets/re-framework/plugins/
#   skills/*                                     → $DSH_HOME/.agent-presets/re-framework/skills/
#                                                → $DSH_HOME/skills/            (user-global)
#
# Same visibility design as install.ps1: skills are user-global (any preset,
# any working directory); the three ref_* tools live ONLY on the re-framework
# preset. The legacy global tool row (re-framework-tools-global) is withdrawn
# idempotently.
#
# GATE: never ship a plugin whose tool schemas are not compiled JSON Schema
# (a flat spec reaches the LLM without a top-level type and breaks EVERY
# session). The gate runs before anything is copied.
#
# Idempotent: safe to re-run after editing any source file.

set -euo pipefail

src_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dsh_home="${DSH_HOME:-$HOME/.dsh}"
preset_dir="$dsh_home/.agent-presets/re-framework"
user_skills="$dsh_home/skills"

echo "== RE-Framework DSH install =="
echo "source      : $src_root"
echo "preset      : $preset_dir"
echo "user skills : $user_skills (user-global, any session)"

# 0. Schema gate (see tests/check_plugin_schema.mjs for why this is mandatory).
if command -v node >/dev/null 2>&1; then
  if ! node --no-warnings "$src_root/tests/check_plugin_schema.mjs"; then
    echo "plugin tool-schema check failed - refusing to install" >&2
    exit 1
  fi
elif [ "${SKIP_SCHEMA_CHECK:-0}" = "1" ]; then
  echo "  WARNING: node not found - schema gate SKIPPED (SKIP_SCHEMA_CHECK=1)"
else
  echo "node not found: the plugin tool-schema gate cannot run." >&2
  echo "Install Node.js, or re-run with SKIP_SCHEMA_CHECK=1 to bypass (not recommended)." >&2
  exit 1
fi

# 1. Cleanup legacy wrong mounts (2026-08-13 incident + 2026-08-15 reversal).
legacy_home_patch="$dsh_home/cordis.patch.yml"
if [ -f "$legacy_home_patch" ] && grep -q 're-framework-tools-global' "$legacy_home_patch"; then
  rm -f "$legacy_home_patch"
  echo "  - removed legacy ~/.dsh/cordis.patch.yml (host does not read it)"
fi
if [ -d "$dsh_home/plugins/re-framework" ]; then
  rm -rf "$dsh_home/plugins/re-framework"
  echo "  - removed legacy ~/.dsh/plugins/re-framework/ (wrong location)"
fi

# 1c. Withdraw the global tool row from every profile patch (idempotent): drop
#     any re-framework-tools-global insert row, keep everything else (e.g.
#     anchorlaw-tools-global), and delete the profile-local plugin copy.
if [ -d "$dsh_home/profiles" ]; then
  for profile in "$dsh_home"/profiles/*/; do
    [ -f "${profile}package.json" ] || continue
    patch="${profile}cordis.patch.yml"
    if [ -f "$patch" ] && grep -q 're-framework-tools-global' "$patch"; then
      REF_PATCH_PATH="$patch" python3 - <<'PY'
import io, os, sys
try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required to edit a profile patch - run: pip3 install pyyaml")
path = os.environ['REF_PATCH_PATH']
with io.open(path, encoding='utf-8') as f:
    data = yaml.safe_load(f)
rows = list(data) if isinstance(data, list) else []
kept = [r for r in rows if not (
    isinstance(r, dict) and any(
        (e or {}).get('id') == 're-framework-tools-global' for e in (r.get('insert') or [])))]
if len(kept) != len(rows):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(yaml.safe_dump(kept, allow_unicode=True, sort_keys=False))
    print('removed')
else:
    print('absent')
PY
      echo "  - withdrew re-framework-tools-global from $patch"
    fi
    if [ -d "${profile}plugins/re-framework" ]; then
      rm -rf "${profile}plugins/re-framework"
      echo "  - removed ${profile}plugins/re-framework (profile-local plugin copy)"
    fi
  done
fi

# 2. Preset composition + metadata
mkdir -p "$preset_dir"
cp -f "$src_root/preset/agent.cordis.yml" "$preset_dir/"
cp -f "$src_root/preset/preset.yml"       "$preset_dir/"

# 3. Plugin file (preset-embedded)
mkdir -p "$preset_dir/plugins"
cp -f "$src_root/plugins/re-framework-tools.js" "$preset_dir/plugins/"

# 4. Skills: preset-embedded refresh + user-global refresh.
#    `cp -R src/. dst/` copies the CONTENTS (a bare `cp -R src dst` would nest
#    a second skills/ level when dst already exists).
if [ -d "$src_root/skills" ]; then
  rm -rf "$preset_dir/skills"
  cp -R "$src_root/skills" "$preset_dir/skills"
  mkdir -p "$user_skills"
  cp -R "$src_root/skills/." "$user_skills/"
fi

echo ""
echo "Installed:"
find "$preset_dir" -type f | sed "s|^$preset_dir|  preset|"
user_count=0
for d in "$user_skills"/core-* "$user_skills"/re-* "$user_skills"/recode-* \
         "$user_skills"/swe-* "$user_skills"/ref-*; do
  if [ -d "$d" ]; then user_count=$((user_count + 1)); fi
done
echo "  user-global skills: $user_count ref-family directories (expected 17)"
echo ""
echo "Next: run scripts/selfcheck.ps1 (PowerShell) or verify manually; ref-* skills are"
echo "      user-global (any session), the ref_* tools exist ONLY on the re-framework preset."
