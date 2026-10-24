#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RE-Framework target-module manager (P1) - spec §5.7.

Purpose
  Keep the *target program's* module structure as the single organizing axis for
  artifacts, lifted code and knowledge. Derives a module map from real evidence
  (build files / explicit hints / existing module dirs), partitions
  `.artifacts/modules/<id>/`, and provides a transactional correction engine
  (plan -> apply -> rollback) for when the boundary was wrong.

Files
  .artifacts/target-modules.yaml        canonical map (human-editable)
  .artifacts/target-modules.state.json  machine state for the contract guard
  .artifacts/index.yaml                 entries carry target_module / module_revision
  .artifacts/_migrations/<rev>/         plan.json + journal.json + backup/
  .artifacts/modules/<id>/              artifacts per module
  .artifacts/unassigned/                first-class unassigned bucket

Commands
  derive <project> [--hints FILE]
  status <project> [--json]
  verify <project> [--json]
  plan   <project> reassign --from A --to B --files f1,f2
  plan   <project> split --from A --new-id C --files f1,f2
  plan   <project> merge --from A --into B
  plan   <project> rename --module A --new-id C
  plan   <project> demote --module A --files f1,f2
  plan   <project> quarantine
  plan   <project> rebuild-index
  apply  <project> <plan.json>
  repair <project>

Exit codes: 0 ok; 1 verification/action failure; 2 usage or IO error.
"""
import argparse
import datetime as _dt
import hashlib
import json
import os
import shutil
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print('target_modules.py requires PyYAML: pip install pyyaml', file=sys.stderr)
    sys.exit(2)

MAP_NAME = 'target-modules.yaml'
STATE_NAME = 'target-modules.state.json'
INDEX_NAME = 'index.yaml'
MIGRATIONS = '_migrations'
AUDIT = '_audit'
ARTIFACT_DIR = '.artifacts'
MODULES_DIR = 'modules'
UNASSIGNED_DIR = 'unassigned'
REVIEWS_DIR = 'reviews'

BOUNDARY_KINDS = {
    'rtti-cluster', 'namespace', 'package', 'section', 'import-group',
    'module-graph', 'build-unit', 'community', 'hint',
}
CONFIDENCE = {'derived', 'converged', 'disputed', 'confirmed'}
MODULE_STATUS = {'active', 'retired'}
ARTIFACT_STATUS = {'draft', 'candidate', 'confirmed'}
KB_FRONTMATTER = ('signature', 'verdict', 'lesson', 'status')


# ── small helpers ────────────────────────────────────────────────────────────

def now():
    return _dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def artifacts_dir(project):
    return os.path.join(project, ARTIFACT_DIR)


def map_path(project):
    return os.path.join(artifacts_dir(project), MAP_NAME)


def state_path(project):
    return os.path.join(artifacts_dir(project), STATE_NAME)


def index_path(project):
    return os.path.join(artifacts_dir(project), INDEX_NAME)


def read_yaml(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as fh:
        data = yaml.safe_load(fh)
    return default if data is None else data


def write_text(path, text):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    os.replace(tmp, path)


def write_yaml(path, data):
    write_text(path, yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def write_json(path, data):
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def rel(project, path):
    return os.path.relpath(path, project).replace('\\', '/')


def load_map(project, required=True):
    data = read_yaml(map_path(project))
    if data is None:
        if required:
            die(f'no module map at {map_path(project)} - run: target_modules.py derive <project>')
        return None
    data.setdefault('schema_version', 1)
    data.setdefault('revision', 1)
    data.setdefault('modules', [])
    data.setdefault('unassigned', {'reason': '', 'entries': 0})
    data.setdefault('history', [])
    data.setdefault('config', {})
    data['config'].setdefault('code_root', 'work')
    data['config'].setdefault('kb_partition', True)
    data['config'].setdefault('naming', 'auto')
    return data


def module_by_id(data, module_id):
    for mod in data['modules']:
        if mod.get('id') == module_id:
            return mod
    return None


def require_module(data, module_id):
    mod = module_by_id(data, module_id)
    if mod is None:
        die(f'module "{module_id}" is not declared in the map (have: '
            + ', '.join(m.get('id', '?') for m in data['modules']) + ')')
    return mod


def module_dir(project, module_id):
    return os.path.join(artifacts_dir(project), MODULES_DIR, module_id)


def unassigned_dir(project):
    return os.path.join(artifacts_dir(project), UNASSIGNED_DIR)


def reviews_for(project, module_id):
    d = os.path.join(module_dir(project, module_id), REVIEWS_DIR)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        if name.endswith('.md'):
            out.append(name[:-3])
    return out


def die(message, code=1):
    print('FAIL: ' + message, file=sys.stderr)
    sys.exit(code)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


# ── artifact scan / index rebuild ────────────────────────────────────────────

def artifact_files(project, root, target_module):
    """Yield (abs_path, kind, status, name, locator) under root."""
    if not os.path.isdir(root):
        return
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in sorted(filenames):
            if not name.endswith(('.yaml', '.yml')):
                continue
            if name in ('index-entry.yaml',):
                continue
            path = os.path.join(dirpath, name)
            kind = kind_of(name)
            status = 'draft'
            art_name, locator = '', ''
            try:
                doc = read_yaml(path, {})
                if isinstance(doc, dict):
                    status = str(doc.get('status', 'draft'))
                    art_name = str(doc.get('name') or doc.get('class_name') or '')
                    locator = str(doc.get('locator') or doc.get('address') or '')
            except Exception:
                pass
            yield path, kind, status, art_name, locator


def kind_of(filename):
    base = filename.lower()
    if base == 'class.yaml':
        return 'class'
    if base in ('method.yaml', 'function.yaml'):
        return 'method'
    if base.startswith('xref'):
        return 'xref'
    return 'artifact'


def rebuild_index(project, data, write=True):
    entries = []
    seen_paths = {}
    for mod in data['modules']:
        mid = mod['id']
        root = module_dir(project, mid)
        for path, kind, status, name, locator in artifact_files(project, root, mid):
            key = rel(project, path)
            if key in seen_paths:
                continue
            seen_paths[key] = mid
            eid = f'{mid}:{name or os.path.basename(path)}:{locator or key}'
            entries.append({
                'id': eid,
                'path': key,
                'kind': kind,
                'status': status if status in ARTIFACT_STATUS else 'draft',
                'target_module': mid,
                'module_revision': data['revision'],
            })
    un = unassigned_dir(project)
    for path, kind, status, name, locator in artifact_files(project, un, 'unassigned'):
        key = rel(project, path)
        if key in seen_paths:
            continue
        seen_paths[key] = 'unassigned'
        entries.append({
            'id': f'unassigned:{name or os.path.basename(path)}:{locator or key}',
            'path': key,
            'kind': kind,
            'status': status if status in ARTIFACT_STATUS else 'draft',
            'target_module': 'unassigned',
            'module_revision': data['revision'],
        })
    index = {
        'schema_version': 1,
        'project': data.get('project') or os.path.basename(os.path.abspath(project)),
        'module': 'core',
        'revision': data['revision'],
        'entries': entries,
    }
    if write:
        write_yaml(index_path(project), index)
    return index


def count_unassigned(project):
    root = unassigned_dir(project)
    if not os.path.isdir(root):
        return 0
    n = 0
    for dirpath, _d, files in os.walk(root):
        n += sum(1 for f in files if f.endswith(('.yaml', '.yml')))
    return n


def write_state(project, data):
    modules = []
    for mod in data['modules']:
        modules.append({
            'id': mod['id'],
            'status': mod.get('status', 'active'),
            'confidence': mod.get('confidence', 'derived'),
            'provides': list(mod.get('provides') or []),
            'requires': list(mod.get('requires') or []),
            'reviews': reviews_for(project, mod['id']),
        })
    state = {
        'schema_version': 1,
        'project': data.get('project'),
        'revision': data['revision'],
        'modules': modules,
        'unassigned': {'count': count_unassigned(project)},
        'updated_at': now(),
    }
    write_json(state_path(project), state)
    return state


# ── derive ───────────────────────────────────────────────────────────────────

def build_units(project):
    """Return [(module_id, locator, source)] from real build files."""
    out = []
    pkg = read_yaml(os.path.join(project, 'package.json'), {})
    if isinstance(pkg, dict):
        ws = pkg.get('workspaces')
        patterns = []
        if isinstance(ws, list):
            patterns = ws
        elif isinstance(ws, dict) and isinstance(ws.get('packages'), list):
            patterns = ws['packages']
        for pat in patterns:
            pat = str(pat).rstrip('/')
            base = pat.split('*')[0].strip('/')
            if not base:
                continue
            d = os.path.join(project, base)
            if os.path.isdir(d):
                for name in sorted(os.listdir(d)):
                    if os.path.isdir(os.path.join(d, name)):
                        out.append((name, f'{base}/{name}', 'package.json#workspaces'))
    cargo = os.path.join(project, 'Cargo.toml')
    if os.path.exists(cargo):
        text = open(cargo, encoding='utf-8', errors='replace').read()
        in_ws = False
        for line in text.splitlines():
            s = line.strip()
            if s.startswith('[workspace]'):
                in_ws = True
                continue
            if in_ws and s.startswith('['):
                in_ws = False
            if in_ws and s.startswith('members'):
                rest = s.split('=', 1)[-1]
                for item in rest.replace('[', '').replace(']', '').split(','):
                    item = item.strip().strip('"').strip("'")
                    if item:
                        base = item.split('*')[0].strip('/')
                        out.append((os.path.basename(base), item, 'Cargo.toml#workspace'))
    pom = os.path.join(project, 'pom.xml')
    if os.path.exists(pom):
        import re
        text = open(pom, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'<module>([^<]+)</module>', text):
            item = m.group(1).strip()
            if item:
                out.append((os.path.basename(item.rstrip('/')), item, 'pom.xml#modules'))
    return out


def normalise_id(raw):
    out = []
    for ch in str(raw):
        if ch.isalnum() or ch in '-_':
            out.append(ch.lower())
        elif ch in './\\ ':
            out.append('-')
    ident = ''.join(out).strip('-')
    while '--' in ident:
        ident = ident.replace('--', '-')
    return ident or 'module'


def cmd_derive(project, hints_path=None):
    art = artifacts_dir(project)
    os.makedirs(os.path.join(art, MODULES_DIR), exist_ok=True)
    os.makedirs(os.path.join(art, UNASSIGNED_DIR), exist_ok=True)
    data = load_map(project, required=False) or {
        'schema_version': 1,
        'project': os.path.basename(os.path.abspath(project)),
        'revision': 1,
        'config': {'code_root': 'work', 'kb_partition': True, 'naming': 'auto'},
        'modules': [],
        'unassigned': {'reason': 'no boundary evidence yet', 'entries': count_unassigned(project)},
        'history': [],
    }
    existing = {m['id']: m for m in data['modules']}
    added = []

    def add(mid, title, kind, locator, source, confidence):
        if mid in existing:
            return
        data['modules'].append({
            'id': mid,
            'title': title,
            'aliases': [],
            'boundaries': [{'kind': kind, 'locator': locator, 'evidence': source}],
            'confidence': confidence,
            'provides': [],
            'requires': [],
            'code_dirs': [os.path.join(data['config'].get('code_root', 'work'), mid)],
            'status': 'active',
        })
        existing[mid] = data['modules'][-1]
        added.append(mid)

    # 1) explicit hints win (a human/agent may know boundaries the build files do not)
    if hints_path:
        hints = read_yaml(hints_path, [])
        if isinstance(hints, dict):
            hints = hints.get('modules', [])
        for item in hints or []:
            if not isinstance(item, dict) or not item.get('id'):
                continue
            mid = normalise_id(item['id'])
            add(mid, item.get('title', mid), item.get('kind', 'hint'),
                item.get('locator', ''), item.get('evidence', os.path.basename(hints_path)), 'derived')
    # 2) build units
    for raw_id, locator, source in build_units(project):
        mid = normalise_id(raw_id)
        add(mid, raw_id, 'build-unit', locator, source, 'converged')
    # 3) existing module dirs survive
    md = os.path.join(art, MODULES_DIR)
    for name in sorted(os.listdir(md)):
        if os.path.isdir(os.path.join(md, name)) and name not in existing:
            add(normalise_id(name), name, 'hint', f'{MODULES_DIR}/{name}', 'existing directory', 'derived')

    if not data['modules']:
        print('FAIL: no module evidence found (no package.json workspaces / Cargo workspace / '
              'pom modules / existing .artifacts/modules/*) - pass --hints <file> or write '
              'artifacts under .artifacts/unassigned/', file=sys.stderr)
        return 1

    data['revision'] = int(data['revision']) + (1 if added else 0)
    data['unassigned']['entries'] = count_unassigned(project)
    write_yaml(map_path(project), data)
    for mod in data['modules']:
        os.makedirs(module_dir(project, mod['id']), exist_ok=True)
    rebuild_index(project, data)
    write_state(project, data)
    print(f'derived {len(data["modules"])} module(s) at revision {data["revision"]}: '
          + ', '.join(m['id'] for m in data['modules']))
    if added:
        print('added: ' + ', '.join(added))
    legacy = []
    art = artifacts_dir(project)
    for name in sorted(os.listdir(art)) if os.path.isdir(art) else []:
        if name in (MODULES_DIR, UNASSIGNED_DIR, MIGRATIONS, AUDIT) or name.startswith('.'):
            continue
        if os.path.isdir(os.path.join(art, name)):
            for dirpath, _d, files in os.walk(os.path.join(art, name)):
                legacy += [f for f in files if f.endswith(('.yaml', '.yml'))]
    if legacy:
        print(f'NOTE: {len(legacy)} legacy flat artifact(s) outside modules/ - '
              'run: plan adopt-legacy (then apply) to move them into unassigned/')
    return 0


# ── verify (G1-G9) ───────────────────────────────────────────────────────────

def verify(project, data=None):
    data = data or load_map(project)
    failures, warnings = [], []
    modules = {m['id']: m for m in data['modules']}

    # G1: path belongs to exactly one module (index) + no duplicate content across modules
    index = read_yaml(index_path(project), {'entries': []}) or {'entries': []}
    entries = index.get('entries') or []
    by_path = {}
    for e in entries:
        p = e.get('path')
        if p in by_path:
            failures.append(f'G1 duplicate index path: {p}')
        by_path[p] = e
    hashes = {}
    for mod in data['modules']:
        for path, *_ in artifact_files(project, module_dir(project, mod['id']), mod['id']):
            h = sha256(path)
            if h in hashes:
                failures.append(f'G1 duplicate content (E4): {rel(project, path)} == {rel(project, hashes[h])}')
            else:
                hashes[h] = path
    # G2: every active module has at least one boundary with evidence
    for mid, mod in modules.items():
        if mod.get('status', 'active') != 'active':
            continue
        b = mod.get('boundaries') or []
        if not b or not any(x.get('kind') in BOUNDARY_KINDS and x.get('locator') for x in b):
            failures.append(f'G2 module "{mid}" has no boundary evidence')
    # G3: unassigned count matches
    expect = int((data.get('unassigned') or {}).get('entries', 0))
    actual = count_unassigned(project)
    if expect != actual:
        failures.append(f'G3 unassigned count mismatch: map={expect} disk={actual}')
    # G4: revision consistency
    rev = int(data['revision'])
    for e in entries:
        er = e.get('module_revision')
        if er != rev:
            failures.append(f'G4 entry {e.get("id")} has module_revision={er}, map={rev}')
    # G5: no orphan module dirs; retired modules keep no artifacts
    md = os.path.join(artifacts_dir(project), MODULES_DIR)
    if os.path.isdir(md):
        for name in sorted(os.listdir(md)):
            if not os.path.isdir(os.path.join(md, name)):
                continue
            if name not in modules:
                failures.append(f'G5 orphan module directory: {MODULES_DIR}/{name}')
            elif modules[name].get('status') == 'retired':
                files = [rel(project, p) for p, *_ in artifact_files(project, module_dir(project, name), name)]
                if files:
                    failures.append(f'G5 retired module "{name}" still holds {len(files)} artifact(s)')
    # G6: provides unique; requires resolve
    providers = {}
    for mid, mod in modules.items():
        for c in mod.get('provides') or []:
            if c in providers and providers[c] != mid:
                failures.append(f'G6 contract "{c}" provided by both "{providers[c]}" and "{mid}"')
            providers[c] = mid
    for mid, mod in modules.items():
        for c in mod.get('requires') or []:
            if c not in providers:
                failures.append(f'G6 module "{mid}" requires unresolved contract "{c}"')
    # G7: every applied revision has a migration record
    for rev_h in data.get('history') or []:
        r = rev_h.get('revision')
        d = os.path.join(artifacts_dir(project), MIGRATIONS, str(r))
        if not (os.path.exists(os.path.join(d, 'plan.json')) and os.path.exists(os.path.join(d, 'journal.json'))):
            failures.append(f'G7 revision {r} lacks plan.json/journal.json')
    # G9: no artifact outside modules/ / unassigned/ (legacy flat trees must be adopted)
    art = artifacts_dir(project)
    allowed = {MODULES_DIR, UNASSIGNED_DIR, MIGRATIONS, AUDIT}
    for name in sorted(os.listdir(art)) if os.path.isdir(art) else []:
        full = os.path.join(art, name)
        if name in allowed or name.startswith('.'):
            continue
        if os.path.isfile(full) and name in (MAP_NAME, STATE_NAME, INDEX_NAME):
            continue
        if os.path.isdir(full):
            for dirpath, _d, files in os.walk(full):
                for f in files:
                    if f.endswith(('.yaml', '.yml')):
                        failures.append(f'G9 unclassified artifact: {rel(project, os.path.join(dirpath, f))} '
                                        '(run: plan adopt-legacy)')
        elif name.endswith(('.yaml', '.yml')):
            failures.append(f'G9 unclassified artifact: {rel(project, full)} (run: plan adopt-legacy)')
    # G8: candidate/confirmed modules have a review record for the current revision
    for mid, mod in modules.items():
        if mod.get('status') != 'active':
            continue
        status = 'draft'
        for path, _k, st, *_ in artifact_files(project, module_dir(project, mid), mid):
            if st == 'candidate':
                status = 'candidate'
                break
            if st == 'confirmed':
                status = 'confirmed'
                break
        if status in ('candidate', 'confirmed'):
            if str(rev) not in reviews_for(project, mid):
                failures.append(f'G8 module "{mid}" is {status} without reviews/{rev}.md')
    for mid, mod in modules.items():
        if mod.get('confidence') == 'disputed':
            warnings.append(f'module "{mid}" is disputed (provisional, does not block)')
    return {'failures': failures, 'warnings': warnings, 'revision': rev, 'modules': len(modules)}


def cmd_verify(project, as_json=False):
    res = verify(project)
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for w in res['warnings']:
            print('WARN: ' + w)
        if res['failures']:
            for f in res['failures']:
                print('FAIL: ' + f)
        else:
            print(f'OK: {res["modules"]} module(s), revision {res["revision"]}, G1-G9 pass')
    return 0 if not res['failures'] else 1


# ── status ───────────────────────────────────────────────────────────────────

def cmd_status(project, as_json=False):
    data = load_map(project)
    res = verify(project, data)
    mods = []
    for mod in data['modules']:
        mods.append({
            'id': mod['id'],
            'status': mod.get('status', 'active'),
            'confidence': mod.get('confidence', 'derived'),
            'boundaries': len(mod.get('boundaries') or []),
            'reviews': reviews_for(project, mod['id']),
            'provides': list(mod.get('provides') or []),
            'requires': list(mod.get('requires') or []),
        })
    out = {
        'project': data.get('project'),
        'revision': data['revision'],
        'modules': mods,
        'unassigned': {'map': int((data.get('unassigned') or {}).get('entries', 0)),
                       'disk': count_unassigned(project)},
        'verify': res,
    }
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f'project: {out["project"]}  revision: {out["revision"]}')
        for m in mods:
            print(f'  - {m["id"]}: {m["status"]}/{m["confidence"]} '
                  f'boundaries={m["boundaries"]} reviews={m["reviews"] or "-"} '
                  f'provides={m["provides"] or "-"} requires={m["requires"] or "-"}')
        print(f'  unassigned: map={out["unassigned"]["map"]} disk={out["unassigned"]["disk"]}')
        for f in res['failures']:
            print('  FAIL: ' + f)
    return 0 if not res['failures'] else 1


# ── plan / apply ─────────────────────────────────────────────────────────────

def cmd_plan(project, action, args):
    data = load_map(project)
    rev = int(data['revision']) + 1
    moves = []  # {from, to, kind}
    index_updates = []
    history_action = action
    detail = {}

    def collect(src_module, files):
        src_root = module_dir(project, src_module)
        out = []
        for item in files:
            item = item.strip()
            if not item:
                continue
            cand = os.path.join(src_root, item)
            if not os.path.exists(cand):
                die(f'file not found: {rel(project, cand)}')
            out.append(cand)
        return out

    if action == 'reassign':
        src, dst = args['from'], args['to']
        require_module(data, src)
        require_module(data, dst)
        for path in collect(src, args['files']):
            moves.append({'from': rel(project, path),
                          'to': rel(project, os.path.join(module_dir(project, dst), os.path.basename(path)))})
        detail = {'from': src, 'to': dst}
    elif action == 'split':
        src, new_id = args['from'], normalise_id(args['new_id'])
        require_module(data, src)
        if module_by_id(data, new_id):
            die(f'module "{new_id}" already exists')
        for path in collect(src, args['files']):
            moves.append({'from': rel(project, path),
                          'to': rel(project, os.path.join(module_dir(project, new_id), os.path.basename(path)))})
        detail = {'from': src, 'new_id': new_id}
    elif action == 'merge':
        src, dst = args['from'], args['into']
        require_module(data, src)
        require_module(data, dst)
        src_root = module_dir(project, src)
        for path, *_ in artifact_files(project, src_root, src):
            moves.append({'from': rel(project, path),
                          'to': rel(project, os.path.join(module_dir(project, dst), os.path.basename(path)))})
        detail = {'from': src, 'into': dst}
    elif action == 'rename':
        old, new_id = args['module'], normalise_id(args['new_id'])
        require_module(data, old)
        if module_by_id(data, new_id):
            die(f'module "{new_id}" already exists')
        old_root = module_dir(project, old)
        for path, *_ in artifact_files(project, old_root, old):
            moves.append({'from': rel(project, path),
                          'to': rel(project, os.path.join(module_dir(project, new_id), os.path.basename(path)))})
        detail = {'from': old, 'new_id': new_id}
    elif action == 'demote':
        src = args['module']
        require_module(data, src)
        for path in collect(src, args['files']):
            moves.append({'from': rel(project, path),
                          'to': rel(project, os.path.join(unassigned_dir(project), os.path.basename(path)))})
        detail = {'from': src, 'to': 'unassigned'}
    elif action == 'quarantine':
        md = os.path.join(artifacts_dir(project), MODULES_DIR)
        known = {m['id'] for m in data['modules']}
        for name in sorted(os.listdir(md)) if os.path.isdir(md) else []:
            full = os.path.join(md, name)
            if os.path.isdir(full) and name not in known:
                for path, *_ in artifact_files(project, full, name):
                    moves.append({'from': rel(project, path),
                                  'to': rel(project, os.path.join(unassigned_dir(project), '_orphaned', name, os.path.basename(path)))})
        detail = {'orphans': True}
    elif action == 'rebuild-index':
        detail = {'rebuild': True}
    elif action == 'adopt-legacy':
        art = artifacts_dir(project)
        allowed = {MODULES_DIR, UNASSIGNED_DIR, MIGRATIONS, AUDIT}
        for name in sorted(os.listdir(art)) if os.path.isdir(art) else []:
            full = os.path.join(art, name)
            if name in allowed or name.startswith('.'):
                continue
            if not os.path.isdir(full):
                continue
            for dirpath, _d, files in os.walk(full):
                for f in files:
                    if not f.endswith(('.yaml', '.yml')):
                        continue
                    path = os.path.join(dirpath, f)
                    tail = rel(project, path)[len(ARTIFACT_DIR) + 1:]
                    moves.append({'from': rel(project, path),
                                  'to': f'{ARTIFACT_DIR}/{UNASSIGNED_DIR}/{tail}'})
        detail = {'adopt': True}
    else:
        die(f'unknown action "{action}"')

    if not moves and action != 'rebuild-index':
        die('plan is empty - nothing to move' if action != 'adopt-legacy'
            else 'no legacy flat artifacts found - nothing to adopt')

    plan = {
        'action': history_action,
        'revision': rev,
        'created_at': now(),
        'detail': detail,
        'moves': moves,
        'index_rebuild': True,
        'notes': args.get('notes', ''),
    }
    # dry-run: target conflicts and duplicate destinations
    dests = set()
    for mv in moves:
        dest = os.path.join(project, mv['to'].replace('/', os.sep))
        if dest in dests:
            die(f'duplicate destination in plan: {mv["to"]}')
        dests.add(dest)
        if os.path.exists(dest):
            die(f'destination already exists: {mv["to"]} (revision conflict; run verify/repair first)')
        if not os.path.exists(os.path.join(project, mv['from'].replace('/', os.sep))):
            die(f'source missing: {mv["from"]}')
    out = os.path.join(artifacts_dir(project), MIGRATIONS, str(rev), 'plan.json')
    write_json(out, plan)
    print(f'plan written: {rel(project, out)} ({len(moves)} move(s), revision {rev})')
    return 0


def downgrade_status(path):
    """Invalidate candidate/confirmed when an artifact changes module (proof applicability).

    Returns the previous status when a downgrade happened, else None.
    """
    try:
        doc = read_yaml(path, None)
    except Exception:
        return None
    if not isinstance(doc, dict):
        return None
    status = doc.get('status')
    if status not in ('candidate', 'confirmed'):
        return None
    doc['status'] = 'draft'
    write_yaml(path, doc)
    return status


def apply_plan(project, plan):
    data = load_map(project)
    rev = plan['revision']
    if rev != int(data['revision']) + 1:
        die(f'revision mismatch: plan targets {rev}, map is {data["revision"]}')
    mig_dir = os.path.join(artifacts_dir(project), MIGRATIONS, str(rev))
    backup_dir = os.path.join(mig_dir, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    journal = {'revision': rev, 'started_at': now(), 'moves': [], 'status': 'running'}
    journal_path = os.path.join(mig_dir, 'journal.json')
    backup = {}

    def snapshot(path):
        if path not in backup and os.path.exists(path):
            dst = os.path.join(backup_dir, rel(project, path))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(path, dst)
            backup[path] = dst

    try:
        for name in (map_path(project), index_path(project), state_path(project)):
            snapshot(name)
        for mv in plan['moves']:
            src = os.path.join(project, mv['from'].replace('/', os.sep))
            dst = os.path.join(project, mv['to'].replace('/', os.sep))
            snapshot(src)
            if os.path.exists(dst):
                raise RuntimeError(f'destination appeared after planning: {mv["to"]}')
            previous_status = downgrade_status(src)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            journal['moves'].append({'from': mv['from'], 'to': mv['to'], 'state': 'moved',
                                     'previous_status': previous_status})
        # map mutation
        detail = plan.get('detail') or {}
        action = plan['action']
        if action == 'split':
            src = require_module(data, detail['from'])
            data['modules'].append({
                'id': detail['new_id'], 'title': detail['new_id'], 'aliases': [],
                'boundaries': [{'kind': 'hint', 'locator': f'{MODULES_DIR}/{detail["new_id"]}',
                                'evidence': f'split from {detail["from"]} (rev {rev})'}],
                'confidence': 'derived', 'provides': [], 'requires': [],
                'code_dirs': [os.path.join(data['config'].get('code_root', 'work'), detail['new_id'])],
                'status': 'active',
            })
            src.setdefault('aliases', []).append(f'{detail["new_id"]} (split rev {rev})')
        elif action == 'merge':
            src = require_module(data, detail['from'])
            src['status'] = 'retired'
            src.setdefault('aliases', []).append(f'merged into {detail["into"]} (rev {rev})')
        elif action == 'rename':
            src = require_module(data, detail['from'])
            src['aliases'] = list(src.get('aliases') or []) + [src['id']]
            src['id'] = detail['new_id']
            src['title'] = src.get('title') or detail['new_id']
            for b in src.get('boundaries') or []:
                if str(b.get('locator', '')).startswith(f'{MODULES_DIR}/'):
                    b['locator'] = f'{MODULES_DIR}/{detail["new_id"]}'
        elif action == 'demote':
            pass
        elif action == 'quarantine':
            pass
        data['revision'] = rev
        data['unassigned']['entries'] = count_unassigned(project)
        data.setdefault('history', []).append({
            'revision': rev, 'action': action, 'detail': detail,
            'at': now(), 'plan': rel(project, os.path.join(mig_dir, 'plan.json')),
        })
        write_yaml(map_path(project), data)
        rebuild_index(project, data)
        write_state(project, data)
        journal['status'] = 'applied'
        journal['finished_at'] = now()
        write_json(journal_path, journal)
        print(f'applied revision {rev} ({len(plan["moves"])} move(s))')
        return 0
    except Exception as exc:  # rollback
        for mv in reversed(journal['moves']):
            src = os.path.join(project, mv['to'].replace('/', os.sep))
            dst = os.path.join(project, mv['from'].replace('/', os.sep))
            try:
                if os.path.exists(src):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.move(src, dst)
            except Exception:
                pass
        for orig, bak in backup.items():
            try:
                os.makedirs(os.path.dirname(orig), exist_ok=True)
                shutil.copy2(bak, orig)
            except Exception:
                pass
        journal['status'] = 'rolled-back'
        journal['error'] = str(exc)
        journal['finished_at'] = now()
        write_json(journal_path, journal)
        print(f'FAIL: apply failed and was rolled back: {exc}', file=sys.stderr)
        return 1


def cmd_apply(project, plan_path):
    plan = json.load(open(plan_path, encoding='utf-8'))
    return apply_plan(project, plan)


# ── repair ───────────────────────────────────────────────────────────────────

def cmd_repair(project):
    data = load_map(project, required=False)
    if data is None:
        die('no module map - nothing to repair')
    for mod in data['modules']:
        os.makedirs(module_dir(project, mod['id']), exist_ok=True)
    os.makedirs(unassigned_dir(project), exist_ok=True)
    data['unassigned']['entries'] = count_unassigned(project)
    write_yaml(map_path(project), data)
    rebuild_index(project, data)
    write_state(project, data)
    res = verify(project, data)
    print(f'repaired index/state at revision {data["revision"]}; '
          f'{"G1-G9 pass" if not res["failures"] else str(len(res["failures"])) + " failure(s)"}')
    return 0 if not res['failures'] else 1


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv):
    ap = argparse.ArgumentParser(description='RE-Framework target-module manager (P1)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('derive')
    p.add_argument('project')
    p.add_argument('--hints')

    for name in ('status', 'verify', 'repair'):
        p = sub.add_parser(name)
        p.add_argument('project')
        p.add_argument('--json', action='store_true')

    p = sub.add_parser('plan')
    p.add_argument('project')
    p.add_argument('action', choices=['reassign', 'split', 'merge', 'rename', 'demote',
                                      'quarantine', 'rebuild-index', 'adopt-legacy'])
    p.add_argument('--from', dest='src')
    p.add_argument('--to', dest='dst')
    p.add_argument('--into')
    p.add_argument('--module')
    p.add_argument('--new-id')
    p.add_argument('--files', default='')
    p.add_argument('--notes', default='')

    p = sub.add_parser('apply')
    p.add_argument('project')
    p.add_argument('plan')

    a = ap.parse_args(argv)
    project = os.path.abspath(a.project)
    if not os.path.isdir(project):
        die(f'project directory not found: {project}', 2)

    if a.cmd == 'derive':
        return cmd_derive(project, a.hints)
    if a.cmd == 'status':
        return cmd_status(project, a.json)
    if a.cmd == 'verify':
        return cmd_verify(project, a.json)
    if a.cmd == 'repair':
        return cmd_repair(project)
    if a.cmd == 'plan':
        files = [x for x in (a.files or '').split(',') if x.strip()]
        args = {'from': a.src, 'to': a.dst, 'into': a.into, 'module': a.module,
                'new_id': a.new_id, 'files': files, 'notes': a.notes}
        return cmd_plan(project, a.action, args)
    if a.cmd == 'apply':
        return cmd_apply(project, a.plan)
    die('unknown command', 2)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
