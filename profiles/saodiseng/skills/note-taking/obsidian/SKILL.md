---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault, including vault consolidation, duplicate cleanup, and cross-reference management.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, adding wikilinks, and **consolidating duplicate content across the vault**.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## File consolidation / merge workflow

When the user asks to "合并" or "精炼" duplicate files covering the same content, follow this pattern:

### Step 1 — Identify duplicates
Use `search_files` with `target: "content"` to find all files that reference the same book/topic. Also check `_raw_sources/` and `01-信息流/` for original source files.

### Step 2 — Assess each file
Read all candidates to understand what each contains. Determine which is the master file (usually the structured deep-dive in `六韬智脑/ZN-*` or `六韬道史/DS-*`).

### Step 3 — Identify unique content
Compare the master against duplicates. Look for:
- Stories or cases in the duplicate but not in the master
- Applied insights (brand出海, specific frameworks) unique to one file
- Visual summaries (concept maps, ASCII art)
- Different organizational formats that could enrich the master

### Step 4 — Merge into master
- Update frontmatter: bump version, add `merged_from` field documenting what was absorbed
- Patch unique content into appropriate sections of the master
- **⚠️ Pitfall: patch operations on files with repeated `---` section separators** — these often hit "Found N matches" errors. Use a broader anchor (include surrounding heading text or content lines) to make the match unique. Never rely on `---` alone as context.
- **⚠️ Pitfall: duplicate headers after patch** — when you replace text that ends right before a section break, the original file's next heading may survive alongside the one you added. Always verify by reading around the edit site after each patch.

### Step 5 — Update cross-references
Search for all files that wikilink to the duplicate:
```python
from hermes_tools import search_files
search_files(pattern="Target File Name", path="/mnt/c/Users/18502/Documents/Obsidian Vault", file_glob="*.md")
```
Update each referencing file to point to the master instead. Files to check include:
- `MOC地图/第二大脑搭建日志.md`
- `知识库方法论/*.md` (audit reports, grade reports)
- Any index files (`index.md`)
- The master file itself, if it used wikilinks to the duplicate

### Step 6 — Handle the duplicate
Two options depending on how many external links point to it:

- **If few/no external links**: delete the file.
- **If significant external links exist**: convert to a redirect/notice page. Write a short file with:
  - Frontmatter marking it as `type: redirect` and `merged_into: [[Master File]]`
  - A clear notice: "Content merged into [[Master File]] (vX.Y)"
  - This prevents broken wikilinks while directing readers to the correct location.

### Step 7 — Update audit records
If the vault has a `全库入仓分级审计报告.md` or similar reconciliation document, update the relevant section with a `— ✅ 已处理` marker and the new status.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content. When deprecating a file, always preserve wikilink integrity — a broken wikilink on a redirect page is acceptable (it redirects with context), but a broken wikilink in another file that still points to a deleted file is not.
