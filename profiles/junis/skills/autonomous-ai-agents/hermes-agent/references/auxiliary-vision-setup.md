# Auxiliary Vision Model Setup

Configure a secondary vision-capable model for image analysis while keeping a different model as the main conversation engine.

## Pattern: DeepSeek (main) + DashScope/Qwen (vision)

This is the most common setup for Chinese users who want DeepSeek's strong reasoning as the primary model but need image input support.

### 1. Add API Key

```bash
# .env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. Configure Auxiliary Vision

```bash
hermes config set auxiliary.vision.provider custom
hermes config set auxiliary.vision.model <model-name>
hermes config set auxiliary.vision.base_url https://dashscope.aliyuncs.com/compatible-mode/v1
hermes config set auxiliary.vision.api_key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Model Recommendations (DashScope, 2026-05)

| Tier | Model | Notes |
|------|-------|-------|
| 🏆 Best | `qwen3.5-omni-plus` | Latest multimodal flagship (vision+text+audio) |
| ⭐ Great | `qwen3.5-omni-flash` | Lighter, faster multimodal |
| ✅ Good | `qwen3-vl-plus` | Pure vision-language, no audio |
| ✅ Good | `qwen3-vl-flash` | Fast pure vision |
| ⚠️ Legacy | `qwen-vl-max` | Previous gen, still works |

### 4. Restart Gateway

```bash
hermes gateway restart
```

The new vision model is used for `vision_analyze` tool calls — triggered automatically when images are attached in conversation.

## How It Works

- **Main model** (e.g. `deepseek-v4-flash`): handles all text conversation, reasoning, tool calls
- **Auxiliary vision**: activated only when `vision_analyze` tool is called (user sends an image)
- The auxiliary model processes the image and returns a text description, which the main model then uses in its response

## Model Discovery — Query DashScope API Directly

To list all available Qwen models (including new releases not in this doc), call the DashScope OpenAI-compatible models endpoint:

```python
import urllib.request, json

url = "https://dashscope.aliyuncs.com/compatible-mode/v1/models"
req = urllib.request.Request(url, headers={
    "Authorization": "Bearer $DASHSCOPE_API_KEY"
})
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
models = [m["id"] for m in data.get("data", []) if "qwen" in m["id"].lower()]
for m in sorted(models):
    print(m)
```

Latest Qwen model naming conventions (as of May 2026):
- **qwen3.x** = generation (qwen3.7 = May 2026, qwen3.6 = Apr 2026, qwen3.5 = Feb 2026)
- **plus** = flagship (e.g., qwen3.6-plus, qwen3.5-plus)
- **max** = premium (e.g., qwen3.7-max, qwen3-max)
- **flash** = lightweight/fast
- **omni** = multimodal (vision + text + audio)
- **vl** = vision-language only
- **coder** = code-specialized
- **math** = math-specialized

## Verify

Send an image in Feishu or CLI and check that the vision model responds without error. Common failure modes:

- **Model doesn't support images**: `unknown variant 'image_url', expected 'text'` → switch to a VL/omni model
- **401 Unauthorized**: API key missing or wrong provider base_url
- **Rate limited**: Upgrade DashScope tier or switch to a cheaper model (qwen-turbo-latest for text, keep VL for images)
