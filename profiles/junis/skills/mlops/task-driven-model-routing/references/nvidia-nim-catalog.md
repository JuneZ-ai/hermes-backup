# NVIDIA NIM 模型目录（2026-06-02 实测）

> 端点：`https://integrate.api.nvidia.com/v1`
> Auth: `OPENAI_API_KEY`
> 注意：模型列表会变化，建议定期用 `curl` 刷新

## 免费可用的关键模型

### DeepSeek 系列（重点 — 与付费版同模型）

| NIM 模型 ID | 对应 DeepSeek 官方名 | 质量 | 推荐场景 |
|-------------|-------------------|------|---------|
| `deepseek-ai/deepseek-v4-flash` | `deepseek-v4-flash` | ⭐⭐⭐⭐ | 日常对话、执行任务、中等推理 |
| `deepseek-ai/deepseek-v4-pro` | `deepseek-v4-pro` | ⭐⭐⭐⭐⭐ | 深度分析、复杂推理、思辨 |
| `deepseek-ai/deepseek-coder-6.7b-instruct` | — | ⭐⭐⭐ | 代码补全（小模型） |

### Meta Llama 系列

| NIM 模型 ID | 参数量 | 质量 | 推荐场景 |
|-------------|-------|------|---------|
| `meta/llama-4-maverick-17b-128e-instruct` | 17B MoE | ⭐⭐⭐⭐ | 通用对话、创意 |
| `meta/llama-3.3-70b-instruct` | 70B | ⭐⭐⭐⭐ | 通用推理、长文 |
| `meta/llama-3.1-70b-instruct` | 70B | ⭐⭐⭐⭐ | 通用推理 |
| `meta/llama-3.1-8b-instruct` | 8B | ⭐⭐⭐ | 简单任务、快速响应 |
| `meta/llama-3.2-90b-vision-instruct` | 90B | ⭐⭐⭐⭐ | 视觉理解 |
| `meta/llama-3.2-11b-vision-instruct` | 11B | ⭐⭐⭐ | 轻量视觉 |

### Mistral 系列

| NIM 模型 ID | 参数量 | 推荐场景 |
|-------------|-------|---------|
| `mistralai/mistral-large-3-675b-instruct-2512` | 675B | 最强推理（慢） |
| `mistralai/mistral-large` | — | 强推理 |
| `mistralai/mistral-small-4-119b-2603` | 119B | 性价比推理 |
| `mistralai/mixtral-8x22b-v0.1` | 141B MoE | 多语言、推理 |

### Qwen 系列（中文优势）

| NIM 模型 ID | 参数量 | 推荐场景 |
|-------------|-------|---------|
| `qwen/qwen3.5-122b-a10b` | 122B | 中文推理、复杂任务 |
| `qwen/qwen3.5-397b-a17b` | 397B | 极致中文推理（慢） |
| `qwen/qwen3-coder-480b-a35b-instruct` | 480B | 代码生成 |

### StepFun 系列

| NIM 模型 ID | 推荐场景 |
|-------------|---------|
| `stepfun-ai/step-3.7-flash` | 执行任务（燕青默认） |
| `stepfun-ai/step-3.5-flash` | 轻量兜底 |

### NVIDIA 自有优化模型

| NIM 模型 ID | 说明 |
|-------------|------|
| `nvidia/llama-3.3-nemotron-super-49b-v1.5` | NVIDIA 优化的 Llama |
| `nvidia/llama-3.1-nemotron-ultra-253b-v1` | 超大规模推理 |
| `nvidia/llama-3.1-nemotron-70b-instruct` | NVIDIA 优化的 70B |

## 模型选择策略

### 按任务类型

| 任务 | 推荐 NIM 模型 | 理由 |
|------|-------------|------|
| 日常对话 | `deepseek-ai/deepseek-v4-flash` | 快、便宜（免费）、质量好 |
| 深度思辨 | `deepseek-ai/deepseek-v4-pro` | 推理质量最高，免费 |
| 代码工程 | `qwen/qwen3-coder-480b-a35b-instruct` 或 `deepseek-ai/deepseek-v4-pro` | 代码能力强 |
| 中文内容 | `qwen/qwen3.5-122b-a10b` | 中文优化 |
| 快速执行 | `stepfun-ai/step-3.7-flash` | 速度快 |
| 视觉分析 | `meta/llama-3.2-90b-vision-instruct` | 视觉能力强 |

### 按Bot分配（六韬团队）

| Bot | NIM 默认 | 兜底 |
|-----|---------|------|
| 主（Junis） | `deepseek-ai/deepseek-v4-flash` | DeepSeek官方 `deepseek-v4-flash` |
| 燕青 | `deepseek-ai/deepseek-v4-flash` | DeepSeek官方 `deepseek-v4-flash` |
| 扫地僧 | `deepseek-ai/deepseek-v4-pro` | DeepSeek官方 `deepseek-v4-pro` |
| 黄老邪 | `stepfun-ai/step-3.7-flash` | DeepSeek官方 `deepseek-v4-pro` |

## 配置注意事项

- **模型名不对称：** NIM 使用 `组织/模型名` 格式（`deepseek-ai/deepseek-v4-flash`），DeepSeek 官方使用简写（`deepseek-v4-flash`）。两个通道的模型名不同，fallback 时由 Hermes 自动按 models 列表映射
- **provider 配置：** NIM 使用 `provider: custom` 模式，不能用 `custom:nvidia` 语法
- **速率限制：** 免费通道有速率限制，高并发场景建议测试极限
- **API Key：** 使用 `OPENAI_API_KEY`（关联NVIDIA账户）
