# Image Cache OCR Fallback

> When `vision_analyze()` fails because the current model doesn't support images (error: `unknown variant image_url, expected text`), use RapidOCR as a fallback on the cached image files.

## Trigger

Use this workflow when:
- User sends images (screenshots, photos of text) via a messaging platform (Feishu, Telegram, etc.)
- `vision_analyze(image_url=path)` returns a 400 error like `unknown variant image_url, expected text`
- The image is a screenshot of text, not a diagram/photograph that needs visual comprehension

## Workflow

### Step 1: Locate the cached image

Hermes saves user images to:
```
/home/hermes/.hermes/image_cache/img_<hash>.jpg
```

The images are referenced in the conversation turn as `MEDIA:/home/hermes/.hermes/image_cache/img_xxx.jpg`.

### Step 2: Install RapidOCR (if not already)

```bash
pip3 install rapidocr-onnxruntime
```

One-time install ~150MB (ONNX Runtime + models). No sudo, no PyTorch, works on all x86_64 CPUs.

### Step 3: Run OCR on cached images

```python
from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()
result, elapse = engine("/home/hermes/.hermes/image_cache/img_xxx.jpg")

if result:
    for box, text, conf in result:
        if conf >= 0.5:
            print(text)
```

### Step 4: OCR multiple images

Batch process all images in cache:

```python
from rapidocr_onnxruntime import RapidOCR
import glob

engine = RapidOCR()
for fname in sorted(glob.glob("/home/hermes/.hermes/image_cache/img_*.jpg")):
    print(f"===== {fname.split('/')[-1]} =====")
    result, elapse = engine(fname)
    if result:
        for box, text, conf in result:
            if conf >= 0.5:
                print(text)
    print()
```

## Pitfalls

- **First run slow**: Model download happens on first `from rapidocr_onnxruntime import RapidOCR`. Can take 30-60s.
- **Confidence threshold**: Use `conf >= 0.5` for clean results. Low-quality screenshots may need `>= 0.3`.
- **Model compatibility**: The current version installed in the session's venv is the one that works. If switching to a different venv, reinstall.
- **Large images**: Images >1000px height should be chunked (see RapidOCR chunking section in the main SKILL.md).

## Verification

After OCR, you should have readable text of the image content. If text quality is poor:
1. Try lowering confidence threshold to 0.3
2. Check if image is a complex diagram/flowchart (OCR won't capture structure)
3. For hand-drawn text/images, RapidOCR will fail — don't attempt

---

*Added: 2026-05-24*
