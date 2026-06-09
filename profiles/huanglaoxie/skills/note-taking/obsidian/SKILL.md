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

## WSL2 Networking: Reaching Windows-Bound Plugin Services

Some plugins (notably **MCP Connector**) bind their HTTP/MCP server to `127.0.0.1` on **Windows only**. From WSL2, `127.0.0.1` is the WSL VM's own loopback, NOT Windows'. The plugin's service is unreachable even though it's running.

### Diagnosis

```python
# From WSL, both of these fail:
# 127.0.0.1:27200 → WSL's own loopback (nothing listening)
# 172.24.0.1:27200 → Windows host, but plugin doesn't listen on external IP
```

Use `netstat` on Windows to confirm the service IS running on 127.0.0.1:
```powershell
netstat -ano | findstr 27200
# Should show: TCP 127.0.0.1:27200  LISTENING  <pid>
```

### Fix: Patch the Plugin's main.js

Most Obsidian plugins hardcode `BIND_HOST` in their compiled `main.js`. Search for `127.0.0.1` in the bundled JS to find the binding assignment:

```bash
grep -oP '.{80}127\\.0\\.0\\.1.{80}' /path/to/vault/.obsidian/plugins/<plugin-id>/main.js
```

Look for the pattern that assigns it as a value (not a URL example or regex). Typical minified pattern:
```javascript
U3="127.0.0.1"   // ← this is the bind host
```

Replace with `0.0.0.0`:
```bash
# In a tool that can edit the file:
patch(path="/path/to/.obsidian/plugins/<plugin-id>/main.js",
      old_string='U3="127.0.0.1"',
      new_string='U3="0.0.0.0"')
```

Then restart Obsidian.

### Verify

```python
# After restart, from WSL:
import socket
s = socket.socket()
s.settimeout(3)
try:
    s.connect(("172.24.0.1", 27200))  # Windows gateway IP
    print("✅ Reachable")
except Exception:
    print("❌ Still unreachable")

# Or try the MCP protocol:
curl -s -X POST http://172.24.0.1:27200/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### Alternative: netsh Port Proxy

If patching is undesired, the user can run this on Windows (Admin):
```powershell
netsh interface portproxy add v4tov4 listenport=27200 listenaddress=0.0.0.0 connectport=27200 connectaddress=127.0.0.1
```

### Pitfalls

- `main.js` is minified — the bind host string appears 3-4 times in different contexts (bind value, host info display, URL examples, regex patterns). Only change the **value assignment** (`U3="127.0.0.1"`). Leave regex patterns and URL examples untouched.
- Obsidian must be restarted after patching. Toggling the plugin off/on in settings does NOT reload the JS bundle.
- The patch survives plugin updates ONLY until the user installs a newer version. Document the fix for reapplication.
- Smart Connections doesn't listen on a port (runs entirely in-process), so it needs no networking fix.
- On WSL2, the Windows host's external IP is found in `/etc/resolv.conf` as the `nameserver` value (typically `172.24.0.1` or `172.x.x.x`).

## Install Community Plugins from CLI

Obsidian plugins can be installed by downloading release files into `.obsidian/plugins/<plugin-id>/`. Use this when you can't access Obsidian's UI (automation, WSL, headless).

**Step 1 — Find the plugin.** Look it up in the community plugin registry:
```python
import json, urllib.request
url = "https://cdn.jsdelivr.net/gh/obsidianmd/obsidian-releases@master/community-plugins.json"
req = urllib.request.Request(url, headers={"User-Agent": "..."})
with urllib.request.urlopen(req, timeout=30) as resp:
    plugins = json.loads(resp.read())
# Find by plugin id: [p for p in plugins if p["id"] == "mcp-tools-istefox"]
# repo = p["repo"]  => GitHub repo name
```

**Step 2 — Get the latest release assets.**
```python
rel_url = f"https://api.github.com/repos/{repo}/releases/latest"
# Check assets for: main.js, manifest.json, styles.css
```

**Step 3 — Download into .obsidian/plugins/<plugin-id>/**
```python
import os, urllib.request
plugins_dir = os.path.join(vault_path, ".obsidian", "plugins", plugin_id)
os.makedirs(plugins_dir, exist_ok=True)
for fname, furl in {asset["name"]: asset["browser_download_url"]
                     for asset in release["assets"]}.items():
    urllib.request.urlretrieve(furl, os.path.join(plugins_dir, fname))
```

**Step 4 — Register in community-plugins.json:**
```python
comm_path = os.path.join(vault_path, ".obsidian", "community-plugins.json")
with open(comm_path) as f:
    enabled = json.load(f)
if plugin_id not in enabled:
    enabled.append(plugin_id)
with open(comm_path, 'w') as f:
    json.dump(enabled, f, indent=2)
```

**Required files per plugin:** At minimum `main.js` + `manifest.json`. Some also ship `styles.css`.

**Verification:**
```python
plugins_dir = os.path.join(vault_path, ".obsidian", "plugins")
for p in sorted(os.listdir(plugins_dir)):
    manifest_path = os.path.join(plugins_dir, p, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            data = json.load(f)
        print(f"  ✅ {p} v{data.get('version', '?')}")
```

**Notable plugins installable this way:**
| Plugin ID | Name | What it does |
|-----------|------|-------------|
| `mcp-tools-istefox` | MCP Connector | Turns Obsidian into an MCP Server (port 27200, 43 tools, local semantic search) |
| `smart-connections` | Smart Connections | AI-powered auto-linking while writing, local embedding, no API key needed |
| `lark-doc` | Lark/Feishu Bridge | Syncs Feishu documents into the vault |

**Pitfalls:**
- Obsidian must be restarted (or plugin toggled off/on in settings) for new plugins to activate
- `community-plugins.json` is the enable list; the plugin files MUST be in the directory AND listed here
- MCP Connector runs in-process inside Obsidian — Obsidian needs to be open for its MCP tools to work
- Smart Connections runs locally without API keys (built-in MiniLM-L6-v2 embedding model)
- On WSL, the vault path is under `/mnt/c/Users/...` — always translate Windows paths explicitly
