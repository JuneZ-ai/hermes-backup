# Feishu Gateway Document/PDF File Handling

When a user sends a PDF or other document file in a Feishu DM to a Hermes bot, the gateway handles it through a specific pipeline. Understanding this pipeline is key to building bots that can process uploaded documents.

## Architecture Overview

```
User sends PDF in Feishu DM
        │
        ▼
[Feishu Gateway] _process_inbound_message()
        │
        ▼
[Feishu Adapter] _extract_message_content()
        │
        ├─ _download_feishu_message_resources()
        │   ├─ _download_feishu_image()      ← for images
        │   └─ _download_feishu_message_resource()  ← for files (PDF, doc, etc.)
        │
        ▼
File cached locally via cache_document_from_bytes()
        │
        ▼
MessageEvent created with:
  - media_urls: [cached_path]     ← file path on disk
  - media_types: ["application/pdf"]
  - message_type: DOCUMENT
        │
        ▼
[Gateway Run Loop] _handle_message_with_guards()
        │
        ▼
For DOCUMENT type, injected into agent context as:
"[The user sent a document: 'filename.pdf'.
  The file is saved at: /path/to/file.
  Ask the user what they'd like you to do with it.]"
```

## Key Insight

PDF files are **NOT** auto-converted to images. They are:
1. ✅ Downloaded and cached to disk
2. ✅ File path injected into the agent's system prompt as context
3. ❌ NOT auto-converted to images (only images go through vision pipeline)
4. ❌ NOT auto-extracted for text (only .txt/.md files get content injection)

The bot agent receives the file path and must handle conversion itself.

## Where It Happens

| Step | File | Function/Line |
|------|------|--------------|
| Download file resources | `gateway/platforms/feishu.py` | `_download_feishu_message_resources()` (L3485) |
| Download single file | `gateway/platforms/feishu.py` | `_download_feishu_message_resource()` (L3588) |
| File caching | `gateway/platforms/base.py` | `cache_document_from_bytes()` (L841) |
| Inject document context | `gateway/run.py` | L6984-7024 (DOCUMENT type handling) |
| Supported doc types | `gateway/platforms/base.py` | `SUPPORTED_DOCUMENT_TYPES` (L815) |

## Supported Document Types (SUPPORTED_DOCUMENT_TYPES)

From `gateway/platforms/base.py` L815:
- `.pdf` → `application/pdf`
- `.docx` → `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `.xlsx` → `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `.pptx` → `application/vnd.openxmlformats-officedocument.presentationml.presentation`

## Bot-Agent Pipeline for PDF Processing

Since the bot gets the file path as context, it can process PDFs using pymupdf:

```python
# Step 1: Extract text (for PDFs with text layer)
import pymupdf
doc = pymupdf.open("/path/to/file.pdf")
for page in doc:
    print(page.get_text())

# Step 2: Convert pages to images (for scanned/image-only PDFs)
doc = pymupdf.open("/path/to/file.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(200/72, 200/72))
    pix.save(f"page_{i+1:03d}.png")
```

Then feed the images to the vision model for analysis.

## Helper Script

For profile-based bots (e.g., 燕青/扫地僧/黄老邪), a ready-to-use script:

**`~/.hermes/profiles/<name>/pdf_to_images.py`**

Usage: `python3 pdf_to_images.py /path/to/file.pdf --dpi 200`
Output: PNG images for each page, printed paths at stdout.

## Enabling PDF Processing for a Bot

1. Install pymupdf (already in Hermes venv: `/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/`)
2. Add PDF handling instructions to the bot's SOUL.md or personality prompt
3. Create the pdf_to_images.py helper script
4. Restart the bot's gateway to pick up new personality

Pymupdf is available as `import pymupdf` from the Hermes venv.
