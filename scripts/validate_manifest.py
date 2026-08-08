#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RE-Framework v2 manifest 校验器（spec §2.5 R1-R5 的实现守护）

用法:
    python scripts/validate_manifest.py [--framework-dir <path>]

校验规则（spec engineering-framework-v1.md §2.5）:
    R1  frontmatter 完整: 每个 SKILL.md 有 name/description/layer/execution（role 为 kind/runAs/layer）
    R2  无孤儿引用: skill 引用的其他 skill 必须存在于 自身模块 ∪ core ∪ Anchorlaw 接口面
    R3  层合法: layer ∈ {L0,L1,L2,L3,L4,role}；role 必须 kind: role + runAs: subagent
    R4  触发表一致: AGENTS.md 注册的每个 skill 有实体文件，实体文件均被模块声明收录
    R5  无跨模块引用: skill 正文引用的其他领域 skill → 违规
    R6  模块声明完整: modules/*.yaml 存在，且其 Skill 清单与实体目录一致
    冒烟: 探测器触发表覆盖各模块关键触发特征（re-binary/re-code/swe）

退出码: 0 = 通过; 1 = 有 error（warnings 不阻塞）
"""
import os
import re
import sys

DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALID_LAYERS = {'L0', 'L1', 'L2', 'L3', 'L4', 'role'}
FILE_EXT_BLACKLIST = ('.yaml', '.txt', '.md', '.json')  # 正则误匹配过滤

# 模块声明文件 → 该模块的 skill 前缀（与 modules/*.yaml 对应）
MODULE_SKILL_PREFIX = {
    'core': 'core.',
    're-binary': 're.',
    're-code': 'recode.',
    'swe': 'swe.',
}


def parse_frontmatter(path):
    """解析 SKILL.md 的 YAML frontmatter（仅支持扁平 key: value）"""
    text = open(path, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---', text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                fm[k.strip()] = v.strip()
    return fm, text


def extract_skill_refs(text):
    """提取正文中 `xxx.yyy` 形式的 skill 引用，过滤文件扩展名误匹配"""
    refs = set(re.findall(r'`([a-z]+\.[a-z]+)`', text))
    return {r for r in refs if not r.endswith(FILE_EXT_BLACKLIST)}


def main(root=DEFAULT_ROOT):
    skills_dir = os.path.join(root, 'skills')
    modules_dir = os.path.join(skills_dir, 'modules')
    agents_path = os.path.join(root, 'AGENTS.md')
    errors, warnings = [], []

    # ── 收集: 实体 skill + 模块声明 ──
    entity_skills = {}   # name -> dict(fm, body, module)
    for entry in os.listdir(skills_dir):
        md = os.path.join(skills_dir, entry, 'SKILL.md')
        if os.path.isfile(md):
            fm, body = parse_frontmatter(md)
            entity_skills[entry] = {'fm': fm, 'body': body, 'module': None}

    module_decls = {}
    for mod in sorted(MODULE_SKILL_PREFIX):
        p = os.path.join(modules_dir, mod + '.yaml')
        if not os.path.isfile(p):
            errors.append(f'R6: 模块声明缺失 modules/{mod}.yaml')
            continue
        text = open(p, encoding='utf-8').read()
        # 从 Skill 清单表提取 skill 名（`xxx.yyy` 反引号）
        declared = {r for r in extract_skill_refs(text) if r.startswith(MODULE_SKILL_PREFIX[mod])}
        module_decls[mod] = declared
        for name in declared:
            if name not in entity_skills:
                errors.append(f'R6: {mod} 声明了不存在的 skill: {name}')
            elif entity_skills[name]['module'] is None:
                entity_skills[name]['module'] = mod
            else:
                errors.append(f'R6: {name} 被多个模块声明: {entity_skills[name]["module"]}, {mod}')

    # 未归属模块声明的实体 → 警告（可能是未注册 skill）
    for name, info in entity_skills.items():
        if info['module'] is None:
            warnings.append(f'R6: {name} 有实体但未被任何模块声明')

    # ── R1/R3: frontmatter 完整 + 层合法 ──
    for name, info in entity_skills.items():
        fm = info['fm']
        if fm.get('name') != name:
            errors.append(f'R1: {name} frontmatter name 不一致: {fm.get("name")!r}')
        if 'description' not in fm:
            errors.append(f'R1: {name} 缺 description')
        layer = fm.get('layer')
        if layer not in VALID_LAYERS:
            errors.append(f'R3: {name} layer 非法: {layer!r}')
        if layer == 'role':
            if fm.get('kind') != 'role':
                errors.append(f'R3: {name} role 必须 kind: role')
            if fm.get('runAs') != 'subagent':
                errors.append(f'R3: {name} role 必须 runAs: subagent')
        else:
            if fm.get('execution') not in ('inline', 'subprocess'):
                errors.append(f'R3: {name} execution 非法: {fm.get("execution")!r}')

    # ── R2/R5: 引用检查（自身模块 ∪ core ∪ anchor.* 允许）──
    for name, info in entity_skills.items():
        for ref in extract_skill_refs(info['body']):
            if ref == name or ref.startswith('anchor.'):
                continue  # 自身 / Anchorlaw 外部接口
            if ref not in entity_skills:
                warnings.append(f'R2: {name} 引用未知 skill: {ref}')
                continue
            if ref.startswith('core.'):
                continue  # core 允许被所有模块引用
            ref_mod = entity_skills[ref]['module']
            if ref_mod and ref_mod != info['module']:
                # R5 豁免：core 模块 role skill（协调角色，如 core.worker 的操作手册路由表）
                # 引用领域 skill 名称 = 提及名称与职责作路由，非拷贝正文/依赖实现（spec §1.6/§2.5）
                if info['module'] == 'core' and info['fm'].get('layer') == 'role':
                    continue
                errors.append(f'R5: {name}({info["module"]}) 跨模块引用 {ref}({ref_mod})')

    # ── R4: AGENTS.md 触发表 ↔ 实体 ──
    if os.path.isfile(agents_path):
        agents_text = open(agents_path, encoding='utf-8').read()
        mentioned = extract_skill_refs(agents_text)
        for m in mentioned:
            if m not in entity_skills and not m.startswith('anchor.'):
                warnings.append(f'R4: AGENTS.md 提到无实体 skill: {m}')
        for name in entity_skills:
            if name not in mentioned:
                warnings.append(f'R4: 实体 {name} 未在 AGENTS.md 触发表注册')
    else:
        errors.append(f'R4: 找不到 AGENTS.md: {agents_path}')

    # ── 冒烟: 探测器触发特征覆盖 ──
    smoke = {
        're-binary': ['dll', 'exe', '汇编', 'IDA', 'Ghidra', 'x64dbg', 'vtable', 'RTTI', 'xref', '脱壳'],
        're-code': ['jar', 'class', '字节码', '反混淆', 'mapping', 'ProGuard', 'R8', 'MCP', 'Fabric', 'Forge', 'mod', 'Minecraft'],
        'swe': ['编写', '重构', '协议设计', '测试', '审查'],
    }
    routes = open(agents_path, encoding='utf-8').read() if os.path.isfile(agents_path) else ''
    for mod, decl in module_decls.items():
        if mod != 'core':
            routes += '\n' + open(os.path.join(modules_dir, mod + '.yaml'), encoding='utf-8').read()
    for label, keys in smoke.items():
        missing = [k for k in keys if k not in routes]
        if missing:
            warnings.append(f'冒烟[{label}]: 触发特征缺失 {missing}')

    # ── 报告 ──
    print(f'=== RE-Framework manifest 校验: {len(errors)} errors, {len(warnings)} warnings ===')
    print(f'skill 实体: {len(entity_skills)} | 模块声明: {sorted(module_decls)}')
    for e in sorted(errors):
        print(f'ERROR: {e}')
    for w in sorted(warnings):
        print(f'WARN : {w}')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    root = sys.argv[sys.argv.index('--framework-dir') + 1] if '--framework-dir' in sys.argv else DEFAULT_ROOT
    main(root)
