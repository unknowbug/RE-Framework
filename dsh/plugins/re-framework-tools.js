// re-framework-tools — RE-Framework methodology tools for DSH.
//
// ESM Cordis plugin file, import-free on purpose: the preset loader resolves
// entry modules through Node's ESM resolver from the preset's own directory,
// which cannot reach the harness's node_modules.
//
// Registers model tools into the session's tool registry. `config.tools`
// selects the subset (names below); absent/empty = all three. Since the
// Reasonix host format was archived (2026-08-21), the maintenance tools that
// wrapped Reasonix scripts (ref_manifest_validate → validate_manifest.py,
// ref_install → install.py) were retired with it; the remaining tools operate
// on session-workspace data + the retained scripts/merge_index.py, so they
// are usable from any project session without sandbox issues.
//
// Tool inventory:
//   ref_status             — framework health: workspace/repo/python/skills/modules
//   ref_merge_index        — merge parallel-worker index fragments (scripts/merge_index.py, core.artifact §5.1)
//   ref_init               — create the project skeleton (.artifacts/.investigations/knowledge)
//
// Contract guard (spec §5.7): deny-only preconditions on write/edit, in the
// style of DSH's fs-observation-policy — the action fails before it happens and
// the one-line message names the recovery. Rules R1 (undeclared module),
// R3 (candidate without a judge review at this revision), R5 (knowledge entry
// without reviewable front-matter). REF_GUARD=off is the audited self-rescue
// switch; every denial and bypass is appended to .artifacts/_audit/guard.jsonl.
//
// Maintained by: DSH agent (RE-Framework maintainer). Source of truth:
// this repository's dsh/ subtree (cordis.patch.yml + plugins/ + skills/), per dsh/AGENTS.md.

export const name = 're-framework-tools'
export const inject = ['tools']

export function apply(ctx, config = {}) {
  // Optional capabilities, read with ctx.get and handled when absent.
  const subprocess = ctx.get('subprocess')
  const skills = ctx.get('skills')
  const fsService = ctx.get('fs')
  const sandboxPolicy = ctx.get('sandboxPolicy')
  if (subprocess === undefined) return

  const ALL_TOOLS = ['status', 'merge_index', 'init']
  const enabled = new Set(
    Array.isArray(config.tools) && config.tools.length ? config.tools : ALL_TOOLS,
  )

  const REF_SKILLS = [
    'core-plan', 'core-artifact', 'core-knowledge', 'core-version', 'core-fanout',
    'core-worker', 'core-judge',
    're-lift', 're-classify', 're-trace', 're-scout',
    'recode-deobfuscate', 'recode-classmap', 'recode-behavior', 'recode-scout',
    'swe-guide', 'ref-maintain',
  ]

  let pythonPathPromise
  function pythonPath() {
    if (!pythonPathPromise) pythonPathPromise = subprocess.resolveExecutable('python')
    return pythonPathPromise
  }

  function readAll(reader) {
    if (!reader) return ''
    let text = ''
    let offset = 0
    for (;;) {
      const chunk = reader.readFrom(offset)
      text += chunk.text
      if (chunk.nextOffset <= offset) break
      offset = chunk.nextOffset
    }
    return text
  }

  async function runPython(args, cwd) {
    const py = await pythonPath()
    const handle = subprocess.spawn({
      argv: [py].concat(args),
      cwd,
      stdio: {
        stdin: 'ignore',
        stdout: { maxBytes: 256 * 1024, spill: { maxBytes: 2 * 1024 * 1024 } },
        stderr: { maxBytes: 64 * 1024, spill: { maxBytes: 512 * 1024 } },
      },
      graceMs: 2000,
    })
    const outcome = await handle.done
    return {
      exitCode: outcome.exitCode,
      stdout: readAll(handle.collected.stdout),
      stderr: readAll(handle.collected.stderr),
    }
  }

  // The calling agent's session workspace, then the sandbox root, then '.'.
  function sessionCwd(exec) {
    try {
      const agent = exec && exec.agent
      if (agent && agent.session && agent.session.header && agent.session.header.cwd) {
        return agent.session.header.cwd
      }
    } catch (error) {
      // fall through
    }
    if (sandboxPolicy && sandboxPolicy.workspaceRoot) return sandboxPolicy.workspaceRoot
    return '.'
  }

  // Locate the RE-Framework repository: walk up from cwd until a directory
  // holds AGENTS.md + scripts/validate_manifest.py (the framework markers).
  async function resolveRepo(cwd) {
    if (fsService === undefined) return cwd
    let dir = cwd
    for (let i = 0; i < 8; i++) {
      try {
        const agents = await fsService.stat(await fsService.resolve('AGENTS.md', { cwd: dir }))
        const validator = await fsService.stat(
          await fsService.resolve('scripts/validate_manifest.py', { cwd: dir }))
        if (agents !== undefined && validator !== undefined) return dir
      } catch (error) {
        // keep walking
      }
      const parent = pathParent(dir)
      if (!parent || parent === dir) break
      dir = parent
    }
    return cwd
  }

  function pathParent(p) {
    const norm = String(p).replace(/[\\/]+$/, '')
    const idx = Math.max(norm.lastIndexOf('/'), norm.lastIndexOf('\\'))
    if (idx <= 0) return null
    return norm.slice(0, idx)
  }

  async function absPath(p, cwd) {
    const raw = String(p)
    if (fsService !== undefined) {
      try {
        const target = await fsService.resolve(raw, { cwd })
        return fsService.processPath(target)
      } catch (error) {
        // fall through to raw path
      }
    }
    return raw
  }

  function renderText(v) {
    return [{ type: 'text', text: String(v) }]
  }

  function register(definition) {
    ctx.effect(() => ctx.tools.register(definition))
  }

  // ── ref_status ────────────────────────────────────────────────────────────
  if (enabled.has('status')) register({
    name: 'ref_status',
    description: 'Report the RE-Framework toolchain status: session workspace, resolved framework repository, python availability, installed framework modules, and the ref-* skills visible to the current session.',
    parameters: {
      type: 'object',
      properties: {},
    },
    output: { schema: { type: 'string' }, render(_args, v) { return renderText(v) } },
    async execute(_args, exec) {
      const lines = []
      const cwd = sessionCwd(exec)
      const repo = await resolveRepo(cwd)
      lines.push(`[session workspace: ${cwd}]`)
      lines.push(`[framework repo: ${repo}]${repo === cwd ? ' (fallback: no AGENTS.md+scripts marker above cwd)' : ''}`)
      try {
        const r = await runPython(['-c', 'import sys; print(sys.version.split()[0])'], cwd)
        lines.push(r.stdout.trim() ? `[python: ${r.stdout.trim()}]` : '[python: no version output]')
        if (r.stderr && r.stderr.trim()) lines.push('[stderr] ' + r.stderr.trim())
        lines.push(`[exit code: ${r.exitCode}]`)
      } catch (error) {
        lines.push('[python check failed: ' + error.message + ']')
      }
      try {
        const fs = await fsService?.listDir(await fsService.resolve('skills/modules', { cwd: repo }))
        const modules = (fs || []).map((e) => e.name.replace(/\.yaml$/, '')).filter((n) => n)
        lines.push(`[modules: ${modules.length ? modules.join(', ') : 'none found'}]`)
      } catch (error) {
        lines.push('[modules: not resolvable from repo]')
      }
      if (skills !== undefined) {
        try {
          const list = await skills.list({ cwd, scope: exec && exec.agent })
          const found = list.filter((s) => typeof s.name === 'string' && REF_SKILLS.includes(s.name))
          lines.push('')
          lines.push(`ref skills discovered: ${found.length}/${REF_SKILLS.length}`)
          for (const s of found) lines.push(`  - ${s.name}: ${s.description}`)
        } catch (error) {
          lines.push('skills.list failed: ' + error.message)
        }
      }
      return lines.join('\n')
    },
  })

  // ── ref_merge_index ───────────────────────────────────────────────────────
  if (enabled.has('merge_index')) register({
    name: 'ref_merge_index',
    description: 'Merge .artifacts/**/index-entry.yaml fragments into the root .artifacts/index.yaml via scripts/merge_index.py (core.artifact §5.1). Conflicts are reported but never silently overwritten.',
    parameters: {
      type: 'object',
      properties: {
        project: { type: 'string', description: 'Project directory containing .artifacts/.' },
        dryRun: { type: 'boolean', default: false, description: 'Report only, do not write.' },
      },
      required: ['project'],
    },
    output: { schema: { type: 'string' }, render(_args, v) { return renderText(v) } },
    async execute(args, exec) {
      const cwd = sessionCwd(exec)
      const repo = await resolveRepo(cwd)
      const project = await absPath(args.project, cwd)
      const argv = [await absPath('scripts/merge_index.py', repo), project]
      if (args.dryRun) argv.push('--dry-run')
      const r = await runPython(argv, cwd)
      let out = r.stdout
      if (r.stderr && r.stderr.trim()) out += '\n[stderr]\n' + r.stderr
      out += `\n[exit code: ${r.exitCode}]`
      return out
    },
  })

  // ── ref_init ──────────────────────────────────────────────────────────────
  if (enabled.has('init')) register({
    name: 'ref_init',
    description: 'Create the RE-Framework project skeleton in a directory: .artifacts/index.yaml (empty schema), .investigations/, knowledge/INDEX.md + builtin/ + discovered/errors/. Existing files are never overwritten.',
    parameters: {
      type: 'object',
      properties: {
        project: { type: 'string', description: 'Project directory to initialize. Defaults to the session workspace.' },
      },
    },
    output: { schema: { type: 'string' }, render(_args, v) { return renderText(v) } },
    async execute(args, exec) {
      const cwd = sessionCwd(exec)
      const project = args.project ? await absPath(args.project, cwd) : cwd
      const code = [
        'import os, sys',
        'root = os.path.abspath(sys.argv[1])',
        "os.makedirs(os.path.join(root, '.artifacts'), exist_ok=True)",
        "os.makedirs(os.path.join(root, '.investigations'), exist_ok=True)",
        "os.makedirs(os.path.join(root, 'knowledge', 'builtin'), exist_ok=True)",
        "os.makedirs(os.path.join(root, 'knowledge', 'discovered', 'errors'), exist_ok=True)",
        "idx = os.path.join(root, '.artifacts', 'index.yaml')",
        "if not os.path.exists(idx):",
        "    with open(idx, 'w', encoding='utf-8') as f:",
        "        f.write('schema_version: 1\\nproject: %s\\nmodule: core\\nentries: []\\n' % os.path.basename(root))",
        "kid = os.path.join(root, 'knowledge', 'INDEX.md')",
        "if not os.path.exists(kid):",
        "    with open(kid, 'w', encoding='utf-8') as f:",
        "        f.write('# Knowledge INDEX\\n\\n## 错误账本（最高优先级）\\n\\n（暂无条目——发现错误立即记录到 discovered/errors/）\\n\\n## builtin\\n\\n## discovered\\n')",
        "print('skeleton created at', root)",
      ].join('\n')
      const r = await runPython(['-c', code, project], cwd)
      let out = r.stdout
      if (r.stderr && r.stderr.trim()) out += '\n[stderr]\n' + r.stderr
      out += `\n[exit code: ${r.exitCode}]`
      return out
    },
  })

  // ── contract guard (spec §5.7) ─────────────────────────────────────────────
  //
  // Deny-only preconditions, mirroring DSH's fs-observation-policy pattern: the
  // action fails *before* it happens and the message names the next step. State
  // is read from .artifacts/target-modules.state.json on every call (disk, never
  // cached), so a resumed session sees the same map. REF_GUARD=off is the
  // audited self-rescue switch; damage from a bypass is still caught by the
  // target_modules gates.
  //   R1 REF_MODULE_UNDECLARED — artifact write into an undeclared module
  //   R3 REF_REVIEW_MISSING    — candidate/confirmed without a review at this revision
  //   R5 REF_KB_FRONTMATTER    — knowledge entry missing signature/verdict/lesson/status
  const guardFs = (() => {
    try { return process.getBuiltinModule('node:fs') } catch (error) { return undefined }
  })()
  const guardPath = (() => {
    try { return process.getBuiltinModule('node:path') } catch (error) { return undefined }
  })()
  const GUARDED_TOOLS = new Set(['write', 'edit'])
  const bypassedAgents = new WeakSet()
  let bypassedAnonymous = false

  function guardAudit(cwd, entry) {
    if (guardFs === undefined || guardPath === undefined || !cwd) return
    try {
      const dir = guardPath.join(cwd, '.artifacts', '_audit')
      guardFs.mkdirSync(dir, { recursive: true })
      guardFs.appendFileSync(guardPath.join(dir, 'guard.jsonl'),
        JSON.stringify(Object.assign({ at: new Date().toISOString() }, entry)) + '\n', 'utf8')
    } catch (error) {
      // Auditing must never block the turn.
    }
  }

  function guardState(cwd) {
    if (guardFs === undefined || guardPath === undefined || !cwd) return undefined
    try {
      const file = guardPath.join(cwd, '.artifacts', 'target-modules.state.json')
      if (!guardFs.existsSync(file)) return undefined
      const state = JSON.parse(guardFs.readFileSync(file, 'utf8'))
      return state && Array.isArray(state.modules) ? state : undefined
    } catch (error) {
      return undefined
    }
  }

  function relativeTo(cwd, filePath) {
    if (!cwd || guardPath === undefined) return String(filePath).replace(/\\/g, '/')
    return guardPath.relative(cwd, guardPath.resolve(cwd, String(filePath))).replace(/\\/g, '/')
  }

  function contractGuard(exec) {
    try {
      if (!GUARDED_TOOLS.has(exec.name)) return undefined
      const args = exec.arguments || {}
      const filePath = args.file_path
      if (typeof filePath !== 'string' || filePath === '') return undefined
      const cwd = sessionCwd(exec)
      const state = guardState(cwd)
      if (state === undefined) return undefined
      const relative = relativeTo(cwd, filePath)

      if (process.env.REF_GUARD === 'off') {
        const key = exec.agent
        if (key !== undefined) {
          if (!bypassedAgents.has(key)) {
            bypassedAgents.add(key)
            guardAudit(cwd, { event: 'bypass', reason: 'REF_GUARD=off' })
          }
        } else if (!bypassedAnonymous) {
          bypassedAnonymous = true
          guardAudit(cwd, { event: 'bypass', reason: 'REF_GUARD=off' })
        }
        return undefined
      }

      const match = /(?:^|\/)\.artifacts\/modules\/([^/]+)\//.exec(relative)
      const moduleId = match ? match[1] : undefined
      const known = new Set(state.modules.map((entry) => entry && entry.id))
      const content = typeof args.content === 'string' ? args.content
        : (typeof args.new_string === 'string' ? args.new_string : '')

      // R1 - an artifact must land in a declared module (or in unassigned/).
      if (moduleId !== undefined && !known.has(moduleId)) {
        guardAudit(cwd, { event: 'deny', code: 'REF_MODULE_UNDECLARED', tool: exec.name, path: relative })
        return 'REF_MODULE_UNDECLARED: module "' + moduleId + '" is not declared'
          + ' - run ref_modules derive (or write under .artifacts/unassigned/), then retry'
      }

      // R3 - candidate/confirmed needs a judge review recorded for this revision.
      const isYaml = relative.endsWith('.yaml') || relative.endsWith('.yml')
      const isReviewFile = relative.includes('/reviews/')
      if (moduleId !== undefined && isYaml && !isReviewFile
        && /status:\s*(candidate|confirmed)/.test(content)) {
        const module = state.modules.find((entry) => entry && entry.id === moduleId)
        const reviews = (module && module.reviews) || []
        const revision = String(state.revision)
        if (!reviews.includes(revision)) {
          guardAudit(cwd, { event: 'deny', code: 'REF_REVIEW_MISSING', tool: exec.name,
            path: relative, revision: state.revision })
          return 'REF_REVIEW_MISSING: module "' + moduleId + '" has no judge review at revision '
            + revision + ' - invoke core-judge (scope module:' + moduleId + '), then retry'
        }
      }

      // R5 - knowledge entries must stay reviewable at the index level.
      if (exec.name === 'write' && relative.startsWith('knowledge/discovered/')
        && relative.endsWith('.md')) {
        const missing = ['signature', 'verdict', 'lesson', 'status']
          .filter((key) => !new RegExp('^' + key + ':', 'm').test(content))
        if (missing.length > 0) {
          guardAudit(cwd, { event: 'deny', code: 'REF_KB_FRONTMATTER', tool: exec.name, path: relative })
          return 'REF_KB_FRONTMATTER: knowledge entry missing front-matter: ' + missing.join(', ')
            + ' - add them, then retry'
        }
      }
      return undefined
    } catch (error) {
      return undefined
    }
  }

  if (typeof ctx.tools.guard === 'function') {
    ctx.effect(() => ctx.tools.guard(contractGuard))
  }
}
