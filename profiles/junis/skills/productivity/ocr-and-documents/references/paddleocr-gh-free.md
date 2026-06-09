# PaddleOCR: GitHub-Free Chinese OCR on Screenshots

## Context

Ubuntu 26.04 WSL environment, China network: GitHub/Google CDN blocked, Baidu accessible.
Need to OCR a 929×11822px long screenshot (phone screenshot of a WeChat video channel article).

## Why PaddleOCR over alternatives

| Tool | Verdict | Reason |
|------|---------|--------|
| EasyOCR | ❌ Blocks via GitHub | Model downloads from GitHub releases, connection timed out |
| Tesseract | ❌ Poor quality for modern Chinese | Scanned book OCR OK, but modern UI screenshots with mixed fonts = garbage |
| marker-pdf | ❌ Too heavy | ~3-5GB PyTorch + models, overkill for screenshot |
| PaddleOCR | ✅ Works | Baidu CDN models, ~200MB total, good Chinese recognition |

## Full install sequence

```bash
pip install paddlepaddle paddleocr
```

No extra model download step — models auto-download on first `PaddleOCR()` call.

## The big screenshot problem

The screenshot was 929×11822px — too large for a single PaddleOCR instance:
- Memory: ~600-800MB per instance, system has only 3804MB total, ~1400MB free
- Processing the full image caused OOM kill (exit code 9 or 143)

## Solution: split → OCR → reassemble

```python
# Step 1: Split
from PIL import Image
img = Image.open("screenshot.jpg")
w, h = img.size
chunk_h = h // 6  # ~1970px each
for i in range(6):
    y1 = i * chunk_h
    y2 = (i+1) * chunk_h if i < 5 else h
    img.crop((0, y1, w, y2)).save(f"chunk_{i}.jpg", quality=90)

# Step 2: OCR one by one with explicit GC
import gc
from paddleocr import PaddleOCR
all_text = []
for i in range(6):
    ocr = PaddleOCR(lang='ch')
    result = ocr.ocr(f"chunk_{i}.jpg")
    if result and result[0]:
        texts = [line[1][0] for line in result[0]]
        all_text.extend(texts)
    del ocr
    gc.collect()

# Step 3: Save
with open("result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(all_text))
```

## Version quirks found

- `show_log=False` → `ValueError: Unknown argument: show_log` (remove entirely)
- `use_angle_cls` → DeprecationWarning, use `use_textline_orientation` or omit
- Fresh `PaddleOCR()` per chunk is necessary — reusing the same instance still accumulates memory

## ⚠️ Version compatibility crisis (Ubuntu 26.04 WSL, AVX2-only CPU)

This environment had no working PaddleOCR combination:

| Attempt | Versions | Result | Root cause |
|---------|----------|--------|------------|
| pip install latest | paddlepaddle 3.3.1 + paddleocr 3.5.0 | ❌ `NotImplementedError: ConvertPirAttribute2RuntimeAttribute not support` | PaddlePaddle 3.x static runner bug with certain model architectures |
| pip install "paddlepaddle<3.0" | paddlepaddle 2.6.2 + paddleocr 2.10.0 (after auto-downgrade) | ❌ `SIGILL` / `Illegal instruction` | Prebuilt wheel requires AVX512; i5-8265U (Whiskey Lake) only has AVX2 |
| pip install "paddleocr<3.0" | paddleocr 2.10.0 (was already installed) | ⚠️ also crashes | Same AVX512 issue via paddlepaddle 2.6.2 compat layer |

**CPU details that matter:**
```
Intel(R) Core(TM) i5-8265U CPU @ 1.60GHz
flags: sse sse2 sse3 fma sse4_1 sse4_2 avx avx2
# NO avx512
```

**Verification command:**
```bash
cat /proc/cpuinfo | grep flags | head -1 | grep -o avx512
# Empty = no AVX512 = paddlepaddle 2.x prebuilt wheels will SIGILL
```

**Lesson**: When AVX512 is absent on the CPU, skip PaddleOCR entirely and use **RapidOCR** (`rapidocr-onnxruntime` on PyPI) which uses ONNX Runtime and works on all x86_64 CPUs.

## RapidOCR as fallback

Installed via: `pip install rapidocr-onnxruntime`

- Models auto-download from HuggingFace/GitHub on first run — may be blocked in strict China firewall environments
- Much lighter: ~200-300MB per instance, reusable across chunks
- Faster: ~10-30s per 2000×929px chunk
- No AVX512 requirement — works on any x86_64 CPU

## Processing time estimate

| Chunk size | Time (CPU) |
|-----------|-----------|
| ~2000×929px | ~30-60s |
| 6 chunks total | ~3-6 min |

## Recovery after gateway restart

When the Hermes gateway restarts, background processes are killed:
- `process(action='list')` returns empty
- But **split chunks** survive in `/home/hermes/tmp/chunks/`
- The OCR venv at `/home/hermes/tmp/ocr_venv/` also survives
- Simply re-run the OCR loop over the existing chunks
