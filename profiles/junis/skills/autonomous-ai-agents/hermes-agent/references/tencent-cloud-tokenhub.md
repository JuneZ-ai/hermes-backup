# 腾讯云 TokenHub（模型广场）API 集成参考

> TokenHub 是腾讯云的模型网关服务，聚合 DeepSeek、GPT、Claude、混元等多个模型。  
> 控制台地址：`https://console.cloud.tencent.com/tokenhub/models`

## OpenAI 兼容 API

| 项目 | 值 |
|------|-----|
| **Endpoint** | `https://api.tokenhub.cloud.tencent.com/v1` |
| **Auth** | `Authorization: Bearer <api_key>` |
| **API Key 格式** | 控制台生成的 `ak-xxx:sk-yyy` 或单独的 `ak-xxx`/`sk-xxx` |
| **凭证来源** | 控制台 → TokenHub → 创建 API Key（非 Tencent Cloud SecretId/SecretKey） |
| **替代地址** | `https://api.hunyuan.cloud.tencent.com/v1`（仅限混元模型） |

## WSL DNS 问题

`api.tokenhub.cloud.tencent.com` 在 WSL 中**无法解析**（DNS 返回 `Name or service not known`），因为：

- WSL 使用 Windows DNS 代理（`172.24.0.1`）
- Windows DNS 对某些腾讯云内部域名不转发
- 纯 IP 连接也不行（域名无法获取 IP）

### 修复方法

从 Windows PowerShell（以管理员身份运行）将 WSL DNS 改为公共 DNS：

```powershell
wsl -u root -d Ubuntu -- sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf"
```

注意：WSL 会在重新启动时重置 `resolv.conf`（由 `/etc/wsl.conf` 的 `generateResolvConf = true` 控制）。如需永久修改，需在 `%USERPROFILE%\.wslconfig` 或 `/etc/wsl.conf` 中配置。

### 从 Windows 测连通性

```powershell
# 查看可用模型
$headers = @{ "Authorization" = "Bearer ak-xxx:sk-yyy" }
Invoke-RestMethod -Uri "https://api.tokenhub.cloud.tencent.com/v1/models" -Headers $headers

# 测试对话
$body = @{ model = "gpt-4o-mini"; messages = @(@{role="user"; content="Hello"}) } | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.tokenhub.cloud.tencent.com/v1/chat/completions" -Headers $headers -Body $body -ContentType "application/json" -Method Post
```

## Hermes 配置

在 `config.yaml` 中配置为 custom provider：

```yaml
model:
  provider: custom
  base_url: https://api.tokenhub.cloud.tencent.com/v1
  api_key: <ak-xxx:sk-yyy>
  default: gpt-4o-mini  # 或其他 TokenHub 支持的模型
```

或通过 CLI（仅限有终端访问时）：

```bash
hermes config set model.provider custom
hermes config set model.base_url https://api.tokenhub.cloud.tencent.com/v1
hermes config set model.api_key <ak-xxx:sk-yyy>
hermes config set model.default gpt-4o-mini
```

## 注意

- TokenHub 的 `ak-xxx:sk-yyy` 格式 API Key 不能用于混元 API endpoint（`api.hunyuan.cloud.tencent.com`）
- 从 WSL 内部无法直接 `curl` 到 TokenHub API（DNS 问题），需先修复 DNS
- 如需 vision 能力，需选择支持多模态的模型（如 `gpt-4o`、`claude-3.5-sonnet` 等）
