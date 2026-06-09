# 多Bot飞书部署完整性巡检清单

> 用途：对六韬工作室（或任意多Bot群聊）做定期完整性体检。
> 频率：部署后、Gateway重启后、疑似配置漂移时。
> 耗时：约 3-5 分钟。

---

## 1️⃣ Gateway 进程存活检查

**目标**：确认所有Bot的Gateway进程都在运行，没有被系统杀死/重启。

```bash
# 一键检查所有Bot进程
ps aux | grep -E "python.*-p (junis|yanqing|saodiseng|huanglaoxie|luban).*gateway" | grep -v grep
```

**正常输出**：每个Bot一行，格式如：
```
hermes 17309 ... python -m hermes_cli.main -p junis gateway run --replace
hermes 17376 ... python -m hermes_cli.main -p yanqing gateway run --replace
hermes 17374 ... python -m hermes_cli.main -p huanglaoxie gateway run --replace
hermes 17375 ... python -m hermes_cli.main -p luban gateway run --replace
hermes 17310 ... python -m hermes_cli.main -p saodiseng gateway run --replace
```

**异常处理**：
- 缺少某个Bot → 检查 `gateway.lock` / `gateway.pid` 残留锁
- 重启：`hermes -p <profile> gateway run --replace`
- 锁文件残留：`rm -f ~/.hermes/profiles/<profile>/gateway.{lock,pid}`

---

## 2️⃣ WebSocket 连接确认

**目标**：确认每个Bot的飞书WebSocket连接已建立。

```bash
# 查看飞书连接（每个Bot应有1条ESTABLISHED到59.36.x.x:443）
ss -pant | grep python | grep 443
```

**正常输出**：5条 `ESTABLISHED`，分别对应 `59.36.42.103:443` 或其他飞书IP。

---

## 3️⃣ .env 配置审计

**目标**：检查每个Bot的 `.env` 文件关键字段。

```bash
# 批量查看关键字段
for p in junis yanqing huanglaoxie luban saodiseng; do
  echo "=== $p ==="
  grep -E "^(FEISHU_APP_ID|FEISHU_GROUP_POLICY|FEISHU_CONNECTION_MODE|FEISHU_BOT_OPEN_ID|FEISHU_BOT_NAME)" ~/.hermes/profiles/$p/.env 2>/dev/null
done
```

### 3.1 FEISHU_GROUP_POLICY —— 🔴 最容易出错

| 值 | 效果 | 适用 |
|---|---|---|
| `mention` | ✅ **正确** — 只在被@时响应 | 群内Bot |
| `open` | ❌ **错误** — 响应群内所有消息 | 只有单Bot在群时可用 |
| 空/未设置 | ⚠️ 取决于代码默认值 | 不推荐 |

**多Bot同群时，务必全部设为 `mention`。** 否则所有Bot会同时响应每条消息。

**修改方式**（需重启Gateway生效）：
```bash
echo "FEISHU_GROUP_POLICY=mention" >> ~/.hermes/profiles/<profile>/.env
```

**⚠️ 已知陷阱**：
- `.env` 文件可能被重置（如profile重建），导致 `FEISHU_GROUP_POLICY` 回到默认值
- `echo >> .env` 追加时如果已有 `open` 行，不会覆盖，会产生重复行。**应使用 `mcp_filesystem_edit_file` 做精确替换**（`read_file` 在 cross-profile 场景下路径解析会出错，改用 `mcp_filesystem_read_text_file` 读取，`mcp_filesystem_edit_file` 编辑）
- 修改后必须重启Gateway

### 3.3 FEISHU_BOT_OPEN_ID 和 FEISHU_BOT_NAME —— ⚠️ 隐蔽但关键

**这是本次调试深坑（2026-06-03）。** @mention检测依赖这两个字段，虽然Gateway有自动发现机制，但可能静默失败，导致所有@被静默丢弃。

| 变量 | 作用 | 获取方式 |
|---|---|---|
| `FEISHU_BOT_OPEN_ID` | @mention ID匹配 | `curl /open-apis/bot/v3/info` 返回的 `open_id` |
| `FEISHU_BOT_NAME` | @mention 名称兜底匹配 | `app_name` 字段 |

**注意**：自动发现（`_hydrate_bot_identity`）失败时仅输出DEBUG日志，默认INFO级别看不到。失败后这俩变量为空，`_message_mentions_bot()` 会拒绝所有@mention。

**解决方案**：在 `.env` 中**显式写死**这两个值，不要依赖自动发现。


确保每个Bot的 `.env` 包含其config.yaml中声明的所有provider对应的key：

| Provider | 环境变量 | 必配Bot |
|---|---|---|
| DeepSeek | `DEEPSEEK_API_KEY` | 全部 |
| StepFun | `STEPFUN_API_KEY` | junis, yanqing, huanglaoxie, saodiseng |
| NVIDIA NIM | `NVIDIA_API_KEY` / `OPENAI_API_KEY` | junis, yanqing, huanglaoxie |
| DashScope | `DASHSCOPE_API_KEY` | 若config.yaml配置了auxiliary.vision |

**重点检查**：如果config.yaml配置了 `auxiliary.vision`（如鲁班的qwen），对应key必须在.env中存在，否则vision功能不可用。

---

## 4️⃣ SOUL.md 人格定义检查

**目标**：确认每个Bot的SOUL.md存在且内容完整。

```bash
for p in junis yanqing huanglaoxie luban saodiseng; do
  f=~/.hermes/profiles/$p/SOUL.md
  lines=$(wc -l < "$f" 2>/dev/null || echo 0)
  echo "$p: $lines 行"
done
```

**检查要点**：
- ✅ 文件存在，行数 > 10
- ✅ 包含「职责」部分（你会做/不会做）
- ✅ 包含「群聊规则」（只在被@时回应）
- ✅ 内容与Bot角色匹配（燕青=执行型，黄老邪=分析型，等）

---

## 5️⃣ config.yaml 模型路由检查

**目标**：确认每个Bot的模型配置正确，provider路由指向正确端点。

### 关键字段检查

```bash
for p in junis yanqing huanglaoxie luban saodiseng; do
  echo "=== $p ==="
  grep -A2 "^model:" ~/.hermes/profiles/$p/config.yaml 2>/dev/null | head -3
  echo "---"
done
```

**检查要点**：
| 字段 | 应取值 | 说明 |
|---|---|---|
| `model.default` | `deepseek-v4-flash` | 主模型 |
| `model.provider` | `deepseek` | 指向官方 API |
| `model.api_key_env` | `DEEPSEEK_API_KEY` | 对应 .env 中的 key |
| `fallback_providers` | 应有 v4-pro | 主模型不可用时的兜底 |
| `platforms.feishu.enabled` | `true` | 飞书平台开启 |

### 工具集隔离检查

每个Bot按角色禁用了不必要的工具集：

| Bot | 应禁用的工具 |
|---|---|
| 燕青 | 无（全工具）
| 黄老邪 | `terminal`, `browser`, `delegation`, `cronjob`, `image_gen` 等 |
| 鲁班 | `terminal`, `browser`, `delegation`, `cronjob` 等 |
| 扫地僧 | `terminal`, `browser`, `delegation`, `cronjob`, `code_execution` 等 |
| Junis | 无（全工具，调度中枢）|

### 特殊配置确认

- **Junis的model_catalog**: `enabled: true`，但 `url: ''`（不拉远程目录，仅本地覆盖）
- **其他Bot的model_catalog**: 默认远程拉取（如有 `url`），或留空
- **各Bot的 display.language**: 中文Bot建议设为 `zh`

---

## 6️⃣ 完整巡检查速查表

| # | 检查项 | 命令/方法 | 预期结果 |
|---|---|---|---|
| 1 | Gateway进程 | `ps aux \| grep gateway` | 5行，各Bot一行 |
| 2 | WebSocket连接 | `ss -pant \| grep 443` | 5条ESTABLISHED |
| 3 | FEISHU_GROUP_POLICY | `grep FEISHU_GROUP_POLICY .env` | 全部 `mention` |
| 3.1 | FEISHU_BOT_OPEN_ID | `grep FEISHU_BOT_OPEN_ID .env` | 全部必须存在 |
| 3.2 | FEISHU_BOT_NAME | `grep FEISHU_BOT_NAME .env` | 全部必须存在 |
| 4 | API Key完整性 | 逐文件核对 | 与config.yaml声明的providers匹配 |
| 5 | SOUL.md存在 | `ls -la SOUL.md` | 5个文件均存在 >10行 |
| 6 | 模型路由 | `grep -A2 "^model:" config.yaml` | 统一 deepseek-v4-flash |
| 7 | 飞书平台开启 | `grep feishu: -A2 config.yaml` | `enabled: true` |

---

## 7️⃣ 常见问题对照表

| 症状 | 可能原因 | 解决 |
|---|---|---|
| 群里发消息没Bot回 | Gateway进程挂了 | 检查进程，重启Gateway |
| 群里@某个Bot不回，其他Bot回 | 该Bot未加群/群内名称不匹配 | 检查群成员，确认@用的名字 |
| 所有Bot同时回一条消息 | `FEISHU_GROUP_POLICY=open` | 改为 `mention`，重启Gateway |
| 群里消息无响应（@所有人） | @所有人不触发Bot，需@具体Bot名 | 用飞书@选择器选Bot |
| 鲁班说看不到图片 | `DASHSCOPE_API_KEY` 未配 | 补key到.env |
| **已确认Bot在群、@格式正确，还是不响应** | 可能是`mention`政策下消息送达不可见 | **临时切`open`诊断**：把Bot的`FEISHU_GROUP_POLICY`改为`open`，重启，发一条纯文本消息。Bot回了 → 是@问题；没回 → 深层送达问题 |

---

## 8️⃣ 巡检报告模板

巡检完成后，可参考以下简洁格式汇报：

```
## 六韬工作室巡检报告

### ✅ 正常
- 进程：5/5 Gateway存活
- 连接：5条WebSocket已建立
- 模型：全部指向 deepseek-v4-flash (DeepSeek API)

### 🔴 需修复
- [Bot名] FEISHU_GROUP_POLICY=open，需改为 mention
- [Bot名] 缺少 DASHSCOPE_API_KEY

### 🟢 待验证
- 群内@响应未实测
```
