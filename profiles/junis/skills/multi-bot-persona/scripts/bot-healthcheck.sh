#!/bin/bash
# Multi-bot health check — run from any profile
# Usage: bash ~/.hermes/profiles/junis/skills/multi-bot-persona/scripts/bot-healthcheck.sh

PROFILES="junis yanqing huanglaoxie luban saodiseng"
GROUP_ID="oc_a57651e58047606b3d8f6231ebb45f49"
ALL_OK=true

echo "════════════════════════════════════════════"
echo "  六韬Bot团队 · 快速健康检查"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════"

for P in $PROFILES; do
  ENV_FILE="$HOME/.hermes/profiles/$P/.env"
  LOG_FILE="$HOME/.hermes/profiles/$P/logs/gateway.log"
  
  printf "\n[%s]\n" "$P"
  
  # 1. Process check
  PID=$(ps aux | grep "python.*-p $P.*gateway" | grep -v grep | awk '{print $2}')
  if [ -n "$PID" ]; then
    printf "  PID: %-6s ✅\n" "$PID"
  else
    printf "  PID: ----- ❌ 进程不存在\n"; ALL_OK=false
  fi
  
  # 2. .env check
  if [ -f "$ENV_FILE" ]; then
    POLICY=$(grep "^FEISHU_GROUP_POLICY=" "$ENV_FILE" | cut -d= -f2)
    [ -z "$POLICY" ] && POLICY="(未设置)"
    printf "  群策略: %-10s\n" "$POLICY"
  else
    printf "  .env:  ❌ 文件不存在"; ALL_OK=false
  fi
  
  # 3. Gateway connection check
  if [ -n "$PID" ]; then
    CONN=$(ss -tnp 2>/dev/null | grep "$PID" | grep ESTAB | grep -c "443")
    if [ "$CONN" -gt 0 ]; then
      printf "  连接:   %d个ESTAB ✅\n" "$CONN"
    else
      printf "  连接:   无ESTAB ❌\n"; ALL_OK=false
    fi
  fi
  
  # 4. Gateway log check — last inbound activity
  if [ -f "$LOG_FILE" ]; then
    LAST_RAW=$(grep -a "Received raw message" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oP '\d{2}:\d{2}:\d{2}' || echo "从未")
    LAST_GROUP=$(grep -a "Inbound group" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oP '\d{2}:\d{2}:\d{2}' || echo "从未")
    printf "  最后消息: raw=%s | group=%s\n" "$LAST_RAW" "$LAST_GROUP"
  fi

  # 5. SOUL.md check
  if [ -f "$HOME/.hermes/profiles/$P/SOUL.md" ]; then
    printf "  SOUL.md: ✅\n"
  else
    printf "  SOUL.md: ❌ 不存在\n"; ALL_OK=false
  fi
done

# Group-level check (from the first available token)
echo ""
echo "── 群级别检查 ──"
TOKEN_RAW=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"cli_aa869b8d6b3c5cc3","app_secret":"qSk4tz1A15aWo5K4eFw2lbhibgMAVaHN"}')
TOKEN=$(echo "$TOKEN_RAW" | sed 's/.*"tenant_access_token":"\([^"]*\)".*/\1/')
GRP=$(curl -s -X GET "https://open.feishu.cn/open-apis/im/v1/chats/$GROUP_ID" -H "Authorization: Bearer $TOKEN" 2>/dev/null)
BOT_CNT=$(echo "$GRP" | grep -oP '"bot_count":"\K[^"]+')
GRP_NAME=$(echo "$GRP" | grep -oP '"name":"\K[^"]+')
if [ -n "$BOT_CNT" ]; then
  printf "  群名: %s | 群内Bot数: %s ✅\n" "$GRP_NAME" "$BOT_CNT"
else
  printf "  无法获取群信息 ❌\n"; ALL_OK=false
fi

echo ""
if $ALL_OK; then
  echo "  ✅ 全部正常"
else
  echo "  ⚠️ 存在问题，检查以上 ❌ 标记"
fi
echo "════════════════════════════════════════════"
