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

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

### Alias (display text) syntax

Use `[[Note Name|Display Text]]` to show different text than the note title:
- `[[六韬智脑/07-韩非子精要|韩非子精要]]` renders as "韩非子精要" but links to the full path.
- Avoid `[[../relative/path]]` in notes meant to be moved; prefer full module-qualified paths.

### ⚠️ `read_file` → `write_file` corruption pitfall

**NEVER do this in `execute_code`:**
```python
from hermes_tools import read_file, write_file
content = read_file(path)["content"]   # ← returns "1|...\n2|...\n3|..." format
write_file(path, content)              # ← writes line numbers into the file!
```

`read_file` returns content with `LINE_NUM|CONTENT` format (every line starts with `N|`, e.g. `1|---\n2|title:...`). Writing this back verbatim via `write_file` corrupts the file — each line now starts with a line number embedded as actual file content.

**Safe alternatives:**
1. **Use `patch`** for targeted edits instead of read-write cycles.
2. **Use `terminal`** with `cp` for large file copies (texts/ to vault, etc.).
3. **If you must use `execute_code`**, strip the prefix before writing back:
   ```python
   import re
   content = read_file(path)["content"]
   lines = content.split('\n')
   cleaned = [re.sub(r'^\s*\d+\|', '', line) for line in lines]
   write_file(path, '\n'.join(cleaned))
   ```
4. **Read raw file content** via terminal (Python open) in execute_code instead:
   ```python
   with open(path, 'r', encoding='utf-8') as f:
       content = f.read()  # pure content, no line numbers
   ```

This pitfall is especially dangerous for large files (100KB+), where a single `write_file` can corrupt thousands of lines before you notice.

### Table escaping pitfall

When `[[link|display]]` appears inside a **markdown table**, the `|` between link and display text conflicts with the table's column-separator `|`. Obsidian requires it to be escaped as `\\|`:

```markdown
| 史鉴笔记 | 关联智脑笔记 |
|---------|-------------|
| [[01-道德经精要]] | [[六韬智脑/02-战略哲学与灰度治理\\|灰度治理]]（无为而治） |
```

**⚠️ patch 工具陷阱**：使用 `patch` 或 `skill_manage(action='patch')` 修改含 `\\|` 转义的表格时，模糊匹配容易将 `\\|` 变成 `\\\\|`（双反斜线）或引入多余的 `|` 列前缀。**修复方法**：用新字符串完整替换整行（含相邻上下文的稳定锚点），或用 `write_file` 重写整个表格区，或用 execute_code 的 Python 脚本做 `str.replace()`。

### Cross-module links

Link across modules by prefixing the relative path:
- `[[六韬智脑/03-CEO决策控制台]]` — links from any module
- `[[MOC地图/决断一体索引]]` — links to cross-module index

Avoid `[[../relative/path]]` in notes meant to be moved; prefer full module-qualified paths.

## Frontmatter Standardization

Use a single YAML list format for frontmatter across the vault. Do NOT mix `tags: [a, b]` (inline array), `tags: #a #b` (hash tags), and `tags:\n  - a` (YAML list) — pick one and apply consistently. **YAML list format is preferred** because it survives round-trip editing and supports hierarchical tag naming.

### Standard field set

```yaml
---
title: 笔记标题
tags:
  - 模块名        # first-level: which module owns this
  - 主题/分类      # second-level: content category
created: 2026-05-21   # YYYY-MM-DD, required on all notes
---
```

Optional fields per note type:
| Note type | Extra fields |
|-----------|-------------|
| Hub/MOC | `aliases: [别名1, 别名2]`, `status: evergreen`, `version: vX.X`, `updated:` |
| Deep-dive | `type: deep-dive`, `status: growing`, `version: vX.X` |
| Information-flow material | `type: article\|book\|report`, `creator:`, `source:`, `status: raw\|processed` |

### Tag naming conventions

- YAML list format: `tags:\n  - 六韬智脑\n  - 决策框架`, never `tags: [六韬智脑, 决策框架]` or `tags: #六韬智脑 #决策框架`
- Module tags first: `六韬智脑`, `太极双螺旋`, `六韬易哲`, `决断之桥`, `六韬史鉴`
- Hierarchy with hyphens: `六韬智脑-吴恩达`
- Chinese primary, English only for fixed terms: `framework`, `dashboard`, `MOC`
- Status tags follow a controlled set: `seed → seedling → growing → evergreen` (for module notes), `raw → processed` (for inbox)

### ⚠️ YAML `#` comment pitfall

Never write `tags: #太极双螺旋 #元认知` in YAML frontmatter. The `#` character is a YAML comment marker — the parser discards everything after it, resulting in an empty tags field. Always use list format instead:

```yaml
# ✅ CORRECT
tags:
  - 太极双螺旋
  - 元认知

# ❌ WRONG — YAML treats # as comment, tags become empty
tags: #太极双螺旋 #元认知
```

### Vault maintenance: batch frontmatter normalization

When existing notes have mixed frontmatter formats (inline arrays, hash tags, Chinese field names), use a Python script to normalize them in bulk:

1. Walk all `.md` files, skip `.trash/` and `.obsidian/`.
2. For each file with a YAML frontmatter block (`---\n...\n---\n`):
   - Convert `tags: [a, b]` → `tags:\n  - a\n  - b`
   - Convert `tags: #a #b` → `tags:\n  - a\n  - b`  (watch for YAML comment issue above)
   - Convert Chinese field names (`创建日期` → `created`, `标签` → `tags`, `标题` → `title`, `关联` → `links`)
   - Add missing `created` field from `date` if present
   - Normalize `aliases: a, b` (comma string) → `aliases:\n  - a\n  - b`
3. Write back only if changed.
4. Re-scan to verify: every note's frontmatter parses as valid YAML and has `title` + `tags` in list format.

The `patch` tool can leave orphaned list items when the matched context is misaligned — prefer `write_file` for complete frontmatter rewrites, or verify the result after every 5-10 files.

### 📊 Module status table in root MOC

After normalizing frontmatter, add a metadata table to the root MOC (`00-六韬总纲.md`) showing each module's health:

```markdown
## 📊 模块状态一览
| 模块 | 笔记数 | Deep-Dive | 状态 |
|:----|:------:|:----------|:----:|
| ☯️ 太极双螺旋 | 5/5 | 法治的细节·罗翔 v2.0 | 🟢 evergreen |
```

Status legend: 🟢 evergreen (stable) · 🟡 growing (being expanded) · 🔴 seed (just started)

## Knowledge Base Architecture Patterns

When building a multi-module Obsidian knowledge base from external sources (files, skills, databases), use these patterns:

### 1. MOC-First Design

Create a master index note (Map of Content / MOC) at the vault root as the single entry point. Structure it as:

```
00-总纲.md              ← Root MOC
├── 模块A/              ← Subject area
│   ├── 00-模块总览.md   ← Module entry point
│   ├── 01-子主题.md    ← Specific topics
│   └── ...
├── 模块B/
└── MOC地图/             ← Cross-module indexes
    └── 交叉索引.md
```

Rules:
- Root MOC links ONLY to module-level entry notes, never to individual leaf notes.
- Each module entry note (`00-名称.md`) contains an ASCII tree or table of all its sub-notes.
- Cross-module indexes live in `MOC地图/`.
- Every note ends with `*返回 [[上级笔记]]*` for navigation.

### 2. The "Bridge" Pattern for Integrating Two Knowledge Systems

When merging two separate knowledge systems (e.g., a decision-making framework + a divination system):

Create a `决断之桥/` (bridge) directory with:
- `00-关系总论.md` — philosophical relationship between the two systems
- `01-系统A映射到系统B.md` — specific cross-references
- `02-时机与融合.md` — temporal/contextual integration
- `03-风险交叉.md` — risk assessment across both systems
- `04-哲学统御.md` — unifying philosophical layer

Each bridge note contains:
- A mapping table: System A concept → System B concept
- A concrete usage flow: when to use which system
- Links to relevant notes in both source systems

### 3. WorkBuddy-to-Obsidian Knowledge Transfer

When extracting knowledge from WorkBuddy custom skills (SKILL.md with YAML frontmatter) into Obsidian:

1. **Assess**: Read the source SKILL.md. Identify: (a) which modules exist, (b) which content is already in the vault, (c) what's missing.
2. **Decompose**: Break monolithic skill files into focused Obsidian notes — one per module/concept, not one file mirroring the whole skill.
3. **Link**: Create Obsidian wikilinks between related concepts from different skill sources.
4. **Bridge**: If the skills come from different domains (e.g., strategy vs divination), add bridge notes to connect them.
5. **MOC**: Update or create a root MOC that points to all modules.

Tool chain: `read_file(source SKILL.md)` → `delegate_task(tasks=[...])` for parallel note creation → `write_file(target note)` per note.

### 4. Large-Scale Content Ingestion from Local Files

When ingesting large content (e.g., 300KB+ notes, PDF extracts, full-book translations):

1. **Extract structured data** with Python regex from the source file.
2. **Create an enhanced quick-reference** (table format, 1-page) for daily use.
3. **Create a full-reference** (all details, 40KB+) for deep lookup.
4. **Link the quick-ref to the full-ref** so users can drill down.
5. **Add a note** in the vault pointing to the original local file path for when the original context matters.

Avoid duplicating entire source files into Obsidian when the source is already on disk — create curated extracts that add value (summary, structure, cross-links) instead.

### 5. Directory naming conventions

- Module directories: Chinese names matching the source system (e.g., `六韬智脑/`, `决断之桥/`)
- Entry notes: `00-名称.md` for module overviews, `01-` `02-` for ordered sub-topics
- MOC: uppercase `MOC地图/` directory at module level
- Case studies: `实战案例/` directory with `00-案例索引.md` + individual `YYYY-MM-DD-案例名.md` files
- Projects: keep under the relevant module, not at vault root

### 6. WorkBuddy texts/ → Obsidian Vault Sync

When synchronizing original text files (classical texts, full-book content) from the WorkBuddy skill's `texts/` directory into the Obsidian vault as standalone notes:

**Workflow:**

1. **Scan** — List the WB skill's `texts/` directory. Identify which vault module(s) the files belong to.

2. **Compare** — For each file, check the vault for existing content:
   - Same name & size → likely identical, skip
   - Same name, vault is truncated/stub → replace with WB full version
   - WB-only → new addition to vault (get `max_NN + 1` for new number)
   - Vault-only → keep as-is (different content type)

3. **Copy/Move** — Use `terminal` `cp` for large files (100KB+). Use `write_file` for small files. Set `source:` in frontmatter for provenance (e.g., `source: WB六韬易哲技能库`).

4. **Parallel execution with delegate_task** — For syncs with 8+ files, delegate the copy/replace batch to a subagent via `delegate_task` with `toolsets=["terminal"]`. The subagent handles all file operations in one shot, keeping your context clean of large file listings.

5. **Frontmatter** — Each new/replaced vault note needs standard YAML frontmatter:
   ```yaml
   ---
   title: 易经经文
   tags:
     - 六韬易哲     # module tag
     - 典籍         # content type tag
   aliases:
     - 易经原文
   created: YYYY-MM-DD
   source: WB六韬易哲技能库
   ---
   ```
   - Files from WB often have no frontmatter at all, or start with BOM (U+FEFF) — strip BOM before adding frontmatter.
   - For replacement files, check if old frontmatter exists. If replacing entirely, add fresh frontmatter.

6. **Merge Table Content** — When a vault note and WB file overlap in format (e.g., both have 爻辞原文 table format) but one is missing content (e.g., vault lacks 卦辞), merge by:
   - Reading both files to understand the format
   - Adding the missing content to the vault version
   - Prefer `write_file` for complex merges (safer than multiple patch calls on markdown tables)

7. **Update Module Total Overview** — Add new entries to the module's overview (`00-总览.md`):
   - Update the ASCII tree with new file references
   - Update book lists / resource tables, marking newly added items as ✅ 已入库
   - Update `updated:` date in frontmatter

8. **Log to Bitable** — Record in 搭建日志:
   ```bash
   lark-cli base +record-upsert --base-token NzuPbMtMFa0wUusVQKwc69lenib --table-id tbllV9WgN64Zwput --as bot --json '{"时间":"YYYY-MM-DD","操作内容":"...","领域":"知识库同步","状态":"✅ 已完成","沟通状态":"○ 无需沟通","备注":"..."}'
   ```

9. **Verify** — `ls -lh` the target directory to confirm all files present and correct sizes. Spot-check head/tail of key files.

**Directory layout pattern for original-text syncs:**

WB texts/ files fall into two structural categories, each with a different vault layout:

| Category | Vault layout | Example |
|----------|-------------|---------|
| **Original classics** (古籍原文) | Create `典籍/` subdirectory within the module | `八字命理/典籍/滴天髓.md`, `中医基础/典籍/黄帝内经.md` |
| **Teaching modules** (教学框架) | Sequential numbering in module root: `max_NN + 1` | `中医基础/08-五运六气.md` (after existing 01-07) |

New files always get `max_NN + 1`. Never insert in the middle. For `典籍/`, number files by their canonical sequence (黄帝内经 = book 1 in TCM canon).

**Key File Categories for WB 六韬易哲 texts/ sync:**

| Category | WB path | Vault target | Example files |
|----------|---------|--------------|---------------|
| 易经体系 | `texts/易经经文.md` | `易经体系/08-易经经文.md` | 易经经文, 周易正义, 易经笔记 |
| 八字命理/典籍 | `texts/滴天髓.md` | `八字命理/典籍/滴天髓.md` | 滴天髓, 子平真诠, 渊海子平 |
| 其他术数 | `texts/梅花易数-邵康节.md` | `梅花易数/` | 梅花易数, 奇门遁甲, 大六壬 |
| 中医经典 | `texts/黄帝内经.md` | `中医基础/典籍/黄帝内经.md` | 黄帝内经, 伤寒论, 金匮要略 |
| 中医教学 | `modules/五运六气.md` | `中医基础/08-五运六气.md` | 五运六气, 伤寒论框架, 四诊详解 |
| 相学风水面相 | `texts/麻衣神相-麻衣道者.md` | `相学体系/` | 麻衣神相, 冰鉴, 柳庄神相 |

**Pitfalls:**
- **patch double-escape in tables**: When updating vault table content that has `\\|` (Obsidian table escape for wikilinks), patch tool may double-escape to `\\\\|`. Fix: use `write_file` for the complete table area, or an `execute_code` Python script:
  ```python
  from hermes_tools import patch
  # Target a unique sentence around the broken line, use plain str
  patch(path=filepath, old_string="...\\\\|已入库...", new_string="...\\|已入库...")
  ```
- **read_file → write_file corruption**: In `execute_code`, `from hermes_tools import read_file; content = read_file(path)["content"]` returns `LINE_NUM|CONTENT` format (every line starts with `N|`). Writing `content` directly via `write_file` corrupts every line. Always strip before writing back:
  ```python
  import re
  lines = content.split('\n')
  cleaned = [re.sub(r'^\s*\d+\|', '', line) for line in lines]
  write_file(path, '\n'.join(cleaned))
  ```
  For large files, prefer `terminal` `cp` to avoid this pitfall entirely.
- **BOM characters**: Some WB texts files start with BOM (U+FEFF). Before adding frontmatter or detecting file encoding, strip BOM with Python (reliable across platforms):
  ```python
  import sys; path = sys.argv[1]
  with open(path, 'rb') as f: content = f.read()
  if content.startswith(b'\\xef\\xbb\\xbf'):
      with open(path, 'wb') as f: f.write(content[3:])
      print('BOM stripped')
  ```
- **Number sequencing**: New vault notes get `max_NN + 1`, never insert in the middle.
- **Cross-module content**: Some WB texts belong to a different vault module than file prefix suggests (e.g., 辰州符咒原文 belongs in 六韬史鉴/民俗文化, not 六韬易哲). Check the module scope before filing.

## Vault Audit

See `references/vault-audit.md` for the periodic audit workflow: broken wikilink detection, MOC tree consistency, orphan wiki page detection, status field audit, cross-reference injection. Run after bulk additions or reorganizations.
