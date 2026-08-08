#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RE-Framework v2 安装/升级/卸载脚本（替代纯复制粘贴部署）

用法:
    python scripts/install.py <target_dir> [--modules core,re-binary,re-code,swe]
                              [--docs] [--uninstall] [--framework-dir <path>]

参数:
    <target_dir>      目标项目目录（框架安装到 <target>/.reasonix/skills/）
    --modules         要安装的模块，逗号分隔。core 必装（自动包含），默认全部
    --docs            同时复制 spec/ 与 templates/ 到目标项目
    --uninstall       按安装清单卸载（只删除本次安装标记过的文件）
    --framework-dir   框架包路径（默认 = 本脚本所在目录的上级）

行为:
    - 复制模块 skills → <target>/.reasonix/skills/<name>/
    - 复制模块声明   → <target>/.reasonix/skills/modules/*.yaml
    - 写版本戳       → <target>/.reasonix/framework.json（version/commit/时间/模块清单）
    - 已安装时检测升级（版本/commit 不一致 → 提示）
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys

FRAMEWORK_VERSION = "2.0.0"
MANDATORY_MODULE = "core"
ALL_MODULES = ("core", "re-binary", "re-code", "swe")


def framework_root(script_dir):
    return os.path.dirname(script_dir)


def git_commit(root):
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                           cwd=root, capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def module_skills(root, module):
    """模块声明文件里收录的 skill 名（与 validate_manifest.py 一致逻辑）"""
    import re
    decl = os.path.join(root, 'skills', 'modules', module + '.yaml')
    if not os.path.isfile(decl):
        return []
    text = open(decl, encoding='utf-8').read()
    refs = set(re.findall(r'`([a-z]+\.[a-z]+)`', text))
    prefix = {'core': 'core.', 're-binary': 're.', 're-code': 'recode.', 'swe': 'swe.'}[module]
    return sorted(r for r in refs if r.startswith(prefix))


def read_stamp(target):
    p = os.path.join(target, '.reasonix', 'framework.json')
    if os.path.isfile(p):
        try:
            return json.load(open(p, encoding='utf-8'))
        except Exception:
            return None
    return None


def write_stamp(target, data):
    d = os.path.join(target, '.reasonix')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'framework.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def install(args):
    root = os.path.abspath(args.framework_dir)
    target = os.path.abspath(args.target_dir)
    modules = [MANDATORY_MODULE] + [m for m in args.modules if m != MANDATORY_MODULE]
    for m in modules:
        if m not in ALL_MODULES:
            sys.exit(f'未知模块: {m}（可选: {", ".join(ALL_MODULES)}）')

    stamp = read_stamp(target)
    if stamp:
        print(f'[检测到已安装] 现有: v{stamp.get("version")} @ {stamp.get("commit", "?")} '
              f'({stamp.get("installed_at", "?")})')
        print(f'[本次安装] v{FRAMEWORK_VERSION} @ {git_commit(root)} '
              f'模块: {",".join(modules)} -> 覆盖升级')
    else:
        print(f'[全新安装] v{FRAMEWORK_VERSION} 模块: {",".join(modules)}')

    installed = {'skills': [], 'modules': [], 'docs': []}
    for mod in modules:
        for skill in module_skills(root, mod):
            src = os.path.join(root, 'skills', skill)
            dst = os.path.join(target, '.reasonix', 'skills', skill)
            if not os.path.isdir(src):
                print(f'  ! 跳过缺失 skill: {skill}')
                continue
            shutil.copytree(src, dst, dirs_exist_ok=True)
            installed['skills'].append(skill)
        # 模块声明（仅安装的模块）
        decl_src = os.path.join(root, 'skills', 'modules', mod + '.yaml')
        decl_dst = os.path.join(target, '.reasonix', 'skills', 'modules', mod + '.yaml')
        os.makedirs(os.path.dirname(decl_dst), exist_ok=True)
        shutil.copy2(decl_src, decl_dst)
        installed['modules'].append(mod)

    if args.docs:
        for d in ('spec', 'templates'):
            src = os.path.join(root, d)
            dst = os.path.join(target, d)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
                installed['docs'].append(d)
        # 索引式入口（AGENTS.md）——已在目标项目的可不覆盖
        agents_dst = os.path.join(target, 'AGENTS.md')
        if not os.path.exists(agents_dst):
            shutil.copy2(os.path.join(root, 'AGENTS.md'), agents_dst)
            installed['docs'].append('AGENTS.md')
        else:
            print('  ! 目标项目已有 AGENTS.md，未覆盖（手动合并触发表）')

    write_stamp(target, {
        'framework': 'RE-Framework',
        'version': FRAMEWORK_VERSION,
        'source_commit': git_commit(root),
        'installed_at': datetime.datetime.now().isoformat(timespec='seconds'),
        'modules': modules,
        'skills': installed['skills'],
    })
    print(f'[完成] 已安装 {len(installed["skills"])} skills + {len(installed["modules"])} 模块声明'
          f'{(" + " + str(len(installed["docs"])) + " 文档") if installed["docs"] else ""}')
    print(f'       位置: {os.path.join(target, ".reasonix", "skills")}')
    print('       建议: 框架包内运行 scripts/validate_manifest.py 保持 manifest 一致')


def uninstall(args):
    target = os.path.abspath(args.target_dir)
    stamp = read_stamp(target)
    if not stamp:
        sys.exit('未找到安装清单（.reasonix/framework.json），无法安全卸载')
    removed = 0
    for skill in stamp.get('skills', []):
        p = os.path.join(target, '.reasonix', 'skills', skill)
        if os.path.isdir(p):
            shutil.rmtree(p)
            removed += 1
    for mod in stamp.get('modules', []):
        p = os.path.join(target, '.reasonix', 'skills', 'modules', mod + '.yaml')
        if os.path.isfile(p):
            os.remove(p)
            removed += 1
    # 清理空 modules 目录
    md = os.path.join(target, '.reasonix', 'skills', 'modules')
    if os.path.isdir(md) and not os.listdir(md):
        os.rmdir(md)
    os.remove(os.path.join(target, '.reasonix', 'framework.json'))
    print(f'[卸载完成] 删除 {removed} 项（.reasonix/framework.json 清单）')
    print('  note: --docs 安装的 spec/templates 未自动删除，手动确认')


def main():
    ap = argparse.ArgumentParser(description='RE-Framework v2 安装器')
    ap.add_argument('target_dir', help='目标项目目录')
    ap.add_argument('--modules', default=','.join(ALL_MODULES),
                    help=f'模块列表（默认全部: {",".join(ALL_MODULES)}）；core 必装自动包含')
    ap.add_argument('--docs', action='store_true', help='同时复制 spec/ + templates/')
    ap.add_argument('--uninstall', action='store_true', help='按清单卸载')
    ap.add_argument('--framework-dir', default=framework_root(os.path.dirname(os.path.abspath(__file__))),
                    help='框架包路径')
    args = ap.parse_args()
    args.modules = [m.strip() for m in args.modules.split(',') if m.strip()]

    if args.uninstall:
        uninstall(args)
    else:
        install(args)


if __name__ == '__main__':
    main()
