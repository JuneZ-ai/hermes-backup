# Tool Update Protocol (User Preference)

## Core Rule

**Never auto-update any installed tool or package without explicit user confirmation.**

The user established this rule on 2026-05-29 (lark-cli context) and it applies to ALL software updates the agent performs.

## Protocol (4 Steps)

### 1️⃣ Backup — Save current version info
Before any update, write the current version to a backup file:
```bash
tool --version > ~/.hermes/backups/<tool-name>-backup-v<version>.txt
```
Backup location: `~/.hermes/backups/` (create if needed).

### 2️⃣ Notify — Tell the user what's available
Present a clear comparison:
- Current version
- Latest version
- Source (npm, pip, GitHub releases, etc.)
- Link to changelog or project page if relevant

### 3️⃣ Wait — Do NOT proceed until user says "update" or "go ahead"
The user must explicitly confirm. Passive silence or a later "ok" in a different message counts — but never assume consent just because no objection was raised. If the user acknowledged the notification but didn't say to proceed, do nothing.

### 4️⃣ Update — Execute the update
Only run the update after receiving explicit confirmation. After completion, verify the new version and report back.

## Watchdog Check Pattern (no_agent=True)

For periodic version checking (cron jobs), use `no_agent=True` watchdog scripts:

```bash
#!/bin/bash
# Silent when nothing to report, noisy when new version available
CURRENT=$(tool --version | grep -oP '[\d]+\.[\d]+[\d.]+')
LATEST=$(get_latest_version_cmd)

if [ -z "$CURRENT" ] || [ -z "$LATEST" ]; then
    exit 0
fi

if [ "$CURRENT" != "$LATEST" ]; then
    echo "🔔 <Tool> 有新版本"
    echo "当前版本：$CURRENT"
    echo "最新版本：$LATEST"
    echo ""
    echo "如需更新，请回复：更新 <tool>"
    exit 0
fi
# Same version -> silent
exit 0
```

Key properties:
- `no_agent=True` — no LLM cost, runs as pure script
- Empty stdout = silent (no notification sent to user)
- Non-empty stdout = delivered verbatim as the notification message
- Script instructs the user what to say to trigger the update

## Cron Schedule

Recommended: every 5 days (`0 9 */5 * *`). Weekly is also acceptable. Daily is excessive.

## Scope

This protocol applies to any tool update the agent performs on behalf of the user, including but not limited to:
- npm packages (lark-cli, hermes itself, etc.)
- pip packages
- GitHub CLI tools
- apt/homebrew packages
- Downloadable binaries
