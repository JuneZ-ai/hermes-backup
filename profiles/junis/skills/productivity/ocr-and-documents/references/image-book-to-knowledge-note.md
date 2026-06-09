# Image-based PDF → Knowledge Note Pipeline

End-to-end workflow for processing scanned/image-based books into structured Obsidian knowledge notes.

## When to Use

- PDF has no text layer (text_len=0, images>0 per page with pymupdf)
- Book is Chinese-language (use RapidOCR)
- PDF creator is "UniDoc" or similar image-to-PDF tools

## Pipeline

```
PDF → page check → extract pages(200DPI) → RapidOCR → text cleanup → structure analysis → knowledge note → vault injection → Feishu record
```

### Step 1: Detect text layer

```python
import pymupdf
doc = pymupdf.open("book.pdf")
for i in range(min(3, doc.page_count)):
    t = len(doc[i].get_text().strip())
    imgs = len(doc[i].get_images())
    print(f"Page {i+1}: text={t}, images={imgs}")
# text_len=0 + images>0 = image-based → need OCR
```

### Step 2: Extract pages as images

```python
doc = pymupdf.open("book.pdf")
for i in range(doc.page_count):
    pix = page.get_pixmap(dpi=200)
    pix.save(f"pages/page_{i+1:03d}.png")
```

200 DPI is sufficient for modern printed Chinese text. 300 DPI is slower but better for fine print.

### Step 3: OCR

Using RapidOCR (single instance reusable across pages):

```python
from rapidocr_onnxruntime import RapidOCR
engine = RapidOCR()
for i in range(1, total_pages + 1):
    result, _ = engine(f"pages/page_{i:03d}.png")
    if result:
        texts = [text for box, text, conf in result if conf >= 0.5]
        # Save per-page text
        with open(f"ocr/page_{i:03d}.txt", "w") as f:
            f.write("\n".join(texts))
```

### Step 4: Clean and identify structure

OCR output contains artifacts:
- Page header/footer noise ("网络加速器" "t.tizi8.com" etc.)
- Interleaved advertisement text
- Page numbers mixed with content

Write a cleanup step per PDF type. Common Chinese PDF noise patterns to strip:
- VPN/network accelerator URLs: `t\.(tizi|hi|it)`
- Page number lines
- Repeated publisher/copyright notices

### Step 5: Extract structure

For table of contents:
1. OCR first 25 pages (cover → copyright → preface → TOC)
2. Identify chapter/section hierarchy from TOC
3. Map page numbers back to the original PDF page numbering

### Step 6: Synthesize knowledge note

Based on TOC structure + domain knowledge of the book, create a structured note:

**Frontmatter** (Obsidian-compatible):
```yaml
---
name: Book Title
tags: [domain, category]
aliases: [Alternative names]
created: YYYY-MM-DD
source: /path/to/pdf.pdf
status: processed
---
```

**Content sections**:
- Book positioning (1-2 paragraphs)
- Frame overview (table of parts/sections)
- Per-section summary (key concepts, models, tools table)
- Cross-module connections (how this connects to existing knowledge base)
- Personal reading notes
- Source info

### Step 7: Inject into Obsidian vault

Place in appropriate module directory. Update the module's index.md. Create info feed entry in 01-信息流/.

### Step 8: Record in Feishu (三表同步)

Always sync three tables:
1. 搭建日志 — operation log
2. 每日记录 — daily date entry with lunar calendar
3. 收藏随想录 — book/source record

## Pitfalls

- **Page number mismatch**: The PDF page count and the printed page numbers rarely match. OCR'd TOC references printed page numbers, not PDF page numbers. Look for the actual chapter heading text in OCR output to find the right PDF page.
- **OCR noise pattern varies by publisher**: Beijing University Press PDFs showed "网络加速器" + "t.tizi8.com" as footer noise on every page. Identify the noise pattern from the first OCR'd pages and strip it programmatically.
- **Time estimate**: 382 pages at ~10-30s/page = 1-3 hours for full OCR. Use stepwise approach: TOC only first (10 pages, ~2-3 min), then full book as background task.
- **Partial extraction is better than none**: A TOC + chapter structure note (9-10KB) with key frameworks is immediately useful. Full text extraction can be deferred.
