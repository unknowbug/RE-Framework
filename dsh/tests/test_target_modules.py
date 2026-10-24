#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixture tests for scripts/target_modules.py (spec §5.7, P1).

Runs a real project fixture in .investigations/_tm_fixture/ and asserts:
  derive / verify(G1,G2,G5,G6,G8,G9) / adopt-legacy / reassign / rollback.

Usage: python dsh/tests/test_target_modules.py
Exit: 0 all pass; 1 failure.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, 'scripts'))

import target_modules as tm  # noqa: E402

ROOT = os.path.join(REPO, '.investigations', '_tm_fixture')
PROJECT = os.path.join(ROOT, 'project')

failures = []


def check(name, cond, detail=''):
    if cond:
        print(f'  OK   {name}')
    else:
        print(f'  FAIL {name} {detail}')
        failures.append(name)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


def setup():
    if os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(os.path.join(PROJECT, 'packages', 'alpha'))
    os.makedirs(os.path.join(PROJECT, 'packages', 'beta'))
    write(os.path.join(PROJECT, 'package.json'), '{"name":"fx","workspaces":["packages/*"]}\n')
    write(os.path.join(PROJECT, '.artifacts', 'classes', 'Legacy.yaml'),
          'schema_version: 1\nclass_name: Legacy\nlocator: "0x1000"\nstatus: draft\n')


def run(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except SystemExit as exc:
        return int(exc.code or 0)


def main():
    setup()
    print('[1] derive')
    rc = run(tm.cmd_derive, PROJECT, None)
    check('derive exit 0', rc == 0)
    data = tm.load_map(PROJECT)
    ids = sorted(m['id'] for m in data['modules'])
    check('two build modules', ids == ['alpha', 'beta'], str(ids))
    check('state json written', os.path.exists(tm.state_path(PROJECT)))
    state = json.load(open(tm.state_path(PROJECT), encoding='utf-8'))
    check('state modules', sorted(m['id'] for m in state['modules']) == ['alpha', 'beta'], str(state))

    print('[2] legacy artifact is G9 red until adopted')
    res = tm.verify(PROJECT)
    check('G9 flags legacy', any('G9' in f for f in res['failures']), str(res['failures']))
    rc = run(tm.cmd_plan, PROJECT, 'adopt-legacy',
             {'from': None, 'to': None, 'into': None, 'module': None, 'new_id': None,
              'files': [], 'notes': ''})
    check('adopt plan exit 0', rc == 0)
    plan_path = os.path.join(tm.artifacts_dir(PROJECT), '_migrations',
                             str(tm.load_map(PROJECT)['revision'] + 1), 'plan.json')
    rc = run(tm.apply_plan, PROJECT, json.load(open(plan_path, encoding='utf-8')))
    check('adopt apply exit 0', rc == 0)
    check('legacy moved to unassigned',
          os.path.exists(os.path.join(PROJECT, '.artifacts', 'unassigned', 'classes', 'Legacy.yaml')))
    res = tm.verify(PROJECT)
    check('verify after adopt', not res['failures'], str(res['failures']))

    print('[3] G8 candidate needs a revision-scoped review')
    art = os.path.join(tm.module_dir(PROJECT, 'alpha'), 'func.yaml')
    write(art, 'schema_version: 1\nname: Send\nlocator: "0x1400"\nstatus: candidate\n')
    rev = tm.load_map(PROJECT)['revision']
    res = tm.verify(PROJECT)
    check('G8 red without review', any('G8' in f for f in res['failures']), str(res['failures']))
    write(os.path.join(tm.module_dir(PROJECT, 'alpha'), 'reviews', f'{rev}.md'),
          '# review\nscope: alpha\nverdict: pass\n')
    res = tm.verify(PROJECT)
    check('G8 green with review', not res['failures'], str(res['failures']))

    print('[4] duplicate content is G1 red')
    write(os.path.join(tm.module_dir(PROJECT, 'beta'), 'func.yaml'),
          'schema_version: 1\nname: Send\nlocator: "0x1400"\nstatus: candidate\n')
    res = tm.verify(PROJECT)
    check('G1 duplicate', any('G1' in f for f in res['failures']), str(res['failures']))
    os.remove(os.path.join(tm.module_dir(PROJECT, 'beta'), 'func.yaml'))

    print('[5] orphan module directory is G5 red')
    write(os.path.join(PROJECT, '.artifacts', 'modules', 'ghost', 'g.yaml'),
          'name: G\nlocator: "1"\nstatus: draft\n')
    res = tm.verify(PROJECT)
    check('G5 orphan', any('G5' in f for f in res['failures']), str(res['failures']))
    shutil.rmtree(os.path.join(PROJECT, '.artifacts', 'modules', 'ghost'))

    print('[6] unresolved contract is G6 red')
    d = tm.load_map(PROJECT)
    for m in d['modules']:
        if m['id'] == 'beta':
            m['requires'] = ['no.such.contract']
    tm.write_yaml(tm.map_path(PROJECT), d)
    res = tm.verify(PROJECT)
    check('G6 requires', any('G6' in f for f in res['failures']), str(res['failures']))
    for m in d['modules']:
        if m['id'] == 'beta':
            m['requires'] = []
    tm.write_yaml(tm.map_path(PROJECT), d)

    print('[7] reassign moves the artifact and bumps revision')
    before = tm.load_map(PROJECT)['revision']
    rc = run(tm.cmd_plan, PROJECT, 'reassign',
             {'from': 'alpha', 'to': 'beta', 'into': None, 'module': None, 'new_id': None,
              'files': ['func.yaml'], 'notes': 'test'})
    check('reassign plan exit 0', rc == 0)
    plan = json.load(open(os.path.join(tm.artifacts_dir(PROJECT), '_migrations',
                                       str(before + 1), 'plan.json'), encoding='utf-8'))
    rc = tm.apply_plan(PROJECT, plan)
    check('reassign apply exit 0', rc == 0)
    check('artifact moved',
          os.path.exists(os.path.join(tm.module_dir(PROJECT, 'beta'), 'func.yaml'))
          and not os.path.exists(os.path.join(tm.module_dir(PROJECT, 'alpha'), 'func.yaml')))
    check('revision bumped', tm.load_map(PROJECT)['revision'] == before + 1)
    index = tm.read_yaml(tm.index_path(PROJECT), {'entries': []})
    entry = [e for e in index['entries'] if e['path'].endswith('beta/func.yaml')]
    check('index points at new module', bool(entry) and entry[0]['target_module'] == 'beta', str(entry))
    moved = tm.read_yaml(os.path.join(tm.module_dir(PROJECT, 'beta'), 'func.yaml'), {})
    check('moved candidate downgraded to draft', moved.get('status') == 'draft', str(moved))
    journal = json.load(open(os.path.join(tm.artifacts_dir(PROJECT), '_migrations',
                                          str(before + 1), 'journal.json'), encoding='utf-8'))
    check('journal records previous status',
          journal['moves'][0].get('previous_status') == 'candidate', str(journal['moves']))

    print('[8] failed apply rolls back')
    rev0 = tm.load_map(PROJECT)['revision']
    rc = run(tm.cmd_plan, PROJECT, 'reassign',
             {'from': 'beta', 'to': 'alpha', 'into': None, 'module': None, 'new_id': None,
              'files': ['func.yaml'], 'notes': ''})
    check('rollback plan exit 0', rc == 0)
    plan = json.load(open(os.path.join(tm.artifacts_dir(PROJECT), '_migrations',
                                       str(rev0 + 1), 'plan.json'), encoding='utf-8'))
    write(os.path.join(tm.module_dir(PROJECT, 'alpha'), 'func.yaml'), 'blocker\n')
    rc = tm.apply_plan(PROJECT, plan)
    check('apply returns 1', rc == 1)
    check('source restored',
          os.path.exists(os.path.join(tm.module_dir(PROJECT, 'beta'), 'func.yaml')))
    check('revision unchanged', tm.load_map(PROJECT)['revision'] == rev0)
    journal = json.load(open(os.path.join(tm.artifacts_dir(PROJECT), '_migrations',
                                          str(rev0 + 1), 'journal.json'), encoding='utf-8'))
    check('journal rolled-back', journal['status'] == 'rolled-back', str(journal))

    print('[9] repair rebuilds index/state')
    os.remove(os.path.join(tm.module_dir(PROJECT, 'alpha'), 'func.yaml'))
    rc = run(tm.cmd_repair, PROJECT)
    check('repair exit 0', rc == 0)
    res = tm.verify(PROJECT)
    check('verify after repair', not res['failures'], str(res['failures']))

    shutil.rmtree(ROOT, ignore_errors=True)
    print()
    if failures:
        print(f'FAILED: {len(failures)} check(s): ' + ', '.join(failures))
        return 1
    print('ALL TARGET-MODULE TESTS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
