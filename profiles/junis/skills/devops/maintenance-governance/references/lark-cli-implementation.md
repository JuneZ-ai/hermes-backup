# lark-cli 版本巡检 · 实现参考

本文件记录 maintenance-governance 看门狗巡检模式在 lark-cli 上的首次落地实践，供后续同类巡检参考。

## 脚本位置

`~/.hermes/scripts/check-lark-cli-update.sh`

## 脚本内容

```bash
#!/bin/bash
# lark-cli 版本巡检脚本
# 仅检测并通知，不做更新（需要用户确认）
# 无更新时静默退出（watchdog pattern）

CURRENT=$(lark-cli --version 2>/dev/null | grep -oP '[\d]+\.[\d]+\.[\d]+')
LATEST=$(npm view @larksuite/cli version 2>/dev/null)

if [ -z "$CURRENT" ] || [ -z "$LATEST" ]; then
    exit 0
fi

if [ "$CURRENT" != "$LATEST" ]; then
    echo "🔔 lark-cli 有新版本"
    echo ""
    echo "当前版本：$CURRENT"
    echo "最新版本：$LATEST"
    echo "npm: https://www.npmjs.com/package/@larksuite/cli"
    echo "GitHub: https://github.com/larksuite/cli"
    echo ""
    echo "如需更新，请回复：更新 lark-cli"
    exit 0
fi
# Same version -> silent
exit 0
```

## Cron 配置

| 参数 | 值 |
|------|-----|
| job_id | 9deb89a65ff5 |
| name | lark-cli 版本巡检 |
| schedule | 0 9 */5 * *（每5天早9点） |
| script | check-lark-cli-update.sh |
| no_agent | true |
| deliver | origin |

## 手动更新流程（用户确认后）

```bash
# Step 1: 备份
lark-cli --version > /home/hermes/.hermes/scripts/lark-cli-backup-v1.0.41.txt

# Step 2: 更新
npm install -g @larksuite/cli

# Step 3: 验证
lark-cli --version
```

## 注意事项

- `no_agent=true` 模式要求脚本自行处理所有逻辑，不经过 LLM
- 非空 stdout = 投递给用户；空 stdout = 静默（无消息）
- 备份文件命名规范：`<tool>-backup-v<version>.txt`
- cron 脚本路径必须是 `~/.hermes/scripts/` 下的相对路径
