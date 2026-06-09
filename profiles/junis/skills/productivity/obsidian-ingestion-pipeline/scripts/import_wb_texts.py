#!/usr/bin/env python3
"""
WB→Vault 典籍批量导入脚本
用法：编辑 BOOKS 列表，指定 src/WB文件名 和 dst/Vault路径，然后运行。
会自动：① 读取WB文件 ② 生成frontmatter ③ 规范化标点 ④ 加返回链接 ⑤ 写入vault
"""
import os, re, hashlib

WB_DIR = r"/mnt/c/Users/18502/.workbuddy/skills/六韬易哲/texts"
VAULT = r"/mnt/c/Users/18502/Documents/Obsidian Vault"

# ===== 编辑区：填入要导入的书籍 =====
BOOKS = [
    # (src_文件名, dst_路径, title, author, [tags], [aliases], category)
    # 示例：
    # ("梅花易数-邵康节.md", "六韬易哲/易经体系/11-梅花易数-邵康节.md",
    #  "梅花易数", "（宋）邵康节 撰", ["六韬易哲", "易经", "梅花易数"], ["观梅数"], "典籍"),
]
# =====

def make_frontmatter(title, author, tags, aliases=None, category="典籍"):
    als = "\n  - ".join(aliases) if aliases else ""
    tags_yaml = "\n  - ".join(tags)
    fm = f"---\ntitle: {title}\nauthor: {author}\ntags:\n  - {tags_yaml}\n"
    if als:
        fm += f"aliases:\n  - {als}\n"
    fm += f"category: {category}\ntype: fulltext\nsource: 六韬易哲技能·WB\n---\n"
    return fm

def fix_punctuation(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = text.replace(',', '，').replace(':', '：').replace(';', '；')
    text = text.replace('!', '！').replace('?', '？')
    text = text.replace('(', '（').replace(')', '）')
    return text

for src_name, dst_path, title, author, tags, aliases, cat in BOOKS:
    src = os.path.join(WB_DIR, src_name)
    if not os.path.exists(src):
        print(f"⚠ 缺失: {src_name}")
        continue
    with open(src, encoding='utf-8') as f:
        content = f.read()
    frontmatter = make_frontmatter(title, author, tags, aliases, cat)
    body = fix_punctuation(content)
    # 跳过源文件的 # 标题行
    lines = body.split('\n')
    start = 0
    for i, ln in enumerate(lines):
        if ln.strip() and not ln.startswith('#') and not ln.startswith('>'):
            start = i
            break
    body = '\n'.join(lines[start:])
    final = frontmatter + body.rstrip() + '\n\n*返回 [[六韬易哲]]*'
    dst_full = os.path.join(VAULT, dst_path)
    os.makedirs(os.path.dirname(dst_full), exist_ok=True)
    with open(dst_full, 'w', encoding='utf-8') as f:
        f.write(final)
    kb = len(final.encode()) // 1024
    print(f"✅ {title} → {dst_path} ({kb}K)")
