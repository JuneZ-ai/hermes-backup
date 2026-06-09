# WSL2 → Obsidian MCP Bridge

## Problem

Hermes runs inside WSL2. Obsidian runs on Windows. MCP Connector plugin listens on `127.0.0.1` (Windows loopback). From WSL2, `127.0.0.1` is the WSL VM's own loopback — NOT Windows' loopback.

**Netstat from WSL**: Port shows listening on Windows but `curl 127.0.0.1:27200` always returns "Connection refused" because WSL2's 127.0.0.1 ≠ Windows' 127.0.0.1.

## Solution Chain

### Step 1: Patch the Plugin

MCP Connector v0.13.1 hardcodes `BIND_HOST = "127.0.0.1"` as a TypeScript `const` — but the compiled `main.js` stores it in a regular variable.

**File**: `.obsidian/plugins/mcp-tools-istefox/main.js`

**Find**: `U3="127.0.0.1"` (minified var after the port range array `Uz0=[27200,...]`)

**Replace**: `U3="0.0.0.0"`

**Restart Obsidian** to reload the plugin. The plugin now listens on all interfaces.

### Step 2: Find the Actual Port

MCP Connector tries `[27200, 27201, 27202, 27203, 27204, 27205]` with fallback. If 27200 is in use, it picks 27201. Check the port in:
- Obsidian → Settings → MCP Connector (shows "Server running on port NNNNN")
- Or Windows: `netstat -ano | findstr obsidian_pid` looking for LISTENING on 127.0.0.1:NNNNN

### Step 3: Windows Firewall

Add inbound rule for the MCP port:
```powershell
netsh advfirewall firewall add rule name="MCP Connector WSL" dir=in action=allow protocol=TCP localport=27201
```

### Step 4: Find Windows Host IP

From WSL2, the Windows host is reachable via the gateway IP in `/etc/resolv.conf`:
```
nameserver 172.24.0.1   ← example, check actual value
```
WSL's own IP: `hostname -I` (e.g., `172.24.1.197`)

Test with Python socket, not curl (curl doesn't handle MCP's streamable HTTP cleanly):
```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(3)
s.connect(("172.24.0.1", 27201))  # Use the actual port
```

### Step 5: Register in Hermes

```bash
# Add MCP server (interactive — needs token)
export MCP_OBSIDIAN_API_KEY="<token from data.json>"
hermes mcp add obsidian --url http://172.24.0.1:27201/mcp
# Respond: Y (needs auth) → paste token → y (save anyway)

# Enable it (saved as disabled after first test failure)
# Edit ~/.hermes/profiles/huanglaoxie/config.yaml:
#   mcp_servers:
#     obsidian:
#       enabled: true

# Verify
hermes mcp test obsidian
# Expected: ✓ Connected (200-500ms) ✓ Tools discovered: 43
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `curl: (7) Connection refused` | WSL2 127.0.0.1 ≠ Windows 127.0.0.1 | Use Windows gateway IP (Step 4) |
| Connection times out (socket/curl) | MCP Connector still on 127.0.0.1 | Verify Step 1 patch applied; restart Obsidian |
| Connection times out via Windows IP | Firewall blocking | Check Step 3 firewall rule |
| `401 Unauthorized` on MCP calls | No bearer token in Authorization header | Add `-H "Authorization: Bearer <token>"` |
| `Not Acceptable` error | Missing Accept header | Add `-H "Accept: application/json, text/event-stream"` |
| `get_vault_file` returns empty | Wrong parameter name | Use `path`, not `filename`. Use `"format": "json"` for structured response |
| Port 27200 taken | Another process already using it | The plugin auto-falls back; check Settings page for actual port |
| PowerShell/cmd times out from WSL | Slow WSL↔Windows filesystem | Prefer Python socket test or direct Netsh via full path |

## MCP Connector Tool Categories

Total: 43 tools. Key families:

| Category | Tools |
|----------|-------|
| Server info | `get_server_info` |
| Active file | `get_active_file`, `update_active_file`, `append_to_active_file`, `patch_active_file` |
| Vault files | `get_vault_file`, `create_vault_file`, `append_to_vault_file`, `patch_vault_file`, `delete_vault_file`, `rename_vault_file` |
| Partial read | `get_vault_file_partial` (frontmatter/heading/block/outline modes) |
| Listing | `list_vault_files`, `list_tags`, `list_bookmarks` |
| Search | `search_vault_smart` (semantic), `search_vault_simple` (text), `search_vault` (DQL) |
| Graph | `get_backlinks`, `get_outgoing_links`, `get_files_by_tag` |
| Vault intelligence | `find_broken_links`, `find_orphaned_notes`, `search_and_replace`, `get_note_outline` |
| Periodic notes | `get_or_create_daily_note`, `append_to_periodic_note` |
| Miscellaneous | `fetch` (web → markdown), Dataview query execution |

## Smart Connections Plugin

- No API key required — built-in local embedding model (~25MB download once)
- Suggests semantically related notes in right sidebar while you write
- Works with Chinese text (model handles CJK)
- Settings UI is English-only but one-time setup
- Complements MCP Connector: MCP for backend ops, Smart Connections for frontend discovery
