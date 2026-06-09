# PDF OCR workflow (absorbed from `pdf-processing` skill)

WSL-specific guidance for handling scanned/image-based PDFs when PyMuPDF text extraction returns near-empty output.
`second-brain-feeding` §4.5 covers the basic PyMuPDF text-extraction path; this reference adds the OCR strategy for when that path fails.

## When to use this path

If `page.get_text("text")` returns <500 chars on a multi-page document, the PDF is scanned/image-based — do NOT output the near-empty result as the final Markdown. Pivot to this OCR workflow.

## Preferred approach: vision_analyze on rendered page images

Render pages with `pymupdf` (`page.get_pixmap(dpi=200)`) and run `vision_analyze` on the images.

```python
import fitz  # pymupdf
doc = fitz.open('book.pdf')
page = doc[0]
pix = page.get_pixmap(dpi=200)
pix.save('/tmp/page-001.png')
```

### Cost-aware strategy

Do NOT run every page through vision. Sample strategically:
- Always extract: cover (page 1), copyright/imprint (page 2), TOC (page 3+ until found), first content page of each chapter
- Build a structural outline from sampled pages
- Only OCR the remaining pages if the full text is actually needed

### If full text is required

Batch pages into groups of 5-10 and parallelize via `delegate_task` or background vision calls.

## Environment constraints (this WSL)

- No sudo access for installing OCR binaries
- `pip install` fails due to externally-managed-environment (PEP 668)
- Do not retry failed pip installs; pivot to vision-based approach immediately
- `/tmp` may have limited space; verify before writing many image files

## Output format

Write Markdown with page markers (`--- Page N ---`), frontmatter with source PDF path, and preserved Q&A/heading structure where possible.

## Pitfalls

- ❌ Do not retry failed pip installations without checking disk space
- ❌ Avoid using `--break-system-packages` unless necessary
- ❌ Never assume `/tmp` has sufficient space; always verify
- ❌ Do not rely on model-free OCR if user expects high accuracy
- ❌ WSL environments often lack sudo and have PEP 668 pip restrictions — do not waste turns trying to install tesseract/easyocr/paddleocr; pivot to vision-based OCR on page images immediately
- ❌ Do not run vision_analyze on every page of a large scanned PDF (e.g. 400+ pages) — costs explode. Sample strategically: cover, copyright, TOC, chapter starts. Only OCR all pages if full text is explicitly required.
- ❌ `page.get_text()` returning a few chars on a 400-page PDF is a strong signal the PDF is scanned/image-based, not a usable text layer — do not output the near-empty result as the final MD.
- ❌ 对扫描件PDF提取了"近似空结果"后不要立即放弃：先用pymupdf转图片（`page.get_pixmap(dpi=200)`），然后用vision_analyze逐页或抽样识别。优先抽样前15-20页建目录框架，全量OCR仅在用户明确要求时进行。
- ❌ 对400页+的扫描件PDF，不要无差别全量vision——成本会爆炸。策略：1）抽样前15-20页建目录框架；2）仅对用户指定章节或高价值页面全量OCR；3）其余页面保留图片待命，在搭建日志中标注"待OCR"状态。
