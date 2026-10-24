/**
 * Contract-guard tests for dsh/plugins/re-framework-tools.js (spec §5.7).
 *
 * Exercises the deny-only preconditions without a live harness: the plugin is
 * mounted on a fake Cordis context, the registered guard is captured, and each
 * rule is evaluated against a temporary project fixture.
 *
 * Usage: node dsh/tests/test_contract_guard.mjs
 */
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { tmpdir } from 'node:os'
import { fileURLToPath, pathToFileURL } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const REPO = join(HERE, '..', '..')
const plugin = await import(pathToFileURL(join(REPO, 'dsh', 'plugins', 're-framework-tools.js')).href)

const failures = []
function check(name, cond, detail = '') {
  if (cond) console.log(`  OK   ${name}`)
  else { console.log(`  FAIL ${name} ${detail}`); failures.push(name) }
}

function mount() {
  let guard
  const ctx = {
    get(name) { return name === 'subprocess' ? {} : undefined },
    effect(fn) { const d = fn(); return typeof d === 'function' ? d : () => {} },
    tools: {
      register() { return () => {} },
      guard(fn) { guard = fn; return () => {} },
    },
  }
  plugin.apply(ctx, {})
  return { guard }
}

function project({ revision = 3, modules = [{ id: 'alpha', reviews: [] }], unassigned = 0 } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'ref-guard-'))
  const art = join(root, '.artifacts')
  mkdirSync(art, { recursive: true })
  writeFileSync(join(art, 'target-modules.state.json'), JSON.stringify({
    schema_version: 1, revision, modules, unassigned: { count: unassigned },
  }))
  return root
}

function exec(root, name, args) {
  return {
    name,
    arguments: args,
    agent: { session: { header: { cwd: root } } },
  }
}

const { guard } = mount()
check('guard registered', typeof guard === 'function')

// Inert without a map (no map = no enforcement).
{
  const root = mkdtempSync(join(tmpdir(), 'ref-guard-empty-'))
  const reason = guard(exec(root, 'write', {
    file_path: join(root, '.artifacts', 'modules', 'ghost', 'a.yaml'), content: 'x',
  }))
  check('inert without state file', reason === undefined, String(reason))
  rmSync(root, { recursive: true, force: true })
}

// R1: undeclared module.
{
  const root = project()
  const reason = guard(exec(root, 'write', {
    file_path: join(root, '.artifacts', 'modules', 'beta', 'a.yaml'),
    content: 'name: A\nstatus: draft\n',
  }))
  check('R1 denies undeclared module', typeof reason === 'string' && reason.startsWith('REF_MODULE_UNDECLARED:'), String(reason))
  check('R1 message names recovery', typeof reason === 'string' && reason.includes('ref_modules derive'), String(reason))
  const ok = guard(exec(root, 'write', {
    file_path: join(root, '.artifacts', 'modules', 'alpha', 'a.yaml'),
    content: 'name: A\nstatus: draft\n',
  }))
  check('R1 allows declared module', ok === undefined, String(ok))
  rmSync(root, { recursive: true, force: true })
}

// R3: candidate/confirmed needs a review at the current revision.
{
  const root = project()
  const deny = guard(exec(root, 'write', {
    file_path: join(root, '.artifacts', 'modules', 'alpha', 'a.yaml'),
    content: 'name: A\nstatus: candidate\n',
  }))
  check('R3 denies candidate without review', typeof deny === 'string' && deny.startsWith('REF_REVIEW_MISSING:'), String(deny))
  check('R3 message names judge', typeof deny === 'string' && deny.includes('core-judge'), String(deny))
  const review = guard(exec(root, 'write', {
    file_path: join(root, '.artifacts', 'modules', 'alpha', 'reviews', '3.md'),
    content: 'status: candidate reviewed\n',
  }))
  check('R3 allows review record writes', review === undefined, String(review))
  rmSync(root, { recursive: true, force: true })

  const reviewed = project({ modules: [{ id: 'alpha', reviews: ['3'] }] })
  const allow = guard(exec(reviewed, 'edit', {
    file_path: join(reviewed, '.artifacts', 'modules', 'alpha', 'a.yaml'),
    new_string: 'status: candidate\n',
  }))
  check('R3 allows reviewed candidate', allow === undefined, String(allow))
  rmSync(reviewed, { recursive: true, force: true })
}

// R5: knowledge front-matter.
{
  const root = project()
  const deny = guard(exec(root, 'write', {
    file_path: join(root, 'knowledge', 'discovered', 'note.md'),
    content: '# note\n\nno front matter\n',
  }))
  check('R5 denies missing front-matter', typeof deny === 'string' && deny.startsWith('REF_KB_FRONTMATTER:'), String(deny))
  check('R5 lists fields', typeof deny === 'string' && deny.includes('signature'), String(deny))
  const allow = guard(exec(root, 'write', {
    file_path: join(root, 'knowledge', 'discovered', 'note.md'),
    content: '---\nsignature: s\nverdict: v\nlesson: l\nstatus: draft\n---\nbody\n',
  }))
  check('R5 allows complete front-matter', allow === undefined, String(allow))
  rmSync(root, { recursive: true, force: true })
}

// Self-rescue: REF_GUARD=off allows and audits.
{
  const root = project()
  process.env.REF_GUARD = 'off'
  const reason = guard(exec(root, 'write', {
    file_path: join(root, '.artifacts', 'modules', 'ghost', 'a.yaml'), content: 'x',
  }))
  delete process.env.REF_GUARD
  check('bypass allows', reason === undefined, String(reason))
  const audit = join(root, '.artifacts', '_audit', 'guard.jsonl')
  check('bypass audited', existsSync(audit) && readFileSync(audit, 'utf8').includes('"bypass"'), audit)
  rmSync(root, { recursive: true, force: true })
}

// Audit records denials too.
{
  const root = project()
  guard(exec(root, 'write', {
    file_path: join(root, '.artifacts', 'modules', 'ghost', 'a.yaml'), content: 'x',
  }))
  const audit = join(root, '.artifacts', '_audit', 'guard.jsonl')
  check('denial audited', existsSync(audit) && readFileSync(audit, 'utf8').includes('REF_MODULE_UNDECLARED'), audit)
  rmSync(root, { recursive: true, force: true })
}

console.log()
if (failures.length) {
  console.log(`FAILED: ${failures.length} check(s): ${failures.join(', ')}`)
  process.exit(1)
}
console.log('ALL CONTRACT-GUARD TESTS PASSED')
