---
name: knowledge-base-audit
description: Diagnose, analyze, and plan evolution for an Obsidian-based second brain / personal knowledge management (PKM) system. Covers structural exploration, quantitative metrics, qualitative assessment, bottleneck diagnosis, and tiered evolution planning.
triggers:
  - user asks to "analyze my knowledge base" / "how should my vault evolve" / "第二大脑还需要怎么进化" / "diagnose my second brain"
  - user asks for a "knowledge base health check" or "vault audit"
  - user says "how can I improve my note-taking system"
  - any session where the primary goal is understanding the state and trajectory of a PKM/Obsidian vault
  - user says "analyze [tool X] and see if it can improve our work" — cross-pollination from external tools
  - user says "集思广益" / "博采众长" / "积众长以成个性" — the core philosophy of borrowing design patterns
platforms: [linux, macos, wsl]
---

# Knowledge Base Audit & Evolution Planning

A systematic method for auditing an Obsidian-based second brain, diagnosing bottlenecks, and proposing a tiered evolution plan.

---

## Phase 1: Structural Exploration

### 1.1 Get the vault path

The vault path is typically under the user's Documents directory. Common locations:

- `~/Documents/Obsidian Vault/` (Linux/macOS)
- `/mnt/c/Users/<username>/Documents/Obsidian Vault/` (WSL)
- `$OBSIDIAN_VAULT_PATH` (env var, check ~/.hermes/.env)

Use `search_files` or a quick `terminal` `ls` to verify the path exists.

### 1.2 Map the directory tree

```python
# In execute_code or terminal:
import subprocess
root = "/path/to/vault"
result = subprocess.run(["find", root, "-name", "*.md", "-not", "-path", "*/.obsidian/*"],
                        capture_output=True, text=True, timeout=30)
all_mds = [f for f in result.stdout.strip().split("\n") if f]
```

Key observations:
- **Top-level directories**: What's the organizing metaphor? (tree / building / library / zettelkasten / PARA / etc.)
- **File naming conventions**: Are there prefixes (ZN-, DS-, LX-, etc.)? Sequential numbering?
- **Index/MOC files**: Are there `index.md`, `00-*.md`, or MOC files at each level?

### 1.3 Count per module

```python
from collections import Counter
dirs = Counter()
for f in all_mds:
    rel = f.replace(root, "").lstrip("/")
    parts = rel.split("/")
    parent = parts[0] if len(parts) > 1 else "/"
    dirs[parent] += 1
```

This reveals which modules are overweighted or under-invested.

---

## Phase 2: Quantitative Analysis

### 2.1 File size distribution

```python
sizes = []
for f in all_mds:
    sz = os.path.getsize(f)
    sizes.append(sz)
```

Metrics to compute:
| Metric | Meaning | Warning signal |
|--------|---------|----------------|
| Total size & file count | Scale of knowledge base | — |
| Avg / median file size | Density per note | < 2KB median → too many stubs |
| Files < 1KB | Stub/placeholder ratio | > 15% → cleanup needed |
| Files > 50KB | Monolithic note ratio | > 5% → may need splitting |

### 2.2 Frontmatter health

```python
no_frontmatter = 0
frontmatter_count = 0
no_tags = 0
no_aliases = 0
for f in all_mds:
    with open(f, 'r') as fh:
        content = fh.read()
    if content.startswith('---'):
        frontmatter_count += 1
        parts = content.split('---', 2)
        fm = parts[1]
        if 'tags:' not in fm:
            no_tags += 1
        if 'aliases:' not in fm:
            no_aliases += 1
    else:
        no_frontmatter += 1
```

Key ratios:
- **Frontmatter coverage**: `frontmatter_count / len(all_mds)` — target > 90%
- **Tag coverage**: `(frontmatter_count - no_tags) / frontmatter_count` — target > 85%
- **Alias coverage**: `(frontmatter_count - no_aliases) / frontmatter_count` — target > 70%

### 2.3 Link density

```python
import re
total_links = 0
for f in all_mds:
    with open(f, 'r') as fh:
        content = fh.read()
    total_links += len(re.findall(r'\[\[([^\]]+)\]\]', content))

link_density = total_links / len(all_mds)
```

- **Low** (< 3 per file): vault is mostly isolated islands
- **Medium** (3-8 per file): decent connectivity
- **High** (> 8 per file): rich cross-linking (target)

### 2.4 Tag consistency check

Check for quoted vs unquoted YAML tags — Obsidian treats `"六韬智脑"` and `六韬智脑` as different tags.

```python
tag_counts = {}
for f in all_mds:
    with open(f, 'r') as fh:
        content = fh.read()
    if content.startswith('---'):
        # ... extract YAML tags and count
```

If a tag appears in both quoted and unquoted forms, flag for cleanup.

### 2.5 Pipeline health (raw/processed ratio)

For vaults with a "feed pipeline" pattern (`01-信息流/` or similar):

```python
# Count raw vs processed files in the pipeline directory
raw_count = search_files(pattern="status: raw", target="content", path=info_flow_path)
processed_count = search_files(pattern="status: processed", target="content", path=info_flow_path)
digestion_rate = processed_count / (raw_count + processed_count)
```

- **Digestion rate < 50%**: pipeline is backing up — P0 issue
- **Digestion rate 50-80%**: needs attention
- **Digestion rate > 80%**: healthy

---

## Phase 3: Qualitative Assessment

### 3.1 Architecture evaluation

Check the meta-model:
- Is there a clear organizing metaphor? (tree / building / river / garden / etc.)
- Is every module's purpose documented? (total lack of index files is a red flag)
- Are cross-module relationships documented? (explicit connection tables → good sign)

Read the top-level index/MOC files. Note:
- Whether the hook in the architecture is followed consistently at lower levels
- Whether the modular boundaries are clear or leaky
- Whether there are orphan entries that don't follow the naming convention

### 3.2 Content quality sampling

Read 3-5 representative content files across different modules. Check:
- **Depth**: Is it a quick summary or a structured analysis?
- **Linking**: Does it reference other notes in the vault?
- **Actionability**: Does it connect to decision-making or practice?
- **Freshness**: When was it last updated?

### 3.3 Cross-module connectivity

Key diagnostic: **the concept/wiki layer**. A vault that depends on a shared concept layer (e.g. `wiki/` or `concepts/`) should have enough concept pages to cover the main cross-domain ideas. If concepts are < 5% of total files, the neural network of the vault is too thin.

### 3.4 Standards compliance

If SCHEMA.md or similar standards exist:
- Check freshness (last updated date)
- Check whether notes actually follow the stated conventions
- Check whether the SCHEMA itself needs updating (new file types, new naming needs that evolved organically)

---

## Phase 4: Graph-Based Structural Analysis

> This phase is an optional deep dive between quantitative analysis and bottleneck diagnosis. Run when the vault has 150+ files and link density > 5 per file.

### 4.1 Build the Wikilink Graph

```python
import os, re
from collections import defaultdict, Counter

vault = "/path/to/vault"
nodes = set()
edges = set()

for root, dirs, files in os.walk(vault):
    if ".obsidian" in root or ".git" in root:
        continue
    for f in files:
        if not f.endswith(".md"):
            continue
        rel = os.path.relpath(os.path.join(root, f), vault)
        rel_noext = rel[:-3]
        nodes.add(rel_noext)
        content = open(os.path.join(root, f), 'r', encoding='utf-8').read()
        for wl in re.findall(r'\[\[([^\]]+?)(?:\|[^\]]*?)?\]\]', content):
            edges.add((rel_noext, wl.strip()))
```

### 4.2 Degree Analysis

```python
out_deg = Counter()
in_deg = Counter()
for src, tgt in edges:
    out_deg[src] += 1
    in_deg[tgt] += 1

total_deg = {n: out_deg[n] + in_deg[n] for n in nodes}
```

| Metric | Signal | Action |
|--------|--------|--------|
| Isolated pages (deg ≤ 1) | Page disconnected from the network | Add `[[wikilinks]]` or mark as stub |
| Hub nodes (deg ≥ 15) | High-connectivity anchor pages | Maintain/expand — they hold the structure |
| Bridge nodes (connecting 3+ modules) | Cross-modality connectors | Document in fusion notes or MOC |

### 4.3 Module Internal Density

For each module, compute internal edge density:

```python
def module_density(module_pages):
    n = len(module_pages)
    if n < 3:
        return None
    internal = sum(1 for s, t in edges 
                   if s in module_pages and t in module_pages)
    max_edges = n * (n - 1)
    return internal / max_edges if max_edges > 0 else 0
```

- **Density ≥ 0.15** — Healthy cross-linking within module
- **Density 0.08–0.15** — Sparse, could benefit from more internal links
- **Density < 0.08** — Isolated cluster, module feels like a folder of unrelated files

### 4.4 Source Overlap Detection

> Inspired by LLM Wiki's four-signal relevance model.

Two signals for finding pages that share the same source but lack direct links:

**Signal A** — From `01-信息流/` (or equivalent feed directory) wikilinks: if a source file links to multiple knowledge entries, those entries should cross-reference each other.

```python
# For each source file, extract [[wikilinks]] to knowledge modules
# Group knowledge entries by source file
# If two entries share a source but don't link to each other → missing link
```

**Signal B** — From `source_note` frontmatter field: if two knowledge entries both cite the same source via `source_note: "[[01-信息流/XXX]]"`, they should cross-reference.

See `scripts/source-overlap-scanner.py` for the full implementation.

Run with:
```bash
python "scripts/source-overlap-scanner.py"          # Report only
python "scripts/source-overlap-scanner.py" --apply  # Auto-add [[wikilinks]]
```

### 4.5 Tag-Based Potential Links

When two pages share 3+ tags but have no direct `[[wikilink]]`, they are candidates for manual linking. This catches semantic relatedness that the graph topology misses.

### 4.6 Orphan Source Materials

For the feed pipeline (e.g. `01-信息流/`), check if `status:processed` source materials receive inbound links from knowledge entries. Unlinked processed sources indicate a gap in the traceability network.

---

## Phase 5: Bottleneck Diagnosis

Organize findings into a bottleneck framework. The common categories are:

| Code | Category | Symptoms |
|------|----------|---------|
| 🔴 P0 | **Pipeline blockage** | Raw materials piling up, low digestion rate, inconsistency between index and actual files |
| 🔴 P1 | **Thin connective tissue** | Low wiki/concept count, weak cross-module links, tag noise |
| 🟡 P2 | **Weak practice loop** | Few case studies, no synthesis notes, no feedback from practice back into knowledge |
| 🟡 P2 | **Missing self-checks** | No linting, no health metrics, no automated reports |
| 🟢 P3 | **Under-invested modules** | Some branches of the knowledge tree have 1/5 the files of others |
| 🔵 P4 | **Meta-evolution** | The organizing system itself isn't being updated as the vault grows |

---

## Phase 7: Evolution Planning

Present findings in a tiered priority format:

```
P0 🔴 [Immediate: 1-2 days] — Fixes that unblock the whole system
  1. Process pipeline backlog (batch raw→processed)
  2. Fix tag conflicts (quoted vs unquoted)
  3. Sync indices with actual files

P1 🟡 [Short-term: 3-5 days] — Strengthen the network
  1. Expand concept/wiki layer to X+ entries
  2. Introduce synthesis/fusion note type
  3. Create missing MOC or index files

P2 🟢 [Ongoing] — Close the practice loop
  1. Standardize case study template
  2. Set up automated linting (cron job)
  3. Establish health metrics dashboard

P3 🔵 [Long-term] — Meta-evolution
  1. Upgrade organizing schema for new scale
  2. Introduce retrieval analytics
  3. Output archive (query/discussion products)
```

Each item should include:
- Concrete action
- Estimated effort
- Who should do it (if working in a team context)
- How to verify it's done

---

## Phase 8: Remediation — Fixing the Bottlenecks

> Supporting files in this skill: `references/tag-cleanup-script.md` (tag cleanup), `references/wiki-concept-batch-creation.md` (concept expansion), `templates/fusion-note.md` (synthesis notes), `references/2026-05-30-六韬知识库审计.md` (full audit example).

The audit identifies bottlenecks. This phase provides the actual fix techniques.

### 6.1 Fix Pipeline Blockage (P0)

When the info-flow/feed directory has a low digestion rate:

**Step 1 — Cross-reference**: For each raw file, check if a corresponding knowledge entry exists via grep:
```python
import subprocess
for fname in os.listdir(info_dir):
    # Check if the base name is referenced in any .md file outside info_dir
    result = subprocess.run(["grep", "-rl", base_name, vault_root, "--include=*.md"],
                            capture_output=True, text=True)
```

**Step 2 — Triage**:
| Category | Criteria | Action |
|----------|----------|--------|
| ✅ Already processed (has corresponding entry) | grep finds refs | Add `source_note` to knowledge entry's frontmatter + set info file status = processed |
| 📝 Worth distilling | >1KB, unique content not yet captured | Quick extraction → inject to appropriate module |
| 🗑️ Skip | Stub/placeholder, template, template instance | Mark `status: archived` or leave as is |
| 📄 Tool/doc (not knowledge) | System prompts, tool definitions | Mark `status: processed` w/ tool tag, no entry needed |

**Step 3 — Add source_note backlinks** to knowledge entries that don't have them:
```yaml
# In the knowledge entry's frontmatter:
source_note: "[[01-信息流/XXX]]"
```

**Step 4 — Sync the info-flow index.md** with actual files.

### 6.2 Fix Tag Noise (P0)

When YAML tags use inconsistent formats (inline `tags: [a, b]` vs list `tags:\n  - a`):

**Detection**:
```bash
grep -rn "^tags: \[" vault_root --include="*.md"
```

**Fix — Inline-to-list conversion**:
```python
import re
def convert_inline_tags(content):
    def _convert(match):
        raw = re.search(r'tags:\s*\[(.*?)\]', match.group(0))
        if not raw:
            return match.group(0)
        tags = [t.strip().strip('"').strip("'").strip() for t in raw.group(1).split(',') if t.strip()]
        if not tags:
            return "tags: []"
        return "tags:" + "".join(f"\n  - {t}" for t in tags)
    return re.sub(r'^tags:\s*\[.*?\]', _convert, content, count=1, flags=re.MULTILINE)
```

Apply to all files found. Verify with same grep after. This eliminates the "same tag, different format" problem in Obsidian's graph view.

### 6.3 Expand Wiki / Concept Layer (P1)

When the concept layer is too thin (< 10% of total files):

**Step 1 — Identify candidates**: Scan the knowledge base for concepts that appear in 3+ modules. From MOC/index files, extract top-level themes. Look for nouns that bridge domains (e.g. "灰度" appears in 智脑(management), 易哲(philosophy), 史鉴(history)).

**Step 2 — Batch-create concept pages** with consistent format:

```yaml
---
title: Concept Name (Chinese)
tags:
  - wiki
  - cross-module
  - concept
aliases:
  - alternative names in English/Chinese
created: YYYY-MM-DD
type: concept
---

# Concept Name

> One-line definition that captures the essence.

## Cross-Module Mapping

| Module | Linked Note | Role of This Concept in That Module |
|--------|-------------|-------------------------------------|
| 六韬智脑 | [[link]] | — |
| 六韬史鉴 | [[link]] | — |

---

*Concept node — links knowledge modules together*
```

**Step 3 — Update the wiki/index.md** with categorization tables (group concepts by domain: philosophical, cognitive, strategic, business).

**Target**: 30+ concept pages for a 200+ file vault. Each concept should link to 2-4 module-level notes.

### 6.4 Launch Fusion / Synthesis Note Pattern (P1)

When 决断之桥 or equivalent synthesis layer is weak:

**Create a template** in the appropriate directory:
```markdown
---
title: 🌉 Fusion Note — [Topic]
tags:
  - [module]
  - fusion-note
type: fusion
---

## Trigger

[What real-world problem or discovery prompted this cross-module conversation.]

## Participating Modules

| Module | Perspective | Notes Used |
|--------|-------------|------------|
| 🧠 智脑 | | |
| 💭 易哲 | | |
| 📖 史鉴 | | |

## Cross-Examination

[Modules challenge each other's assumptions and findings.]

## Synthesis Conclusion

[What new insight emerged that no single module could produce alone.]

## Landing

- [ ] Action taken → [[case study]]
- [ ] Changed cognition → [[wiki/concept]]

## Backflow

- [[entry 1]] — corrected/clarified
```

Publish the first fusion note using an existing cross-module relationship (e.g. one already documented in a build log or MOC table). This creates a demonstration effect for future fusion notes.

### 6.5 Standardize Case Study / Practice Loop (P2)

When the practice-validation layer is thin:

**Define a case study frontmatter**:
```yaml
type: case-study
status: drafted | validated | iterated
hypothesis: "My judgment before acting was..."
reflection:
  - What was right
  - What was wrong
  - What this corrects in the knowledge base
```

Add a case study template to the module directory.

### 6.7 Reference Project Cross-Pollination

> When the vault needs improvements that don't come from self-audit, borrow from reference projects. This section documents the pattern of extracting techniques from external tools (like LLM Wiki, Mem, Roam) and applying them to the vault.

**When to use**: After an audit identifies a bottleneck, or when the user asks "can we steal X from [project Y]?"

**Pattern**:

```
1. Decompose the reference project into its design decisions
   - What problem does each feature solve?
   - What data/signal does it rely on?
   - Which of those data/signals already exist in our vault?

2. Map reference signals to vault equivalents
   Reference signal          → Vault equivalent
   ──────────────────────────┼────────────────────
   LLM Wiki "sources[]"      → source_note frontmatter + 01-信息流/ wikilinks
   LLM Wiki "[[wikilinks]]"  → [[wikilinks]] (already exists)
   LLM Wiki page type        → YAML frontmatter type field
   LLM Wiki index.md         → module-level index.md + 00-总纲.md
   LLM Wiki purpose.md       → SCHEMA.md (purpose section)
   LLM Wiki graph insights   → wikilink graph analysis
   GBrain typed edges        → cross-module mapping tables (parse `—` descriptors)
   GBrain synthesis          → LLM answer template with gap analysis blocks
   GBrain gap analysis       → "knowledge blank" report at end of every answer

3. Classify each borrowed feature as:
   - 🔴 Direct port (same data exists, just process it differently)
   - 🟡 Adaptation (need new data or format, but doable)
   - 🟢 Inspiration (different architecture, design pattern only)

4. Implement P0/P1 candidates first
   - Low-hanging fruit: anything where the data already exists but isn't being used
   - Example: source overlap → already have source_note + 01-信息流 links, just need a script to find missing cross-references
```

### Tool Location

The scripts and templates in this skill live in TWO places:
- **Skill directory**: `~/.hermes/profiles/huanglaoxie/skills/note-taking/knowledge-base-audit/scripts/` and `templates/` — Hermes internal, usable by future sessions via `skill_view`
- **Vault `_工具/` directory**: `VaultRoot/_工具/` — the canonical runnable location. The user runs these from the vault directory. When updating scripts, write to BOTH locations.

Run from vault:
```bash
cd "/mnt/c/Users/.../Obsidian Vault"
python "_工具/来源重叠扫描.py"
python "_工具/图谱洞察扫描.py" --save-report
python "_工具/类型化边扫描.py"
```

The vault versions are the source of truth. Sync to skill versions when they stabilize.

### User Preference: Real-Time Visibility

This user values **real-time visibility of operations**. When the Obsidian vault is open and MCP Connector is running, every write/modify/search operation appears instantly in Obsidian's file tree and graph view. The user commented: "开着的时候，所有的动作变得可视化了。这一点挺好的" (when it's open, every action becomes visible — that's great). Also: "在ob里做可视化呈现，我要盯着一步一步完成" — step-by-step visual confirmation is preferred.

**Implication**: 
- Prefer MCP-based operations over direct filesystem writes when Obsidian is running
- When making changes, do them one file at a time, announce what you're about to do, wait for confirmation before proceeding to the next
- Direct filesystem writes work when Obsidian is closed, but lack immediate visual feedback
- Always announce completion with "你看 Obsidian 里…" cues so the user knows what to look at

**Obsidian Plugin Stack for Real-Time Ops**:
| Plugin | Role | Port | Tools |
|--------|------|------|-------|
| MCP Connector (istefox/obsidian-mcp-connector) | Backend MCP server | 27200-27205 (auto-fallback) | 43 tools (read/write/search/patch/graph) |
| Smart Connections (brianpetro/obsidian-smart-connections) | Frontend auto-linking | — (in-process) | Semantic recommendations in sidebar |
| Combined effect | Writes appear in file tree + links auto-suggest in right panel | | |

**Smart Connections setup**: No API key needed — uses built-in local embedding model (Transformers.js + MiniLM-L6-v2, ~25MB download once). Tags Chinese text correctly. Settings panel is English-only but one-time setup.

---

## WSL → Obsidian MCP Bridge Setup

When Hermes (WSL2) needs to control Obsidian (Windows) via MCP Connector plugin:

### The WSL2 Networking Challenge

MCP Connector binds to `127.0.0.1` (hardcoded in `constants.ts` as `BIND_HOST`). In WSL2, `127.0.0.1` is the WSL VM's own loopback — NOT Windows' loopback. Direct access fails.

### Fix: Modify Plugin Source

**One-time patch** to the installed plugin's `main.js`:
```
1. Find: U3="127.0.0.1"  (minified var for BIND_HOST)
2. Replace with: U3="0.0.0.0"
3. File: .obsidian/plugins/mcp-tools-istefox/main.js
4. Restart Obsidian to reload plugin
```

Note: The plugin's TypeScript source has `export const BIND_HOST = "127.0.0.1" as const;` — the `as const` makes it a literal type, but the compiled `main.js` stores it in a regular variable that can be patched.

### Additional Setup

1. **Find the port**: MCP Connector auto-falls back through `[27200, 27201, 27202, 27203, 27204, 27205]` if ports are occupied. Check MCP Connector settings page in Obsidian to see the actual port.

2. **Windows Firewall**: Add an inbound rule to allow connections on the MCP port:
   ```powershell
   netsh advfirewall firewall add rule name="MCP Connector WSL" dir=in action=allow protocol=TCP localport=27201
   ```

3. **Authenticate**: MCP Connector generates a bearer token on first run, stored in:
   - `data.json` at `.obsidian/plugins/mcp-tools-istefox/data.json` under `mcpTransport.bearerToken`
   - Hermes saves it to profile `.env` as `MCP_OBSIDIAN_API_KEY` during `hermes mcp add --url`

4. **Add to Hermes**: 
   ```bash
   hermes mcp add obsidian --url http://172.24.0.1:27201/mcp
   # Interactive prompts: Y (needs auth) → paste token → y (save anyway)
   ```
   After adding, edit config to set `enabled: true` (saved as disabled on first test failure).

5. **Verify**: `hermes mcp test obsidian` → should show "✓ Connected (NNNms) ✓ Tools discovered: 43"

### Windows Host IP in WSL2

WSL2 accesses the Windows host via the gateway IP found in `/etc/resolv.conf`:
```
nameserver 172.24.x.x   ← This is the Windows host
```
The WSL VM's own IP is visible via `hostname -I` (e.g., `172.24.1.197`). Always use the **gateway/nameserver** IP to reach Windows services from WSL2.

### Three Operation Modes

| Mode | Obsidian State | How Data Flows | Visible? |
|------|---------------|----------------|----------|
| MCP (preferred) | Open | Hermes → MCP → Obsidian → vault | ✅ Real-time in editor/graph |
| Direct filesystem | Closed | Hermes → write_file/patch → vault files | ❌ Only visible on next Obsidian open |
| Mixed | Open (both) | Hermes → direct filesystem → file changes + Obsidian auto-reloads | ⚠️ File tree updates but no graph refresh |

---

## Scheduled Health Checks

### Weekly Cron Job Pattern

```bash
hermes cron create "0 8 * * 1" \
  "执行六韬知识库周体检。步骤: 1) 运行图谱洞察扫描 2) 读取报告 3) 运行来源重叠扫描 4) 合并结果发报告" \
  --name "六韬周体检" \
  --deliver "origin"
```

This creates a Monday 8am cron that:
1. Runs `_工具/图谱洞察扫描.py --save-report` — degree analysis, module density, bridge nodes, orphan sources
2. Runs `_工具/来源重叠扫描.py` — missing cross-references from shared sources
3. Sends a consolidated Chinese-language report to the user's origin chat

**Report format** (sent to user):
```
六韬周报 · YYYY-MM-DD
- 孤立页面: N 个（较上周 ±M）
- 模块密度: 智脑 X%、史鉴 Y%（较上周 ±Z%）
- 新增来源重叠链接: N 条
- 新素材孤岛: N 个
───
建议关注：本周最值得织网的方向
```

**Verification**: `hermes cron list` to confirm the job shows as `[active]` with correct next run date.

**Common cross-pollination targets**:

| LLM Wiki Feature | 六韬 Equivalent | Implementation | Priority |
|-----------------|----------------|---------------|----------|
| Source overlap (×4.0) | source_note → shared knowledge | `scripts/source-overlap-scanner.py` | P0 |
| Two-step ingestion | Pre-analysis → Review → Generate | `templates/two-step-ingest.md` | P0 |
| Graph insights | Degree / density / bridge analysis | `scripts/graph-insight-scanner.py` | P1 |
| Context budget (60/20/5/15) | Retrieval prompt template | `templates/context-budget-rules.md` | P1 |
| Louvain community detection | Module grouping (already exists) | Manual cross-ref tables | P2 |
| Deep Research (knowledge gaps) | User identifies gaps → search | Manual process | P2 |
| MCP Server / API | AI bot direct access via MCP Connector plugin | `hermes mcp test obsidian` — Obsidian MCP Connector (43 tools) | P2 ✓ DONE |
| Typed edges (GBrain) | Cross-module mapping tables with `—` descriptors | `scripts/typed-edge-scanner.py` | P1 |
| Synthesis + Gap Analysis (GBrain) | Answer template with "已覆盖 + 知识空白 + 填补建议" | `templates/gap-analysis-prompt.md` | P1 |

**Pitfalls**:
- Don't port features that solve problems you don't have. LLM Wiki's vector search (LanceDB) improves recall by 13%, but the vault's tag + wikilink system may already cover the gap.
- Don't assume the reference project's data model maps 1:1. Adapt, don't copy.
- Each cross-pollination creates maintenance debt. Minimize scripts that modify files unless the user commits to running them regularly.

### 6.8 Two-Step Ingestion Workflow

> Adapted from LLM Wiki's "两步思维链摄入" — split material processing into two sequential LLM calls: first analyze, then generate. The human only reviews.

**Pattern**:

```
Step 1: LLM Pre-analysis
  Input: raw material content
  Output: structured analysis (6 blocks)
    1. Key entities (people, orgs, products, events)
    2. Core concepts (theories, methods, frameworks)
    3. Cross-module relevance prediction
    4. Tensions & contradictions with existing knowledge
    5. Recommended knowledge entry structure (how many entries, titles, types)
    6. Uncertainties & questions for human

Step 2: Human Review (3-5 min)
  Check: entity recall, concept fidelity, module fit, contradiction reality check,
         entry structure suitability, AI's uncertainties

Step 3: LLM Generation
  Input: raw material + reviewed analysis
  Output: knowledge entry (.md) + index update + source_note + status change
```

Full prompt template at `templates/two-step-ingest.md`.

**When to use**:
- Every material ingestion where quality matters more than speed
- Skip for: single-paragraph clippings, tool docs, status updates
- Always use for: PDFs, long-form articles, books, research papers

**Verification**: After generation, check:
1. New knowledge entry has correct frontmatter (`type`, `tags`, `source_note`, `status`)
2. Module `index.md` was updated
3. Source material status changed to `processed`
4. Cross-module `[[wikilinks]]` reference real existing pages

### 6.9 Context-Budgeted Retrieval

> Adapted from LLM Wiki's budget-controlled retrieval pipeline. When querying the vault via LLM, explicitly allocate the context window to prevent either underfeeding or overwhelming the model.

**Formula**:
```
Safe window = model_limit × 0.8
  ├── 60% → Knowledge entries (retrieved pages, full text)
  ├── 20% → Chat history (recent N turns)
  ├──  5% → Navigation index (总纲 + index.md)
  └── 15% → System prompt (SCHEMA + format rules)
```

The 60% knowledge budget is further divided:
- 50% → Top-ranked matches from keyword/token search
- 30% → One-hop graph neighbors of matched pages
- 20% → Two-hop graph neighbors (decaying relevance)

Full prompt template at `templates/context-budget-rules.md`.

**Model reference**:

| Model | Total | Safe(×0.8) | Knowledge(60%) | History(20%) | Index(5%) | System(15%) |
|-------|-------|-----------|----------------|--------------|-----------|-------------|
| DeepSeek V4 Pro/Flash | 128K | 102K | ~61K | ~20K | ~5K | ~15K |
| DeepSeek V3 | 64K | 51K | ~30K | ~10K | ~2.5K | ~7.5K |
| Claude Opus 4 | 200K | 160K | ~96K | ~32K | ~8K | ~24K |

**When to use**:
- Cross-module synthesis queries (large surface area)
- Knowledge gap analysis (needs to scan broadly)
- Skip for: one-page queries, wiki concept lookups, simple fact retrieval

## Pitfalls (Remediation-Specific)

- **Info flow triage is not 1-to-1**: Some info files bypass the pipeline entirely (user sent directly to knowledge entry). Always cross-reference via grep before counting "unprocessed."
- **Wiki concepts need curated linking**: After creating concept pages, update existing high-value notes to link to them. Otherwise concept pages are isolated nodes.
- **Fusion notes should be rare, not routine**: Not every cross-reference needs a fusion note. Reserve for insights that genuinely change cognition. Target ratio: 1 fusion note per ~20 knowledge entries.
- **Don't over-engineer tags**: After the initial cleanup, let tags emerge naturally. Obsidian's graph handles ~50 distinct tags well.

## Phase 9: Codification

After the audit:
1. Save audit findings as a reference file under this skill
2. Save batch scripts as references/ files for reproducibility
3. If new patterns emerged, create or update templates in `templates/` 
4. If the user expressed preferences about format or depth, embed them here

## General Pitfalls

- **Don't trust the index alone**: Always verify actual file count vs indexed file count. Indices go stale.
- **Don't assume raw materials are waste**: Some raw materials are bypassed by direct-to-knowledge-entry workflows. Check for source_note links before counting as unprocessed.
- **Don't diagnose without sampling**: Quantitative metrics without content sampling miss context (e.g., a stub might be intentionally templated vs truly abandoned).
- **Don't propose P0 cleanup without checking labels**: Some "raw" notes in 01-信息流 may have been intentionally left as reference material, never meant for processing.
- **Don't prescribe a fix without understanding the user's rhythm**: A user who batch-processes weekly has different needs than one who processes daily.
