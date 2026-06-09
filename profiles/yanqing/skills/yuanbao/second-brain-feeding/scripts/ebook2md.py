#!/usr/bin/env python3.14
"""
ebook2md.py — 电子书转 Markdown/纯文本
支持：epub, mobi, azw3 (mobi 格式)
用法：
  python3 ebook2md.py book.epub               → book.md
  python3 ebook2md.py book.epub --format text  → book.txt（纯文本，不含图片引用）
  python3 ebook2md.py book.mobi                → book.md
  python3 ebook2md.py book.epub --output /path/to/output.md
  python3 ebook2md.py book.epub --list         # 只列出章节不转换
"""

import argparse
import os
import sys
import re

def _get_toc_titles(book):
    """Extract chapter titles from EPUB TOC"""
    titles = []
    nav_map = getattr(book, 'toc', [])
    for item in nav_map:
        if isinstance(item, tuple):
            for sub in item:
                if hasattr(sub, 'title') and sub.title:
                    titles.append(sub.title)
        elif hasattr(item, 'title') and item.title:
            titles.append(item.title)
        elif hasattr(item, 'href'):
            titles.append(item.href)
    return titles


def extract_epub(epub_path, output_path, fmt='markdown'):
    """转换 EPUB 到 Markdown 或纯文本"""
    from ebooklib import epub
    from ebooklib.epub import EpubHtml

    book = epub.read_epub(epub_path)
    title = book.get_metadata('DC', 'title')
    title = title[0][0] if title else os.path.basename(epub_path)
    author = book.get_metadata('DC', 'creator')
    author = author[0][0] if author else 'Unknown'

    # Get all document items, skip nav
    items = []
    for item in book.get_items_of_type(9):  # ITEM_DOCUMENT = 9
        if not isinstance(item, EpubHtml):
            continue
        name = item.get_name().lower()
        if 'nav' in name or 'toc' in name or name in ('nav.xhtml', 'nav.html'):
            continue
        items.append(item)

    # Get chapter titles from toc
    toc_titles = _get_toc_titles(book)

    lines = []
    if fmt == 'markdown':
        lines.append(f'# {title}')
        lines.append('')
        lines.append(f'> **作者：** {author}')
        lines.append('')
        lines.append(f'---')
        lines.append('')
    else:
        lines.append(f'【{title}】作者：{author}')
        lines.append('')

    for i, item in enumerate(items):
        chapter_title = toc_titles[i] if i < len(toc_titles) else None
        if not chapter_title:
            content = item.get_body_content().decode('utf-8', errors='replace')
            match = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.DOTALL)
            chapter_title = _html_to_text(match) if match else item.get_name()

        content = item.get_body_content().decode('utf-8', errors='replace')
        text = _epub_html_to_md(content, fmt)

        if fmt == 'markdown':
            lines.append(f'## {chapter_title}')
            lines.append('')
            lines.append(text)
            lines.append('')
            lines.append('---')
            lines.append('')
        else:
            lines.append(f'【{chapter_title}】')
            lines.append(text)
            lines.append('')

    result = '\n'.join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)

    para_count = len([l for l in lines if l.strip() and not l.startswith(('#', '>', '---'))])
    char_count = len(result)
    print(f'✅ 转换完成: {os.path.basename(epub_path)} → {os.path.basename(output_path)}')
    print(f'   章节: {len(items)} | 段落数: ~{para_count} | 字数: {char_count}')
    return output_path


def extract_mobi(mobi_path, output_path, fmt='markdown'):
    import mobi
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    try:
        extract_result = mobi.extract(mobi_path)
        extracted_path = extract_result[0]

        if extracted_path and extracted_path.endswith('.epub'):
            extract_epub(extracted_path, output_path, fmt)
        else:
            with open(extracted_path, 'r', encoding='utf-8', errors='replace') as f:
                html_content = f.read()
            text = _epub_html_to_md(html_content, fmt)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            char_count = len(text)
            print(f'✅ 转换完成: {os.path.basename(mobi_path)} → {os.path.basename(output_path)}')
            print(f'   字数: {char_count}')
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    return output_path


def list_chapters(book_path):
    ext = os.path.splitext(book_path)[1].lower()

    if ext == '.epub':
        from ebooklib import epub
        book = epub.read_epub(book_path)
        title = book.get_metadata('DC', 'title')
        title = title[0][0] if title else os.path.basename(book_path)
        items = list(book.get_items_of_type(9))
        print(f'📖 {title}')
        print(f'   章节数: {len(items)}')
        print()
        for i, item in enumerate(items):
            if hasattr(item, 'get_name'):
                print(f'  [{i+1:3d}] {item.get_name()}')
    elif ext in ('.mobi', '.azw3'):
        import mobi
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        try:
            result = mobi.extract(book_path)
            extracted = result[0]
            if extracted and extracted.endswith('.epub'):
                from ebooklib import epub
                book = epub.read_epub(extracted)
                title = book.get_metadata('DC', 'title')
                title = title[0][0] if title else os.path.basename(book_path)
                items = list(book.get_items_of_type(9))
                print(f'📖 {title}')
                print(f'   章节数: {len(items)}')
                print()
                for i, item in enumerate(items):
                    if hasattr(item, 'get_name'):
                        print(f'  [{i+1:3d}] {item.get_name()}')
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    else:
        print(f'❌ 不支持的文件格式: {ext}')
        sys.exit(1)


def _epub_html_to_md(html_content, fmt='markdown'):
    from html.parser import HTMLParser
    import re

    class MDConverter(HTMLParser):
        def __init__(self, fmt):
            super().__init__()
            self.fmt = fmt
            self.output = []
            self.buf = []
            self.skip_depth = 0
            self.skip_tags = {'script', 'style', 'nav', 'head', 'meta', 'link'}

        def handle_starttag(self, tag, attrs):
            if tag in self.skip_tags:
                self.skip_depth += 1
                return
            if self.skip_depth > 0:
                return
            tag = tag.lower()
            if tag in ('p', 'div'):
                self._flush_buf()
                if self.output and self.output[-1] != '\n\n':
                    self.output.append('\n\n')
            elif tag in ('h1','h2','h3','h4','h5','h6'):
                self._flush_buf()
                level = int(tag[1])
                if self.fmt == 'markdown':
                    self.output.append('\n\n' + '#' * level + ' ')
                else:
                    self.output.append('\n\n【')
            elif tag in ('em', 'i'):
                if self.fmt == 'markdown':
                    self.buf.append('*')
            elif tag in ('strong', 'b'):
                if self.fmt == 'markdown':
                    self.buf.append('**')
            elif tag == 'code':
                if self.fmt == 'markdown':
                    self.buf.append('`')
            elif tag == 'br':
                self.buf.append('\n')
            elif tag == 'li':
                if self.fmt == 'markdown':
                    self.buf.append('\n- ')
                else:
                    self.buf.append('\n- ')
            elif tag == 'img':
                src = dict(attrs).get('src', '')
                alt = dict(attrs).get('alt', '')
                if self.fmt == 'markdown' and src:
                    self.buf.append(f'![{alt}]({src})')
                elif alt:
                    self.buf.append(f'[{alt}]')

        def handle_endtag(self, tag):
            if tag in self.skip_tags:
                self.skip_depth -= 1
                return
            if self.skip_depth > 0:
                return
            tag = tag.lower()
            if tag in ('em', 'i'):
                if self.fmt == 'markdown':
                    self.buf.append('*')
            elif tag in ('strong', 'b'):
                if self.fmt == 'markdown':
                    self.buf.append('**')
            elif tag == 'code':
                if self.fmt == 'markdown':
                    self.buf.append('`')

        def handle_data(self, data):
            if self.skip_depth > 0:
                return
            data = re.sub(r'\s+', ' ', data).strip()
            if data:
                self.buf.append(data)

        def _flush_buf(self):
            text = ''.join(self.buf).strip()
            if text:
                self.output.append(text)
            self.buf = []

        def get_result(self):
            self._flush_buf()
            result = ''.join(self.output)
            result = re.sub(r'\n{3,}', '\n\n', result)
            return result.strip()

    converter = MDConverter(fmt)
    converter.feed(html_content)
    converter.close()
    return converter.get_result()


def _html_to_text(match):
    if match:
        tag = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        return tag
    return ''


def main():
    parser = argparse.ArgumentParser(description='电子书转 Markdown/纯文本')
    parser.add_argument('input', help='输入文件 (.epub / .mobi / .azw3)')
    parser.add_argument('--output', '-o', help='输出路径（默认: 输入文件名.md）')
    parser.add_argument('--format', '-f', choices=['markdown', 'text'], default='markdown',
                        help='输出格式（默认: markdown）')
    parser.add_argument('--list', action='store_true', help='只列出章节，不转换')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f'❌ 文件不存在: {args.input}')
        sys.exit(1)

    ext = os.path.splitext(args.input)[1].lower()

    if args.list:
        list_chapters(args.input)
        return

    if args.output:
        output_path = args.output
    else:
        suffix = '.md' if args.format == 'markdown' else '.txt'
        output_path = os.path.splitext(args.input)[0] + suffix

    if ext == '.epub':
        extract_epub(args.input, output_path, args.format)
    elif ext in ('.mobi', '.azw3'):
        extract_mobi(args.input, output_path, args.format)
    else:
        print(f'❌ 不支持的文件格式: {ext}')
        print('   支持的格式: .epub, .mobi, .azw3')
        sys.exit(1)


if __name__ == '__main__':
    main()
