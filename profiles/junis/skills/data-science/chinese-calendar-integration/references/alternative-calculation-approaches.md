# Alternative Calculation Approaches

When `lunar-python` (6tail) is unavailable, use these fallback methods:

## Basic Lunar Date via `lunardate`

```python
import lunardate

lunar = lunardate.LunarDate.fromSolarDate(2026, 5, 30)
# LunarDate(2026, 4, 14, 0) — year=丙午, month=四月, day=十四
```

`lunardate` provides year/month/day as integers. You must convert to Chinese names manually:

```python
LUNAR_MONTHS = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊']
LUNAR_DAYS = [
    '初一','初二','初三','初四','初五','初六','初七','初八','初九','初十',
    '十一','十二','十三','十四','十五','十六','十七','十八','十九','二十',
    '廿一','廿二','廿三','廿四','廿五','廿六','廿七','廿八','廿九','三十'
]

month_name = LUNAR_MONTHS[lunar.month - 1] + '月'
day_name = LUNAR_DAYS[lunar.day - 1]
```

## Day Pillar (干支日柱) via Date-Diff Calibration

`lunardate` does NOT provide stem-branch (干支). Calculate using a known reference date.

**Step 1: Calibrate.** Find any known day pillar from a verified source (e.g., an existing 每日记录 entry).

```python
from datetime import date

TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# Given: 2026-05-29 = 癸卯日 (stem idx 9, branch idx 3)
known_date = date(2026, 5, 29)
known_stem_idx = TIANGAN.index('癸')  # 9
known_branch_idx = DIZHI.index('卯')  # 3

# Calculate the offset from reference date
ref = date(2000, 1, 1)
diff = (known_date - ref).days  # 9645

# Derive ref's stem/branch indices
ref_stem = (known_stem_idx - diff) % 10    # (9 - 9645) % 10 = 4 → 戊
ref_branch = (known_branch_idx - diff) % 12 # (3 - 9645) % 12 = 6 → 午
# 2000-01-01 = 戊午日
```

**Step 2: Calculate any target date.**

```python
def get_day_pillar(target_date, ref_stem, ref_branch, ref=date(2000,1,1)):
    diff = (target_date - ref).days
    stem = (ref_stem + diff) % 10
    branch = (ref_branch + diff) % 12
    return TIANGAN[stem] + DIZHI[branch]

# 2026-05-30 → 甲辰日
# 2026-05-31 → 乙巳日
```

## Month Pillar (月柱) — Approximate

Month stem-branch is tied to solar terms, not the calendar month. A reasonable approximation:

```python
def get_month_pillar(year, month_day_tuple):
    """Simple mapping for common months. Precise calculation requires solar term boundaries."""
    # 丙午年 → 癸巳月 for months between 立夏(May 6) and 芒种(Jun 6)
    # Year stem: 丙(2), branch: 午(6)
    # Month stem formula: (year_stem_idx * 2 + month_branch_idx) % 10
    pass  # Use lunar-python for accurate results
```

For accurate month pillars, prefer `lunar-python`'s `getMonthInGanZhi()`.

## Year Pillar (年柱)

```python
def get_year_pillar(year):
    t = (year - 4) % 10
    d = (year - 4) % 12
    return TIANGAN[t] + DIZHI[d]
# 2026 → 丙午年
```

## Solar Terms (节气) Approximation

```python
TERMS = {
    (1,5): '小寒', (1,20): '大寒', (2,4): '立春', (2,19): '雨水',
    (3,6): '惊蛰', (3,21): '春分', (4,5): '清明', (4,20): '谷雨',
    (5,6): '立夏', (5,21): '小满', (6,6): '芒种', (6,21): '夏至',
    (7,7): '小暑', (7,23): '大暑', (8,7): '立秋', (8,23): '处暑',
    (9,8): '白露', (9,23): '秋分', (10,8): '寒露', (10,23): '霜降',
    (11,7): '立冬', (11,22): '小雪', (12,7): '大雪', (12,22): '冬至',
}

def get_solar_term(month, day):
    last = ''
    for (m, d), name in sorted(TERMS.items()):
        if (month > m) or (month == m and day >= d):
            last = name
    return last  # Returns the last solar term that has passed
```

## Pitfalls

- **2000-01-01 ≠ 甲子日** in common reference books. Always calibrate against a known date. The calibration method above gives correct results (verified against 8 consecutive days of existing 每日记录 data).
- **Month pillar** requires knowing the exact solar term boundary (立春/惊蛰/清明/etc.), not the calendar month. For Feishu daily logs, a close approximation is acceptable, but official output should use `lunar-python`.
- **`lunardate`** is a lighter dependency than `lunar-python` and installs faster, but provides no stem-branch or 黄历 data.
