# Vault Health Audit & Maintenance

Run this periodically to keep the vault healthy, especially after bulk ingestion or note reorganization.

## 1. Structural Inventory

```bash
# Count total notes
find "/path/to/vault" -type f -name "*.md" | wc -l

# List all directories
find "/path/to/vault" -type d | sort

# Count notes per module directory
for dir in 六韬智脑 六韬史鉴 六韬易哲 决断之桥 太极双螺旋 实战案例 wiki 01-信息流 MOC地图; do
  count=$(find "/path/to/vault/$dir" -name "*.md" 2>/dev/null | wc -l)
  echo "$dir: $count notes"
done
```

## 2. Broken Wikilink Detection

Extract all `[[links]]` from the root MOC (`00-六韬总纲.md`) and verify each resolves:

```python
from pathlib import Path
import re

vault = Path("/path/to/Obsidian Vault")
moc_text = (vault / "00-六韬总纲.md").read_text()

# Extract all wikilinks
links = re.findall(r'\[\[([^\]]+)\]\]', moc_text)
broken = []
for link in links:
    # Strip alias
    target = link.split("|")[0].split("\\|")[0]
    # Check file existence (with .md extension)
    found = list(vault.rglob(f"{target}.md"))
    if not found:
        broken.append(target)

if broken:
    print(f"🔴 BROKEN: {len(broken)} broken links found:")
    for b in broken:
        print(f"  - [[{b}]]")
else:
    print("✅ All MOC links resolve correctly.")
```

**Common causes of broken links:**
- Note was renamed but MOC not updated
- Path uses `MOC地图/易医同源` but file is at `六韬易哲/MOC地图/易医同源`
- Escaped pipes `\\|` in table context got mangled by patch tool

**⚠️ Patch tool trap**: When patching `\\|` (escaped pipe) in table wikilinks, the fuzzy matcher may double-escape to `\\\\|`. Fix: replace the entire line with a stable surrounding anchor, or rewrite the whole table block.

## 3. Orphan Wiki / Concept Page Detection

Wiki pages with no backlinks from the rest of the vault are dead ends:

```bash
cd "/path/to/vault"
for page in wiki/*.md; do
  name=$(basename "$page" .md)
  refs=$(grep -rl "\[\[$name\]\]" --include="*.md" . | grep -v "^./wiki/" | grep -v "^./实战案例/" | wc -l)
  if [ "$refs" -eq 0 ]; then
    echo "🔴 UNREFERENCED: [[wiki/$name]]"
  else
    echo "🟢 [[wiki/$name]] — $refs inbound links"
  fi
done
```

**Fix**: For each orphan, find a natural home:
- Read the wiki page to understand its concept
- Find a related module note whose content naturally connects to it
- Insert a `→ 参见 [[wiki/xxx]]` line at the end of that module note (before the closing `---` or footer area)
- Avoid forced links — only link where the connection is conceptually sound

Good injection targets by wiki concept type:
| Wiki concept type | Best injection targets |
|---|---|
| AI/Human (物我合一, 人机协作) | 六韬智脑/19-埃森哲AI, 太极双螺旋总纲 |
| Attention/Info (上下文税, 输出通胀) | 六韬智脑/05-神经突触, 03-CEO控制台 |
| Resource (调度折价, 预算内生化) | 六韬智脑/02-战略哲学, 03-CEO控制台 |

## 4. MOC Tree Consistency Check

Verify that the ASCII tree in the root MOC matches actual file names:

```python
from pathlib import Path
import re

vault = Path("/path/to/Obsidian Vault")
moc = (vault / "00-六韬总纲.md").read_text()

# Extract wikilinks from the tree block (between ``` markers)
tree_block = re.search(r'```\n六韬·决断一体.*?\n```', moc, re.DOTALL)
if tree_block:
    tree_links = re.findall(r'\[\[([^\]]+)\]\]', tree_block.group())
    for link in tree_links:
        target = link.split("|")[0].split("\\|")[0]
        file_path = vault / f"{target}.md"
        if not file_path.exists():
            print(f"❌ TREE BROKEN: [[{target}]] — file not found")
    
    # Check for duplicate entries (same file linked twice)
    link_targets = [link.split("|")[0].split("\\|")[0] for link in tree_links]
    dupes = [t for t in link_targets if link_targets.count(t) > 1]
    if dupes:
        print(f"⚠️ DUPLICATE TREE ENTRIES: {set(dupes)}")
```

## 5. Status Field Audit

Ensure all status fields are consistent:

```python
from pathlib import Path
import re

vault = Path("/path/to/Obsidian Vault")
for note in vault.rglob("*.md"):
    if ".obsidian" in note.parts or ".trash" in note.parts:
        continue
    text = note.read_text()
    fm_match = re.match(r'^---\n(.*?)\n(?:---|\.\.\.)', text, re.DOTALL)
    if not fm_match:
        print(f"⚠️ No frontmatter: {note.relative_to(vault)}")
        continue
    fm = fm_match.group(1)
    # Check status field
    if note.parent.name == "01-信息流":
        if "status:" not in fm:
            print(f"⚠️ No status: {note.relative_to(vault)}")
        elif "status: raw" in fm or "status: processed" in fm:
            pass  # OK
        else:
            print(f"⚠️ Unknown status value: {note.relative_to(vault)}")
```

## 6. Cross-Reference Injection

After audit, inject missing cross-references. Pattern:

```
→ 深度概念：[[wiki/物我合一]] · [[wiki/人机协作]]
```

Append this line before the closing `---` or footer section of the target note.

For each link, verify:
1. The target file exists
2. The concept is genuinely relevant to the source note's content
3. Don't over-link — 2-3 wiki links per note is the sweet spot

## 7. Module Status Table Update

After any structural change, update the table in `00-六韬总纲.md`:

```markdown
| 模块 | 笔记数 | Deep-Dive | 状态 |
|:----|:------:|:----------|:----:|
| ☯️ 太极双螺旋 | N | — | 🟢 evergreen |
| 🧠 六韬智脑 | M | topic list | 🟢 growing |
| 🔮 六韬易哲 | K (submodules) | — | 🟡 growing |
| ⚡ 决断之桥 | P + Q 知识库 | — | 🟢 growing |
| 🆕 六韬史鉴 | R | deep-dive list | 🟢 growing |
| 🧘 MOC 心法层 | S | — | 🟡 seedling |
| 🏢 实战案例 | T | latest case | 🟢 growing |
```

Count notes with: `find "vault/module_dir" -name "*.md" | wc -l`
Update the `updated:` field in the MOC frontmatter.

## Quick Reference: repair patterns

| Issue | Fix command |
|---|---|
| Broken wikilink from rename | `patch(path=MOC, old="旧名", new="新名")` |
| Wrong path prefix | `patch(old="[[MOC地图/X]]", new="[[六韬易哲/MOC地图/X]]")` |
| Duplicate tree entry | `patch(old="  └── duplicate line", new="")` — empty string to delete |
| Doubled backslash in tables | use execute_code Python str.replace — patch fuzzy matcher double-escapes `\\|` to `\\\\|`; Python `str.replace` is deterministic |
| Orphan wiki page | `patch(note_end, old="---", new="→ 参见 [[wiki/xxx]]\n\n---")` |
