#!/usr/bin/env python3
"""
排版清洗工具 · 期刊格式自动校正
用法: python3 format_clean.py <文件路径>
      python3 format_clean.py --batch <目录路径>
      python3 format_clean.py <目录路径> --dry-run  # 预览模式

依赖: Python 3 stdlib (无外部依赖)

覆盖:
  - 中文标点全角化（，。、？！：；「」《》）
  - 英文/数字保持半角
  - 15组常见错别字修正
  - 段落间距修复（标题前后空行、列表前后空行）
  - 行尾空格清理
  - frontmatter 前后格式
"""

import re, sys, os

TYPO_MAP = {
    '罗辑': '逻辑', '年令': '年龄', '即然': '既然',
    '既使': '即使', '苻合': '符合', '暄嚣': '喧嚣',
    '针炙': '针灸', '好象': '好像', '偶而': '偶尔',
    '因该': '应该', '图象': '图像', '部份': '部分',
    '其它': '其他', '証据': '证据', '宮位': '宫位',
    '苻号': '符号', '幹部': '干部',
}

def fix_typos(text):
    for wrong, right in TYPO_MAP.items():
        text = text.replace(wrong, right)
    return text

def fix_punctuation(text):
    # 中文内容中半角→全角标点
    text = re.sub(r'(?<=[\u4e00-\u9fff\uff00-\uffef])[,](?=[\u4e00-\u9fff])', '，', text)
    text = re.sub(r'(?<=[\u4e00-\u9fff])[.](?=[\u4e00-\u9fff])', '。', text)
    text = re.sub(r'(?<=[\u4e00-\u9fff])[!]', '！', text)
    text = re.sub(r'(?<=[\u4e00-\u9fff])[?]', '？', text)
    text = re.sub(r'(?<=[\u4e00-\u9fff]):', '：', text)
    text = re.sub(r':(?=[\u4e00-\u9fff])', '：', text)
    text = re.sub(r'(?<=[\u4e00-\u9fff]),\s*(?=[\u4e00-\u9fff])', '、', text)
    text = text.replace('(', '（').replace(')', '）')
    text = re.sub(r'：\s+', '：', text)
    return text

def fix_spacing(text):
    lines = [line.rstrip() for line in text.split('\n')]
    result = '\n'.join(lines)
    result = re.sub(r'([^\n])\n(#{2,4}\s)', r'\1\n\n\2', result)
    result = re.sub(r'(#{2,4}\s.*)\n([^\n#])', r'\1\n\n\2', result)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result

def fix_frontmatter(text):
    return re.sub(r'(---)\n(?!#)', r'\1\n\n', text)

def clean_file(filepath, dry_run=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    text = original
    text = fix_typos(text)
    text = fix_punctuation(text)
    text = fix_spacing(text)
    text = fix_frontmatter(text)
    if text == original:
        return False, 0
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
    changes = sum(1 for a, b in zip(original.split('\n'), text.split('\n')) if a != b)
    return True, changes

def batch_clean(directory, dry_run=False):
    total_files = total_changes = 0
    for root, dirs, files in os.walk(directory):
        if '.obsidian' in root: continue
        for f in (f for f in files if f.endswith('.md')):
            path = os.path.join(root, f)
            try:
                changed, n = clean_file(path, dry_run)
                if changed:
                    tag = "[DRY]" if dry_run else "[FIX]"
                    print(f"{tag} {path} ({n}行)")
                    total_files += 1
                    total_changes += n
            except Exception as e:
                print(f"[ERR] {path}: {e}")
    print(f"\n总计: {total_files}个文件, {total_changes}行变化")
    return total_files, total_changes

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 format_clean.py <文件/目录> [--dry-run]"); sys.exit(1)
    target, dry = sys.argv[1], '--dry-run' in sys.argv
    (batch_clean if os.path.isdir(target) else lambda t: clean_file(t, dry) and print(
        f"[{'DRY' if dry else 'FIX'}] {t}" if clean_file(t, dry)[0] else f"[OK] 无需修改: {t}")
    )(target)
