# 飞书 CLI（lark-cli）安装与绑定 — Hermes Agent 环境

## 概述

飞书 CLI（`@larksuite/cli` / `lark-cli`）是飞书官方提供的命令行工具，让 AI Agent 通过 CLI 直接操作飞书（多维表格、文档、日历、消息等）。在 Hermes Agent 环境下安装时，需要用 `config bind` 绑定到已有的 Hermes 应用凭证，而非创建新应用。

## 安装步骤

### 前置条件

- Node.js（npm/npx）

### 第 1 步：安装 CLI

```shell
npm install -g @larksuite/cli
```

验证：`lark-cli --version` → 应显示版本号（如 `1.0.41`）

### 第 2 步：安装 CLI SKILL（必需）

```shell
npx -y skills add https://open.feishu.cn --skill -y
```

这会在 `~/.agents/skills/` 下安装飞书相关的 skill 集合。

### 第 3 步：绑定到 Hermes 应用凭证（HERMES 专属）

**不要** 运行 `lark-cli config init --new` —— 在 Hermes Agent 上下文中，该命令会被拒绝：

```
config init is refused inside hermes context
(would create a parallel app and shadow the existing hermes binding)
```

正确做法：

```shell
# 查看帮助
lark-cli config bind --help

# 绑定到现有 Hermes 应用（自动检测来源）
lark-cli config bind --source hermes --identity user-default
```

`--identity` 参数：
| 值 | 说明 | 适用场景 |
|:---|:-----|:---------|
| `bot-only` | 仅机器人身份（安全，不模拟用户） | 操作 Bitable、发送消息 |
| `user-default` | 允许用户身份 | 访问个人云盘、日历、邮件 |

### 第 4 步：登录（用户授权）— AI Agent 设备流模式

不要在同一个轮次里阻塞执行 `--device-code`。正确的 AI agent 模式：

```shell
# Step A: 获取 device_code 和 verification_url（不阻塞）
lark-cli auth login --recommend --no-wait --json

# 输出示例：
# {"device_code":"xxx","verification_url":"https://accounts.feishu.cn/oauth/v1/device/verify?flow_id=xxx&user_code=XXX-XXX"}

# Step B: 生成二维码（路径必须相对，不支持绝对路径）
cd /home/hermes
lark-cli auth qrcode "<verification_url>" --output feishu_auth_qr.png

# Step C: 用户扫描/打开链接授权后，用 device_code 完成
lark-cli auth login --device-code "<device_code>"
```

**关键规则：**
- `verification_url` 是 opaque string，不可做任何修改（不要 URL 编码/解码、不要加空格标点）
- 二维码必须用 `lark-cli auth qrcode` 生成，PNG 优先，QR code 图片必须包含在回复中展示
- `--device-code` 命令最长阻塞约 10 分钟，确保 runner timeout ≥ 600s
- 如果缺少 scope，用 `--domain` 参数重新登录：`lark-cli auth login --no-wait --json --domain drive`
- `--force` 标志：从 bot-only 切换到 user-default 身份模式时需要

**scope 获取策略：**
| 参数 | 获取的 scope | 适用场景 |
|:-----|:-------------|:---------|
| `--recommend` | 推荐的自动批准 scope | 基础操作（Bitable、消息） |
| `--domain drive` | drive 相关 scope（含 `space:document:retrieve`） | 云盘文件列表 |
| `--domain docs` | 文档相关 scope | 文档读写 |
| `--domain calendar` | 日历相关 scope | 日程操作 |
| `--scope "drive:drive:readonly,space:document:retrieve"` | 精确指定 scope | 精确控制 |
| 组合（逗号分隔） | 所有指定 domain | 全功能 |

### 第 5 步：验证

```shell
lark-cli auth status
```

成功后输出中包含 `"identities": {"user": {"tokenStatus": "valid", ...}}`。

## 飞书云盘空间模型（关键）

飞书云盘有两个隔离的空间，理解这个区别避免权限困惑：

| 空间 | 访问方式 | 可见内容 | 代表场景 |
|:-----|:---------|:---------|:---------|
| **应用空间（My Space）** | `tenant_access_token`（应用身份） | 应用自己创建的文件（如 Bitable） | 从 CLI 创建的表/文档 |
| **用户个人空间** | `user_access_token`（用户身份，需 OAuth） | 用户个人云盘所有文件 | 枚举用户云盘目录树 |

**实际经验：**
- `lark-cli drive files list --as user --page-all` 只能通过 user_access_token 列出用户个人空间
- `tenant_access_token` + `drive:drive` scope 也只能看到应用空间，看不到用户个人空间
- 已知 token 的文档可以直接读取（即使没有 OAuth），因为有 `drive:document` 或 `docx:document:readonly` scope
- 枚举用户文件树→必须 OAuth→user_access_token

## 飞书 CLI 常用命令速查

### 云盘操作

```shell
# 列出用户云盘根目录文件（需要 user 身份 + space:document:retrieve scope）
lark-cli drive files list --as user --page-all

# 查看 schema
lark-cli schema drive.files.list

# 获取文件元信息
lark-cli drive metas

# 下载文件
lark-cli drive download <file_token>

# 搜索文件
lark-cli drive search
```

### 身份与凭证

```shell
# 查看当前身份状态
lark-cli auth status

# 列出所有已授权的 scope
lark-cli auth status --json | jq '.identities.user.scope'

# 重新登录（增加 scope）
lark-cli auth login --no-wait --json --domain drive

# 切换身份策略（不重新 bind）
lark-cli config strict-mode --help
```

## 注意事项

- **权限同步**：绑定的应用需要有相应权限（如 `drive:document`、`drive:drive`），并在飞书开发者后台发布新版本后才能在 CLI 中生效
- **config bind 不覆盖已有配置**：如果只是想切换身份策略（如 bot-only → user-default），用 `lark-cli config strict-mode` 而非重新 bind
- **多账号**：Hermes 多 Profile 场景下，每个 Profile 可以有自己的飞书应用凭证，CLI 绑定到哪个 Profile 就用哪个
- **QR code 路径限制**：`lark-cli auth qrcode` 的 `--output` 必须用相对路径，不支持 `/tmp/xxx.png`，需先 `cd` 到目标目录
- **Token 有效期**：user_access_token 默认 2 小时，refresh_token 7 天
- **scope 追加**：`--domain` 参数是叠加的，可以用逗号组合：`--domain drive,docs,calendar`
- **config bind 切换身份**：从 `bot-only` 切到 `user-default` 时加 `--force` 确认
- **文档链接**：[飞书 CLI 安装指南](https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md)
