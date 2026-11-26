/**
 * audit_prompt_variables.mjs — preset 模板变量门禁（fail-closed）
 *
 * 用途：校验本 bundle 的 preset 载体（`dsh/cordis.patch.yml`）里每一个
 *       `{{变量}}` 引用都对应 harness **当前注册**的提示词变量。
 *       上游删除/改名提示词变量时本脚本非零退出，避免等用户开新会话时才看到
 *       `unknown prompt variable "{{cwd}}" in section "deployment:persona-prefix"`。
 *
 * 事故（2026-10-10）：DSH 0.2.x 按升级指南
 *   `docs/upgrade-guide/v0.2.1-alpha.1/working-directory/guide.md` §Migration 1 移除
 *   了循环内建的 `cwd` 提示词变量（上游 79bd3d8da7 删掉
 *   `packages/core/agent-loop/src/index.ts` 的 `variable('cwd', …)` 行；工作目录改由
 *   `dsh-working-directory` 的 `working-directory:current` 运行时上下文提供）。
 *   本 bundle 的 persona prefix 仍写 `Your working directory is {{cwd}}.`，
 *   而 persona 模板是**渲染期严格解析**的——于是 re-framework preset 的会话在组装
 *   （模型请求之前）直接抛错。第 5 段「preset 行解析门禁」看不见这类故障：
 *   行能解析、包能挂载，**模板变量却已死**——又一次「自检全绿、开新会话即失败」。
 *
 * 判据（镜像上游 `interpolate()` @ core/system-prompt/src/index.ts:336-373）：
 *   - 只有完整的 `{{name}}` 组才是引用；`{{` 后无 `}}` 属字面散文，放行
 *   - `{{` 后有 `}}` 但不是完整简单组 → 上游报 malformed，本门禁同样报 FAIL
 *   - 名字必须匹配 `/^[a-z][a-z0-9_]*$/`，否则上游报 malformed
 *   - 名字未注册 → 上游报 `unknown prompt variable`，本门禁 FAIL
 *   （已注册但该次组装无值 = 上游的另一条错误 `has no value for this assembly`，
 *    取决于运行时状态，静态门禁无法判定，故不在本门禁范围。）
 *
 * 注册集合来源：扫描 harness 源码/编译产物里的 `systemPrompt.variable('<name>', …)`
 *   注册点（默认 `<DSH_CHECKOUT>/packages/<group>/<pkg>/{src,lib}`，跳过 tests 目录
 *   与 spec/test 文件，否则测试里注册的假变量会污染白名单、门禁反而变松）。
 *   扫不到任何名字 → exit 2（**不能执行 ≠ 通过**），由 selfcheck 按 FAIL 处理。
 *
 * 用法：
 *   node dsh/tests/audit_prompt_variables.mjs                 # 默认：本仓库 bundle patch
 *   node dsh/tests/audit_prompt_variables.mjs <file.yml ...>  # 指定文件（排查用）
 *
 * 环境：
 *   DSH_CHECKOUT  harness 源码 checkout（默认 D:\git\deepseek-harness）
 *
 * 退出码：0 = 全部变量已注册；1 = 存在未注册/畸形引用；2 = 无法执行（缺 checkout / 解析器 /
 *         注册集合为空）。2 在 selfcheck 中按 FAIL 处理，可用
 *         DSH_SKIP_PROMPT_VAR_AUDIT=1 显式接受该缺口。
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { join, dirname, resolve } from 'node:path'
import { pathToFileURL, fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const REPO = resolve(HERE, '..', '..')

/**
 * harness 布局：源码 checkout（有 `packages/`）或已安装的 asar 运行时。
 *
 * DSH Desktop 把运行时打进 `resources/app.asar`，普通 Node 的 fs 读不到 asar—
 * 这种布局必须用 `ELECTRON_RUN_AS_NODE=1 "<app>.exe"` 跑本脚本。注册点扫描的差别：
 * checkout 扫 `packages|apps|vendor` 的 src/ 与 lib/，已安装布局扫
 * `node_modules/@deepseek-ai/<pkg>/lib`（编译产物）。
 */
const CHECKOUT = process.env.DSH_CHECKOUT ?? 'D:\\git\\deepseek-harness'

/**
 * Resolve the installed Desktop runtime, preferring the running app:
 *   DSH_NODE_EXECUTABLE = "<install>\DeepSeek Harness.exe"
 *   DSH_INSTALL_DIR     = "<install>\resources\app.asar\dsh\node_modules\@deepseek-ai\dsh"
 * The latter points INSIDE the asar, so it is split at "app.asar" rather than
 * used as a directory. process.execPath covers Electron-run-as-node.
 */
function detectHarnessInstall() {
  const exe = process.env.DSH_NODE_EXECUTABLE
  const installDirEnv = process.env.DSH_INSTALL_DIR ?? ''
  const marker = 'app.asar'
  const markerIndex = installDirEnv.indexOf(marker)
  let resources = exe ? join(dirname(exe), 'resources') : undefined
  let asarDsh = markerIndex >= 0
    ? join(installDirEnv.slice(0, markerIndex + marker.length), 'dsh')
    : undefined
  if (markerIndex >= 0) resources = installDirEnv.slice(0, markerIndex).replace(/[\\/]+$/, '')
  if (!resources && process.execPath) resources = join(dirname(process.execPath), 'resources')
  if (!resources) {
    for (const candidate of [
      process.env.ProgramFiles ? join(process.env.ProgramFiles, 'DeepSeek Harness', 'resources') : undefined,
      process.env.LOCALAPPDATA ? join(process.env.LOCALAPPDATA, 'Programs', 'DeepSeek Harness', 'resources') : undefined,
    ]) {
      if (candidate && existsSync(join(candidate, 'app.asar'))) { resources = candidate; break }
    }
  }
  if (!asarDsh && resources) asarDsh = join(resources, 'app.asar', 'dsh')
  return { resources, asarDsh }
}

const { resources: INSTALL_DIR, asarDsh: ASAR_DSH } = detectHarnessInstall()

/**
 * Layout: a running Desktop session (DSH_NODE_EXECUTABLE set) always validates
 * its own asar runtime; otherwise a source checkout wins (development) and a
 * Desktop install without a checkout falls back to asar.
 */
const runningDesktop = typeof process.env.DSH_NODE_EXECUTABLE === 'string'
const LAYOUT = runningDesktop && ASAR_DSH !== undefined && existsSync(join(ASAR_DSH, 'node_modules')) ? 'asar'
  : existsSync(join(CHECKOUT, 'packages')) ? 'checkout'
    : ASAR_DSH !== undefined && existsSync(join(ASAR_DSH, 'node_modules')) ? 'asar'
      : 'checkout'

const HARNESS = LAYOUT === 'asar' ? ASAR_DSH : CHECKOUT

/** 上游 core/system-prompt/src/index.ts:192/195 的镜像 */
const VARIABLE_NAME = /^[a-z][a-z0-9_]*$/
const GROUP_AT = /^\{\{([^{}]*)\}\}/

const positional = process.argv.slice(2).filter(a => !a.startsWith('--'))
const DEFAULT_PATCH = join(REPO, 'dsh', 'cordis.patch.yml')

let files
if (positional.length > 0) {
  files = positional
} else {
  if (!existsSync(DEFAULT_PATCH)) {
    console.log(`FAIL: bundle patch not found at ${DEFAULT_PATCH} — nothing to verify`)
    process.exit(1)
  }
  files = [DEFAULT_PATCH]
}

// ── 解析器（harness 的 entryListSchema + 其 js-yaml）；缺失则无法执行 ──────────
// checkout：include 构建产物在 vendor/；已安装布局：它就是一个普通依赖包。
const schemaEntry = (LAYOUT === 'asar'
  ? [join(HARNESS, 'node_modules', '@deepseek-ai', 'cordis-plugin-include', 'lib', 'index.js')]
  : [join(HARNESS, 'vendor', 'include', 'lib', 'index.js')]
).find(existsSync)
const yamlCandidates = [
  join(HARNESS, 'node_modules', 'js-yaml', 'dist', 'js-yaml.mjs'),
  // pnpm store 兜底：版本号随上游升级变动，故动态发现而非写死
  ...(() => {
    const pnpm = join(HARNESS, 'node_modules', '.pnpm')
    if (!existsSync(pnpm)) return []
    return readdirSync(pnpm, { withFileTypes: true })
      .filter(e => e.isDirectory() && e.name.startsWith('js-yaml@'))
      .map(e => join(pnpm, e.name, 'node_modules', 'js-yaml', 'dist', 'js-yaml.mjs'))
      .filter(existsSync)
  })(),
]

if (schemaEntry === undefined) {
  console.log(`SKIP: cannot read the harness at ${HARNESS} (layout: ${LAYOUT}) — cannot read the composition schema`)
  if (LAYOUT === 'checkout' && INSTALL_DIR !== undefined) {
    console.log('      this install is packed in app.asar, which plain Node cannot read:')
    console.log(`      run this gate with ELECTRON_RUN_AS_NODE=1 "${join(INSTALL_DIR, '..', 'DeepSeek Harness.exe')}"`)
  } else if (LAYOUT === 'checkout') {
    console.log('      set DSH_CHECKOUT to a harness source checkout')
  }
  process.exit(2)
}
const yamlPath = yamlCandidates.find(existsSync)
if (!yamlPath) {
  console.log(`SKIP: js-yaml not found under ${HARNESS} — cannot parse composition`)
  process.exit(2)
}

/**
 * 收集 harness 注册的提示词变量名。
 *
 * 只认 `systemPrompt.variable('<静态名>', …)`：动态名字（拼出来的变量名）扫不到，
 * 那种情况下与其猜，不如按 fail-closed 报 FAIL 并让人显式处理（DSH_SKIP_PROMPT_VAR_AUDIT=1
 * 或改本门禁的注册集合来源）。
 */
function collectRegisteredVariables() {
  const names = new Set()
  const registration = /\.variable\(\s*['"]([a-z][a-z0-9_]*)['"]/g
  const skipDirs = new Set(['node_modules', '.git', 'dist', 'coverage', 'snapshots', 'tests', '__tests__'])
  const isTest = p => /[\\/](tests|__tests__)[\\/]/.test(p) || /\.(spec|test)\.[cm]?[jt]s$/.test(p)
  /** 从 root 起，最多下探 depth 层，收集 src/ 与 lib/ 里的 .ts/.js */
  const walk = (dir, depth) => {
    if (depth > 4) return
    let entries
    try { entries = readdirSync(dir, { withFileTypes: true }) } catch { return }
    for (const entry of entries) {
      const full = join(dir, entry.name)
      if (entry.isDirectory()) {
        if (skipDirs.has(entry.name)) continue
        walk(full, depth + 1)
        continue
      }
      if (!/\.(ts|js|mjs|cjs)$/.test(entry.name)) continue
      if (isTest(full)) continue
      let text
      try { text = readFileSync(full, 'utf8') } catch { continue }
      registration.lastIndex = 0
      let m
      while ((m = registration.exec(text)) !== null) names.add(m[1])
    }
  }
  if (LAYOUT === 'asar') {
    // 已安装布局：编译产物在 node_modules/@deepseek-ai/<pkg>/lib，没有 workspace 的 packages/。
    const scope = join(HARNESS, 'node_modules', '@deepseek-ai')
    if (existsSync(scope)) {
      for (const entry of readdirSync(scope, { withFileTypes: true })) {
        if (!entry.isDirectory()) continue
        walk(join(scope, entry.name, 'lib'), 2)
      }
    }
  } else {
    walk(join(HARNESS, 'packages'), 0)
    // apps/ 与 vendor/ 里的注册点（若存在）一并算上：集合宁宽勿窄，避免假 FAIL。
    for (const extra of ['apps', 'vendor']) walk(join(HARNESS, extra), 2)
  }
  return names
}

const registered = collectRegisteredVariables()
if (registered.size === 0) {
  console.log(`SKIP: no \`systemPrompt.variable(...)\` registration found under ${HARNESS} (layout: ${LAYOUT}) — cannot derive the registered set`)
  if (LAYOUT === 'checkout' && INSTALL_DIR !== undefined) {
    console.log('      this install is packed in app.asar, which plain Node cannot read:')
    console.log(`      run this gate with ELECTRON_RUN_AS_NODE=1 "${join(INSTALL_DIR, '..', 'DeepSeek Harness.exe')}"`)
  } else {
    console.log('      set DSH_CHECKOUT to the harness checkout the sessions actually boot')
  }
  process.exit(2)
}

const include = await import(pathToFileURL(schemaEntry).href)
const yaml = await import(pathToFileURL(yamlPath).href)

/** 收集 composition 里所有字符串标量，附带其路径标签（preset 子行在 config.plugins[] 内） */
function collectStrings(file) {
  // DSH 0.2.2-rc.3 replaced the exported `entryListSchema` with `parseEntryYaml`
  // (cordis 4.0.0-rc.12 include refactor). Older harnesses only expose the
  // schema, so prefer the function and fall back.
  const text = readFileSync(file, 'utf8')
  const rows = typeof include.parseEntryYaml === 'function'
    ? include.parseEntryYaml(text)
    : yaml.load(text, { schema: include.entryListSchema })
  const out = []
  const walk = (value, path) => {
    if (typeof value === 'string') { out.push({ text: value, path }); return }
    if (Array.isArray(value)) {
      value.forEach((item, i) => walk(item, `${path}[${i}]`))
      return
    }
    if (value !== null && typeof value === 'object') {
      for (const [key, item] of Object.entries(value)) walk(item, path === '' ? key : `${path}.${key}`)
    }
  }
  walk(rows, '')
  return out
}

/**
 * 按上游 `interpolate()` 的扫描规则取出引用（或畸形引用）。
 * 返回 [{ name, malformed }]，只报引用，不报字面散文。
 */
function references(text) {
  const out = []
  let last = 0
  for (let open = text.indexOf('{{'); open >= 0; open = text.indexOf('{{', last)) {
    const group = GROUP_AT.exec(text.slice(open))
    if (group === null) {
      if (text.indexOf('}}', open + 2) >= 0) {
        out.push({ name: text.slice(open, open + 16), malformed: true })
        // 上游在此抛错；门禁继续扫其余引用，一次性报全
      }
      last = open + 2
      continue
    }
    const name = group[0].slice(2, -2)
    if (!VARIABLE_NAME.test(name)) out.push({ name, malformed: true })
    else out.push({ name, malformed: false })
    last = open + group[0].length
  }
  return out
}

let bad = 0
for (const file of files) {
  console.log(`\n== ${file}`)
  if (!existsSync(file)) {
    console.log('   NOT FOUND: target file does not exist (check the path)')
    bad++
    continue
  }
  let strings
  try {
    strings = collectStrings(file)
  } catch (e) {
    console.log(`   PARSE FAIL: ${e.message}`)
    bad++
    continue
  }
  const seen = new Map()   // name -> { ok, where[] }
  for (const { text, path } of strings) {
    for (const ref of references(text)) {
      const key = `${ref.malformed ? 'malformed:' : ''}${ref.name}`
      const entry = seen.get(key) ?? { ref, where: [] }
      entry.where.push(path)
      seen.set(key, entry)
    }
  }
  if (seen.size === 0) {
    console.log('   (no prompt-variable reference in this composition)')
    continue
  }
  let fileBad = 0
  for (const key of [...seen.keys()].sort()) {
    const { ref, where } = seen.get(key)
    const ok = !ref.malformed && registered.has(ref.name)
    if (!ok) { fileBad++; bad++ }
    const why = ref.malformed
      ? `malformed reference (names must match ${String(VARIABLE_NAME)})`
      : `not registered by this harness (registered: ${[...registered].sort().join(', ') || '(none)'})`
    console.log(`   ${ok ? 'OK  ' : 'BAD '} {{${ref.name}}}${ok ? '' : `  <- ${why}`}`)
    console.log(`        at ${[...new Set(where)].join(', ')}`)
  }
  console.log(`   -> ${seen.size} reference(s), ${fileBad} unknown`)
}

console.log(bad === 0
  ? `\nAll prompt-variable references registered ✅  (harness: ${HARNESS}; registered: ${[...registered].sort().join(', ')})`
  : `\n${bad} unknown prompt-variable reference(s) ❌  (harness: ${HARNESS})`)
process.exit(bad === 0 ? 0 : 1)
