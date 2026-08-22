# restore-reasonix.ps1 — 从 archive/reasonix 恢复 Reasonix 工作副本到仓库根
#
# 适用对象：Fork 了 RE-Framework、想基于 Reasonix 版本继续迭代的维护者。
# 主仓库已停止维护 Reasonix 宿主格式（仅维护 DSH），本脚本一键恢复。
# 幂等：已存在的目标备份为 .bak，不静默覆盖。在仓库根执行。

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$archive = Join-Path $repoRoot 'archive\reasonix'

function Restore-Item($src, $dst) {
  if (-not (Test-Path $src)) { Write-Host "  skip (missing source): $src"; return }
  if (Test-Path $dst) {
    $bak = "$dst.bak"
    Write-Host "  backup existing: $dst -> $bak"
    if (Test-Path $bak) { Remove-Item $bak -Recurse -Force }
    Move-Item $dst $bak -Force
  }
  $parent = Split-Path -Parent $dst
  New-Item -ItemType Directory -Path $parent -Force | Out-Null
  Copy-Item $src $dst -Recurse -Force
  Write-Host "  restored: $dst"
}

Write-Host "== RE-Framework Reasonix restore =="

# 1. 技能规范正文（dot 名）
Restore-Item (Join-Path $archive 'skills') (Join-Path $repoRoot 'skills')

# 2. Reasonix 入口 + 文档
Restore-Item (Join-Path $archive 'AGENTS.md') (Join-Path $repoRoot 'AGENTS.md')
Restore-Item (Join-Path $archive 'README.md') (Join-Path $repoRoot 'README.md')
Restore-Item (Join-Path $archive 'README_EN.md') (Join-Path $repoRoot 'README_EN.md')

# 3. Reasonix 脚本（部署器 + manifest 校验器）
Restore-Item (Join-Path $archive 'scripts\install.py') (Join-Path $repoRoot 'scripts\install.py')
Restore-Item (Join-Path $archive 'scripts\validate_manifest.py') (Join-Path $repoRoot 'scripts\validate_manifest.py')

# 4. 技能同步生成器（dsh/skills 从 skills/ 派生）
Restore-Item (Join-Path $archive 'scripts\sync_skills.py') (Join-Path $repoRoot 'dsh\scripts\sync_skills.py')

# 5. memory 文件
Restore-Item (Join-Path $archive 'memory') (Join-Path $repoRoot 'memory')

Write-Host ""
Write-Host "Done. Reasonix 侧已恢复到仓库根：skills/（16 dot 技能 + modules）、根 AGENTS.md（Reasonix 探测器）、"
Write-Host "README/README_EN（Reasonix 版）、scripts/install.py + validate_manifest.py、dsh/scripts/sync_skills.py、memory/"
Write-Host "从此自行迭代：archive/reasonix/ 不再更新。dsh/ 目录保留（双宿主共存，由你决定是否保留）。"
