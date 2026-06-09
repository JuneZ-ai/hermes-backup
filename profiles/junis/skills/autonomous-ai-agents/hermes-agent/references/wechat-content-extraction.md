# WeChat Content Extraction

> Technique for reading WeChat content via curl.
> Two distinct URL types with different access mechanisms:

| Type | URL Pattern | Access Method |
|------|-------------|---------------|
| **公众号文章** (mp.weixin.qq.com) | `https://mp.weixin.qq.com/s/...` | ✅ Mobile UA + HTML parsing |
| **视频号** (weixin.qq.com/sph) | `https://weixin.qq.com/sph/...` | ❌ Not accessible — SPA + auth required |

### 视频号 (Channels / sph) — Known Limitation

视频号链接 (`weixin.qq.com/sph/...`) 使用纯 SPA 渲染，所有内容（视频、文案、配文）通过需要微信登录认证的 API 动态加载。无法通过 curl/API 等程序化方式获取内容。

替代方案：
1. **用户提供文案** — 手动转录视频文字内容
2. **语音转文字** — 手机录屏后通过语音识别
3. **微信内复制文案** — 如果视频下方有文字配文，直接复制

`wechat-knowledge-ingestion` 技能的触发词已标注"视频号链接（需用户提供文案）"。

---

## 公众号文章提取

### Prerequisites

- curl (works from terminal or Python subprocess)
- Python with `re` for HTML parsing (stdlib)

## Core Technique

WeChat article URLs (https://mp.weixin.qq.com/s/...) serve a verification page to desktop user agents. The actual article content is only rendered when using a mobile user agent.

### Step 1: Download with mobile user agent

```bash
curl -sL -A "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36" \
  "https://mp.weixin.qq.com/s/{ARTICLE_ID}" \
  -o /tmp/wechat_article.html
```

**Key: the `-A` (user-agent) flag is essential.** Without a mobile UA, the server returns a 18KB verify page with no content. With mobile UA, it returns the full 3MB+ rendered page.

### Step 2: Extract metadata from JavaScript variables

WeChat embeds metadata in `<script>` blocks as JS variables before the content. Extract with regex:

```python
import re, datetime

with open("/tmp/wechat_article.html", "r", encoding="utf-8") as f:
    html = f.read()

# Title
title_match = re.search(r'var msg_title\s*=\s*"([^"]+)"', html)
title = title_match.group(1) if title_match else "微信文章"

# Author (公众号 name)
author_match = re.search(r'var nickname\s*=\s*"([^"]+)"', html)
author = author_match.group(1) if author_match else ""

# Description
desc_match = re.search(r'var msg_desc\s*=\s*"([^"]+)"', html)
desc = desc_match.group(1) if desc_match else ""

# Publish timestamp
date_match = re.search(r'var ct\s*=\s*"(\d+)"', html)
if date_match:
    pub_date = datetime.datetime.fromtimestamp(int(date_match.group(1))).strftime("%Y-%m-%d")
else:
    pub_date = ""
```

### Step 3: Extract article body

The article content is in the `rich_media_content` div:

```python
content_match = re.search(
    r'class="rich_media_content[^"]*"[^>]*>(.*?)</div>\s*<(?:script|div)',
    html, re.DOTALL
)
if content_match:
    content_html = content_match.group(1)
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', content_html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#39;', "'", text)
    # Clean whitespace
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = text.strip()
```

## Typical Output

For a ~3000-5000 character article:
- Raw HTML: 3MB+ (includes embedded images, JS, CSS)
- Extracted text: 3000-5000 chars (clean plain text)
- Article metadata: title, author (公众号), publish date, description

## Edge Cases

- **Article is behind subscription gate** — some articles require following the account. The mobile UA usually bypasses this for individual articles but may still show a paywall for some content.
- **Images are not extracted** — the image `<img>` tags contain `data-src` attributes with CDN URLs. These are stripped along with all HTML. If images are needed, preserve `data-src` before stripping tags.
- **Emoji-rich articles** — WeChat articles often contain emoji characters embedded as `<span class="emoji">` or custom image references. These are stripped. The meaningful text content is preserved.
- **Articles with heavy formatting** — tables, code blocks, and blockquotes are stripped of their HTML structure but the text content is preserved.
- **Rate limiting** — WeChat may return a "too many requests" page if you crawl aggressively. Space requests at least a few seconds apart.

## Complete Python Function

```python
import re, requests

def extract_wechat_article(url: str) -> dict:
    mobile_ua = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36"
    
    resp = requests.get(url, headers={"User-Agent": mobile_ua}, timeout=30)
    html = resp.text
    
    # Extract metadata
    title = (re.search(r'var msg_title\s*=\s*"([^"]+)"', html) or [None, ""])[1]
    author = (re.search(r'var nickname\s*=\s*"([^"]+)"', html) or [None, ""])[1]
    desc = (re.search(r'var msg_desc\s*=\s*"([^"]+)"', html) or [None, ""])[1]
    
    # Extract content
    match = re.search(r'class="rich_media_content[^"]*"[^>]*>(.*?)</div>\s*<(?:script|div)', html, re.DOTALL)
    if match:
        text = re.sub(r'<[^>]+>', ' ', match.group(1))
        text = re.sub(r'&[a-z]+;', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
    else:
        text = desc
    
    return {"title": title, "author": author, "content": text, "description": desc}
```

## Integration with Feishu Bitable

After extraction, write the article to a 收藏随想录 (bookmark) table:

```python
import requests

record = {
    "fields": {
        "标题": title,
        "来源链接": url,
        "我的感悟": "",  # Ask user to add
        "金句摘录": "",  # Extract key sentences
        "来源类型": "📱 微信文章",
        "分类": "...",   # Auto-detect or ask
        "收藏日期": int(time.time()) * 1000,
        "评分": "⭐⭐⭐",  # Default, let user update
        "状态": "🔖 已收藏",
    }
}

r = requests.post(
    f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json=record,
    timeout=10
)
```
