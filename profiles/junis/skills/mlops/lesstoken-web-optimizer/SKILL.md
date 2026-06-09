---
name: lesstoken-web-optimizer
description: LessToken 网页→Markdown 优化器——将网页内容转为干净、LLM 优化的 Markdown，减少 60-80% Token 使用
category: mlops
trigger_keywords: [lesstoken, less token, 网页优化, 省token, web优化, 减少token]
---

# LessToken 网页优化器

> 吸收自 [LessToken](https://github.com/AndyLiu/lesstoken)（MIT 协议，作者 Andy Liu）

## 是什么

LessToken 是一个网页→Markdown 优化工具，专为 LLM 输入场景设计。将原始 HTML 转为干净 Markdown，减少 60-80% Token 消耗。

## 核心理念

```
URL → 抓取 HTML → 提取主体内容 → 移除广告/导航 → 转 Markdown → Token 统计
                                                                   ↓
                                                           节省 60-80% tokens
```

## Python 实现（Hermes 内嵌版）

less-token 工具可组织 Python 代码来实现其核心能力：

```python
import requests
from markdownify import markdownify as md
from bs4 import BeautifulSoup

def fetch_and_optimize(url: str) -> dict:
    """抓取网页并优化为 Markdown"""
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; HermesAgent/1.0)'}
    resp = requests.get(url, headers=headers, timeout=15)
    html = resp.text
    
    # 提取主体内容
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'aside']):
        tag.decompose()
    
    # 找 main/article/content
    main = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda c: c and 'content' in c.lower())
    content = str(main) if main else str(soup.body) if soup.body else html
    
    # 转 Markdown
    markdown = md(content, heading_style='ATX', bullets='-')
    
    # 清理多余空行
    import re
    markdown = re.sub(r'\n{3,}', '\n\n', markdown).strip()
    
    return {
        'markdown': markdown,
        'original_length': len(html),
        'optimized_length': len(markdown),
        'saved_percent': round((1 - len(markdown)/len(html)) * 100, 1) if html else 0
    }
```

## 与 Hermes 现有能力的整合

Hermes 已有 `auxiliary.web_extract`（配置在 config.yaml），但 LessToken 的优化思路可以补充：

| 场景 | 用法 | 效果 |
|:----|:-----|:-----|
| 微信公众号文章提取 | 先 lesstoken 优化再喂 LLM | Token 省 70%+ |
| 技术文档抓取 | 保留代码块和表格 | 信息无损 |
| RAG 喂料 | 干净的 Markdown 源 | 检索质量提升 |

## 使用方式

### 方式一：CLI（如果已安装）

```bash
# 从源码目录安装
cd /path/to/lesstoken
npm install && npm run build && npm link

# 使用
lesstoken https://example.com -o output.md
lesstoken count myfile.md
```

### 方式二：Python 内联

在 hermes_tools 中直接调用 `fetch_and_optimize()` 函数。

### 方式三：作为 wechat-knowledge-ingestion 的前置过滤器

在提取微信公众号文章内容后，先过 LessToken 优化再入库。

## 依赖

- Python: `requests`, `beautifulsoup4`, `markdownify`
- 安装: `pip install requests beautifulsoup4 markdownify`

## 注意事项

1. **数据安全**：LessToken 完全本地运行，不上传数据
2. **Token 估算**：tiktoken 库的模型定价已在 counter.ts 中预置（GPT-4/Claude 等）
3. **主体提取**：优先找 `<main>` / `<article>` / `class="content"`，兜底用 `<body>`
4. **广告过滤**：通过 class/id 关键词（ad-, advertisement, tracking, cookie-banner）移除
