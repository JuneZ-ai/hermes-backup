# Feishu 多维表格 + 中国传统文化历法集成

> 场景：在飞书多维表格中自动填充农历、节气、干支、黄历宜忌等传统历法数据
> 库：`lunar-python`（6tail 出品，最全面的中国历法 Python 库）

## 安装

```bash
python3 -m pip install lunar-python
```

## 核心用法

```python
from lunar_python import Solar, Lunar

# 从公历获取农历
solar = Solar.fromYmd(2026, 5, 21)
lunar = solar.getLunar()

# 农历日期
lunar.getYearInChinese()   # "二〇二六"
lunar.getMonthInChinese()  # "四"
lunar.getDayInChinese()    # "初五"
f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"  # "四月初五"

# 节气
lunar.getJieQi()           # "小满"

# 干支（四柱）
lunar.getYearInGanZhi()    # "丙午"
lunar.getMonthInGanZhi()   # "癸巳"
lunar.getDayInGanZhi()     # "乙未"
lunar.getYearShengXiao()   # "马"

# 黄历宜忌
lunar.getDayYi()           # ["开光", "纳采", "裁衣", ...]
lunar.getDayJi()           # ["嫁娶", "栽种", "修造", ...]
lunar.getDayChong()        # "丑"
lunar.getDaySha()          # "西"
lunar.getDayJiShen()       # ["月德合", "守日", "天巫", ...]
# ⚠️ 注意：凶神是 getDayXiongSha()，不是 getDayXiongShen()（该名称不存在）
lunar.getDayXiongSha()     # ["五虚", "九空", ...]
```

### 完整字段拼接示例

```python
yi_str = "、".join(lunar.getDayYi())
ji_str = "、".join(lunar.getDayJi())
huangli = f"宜：{yi_str}\n忌：{ji_str}\n冲：{lunar.getDayChong()} 煞：{lunar.getDaySha()}"
ganzhi = f"{lunar.getYearInGanZhi()}年 {lunar.getMonthInGanZhi()}月 {lunar.getDayInGanZhi()}日"
lunar_str = f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
```

## Feishu Bitable 集成模式

将历法数据写入多维表格的典型字段结构：

| 字段名 | 类型 | 值来源 |
|--------|------|--------|
| 公历时间 | DateTime (type=5, primary) | `time.mktime(...) * 1000` |
| 农历 | Text | `lunar.getMonthInChinese() + "月" + lunar.getDayInChinese()` |
| 节气 | Text | `lunar.getJieQi()` |
| 干支 | Text | 年柱+月柱+日柱拼接 |
| 黄历宜忌 | Text | 宜/忌/冲/煞 拼接 |

## 已知节气数据（2026年参考）

| 日期 | 节气 |
|------|------|
| 5月5日 | 立夏 |
| **5月21日** | **小满** |
| 6月5日 | 芒种 |
| 6月21日 | 夏至 |

`lunar-python` 库可自动计算任意日期的节气，不需要硬编码查找表。

## 典型应用场景

- **每日记录**：公历+农历+节气+黄历作为日常记录的前置信息
- **读书/影评笔记**：收藏日期附带传统文化时间标记
- **任务管理**：标注当日宜忌与任务类型匹配
