#!/usr/bin/env python3
"""
类型化边审计 — P1+ 工具
========================
六韬知识库 × GBrain 方法论

核心逻辑：扫描 wiki 概念页的「跨模块映射」表格，提取关联类型，
生成结构化类型化边报告 + 跨模块热力矩阵。

GBrain 的 typed edges (works_at / founded / invested_in / attended) 
表明知识图谱的边应该有具体的语义类型，而非泛泛的"相关"。

六韬的跨模块映射表里，`—` 后面的描述就是天然的 edge type。

用法：
  python "typed-edge-scanner.py"                # 输出报告
  python "typed-edge-scanner.py" --verbose       # 逐页展开每条边
  python "typed-edge-scanner.py" --save-report   # 保存到 _工具/ 目录
"""

import os, re, sys
from collections import defaultdict, Counter

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODULES = {
    "六韬智脑": "ZN", "六韬史鉴": "DS", "六韬易哲": "YZ",
    "决断之桥": "QL", "太极双螺旋": "LX", "实战案例": "AL", "wiki": "wiki",
}


def get_wiki_pages(vault_path):
    wiki_dir = os.path.join(vault_path, "wiki")
    return [os.path.join(wiki_dir, f) for f in os.listdir(wiki_dir)
            if f.endswith(".md") and f != "index.md"]


def parse_cross_module_table(content):
    """解析 ## 跨模块映射 表格：| 模块 | [[path|alias]] — 描述 |"""
    edges = []
    tables = re.findall(r'##\s*跨模块映射\s*\n(.*?)(?=\n##|\n---|\Z)', content, re.DOTALL)
    for section in tables:
        for row in section.strip().split('\n'):
            if '|:' in row or '---' in row or ('模块' in row and '关联笔记' in row):
                continue
            cells = [c.strip() for c in row.split('|') if c.strip()]
            if len(cells) < 2:
                continue
            src_mod = cells[0]
            # 修复 wikilink 内部 | 导致 split 切分
            link_cell = '|'.join(cells[1:])
            wl = re.match(r'\[\[([^\]]+?)(?:\|([^\]]*?))?\]\]', link_cell)
            if wl:
                desc = ""
                after = link_cell[wl.end():].strip()
                if '—' in after:
                    desc = after.split('—', 1)[1].strip()
                edges.append((src_mod, wl.group(1), desc))
    return edges


def parse_concept_source(content):
    """解析 ## 概念来源 列表 (无类型描述)"""
    edges = []
    sources = re.findall(r'##\s*概念来源\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    for section in sources:
        for line in section.strip().split('\n'):
            wl = re.match(r'-\s*\[\[([^\]]+?)(?:\|([^\]]*?))?\]\]', line.strip())
            if wl:
                edges.append(('unknown', wl.group(1), ''))
    return edges


def infer_module(path):
    for mod in MODULES:
        if path.startswith(mod + "/"):
            return mod
    return "other"


def classify(desc):
    if not desc:
        return "unclassified"
    patterns = [
        ("provide methodology", ["方法论", "框架", "方法", "模型", "工具", "算法"]),
        ("provide philosophy", ["哲学", "根基", "元代码", "底层", "范式"]),
        ("provide validation", ["历史", "史鉴", "案例", "印证", "来由"]),
        ("provide practice", ["管理", "熵减", "备胎", "战略", "方法论"]),
        ("provide decision", ["决策", "决断", "权衡", "选择"]),
        ("provide lens", ["认知", "视角", "观念", "意识", "思考"]),
        ("provide theory", ["理论", "原理", "规律", "法则"]),
        ("application", ["实践", "应用", "实战", "具体", "操作"]),
        ("complement", ["互补", "配合", "协同", "融合", "结合"]),
        ("tension", ["矛盾", "冲突", "张力", "对立", "悖论"]),
        ("extension", ["延伸", "扩展", "深化", "启发"]),
        ("manifestation", ["具象", "具象化", "映射", "对应"]),
    ]
    for etype, kws in patterns:
        if any(k in desc for k in kws):
            return etype
    return "other"


def main():
    verbose = "--verbose" in sys.argv
    save = "--save-report" in sys.argv

    wiki_pages = get_wiki_pages(VAULT)
    all_edges = []

    for fpath in wiki_pages:
        name = os.path.basename(fpath)[:-3]
        content = open(fpath, 'r', encoding='utf-8').read()
        for src_mod, target, desc in parse_cross_module_table(content) + parse_concept_source(content):
            all_edges.append({
                'src_page': name, 'target': target,
                'src_mod': src_mod, 'tgt_mod': infer_module(target),
                'etype': classify(desc), 'desc': desc,
                'fmt': 'table' if '—' in desc else 'list',
            })

    print(f"🔍 六韬类型化边审计 v1.0")
    print(f"  Wiki 概念页: {len(wiki_pages)}  总边数: {len(all_edges)}")

    # 类型分布
    tc = Counter(e['etype'] for e in all_edges)
    print(f"\n{'='*60}\n📊 边类型分布\n{'='*60}")
    for et, ct in tc.most_common():
        print(f"  {et:25s} {ct:3d} ({ct/len(all_edges)*100:.1f}%)")

    # 跨模块矩阵
    print(f"\n{'='*60}\n📊 跨模块关联 (wiki→目标模块)\n{'='*60}")
    order = [m for m in MODULES if m != "wiki"]
    mat = defaultdict(lambda: defaultdict(int))
    for e in all_edges:
        mat['wiki'][e['tgt_mod']] += 1
    print(f"{'wiki →':>12s} " + "  ".join(f"{m[:6]:>6s}" for m in order))
    print(f"{'wiki':>10s}  " + "  ".join(
        f"{mat['wiki'][m]:>6d}" if mat['wiki'][m] > 0 else "      ·"
        for m in order))

    # 无类型边
    lists = [e for e in all_edges if e['fmt'] == 'list']
    if lists:
        print(f"\n{'='*60}\n⚠️ 无类型边 (概念来源列表): {len(lists)} 条")
        if verbose:
            for e in lists:
                print(f"  {e['src_page']} → {e['target']}")

    # 逐页详情
    if verbose:
        by_pg = defaultdict(list)
        for e in all_edges:
            by_pg[e['src_page']].append(e)
        for pg in sorted(by_pg):
            es = by_pg[pg]
            print(f"\n  {pg} ({len(es)} 条):")
            for e in es:
                d = e['desc'][:40] if e['desc'] else "(无)"
                print(f"    → {e['target']}  [{e['etype']}] {d}")

    if save:
        from datetime import datetime
        now = datetime.now()
        lines = [
            f"# 类型化边报告 ({now.strftime('%Y-%m-%d %H:%M')})",
            f"概念页: {len(wiki_pages)}  边: {len(all_edges)}  类型数: {len(tc)}",
            f"\n## 类型分布",
        ] + [f"- {et}: {ct}" for et, ct in tc.most_common()]
        rp = os.path.join(VAULT, f"_工具/类型边_{now.strftime('%Y%m%d_%H%M')}.md")
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"\n📝 报告: {rp}")

    print(f"\n{'='*60}\n✅ 完成\n{'='*60}")


if __name__ == "__main__":
    main()
