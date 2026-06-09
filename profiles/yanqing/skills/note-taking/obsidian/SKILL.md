---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Vault Discovery (WSL/Cross-Platform)

When the vault path is unknown, probe likely locations:

```bash
# WSL: check mounted Windows drives
ls /mnt/c/Users/*/Documents/Obsidian*/ 2>/dev/null
ls /mnt/d/Obsidian/ 2>/dev/null
# Linux native
ls ~/Documents/Obsidian*/ 2>/dev/null
ls ~/Obsidian*/ 2>/dev/null
```

Verify by checking for `.obsidian/` directory:
```bash
ls "<path>/.obsidian" 2>/dev/null && echo "Found!"
```

**On WSL**, vaults are often on Windows drives (`/mnt/c/`, `/mnt/d/`). Set `OBSIDIAN_VAULT_PATH` in `.env` after discovering the vault to avoid repeated probes.

## Explore Vault Structure

Before creating notes, list the vault's top-level folders to understand its layout:

- Use `terminal("ls <vault_path>")` to see folder names and structure.
- Common vault conventions: `00-Daily/`, `01-*/` (numbered category folders), `09-MOC/`, `99-Archive/`.
- Check `search_files(target="files", pattern="MOC*", path="<vault_path>")` to find MOC files.
- Check `.obsidian/daily-notes.json` for daily-note template preferences (folder, format, template).

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

## Install a Community Plugin (Manual)

Obsidian community plugins are installed by placing plugin files into `.obsidian/plugins/<plugin-id>/` and enabling them in `community-plugins.json`.

### Manual Installation Steps

```bash
# 1. Create plugin directory
mkdir -p "<vault>/.obsidian/plugins/<plugin-id>"

# 2. Download release assets
cd "<vault>/.obsidian/plugins/<plugin-id>"
curl -sLO "https://github.com/<owner>/<repo>/releases/download/<tag>/main.js"
curl -sLO "https://github.com/<owner>/<repo>/releases/download/<tag>/manifest.json"
curl -sLO "https://github.com/<owner>/<repo>/releases/download/<tag>/styles.css"

# 3. Enable the plugin
echo '["<plugin-id>"]' > "<vault>/.obsidian/community-plugins.json"
```

**Note:** `community-plugins.json` format is a JSON array of enabled plugin IDs. Create it if it doesn't exist. The user must also enable "Community plugins" mode in Obsidian settings first (one-time trust prompt).

### Pre-Requisites Check

Before installing any plugin, check:
- Does it need Node.js or a CLI tool? (e.g. `lark-cli` for Lark Doc / Lark Wiki Sync)
- Is it `isDesktopOnly: true`? (common for plugins that spawn CLI processes)
- What Obsidian `minAppVersion` does it require?

For CLI-dependent plugins, install the CLI first and verify it works before configuring.

### Finding Available Plugins

```bash
# Query the Obsidian community plugin registry
curl -sL "https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-plugins.json" | \
  python3 -c "import json,sys; data=json.load(sys.stdin); \
  [print(f\"{p['id']} | {p['name']} | {p['description'][:100]}\") for p in data if '<filter>' in p.get('description','').lower()]"
```

### Cross-Platform Pitfall: WSL vs Windows

When the agent runs in WSL but the target application (Obsidian) runs on Windows:

- **Plugin files** go in the vault (`/mnt/c/...`), which is fine since WSL can access it
- **CLI tool configs** (e.g. lark-cli) may be written to the WSL HOME path by default. But when Obsidian spawns the CLI on Windows, it reads from the Windows HOME (`C:\Users\<username>\.lark-cli\`)
- **Fix**: Copy/share configs to both locations:
  ```bash
  # WSL home
  mkdir -p /home/hermes/.lark-cli/
  cp config.json /home/hermes/.lark-cli/config.json
  # Windows home (for Obsidian)
  mkdir -p "/mnt/c/Users/<username>/.lark-cli/"
  cp config.json "/mnt/c/Users/<username>/.lark-cli/config.json"
  ```

### lark-cli Setup (for Lark Doc / Lark Wiki Sync)

The Lark Doc and Lark Wiki Sync Obsidian plugins use `lark-cli` (`@larksuite/cli`) as the API transport layer.

```bash
# Install (Node 18+ required)
npm install -g @larksuite/cli

# Fix missing binary (common: postinstall was skipped)
node "$(npm root -g)/@larksuite/cli/scripts/install.js"

# Verify
lark-cli --version  # Expected: "lark-cli version X.X.X"

# Configure with existing Feishu app credentials
echo -n "<app_secret>" | lark-cli config init \
  --app-id "<app_id>" \
  --app-secret-stdin \
  --brand "feishu"

# Config location: ~/.lark-cli/config.json
# IMPORTANT: Also copy to Windows home if using WSL (see cross-platform pitfall above)
```

**Known scopes for Lark operations:**
- Read only: `wiki:space:retrieve wiki:node:retrieve docx:document:readonly drive:drive:readonly`
- Bidirectional: add `docx:document drive:drive` (without `readonly` suffix)

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

### Daily Note Creation

Before creating a daily note, check the vault's existing daily notes for style consistency:

1. Read one or two existing daily notes to learn the format (section headers, emoji conventions, backlink style).
2. Default daily-note format is configured in `.obsidian/daily-notes.json` (e.g. `"format": "YYYY-MM-DD"`, `"folder": "00-Daily"`).
3. Follow the found style: section headers like `## 一、`, emoji markers (✅/❌/📌), cross-reference backlinks (`[[Note Name]]`), and timestamps.
4. Create the note with `write_file` at `<vault_path>/<daily_folder>/<YYYY-MM-DD>.md`.

### User-Specific Vault Layout

This user's second-brain vault follows the **六韬体系** at:
```
C:\Users\18502\Documents\Obsidian Vault
(WSL: /mnt/c/Users/18502/Documents/Obsidian Vault)
```

Vault structure:
| Folder | Purpose |
|--------|---------|
| `六韬易哲/` | Knowledge system: 易经, 中医, 文史哲 books |
| `六韬道史/` | Philosophy foundation + historical evidence |
| `六韬智脑/` | Strategic decision-making system |
| `太极双螺旋/` | Meta-cognition OS |
| `决断之桥/` | Bridges 智脑 and 易哲 |
| `01-信息流/` | Feeding materials (book notes, article extracts) |
| `MOC地图/` | Index files +搭建日志 |
| Root `YYYY-MM-DD.md` | Daily notes at vault root (not in subfolder) |

Key index files: `00-六韬总纲.md` (main index), `MOC地图/第二大脑搭建日志.md` (build log), `六韬易哲/00-知识库总览.md` (易哲 module index).

**Secondary vault** (also has 六韬 content that may need consolidation):
```
D:\Obsidian\异虎事业部知识库
(WSL: /mnt/d/Obsidian/异虎事业部知识库/)
```
This vault contains a separate knowledge base. When user says "异虎事业部知识库里也有六韬易哲的内容", check this vault for content that should be moved to the primary vault.

Before creating notes, ALWAYS read `00-六韬总纲.md` and the relevant module index to understand the existing structure and avoid duplicates.

### Bot Coordination (User's Three-Bot System)

Yanqing (you) owns all feeding. Two other bots handle post-processing:
- **扫地僧** — philosophy: deep analysis, cross-module synthesis
- **黄老邪** — analytics: research frameworks, competitive analysis

Workflow: user sends content → Yanqing feeds → user may ask "让扫地僧看看" or "让黄老邪提炼" → Yanqing delegates

### Knowledge-Base Integration Workflow (喂料)

When adding external content to the vault (skills, articles, references, PDFs):

#### Complete Feed Pipeline
1. **Fetch/Read** — get the source content (PDF, URL, file)
2. **Parse Structure** — identify books/sections/chapters
3. **Extract Metadata** — title, author, publisher, ISBN, page count
4. **Check existing index** (`00-六韬总纲.md`) to avoid duplicates
5. **Classify** — determine vault location:
   - Skills/tools → `01-信息流/`
   - Knowledge books (史/哲/文/医/易) → `六韬易哲/`
   - Strategic frameworks → `六韬智脑/`
   - Philosophy/history → `六韬道史/`
6. **Create notes** — one master index + individual volume notes (see patterns below)
7. **Write diary** → update root `YYYY-MM-DD.md` with summary
8. **Update MOC** → update `00-六韬总纲.md` and module index (`六韬易哲/00-知识库总览.md`)
9. **Cross-reference** → embed `[[wikilinks]]` between related content

#### Document Compression Preferences (User's Style)

When a user asks to compress/simplify a long document:

| Keep | Remove |
|------|--------|
| Latest version params & examples | Older version history |
| Pipeline core workflow | Repeated/redundant section detail |
| Performance/reference data | Knowledge source lists |
| Integration modules | Layout rules & classification dictionaries |
| Platform-specific guides | Version collation details |
| Practical code examples | Upgrade/task logs |

Target size reduction: e.g. ~1000→~300 lines. Keep it readable, not cryptic.

#### PDF Ingestion Pattern (for large multi-document PDFs)

```python
# 1. Check file
import glob, fitz
path = glob.glob("pattern_here")[0]
doc = fitz.open(path)
print(f"Pages: {doc.page_count}, Size: {os.path.getsize(path)/1e6:.1f}MB")

# 2. Find book/section boundaries — sample pages at intervals
for i in range(50, doc.page_count, 100):
    text = doc[i].get_text()
    # look for chapter/section headers

# 3. Verify boundaries with focused scans
for i in range(book_end - 20, book_end + 20):
    text = doc[i].get_text()
    # find empty pages or header transitions

# 4. Extract TOC
# Look for table-of-contents pages near each book's start
```

#### Multi-Volume Master Index Pattern

When a PDF contains multiple books, create:
- **1 master index** — overview table, knowledge system links, cross-references
- **1 note per volume** — full TOC, metadata (author/publisher/year/ISBN), key quotes

All notes link back to the master index via `[[wikilinks]]`.

Example vault layout for a 3-book trilogy:
```
六韬易哲/
├── 文史哲入门三部曲.md              ← master index
├── 中国简史-作者.md                 ← volume 1
├── 中国哲学简史-作者.md             ← volume 2
└── 中国文学简史-作者.md             ← volume 3
```

#### Master Index Note Structure

Frontmatter:
```yaml
---
title: Collection Name
description: Short description
tags: [tag1, tag2, author]
---
```

Body:
- Overview table (book × author × publisher × pages)
- Per-volume summary with embed links
- Knowledge system relevance section
- Cross-reference links

#### Volume Note Structure

Frontmatter:
```yaml
---
title: Book Title
author: Author Name
publisher: Publisher (year)
tags: [relevant tags]
---
```

Body:
- Full TOC (all chapters listed)
- Key quotes / core arguments
- Links to master index and related volumes

#### Diary Entry Style

Follow the existing daily-note style of the vault. Common conventions:
- `# YYYY-MM-DD Title` as heading
- Emoji bullet points for sections: ✅ / ❌ / 📌 / 🏯 / 📰 / 🧠
- Tables for data-heavy content
- Backlinks to all created notes via `[[wikilinks]]`
- Processing timestamp at bottom

#### Dataview for MOC

Example query to auto-list all skills/tools:
```markdown
## 🛠️ 技能工具库

```dataview
TABLE description AS 说明
FROM "07-学习笔记/技术工具"
SORT file.mtime DESC
```
```

For knowledge-system integration, add manual links to the MOC's quick-entry section:
```markdown
- [[Master Index Note]] — description
```

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content. Cross-reference daily notes to new content notes, and content notes back to relevant MOCs.

## Vault Consolidation (Cross-Vault Migration)

When content needs to move between vaults (e.g. from `异虎事业部知识库` to primary vault):

1. **Check both vaults first** — list files in both to avoid re-copying existing content
2. **Copy** to correct location with `cp`
3. **Verify** files exist at destination
4. **Delete** originals from the wrong vault with `rm`
5. **Update indexes** in the target vault — `00-六韬总纲.md`, module index files
6. **Revert ALL changes** in the source vault — delete misplaced files AND undo any MOC/index edits you made there

## Pitfalls

- **Always read an existing daily note before overwriting it.** If the vault already has a `YYYY-MM-DD.md`, read it first and merge new content alongside existing entries. Blind overwriting destroys prior entries.
- **The搭建日志 (`MOC地图/第二大脑搭建日志.md`) is a single accumulating file.** Do NOT overwrite it. Always read first and append or insert new date sections between the header and the oldest existing entry.
- **Verify the vault path before writing.** Read `00-六韬总纲.md` (or the module index) first. If that expected file doesn't exist, you're in the wrong vault.
- **WSL shell can't handle Chinese filenames with `&` or special chars.** Use Python `glob` or `search_files(target="files")` to resolve paths, then pass to file tools. Never pipe Chinese filenames through bash directly.
- **Undo all changes in a wrong vault** — not just misplaced files but also any MOC/index edits. Broken wikilinks in the wrong vault confuse the user later.
- **When moving content between vaults, also check for content that predates the current session.** The异虎 vault's 六韬易哲 folder may contain files (system upgrade logs, upgrade records, philosophical essays) that need consolidation. Always list both vaults' relevant directories.
