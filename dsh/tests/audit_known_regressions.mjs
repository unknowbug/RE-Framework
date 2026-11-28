/**
 * audit_known_regressions.mjs — 已修缺陷的回归门禁（fail-closed）。
 *
 * 每条都是本仓库**曾经真实发生**过的失效（DSH 上游漂移、插件竞态、安装器缺陷）。
 * 修完之后如果只靠人记住，下一次改动很容易悄悄退回去；这里把每条变成可执行断言：
 *
 *   absent  — 某个**错误的**写法/配置不得再出现（回归 = 重新出现）
 *   present — 某个**正确的**写法必须在（回归 = 被删掉或改写）
 *
 * 另含**版本一致性**检查：spec §3 的 Anchorlaw 引用基线必须与 persona、README、
 * AGENTS、ref-maintain 同步（2026-11-27 的教训：persona 曾停留在 v0.24）。
 *
 * 结构/文本级判据在本文件；行为级判据在 test_*.py / test_*.mjs 里（两边互补）。
 *
 * 用法: node audit_known_regressions.mjs [repoRoot]
 * 退出码: 0 全绿 / 1 有回归 / 2 守卫文件缺失（无法判定 = fail-closed）
 */
import { readFileSync, existsSync } from 'node:fs'
import { join, dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const REPO = process.argv[2] ?? resolve(HERE, '..', '..')

/** 每条守卫：why 记录它从哪次事故来，避免"清理注释"时顺手把判据删掉。 */
const GUARDS = [
  // ── DSH 上游漂移（2026-09-09 / 10-10 / 10-17 / 10-24）──────────────────
  { id: 'cwd-prompt-variable', kind: 'absent', file: 'dsh/cordis.patch.yml', needle: '{{cwd}}',
    why: '2026-10-10 DSH 0.2.x 删除 cwd 提示词变量；模板严格解析 → 会话组装期抛错' },
  { id: 'backgroundMode-key', kind: 'absent', file: 'dsh/cordis.patch.yml', needle: 'backgroundMode',
    why: '2026-10-17 dsh-tool-subagent 已移除该键；Schemastery 静默忽略 → 死配置' },
  { id: 'list-agents-subpath-row', kind: 'absent', file: 'dsh/cordis.patch.yml', needle: 'tool-subagent-list-agents',
    why: '2026-10-24 上游删除 ./list-agents subpath（ERR_PACKAGE_PATH_NOT_EXPORTED）' },
  { id: 'working-directory-tool-row', kind: 'absent', file: 'dsh/cordis.patch.yml', needle: 'tool-working-directory',
    why: '2026-11-27 DSH 0.2.2-rc.3 删除 working_directory 工具与包；残留行会在加载时报 not found' },
  { id: 'engines-dsh-declared', kind: 'present', file: 'dsh/package.json', needle: '">=0.2.0 <0.3.0"',
    why: '兼容性必须由 engines.dsh fail-closed 判定，而不是在错误 API 上静默加载' },

  // ── 插件：issue #4 的注入竞态、解释器回退、晚发布服务 ────────────────────
  { id: 'plugin-inject-subprocess', kind: 'present', file: 'dsh/plugins/re-framework-tools.js', needle: "inject = ['tools', 'subprocess']",
    why: 'issue #4：apply() 缺 subprocess 即早退，Cordis 不保证服务就绪 → ref_* 工具静默不注册' },
  { id: 'plugin-python3-fallback', kind: 'present', file: 'dsh/plugins/re-framework-tools.js', needle: "'python', 'python3'",
    why: 'issue #4：麒麟等发行版只有 python3，硬编码 python 会让 ref_* 工具全失效' },
  { id: 'plugin-optional-call-time', kind: 'present', file: 'dsh/plugins/re-framework-tools.js', needle: 'skillsOf',
    why: 'Anchorlaw 0.26.2 / issue #4：可选服务在 apply() 一次性捕获会把"晚发布"固化成永久降级' },

  // ── 安装器：desktop 直装 / 无 BOM / EAP / patch 层 ───────────────────────
  { id: 'desktop-profile-branch', kind: 'present', file: 'dsh/scripts/install.ps1', needle: "-ieq 'desktop'",
    why: '2026-11-13 CLI 按名字拒绝 desktop profile；install.ps1 必须自带直写分支' },
  { id: 'installer-no-bom', kind: 'present', file: 'dsh/scripts/install.ps1', needle: 'UTF8Encoding($false)',
    why: 'PS 5.1 的 Set-Content -Encoding UTF8 会写 BOM；DSH 裸 JSON.parse 会 REQUEST_EXTENSION' },
  { id: 'installer-eap-continue', kind: 'present', file: 'dsh/scripts/install.ps1', needle: 'Invoke-Native',
    why: '原生命令 stderr 在 Stop 下会变终止错误（Node ≥22 警告）；必须只按退出码判定' },
  { id: 'installer-patch-layer', kind: 'present', file: 'dsh/scripts/install.ps1', needle: 'patch_layer.py',
    why: 'home/profile patch 是合法层；只能 row 级摘除，绝不整文件删除（PR #2 / 2026-09-18）' },

  // ── 门禁：asar 运行时 / parseEntryYaml / 零覆盖 ──────────────────────────
  { id: 'selfcheck-asar-runtime', kind: 'present', file: 'dsh/scripts/selfcheck.ps1', needle: 'ELECTRON_RUN_AS_NODE',
    why: '2026-11-13 普通 Node 的 fs 读不到 app.asar；Desktop 布局必须换运行时' },
  { id: 'gate-parse-entry-yaml', kind: 'present', file: 'dsh/tests/audit_preset_rows.mjs', needle: 'parseEntryYaml',
    why: '2026-11-17 DSH 0.2.2-rc.3 起 include 不再导出 entryListSchema' },
  { id: 'gate-zero-row-fails', kind: 'present', file: 'dsh/tests/audit_preset_rows.mjs', needle: 'NO SCAN',
    why: '2026-11-27 Anchorlaw 0.26.2：解析 0 行却报绿 = 假绿；零覆盖必须 fail-closed' },
  { id: 'spec-equivalence-ladder', kind: 'present', file: 'spec/engineering-framework-v1.md', needle: '### 5.8 等价性证据形态阶梯',
    why: '2026-11-28 Portable-Knowledge P03 晋升 spec §5.8；删除即回退到只用行数/计数命名的弱证据' },
  { id: 'prompt-gate-parse-entry-yaml', kind: 'present', file: 'dsh/tests/audit_prompt_variables.mjs', needle: 'parseEntryYaml',
    why: '同 gate-parse-entry-yaml（变量门禁共享同一解析器）' },
]

const failures = []
const skipped = []

for (const guard of GUARDS) {
  const path = join(REPO, guard.file)
  if (!existsSync(path)) {
    skipped.push(`${guard.id}: 守卫文件缺失 ${guard.file}`)
    continue
  }
  const text = readFileSync(path, 'utf8')
  // `absent` judges only ACTIVE lines: comments that explain why the construct was
  // removed are allowed (and valuable), so a comment must not count as a regression.
  const found = guard.kind === 'absent'
    ? text.split(/\r?\n/).some(line => !line.trimStart().startsWith('#') && line.includes(guard.needle))
    : text.includes(guard.needle)
  const ok = guard.kind === 'absent' ? !found : found
  if (!ok) failures.push(guard)
}

// ── 版本一致性：spec §3 基线必须与 persona / README / AGENTS / ref-maintain 同步 ──
function checkReferenceAlignment() {
  const specPath = join(REPO, 'spec', 'engineering-framework-v1.md')
  if (!existsSync(specPath)) return
  const spec = readFileSync(specPath, 'utf8')
  const m = /当前引用基线：\*\*Anchorlaw (v\d+\.\d+\.\d+)\*\*/.exec(spec)
  if (!m) return
  const baseline = m[1]
  const anchors = [
    'dsh/cordis.patch.yml',
    'README.md',
    'README_EN.md',
    'AGENTS.md',
    'dsh/skills/ref-maintain/SKILL.md',
  ]
  for (const rel of anchors) {
    const path = join(REPO, rel)
    if (!existsSync(path)) { skipped.push(`reference-alignment: 缺文件 ${rel}`); continue }
    if (!readFileSync(path, 'utf8').includes(baseline)) {
      failures.push({
        id: `reference-alignment:${rel}`,
        kind: 'present',
        file: rel,
        needle: `Anchorlaw ${baseline}`,
        why: `spec §3 基线为 ${baseline}，该文件仍引用旧版本（persona 曾停留在 v0.24 的同类漂移）`,
      })
    }
  }
}

checkReferenceAlignment()

console.log(`  ${GUARDS.length + 1} known-regression guard(s) checked against ${REPO}`)
for (const s of skipped) console.log(`  SKIP  ${s}`)

if (failures.length === 0) {
  console.log('  All known regressions still fixed ✅')
  process.exit(skipped.length > 0 ? 2 : 0)
}

for (const f of failures) {
  const what = f.kind === 'absent' ? `重新出现 "${f.needle}"` : `缺少 "${f.needle}"`
  console.log(`  REGRESS  ${f.id}`)
  console.log(`           ${f.file}: ${what}`)
  console.log(`           why: ${f.why}`)
}
console.log(`\n  ${failures.length} known regression(s) ❌`)
process.exit(1)
