# Tag Cleanup — Inline-to-YAML-List Conversion

## Problem

Obsidian treats `tags: ["六韬智脑"]` (inline, quoted) and `tags:\n  - 六韬智脑` (YAML list, unquoted) as **separate tags**. This fragments the graph view and makes tag searches miss results.

## Detection

```bash
# Find all files using inline tag format
grep -rn "^tags: \[" /path/to/vault --include="*.md"
```

## Conversion Script

Run in execute_code or as a Python script:

```python
import re, os, subprocess

def convert_inline_tags(content):
    """Convert tags: [a, b, c] to tags:\n  - a\n  - b\n  - c"""
    def _convert(match):
        raw = re.search(r'tags:\s*\[(.*?)\]', match.group(0))
        if not raw:
            return match.group(0)
        tags = [t.strip().strip('"').strip("'").strip() 
                for t in raw.group(1).split(',') if t.strip()]
        if not tags:
            return "tags: []"
        return "tags:" + "".join(f"\n  - {t}" for t in tags)
    return re.sub(r'^tags:\s*\[.*?\]', _convert, content, count=1, flags=re.MULTILINE)

# Apply to all files found
vault_root = "/path/to/vault"
result = subprocess.run(
    ["grep", "-rln", "^tags: \\[", vault_root, "--include=*.md"],
    capture_output=True, text=True, timeout=15
)
files = [f for f in result.stdout.strip().split("\n") if f and ".obsidian" not in f]

converted = 0
for fpath in files:
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
        content = fh.read()
    new_content = convert_inline_tags(content)
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        converted += 1

print(f"Converted {converted}/{len(files)} files")
```

## Verification

```bash
# Confirm no more inline format files remain
grep -rn "^tags: \[" /path/to/vault --include="*.md" | grep -v .obsidian
# Should return 0
```

## Scope

This technique covers:
- `tags: [a, b]` → list format
- `tags: ["a", "b"]` → list format (quotes stripped)
- `tags: ['a', 'b']` → list format (single quotes stripped)
