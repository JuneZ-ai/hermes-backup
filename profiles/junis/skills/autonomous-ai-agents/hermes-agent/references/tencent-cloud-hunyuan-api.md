# Tencent Cloud Hunyuan / TokenHub API

> **Status:** TokenHub (腾讯云令牌服务) has been deprecated and merged into Tencent Cloud Hunyuan (混元大模型) API as of late 2024. The old `api.tokenhub.cloud.tencent.com` domain no longer resolves. Use the Hunyuan API endpoint instead.

## API Endpoint

| Region | Endpoint |
|--------|----------|
| China Mainland | `https://api.hunyuan.cloud.tencent.com/v1` |
| Global (Intl) | `https://api.hunyuan.intl.cloud.tencent.com/v1` |

## Authentication

### ❌ Don't use SecretId/SecretKey directly

The Tencent Cloud API credentials (SecretId + SecretKey) are **NOT** accepted directly as the Bearer token. The API returns:

```
{"error":{"message":"Incorrect API key provided...", "code":"invalid_api_key"}}
```

### ✅ Create a Hunyuan API Key

1. Go to https://console.cloud.tencent.com/hunyuan/start
2. Navigate to **API Key Management** (API密钥管理)
3. Create a new API key
4. Use the generated key as the Bearer token

### Usage with OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="<your-hunyuan-api-key>",  # NOT SecretId/SecretKey
    base_url="https://api.hunyuan.cloud.tencent.com/v1"
)

response = client.chat.completions.create(
    model="hunyuan-turbo",  # or hunyuan-pro, hunyuan-lite, etc.
    messages=[{"role": "user", "content": "Hello"}]
)
```

### cURL test

```bash
curl https://api.hunyuan.cloud.tencent.com/v1/chat/completions \
  -H "Authorization: Bearer <your-hunyuan-api-key>" \
  -H "Content-Type: application/json" \
  -d '{"model": "hunyuan-turbo", "messages": [{"role": "user", "content": "Hello"}]}'
```

## Supporting Models

Hunyuan API supports multiple models via the OpenAI-compatible interface:

| Model | Type | Notes |
|-------|------|-------|
| `hunyuan-turbo` | Chat | Fast, latest |
| `hunyuan-pro` | Chat | Production-grade |
| `hunyuan-lite` | Chat | Lightweight, free tier |
| `hunyuan-vision` | Vision | Image understanding |
| `hunyuan-role` | Role-play | Character-based |
| `hunyuan-code` | Code | Code generation |

List available models: `curl -H "Authorization: Bearer <key>" https://api.hunyuan.cloud.tencent.com/v1/models`

## WSL DNS Issue

When calling `api.hunyuan.cloud.tencent.com` from WSL (Windows Subsystem for Linux), the DNS resolver is the Windows-side proxy at `172.24.0.1` by default. This proxy should resolve Tencent Cloud domains correctly since Windows DNS handles it through the host OS.

If DNS resolution fails, the most likely cause is:
1. The API key is invalid (the endpoint IS resolvable — try `curl -v`)
2. A VPN/firewall is blocking the connection
3. The user has an old cached negative DNS result

To test DNS from WSL:
```bash
python3 -c "import socket; print(socket.getaddrinfo('api.hunyuan.cloud.tencent.com', 443))"
```

## Migration from TokenHub

If a user previously used TokenHub:

1. **Credentials:** Old TokenHub AK/SK pairs (format: `ak-...` / `sk-...`) are **NOT** compatible with Hunyuan API. User must create a new key in Hunyuan console.
2. **Endpoint:** Change `base_url` from `https://api.tokenhub.cloud.tencent.com/v1` to `https://api.hunyuan.cloud.tencent.com/v1`
3. **Models:** TokenHub proxied third-party models (GPT-4, Claude); Hunyuan serves native Tencent models plus some third-party models through the same API.
4. **Auth format:** Both use `Authorization: Bearer <key>` header (OpenAI-compatible).
