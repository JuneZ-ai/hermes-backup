# Hermes Agent Process Architecture

## The Two-Process Model

Hermes Agent typically runs as **two separate processes**:

| Process | What it is | User visible? | Critical? |
|---------|-----------|---------------|-----------|
| **Gateway** (`hermes gateway run`) | Background service that connects to messaging platforms (Feishu, Telegram, Discord, etc.) and runs the agent loop. This is the **core** process. | Usually not (systemd service or nohup background) | ✅ Yes — handles all platform messages |
| **TUI / CLI** (`hermes` or `hermes chat`) | Local terminal client for interactive chat. Connects to the same session store but is NOT needed for gateway-based conversations. | Yes — this is the "blue terminal window" the user sees | ❌ No — closing it does NOT disconnect platform chats |

```
┌──────────────────────────────────────────┐
│              Messaging Platform           │
│         (Feishu / Telegram / ...)         │
└──────────────┬───────────────────────────┘
               │ websocket / webhook
               ▼
┌──────────────────────────────────────────┐
│           Gateway Process (PID X)         │
│   hermes gateway run --replace            │
│   • Handles all incoming platform msgs    │
│   • Runs agent loop (model calls, tools)  │
│   • Sends replies back to platform        │
│   • Reads/writes ~/.hermes/sessions/      │
└──────────────────────────────────────────┘
               │
               │ (they share session store)
               │
┌──────────────────────────────────────────┐
│           TUI Process (PID Y)             │
│   hermes (in tmux or terminal)            │
│   • Local interactive chat only           │
│   • prompt_toolkit UI                     │
│   • Closing this window does NOTHING      │
│     to the gateway or platform chats      │
└──────────────────────────────────────────┘
```

## Key Facts

- **Closing the TUI window does NOT stop the agent.** The gateway runs independently.
- **Gateway can run as a systemd user service** (`hermes gateway install`) or via `hermes gateway run` foreground.
- **In WSL**, the gateway typically runs in the background with `systemd --user` or via `nohup`.
- **Multiple TUI sessions** can be attached at the same time — they all share the session store.

## How to Check What's Running

```bash
# See all Hermes processes
ps aux | grep -E 'hermes|gateway' | grep -v grep

# Check gateway status (if installed as service)
hermes gateway status

# Or check systemd
systemctl --user status hermes-gateway
```

## Common Confusion Patterns

| User says | They mean | Resolution |
|-----------|-----------|------------|
| "Should I close this blue window?" | "Will closing the terminal disconnect my Feishu chat?" | No — that's just the TUI. Gateway handles Feishu. Close it safely. |
| "You're still in the background, right?" | "Is the agent still running even though I closed the window?" | Yes — gateway process is independent. |
| "Why is it slow? Let me exit the agent." | User thinks closing TUI will improve speed | It won't help. Check model provider speed, not local processes. |
