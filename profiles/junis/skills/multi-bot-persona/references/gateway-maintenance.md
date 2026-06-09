# Profile Gateway 维护记录

## 根因

WSL process 模式不像 systemd 有保活机制。网关进程会因以下原因死亡：
- WSL 内核缓存回收（`drop_caches`）
- 系统休眠/网络波动导致飞书 WebSocket 断连
- 进程被系统 OOM 回收
- 无对话约2天后 agent cache 被 idle evict

**关键坑：** `gateway_state.json` 中的 `state: running` 不代表进程真的活着——它是上一次写入时的状态快照。看到 `running` 但飞书无响应时，必须用 `ps -p <PID>` 确认进程是否真实存活。

## 修复记录

### 断联修复通用步骤（2026-05-29）

```bash
# 1. 确认旧进程不在
ps aux | grep <profile名> | grep -v grep

# 2. 清理旧锁
rm -f ~/.hermes/profiles/<profile名>/gateway.lock
rm -f ~/.hermes/profiles/<profile名>/gateway.pid

# 3. 启动网关（background=true 模式）
hermes -p <profile名> gateway run --replace

# 4. 验证
cat ~/.hermes/profiles/<profile名>/gateway_state.json
```

### 扫地僧断联（2026-05-29）
- PID 14916 已死，gateway_state.json 未更新
- 最后对话：14:09，cache evict：15:12
- 根因：无对话约2天后被系统回收

### 三Bot全部断联（2026-05-29）
- 扫地僧：PID 14916 已死
- 燕青：旧进程已死
- 黄老邪：PID 14934 已死
- 均为假活状态（state=运行但进程不在了）
- 修复后：扫地僧 PID 5414、燕青 PID 5755、黄老邪 PID 8525

### 鲁班网关创建（2026-06-02）
- 新增第5个Bot `luban`（鲁班）——视觉工匠/看图出图
- Profile：`~/.hermes/profiles/luban/config.yaml`
- 模型：NIM `deepseek-ai/deepseek-v4-flash` 🆓 → DeepSeek官方兜底 💰
- 视觉通道：auxiliary.vision → NIM `microsoft/phi-4-multimodal-instruct`（当前中国区404）
- 生图：image_gen 工具集启用
- 禁用：terminal、browser、cronjob、delegation（纯视觉，不执行）
- 首次网关启动（PID 10092 via `terminal(background=true, notify_on_complete=true)`）：因未配置独立飞书应用，启动后自动上报飞书配对码。随后用户要求杀掉进程——用 `kill <PID>` + 清理 lock/pid/state文件
- **当前使用方式**：非独立飞书Bot，通过 multi-bot-persona 协议在 Junis 会话内身份切换（叫"鲁班"即可）
- **如需独立飞书Bot**：先创建飞书应用，在 config.yaml 配置 app_id/app_secret，然后 `hermes -p luban gateway run --replace`
- **watchdog 已注册**：`scripts/bot-watchdog.py` 的 PROFILES 列表已加入 `("luban", "鲁班")`

## 自动防御

2026-05-29 部署 `scripts/bot-watchdog.py`，cron 每30分钟巡检：

```bash
python3 ~/.hermes/scripts/bot-watchdog.py
# 输出示例：
# ✅ 🧘 扫地僧 (PID=5414) 正常运行
# ✅ 🏹 燕青 (PID=5755) 正常运行
# ✅ 🦅 黄老邪 (PID=8525) 正常运行
# ✅ 🔧 鲁班 (PID=10092) 正常运行
#
# 📊 四Bot健康度: 4/4
```

重启日志：`~/bot-watchdog/<profile>-restart.log`

### 现象
用户说"扫地僧和hermes断联了，重新连线"。

### 排查过程
1. 确认 profile 目录存在：`~/.hermes/profiles/saodiseng/`
2. 读 `gateway_state.json`：显示 `pid=14916, state=running, feishu=connected`
3. 查 PID 14916：进程已不存在（被系统回收）
4. 查最近日志 `logs/agent.log`：最后一条消息是 2026-05-27 14:09，之后 agent cache 在 15:12 被 idle evict
5. 查 `logs/gateway-exit-diag.log`：上次正常退出是 2026-05-27T02:55（SIGINT）

### 修复步骤
```bash
rm -f ~/.hermes/profiles/saodiseng/gateway.lock
rm -f ~/.hermes/profiles/saodiseng/gateway.pid
hermes -p saodiseng gateway run --replace
```

### 验证
```json
{"gateway_state":"running","platforms":{"feishu":{"state":"connected"}}}
```

### 根因
扫地僧 gateway 在无对话约2天后被系统回收，但 gateway_state.json 未自动更新。
