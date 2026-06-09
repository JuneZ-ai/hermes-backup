#!/usr/bin/env python3
"""
来源重叠扫描 — P0 工具
========================
六韬知识库 × LLM Wiki 方法论

核心逻辑：找到"共享同一来源"的知识条目，自动补上 [[wikilinks]]。
灵感来自 LLM Wiki 四信号关联度模型中的「来源重叠 ×4.0」信号。

工作原理：
  1. 扫描所有 01-信息流/ 文件，提取其中的 [[wikilinks]] → 知识条目
  2. 扫描所有知识条目（六韬智脑/ 六韬史鉴/ 等）的 frontmatter source_note 字段
  3. 合并两种信号，找出"同一来源产生的多个知识条目"
  4. 在未互相引用的条目之间添加 [[wikilinks]]

用法：
  python "来源重叠扫描.py"              # 只输出报告，不修改文件
  python "来源重叠扫描.py" --apply      # 输出报告 + 自动添加 wikilinks
  python "来源重叠扫描.py" --verbose    # 详细输出
"""

import os, re, sys
from collections import defaultdict

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 配置
KNOWLEDGE_MODULES = [
    "六韬智脑", "六韬史鉴", "六韬易哲",
    "决断之桥", "太极双螺旋", "实战案例", "wiki",
]
SOURCE_DIR = "01-信息流"
EXCLUDE_FILES = {"index.md", "00-喂料模板.md"}


def all_md_files(directory, exclude=None):
    result = []
    for root, dirs, files in os.walk(directory):
        if ".obsidian" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                if exclude and f in exclude:
                    continue
                result.append(os.path.join(root, f))
    return result


def parse_frontmatter(content):
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        kv = re.match(r'^\s*([^:]+?)\s*:\s*(.+?)\s*$', line)
        if kv:
            key = kv.group(1).strip()
            val = kv.group(2).strip().strip('"').strip("'")
            fm[key] = val
    return fm


def extract_wikilinks(content):
    links = re.findall(r'\[\[([^\]]+?)(?:\|[^\]]*?)?\]\]', content)
    return [l.strip() for l in links]


def get_source_links_from_infofiles(vault_path):
    source_map = defaultdict(set)
    source_dir = os.path.join(vault_path, SOURCE_DIR)
    for fpath in all_md_files(source_dir, exclude=EXCLUDE_FILES):
        fname = os.path.relpath(fpath, source_dir)
        content = open(fpath, 'r', encoding='utf-8').read()
        wikilinks = extract_wikilinks(content)
        for wl in wikilinks:
            for mod in KNOWLEDGE_MODULES:
                if wl.startswith(mod + "/") or wl.startswith(mod + "\\"):
                    source_map[fname].add(wl)
                    break
    return source_map


def get_source_note_from_knowledge(vault_path):
    sn_map = defaultdict(set)
    for mod in KNOWLEDGE_MODULES:
        mod_dir = os.path.join(vault_path, mod)
        if not os.path.isdir(mod_dir):
            continue
        for fpath in all_md_files(mod_dir):
            content = open(fpath, 'r', encoding='utf-8').read()
            fm = parse_frontmatter(content)
            if 'source_note' in fm:
                sn = fm['source_note'].strip('[] ')
                sn_map[sn].add(os.path.relpath(fpath, vault_path))
    return sn_map


def check_existing_links(vault_path, file_a, file_b):
    def _has_link_to(path, target_name):
        content = open(path, 'r', encoding='utf-8').read()
        pattern = re.escape(target_name)
        return bool(re.search(r'\[\[' + pattern + r'(?:\|[^\]]*?)?\]\]', content))

    path_a = os.path.join(vault_path, file_a) if not file_a.startswith(vault_path) else file_a
    path_b = os.path.join(vault_path, file_b) if not file_b.startswith(vault_path) else file_b

    if not os.path.exists(path_a) or not os.path.exists(path_b):
        return False, False

    name_a = file_a.replace('\\', '/').rsplit('.md', 1)[0]
    name_b = file_b.replace('\\', '/').rsplit('.md', 1)[0]

    return _has_link_to(path_a, name_b), _has_link_to(path_b, name_a)


def add_wikilink(file_path, target_wikilink):
    content = open(file_path, 'r', encoding='utf-8').read()
    pattern = re.escape(target_wikilink)
    if re.search(r'\[\[' + pattern + r'(?:\|[^\]]*?)?\]\]', content):
        return False
    content = content.rstrip() + f"\n\n> **来源重叠关联**：{target_wikilink}\n"
    open(file_path, 'w', encoding='utf-8').write(content)
    return True


def main():
    apply_mode = "--apply" in sys.argv
    verbose = "--verbose" in sys.argv

    if not os.path.isdir(os.path.join(VAULT, SOURCE_DIR)):
        print(f"❌ 未找到 {SOURCE_DIR}/ 目录。请在六韬 Obsidian Vault 目录下运行。")
        print(f"   当前 VAULT = {VAULT}")
        sys.exit(1)

    print(f"🔍 六韬来源重叠扫描器")
    print(f"  Vault: {VAULT}")
    print(f"  模式: {'✏️ APPLY' if apply_mode else '📋 READONLY'}")

    sig_a = get_source_links_from_infofiles(VAULT)
    sig_a_groups = [(src, list(notes)) for src, notes in sig_a.items() if len(notes) >= 2]
    print(f"\n📡 信号 A (01-信息流 → 知识条目): {len(sig_a)} 来源, {len(sig_a_groups)} 重叠")

    sig_b = get_source_note_from_knowledge(VAULT)
    sig_b_groups = [(sn, list(files)) for sn, files in sig_b.items() if len(files) >= 2]
    print(f"📡 信号 B (source_note 重叠): {len(sig_b)} source_note, {len(sig_b_groups)} 重叠")

    all_missing_links = []

    for src_name, notes in sig_a_groups:
        notes_sorted = sorted(notes)
        for i in range(len(notes_sorted)):
            for j in range(i+1, len(notes_sorted)):
                file_a = notes_sorted[i] + ".md"
                file_b = notes_sorted[j] + ".md"
                path_a = os.path.join(VAULT, file_a)
                path_b = os.path.join(VAULT, file_b)
                if not os.path.exists(path_a) or not os.path.exists(path_b):
                    continue
                has_ab, has_ba = check_existing_links(VAULT, file_a, file_b)
                if not has_ab and not has_ba:
                    all_missing_links.append((file_a, file_b, src_name, "信息流信号"))

    for sn_val, files in sig_b_groups:
        files_sorted = sorted(files)
        for i in range(len(files_sorted)):
            for j in range(i+1, len(files_sorted)):
                file_a = files_sorted[i]
                file_b = files_sorted[j]
                has_ab, has_ba = check_existing_links(VAULT, file_a, file_b)
                if not has_ab and not has_ba:
                    all_missing_links.append((file_a, file_b, sn_val, "source_note"))

    print(f"\n{'='*60}")
    print(f"📋 报告: 缺失 {len(all_missing_links)} 个来源重叠链接")
    print(f"{'='*60}")

    for file_a, file_b, source_name, via in sorted(all_missing_links):
        name_a = file_a.replace('\\', '/').rsplit('.md', 1)[0]
        name_b = file_b.replace('\\', '/').rsplit('.md', 1)[0]
        print(f"\n  ├─ {os.path.basename(file_a)}")
        print(f"  ├─ {os.path.basename(file_b)}")
        print(f"  └─ 共同来源: {source_name} ({via})")
        print(f"     → 建议添加: [[{name_a}]] 和 [[{name_b}]]")

    if apply_mode and all_missing_links:
        print(f"\n{'='*60}")
        print(f"✏️  APPLY 模式: 添加缺失链接")
        print(f"{'='*60}")
        added_count = 0
        for file_a, file_b, source_name, via in all_missing_links:
            name_a = file_a.replace('\\', '/').rsplit('.md', 1)[0]
            name_b = file_b.replace('\\', '/').rsplit('.md', 1)[0]
            path_a = os.path.join(VAULT, file_a) if not file_a.startswith(VAULT) else file_a
            path_b = os.path.join(VAULT, file_b) if not file_b.startswith(VAULT) else file_b
            if os.path.exists(path_a):
                if add_wikilink(path_a, f"[[{name_b}]]"):
                    added_count += 1
            if os.path.exists(path_b):
                if add_wikilink(path_b, f"[[{name_a}]]"):
                    added_count += 1
        print(f"\n✅ 共添加 {added_count} 个链接")

    print(f"\n{'='*60}")
    print(f"📊 摘要: 信号A={len(sig_a)} 信号B={len(sig_b)} 缺失={len(all_missing_links)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
