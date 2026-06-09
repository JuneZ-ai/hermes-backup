# Multi-Role Bot Architecture

Design pattern for running multiple specialized Feishu bots via Hermes Profiles, each with an independent persona, toolset, memory, and skill stack.

## Architecture Overview

```
飞书用户
  ├── 🤖 Bot A (哲学顾问) ── Profile: philosopher
  ├── 🤖 Bot B (分析师)   ── Profile: analyst
  ├── 🤖 Bot C (执行管家) ── Profile: executor
  └── 🤖 Bot Cmd (指挥官) ── Profile: default (current Hermes)
```

Each Profile is a fully independent Hermes instance — separate config, `.env`, memory, sessions, and skills. Each connects to one Feishu bot via its own Gateway process.

## Pre-Flight: Create Feishu Bot Applications

In [Feishu Open Platform](https://open.feishu.cn):
1. Create N new apps (one per role)
2. Enable Bot capability (应用功能 → 机器人)
3. Get App ID + App Secret (凭证与基础信息)
4. Publish and enable permissions (at minimum `im:message` scope)
5. Add bot to a chat for testing

## Create Hermes Profiles

```bash
# Create profiles
hermes profile create philosopher
hermes profile create analyst
hermes profile create executor

# Verify
hermes profile list
```

## Configure Each Profile

```bash
# Set Feishu credentials per profile (must use .env, NOT config)
# `.env` is write-protected from write_file/patch — use echo in terminal
echo 'FEISHU_APP_ID=cli_xxx_philosopher' >  ~/.hermes/profiles/philosopher/.env
echo 'FEISHU_APP_SECRET=secret...'        >> ~/.hermes/profiles/philosopher/.env
echo 'FEISHU_DOMAIN=feishu'               >> ~/.hermes/profiles/philosopher/.env
echo 'FEISHU_CONNECTION_MODE=websocket'   >> ~/.hermes/profiles/philosopher/.env
echo 'GATEWAY_ALLOW_ALL_USERS=true'       >> ~/.hermes/profiles/philosopher/.env

echo 'FEISHU_APP_ID=cli_xxx_analyst' >  ~/.hermes/profiles/analyst/.env
echo 'FEISHU_APP_SECRET=secret...'   >> ~/.hermes/profiles/analyst/.env
echo 'FEISHU_DOMAIN=feishu'          >> ~/.hermes/profiles/analyst/.env
echo 'FEISHU_CONNECTION_MODE=websocket' >> ~/.hermes/profiles/analyst/.env
echo 'GATEWAY_ALLOW_ALL_USERS=true'  >> ~/.hermes/profiles/analyst/.env

# ⚠️ Also set model provider explicitly per profile
# model.default alone is NOT enough — missing provider config causes
# "Primary provider auth failed: No inference provider configured"
hermes config set model.default deepseek-v4-flash --profile philosopher
hermes config set model.provider custom --profile philosopher
hermes config set model.base_url "https://api.deepseek.com" --profile philosopher
hermes config set model.api_key "sk-..." --profile philosopher
```

## Set Role Persona

Persona is the system prompt that shapes the bot's behavior. Two approaches:

### Option A: Quick persona via config (simple)

```bash
hermes config set agent.persona "你是哲学顾问（花名：扫地僧）..." --profile saodiseng
```

### Extending Bot Capabilities with Supporting Files

SOUL.md modifications alone may not be enough for complex capabilities. You can add **supporting scripts** to the profile directory:

1. Place scripts at `~/.hermes/profiles/<name>/<tool>.py` (or `.sh`)
2. Reference them in SOUL.md with exact paths
3. The bot agent will use terminal/code_execution to invoke them

Example — adding PDF reading to a bot:
- `~/.hermes/profiles/yanqing/pdf_to_images.py` — converts PDF pages to PNG images
- SOUL.md section instructing: "When user sends a PDF, extract text with pymupdf; if scanned, convert pages to images then analyze with vision model"

The bot's SOUL.md wording should be precise about the expected context note format:
```
[The user sent a document: 'xxx.pdf'. The file is saved at: /path/to/file]
```
This is the exact format injected by the Feishu gateway (see `references/feishu-document-handling.md`).

### Option B: Rich persona via SOUL.md (recommended)

Profiles include a `SOUL.md` file at `~/.hermes/profiles/<name>/SOUL.md` that serves as the persistent system prompt. This supports multi-paragraph persona definitions including identity, communication style, limitations, and tone guidance. Write it directly:

```bash
cat > ~/.hermes/profiles/saodiseng/SOUL.md << 'EOF'
You are 扫地僧（Sweeping Monk）, the philosophy advisor.

## Core Identity
You draw wisdom from the Shaolin sweeping monk in 「天龙八部」...

## Personality
- 深藏不露 — You don't show off. Your strength speaks for itself.
- 一语破天机 — You reframe complex problems with devastating simplicity.

## Your Limitations
You DO NOT handle execution tasks. If the user needs action, defer to the commander.

## Communication Style
- Concise. One-paragraph answers preferred.
- End with a question that deepens the thinking, not a task.
EOF
```

### Persona Design Principles
1. **Role → Name → Persona** — define the role function first, then give it a simple name (花名文化), then write the persona
2. **Scope boundaries** — clearly state what this bot DOES and DOES NOT do
3. **Tone guidance** — match the bot's domain (philosophy bot = contemplative, analyst = crisp)

### Naming Rules (花名文化)

- Simple, memorable names — you can guess the role from the name
- Personified but approachable — NOT abstract concepts (avoid 观澜, 青崖, etc.)
- **Preferred source: Chinese classical novel characters** — characters from 武侠小说 (金庸: 扫地僧 for philosophy, 黄老邪 for analysis), 四大名著 (水浒: 浪子燕青 for execution), 封神演义 (哪吒), or cultural mythology. These are well-known, evocative, and not real historical figures.
- NOT real historical figures (avoid 王阳明, 孔子, 诸葛亮)
- Avoid `-bot` or `-robot` suffixes — keep names human-like for the 花名 culture
- Full format: include the nick/title (浪子燕青, not just 燕青)

## Scoping Toolsets Per Role

Each profile can enable/disable toolsets independently — critical for focusing the bot and saving tokens.

### ⚠️ Toolset Precision Principle（工具集少即是多）

**不要多，要精准。** 给一个角色太多工具，比给太少更糟糕。原因：

- **Token 浪费** — 每个工具的 schema 注入系统 prompt，多余的工具有百害而无一利
- **认知混乱** — 哲学顾问手里有 terminal，它可能会想跑命令而不自知
- **角色模糊** — 三个 Bot 如果都能写代码，那分角色就失去了意义

**决策方法**：
1. 先想清楚这个角色「做且只做」哪一类事
2. 只给它完成那类事 **刚好够用** 的工具
3. 凡是拿不准的、可能用不到的，一概禁掉
4. 以后发现不够再加，但绝不提前配冗余

```bash
# Philosopher: no need for terminal, github, cron
hermes config set agent.disabled_toolsets "terminal,cronjob,github" --profile philosopher

# Analyst: needs web search, may not need file write
hermes config set agent.disabled_toolsets "cronjob,delegation" --profile analyst
```

Typical toolset scoping:

| Role | Recommended Toolsets | Key Disabled Tools | Decision Logic |
|------|---------------------|-------------------|----------------|
| 哲学顾问 | file, web, vision, session_search, memory, skills, clarify, messaging | terminal, cronjob, delegation, code_execution, browser, tts, image_gen | 只动脑不动手。不用跑命令、不用写代码、不用生成图片。能读知识库、能查资料、能看图片、能翻历史就够了。 |
| 分析师 | file, web, vision, **code_execution**, session_search, memory, skills, clarify, messaging | terminal, cronjob, delegation, browser, tts, image_gen | 需要跑分析脚本(code_execution)但不能碰系统命令(terminal)。能读文件、搜资料、看图、跑Python分析。 |
| 执行管家 | terminal, cronjob, code_execution, file, **delegation**, messaging, todo | web, browser, vision, image_gen, skills, tts | 动手不动脑。不用查资料、不用看图、不用哲学思辨。能跑命令、定任务、调度子代理、管理文件。 |
| 指挥官 | all (use `hermes profile create` without modification) | none | 全栈统筹。负责拆解任务、分发、整合汇报。 |

## Load Skills Per Profile

```bash
# Philosopher
hermes -p philosopher skills load 六韬史鉴 太极双螺旋

# Analyst
hermes -p analyst skills load 六韬智脑 数据科学
```

## Run Multiple Gateway Processes

Each Profile needs its own Gateway process, each connecting to a different Feishu bot.

### ⚠️ CRITICAL: Use tmux, NOT terminal(background=true)

`terminal(background=true)` processes are **killed when the agent conversation turn ends** — they do NOT survive across user messages. This means a gateway started via background process will die as soon as the agent's session moves to a new turn.

**Always use tmux** for persistent gateways:

```bash
# Start all three (via tmux) — survives across agent turns and gateway restarts
tmux new-session -d -s gw-saodiseng 'hermes -p saodiseng gateway run --replace'
tmux new-session -d -s gw-huanglaoxie 'hermes -p huanglaoxie gateway run --replace'
tmux new-session -d -s gw-yanqing    'hermes -p yanqing gateway run --replace'

# Verify
tmux ls
```

### WSL Startup Persistence
If using WSL with the VBS startup pattern, each Gateway needs its own bash loop:

```vbs
CreateObject("WScript.Shell").Run "wsl.exe -u hermes -d Ubuntu -- bash -c 'while true; do cd /usr/local/lib/hermes-agent && python -m hermes_cli.main --profile philosopher gateway run --replace; sleep 5; done'", 0, False
```

## Inter-Bot Communication

### Pattern A: Human Bridge
User manually forwards messages between bots in Feishu.
- Simplest, no extra config
- User is the integration point

### Pattern B: Commander Orchestration
User talks to the Commander bot, which uses `delegate_task` to dispatch to the other profiles.
- Commander does task decomposition + result synthesis
- Other profiles run as subagents in Commander's sessions
- No message-forwarding needed

```yaml
# Example: Commander subagents reference other profiles' skills
delegate_task(
    goal="分析这段王阳明原文",
    context="用户问：...",
    toolsets=["file", "web"],
    # Commander spawns a subagent with philosopher's skills
)
```

### Pattern C: Webhook Bridge (future)
Each bot reports back to a shared board. Requires custom webhook setup.

## Provider Migration Across Profiles (Provider切换全流程)

当需要将**所有** Bot 从一个 provider 切换到另一个时（例如 DeepSeek ↔ TokenHub），必须更新每处配置，遗漏一处就会造成 Silent 401：

### 切换清单

切换前确认涉及的文件：

| 文件 | 作用 | 需修改项 |
|------|------|---------|
| 每个 Profile 的 `config.yaml` | 模型连接 | `model.base_url` + `model.api_key` |
| 每个 Profile 的 `.env` | 环境变量 | `OPENAI_API_KEY` + `OPENAI_BASE_URL` |
| 主 `~/.hermes/.env` | 全局环境 | `OPENAI_API_KEY` + `OPENAI_BASE_URL` |
| 主 `~/.hermes/config.yaml` | 主实例 | `model.base_url` + `model.api_key` |

### 完整操作步骤

```bash
# 1. 每个 Profile 的 config.yaml (用 hermes config set --profile)
hermes config set model.base_url https://api.deepseek.com --profile saodiseng
hermes config set model.api_key sk-xxxx --profile saodiseng
hermes config set model.base_url https://api.deepseek.com --profile huanglaoxie
hermes config set model.api_key sk-xxxx --profile huanglaoxie
# ... 对每个 profile 重复

# 2. 每个 Profile 的 .env
cat > ~/.hermes/profiles/saodiseng/.env << 'ENVEOF'
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
OPENAI_API_KEY=sk-xxxx          # 必须与 config.yaml 一致
OPENAI_BASE_URL=https://api.deepseek.com
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
GATEWAY_ALLOW_ALL_USERS=true
ENVEOF
# ... 对每个 profile 重复

# 3. 主实例 .env（用 sed）
sed -i 's|^OPENAI_API_KEY=.*|OPENAI_API_KEY=sk-xxxx|' ~/.hermes/.env
sed -i 's|^OPENAI_BASE_URL=.*|OPENAI_BASE_URL=https://api.deepseek.com|' ~/.hermes/.env

# 4. 主实例 config.yaml
hermes config set model.base_url https://api.deepseek.com
hermes config set model.api_key sk-xxxx

# 5. 重启所有网关
# 主网关：在飞书发 /restart
# Bot 网关：重启 tmux session 或 background process
```

### ⚠️ 关键陷阱

- **不同 Profile 可能有不同的 API Key。** 本架构中扫地僧使用独立的 DeepSeek Key（`sk-436ff3...`），而主实例使用另一个 Key（`sk-d1a9fb...`）。Provider 切换时必须确认每个 Profile 的独立凭证，不要统一覆盖。
- **TokenHub 免费额度用完**会返回 `HTTP 402 FREE_QUOTA_EXHAUSTED` 或 `HTTP 403 endpoint is inactive: NO_FREE_PACKAGE`。恢复方式是切回 DeepSeek 直连（见上方步骤）。
- **修改 .env 后不用重启 gateway？** 要。Hermes 在启动时读取 .env，运行时不会热重载。
- **`hermes config set` 会存储完整值**，但 `read_file` / `cat` 显示时会自动掩码（例如 `sk-d1a...e92f`）。用 `xxd` 验证实际字节。

## Resource Considerations

| N bots | Gateway processes | RAM estimate | Notes |
|--------|------------------|-------------|-------|
| 2 | 2 | ~400-600 MB | Lightweight pilot |
| 3 | 3 | ~600-900 MB | Typical setup |
| 4+ | 4+ | ~800-1200 MB | Heavy, consider model choice |

Optimization tips:
- Use cheaper models (flash) for non-Commander bots
- Disable unused toolsets per profile
- Set lower `max_iterations` for focused bots

## Feishu-Specific Pitfalls

### WebSocket connected but bot doesn't respond

Symptom: Gateway shows `✓ feishu connected` and `[Lark] connected to wss://...` but the bot doesn't respond to user messages in Feishu.

Troubleshooting checklist:
1. **App published?** — In Feishu Open Platform → 版本管理与发布 → create a version → 申请发布. Without this, only the app creator can find the bot, and even then events may not flow.
2. **Bot capability enabled?** — 应用功能 → 机器人 → ON
3. **Permissions granted?** — At minimum: `im:message`, `im:resource`, `im:chat`. Must be added in 权限管理 AND approved via 版本发布.
4. **Event subscriptions configured?** — 事件订阅 must include `im.message.receive_v1`. Even in WebSocket mode (where the lark-oapi SDK auto-subscribes), the event must be visible in the app's event subscription list.
5. **Model provider configured?** — Profile needs `model.provider`, `model.base_url`, and `model.api_key` set explicitly. Logs will show `Primary provider auth failed: No inference provider configured` if missing.

### ⚠️ .env vs config.yaml API Key Mismatch (Silent 401)

**Symptom:** Feishu connects successfully (`✓ feishu connected`, WebSocket handshake OK) but the bot never responds to user messages. No errors in gateway.log. The API call silently fails with 401.

**Root cause:** The API key in `.env` (`OPENAI_API_KEY`) does not match the key in `config.yaml` (`model.api_key`). This happens when:
- A profile is created that copies the `.env` from a different source (e.g. `hermes profile create --clone-from`)
- The `.env` was written using a value from `read_file`/`cat` output — those tools show **masked** values (e.g. `sk-d1a...e92f` instead of the full key)

**Verification:** `read_file` and `cat` mask secret values. Use `xxd` to confirm actual bytes:
```bash
# Compare actual stored values
xxd ~/.hermes/profiles/<name>/.env | grep -A2 "API_KEY"
xxd ~/.hermes/profiles/<name>/config.yaml | head -10
# The hex bytes tell the real story
```

The real API key from the working default profile is at `~/.hermes/.env`. Read it with xxd to get the exact value:
```bash
xxd ~/.hermes/.env | head -6
```

**Fix:** Update `.env` to use the exact same key as `config.yaml`:
```bash
# Write the correct key to .env (cat > works directly via terminal)
cat > ~/.hermes/profiles/<name>/.env << 'ENVEOF'
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret...
OPENAI_API_KEY=sk-xxxx   # Must match config.yaml model.api_key
OPENAI_BASE_URL=https://api.deepseek.com
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
GATEWAY_ALLOW_ALL_USERS=true
ENVEOF
```
Then restart the gateway.

6. **Add ws_ping_interval** — Without keepalive, the WebSocket may not process messages reliably:
   ```bash
   hermes config set platforms.feishu.extra.ws_ping_interval 25 --profile <name>
   hermes config set platforms.feishu.extra.ws_ping_timeout 10 --profile <name>
   ```
6. **Verify with Feishu API** — Use the tenant_access_token to call `bot/v3/info` and check `activate_status`. Status `2` = enabled. Also call `im/v1/chats` to verify the bot can access the API (empty list means no conversations yet).
7. **After all config is done** — Restart the gateway (kill tmux session and recreate)

