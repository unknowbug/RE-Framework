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
 *   DSH_CHECKOUT     harness 源码 checkout（默认 D:\git\deepseek-harness）
 *   DSH_HARNESS_BASE 已安装 harness 所在目录（包名解析基准；默认 <DSH_CHECKOUT>\apps\cli）
 *   DSH_HOME         默认 %USERPROFILE%\.dsh
 *
 * 判据（镜像上游 `classifyRowSpecifier()` @ agent-presets/src/specifier.ts
 * + `packageInstalled()` @ agent-presets/src/discovery.ts）：
 *   - `cordis:` 前缀     → 内置行，Loader 自带，放行
 *   - 以 `.` 开头        → preset 自带文件，相对 composition 所在目录解析；
 *                          源码树跳过（install.ps1 拷贝后才成立），已安装副本要求文件存在
 *   - `file:` / 绝对路径 → 文件 URL，要求文件存在（Windows 盘符路径必须走 file URL）
 *   - 其余               → 包名，从 **已安装 harness 基准**（harness base）向上走
 *                          node_modules 查找（上游同款）；命中后再用 workspace manifest
 *                          校验子路径是否在 exports 内（比上游健康检查更严，因 exports
 *                          外的子路径在挂载时会真的 import 失败）
 *
 * 说明（上游 specifier.ts 的模块注释）：包名解析基准是 **harness base** 而非 preset 目录——
 *   本地 preset 位于用户 home 下，Node 向上 node_modules 查找永远走不到 harness 自身依赖。
 *   上游为此在 mount 的 import override 与 discovery 的健康检查里用**同一套分类**，
 *   否则会出现"健康检查说 OK、挂载时却 import 失败"。
 *   本机 harness base = `<checkout>\apps\cli`（其 node_modules 内有 @deepseek-ai/*）。
 *
 * 退出码：0 = 全部可解析；1 = 存在不可解析行；2 = 无法执行（缺 harness checkout / 解析器）
 *         2 在 selfcheck 中按 **FAIL** 处理（门禁不能执行 ≠ 通过；可用
 *         DSH_SKIP_PRESET_AUDIT=1 显式接受该缺口），不是静默通过。
 *
 * 注：composition 使用 `!!js` 标签，必须用 harness 的 entryListSchema 解析，
 *     普通 js-yaml 会报 unknown tag（属正常，非缺陷）。
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { join, dirname, resolve, isAbsolute } from 'node:path'
import { pathToFileURL, fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const REPO = resolve(HERE, '..', '..')

const HARNESS = process.env.DSH_CHECKOUT ?? 'D:\\git\\deepseek-harness'
/**
 * 已安装 harness 的位置：上游从 **这个基准** 解析裸包名（specifier.ts 模块注释），
 * 因为本地 preset 在用户 home 下，Node 向上查找走不到 harness 依赖。
 *
 * 自动探测而非只认一个硬编码路径：上游 health check 的 harnessBase 是调用方的
 * `ctx.baseUrl`（已安装 harness 所在处）。探测顺序（先命中者胜）：
 *   1. DSH_HARNESS_BASE 环境变量（显式覆盖）
 *   2. <checkout>/apps/cli        —— checkout 布局下的安装点
 *   3. 从 dsh 可执行文件位置向上走 —— 真实安装（npm -g）布局
 *   4. <checkout>/node_modules    —— 兜底
 * 探测失败（找不到任一含 @deepseek-ai 的 node_modules）→ exit 2（无法执行），
 * 而不是拿一个错基准跑出满屏假 BAD。
 */
function detectHarnessBase() {
  const explicit = process.env.DSH_HARNESS_BASE
  if (explicit) return explicit
  const marker = join('node_modules', '@deepseek-ai')
  const candidates = [join(HARNESS, 'apps', 'cli'), HARNESS]
  // 真实安装布局：dsh 可执行文件在 <prefix>/dsh.cmd，harness 在 <prefix>/node_modules/dsh
  try {
    const { execPath } = process
    if (execPath) candidates.push(dirname(execPath))
  } catch { /* 忽略 */ }
  for (const c of candidates) {
    if (existsSync(join(c, marker))) return c
  }
  // 兜底：<checkout>/node_modules 里有 @deepseek-ai 时，其父目录即基准
  if (existsSync(join(HARNESS, marker))) return HARNESS
  return undefined
}

const HARNESS_BASE = detectHarnessBase() ?? join(HARNESS, 'apps', 'cli')
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
/**
 * 基准健全性：解析基准必须真的能解析出 **本 preset 用到的** 包，否则包名行会全量误报
 * BROKEN（Anchorlaw 踩过的坑：传 checkout 根会全量误报——根 node_modules/@deepseek-ai
 * 只有 12 个 junction，而 apps/cli 才是完整安装面）。
 *
 * 判据：抽样本 composition 里若干包名，若基准下全部解析不到 → 基准选错，exit 2 声明
 * "无法执行"，而不是拿一个错基准刷出满屏假 BAD。
 */
function baseLooksUsable(base, names) {
  const probe = names
    .filter(n => !n.startsWith('cordis:') && !n.startsWith('.') && !n.startsWith('file:') && !isAbsolute(n))
    .slice(0, 12)
  if (probe.length === 0) return true
  return probe.some(n => packageInstalled(n, base))
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

// 基准健全性探测（须在行名可解析之后）：错基准 → exit 2，而不是满屏假 BAD。
{
  const target = files.find(f => existsSync(f.file))
  let probeNames = []
  if (target) {
    try {
      const rows = yaml.load(readFileSync(target.file, 'utf8'), { schema: include.entryListSchema })
      const walk = list => {
        for (const row of list) {
          if (typeof row?.name === 'string') probeNames.push(row.name)
          if (Array.isArray(row?.config)) walk(row.config)
        }
      }
      walk(rows)
    } catch { probeNames = [] }
  }
  if (probeNames.length > 0 && !baseLooksUsable(HARNESS_BASE, probeNames)) {
    console.log(`SKIP: harness base ${HARNESS_BASE} resolves none of this preset's packages — wrong base?`)
    console.log('      set DSH_HARNESS_BASE to the installed harness dir (checkout: <checkout>/apps/cli)')
    process.exit(2)
  }
}

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

/**
 * 上游 `classifyRowSpecifier()` 的镜像（agent-presets/src/specifier.ts）。
 *
 * Loader 把每行的 specifier 四分类，只有 `kind` 决定它相对哪个基准解析：
 * `cordis:` 内置不解析任何东西；以 `.` 开头 = preset 自带文件（相对 composition 目录）；
 * `file:` 与绝对路径 = 文件 URL（Windows 盘符路径必须走 file URL，Node ESM 拒绝裸盘符）；
 * 其余 = 包名，从 harness base 解析。
 */
function classifyRowSpecifier(name) {
  if (name.startsWith('cordis:')) return { kind: 'builtin', specifier: name }
  if (name.startsWith('.')) return { kind: 'preset', specifier: name }
  if (name.startsWith('file:')) return { kind: 'file', specifier: name }
  if (isAbsolute(name)) return { kind: 'file', specifier: pathToFileURL(name).href }
  return { kind: 'package', specifier: name }
}

/**
 * 上游 `packageInstalled()` 的镜像（agent-presets/src/discovery.ts:112）：
 * 从 base 向上走，找 `node_modules/<pkg>/package.json`。
 * 故意对"未导出子路径"宽容——与上游健康检查一致；更严的 exports 探针在下面单独施加。
 */
function packageInstalled(name, base) {
  const pkg = name.split('/').slice(0, name.startsWith('@') ? 2 : 1).join('/')
  let dir = base
  for (;;) {
    if (existsSync(join(dir, 'node_modules', pkg, 'package.json'))) return true
    const parent = dirname(dir)
    if (parent === dir) return false
    dir = parent
  }
}

/** 单个 name 的解析结论 */
function classify(name, presetDir, sourceTree) {
  const row = classifyRowSpecifier(name)
  if (row.kind === 'builtin') return { ok: true, why: 'cordis builtin' }
  if (row.kind === 'preset') {
    // preset 自带文件随 preset 一起走：install.ps1 把 preset/ 拷进
    // ~/.dsh/.agent-presets/<id>/ 后，相对路径在 preset 目录内解析。源码树尚未拷贝。
    if (sourceTree) return { ok: true, why: 'preset-relative path (source tree — travels on install)' }
    const target = resolve(presetDir, row.specifier)
    return existsSync(target) ? { ok: true, why: 'preset-relative file' } : { ok: false, why: `preset file missing: ${target}` }
  }
  if (row.kind === 'file') {
    let target
    try {
      target = fileURLToPath(new URL(row.specifier))
    } catch (e) {
      return { ok: false, why: `malformed file row: ${e.message}` }
    }
    return existsSync(target) ? { ok: true, why: 'file row' } : { ok: false, why: `file row missing: ${target}` }
  }
  // 包名行 —— 上游判据是从 harness base 向上走 node_modules。
  // 在那里找不到的包，挂载时必然 import 失败。
  if (!packageInstalled(row.specifier, HARNESS_BASE)) {
    return { ok: false, why: `package not installed above harness base ${HARNESS_BASE} (renamed / removed upstream)` }
  }
  // 比上游健康检查更严（上游接受未导出子路径）：exports 之外的子路径在挂载时
  // 仍会 import 失败，故当 workspace manifest 可知时一并报出。
  const isScoped = row.specifier.startsWith('@')
  const seg = row.specifier.split('/')
  const base = isScoped ? seg.slice(0, 2).join('/') : seg[0]
  const sub = isScoped ? seg.slice(2).join('/') : seg.slice(1).join('/')
  const manifest = packages.get(base)
  if (sub !== '' && manifest && (!manifest.exports || !Object.keys(manifest.exports).includes(`./${sub}`))) {
    const keys = manifest.exports ? Object.keys(manifest.exports).join(', ') : 'none'
    return { ok: false, why: `subpath ./${sub} not in ${base} exports (have: ${keys})` }
  }
  return { ok: true, why: `package (harness base: ${HARNESS_BASE})` }
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
