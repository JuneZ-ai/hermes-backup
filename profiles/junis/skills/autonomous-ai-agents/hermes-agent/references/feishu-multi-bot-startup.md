# 启动飞书三Bot Gateway（异虎专用）

扫地僧、黄老邪、燕青三个 Bot 各用独立的飞书 Bot 凭证，以 tmux 持久化运行。

## 一键重启

```bash
# 清除旧会话
tmux kill-session -t saodiseng 2>/dev/null
tmux kill-session -t huanglaoxie 2>/dev/null
tmux kill-session -t yanqing 2>/dev/null

# 启动脚本方式（推荐）
chmod +x ~/start_bot.sh
for bot in saodiseng huanglaoxie yanqing; do
  tmux new-session -d -s $bot "~/start_bot.sh $bot"
done
```

## 启动脚本（~/start_bot.sh）

```bash
#!/bin/bash
PROFILE=$1
ENV_FILE="/home/hermes/.hermes/profiles/${PROFILE}/.env"
LOG_FILE="/home/hermes/.hermes/logs/${PROFILE}.log"
set -a
source "$ENV_FILE"
set +a
python -m hermes_cli.main gateway run --profile "$PROFILE" &>> "$LOG_FILE"
```

## 状态检查

```bash
tmux list-sessions                              # 三个都应在
grep "connected" /home/hermes/.hermes/logs/*.log # 检查飞书连接
```

## 已知问题

- 每个 Bot 的 `.env` 中 `OPENAI_API_KEY` 若为空或 placeholder，Gateway 仍可连接飞书 WebSocket，但消息回复会静默 401。此时检查 `profile/.env` 的 Key 是否与 `config.yaml` 的 `model.api_key` 一致。
- 三条 Gateway 共用一个主进程的 MCP 服务（time/filesystem/github），不必为每个 Bot 单独配。
