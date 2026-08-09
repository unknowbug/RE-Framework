---
name: re-framework-v2
description: RE-Framework v2 包结构索引 — AGENTS.md 探测器 + spec/engineering-framework-v1.md（模块化协议）+ skills/（core/re-binary/re-code/swe）+ templates/ + knowledge-builtin/
metadata:
  type: reference
---

RE-Framework v2 位于 RE-Framework/ 目录（原 v1 的 42KB CLAUDE.md 已归档为 `spec/legacy-claude-v1.md` 并删除原件）。

**包结构:**

- `AGENTS.md` — 索引式入口：任务类型探测器（模块路由）+ skill 触发表 + 核心铁律简版
- `spec/engineering-framework-v1.md` — 核心协议：铁律（领域无关）+ 模块化接口契约（模块定义/探测自适应/卸载保证/manifest 校验）+ Anchorlaw v0.9 四接口面引用
- `skills/` — 分层 skill 参考实现：
  - core.*（必装）: plan/artifact/knowledge/version/fanout/judge
  - re.*（re-binary 模块）: lift/classify/trace/scout
  - recode.*（re-code 模块）: deobfuscate/classmap/behavior/scout
  - swe.guide（swe 模块，引用 Anchorlaw）
  - modules/*.yaml — 模块声明（触发表/依赖/卸载保证）
- `templates/` — 产物 schema（语言无关：地址/字节码偏移/类全名定位）
- `knowledge-builtin/` — 预置知识库（已填充真实内容）
- `memory/` — 本目录

**部署:** 按模块复制 skills 到目标项目 `.reasonix/skills/` + `pip install anchorlaw anchorlaw-scanner`（方式C）。详见 README.md。

**验证协议:** 引用 Anchorlaw v0.9（MIT，由 Practify 更名而来），不复制实现——见 `spec/engineering-framework-v1.md` §3。
