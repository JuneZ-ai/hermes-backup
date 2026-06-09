# PDF Source Discovery: 先扒网页，后走 OCR

## 原则

扫描型PDF（图片版，无文字层）的 OCR 消耗极大（token + GPU + 时间）。
**在处理任何扫描PDF之前，先用最少成本查找文字版。**

优先级链：
```
PDF文件 → 源发现 → 网页文字版 ✅（推荐，几乎零消耗）
                  → 搜索引擎找原文
                  → 找中文镜像站/转载
                  → OCR（最后手段）
```

## 实战方法

### Step 0: 提取 PDF 中的 URL

许多扫描PDF是由 Chrome「打印为PDF」或「保存为网页版」生成的，URL 会嵌入在 PDF 元数据中：

```bash
# 快速检查：从PDF中提取所有URL
strings file.pdf | grep -oP 'https?://[^\s\)"<>]+' | sort -u
```

**实战案例**：华为韬定律论文
- PDF 文件名含「中文网页版」→ 确认是 Chrome 打印
- `strings` 提取到 `eetop.cn`（创芯网）的 URL
- 网页直取 10,451 字论文原文
- 零 OCR、零 token 浪费

### Step 0b: 检查 PDF 标题元数据

PDF 元数据中的标题/作者字段可能包含来源线索：

```bash
# 用 strings 找可读标题（不依赖 pymupdf）
strings file.pdf | grep -aE '(Title|Subject|Creator)' | head -5

# 或用 pymupdf（如果环境支持）
python3 -c "import fitz; d=fitz.open('f.pdf'); print(d.metadata)"
```

中文标题可能是 UTF-16BE 编码的十六进制形式：
```python
import binascii
hex_str = "534E4E3A201C97EC..."  # 从xxd输出中提取
raw = binascii.unhexlify(hex_str)
text = raw.decode('utf-16-be')
print(text)  # 华为"韬(τ)定律"论文全文...
```

### Step 0c: 检查文件名

文件名经常包含线索：
- `XXX-中文网页版.pdf` → 很可能是从网页打印的 → 网页上有原文
- `XXX-print.pdf` → 同上
- `XXX-scanned.pdf` → 可能是扫描本

### 网页提取

拿到 URL 后，用标准 curl 提取：

```bash
curl -sL "$URL" -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" --max-time 30
```

常见的中国技术社区文章容器：
| 网站 | 容器选择器 |
|:----|:-----------|
| eetop.cn (创芯网) | `div.s_con#s_con > div` |
| 微信公众号 | `div#js_content` |
| csdn.net | `article` 或 `div.article_content` |
| 知乎 | `div.RichContent-inner` |

### 什么时候不要做源发现

- PDF 文件本身很小（< 100KB）且文件名不含「网页版」→ 可能是纯文字 PDF，直接 pymupdf
- 用户明确说「这是我扫描的」→ 跳过源发现
- PDF 标题/文件名含 `scan` 或 `ocr` → 直接走 OCR
