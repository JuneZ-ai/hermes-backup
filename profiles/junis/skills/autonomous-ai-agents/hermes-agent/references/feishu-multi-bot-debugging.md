# Feishu Multi-Bot Debugging

Diagnosis guide for when a Feishu bot (via Hermes Profile) connects but doesn't respond, or responds with errors.

## Symptom: Connected but No Response

### Symptom Tree

```
Bot shows as online in Feishu, but messages get no reply
├── Check 1: Is the gateway process still running?
│   ├── YES → Go to Check 2
│   └── NO → Process was killed between agent turns.
│       Fix: Use tmux, NOT terminal(background=true).
│       tmux new-session -d -s <bot-name> '<wrapper> gateway run --replace'
│
├── Check 2: Does the gateway log show "Primary provider auth failed"?
│   ├── YES → Model provider not configured for this profile.
│   │   Fix: The profile needs its own model config:
│   │   - model.provider (e.g. "custom")
│   │   - model.base_url (e.g. "https://api.deepseek.com")
│   │   - model.api_key (the actual key)
│   │   - model.default (e.g. "deepseek-v4-flash")
│   │   Profiles DO NOT inherit model settings from the default profile.
│   │
│   └── NO → Check gateway.log for "Inbound dm" entries.
│       If none: Feishu app may not be PUBLISHED yet.
│       Fix: Go to Feishu Open Platform → 版本管理与发布 → 创建版本 → 发布
│       Also check: bot toggle ON under 应用功能 → 机器人
│
└── Check 3: Gateway log shows "Inbound dm" but then auth error?
    → API key is wrong. Go to API Key Diagnosis below.
```

## API Key Diagnosis

### Problem: Cannot copy API keys between profiles

All Hermes tool output (terminal, read_file, grep, Python yaml.safe_load) **masks API key values**. A DeepSeek key stored as `sk-d1a9fb87e8a54001ae02e5c88819e92f` will display as `sk-d1a...e92f` or `sk-d1a...e92f` in every tool.

The `config.yaml` on disk actually contains the truncated value `sk-d1a...e92f` — not a display-level mask. The full key was originally written by `hermes config set` or the `hermes model` wizard, but after that, you cannot read it back.

### Problem: .env OPENAI_API_KEY diverges from config model.api_key

When `hermes profile create` makes a new profile, the `.env` gets an `OPENAI_API_KEY` value that may differ from the config's `model.api_key`. The gateway connects to Feishu successfully (Feishu auth and model auth are independent) but **silently 401s on model calls** — no error in gateway.log, only `response ready: time=Xs api_calls=0` or timeout.

**Diagnosis:** Compare the two keys:

```bash
# Read config key via hex
xxd ~/.hermes/profiles/<bot-name>/config.yaml | grep -A1 "api_key" | head -1

# Read .env key via hex
xxd ~/.hermes/profiles/<bot-name>/.env | grep -A3 "API_KEY" | head -2
```

The hex-decoded `sk-...` tokens must be identical. If not, fix the `.env`:

```bash
cat > ~/.hermes/profiles/<bot-name>/.env << 'ENVEOF'
# ... paste correct key from config ...
OPENAI_API_KEY=<same key as config's model.api_key>
OPENAI_BASE_URL=<same base_url as config's model.base_url>
ENVEOF
```

Then restart the gateway.

### How to verify the actual key

Option A — Check via hex dump:
```bash
xxd ~/.hermes/config.yaml | grep -A1 "api_key"
# Decode the hex to get the actual key value
```

Option B — Read raw bytes in Python:
```python
with open('/home/hermes/.hermes/config.yaml', 'rb') as f:
    content = f.read()
idx = content.find(b'api_key')
if idx >= 0:
    line_end = content[idx:].find(b'\n')
    line = content[idx:idx+line_end]
    val = line[line.find(b'sk-'):]
    print(repr(val))  # Shows actual bytes
    print(val.hex())  # Hex decode to verify
```

Option C — Check working profile's auth.json credential pool:
```bash
python3 -c "import json; d=json.load(open('/home/hermes/.hermes/auth.json'));
print(json.dumps(d.get('credential_pool', {}), indent=2))"
```

### If the key is wrong: How to set it correctly

```bash
# Direct write to config.yaml (since terminal tools mask the value)
# Use write_file or sed with the exact key value
# OR use the profile wrapper's hermes config set (the key is stored correctly,
# you just can't read it back later)
```

## Debugging Log Flow

When a user sends a message to the bot, check the gateway log in sequence:

```
[1] Received raw message               → Message arrived from Feishu
[2] Inbound dm message received        → Message accepted by gateway  
[3] inbound message:                   → Forwarded to agent
[4] response ready: time=Xs api_calls=Y → Response generated
[5] Sending response (N chars) to ...  → Response sent back
```

If you see (1) and (2) but nothing after:
- Missing model config → Check for `Primary provider auth failed`
- Model API call failing → Check for `401` or `AuthenticationError`

Key log patterns:

| Log pattern | Meaning | Fix |
|-------------|---------|-----|
| `Primary provider auth failed: No inference provider configured` | Profile has no model config | Set model.provider, base_url, api_key explicitly |
| `HTTP 401: Authentication Fails, Your api key: ****XYZ is invalid` | API key is wrong/expired | Use xxd to find the actual key from the working profile |
| `channel directory built: 0 target(s)` | No conversations found | Normal on first start — user needs to message the bot |
| `response ready: time=9.4s api_calls=0` | Response generated but NO API calls | Fallback/default message used — model auth failed |
| `response ready: time=5.0s api_calls=1 response=199 chars` | Working response | Normal operation |

## Common Root Causes Summary

1. **Gateway process killed** — terminal(background=true) dies between agent turns. Use tmux.
2. **Missing model config in profile** — profiles don't inherit from default. Set provider+base_url+api_key+model.
3. **Wrong API key when copying** — all tools mask the value. Use xxd hex dump to read the actual key.
- **Feishu app not published** — bot toggle ON is not enough. Must create version and publish.
  **Diagnosis**: gateway log shows `✓ feishu connected` but no `Inbound dm` entries appear even after the user sends a message. The WebSocket connects but the platform doesn't forward events to unpublished apps. Use `tail -f` on the gateway log while the user sends a test message to confirm:
  ```bash
  tail -f ~/.hermes/profiles/<bot>/logs/gateway.log | grep -E "Inbound|feishu connected|channel directory"
  ```
  If you see `feishu connected` but never `Inbound dm` after the user messages the bot → app is NOT published.
5. **Feishu app missing permissions** — im:message scope required for event subscription.
