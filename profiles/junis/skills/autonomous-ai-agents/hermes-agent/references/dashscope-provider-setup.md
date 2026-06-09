# DashScope (阿里云通义千问) Provider Setup

Add Qwen models to Hermes via DashScope's OpenAI-compatible API.

## Quick Setup

```bash
# 1. Add API key to .env
echo 'DASHSCOPE_API_KEY=sk-xxxxxxxx' >> ~/.hermes/.env

# 2. Set as main model (or add as auxiliary vision)
# Option A: Main model
hermes config set model.provider custom
hermes config set model.base_url https://dashscope.aliyuncs.com/compatible-mode/v1
hermes config set model.default qwen-turbo-latest

# Option B: Auxiliary vision (keep existing main model)
hermes config set auxiliary.vision.provider custom
hermes config set auxiliary.vision.model qwen3.5-omni-flash
hermes config set auxiliary.vision.base_url https://dashscope.aliyuncs.com/compatible-mode/v1
hermes config set auxiliary.vision.api_key sk-xxxxxxxx
```

## Quota Tiers (实测 2026年5月)

DashScope 对不同模型有不同的免费配额策略。**不是所有模型都有免费额度。**

| Tier | 模型 | 免费配额 | 适合场景 |
|------|------|---------|---------|
| 🟢 充裕 | `qwen-turbo-latest`, `qwen-vl-max`, `qwen-vl-plus` | 长期稳定免费 | 主力文字 / 看图 |
| 🟡 有限 | `qwen3.5-omni-flash`, `qwen3-vl-flash` | 新模型，免费额度少 | 轻量任务 |
| 🔴 易耗尽 | `qwen3.5-omni-plus`, `qwen3.7-max`, `qwen3-coder-plus` | 免费额度极少，需充值 | 仅在充值后使用 |

**关键规律：** 千问3.5/3.6/3.7 系列新模型的免费额度远少于 2.5 代模型（qwen-turbo / qwen-vl-max）。新注册账号推荐先用 `qwen-vl-max`（看图）和 `qwen-turbo`（文字）。

## 可用模型列表

查询 DashScope 当前可用的所有模型：

```bash
curl -s https://dashscope.aliyuncs.com/compatible-mode/v1/models \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" | \
  python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin).get('data',[])]" | \
  grep qwen | sort
```

## 常用模型速查

| 模型名 | 类型 | 免费额度 |
|--------|------|--------|
| `qwen-turbo-latest` | 文字，快速 | 🟢 充裕 |
| `qwen-plus-latest` | 文字，均衡 | 🟢 充裕 |
| `qwen-max-latest` | 文字，最强旧版 | 🟢 充裕 |
| `qwen3.5-plus` | 文字，3.5代旗舰 | 🔴 易耗尽 |
| `qwen3.7-max` | 文字，最新旗舰 | 🔴 易耗尽 |
| `qwen-vl-max` | 看图 | 🟢 充裕 |
| `qwen-vl-plus` | 看图 | 🟢 充裕 |
| `qwen3.5-omni-flash` | 多模态，轻量 | 🟡 有限 |
| `qwen3.5-omni-plus` | 多模态，旗舰 | 🔴 易耗尽 |
| `qwen-coder-plus-latest` | 编程 | 🟡 有限 |
| `qwen3-coder-plus` | 编程，3代 | 🔴 易耗尽 |
| `qwen-math-plus-latest` | 数学 | 🟡 有限 |

## Multi-bot Profile 配置

每个 profile 有独立的 config.yaml 和 .env，需要各自配置：

```bash
# 修改某 profile 的模型
# 编辑 ~/.hermes/profiles/<name>/config.yaml
# model:
#   default: qwen-vl-max
#   provider: custom
#   base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
#   api_key: sk-xxxxxxxx

# 以及对应的 .env
# OPENAI_API_KEY=sk-xxxxxxxx
# OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**注意：** Profile 的 .env 不会继承根 .env 的变量——必须显式设置每个 profile。

## 网关重启

模型变更需要重启网关：

```bash
# 主网关
hermes gateway restart

# 如果卡在 deactivating
systemctl --user reset-failed hermes-gateway.service
systemctl --user start hermes-gateway.service
```
