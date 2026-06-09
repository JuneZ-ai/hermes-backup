# Feishu Permission Audit Guide

When a user asks "are my Feishu permissions OK / too many?", determine what API scopes the code actually uses by auditing the platform adapter.

## Method

1. **Find the platform code** — usually at `gateway/platforms/feishu.py` under the Hermes install dir.

2. **Grep for API endpoint URIs** to find all OpenAPI endpoints called:
   ```bash
   grep -n '\.uri(\|/open-apis/' gateway/platforms/feishu.py | head -30
   ```

3. **Grep for SDK method calls** to find lark_oapi client invocations:
   ```bash
   grep -n 'self\._client\.\|im\.v1\.\|drive\.v1\.\|docx\.v1\.' gateway/platforms/feishu.py | head -50
   ```

4. **Map to Feishu scopes**:

   | API Used | Required Scope |
   |----------|---------------|
   | `im.v1.message.create/reply/get` | `im:message` |
   | `im.v1.image.create` / `im.v1.message_resource.get` | `im:resource` |
   | `im.v1.chat.get` | `im:chat` |
   | `im.v1.message_reaction.create/delete` | `im:message.reaction` |
   | `/open-apis/bot/v3/info` | None (built-in) |
   | `drive.v1.*` | `drive:drive` |
   | `docx.v1.*` | `docx:document` |
   | `contact.v1.*` | `contact:*` |

5. **Report unused scopes** that the user can remove from the Feishu Developer Console:
   - ❌ `drive:*` — cloud document access (not used)
   - ❌ `docx:*` — document read/write (not used)
   - ❌ `contact:*` — employee info (not used)
   - ❌ `calendar:*`, `mail:*`, `sheet:*` — not used

## Baseline for Hermes Gateway (v2.x, May 2026)

The gateway platform code (`feishu.py`) only uses:
- `im:message` — send/receive messages (core)
- `im:resource` — upload/download images/files
- `im:chat` — read chat/group info
- `im:message.reaction` — emoji reactions (typing indicator)

These 4 scopes are sufficient for basic bot operation (DM + group @mention, text/images/files, typing indicators). No document, contact, or drive permissions needed.

## Additional Tool Scopes

The agent's own Feishu tools (`feishu_doc_read`, `feishu_drive_add_comment`, etc.) are in the `feishu_doc` and `feishu_drive` toolsets, which are OPTIONAL — they require `doc:document:readonly` and `drive:drive` scopes respectively. Only grant these when the user explicitly needs Feishu document operations.

## Config

The Hermes `.env` needs:
```
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
FEISHU_DOMAIN=feishu          # or lark for larksuite.com
FEISHU_CONNECTION_MODE=websocket
```
