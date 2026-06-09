# Chinese Scanned PDF — OCR Benchmark

**Test document**: 《易经的智慧5》曾仕强 — 289页, 68MB, 纯扫描件(图片式中文PDF)
**Environment**: WSL2, 4GB RAM, 8 cores, Tesseract 5.0 (built into LiteParse v2.0.4)
**Date**: 2026-06-02

## LiteParse v2 + Tesseract (chi_sim+eng)

### Performance

| Metric | Value |
|--------|-------|
| **Total pages** | 289 |
| **Total chars extracted** | 373,046 |
| **Total time** | 420s (7 min) |
| **Per-page average** | ~1.45s/page |
| **Batch size** | 20 pages/batch (OOM avoidance) |
| **OOM behavior** | ✅ Chunked processing avoided OOM |
| **Output size** | 554KB text + 15 JSON files (with bboxes) |

### Batch breakdown

| Batch | Pages | Chars | Time |
|-------|-------|-------|------|
| 1-20 | 20 | 17,401 | 22.0s |
| 21-40 | 20 | 26,983 | 32.3s |
| 41-60 | 20 | 24,693 | 33.9s |
| 61-80 | 20 | 23,557 | 24.4s |
| 81-100 | 20 | 29,260 | 31.1s |
| 101-120 | 20 | 23,288 | 28.9s |
| 121-140 | 20 | 32,044 | 31.4s |
| 141-160 | 20 | 23,033 | 29.2s |
| 161-180 | 20 | 26,382 | 29.6s |
| 181-200 | 20 | 25,706 | 29.5s |
| 201-220 | 20 | 33,794 | 33.5s |
| 221-240 | 20 | 23,845 | 25.3s |
| 241-260 | 20 | 23,132 | 24.8s |
| 261-280 | 20 | 25,117 | 27.9s |
| 281-289 | 9 | 14,811 | 14.8s |

### Quality assessment

| Page type | Accuracy | Notes |
|-----------|----------|-------|
| Copyright/title pages | ~30% | Tesseract garbage on decorative layout |
| Table of contents | ~40% | Line+grid interference |
| Chapter body (clean) | ~60-70% | Recognizable Chinese, many errors |
| Illustrated pages | ~20% | Background interference |
| Small-print annotations | ~10% | Nearly unreadable |

### Sample OCR output vs. original intent

From copyright page:
```
Tesseract: "上 建 : - 科 ' 哲学"
Intended:  "上架建议：哲学"
```

From Tesseract logo page:
```
Tesseract: "SR as = ="
Intended:  garbage — decorative page with logo
```

From chapter body:
```
Tesseract: "俗话"不 胜 正。"人 都 希望 能 够 长 存"
```

## Comparison: pymupdf

| Metric | Value |
|--------|-------|
| **Open time** | 0.22s (289 pages) |
| **Chars extracted** | 0 |
| **Result** | ❌ Pure scanned PDF — zero native text layer |

## Recommendation

| Scenario | Tool | Rationale |
|----------|------|-----------|
| English text PDF | LiteParse (PDFium) or pymupdf | Instant, high quality |
| Chinese scanned book | **PaddleOCR as HTTP server** + LiteParse | ~85-95% accuracy vs ~50-70% for Tesseract |
| Mixed language | PaddleOCR + LiteParse `ocr_server_url` | Best Chinese support |
| Small batch (<50 pages) | LiteParse built-in Tesseract | Zero setup, acceptable quality |
