---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf, liteparse)."
version: 2.4.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) | LiteParse v2 (~15MB) |
|---------|-----------------|---------------------|----------------------|
| **Text-based PDF** | ✅ | ✅ | ✅ (PDFium — char-level positions) |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) | ✅ (built-in Tesseract or HTTP OCR server) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) | ✅ (grid projection preserves layout) |
| **Equations / LaTeX** | ❌ | ✅ | ❌ |
| **Code blocks** | ❌ | ✅ | ❌ |
| **Forms** | ❌ | ✅ | ❌ |
| **Headers/footers removal** | ❌ | ✅ | ❌ |
| **Reading order detection** | ❌ | ✅ | ❌ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) | ✅ (screenshot generation) |
| **Images → text (OCR)** | ❌ | ✅ | ✅ (selective OCR, zero-config Tesseract) |
| **EPUB** | ✅ | ✅ | ❌ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) | ❌ (outputs structured JSON with bboxes) |
| **Spatial layout preservation** | ❌ | ❌ | ✅ (grid projection → JSON bboxes) |
| **Multi-format (DOCX/XLSX/PPTX)** | ❌ | ❌ | ✅ (via LibreOffice auto-conversion) |
| **Rust-native performance** | ❌ | ❌ | ✅ (5-100x faster on small docs) |
| **RAG/Agent workflow friendly** | ❌ (plain text) | ❌ (markdown) | ✅ (JSON with text_items + bbox per page) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) | ~15MB (Rust binary + Python bindings) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) | Instant (PDFium), slower on OCR pages |

**Decision**:
- Use **pymupdf** for plain text extraction from text-based PDFs (smallest, fastest, no deps).
- Use **marker-pdf** when you need OCR, equations, forms, or complex layout → markdown.
- Use **LiteParse v2** when you need **spatial layout preservation** for RAG/agent workflows, multi-format auto-conversion, or JSON output with per-character bounding boxes.

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

---

## LiteParse v2 (spatial-layout-preserving extraction)

> 📘 详细 API 参考、类型定义、性能实测见 `references/liteparse-v2.md`

**Source**: [github.com/run-llama/liteparse](https://github.com/run-llama/liteparse) (LlamaIndex team) · **PyPI**: `liteparse` (v2+)

LiteParse v2 extracts PDF/office documents into **structured JSON with spatial bounding boxes**, preserving the original visual layout via grid projection. Ideal for RAG pipelines and agent workflows where spatial understanding matters (tables, multi-column layouts).

```bash
pip install liteparse
```

> ⚠️ Uses `python3.14` explicitly if your default `python3` is uv-managed and has import issues.

```python
from liteparse import LiteParse

lp = LiteParse(quiet=True, ocr_enabled=True)
result = lp.parse("document.pdf")

result.text                     # Full concatenated text
result.pages[0].text            # Page 1 text
result.pages[0].text_items      # List of TextItem (text + bbox + font info)
```

**TextItem fields**: text, x, y, width, height, font_name, font_size, confidence

**Key config options** (via `LiteParse(...)`):
| Param | Default | Description |
|-------|---------|-------------|
| `ocr_enabled` | True | Enable OCR for scan-type pages |
| `ocr_server_url` | None | HTTP OCR backend URL (EasyOCR/PaddleOCR) |
| `ocr_language` | None | Tesseract language (e.g. "eng+chi_sim") |
| `tessdata_path` | None | Custom Tesseract data path |
| `max_pages` | None | Limit page count |
| `target_pages` | None | Page range string ("1-5,8") |
| `dpi` | None | Output DPI for screenshots |
| `output_format` | None | Output format override |
| `num_workers` | None | Parallel page processing workers |
| `password` | None | PDF password |
| `quiet` | None | Suppress logs |

**Extraction pipeline**:
1. PDF, DOCX, XLSX, PPTX, images all accepted as input
2. Non-PDF formats auto-converted via LibreOffice → PDF
3. PDFium engine extracts native text (char-level positions)
4. Only scan-type pages get OCR (selective, built-in Tesseract or HTTP server)
5. Grid projection maps text to virtual character grid → preserves visual layout
6. Output: JSON with per-page text, text_items (bbox), and page dimensions

**Tesseract data**: If OCR fails with `Error opening data file ... tessdata/eng.traineddata`, install:
```bash
# Linux
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Or point to any existing tessdata dir:
LiteParse(tessdata_path="/path/to/tessdata")
```

**Chunked processing (OOM avoidance on large scanned PDFs)**:
Processing a full 289-page scanned Chinese PDF in one shot OOMs on 4GB RAM. Use `target_pages` to process in batches:
```python
from liteparse import LiteParse

PDF_PATH = "document.pdf"
BATCH_SIZE = 20
TOTAL_PAGES = 289

for batch_start in range(1, TOTAL_PAGES + 1, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE - 1, TOTAL_PAGES)
    lp = LiteParse(quiet=True, ocr_enabled=True,
                   ocr_language="chi_sim+eng",
                   target_pages=f"{batch_start}-{batch_end}")
    result = lp.parse(PDF_PATH)
    with open(f"batch_{batch_start:03d}-{batch_end:03d}.txt", "w") as f:
        f.write(result.text)
    # Also save JSON with bboxes:
    import json
    with open(f"batch_{batch_start:03d}-{batch_end:03d}.json", "w") as f:
        json.dump([{
            "page_num": p.page_num,
            "text": p.text,
            "items": [{"text": i.text, "x": i.x, "y": i.y, "w": i.width, "h": i.height}
                      for i in p.text_items]
        } for p in result.pages], f, ensure_ascii=False, indent=2)
```

**Chinese scanned PDFs — OCR quality notes**:
Tesseract (built into LiteParse) gives ~50-70% accuracy on Chinese scanned book PDFs. It struggles with:
- Decorative/illustrated backgrounds
- Mixed layout columns
- Small-font annotations

For better Chinese OCR, use **PaddleOCR** or **EasyOCR** as an external HTTP server via `ocr_server_url`:
```bash
# Install PaddleOCR
pip install paddleocr
# Start as HTTP server (e.g. port 12345)
paddleocr --port 12345 --lang ch

# Then in LiteParse:
lp = LiteParse(ocr_server_url="http://localhost:12345", ocr_enabled=True)
```

> 📊 实测基准数据见 `references/chinese-ocr-benchmarks.md`

---

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
