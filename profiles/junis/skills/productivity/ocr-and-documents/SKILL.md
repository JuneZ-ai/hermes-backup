---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, Tesseract OCR, marker-pdf). Also covers image_cache OCR fallback when vision_analyze fails. Covers WSL-local Tesseract 5.5 (no sudo), marker-pdf for high-accuracy OCR, and pymupdf for text-based PDFs."
version: 2.5.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR, WSL]
    related_skills: [powerpoint, obsidian-ingestion-pipeline, knowledge-synthesis]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 0: PDF Source Discovery (BEFORE any extraction or OCR)

**Always check the PDF for embedded metadata that reveals the original source.** A scanned/image-only PDF may have been created via Chrome "Print to PDF" or "Save as webpage" — these files embed the original URL, title, and source site in the PDF metadata, even though the visual content is rasterized. This step can save orders of magnitude in token/time over OCR.

### Discovery workflow

```bash
# 1. Check for URLs embedded in the raw PDF
strings document.pdf | grep -Eo 'https?://[^"<>)]+' | sort -u

# 2. Decode hex-encoded PDF title
xxd document.pdf | head -20 | grep 'Title' | awk '{print $NF}' | \
  xxd -r -p 2>/dev/null

# 3. Fetch the source URL and extract text
curl -sL "URL" -A "Mozilla/5.0" --max-time 30 | python3 -c "
import sys, re, html
c = sys.stdin.read()
for p in [r'<div class=\"s_con\"[^>]*>(.*?)</div>',
          r'<article[^>]*>(.*?)</article>',
          r'<div class=\"entry-content\"[^>]*>(.*?)</div>',
          r'<td class=\"t_f\"[^>]*>(.*?)</td>']:
    m = re.search(p, c, re.DOTALL)
    if m:
        t = re.sub(r'<[^>]+>', '', m.group(1))
        t = html.unescape(t)
        t = re.sub(r'\s+', ' ', t).strip()
        if len(t) > 200: print(t); break
"
```

### What to look for

| Signal | Meaning | Action |
|--------|---------|--------|
| `https://...` in `strings` output | PDF printed from web | Visit URL, extract HTML |
| `Creator (Mozilla/5.0...Chrome)` | Chrome "Save as PDF" | Search URL from metadata |
| eetop.cn / csdn.net / zhihu.com URLs | Chinese tech site | Direct curl + regex works |
| UTF-16BE hex-encoded title | Chinese article title | Decode via xxd to find source |

### Decision rule
```
PDF arrives → strings/xxd for embedded URLs
├── URLs found → try web extraction FIRST
│   ├── success → done (0 OCR tokens)
│   └── fail → fall back to Step 2
└── no URLs → proceed to Step 1
```

## Step 0: PDF Source Discovery (先扒网页)

Before ANY PDF processing, check if the text exists as a web page. Many "scanned PDFs" are Chrome-printed web pages containing the original URL — extracting from the web is zero-cost vs OCR hell.

**Quick check**: `strings file.pdf | grep -oP 'https?://[^\s\)"<>]+'`

See `references/pdf-source-discovery.md` for full workflow.

## Step 1: Remote URL Available?

If the document has a URL (already known), **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## ⚠️ Chinese Text Encoding Recovery (GBK/GB2312 Mojibake Fix)

**Scenario**: A file claims to be UTF-8 but shows garbled Chinese characters like `Ã« Ôó ¶« Ñ¡ ¼¯` instead of `毛泽东选集`. This is classic mojibake — the original text was in GBK/GB2312, then incorrectly decoded as Latin-1 and re-saved as UTF-8.

**Detection**: Look for single characters separated by spaces, with accented Latin chars (Ã, Ô, Ñ, Õ, µ, ß) where Chinese should be.

**Fix** (encode back to Latin-1, decode as GB18030):

```python
import re

with open('garbled.txt', 'rb') as f:
    raw = f.read()
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]

text = raw.decode('utf-8')
result_bytes = bytearray()
for ch in text:
    try:
        result_bytes.extend(ch.encode('latin-1'))
    except UnicodeEncodeError:
        continue

recovered = result_bytes.decode('gb18030', errors='replace')

# Clean inter-CJK spaces (MinerU artifact)
cleaned = re.sub(
    r'([\u4e00-\u9fff\u3400-\u4dbf])\s+(?=[\u4e00-\u9fff\u3400-\u4dbf])',
    r'\1', recovered
)
cleaned = re.sub(r'\s*([，。、；：？！""''（）【】《》—…·])\s*', r'\1', cleaned)

with open('cleaned.txt', 'w', encoding='utf-8') as f:
    f.write(cleaned)
```

**Why**: GBK maps each Chinese char to 2 bytes (A1-FE range). Misread as Latin-1, those bytes become accented chars. Encoding back to Latin-1 recovers the raw GBK bytes; decoding as GB18030 yields correct Chinese.

**Note**: Always use `gb18030` (superset of GBK/GB2312). Expect minor residual corruption from `errors='replace'`.

---

## WSL Tesseract OCR (no-sudo alternative to marker-pdf)

When marker-pdf's ~5GB footprint is prohibitive, use Tesseract 5.5 installed locally via deb extraction. This is the **Hermes 文渊匠** workflow — designed for WSL environments without sudo access.

### Install Tesseract in WSL (no sudo)

一键安装脚本：`scripts/wsl-tesseract-setup.sh`

它会自动完成：下载 10 个 deb 包 → 提取到 `~/.local/tesseract/` → 下载简体中文语言包 → 创建 `hermes-ocr` 包装脚本。

手动分步操作：
```bash
# 下载 10 个必需的 deb 包
for pkg in tesseract-ocr libtesseract5 libleptonica6 libarchive13t64 \
  libjpeg-turbo8 libgif7 libtiff6 liblerc4 libjbig0 libdeflate0; do
  URL=$(apt-cache show "$pkg" 2>/dev/null | grep "Filename:" | head -1 | \
    awk '{print "http://archive.ubuntu.com/ubuntu/" $2}')
  [ -n "$URL" ] && wget -q "$URL" -O "/tmp/$pkg.deb"
done
mkdir -p ~/.local/tesseract
for deb in /tmp/*.deb; do dpkg --extract "$deb" ~/.local/tesseract/; done
# 中文语言包
wget -q "https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata" \
  -O ~/.local/tesseract/usr/share/tesseract-ocr/5/tessdata/chi_sim.traineddata
```

验证：`export PATH="$HOME/.local/bin:$PATH" && hermes-ocr --list-langs`

### Scan check (text layer vs scanned)

```bash
python3 -c "
import fitz
d = fitz.open('file.pdf')
for i in range(min(3, len(d))):
    t = len(d[i].get_text())
    print(f'Page {i+1}: text_len={t}, images={len(d[i].get_images())}')
# text_len < 50 per page + images > 0 → scanned → OCR needed
"
```

### Batch OCR pipeline

```
PDF → extract images(300DPI) → Tesseract OCR(chi_sim) → clean text → structured output
```

Uses `scripts/wsl-batch-ocr.py` (unbuffered, checkpoint-enabled). Invoke:

```python
terminal("python3 -u scripts/wsl-batch-ocr.py pages_dir/ output_dir/",
         background=True, notify_on_complete=True)
```

### Progress monitoring

由于 `terminal(background=True)` 输出被 `bash -lic` 管道缓冲，无法实时查看 `python3 -u` 脚本的进度。两种方案：

**方案 A**（推荐）：使用 Shell 循环直接调用 `hermes-ocr`，每页实时输出
**方案 B**：检查 OS 进程和中间文件判断进度
```bash
# 检查 tesseract 是否在跑
ps aux | grep tesseract | grep -v grep
# 检查已处理页数（shell循环方式）
ls output/page_*.txt 2>/dev/null | wc -l
```

### 断点续跑

Shell 循环天然支持中断恢复——跳过已有输出的页面：
```bash
for i in $(seq 1 58); do
  f=$(printf "page_%03d" $i)
  [ -f "$OUTDIR/${f}.txt" ] && continue  # 跳过已处理的
  hermes-ocr "$PAGEDIR/${f}.png" stdout -l chi_sim --psm 6 > "$OUTDIR/${f}.txt" 2>/dev/null
  echo "[$i] done"
done
```

### 处理时间预期

- 300 DPI: 首页 ~15-30s（Tesseract 初始化），后续页 ~5-15s
- 200 DPI: 快 2-3x，但 OCR 质量略有下降（现代文档可接受）
- 58 页总耗时: ~5-12 min（300DPI）
- 规律：第 1-5 页最慢，后面会加速（Tesseract 缓存优化）

Pitfalls:
- **最隐蔽的坑**：`python3 -u` + `sys.stdout.flush()` 在 `terminal(background=true)` 中输出仍被缓冲！日志只在进程结束后一次性可见。所以 Shell 循环方式（每页存独立 .txt 文件）比 Python 后台脚本更可靠。
- Set TESSDATA_PREFIX and LD_LIBRARY_PATH in every shell call
- ~2-5s/page at 300 DPI; 58p → 3-5min, 117p → 6-10min (现代文档可用200DPI加速)
- Memory: process one page at a time (~1GB free sufficient)
- No sudo, no apt, no pip system packages needed

### Shell 循环方式（推荐，可实时查看进度）

替代 Python 后台脚本，直接在 terminal() 中运行 shell 循环：

```bash
export LD_LIBRARY_PATH="/home/hermes/.local/tesseract/usr/lib/x86_64-linux-gnu"
export TESSDATA_PREFIX="/home/hermes/.local/tesseract/usr/share/tesseract-ocr/5/tessdata"
export PATH="/home/hermes/.local/bin:$PATH"
OUTDIR=/home/hermes/output
for i in $(seq 1 58); do
  f=$(printf "page_%03d" $i)
  hermes-ocr "$PAGEDIR/${f}.png" stdout -l chi_sim --psm 6 > "$OUTDIR/${f}.txt" 2>/dev/null
  echo "[$i/58] $(wc -c < "$OUTDIR/${f}.txt")chars"
done
cat "$OUTDIR"/page_*.txt > "$OUTDIR/full_text.txt"
```

优势：每页实时显示进度，被中断后检查已处理的 .txt 文件即可继续。

### 知识库入库（OCR 后）

OCR 完成后，清洗文本 → 结构化 Markdown → 写入 Obsidian Vault：

创建两个层级（**知识库双条目模式**）：
1. **主条目**：完整结构化 Markdown（含表格、层级、标签、来源引用），7-10KB
2. **速查版**：核心框架提炼 1-2KB，含 `[[双向链接]]` 交叉引用主条目和其他知识库文档
   - 速查版标签应与六韬智脑等知识体系对齐，便于交叉检索

```bash
# 输出路径约定
/home/hermes/.hermes/cache/documents/<project>_pages/   # 临时图片
/home/hermes/.hermes/cache/documents/<project>_ocr/      # OCR结果
# 知识库目标
/mnt/c/Users/18502/Documents/Obsidian Vault/决断之桥/知识库/
```

创建两个层级：
1. **主条目**：完整结构化 Markdown（含表格、层级、标签、来源）
2. **速查版**：核心框架提炼，含 `[[双向链接]]` 交叉引用

**完整端到端流程**（图片PDF→OCR→知识笔记→Obsidian→飞书）见 `references/image-book-to-knowledge-note.md`。

## PaddleOCR (Chinese OCR, GitHub-free)

When GitHub is unreachable (e.g. Ubuntu 26.04 behind China firewall), use PaddleOCR — models download from Baidu's CDN (accessible within China).

### Install & Version Compatibility

```bash
pip install paddlepaddle paddleocr
```

No PyTorch dependency — uses Baidu's PaddlePaddle framework (~200MB total with models, vs marker-pdf ~3-5GB).

**⚠️ Version traps (Ubuntu 26.04 WSL environment):**

| Issue | Versions | Error | Fix |
|-------|----------|-------|-----|
| API mismatch | paddlepaddle 3.3.1 + paddleocr 3.5.0 | `ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]` | Downgrade to paddlepaddle 2.6.2 + paddleocr 2.10.0 (see below) |
| SIGILL / AVX512 | paddlepaddle 2.6.2 + paddleocr 2.10.0 | `SIGILL: Illegal instruction` — prebuilt wheel requires AVX512, but Intel i5-8265U (Whiskey Lake, 2018) only has AVX2 | Switch to **RapidOCR** (ONNX Runtime) or try `pip install paddlepaddle==2.5.2` (older build without AVX512) |

**Verification before committing to PaddleOCR:**
```bash
# Check CPU AVX512 support
cat /proc/cpuinfo | grep flags | head -1 | grep -o avx512
# Empty output = no AVX512 = paddlepaddle 2.6.x will SIGILL
```

When AVX512 is absent, **skip PaddleOCR entirely** and use RapidOCR (below).

### Chinese OCR on a single image

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='ch')
result = ocr.ocr("image.jpg")

if result and result[0]:
    for line in result[0]:
        bbox, (text, conf) = line
        if conf >= 0.35:  # filter garbage
            print(f"{' [LOW:{conf:.2f}]' if conf < 0.5 else ''} {text}")
```

### Processing a giant screenshot (OOM prevention)

For images >900px height (e.g. 929×11822 phone screenshot):

1. **Split first** — PIL crop into ~2000px-high chunks
2. **Process one chunk at a time** — new PaddleOCR instance per chunk
3. **Free memory between chunks** — `del ocr; gc.collect()`

```python
from PIL import Image
from paddleocr import PaddleOCR
import gc

# Split
img = Image.open("screenshot.jpg")
w, h = img.size
n = h // 2000 + 1
for i in range(n):
    y1, y2 = i * 2000, min((i+1) * 2000, h)
    img.crop((0, y1, w, y2)).save(f"chunk_{i}.jpg")

# OCR one at a time
for i in range(n):
    ocr = PaddleOCR(lang='ch')
    result = ocr.ocr(f"chunk_{i}.jpg")
    # ... process result ...
    del ocr
    gc.collect()
```

**Pitfalls**:
- This PaddleOCR version does NOT support `show_log=False` — drop that parameter
- `use_angle_cls` is deprecated, use `use_textline_orientation` instead (or just omit)
- Memory: ~600-800MB per PaddleOCR instance. With ~1400MB free, process one chunk at a time
- Processing speed: ~30-60s per chunk (CPU), each chunk ~2000×900px
- Do NOT reassign ocr without `del ocr; gc.collect()` — memory accumulates and OOM kills the process
- **AVX512**: paddlepaddle 2.6.x prebuilt binaries crash (SIGILL) on CPUs without AVX512 — check `/proc/cpuinfo | grep avx512` first. If absent, use RapidOCR instead.

## RapidOCR (ONNX Runtime, no Paddle dependency)

When PaddleOCR is unavailable (AVX512 issue, version bugs), use RapidOCR — lightweight Chinese OCR based on ONNX Runtime. Works on all x86_64 CPUs, no special instruction set requirements.

### Install

```bash
pip install rapidocr-onnxruntime
```

Notably lighter than PaddleOCR: ~150MB vs ~300MB with models.

### Chinese OCR on a single image

```python
from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()
result, elapse = engine("image.jpg")

if result:
    for box, text, conf in result:
        if conf >= 0.5:
            tag = "" if conf >= 0.7 else f" [LOW:{conf:.2f}]"
            print(f"{tag} {text}")
```

### Processing a giant screenshot (OOM prevention)

Same chunking approach as PaddleOCR:

```python
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

# Split
img = Image.open("screenshot.jpg")
w, h = img.size
n = h // 2000 + 1
for i in range(n):
    y1, y2 = i * 2000, min((i+1) * 2000, h)
    img.crop((0, y1, w, y2)).save(f"chunk_{i}.jpg")

# OCR
engine = RapidOCR()
all_text = []
for i in range(n):
    result, _ = engine(f"chunk_{i}.jpg")
    if result:
        texts = [text for box, text, conf in result if conf >= 0.5]
        all_text.extend(texts)
        print(f"  chunk {i}: {len(texts)} lines")

full = "\n".join(all_text)
with open("result.txt", "w", encoding="utf-8") as f:
    f.write(full)
```

**Pitfalls**:
- `RapidOCR()` instance can be reused across chunks (unlike PaddleOCR) — lighter memory footprint
- If models fail to download on first run, set `model_download=True` or pre-download them
- Processing speed: ~10-30s per chunk (~2000×900px) — faster than PaddleOCR
- Supports `text_score` filtering — use >= 0.5 for clean results, >= 0.3 for inclusive

## Decision: PaddleOCR vs RapidOCR

| Factor | PaddleOCR | RapidOCR |
|--------|-----------|----------|
| AVX512 requirement | ✅ 3.x version only; 2.x wheels SIGILL on AVX2 CPUs | ✅ All x86_64 |
| Network | Baidu CDN (China-accessible) | HuggingFace/GitHub (blocked in China) |
| Memory per run | ~600-800MB, must `del ocr; gc.collect()` per chunk | ~200-300MB, reusable instance |
| Speed | ~30-60s/chunk | ~10-30s/chunk |
| Accuracy | Excellent for Chinese UI screenshots | Good for modern Chinese text |

**Rule of thumb**: If CPU has AVX512 → try PaddleOCR first. If no AVX512 → use RapidOCR (models download from PyPI — works in restricted envs).

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
- **Image cache OCR fallback**: When `vision_analyze()` fails (model doesn't support images), use RapidOCR on cached images. See `references/image-cache-ocr-fallback.md`.

## ⚠️ Python Version Path Conflict (--break-system-packages)

**Scenario**: Running `pip3 install --break-system-packages <pkg>` succeeds but the module can't be imported because it landed in a different Python version's site-packages.

**Root cause**: The system has multiple Python versions (3.11 in the venv, 3.14 as the system `pip3` default). The `pip3` command may map to a different Python than the active `python3`. The `--break-system-packages` flag bypasses PEP 668 but does NOT change which Python the package installs to.

**Fix**: 
```bash
# Check where pip installs: look at the "Location" line
pip3 show <pkg> 2>/dev/null | grep "Location"

# If the location shows a different Python version (e.g. python3.14), 
# the package is in the wrong place. Install directly via the venv's pip:
/usr/local/lib/hermes-agent/venv/bin/python3 -m pip install <pkg>

# If venv pip has permission errors (Errno 13), install to a writable target:
/usr/local/lib/hermes-agent/venv/bin/python3 -m pip install \
  --target=/home/hermes/.local/hermes_extras <pkg>

# Then set PYTHONPATH before importing:
export PYTHONPATH="/home/hermes/.local/hermes_extras:$PYTHONPATH"
python3 -c "import <pkg>; print('<pkg> OK')"
```

**Prevention**: Always check `which python3` and `python3 --version` before installing. When in doubt, use the venv's python directly: `$(which python3) -m pip install`.
