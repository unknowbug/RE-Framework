/**
 * audit_preset_rows.mjs — preset 行解析性门禁（fail-closed）
 *
 * 用途：校验 re-framework agent preset composition 里每一行的 `name:` 能否在当前
 *       harness 版本中解析。上游改名/移除插件包时本脚本非零退出，避免等用户 resume
 *       会话时才看到 `failed to mount`（2026-09-09 上游漂移事故：
 *       @deepseek-ai/dsh-workflow-worker-thread 改名 @deepseek-ai/dsh-workflow-ptc，
 *       见 .investigations/dsh-upstream-drift-20260909/报告.md）。
 *
 * 用法：
 *   node dsh/tests/audit_preset_rows.mjs                          # 默认：源码 composition + 已安装副本（若存在）
 *   node dsh/tests/audit_preset_rows.mjs <composition.yml ...>    # 指定源码 composition（跳过 ./ 本地行）
 *   node dsh/tests/audit_preset_rows.mjs --installed <preset ...> # 校验 ~/.dsh/.agent-presets/<名>/agent.cordis.yml
 *
 * 环境：
 *   DSH_CHECKOUT   harness 源码 checkout（默认 D:\git\deepseek-harness）
 *   DSH_HOME       默认 %USERPROFILE%\.dsh
 *
 * 判据：
 *   - `cordis:` 前缀    → 内置行，放行
 *   - `./` / `../` 开头 → 源码树内该相对路径要 install 后才成立；源码 composition 跳过，
 *                         已安装副本则要求本地文件存在
 *   - 其余              → 包名必须存在于 harness workspace 包集合；带子路径者子路径须在其 exports 内
 *
 * 退出码：0 = 全部可解析；1 = 存在不可解析行；2 = 无法执行（缺 harness checkout / 解析器）
 *         2 在 selfcheck 中按 **FAIL** 处理（门禁不能执行 ≠ 通过；可用
 *         DSH_SKIP_PRESET_AUDIT=1 显式接受该缺口），不是静默通过。
 *
 * 注：composition 使用 `!!js` 标签，必须用 harness 的 entryListSchema 解析，
 *     普通 js-yaml 会报 unknown tag（属正常，非缺陷）。
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { join, dirname, resolve } from 'node:path'
import { pathToFileURL, fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const REPO = resolve(HERE, '..', '..')

const HARNESS = process.env.DSH_CHECKOUT ?? 'D:\\git\\deepseek-harness'
const HOME = process.env.DSH_HOME ?? join(process.env.USERPROFILE ?? '', '.dsh')

const PRESET_NAME = 're-framework'

const args = process.argv.slice(2)
const installedMode = args.includes('--installed')
const positional = args.filter(a => !a.startsWith('--'))

/** 目标文件：[{ file, sourceTree }] */
let files
if (installedMode) {
  files = positional.map(name => ({
    file: join(HOME, '.agent-presets', name, 'agent.cordis.yml'),
    sourceTree: false,
  }))
} else if (positional.length > 0) {
  files = positional.map(f => ({ file: f, sourceTree: true }))
} else {
  // selfcheck 默认：源码 composition（跳过 ./ 本地行）+ 已安装副本（若存在）
  files = [{ file: join(REPO, 'dsh', 'preset', 'agent.cordis.yml'), sourceTree: true }]
  const installed = join(HOME, '.agent-presets', PRESET_NAME, 'agent.cordis.yml')
  if (existsSync(installed)) files.push({ file: installed, sourceTree: false })
}

// ── 解析器（harness 的 entryListSchema + 其 js-yaml）；缺失则跳过并显式说明 ──
const schemaEntry = join(HARNESS, 'vendor', 'include', 'lib', 'index.js')
const yamlCandidates = [
  join(HARNESS, 'node_modules', 'js-yaml', 'dist', 'js-yaml.mjs'),
  // pnpm store 兜底：版本号会随上游升级变动，故动态发现而非写死
  ...(() => {
    const pnpm = join(HARNESS, 'node_modules', '.pnpm')
    if (!existsSync(pnpm)) return []
    return readdirSync(pnpm, { withFileTypes: true })
      .filter(e => e.isDirectory() && e.name.startsWith('js-yaml@'))
      .map(e => join(pnpm, e.name, 'node_modules', 'js-yaml', 'dist', 'js-yaml.mjs'))
      .filter(existsSync)
  })(),
]

if (!existsSync(schemaEntry)) {
  console.log(`SKIP: harness checkout not found at ${HARNESS} (set DSH_CHECKOUT) — cannot resolve packages`)
  process.exit(2)
}
const yamlPath = yamlCandidates.find(existsSync)
if (!yamlPath) {
  console.log(`SKIP: js-yaml not found under ${HARNESS} — cannot parse composition`)
  process.exit(2)
}

const include = await import(pathToFileURL(schemaEntry).href)
const yaml = await import(pathToFileURL(yamlPath).href)

/** 收集 harness workspace 里所有包：name -> { dir, exports } */
function collectPackages() {
  const map = new Map()
  const roots = []
  const pkgs = join(HARNESS, 'packages')
  if (existsSync(pkgs)) {
    for (const g of readdirSync(pkgs, { withFileTypes: true })) {
      if (g.isDirectory()) roots.push(join(pkgs, g.name))
    }
  }
  roots.push(join(HARNESS, 'vendor'), join(HARNESS, 'apps'))
  for (const root of roots) {
    if (!existsSync(root)) continue
    for (const entry of readdirSync(root, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue
      const pj = join(root, entry.name, 'package.json')
      if (!existsSync(pj)) continue
      try {
        const manifest = JSON.parse(readFileSync(pj, 'utf8'))
        if (typeof manifest.name === 'string') {
          map.set(manifest.name, { dir: join(root, entry.name), exports: manifest.exports })
        }
      } catch { /* 坏 manifest 忽略 */ }
    }
  }
  return map
}

const packages = collectPackages()

/** composition 里全部行的 name（含嵌套 group） */
function rowNames(file) {
  const rows = yaml.load(readFileSync(file, 'utf8'), { schema: include.entryListSchema })
  const out = []
  const walk = list => {
    for (const row of list) {
      if (typeof row?.name === 'string') out.push(row.name)
      if (Array.isArray(row?.config)) walk(row.config)
    }
  }
  walk(rows)
  return out
}

/** 单个 name 的解析结论 */
function classify(name, presetDir, sourceTree) {
  if (name.startsWith('cordis:')) return { ok: true, why: 'cordis builtin' }
  if (name.startsWith('./') || name.startsWith('../')) {
    if (sourceTree) return { ok: true, why: 'source-tree relative path (skipped)' }
    const target = resolve(presetDir, name)
    return existsSync(target) ? { ok: true, why: 'local file' } : { ok: false, why: `local file missing: ${target}` }
  }
  const isScoped = name.startsWith('@')
  const seg = name.split('/')
  const base = isScoped ? seg.slice(0, 2).join('/') : seg[0]
  const sub = isScoped ? seg.slice(2).join('/') : seg.slice(1).join('/')
  const found = packages.get(base)
  if (!found) return { ok: false, why: 'package not in harness workspace (renamed / removed upstream)' }
  if (sub !== '') {
    const keys = typeof found.exports === 'object' && found.exports !== null ? Object.keys(found.exports) : []
    if (!keys.includes(`./${sub}`)) {
      return { ok: false, why: `subpath ./${sub} not in exports (have: ${keys.join(', ') || 'none'})` }
    }
  }
  return { ok: true, why: found.dir.replace(HARNESS, '<harness>') }
}

let bad = 0
for (const { file, sourceTree } of files) {
  console.log(`\n== ${file}${sourceTree ? '  (source tree)' : '  (installed)'}`)
  if (!existsSync(file)) {
    // 显式传入的目标文件不存在 = 调用错误，不是"跳过"（否则拼错路径会假绿）
    if (positional.length > 0 || installedMode) {
      console.log('   NOT FOUND: target file does not exist (check the path / preset name)')
      bad++
    } else {
      console.log('   (optional installed copy not present — skipped)')
    }
    continue
  }
  let names
  try {
    names = [...new Set(rowNames(file))]
  } catch (e) {
    console.log(`   PARSE FAIL: ${e.message}`)
    bad++
    continue
  }
  let fileBad = 0
  for (const name of names.sort()) {
    const r = classify(name, dirname(file), sourceTree)
    if (!r.ok) { fileBad++; bad++ }
    console.log(`   ${r.ok ? 'OK  ' : 'BAD '} ${name}${r.ok ? '' : `  <- ${r.why}`}`)
  }
  console.log(`   -> ${names.length} reference(s), ${fileBad} unresolvable`)
}

console.log(bad === 0 ? '\nAll preset rows resolvable ✅' : `\n${bad} unresolvable preset row(s) ❌`)
process.exit(bad === 0 ? 0 : 1)
