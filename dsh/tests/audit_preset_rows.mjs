/**
 * audit_preset_rows.mjs — preset 行解析性门禁（fail-closed）
 *
 * 用途：校验 re-framework agent preset 的每一行 `name:` 能否在当前 harness 版本中解析。
 *       上游改名/移除插件包时本脚本非零退出，避免等用户 resume 会话时才看到挂载失败。
 *       两类事故都由本门禁负责拦下：
 *         - 2026-09-09 上游包改名（`dsh-workflow-worker-thread` → `dsh-workflow-ptc`）
 *         - **2026-09-23 载体迁移**：DSH 0.1.7 把 preset 载体从
 *           `$DSH_HOME/.agent-presets/<id>/` 目录换成 **bundle patch 声明行**。旧门禁
 *           既不认识新载体、也不走 `config.plugins[]`，于是**全绿而 resume 报
 *           `Unknown agent preset`**。递归 1/3（见 `rowNames`）即该事故的修复本体。
 *
 * 用法：
 *   node dsh/tests/audit_preset_rows.mjs                        # 默认：本仓库 bundle patch（dsh/cordis.patch.yml）
 *   node dsh/tests/audit_preset_rows.mjs <file.yml ...>         # 指定文件（bundle patch 或旧 entry list）
 *   node dsh/tests/audit_preset_rows.mjs --installed <preset>   # 校验历史 ~/.dsh/.agent-presets/<名>/（仅排查用）
 *
 * 环境：
 *   DSH_CHECKOUT     harness 源码 checkout（默认 D:\git\deepseek-harness）
 *   DSH_HARNESS_BASE 已安装 harness 所在目录（包名解析基准；默认 <DSH_CHECKOUT>\apps\cli）
 *   DSH_HOME         默认 %USERPROFILE%\.dsh
 *
 * 判据（镜像上游 `classifyRowSpecifier()` @ agent-presets/src/specifier.ts
 * + `packageInstalled()` @ agent-presets/src/discovery.ts）：
 *   - `cordis:` 前缀     → 内置行，Loader 自带，放行
 *   - 以 `.` 开头        → bundle 自带文件，锚定在**该 patch 文件所在目录**（上游
 *                          `anchorInsertedPluginNames()` 语义；仅顶层 insert 生效，
 *                          `config.plugins[]` 内的相对路径**不会**被锚定）
 *   - `file:` / 绝对路径 → 文件 URL，要求文件存在（Windows 盘符路径必须走 file URL）
 *   - **本 bundle 自身的包** → 由安装步骤以依赖形式进入 profile，按设计不在 harness base
 *                          下；用本仓库 `dsh/package.json` 的 exports 校验子路径**且**
 *                          要求其指向的文件存在（只校验键会让"插件被改名/移动"照样绿）
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

/**
 * harness 布局：源码 checkout（有 `packages/`）或已安装的 asar 运行时。
 *
 * DSH Desktop 把整个运行时打进 `resources/app.asar`，**普通 Node 的 fs 读不到 asar**——
 * 这种布局必须用 `ELECTRON_RUN_AS_NODE=1 "<app>.exe"` 跑本脚本（Electron 的 fs 透明
 * 读 asar）。两种布局的包都落在 `<HARNESS>/node_modules`，所以包名解析与 exports
 * 校验的代码不变，只有包清单的来源不同（checkout: packages/；asar: node_modules/@deepseek-ai）。
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
  // asar 布局：harness 根（app.asar/dsh）下的 node_modules 就是完整安装面。
  const candidates = LAYOUT === 'asar' ? [HARNESS] : [join(HARNESS, 'apps', 'cli'), HARNESS]
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

const args = process.argv.slice(2)
const installedMode = args.includes('--installed')
const positional = args.filter(a => !a.startsWith('--'))

/** 目标文件：[{ file, sourceTree }] */
const DEFAULT_PATCH = join(REPO, 'dsh', 'cordis.patch.yml')
let files
if (installedMode) {
  // 旧目录形态已死（DSH >= 0.1.7 无任何代码读 .agent-presets/）。保留该开关仅用于
  // 显式排查历史副本；它**不再是** selfcheck 的默认路径。
  files = positional.map(name => ({
    file: join(HOME, '.agent-presets', name, 'agent.cordis.yml'),
    sourceTree: false,
  }))
} else if (positional.length > 0) {
  // 显式指定的文件按真实载体处理（相对行必须存在——bundle patch 就地生效，不像
  // 旧形态那样要等 install 拷贝）。
  files = positional.map(f => ({ file: f, sourceTree: false }))
} else {
  // selfcheck 默认：**bundle patch**（DSH >= 0.1.7 的 preset 载体）。
  // 主目标缺失 = 门禁失效，必须报错而非静默跳过——本门禁存在的理由就是
  // "别让会话在运行时才发现 preset 挂不上"（2026-09-23 事故）。
  if (!existsSync(DEFAULT_PATCH)) {
    console.log(`FAIL: bundle patch not found at ${DEFAULT_PATCH} — nothing to verify`)
    process.exit(1)
  }
  files = [{ file: DEFAULT_PATCH, sourceTree: false }]
}

// ── 解析器（harness 的 entryListSchema + 其 js-yaml）；缺失则跳过并显式说明 ──
// checkout：include 构建产物在 vendor/；已安装布局：它就是一个普通依赖包。
const schemaEntry = (LAYOUT === 'asar'
  ? [join(HARNESS, 'node_modules', '@deepseek-ai', 'cordis-plugin-include', 'lib', 'index.js')]
  : [join(HARNESS, 'vendor', 'include', 'lib', 'index.js')]
).find(existsSync)
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

if (schemaEntry === undefined) {
  console.log(`SKIP: cannot read the harness at ${HARNESS} (layout: ${LAYOUT}) — cannot resolve packages`)
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

/** 收集 harness 里所有包：name -> { dir, exports } */
function collectPackages() {
  const map = new Map()
  const roots = []
  if (LAYOUT === 'asar') {
    // 已安装布局：@deepseek-ai/<pkg> 直接挂在 node_modules 下（没有 workspace 的 packages/）。
    const scope = join(HARNESS, 'node_modules', '@deepseek-ai')
    if (existsSync(scope)) roots.push(scope)
  } else {
    const pkgs = join(HARNESS, 'packages')
    if (existsSync(pkgs)) {
      for (const g of readdirSync(pkgs, { withFileTypes: true })) {
        if (g.isDirectory()) roots.push(join(pkgs, g.name))
      }
    }
    roots.push(join(HARNESS, 'vendor'), join(HARNESS, 'apps'))
  }
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

/**
 * 本仓库自己的 bundle 清单（`dsh/package.json`）。bundle 的 preset 行用**裸包名**
 * 指向自身插件（`<name>/plugin`）——该包由安装步骤以依赖形式进入 profile，既不在
 * harness 里、也不在任何 node_modules 中，所以**不能**走 harness base 查找，只能用
 * 本仓库清单的 `exports` 校验子路径 + 目标文件存在。
 */
const SELF_BUNDLE = (() => {
  const p = join(REPO, 'dsh', 'package.json')
  if (!existsSync(p)) return undefined
  try {
    const m = JSON.parse(readFileSync(p, 'utf8'))
    return typeof m?.name === 'string' ? { name: m.name, exports: m.exports } : undefined
  } catch { return undefined }
})()

// 基准健全性探测（错基准 → exit 2，而不是满屏假 BAD）。复用 rowNames（函数声明提升）
// 以保证探测与正式审计走**同一套**遍历——否则会出现"探测看得见、审计看不见"（或
// 反之）的错位，正是 2026-09-23 事故的形态。
{
  const target = files.find(f => existsSync(f.file))
  let probeNames = []
  if (target) {
    try { probeNames = rowNames(target.file) } catch { probeNames = [] }
  }
  if (probeNames.length > 0 && !baseLooksUsable(HARNESS_BASE, probeNames)) {
    console.log(`SKIP: harness base ${HARNESS_BASE} resolves none of this preset's packages — wrong base?`)
    console.log('      set DSH_HARNESS_BASE to the installed harness dir (checkout: <checkout>/apps/cli)')
    process.exit(2)
  }
}

/**
 * 收集所有行的 `name`。必须覆盖**两种载体 + 三条递归路径**，缺一即漏检：
 *   载体 a. bundle patch（顶层是 `- insert: [...]`；DSH >= 0.1.7 的 preset 载体）
 *   载体 b. 旧 entry list（顶层直接是行数组；<= 0.1.6）
 *   递归 1. `insert[]`          —— 载体 a 的行在这里
 *   递归 2. `config[]`          —— group 子行
 *   递归 3. `config.plugins[]`  —— **preset 行的子行列表，新机制的全部内容**
 *
 * 2026-09-23 事故：本函数原先只走递归 2、且不认识载体 a。上游 0.1.7 把 preset 换成
 * bundle patch 后，本门禁**全绿**而会话 resume 报 `Unknown agent preset: re-framework`。
 * 递归 1/3 是那次事故的修复本体，**勿删**。
 */
function rowNames(file) {
  // DSH 0.2.2-rc.3 replaced the exported `entryListSchema` with `parseEntryYaml`
  // (cordis 4.0.0-rc.12 include refactor). Older harnesses only expose the
  // schema, so prefer the function and fall back — this gate must run against
  // both the installed runtime and a newer checkout. Passing `schema: undefined`
  // would silently fall back to the default schema, which cannot parse `!!js`,
  // and then report a PARSE FAIL on our own bundle patch.
  const text = readFileSync(file, 'utf8')
  const rows = typeof include.parseEntryYaml === 'function'
    ? include.parseEntryYaml(text)
    : yaml.load(text, { schema: include.entryListSchema })
  const out = []
  const walk = list => {
    for (const row of list ?? []) {
      if (Array.isArray(row?.insert)) walk(row.insert)                    // 载体 a
      if (typeof row?.name === 'string') out.push(row.name)
      if (Array.isArray(row?.config)) walk(row.config)                    // group 子行
      if (Array.isArray(row?.config?.plugins)) walk(row.config.plugins)   // preset 子行
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
    // bundle 自带文件随 bundle 一起走：`.` 开头的行锚定在**该 patch 文件所在目录**
    // （上游 anchorInsertedPluginNames() 语义）。注意 preset 行**不是** group，故其
    // config.plugins[] 内的相对路径**不会**被锚定——那里的本地插件必须用裸包名子路径。
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
  // 自引用：bundle 自身的包（preset 里的本地插件行）。它由安装步骤装进 profile，
  // 按设计就不在 harness base 下——用本仓库 bundle 清单的 exports 校验子路径，
  // 而不是误报"上游改名/移除"。
  const selfBase = row.specifier.startsWith('@')
    ? row.specifier.split('/').slice(0, 2).join('/')
    : row.specifier.split('/')[0]
  if (SELF_BUNDLE !== undefined && selfBase === SELF_BUNDLE.name) {
    const selfSub = row.specifier.slice(selfBase.length).replace(/^\//, '')
    const keys = Object.keys(SELF_BUNDLE.exports ?? {})
    if (selfSub !== '' && !keys.includes(`./${selfSub}`)) {
      return { ok: false, why: `self-bundle subpath ./${selfSub} not in exports (have: ${keys.join(', ') || 'none'})` }
    }
    // exports 里有这个键还不够：**它指向的文件必须存在**。只校验键会让"插件文件
    // 被改名/移动"照样绿——与 2026-09-23 事故同一失效类（门禁绿、运行时挂载失败）。
    if (selfSub !== '') {
      const entry = SELF_BUNDLE.exports[`./${selfSub}`]
      const rel = typeof entry === 'string' ? entry : entry?.default
      if (typeof rel !== 'string') {
        return { ok: false, why: `self-bundle export ./${selfSub} has no string target` }
      }
      if (!existsSync(join(REPO, 'dsh', rel))) {
        return { ok: false, why: `self-bundle export ./${selfSub} points at a missing file: dsh/${rel}` }
      }
    }
    return { ok: true, why: `self bundle (${SELF_BUNDLE.name})` }
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
let totalRows = 0
for (const { file, sourceTree } of files) {
  console.log(`\n== ${file}${installedMode ? '  (legacy installed copy — 排查用)' : ''}`)
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
  // "Green on things that were never looked at" is the same silent-green class as
  // the 2026-09-09 incident: an empty/misparsed carrier yields zero rows, and a
  // zero-row pass proves nothing. Fail closed instead.
  if (names.length === 0) {
    console.log(`   NO SCAN: parsed 0 rows from ${file} — empty file or the parser no longer matches the carrier; not a pass`)
    bad++
    continue
  }
  totalRows += names.length
  for (const name of names.sort()) {
    const r = classify(name, dirname(file), sourceTree)
    if (!r.ok) { fileBad++; bad++ }
    console.log(`   ${r.ok ? 'OK  ' : 'BAD '} ${name}${r.ok ? '' : `  <- ${r.why}`}`)
  }
  console.log(`   -> ${names.length} reference(s), ${fileBad} unresolvable`)
}

console.log(bad === 0
  ? `\nAll preset rows resolvable ✅ (${totalRows} row(s) across ${files.length} file(s))`
  : `\n${bad} unresolvable preset row(s) ❌`)
process.exit(bad === 0 ? 0 : 1)
