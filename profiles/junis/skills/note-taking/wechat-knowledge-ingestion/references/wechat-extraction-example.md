# WeChat Article Extraction — Verified Example (2026-05-24)

## Article
- **URL**: `https://mp.weixin.qq.com/s/CDXPyaHnJ-_ejdmrRO_k8A`
- **Title**: AI进入第二幕：从对话到行动
- **Author**: 地球球长A6
- **HTML size**: ~2.96 MB
- **Extracted text**: ~1,200 chars

## Extraction Method

```python
import re, requests, html as htmlmod

url = "https://mp.weixin.qq.com/s/..."
headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"}
resp = requests.get(url, headers=headers, timeout=20)
html = resp.text

# Meta extraction
meta = {}
og_title = re.search(r'<meta property="og:title" content="([^"]+)"', html)
if og_title: meta["title"] = og_title.group(1)
og_author = re.search(r'<meta property="og:article:author" content="([^"]+)"', html)
if og_author: meta["author"] = og_author.group(1)
pub_time = re.search(r'<em id="publish_time">([^<]+)</em>', html)
if pub_time: meta["publish_time"] = pub_time.group(1)

# Content extraction
m = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
if m:
    text = re.sub(r'<[^>]+>', '', m.group(1))
    text = htmlmod.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
```

## Key Observations
- WeChat HTML is ~3MB, `js_content` div contains the full article body
- Mobile UA is **required** — desktop UA redirects to verification page
- Meta extraction from `og:title` and `og:article:author` works reliably
- `publish_time` is in `em#publish_time`
- If `js_content` regex fails, fall back to Trafilatura
