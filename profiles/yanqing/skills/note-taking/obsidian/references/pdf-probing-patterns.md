# PDF Probing Patterns for Multi-Book Documents

When a single PDF contains multiple books (common with Chinese "三部曲" collections), use these patterns to efficiently locate book boundaries and extract structure.

## Step 1: Initial Probe

```python
import glob, fitz, os

path = glob.glob("<pattern>")[0]   # use glob for Chinese/special-char filenames
doc = fitz.open(path)
print(f"Pages: {doc.page_count}, Size: {os.path.getsize(path)/1e6:.1f}MB")

# Check first pages for TOC or title info
for i in range(min(8, doc.page_count)):
    text = doc[i].get_text()
    print(f"p{i+1}: {text[:200]}")
```

## Step 2: Find Book Boundaries (Wide Scan)

Sample every 50-100 pages looking for book/section headers:

```python
for i in range(50, doc.page_count, 100):
    text = doc[i].get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()][:3]
    print(f"p{i+1}: {' | '.join(lines)}")
```

Look for markers:
- Book titles like "中国简史", "中国哲学简史"
- First-chapter markers like "第一章", "第一篇"
- Empty pages (page-turn breaks between books)

## Step 3: Verify Boundary (Narrow Scan)

Once you have a suspected boundary range, scan every page:

```python
for i in range(boundary_start, boundary_end):
    text = doc[i].get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        print(f"p{i+1}: {' | '.join(lines[:2])}")
```

Look for:
- Title page of next book (often has author + publisher info)
- Empty pages between books
- TOC pages

## Step 4: Extract Table of Contents

For each book, scan the first 30-60 pages for the TOC section:

```python
for i in range(toc_start, toc_start + 50):
    text = doc[i].get_text()
    if '目录' in text[:100] or '目次' in text[:100] or '第' in text:
        print(f"p{i+1}: {text[:600]}")
```

For books without a dedicated TOC page, look for consistent chapter headers like "第一章", "第一篇", "第一编".

## Step 5: Check Last Page

Always check the last page to confirm the book's end:

```python
text = doc[doc.page_count - 1].get_text()
print(f"Last page: {text[:200]}")
```

## Large-Document Performance

For 40+ MB PDFs on WSL:
- `fitz.open()` is fast (~2s even for 43MB/2000+ pages)
- Text extraction per page is fast (~0.001s)
- Use `execute_code` (sandbox) rather than `terminal` for Python-based probing — avoids shell timeout issues
- Always `doc.close()` when done
