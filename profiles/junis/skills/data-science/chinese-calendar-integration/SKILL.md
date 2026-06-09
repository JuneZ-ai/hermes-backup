---
name: chinese-calendar-integration
description: Integrate traditional Chinese calendar data (lunar dates, solar terms, stem-branch almanac, huangli/auspicious calendar) into productivity tools, databases, and flysheets. Covers the lunar-python library API, Feishu Bitable integration patterns, and data-engineering workflows for daily log systems.
trigger_keywords:
  - 农历
  - 节气
  - 黄历
  - 天干地支
  - 中国传统历法
  - 公历农历转换
  - lunar-python
  - Chinese calendar
  - 宜忌
  - 第二大脑
  - 每日记录
---

# Chinese Calendar Integration (中华历法数据集成)

Integrate traditional Chinese calendar data into digital tools. Uses the `lunar-python` (6tail) library, which provides comprehensive Chinese calendar calculations including lunar dates, solar terms, stem-branch calendar, and Chinese almanac (黄历).

## Installation

```bash
pip install lunar-python
```

Library: **lunar-python** (by 6tail) — pure Python, no external dependencies.
Documentation: https://github.com/6tail/lunar-python

## Core API Reference

### Basic Lunar Date

```python
from lunar_python import Solar, Lunar

# Solar → Lunar
solar = Solar.fromYmd(2026, 5, 21)
lunar = solar.getLunar()

# Read component values
lunar.getYearInChinese()    # "二〇二六"
lunar.getMonthInChinese()   # "四"
lunar.getDayInChinese()     # "初五"
```

### Solar Terms (节气)

```python
lunar.getJieQi()  # Returns current solar term, e.g. "小满"
```

### Stem-Branch Calendar (干支历)

```python
lunar.getYearInGanZhi()     # "丙午"
lunar.getMonthInGanZhi()    # "癸巳"
lunar.getDayInGanZhi()      # "乙未"
lunar.getYearShengXiao()    # "马" (zodiac animal)
```

### Chinese Almanac (黄历)

```python
# 宜/忌 (what to do/avoid)
lunar.getDayYi()    # ['开光', '纳采', ...]
lunar.getDayJi()    # ['嫁娶', '栽种', ...]

# 冲煞 (conflict direction)
lunar.getDayChong()  # "丑"
lunar.getDaySha()    # "西"

# 吉神/凶神
lunar.getDayJiShen()    # auspicious deities
lunar.getDayXiongSha()  # inauspicious forces
```

## Feishu Bitable Integration

### Field Structure for Daily Log Tables

| Field Name | Type | Note |
|---|---|---|
| **公历时间** | DateTime (type 5) | Primary/index field, first column. User prefers this as column 1. |
| **农历** | Text (type 1) | Month-day in Chinese, e.g. "四月初五" |
| **节气** | Text (type 1) | Solar term, e.g. "小满" |
| **干支** | Text (type 1) | Year-Month-Day stem-branch, e.g. "丙午年 癸巳月 乙未日" |
| **黄历宜忌** | Text (type 1) | Multi-line: 宜：...\n忌：...\n冲：X 煞：Y |
| **记录内容** | Text (type 1) | What the user experienced/learned |
| **类型** | SingleSelect (type 3) | Options: 读书/工作/会议/思考/生活/见闻 |

### Bitable API Pitfalls

- **DateTime timestamps must be in MILLISECONDS** (epoch * 1000). Passing seconds gives Jan 1970 dates.
- **PATCH** to rename a table, not PUT (returns 404 if wrong method).
- **Creating tables**: wrap in `{"table": {...}}`. If providing `default_view_name`, must also provide `fields`.
- **Primary field** (first field) supports: Text (1), Number (2), DateTime (5), Phone (13), URL (15), Formula (20), Location (22).
- **Renaming fields**: Must include `type` parameter in request body.
- **Delete empty template rows**: New bitable tables often come with 10 empty rows from the default template. Check `fields == {}` and delete them.

### Sample: Create Table with Fields

```python
requests.post(
    f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={
        "table": {
            "name": "每日记录",
            "default_view_name": "日历视图",
            "fields": [
                {"field_name": "公历时间", "type": 5, "ui_type": "DateTime",
                 "property": {"date_formatter": "yyyy/MM/dd"}},
                {"field_name": "农历", "type": 1},
                {"field_name": "节气", "type": 1},
                {"field_name": "干支", "type": 1},
                {"field_name": "黄历宜忌", "type": 1},
                {"field_name": "记录内容", "type": 1},
                {"field_name": "类型", "type": 3, "ui_type": "SingleSelect",
                 "property": {"options": [{"name": "📚 读书", "color": 0}, ...]}},
            ]
        }
    }
)
```

### Sample: Write Daily Record

```python
# Convert lunar date to Chinese strings
lunar_str = f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
ganzhi = f"{lunar.getYearInGanZhi()}年 {lunar.getMonthInGanZhi()}月 {lunar.getDayInGanZhi()}日"
yi_str = "、".join(lunar.getDayYi())
ji_str = "、".join(lunar.getDayJi())
huangli = f"宜：{yi_str}\n忌：{ji_str}\n冲：{lunar.getDayChong()} 煞：{lunar.getDaySha()}"

# Milliseconds!
today_ms = int(datetime.strptime("2026-05-21", "%Y-%m-%d").timestamp()) * 1000

requests.post(url, json={"fields": {
    "公历时间": today_ms,
    "农历": lunar_str,
    "节气": solar_term,
    "干支": ganzhi,
    "黄历宜忌": huangli,
    "记录内容": "...",
    "类型": "💼 工作",
}})
```

## User Preferences
- **First column** of any log table must be the date (公历时间), as DateTime primary field.
- **Chinese calendar fields** should always include: 农历, 节气, 黄历宜忌 — these are core to the "第二大脑" daily log system.
- Feishu Bitable + Chinese calendar is the preferred daily recording tool over plain text files.

## Related Skills
- `obsidian-ingestion-pipeline` — for knowledge-base feeding workflows (complementary: this skill handles the data source, that skill handles the ingestion)
- `knowledge-synthesis` — for synthesizing insights from research into skills (complementary: this skill handles calendar metadata, that skill handles analytical depth)

## Alternative Calculation Methods
See [references/alternative-calculation-approaches.md](references/alternative-calculation-approaches.md) for fallback techniques when `lunar-python` is unavailable:
- Basic lunar date via `lunardate` library
- Day pillar (干支日柱) calculation using date-diff calibration against a known reference date
- Solar term approximation
