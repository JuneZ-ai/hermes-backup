# Feishu Calendar (日历) API 操作指南

> 场景：通过飞书 Open API 查询/创建日历日程
> 凭证来源：`~/.hermes/.env` → `FEISHU_APP_ID` + `FEISHU_APP_SECRET`
> 本会话首次打通日期：2026-05-21

## 鉴权

与 Bitable 共享同一鉴权流程：

```python
import requests
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": app_id, "app_secret": app_secret},
    timeout=10
)
token = resp.json()["tenant_access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

## 已验证的 API 端点

### 列出主日历日程

```python
GET /open-apis/calendar/v4/calendars/primary/events?page_size=50
```

**关键坑：** `page_size` 最小值是 **50**（不是默认的 20）。传 `page_size=5` 会报 `code: 99992402` (`the min value is 50`)。

返回格式示例：

```json
{
  "code": 0,
  "data": {
    "items": [...],
    "has_more": false,
    "sync_token": "..."
  }
}
```

每个 event 包含：`summary`（标题）、`start_time`/`end_time`（含 `timestamp` + `timezone`）、`event_id`、`description`。

### 创建日程

```python
POST /open-apis/calendar/v4/calendars/primary/events
{
  "summary": "📝 Hermes 日历测试",
  "description": "这是一条由 API 自动创建的测试日程",
  "start_time": {
    "timestamp": "1779386400",   # Unix 秒级时间戳（字符串）
    "timezone": "Asia/Shanghai"
  },
  "end_time": {
    "timestamp": "1779390000",
    "timezone": "Asia/Shanghai"
  }
}
```

**关键坑：** 字段名是 `start_time`/`end_time`（**不是** `start`/`end`），且内部用 `timestamp` + `timezone`（**不是** `datetime`/`date`/`time`）。时间戳为 **秒级** Unix 时间戳（字符串形式）。

### 创建重复日程（RRULE）

```python
POST /open-apis/calendar/v4/calendars/primary/events
{
  "summary": "📥 第二大脑 · 每日喂料",
  "description": "记录今天读/看/学了什么",
  "start_time": {
    "timestamp": "1779440400",
    "timezone": "Asia/Shanghai"
  },
  "end_time": {
    "timestamp": "1779442200",
    "timezone": "Asia/Shanghai"
  },
  "recurrence": "FREQ=DAILY;INTERVAL=1",   # RRULE 格式，支持 FREQ=WEEKLY;BYDAY=MO,TU,WE 等
  "color": 6,                                # 0=红 1=橙 2=黄绿 3=绿 4=青 5=蓝 6=紫 7=灰
  "free_busy_status": "free"                 # "busy"(占用) / "free"(空闲) / "tentative"(待定)
}
```

支持常见 RRULE：`FREQ=DAILY`, `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR`, `FREQ=MONTHLY`。

### 删除日程

```python
DELETE /open-apis/calendar/v4/calendars/primary/events/{event_id}
```

先通过列出日程获取 `event_id`，再删除。适用于清理测试数据。

成功返回：

```json
{
  "code": 0,
  "data": {
    "event": {
      "event_id": "1b202492-...",
      "summary": "📝 Hermes 日历测试",
      "start_time": { "timestamp": "1779386400", "timezone": "Asia/Shanghai" },
      "end_time": { "timestamp": "1779390000", "timezone": "Asia/Shanghai" },
      "app_link": "https://applink.feishu.cn/client/calendar/event/detail?..."
    }
  }
}
```

### 创建全日期程（不跨天）

使用 `start_time.date` 格式：

```python
{
  "summary": "全天事件",
  "start_time": { "date": "2026-05-22", "timezone": "Asia/Shanghai" },
  "end_time": { "date": "2026-05-23", "timezone": "Asia/Shanghai" }  # 结束日期是开始日期的下一天
}
```

## 所需权限

| 权限 scope | 说明 | 是否需要 |
|-----------|------|---------|
| `calendar:calendar:readonly` | 只读日程 | 查日程用 |
| `calendar:calendar` | 读写日程 | 创建/修改日程用 |
| `calendar:calendar.event:read` | 读事件 | 部分场景需 |

**开通方式：** 开发者后台 → 权限管理 → 日历 → 勾选 → 版本管理与发布 → 发布。

## 经验总结

1. 日历 API v4 使用 `start_time`/`end_time`（带下划线），不是 `start`/`end`
2. 时间字段传入 Unix 秒级时间戳（字符串） + 时区
3. `page_size` 最小值 50，没有默认值
4. 读取权限 (`calendar:calendar:readonly`) 和写入权限 (`calendar:calendar`) 是分开的 scope
5. 创建成功后返回 `app_link` 可直接跳转到飞书日历
