# NVIDIA NIM — OpenAI-Compatible Probe Findings (2026-06-01)

## Base URL / Endpoint

NIM exposes an OpenAI-compatible API at `https://integrate.api.nvidia.com/v1`.  
Use the standard `chat/completions` path (`/v1/chat/completions`), same payload shape as OpenAI/DeepSeek.

## Auth

Header: `Authorization: Bearer $NVIDIA_API_KEY`  
`NVIDIA_API_KEY` values start with `nvapi-`.  
No `OPENAI_API_KEY` or other alias is needed for NIM.

## Model naming convention

NIM models are namespaced: `vendor/model-name`.  
Examples observed during probe:
- `deepseek-ai/deepseek-v4-pro`
- `deepseek-ai/deepseek-v4-flash`
- `stepfun-ai/step-3.5-flash`
- `stepfun-ai/step-3.7-flash`

List with: `curl $NIM_BASE/models` (returns 200 without auth for catalog).

## Response shape quirk: `reasoning_content`

When calling NIM Step models, the response may contain:
- `message.content` — `null` when the model emitted a reasoning trace
- `message.reasoning_content` — the actual assistant text
- `finish_reason: "length"` — often means `max_tokens` too small for the reasoning + answer

Get the real text with:
```python
msg = data["choices"][0]["message"]
text = msg["content"] or msg["reasoning_content"]
```

If `text` is still `None` and `finish_reason == "length"`, increase `max_tokens`.

## Hermes config for NIM

Use `provider: custom` (or a named provider with matching `base_url`):
```yaml
model:
  provider: custom
  default: deepseek-ai/deepseek-v4-pro
providers:
  nvidia-nim:
    api_key_env: NVIDIA_API_KEY
    base_url: https://integrate.api.nvidia.com/v1
    models:
      - deepseek-ai/deepseek-v4-pro
      - deepseek-ai/deepseek-v4-flash
      - stepfun-ai/step-3.5-flash
```

Hermes classifies it as `custom` because there is no dedicated NIM plugin under `plugins/model-providers/nvidia-nim/`, but the generic chat_completions adapter handles it fine.

## Network quirks observed (WSL)

- `integrate.api.nvidia.com` may time out at 30 s on some WSL networks, while the model catalog (`/v1/models`) is reachable in ~1-2 s.  
- If inference times out but catalog pings fine: retry `chat/completions`, try a different model (`step-3.5-flash` responded in ~4 s on 2026-06-01), or check local DNS/gateway.  
- DeepSeek-official (`api.deepseek.com`) and NIM are completely separate; try one before concluding the other is down.
