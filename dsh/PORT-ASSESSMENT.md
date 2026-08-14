# RE-Framework → DSH 移植评估与路线图

> 评估日期：2026-08-14 · 评估人：DSH Agent（RE-Framework maintainer）
> 源项目：`E:\PYTHON\RE-Framework`（RE-Framework v2，逆向 + 编程通用工程方法论框架，spec/engineering-framework-v1.md）
> 参照先例：`E:\PYTHON\Anchorlaw\dsh`（Anchorlaw 协议 DSH 宿主适配层，2026-08-12 完成）
> 结论：**可移植性高**——16/16 技能正文零漂移落地，5 个工具封装 Python 脚本，完整工作流通过 agent preset 打包。

---

## 一、RE-Framework 资产清单（要搬什么）

| 资产 | 位置 | 形态 |
|------|------|------|
| 核心协议 | `spec/engineering-framework-v1.md`（490 行） | 语言无关协议文本（铁律 + 模块化接口契约 §1-§9） |
| 16 个方法论技能 | `skills/*/SKILL.md` | 分层技能（L0-L4）+ 执行角色（scout/worker/judge），dot 命名（core./re./recode./swe.） |
| 模块声明 | `skills/modules/{core,re-binary,re-code,swe}.yaml` | 触发表 + 依赖声明 + 卸载保证 |
| 工程脚本 | `scripts/install.py` / `validate_manifest.py` / `merge_index.py` | 部署 / R1-R6 自检 / 索引合并（纯 stdlib + 可选 PyYAML） |
| 预置知识库 | `knowledge-builtin/`（5 条目） | calling-conventions / cpp-abi / common-patterns / assembly-reference / anti-re |
| 产物模板 | `templates/`（7 schema） | class / function / method / xref / index / uncompilable / noise |

## 二、DSH 侧映射（搬到哪里）

| RE-Framework 资产 | DSH 机制 | 落地位置 | 状态 |
|-------------------|----------|----------|------|
| 16 个 SKILL.md | **DSH 技能**（`SKILL.md` + frontmatter，kebab-case 命名 + whenToUse） | `dsh/skills/`（preset 内嵌，`customSkillDirs`） | ✅ 生成完成 |
| ref-maintain（新增，DSH-only） | DSH 技能（维护职责技能化） | `dsh/skills/ref-maintain/` | ✅ 手写完成 |
| validate_manifest.py | **Host 插件工具**（`ref_manifest_validate`） | `dsh/plugins/re-framework-tools.js` | ✅ 完成 |
| install.py | Host 插件工具（`ref_install`） | 同上 | ✅ 完成 |
| merge_index.py | Host 插件工具（`ref_merge_index`） | 同上 | ✅ 完成 |
| 项目骨架（README 第 2 步） | Host 插件工具（`ref_init`） | 同上 | ✅ 完成 |
| 环境就绪检查 | Host 插件工具（`ref_status`） | 同上 | ✅ 完成 |
| Phase 0-3 工作流 + 执行强制链 | **agent preset**（`~/.dsh/.agent-presets/re-framework/`）+ subagent 工具（scout/worker/judge/fan-out 隔离执行） | `dsh/preset/agent.cordis.yml` | ✅ 完成 |
| §1.1 confirm hook（confirmed 仅人类） | DSH 审批/确认机制（ask_user_question / 用户确认） | preset 内工作流约定 | ✅ 完成 |

## 三、关键决策（用户拍板）

1. **技能可见范围：仅 preset 内嵌（2026-08-14 初版）→ v2.1 修订为 用户级全局 + preset 内嵌**——初版担心污染其它会话，但 DSH 的 preset 与工作目录正交、默认 preset 是 standard，preset 内嵌技能在用户日常会话不可见（CoreSwap 被迫手工复制项目级 `.dsh/skills` 为证）。修订：17 个 ref-* 技能装用户级全局（`~/.dsh/skills/`），任何会话按需加载；技能是纯指令、加载不碰工作区外文件，无沙箱问题。
2. **工具分层（v2.1 修订，2026-08-15 挂载修复）**：项目侧工具（status/init/merge_index/install）经 **profile patch**（`<dshHome>/profiles/<profile>/cordis.patch.yml`——唯一用户补丁层；`~/.dsh/cordis.patch.yml` 宿主不读，2026-08-13 Anchorlaw 事故教训）以 **`insert` 形态**挂载、插件在 `<profile>/plugins/re-framework/`——它们操作会话工作区数据 + 只读框架源，实测沙箱（跨工作区读放行、写限工作区）不阻塞；维护工具（manifest_validate，校验框架自身）仅 re-framework preset——只在框架工作区有语义。两处注册名不重叠。多框架共存：前缀命名空间 + `<profile>/plugins/<framework>/` 子目录。**schema 门禁**：挂载前强制 `tests/check_plugin_schema.mjs`（parameters 必须编译后 JSON Schema，扁平 spec 投影给模型无顶层 type → 所有会话崩，2026-08-13 事故教训）。
3. **新增 ref-maintain 维护技能**（16+1，DSH-only，测试豁免漂移检查）。

## 四、移植必须做的适配（坑）

1. **命名冲突**：DSH 技能名必须 kebab-case（`/^[a-z0-9]+(?:-[a-z0-9]+)*$/`），`core.plan` 等带点命名**不合法** → 改名 `core-plan` 等（frontmatter 与目录名同步；正文保留 dot 名作规范引用）。
2. **`runAs: subagent` 语义丢失**：Reasonix 的 frontmatter 字段 DSH 忽略 → 删除 kind/runAs/layer/execution；实际隔离由 DSH subagent/subagent_fork 工具实现（DSH 原生，天然对应 spec §4.1-4.3）。
3. **正文零漂移**：`dsh/scripts/sync_skills.py` 从 `../skills/` 逐字节复制正文（仅 CRLF→LF 归一化）+ 重写 frontmatter；`tests/test_manifest.py` 守护（正文/描述漂移即 FAIL）。比 Anchorlaw 先例（手抄 + 校验）更强：生成即一致。
4. **Python 运行时依赖**：脚本仅 stdlib（`merge_index.py` 需 PyYAML）；插件经 `subprocess` 服务 spawn（本机 python 3.x 可用）。
5. **路径基准**：工具以**会话 cwd**（`exec.agent.session.header.cwd`）为基准解析路径；框架仓库自动探测（向上找 AGENTS.md + scripts/validate_manifest.py 标记），不是 harness 进程 cwd。
6. **§1.1 confirm hook**：confirmed 仅人类授予的纪律保留在 persona/技能正文，judge 只出意见不改 status，靠 agent 遵守 + preset 人格承诺。
7. **知识库/模板不搬**：knowledge-builtin/ 与 templates/ 是项目数据/格式，留在 Reasonix 侧，技能正文按路径引用；ref_init 负责在目标项目生成骨架。

## 五、交付物位置

- 技能适配版：`E:\PYTHON\RE-Framework\dsh\skills\`（17 个，可随时重生成/重装）
- 插件：`E:\PYTHON\RE-Framework\dsh\plugins\re-framework-tools.js`
- preset 源：`E:\PYTHON\RE-Framework\dsh\preset\`（agent.cordis.yml + preset.yml）
- 已安装：`C:\Users\NDark\.dsh\.agent-presets\re-framework\`（install.ps1 生成）
- 自检：`pwsh dsh/scripts/selfcheck.ps1`；正文守护：`python dsh/tests/test_manifest.py`

## 六、后续路线（按需推进）

- **A. 现状档（已完成 ✅）**：preset 内嵌 17 技能 + 5 工具 + Phase 0-3 人格。re-framework preset 会话可用全部能力。
- **B. 实测档**：用真实 RE 任务验证 preset（scout/fan-out/judge 触发点、命令委托模式、merge_index 并行合并），把验证结果记入 SYNC.md 变更日志。
- **C. 深度档**：如需要跨会话能力（全局噪声卡/知识库服务化），可将 ref 能力上升为 Host 插件（进宿主 cordis.yml，影响所有会话）——建议 A/B 跑通后再做。
