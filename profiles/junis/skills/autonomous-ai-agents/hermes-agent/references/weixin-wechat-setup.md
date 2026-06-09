# WeChat (Weixin) Gateway Setup

Connecting Hermes Agent to personal WeChat via Tencent's iLink Bot API.

## Prerequisites

```bash
pip install aiohttp cryptography qrcode
```

- `aiohttp` — HTTP client for iLink API (long-polling + send)
- `cryptography` — AES-128-ECB for CDN media encryption
- `qrcode` — Terminal ASCII QR rendering (optional; falls back to URL)

## Environment Variables

Set in `~/.hermes/.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `WEIXIN_ACCOUNT_ID` | Yes | iLink bot ID returned from QR login |
| `WEIXIN_TOKEN` | Yes | Bearer token returned from QR login |
| `WEIXIN_BASE_URL` | No | Default: `https://ilinkai.weixin.qq.com` |
| `WEIXIN_CDN_BASE_URL` | No | Default: `https://novac2c.cdn.weixin.qq.com/c2c` |
| `WEIXIN_DM_POLICY` | No | `open` / `pairing` / `allowlist` / `disabled` (default: `open`) |
| `WEIXIN_GROUP_POLICY` | No | Default: `disabled` (iLink bots can't join ordinary groups) |
| `WEIXIN_ALLOWED_USERS` | No | Comma-separated user IDs (when policy is `allowlist`) |
| `WEIXIN_SEND_CHUNK_DELAY_SECONDS` | No | Delay between multi-chunk sends (default: `1.5`) |

## Setup Flow

### Quick Start

```bash
hermes gateway setup
# → Select "Weixin" from the platform menu
# → Terminal shows ASCII QR code
# → Scan with WeChat app
# → Confirm in WeChat
# → Choose DM authorization policy
```

### Programmatic Login

```python
import asyncio
from gateway.platforms.weixin import qr_login
from hermes_constants import get_hermes_home

credentials = asyncio.run(qr_login(str(get_hermes_home())))
# Returns: {"account_id": "...", "token": "...", "base_url": "...", "user_id": "..."}
```

### After Login

```bash
# Enable platform in config
hermes config set platforms.weixin.enabled true

# Start gateway
hermes gateway run
```

## WeChat vs WeCom (企业微信)

Two separate adapters, different setup paths:

| | Weixin (微信) | WeCom (企业微信) |
|---|---|---|
| Adapter file | `gateway/platforms/weixin.py` | `gateway/platforms/wecom.py` |
| Auth method | QR code login | bot_id + secret |
| Transport | HTTP long-poll | WebSocket |
| Group support | Limited (iLink bot identity) | Yes |
| Gateway setup | Select "Weixin" | Select "WeCom" |
| Key env vars | `WEIXIN_ACCOUNT_ID` + `WEIXIN_TOKEN` | `WECOM_BOT_ID` + `WECOM_SECRET` |

## Limitations

- **Message editing**: Not supported (WeChat doesn't allow editing sent messages). Streaming falls back to send-final-only so the cursor (▉) is never left visible.
- **Group messages**: iLink bot identities (e.g. `...@im.bot`) can't be invited into ordinary WeChat groups. The adapter logs a warning if `WEIXIN_GROUP_POLICY` is not `disabled`.
- **Max message**: 2000 characters per chunk.
- **Credentials persisted** at `~/.hermes/weixin/accounts/<account_id>.json` with `0o600` permissions.