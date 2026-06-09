# 飞书群聊搭建（多Bot协作）

> 创建于 2026-06-02 会话。更新于 2026-06-03 会话（修正Bot加群方式 + 新增「Bot不响应」debug指南）。

## 架构前提

五个Bot各自注册了**独立的飞书应用**（不同的 App ID / App Secret），每条 Gateway 使用不同的 `FEISHU_APP_ID` 连接。

```bash
# 每个profile的.env配置
FEISHU_APP_ID=cli_xxx   # 每个Bot不同
FEISHU_APP_SECRET=xxx   # 每个Bot不同
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
```

## 群聊搭建步骤

### 1. 确认各Bot已发布

通过各Bot的 tenant_access_token 调用 `GET /open-apis/bot/v3/info` 检查：

```bash
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}' | sed 's/.*"tenant_access_token":"\([^"]*\)".*/\1/')

curl -s -X GET 'https://open.feishu.cn/open-apis/bot/v3/info' -H "Authorization: Bearer $TOKEN"
# → activate_status: 2 = 已发布且激活
```

`activate_status` 必须为 `2`，否则需要先在飞书开放平台完成发布流程。各Bot的飞书显示名（用于群内@选择）从 `app_name` 字段确认。

### 2. 创建群聊（API方式）

使用任意一个已发布Bot的 token 创建群：

```bash
TOKEN="<已获取的tenant_access_token>"

curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/chats' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "六韬工作室",
    "description": "六韬Bot团队工作群",
    "chat_mode": "group",
    "chat_type": "private",
    "membership_approval": "no_approval_required"
  }'
# 返回值中 data.chat_id = oc_xxx
```

**重要**：创建的群初始成员为空。需要把人类用户加入群后才能进行后续操作。

### 3. 加人类用户进群

获取用户的 open_id（从已有聊天记录中提取，或通过用户搜索API获取），用创建群的Bot token加入：

```bash
curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/chats/<chat_id>/members?member_id_type=open_id' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"id_list":["ou_xxx"]}'
# 空invalid/not_existed列表 = 添加成功
```

### 4. 各Bot用自己Token加自己进群（正确的API方式）

**关键修正（2026-06-03）**：之前文档写的 `member_id_type=open_id` + bot的open_id 会返回 `invalid_id_list`，无效。正确方式是使用 **`member_id_type=app_id`** + bot自己的 `cli_xxx` app_id。

```bash
# 对每个Bot（燕青、黄老邪、鲁班）执行：
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"<BOT_APP_ID>","app_secret":"<BOT_APP_SECRET>"}' | sed 's/.*"tenant_access_token":"\([^"]*\)".*/\1/')

curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/chats/<chat_id>/members?member_id_type=app_id' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"id_list":["<BOT_APP_ID>"]}'
# 期望：code:0, data: {invalid_id_list:[], not_existed_id_list:[], ...}
```

**验证加群是否成功**：`member_id_type=app_id` 加群时返回 `code:0` + 空列表是正常现象。必须通过群API的 `bot_count` 字段确认：

```bash
curl -s -X GET 'https://open.feishu.cn/open-apis/im/v1/chats/<chat_id>' \
  -H "Authorization: Bearer $TOKEN" | grep bot_count
# → "bot_count":"4" 表示4个Bot在群里
```

**为什么不同方式的效果差异：**

| 尝试 | 条件 | 结果 |
|:-----|:-----|:-----|
| Bot用自己的token + open_id加自己 | `member_id_type=open_id`, id=bot的open_id | ❌ `invalid_id_list` |
| 群内Bot用app_id加其他Bot | 跨app权限限制 | ❌ valid但 `invalid/not_existed` 空列表，没实际加 |
| 群内Bot用open_id加其他Bot | open_id跨app | ❌ `99992361: open_id cross app` |
| ✅ **Bot用自己的token + app_id加自己** | `member_id_type=app_id`, id=自己的cli_xxx | ✅ bot_count递增 |

**关键发现**：
- Bot不能跨app操作，`member_id_type=app_id` 配合其他Bot的 `cli_xxx` 在Junis的token下返回空列表不会出错，但实际也未生效
- 每个Bot必须用自己的token调加群API
- 验证是否成功必须看 `bot_count`，而不是add member API的返回码
- 群内成员API查询（`chat.members.get`）只显示人类用户，不显示Bot。Bot数量通过 `chat.get` 的 `bot_count` 字段确认

### 5. 配置群聊响应策略

在每个Bot的 `.env` 中添加：

```bash
FEISHU_GROUP_POLICY=mention   # 仅被@时才响应（多Bot同群建议）
# 可选值: open / mention / disabled
# Junis 可以设为 open 作为调度中枢
```

**重要**：`FEISHU_GROUP_POLICY` 的取值含义：
- `open` — Bot响应群内**所有消息**（适合调度中枢）
- `mention` — Bot只响应自己被 **@mention** 的消息（适合职能Bot）
- 该值写入 `.env` 文件，**修改后必须重启Gateway**才生效

## 配置FEISHU_BOT_OPEN_ID和FEISHU_BOT_NAME（关键！2026-06-03发现）

**这是本次调试最深的一课。** @mention检测依赖Bot的open_id和display name，虽然Gateway有自动发现机制（`_hydrate_bot_identity`），但该机制可能静默失败（DEBUG级别日志，错误不易察觉）。一旦失败，所有@mentions都会被静默丢弃。

### `_message_mentions_bot()` 源码级分析

Gateway的@检测核心在 `_message_mentions_bot()` 方法中（`gateway/platforms/feishu.py:4047-4068`）：

```python
for mention in mentions:
    mention_open_id = mention.id.open_id
    mention_user_id = mention.id.user_id
    mention_name = mention.name

    if mention_open_id and self._bot_open_id:
        if mention_open_id == self._bot_open_id:
            return True
        continue  # ← 关键行！ID不匹配时直接跳过，不走名称回退
    
    if mention_user_id and self._bot_user_id:
        if mention_user_id == self._bot_user_id:
            return True
        continue
    
    if self._bot_name and mention_name == self._bot_name:
        return True

return False
```

**关键行为（2026-06-03调试发现）**：
- 第57-60行：如果 `mention_open_id` 和 `self._bot_open_id` **都有值**，它们进行精确比较。**如果比较失败，直接 `continue`，不再走name回退**。这是正确的——如果你有ID就别用名字匹配。
- 但如果 `self._bot_open_id` **是空字符串**（自动发现失败），代码跳过ID比较，进入name比较。如 `self._bot_name` 也是空 → 没有任何匹配 → **函数返回 False**。
- **所以自动发现失败后，所有@mentions都会被无声拒绝**。

**为什么自动发现可能失败？**
- `_hydrate_bot_identity()` 调用 `/open-apis/bot/v3/info` 获取open_id
- 如果该API调用因网络/限流/Token过期等问题失败，日志会降级到DEBUG级别（`logger.debug`——默认日志级别INFO看不到）
- 失败后 `_bot_open_id` 和 `_bot_name` 保留空值
- 在 `_message_mentions_bot()` 中，如果 `_bot_open_id` 为空，跳过ID比较，进入name比较；如果 `_bot_name` 也为空，所有mention都不匹配 → **全部静默拒绝**

**最佳实践：在.env中显式配死，不要依赖自动发现。**

```bash
# 获取各Bot的open_id和name
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}')
TOKEN=$(echo "$TOKEN" | sed 's/.*"tenant_access_token":"\([^"]*\)".*/\1/')
curl -s -X GET 'https://open.feishu.cn/open-apis/bot/v3/info' -H "Authorization: Bearer $TOKEN"
# 返回: {"bot":{"app_name":"浪子燕青","open_id":"ou_b255d6cfafcca79e050d6e35126c40b2",...}}

# 写入.env
FEISHU_BOT_OPEN_ID=ou_b255d6cfafcca79e050d6e35126c40b2
FEISHU_BOT_NAME=浪子燕青
```

**为什么自动发现可能失败？**
- `_hydrate_bot_identity()` 调用 `/open-apis/bot/v3/info` 获取open_id
- 如果该API调用因网络/限流/Token过期等问题失败，日志会降级到DEBUG级别（`logger.debug`——默认日志级别INFO看不到）
- 失败后 `_bot_open_id` 和 `_bot_name` 保留空值
- 在 `_message_mentions_bot()` 中，如果 `_bot_open_id` 为空，跳过ID比较，进入name比较；如果 `_bot_name` 也为空，所有mention都不匹配 → **全部静默拒绝**

**所有Bot的.env必须包含的完整变量清单：**
```
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
GATEWAY_ALLOW_ALL_USERS=true
DEEPSEEK_API_KEY=sk-xxx
FEISHU_GROUP_POLICY=mention          # 群内Bot设为mention
FEISHU_BOT_OPEN_ID=ou_xxx           # ← 从/bot/v3/info获取，容易遗漏！
FEISHU_BOT_NAME=xxx                 # ← Bot显示名，容易遗漏！
```

### 7. 重启Gateway

```bash
# 正确方式：使用venv Python路径
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main -p <profile> gateway run --replace

# ❌ 错误方式：使用系统python3
python3 -m hermes_cli.main -p <profile> gateway run --replace  # 找不到模块！
```

`--replace` 会优雅关闭旧Gateway再启动新进程。如果失败，需手动kill旧PID：
```bash
kill <old_pid> && sleep 2
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main -p <profile> gateway run --replace
```

## 🔴 关键陷阱：`member_id_type=app_id` 加群API可能无声失败

**这是本次实战（2026-06-03）最深的一课：**

```bash
# 这段代码看起来成功了，但可能什么都没做！
curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/chats/<chat_id>/members?member_id_type=app_id' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"id_list":["cli_xxx"]}'
# 返回: {"code":0,"data":{"invalid_id_list":[],"not_existed_id_list":[],"pending_approval_id_list":[]},"msg":"success"}
```

**这个返回看起来像成功，但Bot可能根本没加进群！** 因为所有三个列表都为空——既没有无效ID、没有不存在ID、也没有待审批——你无法区分"已成功加入"和"什么也没发生"。

**唯一可靠的验证方式：查 `bot_count`**

```bash
curl -s -X GET 'https://open.feishu.cn/open-apis/im/v1/chats/<chat_id>' \
  -H "Authorization: Bearer <TOKEN>" | grep bot_count
# 如果加群前是3，加群后还是3 → API没生效
```

**最可靠的加Bot方法：人类用户在飞书客户端手动添加**

API方式（无论是用Bot自己的token还是跨app token）都不可靠。经过多次尝试，最终确认：
1. Bot用自己的token + `member_id_type=app_id` + 自己的`cli_xxx` → 有时返回空成功但不生效
2. Bot用自己的token + `member_id_type=open_id` + 自己的`open_id` → 返回 `invalid_id_list`
3. 群内Bot用token + `member_id_type=app_id` + 其他Bot的`cli_xxx` → 返回空成功不生效
4. 群内Bot用token + `member_id_type=open_id` + 其他Bot的`open_id` → `99992361: open_id cross app`

**结论：API加Bot入群不可靠，应指导用户在飞书客户端手动添加：** 群设置 → 「群机器人」/「机器人」→ 搜索Bot名称并添加。API适用于加人类用户进群。

## `channel_directory.json` 的原理与局限

**发现（2026-06-03）：`channel_directory.json` 是只读缓存，手动写入会被Gateway覆盖。**

该文件由Gateway在运行时从飞书WebSocket事件动态构建，并定期写入磁盘做checkpoint。但：

1. **手动编辑该文件不会生效** — Gateway重启后用自己的内部状态覆盖，不读此文件
2. **Gateway重启后，飞书服务器不保证重新发送群列表事件** — 导致channel_directory丢失群条目
3. **channel_directory是否包含群，不影响消息收发** — Junis不包含群的条目也能正常接收和回复群消息
4. 真正的消息过滤发生在 `FEISHU_GROUP_POLICY` 层面，与channel_directory无关

因此，如果点3成立（消息能到），但Bot不响应，绝大多数情况是用户没有使用正确的@mention，而不是配置问题。

## 「Bot不响应」调试指南（2026-06-03实战沉淀）

当用户在群里说「只有Junis回应，其他Bot都没有回应」时，按此清单排查：

### 第1层：进程和连接

```bash
# 都是Gateway进程吗？
ps aux | grep -E "gateway run" | grep -v grep
# 每个Bot应有1条ESTABLISHED连接到飞书
ss -tnp | grep python | grep ESTAB
```

### 第2层：Gateway日志

```bash
# 日志路径
tail -10 ~/.hermes/profiles/<profile>/logs/gateway.log
# grep群ID看是否有事件
grep "oc_a57651" ~/.hermes/profiles/<profile>/logs/gateway.log
# grep Bot加入群事件
grep "Bot added to chat" ~/.hermes/profiles/<profile>/logs/gateway.log
```

**预期**：如果Bot在群里，"Bot added to chat: oc_xxx" 应该出现。如果只有最早的记录（重启后没有），说明Gateway在WebSocket重连时没收到群事件。

### 第3层：channel_directory

```bash
cat ~/.hermes/profiles/<profile>/channel_directory.json
```

**检查**：feishu 列表中是否有 `type: group` 的条目。如果只有DM（type: dm），则Gateway不知道这个群的存在。

**原因**：channel_directory 是从WebSocket事件动态构建的，不是从文件读取的。Gateway重启后，飞书服务器不一定会重新发送群列表事件，导致channel_directory不包含群。

### 第4层：确认Bot是否在群里（关键一步）

不要只看channel_directory——它可能因重启丢失。用API确认：

```bash
# 查群详情，看bot_count
curl -s -X GET 'https://open.feishu.cn/open-apis/im/v1/chats/<chat_id>' \
  -H "Authorization: Bearer <token_of_any_bot_in_group>"
# 关注 "bot_count" 字段
```

`bot_count: 4` 表示4个Bot确实在群里。`bot_count: 0` 表示Bot不在群里。

**注**：`chat.members.get` 返回的 `member_total` 只计人类用户，不计Bot。Bot数只能从 `chat.get` 的 `bot_count` 确认。

### 第5层：检查消息是否送达（@mentions）

用户在群里发消息后，检查各Bot的gateway日志是否有 `Inbound group message received`：

```bash
grep "Inbound group" ~/.hermes/profiles/<profile>/logs/gateway.log | tail -3
```

如果Junis收到了而其他Bot没收到，且其他Bot设了 `FEISHU_GROUP_POLICY=mention`，**这是正常的**——消息没有@它们。

### 第6层：确认用户正确使用了@mention

**这是最常见的「Bot不响应」根因**：
- 用户发纯文本消息（如“让4个bot分别输入自己的ID名称”）→ 只有 `FEISHU_GROUP_POLICY=open` 的Bot会响应
- 需要 `@浪子燕青 跑个脚本` → 燕青才响应
- 在飞书客户端，**必须使用 @ 选择器**（打@从列表选），不能手动打字@

各Bot在群中的可搜索显示名：

| Bot | 飞书显示名 | @时用 |
|-----|-----------|-------|
| 燕青 | 浪子燕青 | @浪子燕青 |
| 黄老邪 | 黄老邪-分析师 | @黄老邪-分析师 |
| 鲁班 | 鲁班 | @鲁班 |
| Junis | Hermes-Junis助手 | @Hermes-Junis助手 |

### 第7层（诊断大招）：临时切 `open` 鉴别根因

如果1-6层都走完了还是不确定，用这招一刀切：

1. ✅ 先确认 `.env` 中包含 `FEISHU_BOT_OPEN_ID` 和 `FEISHU_BOT_NAME`（从 `/bot/v3/info` 获取）
2. 把疑似有问题的Bot的 `.env` 中 `FEISHU_GROUP_POLICY` 临时改为 `open`
3. 重启其Gateway
4. 让用户在群里**发一条普通纯文本消息（不用@）**
5. 观察结果：

| 结果 | 结论 |
|:-----|:-----|
| Bot回应了 | ✅ 消息送达正常！只是用户@没选对。告知用户使用飞书@选择器 |
| Bot没回应 | ❌ Bot根本上收不到群消息。排查飞书应用权限 / Bot是否在群 / 重新加群 |

**原理**：`open` 让Bot响应**所有**群内消息，如果 `open` 都不行，说明问题不在 @mention 层面，而是更深层的消息送达问题。

记得诊断完后改回 `mention`。

**2026-06-03实战验证确认**：此方法是一刀切开根因的高效方式。会话中三个Bot（燕青/黄老邪/鲁班）从 `mention` 切到 `open` 后，燕青立即在群里响应了普通消息。黄老邪和鲁班因WebSocket尚未稳定（重启后连接中）延迟了约30秒才响应。证实了：
- Bot收消息的底层通道是通的
- 问题的根因是用户@mention方式，不是配置问题
- Gateway重启后需要等待WebSocket建立稳定（约5-15秒）

### 快速健康检查（一键脚本）

`scripts/bot-healthcheck.sh` 提供一键检查所有5个Bot的进程、连接、策略、最后活动等状态：

```bash
bash ~/.hermes/profiles/junis/skills/multi-bot-persona/scripts/bot-healthcheck.sh
```

输出示例：
```
════════════════════════════════════════════
  六韬Bot团队 · 快速健康检查
════════════════════════════════════════════
[yanqing]
  PID: 19297   ✅
  群策略: open
  连接:   1个ESTAB ✅
  最后消息: raw=10:35:00 | group=10:35:12
  SOUL.md: ✅
...
  群名: 六韬工作室 | 群内Bot数: 4 ✅
  ✅ 全部正常
```

该脚本不消耗token，纯bash+API调用，适合巡检和debug。

### 调试流程图

```
Bot不响应
├─第1层: Gateway进程存活? → 否 → 重启Gateway
├─第2层: WebSocket已连接? → 否 → 排查网络/Token
├─第3层: channel_directory有群? → 否 → 可能重启丢失，继续
├─第4层: API查bot_count确认在群? → 否 → 用飞书客户端手动加Bot
├─第5层: 消息是否送达Bot? → 否 → 检查飞书事件订阅
├─第6层: 用户是否@了Bot? → 否 → 教用户用@选择器
└─第7层: 临时切open → Bot回了? 是=用户@问题; 否=深层消息送达问题
```

### `--replace` 重启的致命陷阱

从**当前profile的会话**中重启**其他profile的Gateway**时：

```bash
# ❌ 危险做法：三步杀
kill <old_pid>  # 1. 旧进程没了
# ← 此时如果 --replace 的新进程启动失败，两步都没了
/usr/local/lib/hermes-agent/venv/bin/python -m ... gateway run --replace  # 2. 新进程没起来
```

**后果**：旧进程已被SIGTERM（`--replace`优雅关闭）或kill杀掉，新进程如果启动失败（路径错误、模块找不到等），你同时失去了新进程和旧进程。

**正确的做法是分步执行**：

```bash
# ✅ 安全做法
# 第一步：先启动新进程（带 --replace），让它先尝试优雅替换
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main -p <profile> gateway run --replace &
# 检查新进程日志是否正常
sleep 5
ps aux | grep <profile> | grep gateway
ss -tnp | grep <pid>
tail -5 ~/.hermes/profiles/<profile>/logs/gateway.log
# 如果新进程正常 → 旧进程已被 --replace 自动关闭
# 如果新进程失败 → 旧进程还在（SIGTERM没生效），此时再手动 kill

# 如果 --replace 失败，不得已才手动kill:
kill <old_pid> && sleep 2
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main -p <profile> gateway run --replace
```

**从非本profile会话中重启时，必须使用完整venv路径**：

```bash
# 正确
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main -p <profile> gateway run --replace
# 错误（模块找不到）
python3 -m hermes_cli.main -p <profile> gateway run --replace
# 错误（terminal后台启动时sleep会导致路径问题叠加）
sleep 2 && /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main -p <profile> gateway run --replace
```

## 常用API调用须知

### Token有效期

`tenant_access_token` 有效期约 4831秒（~80分钟）。超时后调用飞书API会返回：
```
{"code":99991663,"msg":"Invalid access token for authorization."}
```

**每次调用前重新获取**，不要在变量里存着用到底。

### 群信息查询确认

```bash
curl -s -X GET 'https://open.feishu.cn/open-apis/im/v1/chats/<chat_id>' \
  -H "Authorization: Bearer $TOKEN"
# bot_count — 群中机器人数量
# member_total — 群中人类用户数量（注意：不包含bot）
```

## 常见问题

### 用户搜不到Bot

- Bot未在飞书开放平台发布 → 检查 `activate_status`
- Bot发布后需等待1-2分钟生效
- 确认Bot名称在群设置的「机器人」区域搜索（不是「添加成员」）

### 用户@所有人Bot没有反应（高频踩坑）

**这是最常见的UX痛点。** @所有人不会触发任何Bot。Bot只响应自己被@的消息。

正确操作：在输入框打 `@` → 从弹出的成员列表中选择Bot名称（如「浪子燕青」「黄老邪-分析师」「鲁班」）。

### 多个Bot同时响应同一消息

- 如果 `FEISHU_GROUP_POLICY` 被设为了 `open`，所有Bot都会响应群内每条消息
- 应将职能Bot设为 `mention`，只有调度中枢（Junis）设为 `open`

### Gateway重启后Bot不识别群

Gateway在WebSocket重连时，飞书服务器不保证重新发送群列表事件。如果 `channel_directory.json` 中丢失了群条目，可：

1. 在群里 @Bot 发一条消息 → 应该能触发Gateway学习到群
2. 或者重启Gateway（有时飞书重连时会重新发送群列表）
3. 最终方案：如果多次重启都不行，从群里移除Bot再加回来触发 `Bot added to chat` 事件
