#!/usr/bin/env python3
"""LessToken 网页优化器 — Hermes 内嵌版
将网页内容转为干净 Markdown，减少 Token 消耗。

用法:
  python3 lesstoken_optimizer.py https://example.com            # 输出到 stdout
  python3 lesstoken_optimizer.py https://example.com -o out.md  # 保存到文件
  python3 lesstoken_optimizer.py count file.md                 # 统计 Token
"""
import requests
import re
import sys
import json
from urllib.parse import urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from markdownify import markdownify as md
except ImportError:
    md = None


# Token 定价（参照 LessToken counter.ts）
MODEL_PRICING = {
    'gpt-4':          {'input': 0.03, 'output': 0.06},
    'gpt-4-turbo':    {'input': 0.01, 'output': 0.03},
    'gpt-3.5-turbo':  {'input': 0.0005, 'output': 0.0015},
    'claude-3-opus':  {'input': 0.015, 'output': 0.075},
    'claude-3-sonnet':{'input': 0.003, 'output': 0.015},
}


def estimate_tokens(text: str) -> int:
    """估算 token 数（1 token ≈ 4 英文字符，中文约 1.5 字/token）"""
    # 简单估算：英文 4 字符/token，中文 1.5 字/token
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    other_chars = len(text) - chinese_chars
    return chinese_chars * 2 // 3 + other_chars // 4


def fetch_html(url: str, timeout: int = 15) -> str:
    """抓取网页 HTML"""
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_main_content(soup: BeautifulSoup) -> str:
    """提取主体内容"""
    # 优先找语义标签
    for selector in ['main', 'article', '[role="main"]']:
        elem = soup.select_one(selector)
        if elem and len(elem.get_text(strip=True)) > 500:
            return str(elem)

    # 按 class/id 关键词匹配
    for attr in ['class', 'id']:
        for elem in soup.find_all(attrs={attr: lambda v: v and any(
            kw in v.lower() for kw in ['content', 'article', 'post', 'entry', 'main']
        )}):
            if len(elem.get_text(strip=True)) > 500:
                return str(elem)

    # 兜底用 body
    body = soup.find('body')
    return str(body) if body else str(soup)


def optimize(url: str, model: str = 'gpt-4') -> dict:
    """完整优化流程"""
    # 1. 抓取
    raw_html = fetch_html(url)

    # 2. 解析 + 清理
    soup = BeautifulSoup(raw_html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'aside']):
        tag.decompose()

    # 移除广告元素
    for elem in soup.find_all(attrs={
        'class': lambda c: c and any(
            kw in ' '.join(c).lower() for kw in ['ad-', 'advertisement', 'tracking', 'cookie', 'banner']
        ),
        'id': lambda i: i and any(
            kw in i.lower() for kw in ['ad-', 'advertisement', 'tracking', 'cookie', 'banner']
        )
    }):
        elem.decompose()

    # 3. 提取主体
    content_html = extract_main_content(soup) if BeautifulSoup else raw_html

    # 4. 转 Markdown
    if md:
        markdown = md(content_html, heading_style='ATX', bullets='-')
    else:
        markdown = content_html

    # 5. 清理
    markdown = re.sub(r'\n{3,}', '\n\n', markdown).strip()
    markdown = re.sub(r'\[\]\([^)]*\)', '', markdown)  # 空链接
    markdown = re.sub(r'[ \t]+$', '', markdown, flags=re.MULTILINE)  # 行尾空格

    # 6. Token 统计
    original_tokens = estimate_tokens(raw_html)
    optimized_tokens = estimate_tokens(markdown)
    saved = original_tokens - optimized_tokens
    saved_pct = round(saved / original_tokens * 100, 1) if original_tokens > 0 else 0
    pricing = MODEL_PRICING.get(model, MODEL_PRICING['gpt-4'])
    money_saved = (saved / 1000) * pricing['input']

    return {
        'url': url,
        'title': soup.title.string.strip() if soup and soup.title else '',
        'markdown': markdown,
        'stats': {
            'original_tokens': original_tokens,
            'optimized_tokens': optimized_tokens,
            'saved_tokens': saved,
            'saved_percent': saved_pct,
            'model': model,
            'money_saved': round(money_saved, 4),
        }
    }


def count_file(filepath: str, model: str = 'gpt-4') -> dict:
    """统计文件的 Token"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    tokens = estimate_tokens(content)
    pricing = MODEL_PRICING.get(model, MODEL_PRICING['gpt-4'])
    cost = (tokens / 1000) * pricing['input']
    return {'tokens': tokens, 'model': model, 'estimated_cost': round(cost, 4)}


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LessToken 网页优化器')
    parser.add_argument('target', help='URL 或文件路径')
    parser.add_argument('-o', '--output', help='输出文件')
    parser.add_argument('-m', '--model', default='gpt-4', help='Token 统计模型')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')

    subparsers = parser.add_subparsers(dest='command')
    count_parser = subparsers.add_parser('count', help='统计 Token')

    args, _ = parser.parse_known_args()

    try:
        if args.command == 'count':
            # 文件 token 统计
            result = count_file(args.target, args.model)
            if args.json:
                print(json.dumps(result, ensure_ascii=False))
            else:
                print(f"\n📊 Token Count:")
                print(f"   Tokens:  {result['tokens']:,}")
                print(f"   Model:   {result['model']}")
                print(f"   Cost:    ${result['estimated_cost']:.4f}")
        else:
            # URL 优化
            result = optimize(args.target, args.model)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                s = result['stats']
                print(f"\n✔ 优化完成！")
                print(f"   Title:  {result['title']}")
                print(f"\n📊 Token 对比 ({s['model']}):")
                print(f"   原始 HTML:   {s['original_tokens']:,} tokens")
                print(f"   优化后 MD:   {s['optimized_tokens']:,} tokens")
                print(f"   节省:        {s['saved_tokens']:,} tokens ({s['saved_percent']}%)")
                print(f"   节省费用:    ${s['money_saved']:.4f}")
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(result['markdown'])
                    print(f"\n✔ 已保存至 {args.output}")
                else:
                    print(f"\n--- Markdown 输出 ---")
                    print(result['markdown'])

    except Exception as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)
