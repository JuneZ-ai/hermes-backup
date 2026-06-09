# Creating Python MCP Services for Hermes

## Overview

MCP (Model Context Protocol) services expose tools that Hermes agents can call. You can implement an MCP server in Python and register it with Hermes — no Node.js required.

## Architecture

```
Hermes Agent → [MCP stdio protocol] → Python MCP Server (FastMCP)
                                        ├── Tool 1 (e.g. memory_hybrid_search)
                                        ├── Tool 2 (e.g. memory_bm25_search)
                                        └── ...
```

Communication happens over stdio (subprocess stdin/stdout). No HTTP server needed.

## Quick Start

### 1. Install the FastMCP library

```bash
python3 -m pip install mcp
```

### 2. Create a minimal server

```python
#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-service")

@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 3. Register with Hermes

```bash
hermes mcp add my-service \
    --command python3.14 \
    --args /path/to/server.py
```

Or add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  my-service:
    command: python3.14
    args:
      - /path/to/server.py
```

### 4. Verify

```bash
hermes mcp list                  # Should show your service
hermes mcp test my-service       # Should discover N tools
```

## Key Patterns

### File Layout

```
path/to/mcp-service/
├── server.py          ← FastMCP entry point
├── module1.py         ← Implementation modules
├── module2.py
├── requirements.txt   ← pip dependencies
└── test_*.py          ← Tests (run with pytest)
```

### Tool Registration

Use `@mcp.tool()` decorator. The function name becomes the tool name; the docstring becomes the tool description; type-annotated parameters become the schema.

```python
@mcp.tool()
def my_tool(param1: str, param2: int = 42) -> str:
    """Description that shows in `hermes mcp test` output."""
    return json.dumps({"result": "..."})
```

### Structured Data Returns

Always return JSON strings from tools:

```python
import json

@mcp.tool()
def search(query: str, limit: int = 5) -> str:
    results = [...]  # dict/list
    return json.dumps(results, ensure_ascii=False)
```

### Error Handling

```python
@mcp.tool()
def safe_tool() -> str:
    try:
        # ...
        return json.dumps({"success": True, "data": ...})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
```

## Pitfalls

1. **Scripts with hyphens in filenames** cannot be imported as modules. Use underscores.

2. **The server must run on stdio.** `mcp.run(transport="stdio")` is the correct transport for Hermes integration.

3. **First-time registration is interactive** (`hermes mcp add` prompts Y/n to enable all tools). To bypass, write config.yaml directly using the config API:
   ```python
   from hermes_cli.config import load_config, save_config
   cfg = load_config()
   cfg.setdefault("mcp_servers", {})["name"] = {
       "command": "python3.14",
       "args": ["/path/to/server.py"],
   }
   save_config(cfg)
   ```

4. **Config format matters.** The `mcp_servers` key must be a dict of `{name: {command, args}}`. Other formats are silently ignored.

5. **Restart after registration.** MCP servers are loaded at agent startup. After adding one, run `/reset` in CLI or restart the gateway.

6. **Profile isolation.** MCP servers registered in the root config.yaml are shared across profiles. Per-profile MCP servers go in `~/.hermes/profiles/<name>/config.yaml`.

## Testing

```python
# test_server.py
from my_server import mcp

def test_tool_exists():
    tools = mcp.get_tools()
    assert "my_tool" in [t.name for t in tools]
```
