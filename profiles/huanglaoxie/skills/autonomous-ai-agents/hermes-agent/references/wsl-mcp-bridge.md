# WSL-to-Windows MCP Bridge Setup

When Hermes runs inside WSL2 but the MCP server runs on Windows (e.g. Obsidian MCP Connector plugin), WSL2 networking creates several hurdles.

## Core Networking Issue

**WSL2's `127.0.0.1` is NOT Windows' `127.0.0.1`.** WSL2 runs as a lightweight VM with its own loopback interface. To reach a Windows service that listens on `127.0.0.1`, you must:

1. Make the Windows service listen on `0.0.0.0` (all interfaces) instead of `127.0.0.1`
2. Open Windows Firewall for the port
3. Connect from WSL using the Windows host's WSL gateway IP

```
WSL: 172.24.x.x (eth0)
Windows host: 172.24.0.1 (gateway, from /etc/resolv.conf nameserver)
```

## Step-by-Step: Obsidian MCP Connector

### 1. Install the plugin

Download plugin files into `.obsidian/plugins/mcp-tools-istefox/`: `main.js` + `manifest.json`. Register in `.obsidian/community-plugins.json`. User enables in Obsidian Settings → Community Plugins.

### 2. Fix hardcoded bind address

The MCP Connector has `BIND_HOST = "127.0.0.1"` hardcoded. In minified `main.js`:

```
Search: U3="127.0.0.1"
Replace: U3="0.0.0.0"
```

This is near `Uz0=[27200,27201,...]`. Only change this specific assignment — do NOT touch other `127.0.0.1` occurrences (regex patterns, host metadata, URL examples).

### 3. Handle port fallback

Port range `[27200-27205]`. If 27200 is in use, falls back to 27201. **Ask user to check actual port** in Obsidian MCP Connector settings.

### 4. Windows Firewall rule

Admin PowerShell:
```
netsh advfirewall firewall add rule name="MCP Connector WSL" dir=in action=allow protocol=TCP localport=27201
```

Use actual port.

### 5. Find Windows host IP from WSL

```
grep nameserver /etc/resolv.conf  # → 172.24.0.1
ip route show default             # gateway from eth0
```

### 6. Test the connection

MCP Connector requires **both** `application/json` AND `text/event-stream` in Accept header. Missing either returns `Not Acceptable`.

```
curl -s --connect-timeout 5 -X POST http://172.24.0.1:27201/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### 7. Add to Hermes (auth)

Bearer token in `.obsidian/plugins/mcp-tools-istefox/data.json` → `mcpTransport.bearerToken`.

Non-interactive (from execute_code):
```
echo -e "Y\nBEARER_TOKEN\n\ny\n" | hermes mcp add obsidian --url http://172.24.0.1:27201/mcp
```

After add, server is saved `enabled: false` by default. Edit config.yaml to set `enabled: true`.

### 8. Verify

```
hermes mcp test obsidian   # ✓ Connected + ✓ Tools discovered: 43
hermes mcp list            # status = enabled
```
