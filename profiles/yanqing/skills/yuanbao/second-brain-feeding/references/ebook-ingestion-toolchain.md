# ebook-ingestion toolchain (absorbed from `ebook-ingestion` skill)

Detailed reference for the ebook2md toolchain used when ingesting epubs/mobi/azw3 into the Obsidian knowledge base.
`second-brain-feeding` §4.1 and §4.4 cover the high-level workflow; this reference adds engine internals, CLI detail, and session-tested pitfalls.

## Toolchain

| Component | Path | Note |
|-----------|------|------|
| CLI wrapper | `/home/hermes/.local/bin/ebook2md` | On PATH |
| Core script | `~/.hermes/profiles/yanqing/scripts/ebook2md.py` | 11KB |
| Python engine | `/usr/bin/python3.14` | NOT the default `python3` — see pitfalls |

Dependencies: `ebooklib` + `mobi` (installed via `--break-system-packages` to Python 3.14).

## CLI usage

```bash
# Convert to markdown (default)
ebook2md book.epub                        # → book.md
ebook2md book.mobi                        # → book.md (mobi/azw3 also works)
ebook2md book.epub -o ~/output/book.md    # custom output path

# Convert to plain text (no markdown syntax)
ebook2md book.epub --format text           # → book.txt

# Preview chapter structure only
ebook2md book.epub --list
```

## Ingestion pattern

```python
# From hermes_tools import terminal, read_file
terminal("ebook2md /path/to/book.epub -o /tmp/book.md")
content = read_file("/tmp/book.md", offset=1, limit=200)
# process in chunks through multiple read_file calls
```

## Pitfalls

- **Default `python3` is broken** — the uv-managed Python 3.11 at `/usr/local/lib/hermes-agent/venv/bin/python3` hangs on any `import` statement (even `import sys`). Always use `/usr/bin/python3.14` explicitly.
- **Nav/TOC filtering** — EPUB files include a `nav.xhtml` that duplicates chapter titles. The script filters it out automatically.
- **mobi/azw3 extraction** — the `mobi` Python library extracts to a temp dir, converts to epub internally, then ebooklib processes it. The temp dir is cleaned up automatically.
- **Large books (100+ chapters)** — allow 10-30 seconds for conversion. Use `--list` first to preview.
- **DRM-protected ebooks** — the toolchain cannot decrypt DRM. Files must be DRM-free.
- **Image-heavy books** — images are referenced as `![alt](src)` in markdown output but not extracted/embedded.
- **Memory pressure** — very large epubs (>50MB) may cause OOM on the WSL host. Use `--format text` (lighter) for those.
