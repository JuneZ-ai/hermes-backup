# WorkBuddy (腾讯云CodeBuddy) 集成参考

> WorkBuddy 是腾讯云推出的全场景 AI Agent 桌面工作台，底层与 CodeBuddy 共享技术底座。

## 核心发现

### WB 与 Hermes 的关系

| 项目 | Hermes | WorkBuddy |
|------|--------|-----------|
| 运行环境 | WSL (Linux) | Windows 桌面端 (Electron) |
| 用户入口 | 飞书机器人 | Windows 桌面 + 微信/企微 |
| 模型 | DeepSeek V4 Flash | 混元/DeepSeek/GLM/Kimi/MiniMax |
| 技能格式 | SKILL.md 前端数据 | SKILL.md + YAML frontmatter |
| MCP | 支持 (客户端) | 支持 (MCP Server, 端口 9359) |

### WB 数据位置

WSL 可直接通过 `/mnt/c/` 访问 WB 数据：

```
/mnt/c/Users/<username>/.workbuddy/
├── skills/              # 技能目录（SKILL.md + yaml frontmatter）
│   ├── <skill-name>/
│   │   ├── SKILL.md     # 技能定义
│   │   ├── _meta.json   # 元数据
│   │   ├── references/  # 参考文件
│   │   ├── scripts/     # 脚本
│   │   └── assets/      # 资源
├── projects/            # 项目/任务目录
├── sessions/            # 会话历史
├── plugins/             # 插件目录
├── workbuddy.db         # SQLite 数据库
├── settings.json        # 配置（含渠道/MCP/插件）
├── models.json          # 模型配置
├── IDENTITY.md          # 身份定义
├── SOUL.md              # 人格定义
└── .mcp.json            # MCP 服务器配置
```

### WB 技能格式

Skills 使用 SKILL.md 文件，带 YAML 前端数据：

```yaml
---
name: <技能名称>
description: <技能描述>
trigger_words: <触发词，逗号分隔>
---
# 技能标题

## 概述
...

## 使用方式
...
```

标准化的技能需要定义：
- **输入参数** — 从表格、用户输入或上下文获取的数据
- **输出参数** — 技能执行后返回的结构化字段
- **处理逻辑** — prompt/工作流描述

### WB 当前配置

- MCP 代理运行在 `127.0.0.1:9359/mcp`（仅 Windows 本机，WSL 不可达）
- 已连接飞书（独立 Bot，app_id: `cli_a9522415aeb8dcbd`）
- 已连接微信（微信小号 Bot）
- 已启用插件：agent-browser, playwright-cli, skills-sec-audit, find-skills, document-skills, finance-data

### 已知的自定义技能

| 技能名 | 类型 | 备注 |
|--------|------|------|
| 六韬易哲 | 易学智能体 | 复杂内用（易经、八字、风水等），含 modules/ 案例库/ |
| 六韬智脑 | 通用智能体 | 含 scripts/ references/ 子目录 |
| 周报生成 | 工作自动化 | 标准周报/月报模板 |
| 飞书套件 | 飞书集成 | 含 scripts/ references/ |
| 龙虾语录图文生成 | 内容创作 | 图文生成 |

## Hermes ↔ WorkBuddy 连接方案

### 方案A（推荐）：文件系统 + HTTP 桥接

```
飞书用户 → Hermes Gateway → Hermes Agent
    ├─→ 直接读写 /mnt/c/.../.workbuddy/ 文件系统
    │   ├─→ 创建/修改技能文件
    │   ├─→ 操作 projects/ 任务目录
    │   └─→ 读写 workbuddy.db
    │
    ├─→ Hermes 起 HTTP Server
    │   └─→ WB 通过 http_request action 回调
    │
    └─→ 互读互写 shared 目录交换数据
```

**优势**：无需 WB 开端口，Hermes 已有 WSL 文件系统访问权限。

### 方案B：MCP 互联

- WB 的 MCP proxy (port 9359) 仅限 Windows localhost
- 可通过端口转发或 Windows 定时任务暴露给 WSL
- 或让 Hermes Gateway 暴露 MCP Server，WB 配置连接

### 方案C：通过飞书桥接

- WB 已有自己的飞书 Bot
- Hermes 也通过飞书与用户对话
- 可在两个飞书 Bot 之间转发消息

## WB CLI 工具（重大发现）

WB 桌面版内置了完整的 CLI 工具，可从 WSL 通过 PowerShell 直接调用。

### CLI 位置

```
C:\Users\<username>\AppData\Local\Programs\WorkBuddy\resources\app.asar.unpacked\cli\dist\codebuddy.js
```

需要 Node.js（`v24.15.0` 已确认可用）。

### 从 WSL 调用

```bash
cd /mnt/c/Users/<username> && \
powershell.exe -Command "node 'C:\Users\<username>\AppData\Local\Programs\WorkBuddy\resources\app.asar.unpacked\cli\dist\codebuddy.js' --print '你的prompt' --output-format json -y"
```

### 关键 CLI 选项

| 选项 | 用途 |
|------|------|
| `--print` / `-p` | 非交互模式，输出结果后退出（适合 pipe/集成） |
| `--output-format json` | JSON 结构化输出 |
| `--output-format stream-json` | 实时流式 JSON 输出 |
| `--input-format stream-json` | 流式 JSON 输入 |
| `--json-schema <schema>` | 输出 JSON Schema 校验 |
| `-y, --dangerously-skip-permissions` | 跳过权限检查 |
| `--serve` | 启动 HTTP 服务（Web UI + API） |
| `--port <number>` | HTTP 服务端口（默认 auto-assign） |
| `--host <string>` | HTTP 绑定地址（默认 127.0.0.1）|
| `--bg` / `--background` | 后台运行 |
| `--name <name>` | 后台会话命名 |
| `--model <model>` | 指定模型（如 `custom-local:deepseek-v4-flash`）|
| `--agent <agent>` | 指定 Agent 类型 |
| `--mcp-config <fileOrString>` | 加载 MCP 配置 |

### CLI 子命令

```
codebuddy config         管理配置
codebuddy mcp            管理 MCP 服务器
codebuddy plugin         管理插件
codebuddy doctor         检查健康状态
codebuddy ps             列出活跃会话
codebuddy logs <pid>     查看后台会话日志
codebuddy attach <pid>   附着到后台会话
codebuddy kill <pid>     终止后台会话
```

### 已知限制

- 打开 CLI 时会检查版本更新，旧版本会提示升级
- 当前版本存在已知问题（429 响应），建议升级
- CLI 依赖 Node.js，会消耗 WB 积分/额度

## 龙虾技能库（本地技能研究）

用户 D 盘 `/mnt/d/龙虾技能/` 存放了 14 个技能项目：

| 项目 | 用途 |
|------|------|
| goskill-main | 长期运行技能框架 |
| soskill-main | 技能市场安全审核引擎 |
| CEOskill-main | CEO 决策顾问（参考：高层决策技能写法）|
| workbuddy-wiki-main | WB 知识库官方 Schema |
| hyperframes-main | 多 Agent 协作框架 |
| openhuman-main | 开源人机协作 |
| dna-memoryv3.0-main | 记忆系统 |
| nuwa-skill-main | 女娲技能 |
| gbrain-master | GBrain 框架 |

### 关键发现

- WB Skills 使用 `SKILL.md` + YAML frontmatter 格式（与 Hermes 技能格式类似但字段不同）
- 官方 Schema 提倡 "增量构建、持久化 Wiki" 理念
- `trigger_words`（逗号分隔字符串）是 WB 标准触发词格式（非 YAML 列表）
- 输入的 input/output 参数目前由各技能自行定义，无统一标准格式
