# Feishu Open API 应用配置查询

当需要查询或排查 Hermes 的飞书应用配置时，可以直接通过 Feishu Open API 获取信息，无需进入飞书开发者后台网页。

## 前提

需要以下凭证（来自 `~/.hermes/.env`）：
- `FEISHU_APP_ID` — 应用的 App ID
- `FEISHU_APP_SECRET` — 应用的 App Secret（需要完整值，.env 中可能被 mask）

## 通用流程

### 1. 获取 tenant_access_token

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}'
```

返回示例：
```json
{"code":0,"expire":4685,"msg":"ok","tenant_access_token":"t-g1045jg9K6RJBB7PUVFZGE5XOUEIZMBPIR3PQCIS"}
```

Token 有效期约 2 小时（expire=秒数），过期后需重新获取。

### 2. 查询应用基本信息

```bash
curl -s "https://open.feishu.cn/open-apis/application/v6/applications/<APP_ID>?lang=zh_cn" \
  -H "Authorization: Bearer <TOKEN>"
```

返回内容：app_name, description, scopes(权限列表), status, online_version_id, visibility。

### 3. 查询机器人信息

```bash
curl -s "https://open.feishu.cn/open-apis/bot/v3/info" \
  -H "Authorization: Bearer <TOKEN>"
```

返回内容：bot.activate_status(2=启用), app_name, avatar_url, ip_white_list, open_id。

### 4. 查询应用版本详情（含已订阅事件）

```bash
curl -s "https://open.feishu.cn/open-apis/application/v6/applications/<APP_ID>/app_versions/<VERSION_ID>?lang=zh_cn" \
  -H "Authorization: Bearer <TOKEN>"
```

返回内容：events(已订阅事件列表), scopes(该版本的权限范围), ability(bot配置), visibility(可见范围)。

VERSION_ID 从应用基本信息中的 `online_version_id` 字段获取。

### 5. 查询应用版本列表

```bash
curl -s "https://open.feishu.cn/open-apis/application/v6/applications/<APP_ID>/app_versions?lang=zh_cn&page_size=5" \
  -H "Authorization: Bearer <TOKEN>"
```

## 已知限制

| 操作 | API 支持 | 替代方案 |
|------|:--------:|---------|
| 查询应用信息 | ✅ | — |
| 查询机器人状态 | ✅ | — |
| 查询事件订阅 | ✅ | app_versions 中的 events 字段 |
| 查询权限列表 | ✅ | scopes 字段 |
| 修改权限范围 | ❌ | 需登录开发者后台网页 |
| 发布新版本 | ❌ | 需登录开发者后台网页 |
| 修改事件订阅 | ❌ | 需登录开发者后台网页 |

## 常见排查案例

### 审批卡片报错 200340
1. 获取 token
2. 查询应用版本详情
3. 检查 `events` 中是否包含 `card.action.trigger`
4. 如不包含 → 缺少卡片交互事件，需在开发者后台手动添加

### 权限过于宽泛需要精简
1. 获取 token，查询应用信息提取 `scopes`
2. 标记必须保留的（核心通信类）和可删除的（人事/日历/文档等）
3. 给出保留/删除清单，告知用户需在开发者后台手动操作

## 必须保留的核心通信权限

| Scope | 说明 |
|-------|------|
| `im:message` | 获取与发送消息（最核心） |
| `im:chat` | 获取与更新群组（会话上下文） |
| `im:message.p2p_msg:readonly` | 读取用户单聊消息 |
| `im:resource` | 获取与上传图片或文件 |

## 按需开启的文档权限

| Scope | 用途 |
|-------|------|
| `docx:document:readonly` | 读取文档内容 |
| `docs:document.comment:read` | 查看文档评论 |
| `docs:document.comment:create` | 添加文档评论 |
| `docs:document.comment:write_only` | 回复文档评论 |
