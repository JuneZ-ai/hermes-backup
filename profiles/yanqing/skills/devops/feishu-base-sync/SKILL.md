---
name: feishu-base-sync
title: 飞书多维表格三表同步
description: 飞书多维表格三表同步（搭建日志 + 每日记录 + 收藏随想录）。自动留痕，无动作也留记录，月度长度连续覆盖。
---

# feishu-base-sync

飞书多维表格三表同步。每天 21:00 cron 自动运行，同步 OB vault 数据到飞书 Base。

## 什么时候用

- 用户要求同步搭建日志/每日记录到飞书
- 发现飞书 Base 表格有空白日期需要补录
- 用户抱怨日志没有更新

## 三表结构

| 表 | Table ID | 同步方式 |
|:---|:---------|:--------|
| 搭建日志 | `tbllV9WgN64Zwput` | 从 `第二大脑搭建日志.md` 解析 ✅ 标记的任务行 |
| 每日记录 | `tblTLllADiUdhL6e` | 自动生成，有搭建动作写摘要，无动作写「今日无重大搭建动作」 |
| 收藏随想录 | `tblydJHMALlK3stv` | 自动生成留痕条目「无新增收藏」 |

## 核心脚本

**`sync-all-to-feishu.py`** — 三表统一同步脚本
路径: `~/.hermes/profiles/yanqing/scripts/sync-all-to-feishu.py`

**`backfill-feishu-tables.py`** — 空白日期补录脚本（一次性补历史缺漏）
路径: `~/.hermes/profiles/yanqing/scripts/backfill-feishu-tables.py`

**旧脚本（已废弃）**: `sync-log-to-feishu.py`（只同步搭建日志的单表版）

## 执行步骤

### 1. 日常同步（cron 自动）

cron job ID: `35ae3c98874f`
每天 21:00 执行 `sync-all-to-feishu.py`

手动运行: `python3 /home/hermes/.hermes/profiles/yanqing/scripts/sync-all-to-feishu.py`

### 2. 补录空白日期

当发现飞书表中存在日期缺口时，运行:

```bash
python3 /home/hermes/.hermes/profiles/yanqing/scripts/backfill-feishu-tables.py
```

该脚本自动检查 5/21 至今的每日记录和收藏随想录表，补上所有缺失日期的留痕条目。

### 3. 验证覆盖

用 Python requests 调飞书 bitable API，获取所有记录按日期排序，检查 5/21~today 无缺口。

## 认证信息

- APP_ID: `cli_aa869b8d6b3c5cc3`
- APP_SECRET: `qSk4tz1A15aWo5K4eFw2lbhibgMAVaHN`
- BASE_TOKEN: `NzuPbMtMFa0wUusVQKwc69lenib`

### API 调用模式

```python
def get_token():
    r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=10)
    return r.json()["tenant_access_token"]

def add_record(token, table_id, fields):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{table_id}/records",
        headers=headers, json={"fields": fields}, timeout=10)
    return r.json()
```

## 用户偏好（必须遵守）

1. **自主执行，不需要督促** — 日常同步是固定工作，不要等用户提醒
2. **每日记录：无活动也留痕** — 即便当天没有任何搭建动作，也写入一条留痕记录
3. **收藏随想录：不留空壳** — 只有真实收藏/喂料才写入。无内容的日子不写留痕，发现留痕条目可删除
4. **补录空白** — 发现历史日期缺口要主动补录，不要等用户指出
5. **连续覆盖** — 三表日期应从 5/21 起连续覆盖至今，不允许有空白日

## 数据库限制

### 视图排序 API 不生效

当前 app (cli_aa869b8d6b3c5cc3) 的权限范围仅覆盖记录读写，不覆盖视图配置。
- `PATCH /views/{view_id}` 返回 code=0 但 `view_property` 始终为 null
- 视图排序需要用户在飞书 UI 中点击列头手动设置（一键操作，会保存）
- 程序化排序：使用 `POST records/search` 的 `sort` 参数（已验证可用）

### SingleSelect 字段写入规则

飞书 `SingleSelect` 字段写入时传 option 的 name 字符串（非 id），不能传数字。

正确：`"评分": "⭐⭐⭐⭐⭐"`
错误：`"评分": 5`

## 清理违规留痕

当收藏随想录中出现空留痕条目时：

```bash
python3 /home/hermes/.hermes/profiles/yanqing/scripts/cleanup-collections.py
```

该脚本删除分类为「留痕」、标题含「无新增收藏」、感悟含「补录」的条目。

## 警告

- 搭建日志的日期解析基于 `## 2026-MM-DD` 标题行提取当日工作摘要
- 相对路径在 python3 下会触发路径重复 bug，始终用绝对路径调用脚本
- 飞书 Base 表字段名不可随意变更，API 调用字段名必须与 Base 表定义完全一致
