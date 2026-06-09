#!/usr/bin/env python3
"""
图谱洞察扫描 — P1 工具
========================
六韬知识库 × LLM Wiki 方法论

核心逻辑：自动检测知识图谱的结构问题，生成可操作的织网建议。

检测项：
  1. 孤立页面 — degree ≤ N，与知识库失联
  2. 稀疏社区 — 模块内交叉链接密度过低
  3. 枢纽节点 — 链接密集，维系多个知识领域的关键页面
  4. 桥接节点 — 跨模块连接数 ≥ 3 的页面
  5. 源素材孤岛 — 01-信息流 中 status:processed 但无反向链接的素材
  6. 潜力链接 — 共享标签但无直接链接的页面对

用法：
  python "图谱洞察扫描.py"                    # 输出报告
  python "图谱洞察扫描.py" --save-report     # 保存完整报告到 _工具/
  python "图谱洞察扫描.py" --min-degree=2    # 自定义孤立判定阈值
"""

import os, re, sys
from collections import defaultdict, Counter

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KNOWLEDGE_MODULES = [
    "六韬智脑", "六韬史鉴", "六韬易哲",
    "决断之桥", "太极双螺旋", "实战案例", "wiki",
]
EXCLUDE_DIRS = {".obsidian", ".git", "_raw_sources", "_协作", "Lark", "WorkBuddy", "MOC地图"}


def all_md_files(directory, exclude_dirs=None):
    files = []
    for root, dirs, fnames in os.walk(directory):
        if any(ed in root.split(os.sep) for ed in (exclude_dirs or set())):
            continue
        for f in fnames:
            if f.endswith(".md") and not f.startswith("_"):
                files.append(os.path.join(root, f))
    return files


def parse_wikilinks(content):
    return [l.strip() for l in re.findall(r'\[\[([^\]]+?)(?:\|[^\]]*?)?\]\]', content)]


def parse_frontmatter(content):
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        kv = re.match(r'^\s*([^:]+?)\s*:\s*(.+?)\s*$', line)
        if kv:
            fm[kv.group(1).strip()] = kv.group(2).strip().strip('"').strip("'")
    return fm


def get_module(node):
    parts = node.split('/')
    return parts[0] if len(parts) > 1 else "root"


def main():
    min_degree = 2
    save_report = "--save-report" in sys.argv
    for arg in sys.argv:
        if arg.startswith("--min-degree="):
            min_degree = int(arg.split("=")[1])

    print(f"🔍 六韬图谱洞察扫描 v1.0")
    print(f"  Vault: {VAULT}  孤立阈值: ≤ {min_degree}")

    all_files = all_md_files(VAULT, EXCLUDE_DIRS)
    nodes, edges = {}, set()
    for fpath in all_files:
        rel = os.path.relpath(fpath, VAULT).replace('\\', '/')[:-3]
        content = open(fpath, 'r', encoding='utf-8').read()
        nodes[rel] = content
        for wl in parse_wikilinks(content):
            edges.add((rel, wl))

    print(f"  节点: {len(nodes)}  边: {len(edges)}")

    out_deg = Counter()
    in_deg = Counter()
    out_links, in_links = defaultdict(set), defaultdict(set)
    for src, tgt in edges:
        out_deg[src] += 1
        in_deg[tgt] += 1
        out_links[src].add(tgt)
        in_links[tgt].add(src)

    total_deg = {n: out_deg[n] + in_deg[n] for n in nodes}

    module_pages = defaultdict(set)
    for n in nodes:
        module_pages[get_module(n)].add(n)

    # 检测 1: 孤立页面
    isolated = [(n, total_deg[n], out_deg[n], in_deg[n], get_module(n))
                for n in nodes if total_deg[n] <= min_degree
                and get_module(n) in KNOWLEDGE_MODULES
                and not n.endswith("/index")]
    isolated.sort(key=lambda x: x[1])

    print(f"\n{'='*60}")
    print(f"📡 孤立页面 (degree ≤ {min_degree}): {len(isolated)}")
    for n, td, outd, ind, mod in isolated[:30]:
        print(f"  [{td}] {mod} → {n.split('/')[-1]}  (出={outd} 入={ind})")
    if len(isolated) > 30:
        print(f"  ... 及 {len(isolated)-30} 更多")

    # 检测 2: 模块密度
    print(f"\n{'='*60}\n📡 模块内链接密度\n{'='*60}")
    for mod in KNOWLEDGE_MODULES:
        mod_dir = os.path.join(VAULT, mod)
        if not os.path.isdir(mod_dir):
            continue
        mp = [n for n in nodes if get_module(n) == mod]
        if len(mp) < 3:
            continue
        ie = sum(1 for s, t in edges if s in mp and t in mp)
        density = ie / (len(mp) * (len(mp) - 1)) if len(mp) > 1 else 0
        status = "✅" if density > 0.15 else ("⚠️" if density > 0.08 else "❌")
        print(f"  {status} {mod}: {len(mp)}页, {ie}边, 密度={density:.1%}")

    # 检测 3: 枢纽节点
    print(f"\n{'='*60}\n📡 枢纽节点 (deg ≥ 15)")
    hubs = [(n, out_deg[n], in_deg[n], total_deg[n], get_module(n))
            for n in nodes if total_deg[n] >= 15 and get_module(n) in KNOWLEDGE_MODULES]
    hubs.sort(key=lambda x: x[3], reverse=True)
    for n, outd, ind, td, mod in hubs[:20]:
        print(f"  [deg={td}] {mod} → {n.split('/')[-1]}  (出={outd} 入={ind})")

    # 检测 4: 桥接节点
    print(f"\n{'='*60}\n📡 桥接节点 (连接 3+ 模块)")
    bridge_nodes = []
    for n in nodes:
        out_mods = {get_module(t) for t in out_links[n]}
        in_mods = {get_module(s) for s in in_links[n]}
        all_mods = out_mods | in_mods
        if len(all_mods) >= 3 and get_module(n) in KNOWLEDGE_MODULES:
            bridge_nodes.append((n, len(all_mods), sorted(all_mods)))
    bridge_nodes.sort(key=lambda x: x[1], reverse=True)
    for n, nmod, mods in bridge_nodes[:20]:
        print(f"  [{nmod}模] {n.split('/')[-1]} → {mods}")

    # 检测 5: 源素材孤岛
    print(f"\n{'='*60}\n📡 源素材孤岛 (processed 但无人引用)")
    orphan_sources = []
    src_dir = os.path.join(VAULT, "01-信息流")
    if os.path.isdir(src_dir):
        for fname in os.listdir(src_dir):
            if not fname.endswith(".md") or fname in ("index.md", "00-喂料模板.md"):
                continue
            content = open(os.path.join(src_dir, fname), 'r', encoding='utf-8').read()
            fm = parse_frontmatter(content)
            if fm.get('status') == 'processed':
                ref = f"01-信息流/{fname[:-3]}"
                if not any(tgt == ref for _, tgt in edges):
                    orphan_sources.append((fname, fm.get('title', fname)))
    if orphan_sources:
        print(f"  ⚠️ {len(orphan_sources)} 个: {', '.join(s[0] for s in orphan_sources[:10])}")
    else:
        print(f"  ✅ 无")

    # 检测 6: 潜力链接
    print(f"\n{'='*60}\n📡 潜力链接 (共享标签但无直接链接)")
    tag_pages = defaultdict(list)
    for n, content in nodes.items():
        if get_module(n) not in KNOWLEDGE_MODULES:
            continue
        fm = parse_frontmatter(content)
        if 'tags' in fm:
            tags_found = re.findall(r'\s*-\s*(.+?)(?:\n|$)', fm['tags'])
            for t in tags_found:
                t = t.strip()
                if t and t not in ("wiki", "cross-module", "六韬标准", "schema", "规范"):
                    tag_pages[t].append(n)
    pairs = defaultdict(list)
    for tag, pages in tag_pages.items():
        if len(pages) < 2:
            continue
        for i in range(len(pages)):
            for j in range(i+1, len(pages)):
                a, b = pages[i], pages[j]
                if a != b and ((a, b) not in edges and (b, a) not in edges):
                    pairs[tuple(sorted([a, b]))].append(tag)
    sorted_pairs = sorted(pairs.items(), key=lambda x: len(x[1]), reverse=True)
    for (a, b), tags in sorted_pairs[:15]:
        print(f"  🏷️ {len(tags)}标签: {a.split('/')[-1]} ↔ {b.split('/')[-1]} ({', '.join(tags[:3])}...)")
    if len(sorted_pairs) > 15:
        print(f"  ... 及 {len(sorted_pairs)-15} 更多")

    # 建议
    print(f"\n{'='*60}\n🎯 织网建议\n{'='*60}")
    if isolated:
        tops = ", ".join(f"`{n.split('/')[-1]}`" for n, *_ in isolated[:5])
        print(f"\n1. 孤立页面：{len(isolated)} 页应对 ≤ {min_degree}。重点: {tops}")
    if hubs:
        print(f"\n2. 枢纽节点：{len(hubs)} 个维系全局的高链接页面")
    if orphan_sources:
        print(f"\n3. 源素材回溯：{len(orphan_sources)} 个已处理素材无人引用，运行 source-overlap-scanner.py")
    if sorted_pairs:
        tops = ", ".join(f"`{a.split('/')[-1]}`↔`{b.split('/')[-1]}`" for (a, b), _ in sorted_pairs[:3])
        print(f"\n4. 潜力链接：基于标签，{len(sorted_pairs)} 对建议加连。{tops}")

    if save_report:
        from datetime import datetime
        report = [
            f"# 图谱洞察报告 ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
            f"节点: {len(nodes)}  边: {len(edges)}  孤立: {len(isolated)}  枢纽: {len(hubs)}  桥接: {len(bridge_nodes)}",
        ]
        rpath = os.path.join(VAULT, f"_工具/图谱报告_{datetime.now().strftime('%Y%m%d_%H%M')}.md")
        with open(rpath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        print(f"\n📝 报告已保存: {rpath}")

    print(f"\n{'='*60}\n✅ 完成\n{'='*60}")


if __name__ == "__main__":
    main()
