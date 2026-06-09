# Feishu (飞书) Gateway Setup

Connecting Hermes Agent to Feishu via WebSocket (WebSocket mode is simpler
than webhook — no public URL needed).

## Dependencies

Already bundled in the Hermes venv. If missing:

```bash
/usr/local/lib/hermes-agent/venv/bin/python3 -m pip install lark-oapi aiohttp websockets
```

## Environment Variables

Set in `~/.hermes/.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `FEISHU_APP_ID` | **Yes** | From 飞书开放平台 → 凭证与基础信息 |
| `FEISHU_APP_SECRET` | **Yes** | From 飞书开放平台 → 凭证与基础信息 |
| `FEISHU_DOMAIN` | No | `feishu` (飞书) or `lark` (国际版). Default: `feishu` |
| `FEISHU_CONNECTION_MODE` | No | `websocket` (default, recommended) or `webhook` |
| `FEISHU_VERIFICATION_TOKEN` | No | For webhook mode event verification |
| `FEISHU_ENCRYPT_KEY` | No | Event encryption key (webhook mode) |
| `FEISHU_GROUP_POLICY` | No | `open` / `allowlist` / `mention` / `disabled`. Default: `allowlist` |
| `FEISHU_DM_POLICY` | No | `open` (default) / `disabled` |
| `FEISHU_ALLOWED_USERS` | No | Comma-separated user IDs for allowlist policy |
| `GATEWAY_ALLOW_ALL_USERS` | No | Set `true` to bypass allowlist entirely |

## Setup Flow (Step by Step)

### 1. Create Feishu App

Go to https://open.feishu.cn/app → **Create 企业自建应用**.

### 2. Get Credentials

In app dashboard → 左侧「凭证与基础信息」→ copy:
- **App ID** (`cli_...`)
- **App Secret**

### 3. Configure Permissions (授权最小化)

左侧「权限管理」→ add these scopes. 按最小授权原则只开代码实际需要的：

**必需（必须开启）：**
- `im:message` — 收发消息（核心功能）
- `im:resource` — 上传/下载消息中的图片和文件

**推荐（代码使用了，建议开启）：**
- `im:chat` — 读取群聊信息（用于 `im.v1.chat.get`，检查群是否存在）
- `im:message.reaction` — 添加/移除表情反应（用于打字指示器和完成状态标记）

**不需要（代码没用到）：**
- `drive:*` — 云文档/云空间访问
- `docx:*` — 文档读写
- `contact:*` — 通讯录/员工信息
- `calendar:*`、`mail:*`、`sheet:*`
- `im:message:send_as_bot` — 飞书没有这个独立的 scope，`im:message` 已涵盖

> **验证方法：** 代码实际调用的 API 对应的权限通过检查 `gateway/platforms/feishu.py` 中的 `.uri()` 和 `.v1.*` 调用确定。

Click 批量开通/确认.

### 4. Enable Bot

左侧「应用功能」→ **机器人** → toggle ON. Configure bot name/avatar.

### 5. Publish App (CRITICAL — most commonly missed!)

「版本管理与发布」→ **创建版本** → fill in version number → save → **点「申请发布」**.

**Without publishing, only the app admin can see/find the bot.**
This is separate from the bot toggle in step 4.

### 6. Configure Hermes

```bash
# Add credentials to .env
echo 'FEISHU_APP_ID=cli_xxxxxxxxxxxx' >> ~/.hermes/.env
echo 'FEISHU_APP_SECRET=xxxxxxxxxxxxxx' >> ~/.hermes/.env
echo 'FEISHU_DOMAIN=feishu' >> ~/.hermes/.env

# Enable feishu platform
hermes config set platforms.feishu.enabled true

# Add allow-all if desired
echo 'GATEWAY_ALLOW_ALL_USERS=true' >> ~/.hermes/.env

# Restart gateway
hermes gateway restart
```

### 7. Verify Connection

```bash
grep -i feishu ~/.hermes/logs/gateway.log | tail -5
# Should see: ✓ feishu connected
```

## Pitfalls

- **Bot not findable in Feishu client**: Check app is PUBLISHED (step 5), not just that the bot toggle is on. 已发布 ≠ 已启用.
- **Bot can't initiate conversations**: Feishu bots cannot DM users first. The user must send the first message ("你好").
- **No channels in send_message list**: Happens until at least one user messages the bot.
- **DeepSeek models can't analyze images**: Vision analysis fails on DeepSeek provider. Use a Gemini or Claude model for image tasks.
- **pip externally-managed error**: Use the hermes venv: `/usr/local/lib/hermes-agent/venv/bin/python3 -m pip install ...`
- **DeepSeek API 400 on image input**: The DeepSeek API doesn't support `image_url` message parts. Vision tools will return errors.
