# DashScope (通义千问) 辅助视觉模型配置

适用于：主模型用 DeepSeek（无视觉能力），需要加一个国产多模态模型看图。

## 配置步骤

### 1. 获取 API Key

DashScope API key 以 `sk-` 开头，在 https://bailian.console.aliyun.com/ 获取。

### 2. 写入环境变量

```bash
sed -i '$a\DASHSCOPE_API_KEY=sk-你的key' ~/.hermes/.env
```

### 3. 配置辅助视觉模型

```bash
hermes config set auxiliary.vision.provider custom
hermes config set auxiliary.vision.model qwen3.5-omni-plus
hermes config set auxiliary.vision.base_url https://dashscope.aliyuncs.com/compatible-mode/v1
hermes config set auxiliary.vision.api_key sk-你的key
```

### 4. 重启网关

```bash
hermes gateway restart
```

如果重启卡在 `deactivating` 状态（已知问题）：
```bash
# 找到 PID
systemctl --user status hermes-gateway.service --no-pager | grep "Main PID"
# 强制杀掉
kill -9 <PID>
# 重置 failed 状态后启动
systemctl --user reset-failed hermes-gateway.service
systemctl --user start hermes-gateway.service
```

## 可选模型

从 DashScope 可用模型列表（2026年5月实测），按能力分级：

| 类型 | 模型名 | 说明 |
|------|--------|------|
| 全能多模态 | `qwen3.5-omni-plus` | ⭐ 最强，看图+语音+文本 |
| 轻量多模态 | `qwen3.5-omni-flash` | 快速版 |
| 视觉专用 | `qwen3-vl-plus` | 纯视觉升级版 |
| 视觉OCR | `qwen-vl-ocr` | 文字识别专用 |
| 旧版视觉 | `qwen-vl-max` | 前一主力 |

## API 端点

- DashScope OpenAI 兼容地址：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- 直接查询可用模型：`GET /v1/models`（需 Bearer Token）

## 注意事项

- 不需要 `DASHSCOPE_API_KEY` 之外的额外 key，`auxiliary.vision.api_key` 用同一个就行
- 辅助模型是**按需调用**的（发图时自动切过去），不影响主模型的日常对话
- 改模型名后**不需要重启网关**，新会话自动生效
