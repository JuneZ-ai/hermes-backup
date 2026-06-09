# Feishu Bitable API Patterns

Key API quirks discovered during integration work (2026-05-21).

## Authentication

```python
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": app_id, "app_secret": app_secret},
    timeout=10
)
token = resp.json()["tenant_access_token"]
```

- Token expires in 7200s (2 hours). Always get fresh token for each batch.
- App credentials stored in `~/.hermes/.env`: `FEISHU_APP_ID`, `FEISHU_APP_SECRET`

## Table Operations

### Create Table
- Endpoint: `POST /open-apis/bitable/v1/apps/{app_token}/tables`
- Body must be wrapped in `{"table": {...}}`
- If `default_view_name` is provided, `fields` is REQUIRED
- If neither is provided, creates empty table with single Text index field

### Rename Table
- Endpoint: `PATCH /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}`
- Method is **PATCH**, not PUT (PUT returns 404)
- Body: `{"name": "新名称"}`

### List Tables
- Endpoint: `GET /open-apis/bitable/v1/apps/{app_token}/tables?page_size=10`

### Delete Table
- Endpoint: `DELETE /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}`

## Field Operations

### Add Field
- Endpoint: `POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields`
- Body includes `field_name`, `type`, optional `property` and `ui_type`

### Update Field (rename or change options)
- Endpoint: `PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}`
- **Must include `type`** in request body even just for renaming
- For SingleSelect fields, include full `property.options` array

### Delete Field
- Endpoint: `DELETE /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}`

### List Fields
- Endpoint: `GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields`

## Record Operations

### Create Record
- Endpoint: `POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`
- Body: `{"fields": {...}}` — field names match the field definitions

### Update Record
- Endpoint: `PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}`
- Body: `{"fields": {...}}` — only specified fields are updated

### List Records
- Endpoint: `GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=50`

### Delete Record
- Endpoint: `DELETE /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}`

## DateTime Critical Detail

**DateTime field values must be in MILLISECONDS since epoch.**

```python
# CORRECT: milliseconds
today_ms = int(time.mktime(time.strptime("2026-05-21", "%Y-%m-%d"))) * 1000

# WRONG: this gives 1970 dates
wrong = int(time.time())  # seconds, not milliseconds
```

## Common Error Codes

| Code | Meaning | Fix |
|------|---------|-----|
| 0 | Success | — |
| 1254001 | WrongRequestBody | Check body format (e.g., missing `table` wrapper) |
| 1254045 | FieldNameNotFound | Field name in record doesn't match table schema |
| 99992402 | Field validation failed | Missing required field (e.g., `type` in field update) |
| 99991672 | Access denied | Missing permission scope; enable in dev console + publish |

## Calendar API

### List Calendar Events
```python
GET /open-apis/calendar/v4/calendars/primary/events?page_size=50
```

### Create Event (with recurrence)
```python
POST /open-apis/calendar/v4/calendars/primary/events
{
    "summary": "...",
    "description": "...",
    "start_time": {"timestamp": "epoch_seconds", "timezone": "Asia/Shanghai"},
    "end_time": {"timestamp": "epoch_seconds", "timezone": "Asia/Shanghai"},
    "recurrence": "FREQ=DAILY;INTERVAL=1",
    "color": 6,
    "free_busy_status": "free"
}
```
- `start_time`/`end_time` use `timestamp` and `timezone` (not `start`/`end` as in some docs)
- `recurrence` uses iCal RRULE format
- `page_size` minimum is 50 (not smaller)
- Calendar time uses **seconds** (epoch), NOT milliseconds (unlike bitable)

## Task API
```python
GET /open-apis/task/v2/tasks?page_size=5
```
Simple, standard REST. No special quirks.

## Drive API
```python
GET /open-apis/drive/v1/files?page_size=5
```
Returns files and bitables in the bot's accessible drive scope.
