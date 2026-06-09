# Feishu Base (Bitable) Sync from Obsidian

## Overview

Sync daily搭建日志 entries from Obsidian vault to a Feishu Base (多维表格) table via the Feishu Open API, using the existing Hermes Feishu bot credentials.

## Prerequisites

- Feishu bot credentials in `~/.hermes/.env`: `FEISHU_APP_ID`, `FEISHU_APP_SECRET`
- Bitable permission enabled in Feishu Open Platform app config
- Base token and table ID from the target Feishu Base URL

## Credential Access

The Feishu bot credentials live in the Hermes `.env` file. The full secret is readable via Python — grep output may mask it with `...`:

```python
with open("/home/hermes/.hermes/.env") as f:
    for line in f:
        if "FEISHU_APP_SECRET" in line:
            secret = line.strip().split("=", 1)[1]
```

### API Flow

#### Get Tenant Access Token

```python
r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", json={
    "app_id": APP_ID, "app_secret": APP_SECRET
})
token = r.json()['tenant_access_token']
```

#### Read Existing Records (for dedup)

```python
url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/records?page_size=500"
r = requests.get(url, headers=headers)
records = r.json()['data']['items']
# Handle pagination: check data['has_more'], use data['page_token']
```

#### Add a Record

```python
fields = {
    "操作内容": "Task description",
    "领域": "知识库基建",        # must match existing single-select option
    "时间": 1719072000000,     # UTC timestamp in milliseconds
    "状态": "✅ 已完成",        # must match existing single-select option
    "备注": "optional"
}
r = requests.post(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/records",
    headers=headers, json={"fields": fields})
```

### Field Options (搭建日志 Base)

| Field | Type | Options |
|-------|------|---------|
| 操作内容 | text | Free text |
| 领域 | single-select | 飞书权限开通, 工具配置, 知识库基建, 架构决策, API打通验证 |
| 时间 | date | ms timestamp |
| 状态 | single-select | ✅ 已完成, ⏳ 待跟进 |
| 备注 | text | Free text |

### Cron Job Setup

```python
cronjob(action="create",
    name="搭建日志→飞书同步",
    schedule="0 21 * * *",       # daily 21:00
    script="scripts/sync-log-to-feishu.py",
    workdir="/home/hermes/.hermes/profiles/yanqing")
```

### Script Logic

1. Get token → read all existing records (build dedup set from `操作内容`)
2. Parse搭建日志 markdown — split by `## YYYY-MM-DD` headers
3. Extract table rows containing `✅` or `⏳` status markers
4. For each unsynced task, POST new record
5. Auto-classify 领域 via keyword matching on task name

### Pitfalls

- **Masked secret**: App secret from `grep` may show `...`. Read via Python for the full value.
- **Dedup key**: Use `操作内容` text. Ensure task names are unique enough.
- **搭建日志 is accumulating**: Script must only READ the file, never write.
- **Timestamp**: Convert `YYYY-MM-DD` → ms: `datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000`
