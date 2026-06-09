# Feishu Troubleshooting Reference

Common Feishu Open API error codes and their fixes for the Hermes Agent gateway.

## WebSocket 频繁断联 — No Ping/Keepalive

**Meaning:** The Feishu WebSocket connection drops frequently, especially after
laptop sleep/hibernation (S4 state), and doesn't auto-reconnect promptly.

**Root cause:** The Feishu adapter defaults `ws_ping_interval` to `None` —
no Ping/Pong frames are sent on the WebSocket. With no keepalive:

1. When the laptop hibernates (S4), the WSL network stack goes down
2. The TCP connection becomes half-open — neither side knows it's dead
3. The gateway never detects the disconnection until it tries to send a message
4. Without outgoing messages, the gateway sits in "connected" limbo indefinitely

**Diagnosis:**

Check for recent hibernation events in kernel logs:
```bash
journalctl -k --no-pager | grep "RTC can wake from S4" | tail -5
```

Check the current gateway's ping settings (look for the startup log or config):
```bash
systemctl --user status hermes-gateway --no-pager | head -5
grep "ws_ping_interval" ~/.hermes/config.yaml
```

If `ws_ping_interval` is absent or `null`, this is the problem.

**Fix — Enable WebSocket Ping Keepalive:**

Add an `extra` block under `platforms.feishu` in `~/.hermes/config.yaml`:

```yaml
platforms:
  feishu:
    enabled: true
    extra:
      ws_ping_interval: 25       # Send a ping every 25 seconds
      ws_ping_timeout: 10        # Wait 10s for pong; fail if none arrives
```

These values are read from `extra.get("ws_ping_interval")` in
`gateway/platforms/feishu.py` (line 1561) and applied to the lark-oapi
SDK's WebSocket client via the `_apply_runtime_ws_overrides()` monkey-patch
(lines 1294-1307).

The config.yaml `extra` dict is deep-merged with the env-var-sourced extra
dict (app_id, app_secret, domain, connection_mode) — both sources coexist.

**Verification:**

```bash
# Restart gateway for config to take effect
kill -9 $(systemctl --user show -p MainPID hermes-gateway --no-pager | cut -d= -f2)
sleep 3

# Confirm it reconnected
systemctl --user status hermes-gateway --no-pager | grep active
grep "connected to wss" <(journalctl --user -u hermes-gateway -n 5 --no-pager 2>&1)
```

After fix: the gateway sends a WebSocket PING every 25s. If the connection
goes stale (e.g., laptop sleeps), the PONG times out after 10s, the lark-oapi
SDK fires an error, the gateway detects the platform is disconnected, and
the `_platform_reconnect_watcher` (runs every 10s) reconnects automatically.

Maximum detection time after resume: 25s (ping interval) + 10s (timeout) = ~35s.

**How the code works:**

The Feishu adapter defines default values at class scope (line 387-390):
```python
ws_reconnect_nonce: int = 30
ws_reconnect_interval: int = 120
ws_ping_interval: Optional[int] = None        # < disabled by default
ws_ping_timeout: Optional[int] = None
```

When building settings (line 1561-1562), it reads from `extra`:
```python
ws_ping_interval=_coerce_int(extra.get("ws_ping_interval"), default=None, min_value=1),
ws_ping_timeout=_coerce_int(extra.get("ws_ping_timeout"), default=None, min_value=1),
```

The values are applied at runtime (lines 1298-1307):
```python
setattr(ws_client, "_ping_interval", adapter._ws_ping_interval)
# and
kwargs["ping_interval"] = adapter._ws_ping_interval
```

The built-in auto-reconnect of the lark-oapi WS client is explicitly disabled
after initial connection (`_disable_websocket_auto_reconnect`), and the
gateway's own `_platform_reconnect_watcher` handles reconnection instead.

---

## Error 200340 — app_ticket Invalid

**Meaning:** The lark_oapi SDK's WebSocket connection ticket (app_ticket) has expired or
is invalid. This is the authentication credential the SDK uses behind the scenes for
API calls (sending messages, uploading media, etc.).

**When it happens:**
- After multiple rapid Gateway restarts — the old ticket is stale but the SDK hasn't
  obtained a fresh one
- The Gateway process was stuck in `deactivating (stop-sigterm)` and never completed
  a clean WebSocket close + reconnect cycle
- The app_secret was changed on the Feishu Open Platform but the `.env` file still
  has the old value (also prevents WebSocket connection entirely)
- **Interactive Card buttons clicked without Card Request URL configured** — clicking
  Allow Once / Session / Always / Deny on command approval cards returns 200340

**Symptoms:**
- Feishu client shows a system error with code 200340 after sending a message to the bot
- Bot appears online but replies never arrive
- Clicking approval card buttons returns 200340

**Diagnosis:**

Check the agent log for WebSocket connection details:

```bash
grep "Lark: connected to wss" ~/.hermes/logs/agent.log | tail -5
```

Each line shows:
```
... INFO Lark: connected to wss://msg-frontier.feishu.cn/ws/v2?...
  ...&access_key=...&ticket=<uuid>... [conn_id=...]
```

Look for:
- A `ticket=` UUID — this is the current app_ticket
- The most recent connection timestamp — if it's older than the last Gateway start,
  the ticket may be stale

Also check if the Feishu adapter is actually connected:

```bash
grep "feishu connected" ~/.hermes/logs/gateway.log | tail -3
```

**Fix option 1 (app_ticket expired / gateway stuck deactivating) — Force restart Gateway:**

```bash
# Find the PID
systemctl --user status hermes-gateway --no-pager | grep 'Main PID'

# If service is stuck in "deactivating", force kill
kill -9 <pid>

# Wait for systemd to register the death
sleep 2

# Check service state — if "failed", reset before restart
systemctl --user is-active hermes-gateway.service 2>/dev/null
# If it shows "failed", run:
systemctl --user reset-failed hermes-gateway.service

# Then start fresh
systemctl --user start hermes-gateway.service

# Verify
sleep 8 && systemctl --user status hermes-gateway --no-pager | head -5
```

The new connection will have a different `ticket=` UUID and a new `conn_id=`.

**Why `reset-failed` matters:** When the process was stuck in `deactivating (stop-sigterm)` before SIGKILL, systemd transitions the unit to `failed` state (not `inactive`). Without `reset-failed`, `systemctl start` is rejected — the unit must be reset first. This is distinct from a clean kill where systemd auto-restarts.

**Fix option 2 (Interactive Card buttons) — Configure Feishu Developer Console:**
1. Subscribe to `card.action.trigger` event in Event Subscriptions
2. Enable "Interactive Card" capability toggle in App Features > Bot
3. Configure Card Request URL (auto-handled in WebSocket mode)

**Fix option 3 (Simple workaround) — Disable command approvals entirely:**
```bash
hermes config set approvals.mode off
```
This bypasses the need for Interactive Cards entirely — commands execute without
approval prompts. Best for users who find the Feishu Developer Console configuration
too complex. No Gateway restart needed, takes effect immediately.

**Prevention:**
- Avoid restarting Gateway rapidly — let each shutdown complete fully
- If Gateway is stuck in `deactivating (stop-sigterm)`, always use `kill -9` then
  let systemd auto-restart (don't issue another `systemctl restart`)
- For users who don't want to configure Interactive Cards: just set `approvals.mode off`

---

## Permission Diagnosis — 飞书授权检查方法

**场景：** 确认 bot 的权限是否过多或不足。多开权限有安全风险，少开权限会导致 API 调用失败。

**分析方法：** 检查 Feishu 网关平台代码中实际调用的 HTTP API 端点，反向推导所需 scope。

```bash
# 1. 找到代码中调用的 Feishu Open API 端点
grep -E "\.uri\(|\.v1\.\w+\.(create|get|update|delete|reply)" \
  /usr/local/lib/hermes-agent/gateway/platforms/feishu.py | head -30
```

**常见 API → Scope 映射表：**

| API 调用 | 所需 Scope | 必要性 |
|----------|-----------|--------|
| `im.v1.message.create` / `.reply` / `.get` / `.update` | `im:message` | ✅ 必需 |
| `im.v1.image.create` / `im.v1.message_resource.get` | `im:resource` | ✅ 必需 |
| `im.v1.chat.get` | `im:chat` | ⚠️ 推荐 |
| `im.v1.message_reaction.create` / `.delete` | `im:message.reaction` | ⚠️ 推荐（打字/完成标记） |
| `bot/v3/info` | 无（使用 tenant_access_token 即可） | 内置 |
| `drive/*` / `docx/*` / `contact/*` | 不需要（代码未调用） | ❌ 不开 |

**操作步骤：**

```bash
# 2. 查看当前 .env 中的 App ID
grep FEISHU_APP_ID ~/.hermes/.env

# 3. 在飞书开放平台 (open.feishu.cn) → 应用 → 权限管理
#    按上述表格核对已授权的 scope 列表
#    去掉不需要的 scope（drive、docx、contact 等）
#    发布新版本使权限变更生效
```

**常见问题：**
- 开了 `im:message` 但没开 `im:chat` → `chat.get` 调用返回 230011 或类似错误
- 误开了 `drive:drive` → 虽然不影响功能，但授权过多，建议移除
- 显示 `im:message:send_as_bot` 不是有效的飞书 scope 名，`im:message` 已覆盖

---

## Other Common Errors

### Error 230011 — Message Not Found

The reply target message (the user's message you're replying to) was deleted or
is no longer accessible. The adapter auto-falls back to creating a new message
instead of replying.

No action needed — this is handled internally.

### Error 231003 — Chat ID Invalid

Similar to 230011 — the target chat context expired. Also handled by the
adapter's reply-fallback mechanism.

### Error 10001 — Invalid Auth

The `tenant_access_token` used for the API call is malformed or expired.
Typically transient — the SDK auto-refreshes. If persistent, check that
`FEISHU_APP_SECRET` in `.env` matches the 飞书开放平台 credential page.

---

## Bot Connected but Never Replies — Model API Key 401

**Symptom:** Feishu bot shows as connected (`✓ feishu connected`), WebSocket is alive,
inbound messages are received (visible in gateway.log), but the bot never sends any
## Bot Connected but Never Replies — Model API Key 401 / Quota Exhaustion

**Symptom:** Feishu bot shows as connected (`✓ feishu connected`), WebSocket is alive,
inbound messages are received (visible in gateway.log), but the bot never sends any
replies. The user experiences this as "飞书断联" (Feishu disconnection / bot silent).

**Root cause:** The Feishu WebSocket layer is healthy, but the **model API** is failing.
The Gateway can receive messages but cannot process or respond to them because the
LLM provider returns an authentication error or quota exhaustion.

**Diagnosis — check errors.log or the bot's visible process output first:**

```bash
# Look for 401 or 429 errors
grep -i "401\\|429\\|Authentication Fails\\|insufficient_quota\\|quota" ~/.hermes/logs/errors.log | tail -20

# For profile-based bots, check tmux output:
tmux capture-pane -t <session_name> -p | grep -i "429\\|401\\|quota\\|error"
```

Key error signatures:
- **DeepSeek**: `HTTP 401: Authentication Fails, Your api key: ****xxxx is invalid`
- **OpenRouter**: `HTTP 401: Missing Authentication header`
- **DashScope quota**: `HTTP 429: insufficient_quota — You exceeded your current quota`
- **DashScope rate limit**: `HTTP 429: Throttling.Requests throttling triggered`

### Scenario A: Expired/Rotated API Key

```bash
# Each profile has its own config and .env — all may share the same expired key
for p in ~/.hermes/profiles/*/; do
    echo "=== $(basename $p) ==="
    grep "api_key" "$p/config.yaml" 2>/dev/null | head -1
    grep "OPENAI_API_KEY\\|DEEPSEEK_API_KEY" "$p/.env" 2>/dev/null | head -1
    echo
done
```

**Fix:** Update the API key in ALL affected locations:
1. `~/.hermes/.env` — `OPENAI_API_KEY` or `DEEPSEEK_API_KEY`
2. `~/.hermes/config.yaml` — `model.api_key`
3. Each profile's `.env` and `config.yaml` in `~/.hermes/profiles/<name>/`

Then restart the Gateway (see Scenario C for restart with stale lock files).

**Prevention:** When rotating API keys, update ALL profiles simultaneously.
The Gateway reads keys at startup — a restart is always required.

### Scenario B: Placeholder `***` Never Replaced (Setup-Time Failure)

**Symptom:** Brand-new profile setup or bot configuration. The `.env` file contains
`OPENAI_API_KEY=***` — literally three asterisks. The errors.log may be empty because
the Gateway never even attempts authentication (the key fails on the first API call
and the error may be silently swallowed).

**How this happens:** A template `.env` file was created with `***` as a placeholder
(e.g. by a script or manual copy), but the actual key was never written in. This
differs from an expired key — the key was *never valid*.

**Diagnosis — inspect `.env` directly:**

```bash
# Check the actual value stored, not the terminal-masked output
cat ~/.hermes/.env | grep OPENAI_API_KEY
# Expected: OPENAI_API_KEY=sk-xxxxxxx
# If you see: OPENAI_API_KEY=***  — this is the bug
```

Apply the same check to all profiles:
```bash
for p in ~/.hermes/profiles/*/; do
    val=$(grep "OPENAI_API_KEY\|DEEPSEEK_API_KEY" "$p/.env" 2>/dev/null | cut -d= -f2-)
    echo "$(basename $p): \$val"
done
```

**Fix — write the actual key:**

```bash
# Root config
sed -i 's/OPENAI_API_KEY=***/OPENAI_API_KEY=sk-xxxxxxxxxxxxx/' ~/.hermes/.env

# Each profile
for p in huanglaoxie saodiseng yanqing; do
    sed -i "s/OPENAI_API_KEY=\*\*\*/OPENAI_API_KEY=sk-xxxxxxxxxxxxx/" \
        ~/.hermes/profiles/\$p/.env
done
```

Then continue with Scenario C (stale lock cleanup + restart).

### Scenario C: Restart After Key Fix — Stale Lock Files Block Startup

After updating the key, the Gateway may still fail to start if stale `gateway.lock`
and `gateway.pid` files remain from the previous (now-dead) process.

**Symptom:** `hermes -p <profile> gateway run --replace` hangs, or the new process
warns about another gateway using the same app_id.

**Diagnosis:**

```bash
ls -la ~/.hermes/profiles/<name>/gateway.{lock,pid} 2>/dev/null
```

**Fix — clean locks and restart:**

```bash
for p in huanglaoxie saodiseng yanqing; do
    rm -f ~/.hermes/profiles/\$p/gateway.lock ~/.hermes/profiles/\$p/gateway.pid
done

# For bash-loop managed gateways:
pkill -9 -f 'hermes_cli.main gateway'
sleep 3
# Then start fresh (e.g. in tmux sessions)
```

**Verification:**

```bash
# Check each profile's gateway.log for connection and a test response
for p in huanglaoxie saodiseng yanqing; do
    echo "=== \$p ==="
    grep "feishu connected" ~/.hermes/profiles/\$p/logs/gateway.log 2>/dev/null | tail -1
done

# After sending a test message, confirm actual replies:
grep "response ready" ~/.hermes/profiles/*/logs/gateway.log | tail -5
```

**Prevention:** Always clean `gateway.lock` and `gateway.pid` when setting up a profile
for the first time or after a hard kill. The Gateway creates these files at startup
and may fail if stale ones remain from a previous, non-cleanly-shutdown process.

### Scenario D: DashScope / Aliyun Model Free Quota Exhausted

**Symptom:** Bot connects (`✓ feishu connected`), receives messages, but the agent's
API call fails with `HTTP 429: insufficient_quota — You exceeded your current quota`.

**Root cause:** DashScope's premium models (qwen3.5-omni-plus, qwen3.7-max, etc.)
have very limited free quota on new accounts. The model works briefly then hits
the quota ceiling.

**Diagnosis:**

Check the bot's visible output (tmux or journalctl) for:
```
HTTP 429: You exceeded your current quota
```

Check which model is configured:
```bash
grep "default:" ~/.hermes/profiles/<name>/config.yaml
```

**Fix — switch to a model with available free quota:**

From the `dashscope-provider-setup.md` reference:

| Tier | Model | Free quota |
|------|-------|-----------|
| 🟢 Abundant | `qwen-turbo-latest`, `qwen-vl-max` | Stable free tier |
| 🟡 Limited | `qwen3.5-omni-flash`, `qwen3-vl-flash` | Smaller free pool |
| 🔴 Premium | `qwen3.5-omni-plus`, `qwen3.7-max` | Near zero — requires充值 |

Quick fix:
```bash
# Edit the profile's config.yaml
sed -i 's/qwen3.5-omni-plus/qwen-vl-max/' ~/.hermes/profiles/<name>/config.yaml

# Clean stale locks
rm -f ~/.hermes/profiles/<name>/gateway.{lock,pid}

# Restart gateway
tmux kill-session -t <name> 2>/dev/null
tmux new-session -d -s <name> '/home/hermes/start_<name>.sh'
```

**Prevention:** When first setting up DashScope, prefer `qwen-vl-max` (vision) and
`qwen-turbo-latest` (text) — these have reliable free tiers. Reserve premium
qwen3.x models for accounts with充值余额.

---

## OPENAI_BASE_URL Conflict

**Symptom:** Warnings like `OPENAI_BASE_URL is set (https://tokenhub.tencentmaas.com/v1)
but model.provider is 'deepseek'` in errors.log. Auxiliary clients may route to the
wrong endpoint.

**Root cause:** The `.env` file has `OPENAI_BASE_URL` pointed at one provider
(e.g., Tencent TokenHub), but `model.provider` in `config.yaml` is set to a
different provider (e.g., `deepseek`). The `OPENAI_BASE_URL` env var overrides the
base URL for ALL OpenAI-compatible clients, including auxiliary tasks (vision,
compression, session_search).

**Diagnosis:**

```bash
grep "OPENAI_BASE_URL" ~/.hermes/.env
grep "provider:" ~/.hermes/config.yaml | head -5
```

**Fix option 1 — Remove OPENAI_BASE_URL if not using a custom endpoint:**

```bash
sed -i '/^OPENAI_BASE_URL=/d' ~/.hermes/.env
```

**Fix option 2 — Use the correct base_url in config.yaml instead:**

```bash
# Set base_url per-model in config.yaml (doesn't conflict with provider)
hermes config set model.base_url https://api.deepseek.com
```

Restart Gateway after changes.

---

## Gateway Hangs After API Key Rotation — 100% CPU / No Output

**Symptom:** After updating the API key and restarting the Gateway (killing the old process),
the new Gateway process consumes ~100% CPU with very low memory (~27MB vs normal 350MB+),
produces ZERO log output, and times out if run manually in foreground. The systemd service
shows `activating (auto-restart)` but never reaches `active (running)`.

**Root cause:** A stale Gateway process from a manual foreground run (or from a bash loop
that wasn't fully killed) already holds the Feishu WebSocket connection. The new Gateway
tries to connect to the same Feishu app but the WebSocket is locked by the old process.
The lark-oapi SDK hangs in its connection loop without logging anything.

**Diagnosis — use `hermes gateway status`:**

```bash
hermes gateway status
```

Key indicators:
- `⚠ feishu: Another local Hermes gateway is already using this Feishu app_id (PID XXXXX).`
- `⚠ Gateway process is running for this profile, but the service is not active`
- `PID(s): XXXXX, YYYYY` — lists ALL gateway processes, including hung ones

This command is the single best diagnostic for this scenario — it reveals both the
Feishu WebSocket contention and the process PIDs.

**Fix:**

```bash
# 1. Kill ALL gateway processes (not just the systemd one)
pkill -9 -f 'hermes_cli.main gateway'

# 2. Wait for cleanup
sleep 3

# 3. Verify nothing is left
hermes gateway status

# 4. Start fresh
hermes gateway start

# 5. Verify it connects
sleep 10 && grep "feishu connected" ~/.hermes/logs/gateway.log | tail -1
```

**Prevention:** After killing old gateways for key rotation, always kill ALL gateway
processes (not just the most recent one) and verify with `hermes gateway status` before
starting a new one. The `pkill -9 -f` pattern is safer than targeting individual PIDs.

---

## Batch API Key Replacement — All Profiles

**When:** The model API key expires or is rotated. The same key often appears in the
main `config.yaml`, main `.env`, and every profile's `config.yaml` and `.env`.

**Find all locations with the old key:**

```bash
grep -rl 'sk-d1a' ~/.hermes/config.yaml ~/.hermes/.env ~/.hermes/profiles/*/config.yaml ~/.hermes/profiles/*/.env 2>/dev/null
```

**Batch replace in one pass:**

```bash
NEW_KEY="sk-436ff33338ba4404b4d6218048976286"

for f in \
  ~/.hermes/config.yaml \
  ~/.hermes/.env \
  ~/.hermes/profiles/saodiseng/config.yaml ~/.hermes/profiles/saodiseng/.env \
  ~/.hermes/profiles/huanglaoxie/config.yaml ~/.hermes/profiles/huanglaoxie/.env \
  ~/.hermes/profiles/yanqing/config.yaml ~/.hermes/profiles/yanqing/.env; do
  [ -f "$f" ] && sed -i "s/sk-OLD_PREFIX[^\"' ,}]*/$NEW_KEY/g" "$f" && echo "✓ $f"
done
```

Replace `sk-OLD_PREFIX` with the first 8 chars of the old key (e.g., `sk-d1a`), and
`$NEW_KEY` with the full new key. The regex `[^"' ,}]*` matches the rest of the key
up to any YAML/shell delimiter.

**Verify:**

```bash
grep -r 'sk-436' ~/.hermes/config.yaml ~/.hermes/profiles/*/config.yaml ~/.hermes/profiles/*/.env 2>/dev/null | wc -l
# Should match the number of locations found above
```

**Post-replacement:** Kill ALL gateway processes and restart (see "Gateway Hangs After
API Key Rotation" above). The Gateway reads keys at startup — a restart is mandatory.

---

## Quick Diagnostic Commands

```bash
# Recent connection activity
grep -E "feishu.*connect|Lark: connected" ~/.hermes/logs/agent.log | tail -5

# Any Feishu-related errors in the last 100 lines
grep -i "feishu.*error" ~/.hermes/logs/gateway.log | tail -10

# Message flow — are messages being received and sent?
grep -E "Inbound dm|Sending response" ~/.hermes/logs/gateway.log | tail -10

# Gateway process health
systemctl --user status hermes-gateway --no-pager

# Check for laptop hibernation events (S4 sleep)
journalctl -k --no-pager | grep "RTC can wake from S4" | tail -5

# Verify WebSocket keepalive is configured
grep "ws_ping_interval" ~/.hermes/config.yaml
```

---

## Bitable Field PUT — Option ID Rebuild Data Loss

**Symptom:** After using PUT to update a field's options array in a Bitable
SingleSelect field, existing records lose their values. The field shows
blank for every record, even though the option names haven't changed.

**Root cause:** PUT to `/bitable/v1/apps/{t}/tables/{t}/fields/{f}`
replaces the entire field definition. New options get new internal IDs.
Existing records still reference the old IDs — render as blank.
PATCH returns 404; PUT is the only supported method.

**Prevention — two-step field option management:**

1. **Migrate records first** — Update records by option NAME (not ID):
   `PUT /records/{id} {"fields": {"状态": "✅ 已完成"}}`
2. **Then replace the field** — PUT with complete field def including
   `field_name`, `type` (3=SingleSelect), `ui_type` ("SingleSelect"),
   and `property.options`. Required fields: field_name, type, ui_type, property.options.

**Recovery from data loss:**
- Re-fetch all records (non-select fields readable)
- Reconstruct classification from context (title, content, URL)
- Re-write each record with correct option NAME
- New option IDs assigned automatically

**Key insight:** Option NAMES are the stable identifier for record writes.
Field definitions use internal IDs that break on PUT.
