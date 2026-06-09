# 腾讯云 TokenHub Provider Setup

TokenHub（令牌服务）是腾讯云提供的模型网关服务，通过 OpenAI 兼容的 API 提供多种模型（DeepSeek、混元、GLM、Kimi、MiniMax 等）的调用能力。

## API 地址

**注意：** TokenHub 有多个域名，以下为已验证可用的：

| 用途 | 地址 |
|------|------|
| 主 API 端点 | `https://tokenhub.tencentmaas.com/v1` |
| 备选端点 | `https://api.tokenhub.cloud.tencent.com/v1`（可能更旧） |

实际生产中 `tokenhub.tencentmaas.com` 已验证可用且模型最全。

## 认证方式

TokenHub 的 OpenAI 兼容 API **不支持**直接使用腾讯云 SecretId/SecretKey 认证。需要先在 TokenHub 控制台创建一个 **API Key（令牌）**，通过 Bearer Token 方式传入：

```
Authorization: Bearer <your-api-key>
```

### 配置方式

在 Hermes 的 `config.yaml` 中：

```yaml
model:
  default: deepseek-v4-flash
  provider: custom
  base_url: https://tokenhub.tencentmaas.com/v1
  api_key: <your-tokenhub-api-key>
```

或者通过 CLI 命令：

```bash
hermes config set model.default deepseek-v4-flash
hermes config set model.provider custom
hermes config set model.base_url https://tokenhub.tencentmaas.com/v1
hermes config set model.api_key <your-tokenhub-api-key>
```

### 创建 API Key 步骤

1. 打开 https://console.cloud.tencent.com/tokenhub
2. 使用 SecretId/SecretKey 登录
3. 在控制台找到"创建令牌/API Key"的入口
4. 生成一个 API Key
5. 将生成的 Key 复制出来用于配置

### 可用模型（实测验证）

以下为通过 TokenHub 实测可用的模型名称（2026-05）：

| 模型 ID | 说明 | 视觉 | 工具调用 | 注意 |
|---------|------|:---:|:--------:|:----|
| `deepseek-v4-flash` | DeepSeek V4 Flash | ❌ | ✅ | 速度最快，推荐默认 |
| `deepseek-v4-pro` | DeepSeek V4 Pro | ❌ | ✅ | 更强但更慢 |
| `deepseek-v3.2` | DeepSeek V3.2 | ❌ | ✅ | 搜索型智能体 |
| `deepseek-r1-0528` | DeepSeek R1 推理 | ❌ | ✅ | 需推理 |
| `kimi-k2.6` | Kimi K2.6 全能 | ❌ | ✅ | 仅支持 temperature=1 |
| `kimi-k2.5` | Kimi K2.5 | ❌ | ✅ | 开源多模态 |
| `glm-5` | GLM-5 | ❌ | ✅ | 复杂工程主力 |
| `glm-5v-turbo` | GLM-5V Turbo 视觉 | ✅ | ✅ | 截图/UI→代码 |
| `glm-5-turbo` | GLM-5 Turbo 工具链 | ❌ | ✅ | ⚠️ 需额外开通套餐 |
| `minimax-m2.7` | MiniMax M2.7 | ❌ | ✅ | 办公文档PPT首选 |
| `minimax-m2.5` | MiniMax M2.5 | ❌ | ✅ | 成本敏感批量 |
| `hy3-preview` | Hy3 Preview | ❌ | ✅ | 腾讯生态适配 |

> **⚠️ 不同 API Key 的模型权限不同** — 以上列表中每个模型都需要在 TokenHub 控制台单独购买/开通。你的某个 API Key 可能只开通了部分模型（例如只有一个 `deepseek-v4-flash`）。开通新模型后无需更换 API Key，TokenHub 会自动授权。

**模型参数注意事项：**
- `kimi-k2.6` 只接受 `temperature=1`，传其他值会报 `400001`
- `/v1/models` 端点返回 404 — 无法通过 API 列举模型，只能通过 curl 逐模型测试
- 测试方法：`curl -s -X POST 'https://tokenhub.tencentmaas.com/v1/chat/completions' -H 'Authorization: Bearer <key>' -H 'Content-Type: application/json' -d '{"model":"<model-id>","messages":[{"role":"user","content":"hi"}],"max_tokens":1}'`
  - HTTP 200 = 该 Key 可用此模型
  - HTTP 400 + `"model not found"` = 该 Key 未开通此模型

### WB models.json 配置格式

如果要将 TokenHub 模型配置到 WorkBuddy 的 `models.json`，使用以下格式：

```json
{
  "id": "kimi-k2.6",
  "name": "TokenHub - Kimi K2.6",
  "vendor": "tencent-tokenhub",
  "url": "https://tokenhub.tencentmaas.com/v1/chat/completions",
  "apiKey": "<your-tokenhub-api-key>",
  "maxOutputTokens": 8192,
  "supportsToolCall": true,
  "supportsImages": false,
  "supportsReasoning": false
}
```

视觉模型需要设置 `"supportsImages": true`。

## 切换到 TokenHub 后的注意事项

- 修改配置后，Gateway 需要重启（在飞书发 `/restart`）才能生效
- 如果 TokenHub 模型支持 vision（如 `glm-5v-turbo`），则 `vision_analyze` 工具可以使用
- TokenHub 的响应延迟取决于所选模型，与 DeepSeek 直连可能不同
- `.env` 中的 `OPENAI_BASE_URL` 也需要同步更新，否则某些组件可能使用旧端点

## 额度耗尽恢复流程

TokenHub 免费额度用完后，模型调用会返回 HTTP 402/403 错误。

### 症状

```
HTTP 402: endpoint is inactive: FREE_QUOTA_EXHAUSTED
HTTP 403: endpoint is inactive: NO_FREE_PACKAGE
```

### 恢复步骤（切回 DeepSeek 直连）

```bash
# 1. 主实例
hermes config set model.base_url https://api.deepseek.com
hermes config set model.api_key sk-your-deepseek-key
sed -i 's|^OPENAI_BASE_URL=.*|OPENAI_BASE_URL=https://api.deepseek.com|' ~/.hermes/.env

# 2. 每个 Profile — 检查各自用了什么 key
for p in saodiseng huanglaoxie yanqing; do
    hermes config set model.base_url https://api.deepseek.com --profile $p
    # 注意：不同 profile 可能用不同的 key！
    # 先检查再设置
done

# 3. 重启所有网关
# 主网关：在飞书发 /restart
# Bot 网关：重启对应的 tmux / background 进程
```

### 预防

- 在 TokenHub 控制台为关键模型（Kimi K2.6、GLM-5 等）购买付费套餐
- 保留 DeepSeek 直连 Key 作为 fallback
- 不要使用主 Hermes 实例大量探测陌生模型（会快速耗尽免费额度）
