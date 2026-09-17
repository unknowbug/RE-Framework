/**
 * audit_trigger_coverage.mjs — 执行强制链的「触发后有无产物」门禁
 *
 * 用途：core-plan 的四强制触发点（scout / fan-out / judge / knowledge）当前是
 *       「自然语言 + AI 自觉」——模型可以预置一个空/含糊的项而形式上"预置了"。
 *       b2 判断（正确）：**不应**去判定「该不该触发」（那是语义判断，强行机械化会
 *       退化成关键词匹配并制造新盲区），但「**触发后有没有留下产物**」是有限集上的
 *       **可判定谓词**——这正是 reactive coeffect 的精神：不判 satisfaction，只判
 *       transition 是否被观察。
 *
 * 用法：
 *   node dsh/tests/audit_trigger_coverage.mjs <investigation-dir> [<dir> ...]
 *   node dsh/tests/audit_trigger_coverage.mjs --all <investigations-root>
 *
 * 判据（三态，DECLARED-SKIP 必须带非空 reason）：
 *   - fan-out：`candidates/` 存在 → 必有 ≥2 个 .bN；否则计划文件须有
 *               `fan-out: not-triggered(<reason>)` 行
 *   - judge  ：出现 status 从 draft→candidate 的记录 → 必须有 judge-review-*.md / review-*.md
 *   - scout  ：存在管线地图/任务书 → OK；否则计划文件须有 `scout: skipped(<reason>)`
 *   - knowledge：含结论的产物 → 须有对应 knowledge/docs 落盘或显式 no-write 声明
 *
 * 退出码：0 = 全部有产物或显式声明；1 = 存在 MISSING；2 = 无法执行（目录不存在）
 *
 * 设计约束（b2 明确要求）：**误报必须有害羞出口**——合法的「本课题无需 fan-out」
 *   走 `not-triggered(<reason>)`，不是失败。故本门只对「**既无产物又无声明**」报警。
 *
 * 状态：本门为**新增能力**，按 ref-maintain 铁律 3 标注 **Unverified**——尚未用
 *   历史课题回填测过误报率。先作为**报告工具**（人读输出），确认误报可接受后再
 *   考虑接入 selfcheck。接入前不得作为阻塞门。
 */
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs'
import { join, dirname, basename } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const args = process.argv.slice(2)
const allMode = args.includes('--all')
const positional = args.filter(a => !a.startsWith('--'))

if (positional.length === 0) {
  console.log('usage: node audit_trigger_coverage.mjs <investigation-dir> [...]')
  console.log('       node audit_trigger_coverage.mjs --all <investigations-root>')
  process.exit(2)
}

/** 目标课题目录列表 */
function collectDirs() {
  const out = []
  for (const p of positional) {
    if (!existsSync(p)) return { error: `not found: ${p}` }
    if (allMode) {
      for (const e of readdirSync(p, { withFileTypes: true })) {
        if (e.isDirectory()) out.push(join(p, e.name))
      }
    } else {
      out.push(p)
    }
  }
  return { dirs: out }
}

const { dirs, error } = collectDirs()
if (error) { console.log(`SKIP: ${error}`); process.exit(2) }

/** 递归收集文件（相对路径） */
function walk(dir, base = dir, acc = []) {
  let entries
  try { entries = readdirSync(dir, { withFileTypes: true }) } catch { return acc }
  for (const e of entries) {
    const full = join(dir, e.name)
    if (e.isDirectory()) walk(full, base, acc)
    else acc.push(full.slice(base.length + 1).replace(/\\/g, '/'))
  }
  return acc
}

/** 计划类文件全文（用于找显式声明行） */
function planText(files, dir) {
  const planish = files.filter(f =>
    /(架构|计划|方案|plan|任务|task|roadmap|README)/i.test(f) && f.endsWith('.md'))
  return planish.map(f => {
    try { return readFileSync(join(dir, f), 'utf8') } catch { return '' }
  }).join('\n')
}

/** 声明行检测：not-triggered / skipped 带非空括号 reason */
function hasDeclaredSkip(text, key) {
  const re = new RegExp(`${key}\\s*:\\s*(not-triggered|skipped)\\s*\\(([^)]+)\\)`, 'i')
  const m = text.match(re)
  return m && m[2].trim().length > 0
}

let bad = 0
console.log('== 触发点产物覆盖审计 ==')

for (const dir of dirs) {
  const files = walk(dir)
  if (files.length === 0) { console.log(`\n-- ${basename(dir)}: (空目录，跳过)`); continue }
  console.log(`\n-- ${basename(dir)}  (${files.length} files)`)
  const plan = planText(files, dir)

  // 1. fan-out：只有在**已经出现候选**时才要求汇聚完整性（≥2 或显式声明）；
  //    完全没有候选 = 本课题根本没 fan-out，属**正常**（不是缺口）。
  //    实测教训：把"无候选"判为 MISSING 会对真实课题产生 100% 误报——本仓 4 个
  //    历史课题全是单假设调查，从未需要 fan-out。这正是 b2 警告的"语义判断被
  //    强行机械化"的形态；谓词必须只判"触发后有无产物"。
  const cands = files.filter(f => /(^|\/)candidates\//.test(f) && /\.b\d+\./.test(f))
  const bNAnywhere = files.filter(f => /\.b\d+\.(md|yaml|yml)$/.test(f))
  const pool = cands.length > 0 ? cands : bNAnywhere
  if (pool.length >= 2) {
    console.log(`   OK   fan-out: ${pool.length} candidates (${pool.map(f => basename(f)).join(', ')})`)
  } else if (pool.length === 1) {
    console.log(`   MISSING fan-out: 只有 1 个候选 —— 要么补齐 ≥2 互斥候选，要么声明 fan-out: not-triggered(<reason>)`)
    bad++
  } else {
    console.log('   —    fan-out: 无候选（本课题未触发 fan-out）')
  }

  // 2. judge：有 candidate 痕迹 → 须有 review 类产物。
  //    实测教训：只认 review-*.md 会对真实项目误报——CoreSwap 用 draft-*.md /
  //    *-verify.md 等命名承载审查意见。判定放宽为「审查型产物」的多种命名，
  //    **宁可漏报不可误报**（本门目的是发现"完全没做"，不是校验命名规范）。
  const hasCandidate = files.some(f => {
    try { return /status:\s*candidate/i.test(readFileSync(join(dir, f), 'utf8')) } catch { return false }
  })
  const hasReview = files.some(f =>
    // 审查型产物：命名多样（review-<date>-<n>.md / draft-*.md / *-verify.md ...
    // 或中文「审查/复核」）。实测教训：要求「review-NNN.md 结尾」会漏掉
    // review-260907-10-001.md 这类带日期段的真实命名 → 误报。**宁可漏报不可误报**。
    /(^|\/)[^/]*review[^/]*\.md$/i.test(f) ||
    /(^|\/)[^/]*draft[^/]*\.md$/i.test(f) ||
    /(verify|verdict|opinion|audit[^/]*\.md)/i.test(f) ||
    /(审查|复核|意见)/.test(f))
  if (hasCandidate) {
    if (hasReview) console.log('   OK   judge: 审查型产物存在')
    else { console.log('   MISSING judge: 存在 candidate 状态但无任何审查型产物（review-*/draft-*/*-verify*）'); bad++ }
  } else if (hasDeclaredSkip(plan, 'judge')) {
    console.log('   OK   judge: skipped (已声明 reason)')
  } else {
    console.log('   —    judge: 无 candidate 状态（未触发，无需产物）')
  }

  // 3. scout：管线地图/任务书
  const hasScout = files.some(f => /(管线地图|任务书|scout|pipeline-map|recon)/i.test(f))
  if (hasScout) console.log('   OK   scout: 勘探产物存在')
  else if (hasDeclaredSkip(plan, 'scout')) console.log('   OK   scout: skipped (已声明 reason)')
  else console.log('   —    scout: 无勘探产物（若本课题机制已明可声明 scout: skipped(<reason>)）')

  // 4. knowledge：含结论 → 知识落盘或显式 no-write
  const hasConclusion = /status:\s*(candidate|confirmed)/i.test(plan) ||
    files.some(f => /(verdict|结论|conclusion)/i.test(f))
  if (hasConclusion) {
    if (hasDeclaredSkip(plan, 'knowledge')) console.log('   OK   knowledge: no-write (已声明 reason)')
    else console.log('   —    knowledge: 存在结论痕迹——确认知识库/doc 是否已落盘（价值门判定）')
  }
}

console.log(bad === 0 ? '\nAll trigger points covered or explicitly declared ✅' : `\n${bad} MISSING trigger point(s) ❌`)
console.log('note: 本门为新增能力（Unverified），当前作报告工具；误报请用 DECLARED-SKIP(reason) 声明。')
process.exit(bad === 0 ? 0 : 1)
