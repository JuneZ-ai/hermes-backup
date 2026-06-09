#!/usr/bin/env python3 -u
"""
WSL Batch OCR — used by the ocr-and-documents skill.
Processes scanned PDF pages using local Tesseract 5.5.
Usage: python3 wsl-batch-ocr.py <pages_dir> [output_dir]

Features:
- Writes per-page .txt files for crash resilience
- Auto-skips already-processed pages (resume support)
- Final merge to full_text.txt

Output: <output_dir>/page_NNN.txt (per page) + <output_dir>/full_text.txt (merged)
"""
import pytesseract
from PIL import Image
import os, sys, time

pytesseract.pytesseract.tesseract_cmd = os.path.expanduser(
    '~/.local/tesseract/usr/bin/tesseract')
os.environ.setdefault('TESSDATA_PREFIX',
    os.path.expanduser('~/.local/tesseract/usr/share/tesseract-ocr/5/tessdata'))
os.environ.setdefault('LD_LIBRARY_PATH',
    os.path.expanduser('~/.local/tesseract/usr/lib/x86_64-linux-gnu'))

pages_dir = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) > 2 else pages_dir.replace('_pages', '_ocr')
os.makedirs(output_dir, exist_ok=True)

page_files = sorted([f for f in os.listdir(pages_dir) if f.endswith('.png')])
total = len(page_files)
print(f"[START] {total} pages -> {output_dir}")
sys.stdout.flush()

# Resume support: already-done pages
done = {f.replace('.txt', '.png') for f in os.listdir(output_dir)
        if f.startswith('page_') and f.endswith('.txt') and f != 'full_text.txt'}

for i, fname in enumerate(page_files):
    txt_name = fname.replace('.png', '.txt')
    txt_path = os.path.join(output_dir, txt_name)

    if fname in done:
        print(f"[{i+1}/{total}] SKIP (already done)")
        sys.stdout.flush()
        continue

    t0 = time.time()
    try:
        text = pytesseract.image_to_string(
            Image.open(os.path.join(pages_dir, fname)),
            lang='chi_sim', config='--psm 6')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"===== P{i+1} =====\n{text}\n")
        print(f"[{i+1}/{total}] {len(text)}c ({time.time()-t0:.1f}s)")
    except Exception as e:
        print(f"[ERR][{i+1}] {e}")
    sys.stdout.flush()

# Merge all page files
out = os.path.join(output_dir, 'full_text.txt')
page_txts = sorted(f for f in os.listdir(output_dir)
                   if f.startswith('page_') and f.endswith('.txt'))
with open(out, 'w', encoding='utf-8') as f:
    for pt in page_txts:
        with open(os.path.join(output_dir, pt), 'r') as pf:
            f.write(pf.read())
total_chars = os.path.getsize(out) if os.path.exists(out) else 0
print(f"[DONE] {total_chars} chars -> {out}")
sys.stdout.flush()
