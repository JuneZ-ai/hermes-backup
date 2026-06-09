# 财务台账 Base 三层架构

> 适用于：收支流水账 → 月度自动汇总 → 可视化看板

## 架构总览

```
┌──────────────────────────────┐
│  📊 L1: 费用明细（实时录入）   │  ← 用户每日记账的地方
│    字段：月份/类型/科目/项目/   │
│         金额/经手人/关联月份   │
└────────────┬─────────────────┘
             │ Link: 关联月份
             ▼
┌──────────────────────────────┐
│  📋 L2: 月度汇总（自动聚合）   │  ← 每月一条，数字自动跟
│    Lookup字段：总收入(SUM 收入)│
│    Lookup字段：总支出(SUM 支出)│
│    Formula字段：本月结余       │
└────────────┬─────────────────┘
             │ 同数据源
             ▼
┌──────────────────────────────┐
│  📈 L3: 费用收支看板（可视化） │  ← 6个仪表盘组件自动刷新
│    指标卡/折线图/饼图          │
└──────────────────────────────┘
```

## L1: 费用明细（录入层）

### 字段设计

| 字段 | 类型 | 说明 |
|------|------|------|
| 月份 | 日期(yyyy-MM-dd) | 建议存每月1日（如`2026-04-01`），方便按月份分组 |
| 类型 | 单选 | 收入 / 支出 / 结余 |
| 科目 | 单选 | 服务费 / 工资 / 费用 / 月终结余 |
| 项目 | 文本 | 具体费用项名称 |
| 金额 | 货币(CNY) | 保留两位小数 |
| 经手人 | 单选 | 谁操作的 |
| 关联月份 | **Link → 月度汇总** | 链接到汇总表对应月份行 |

### 关键操作：批量链接记录到汇总表

用 `+record-batch-update` 批量设置链接字段：

```json
{
  "record_id_list": ["rec_detail_1", "rec_detail_2", ...],
  "patch": {
    "关联月份": [{"id": "rec_summary_month_x"}]
  }
}
```

**注意**：Link字段的CellValue格式是 `[{"id": "rec_xxx"}]`（对象数组），不是纯字符串。

## L2: 月度汇总（自动计算层）

### 字段设计

| 字段 | 类型 | 说明 |
|------|------|------|
| 月份 | 文本 | 如 `2026-01`，每行对应一个自然月 |
| 总收入 | **Lookup(sum)** | 自动Sum关联的明细记录中类型=收入的金额 |
| 总支出 | **Lookup(sum)** | 自动Sum关联的明细记录中类型=支出的金额 |
| 本月结余 | **Formula** | `{总收入}-{总支出}` |

### Lookup字段配置（关键）

总收入 lookup JSON：
```json
{
  "type": "lookup",
  "name": "总收入",
  "from": "费用明细",
  "select": "金额",
  "aggregate": "sum",
  "where": {
    "logic": "and",
    "conditions": [
      ["关联月份", "intersects", {"type": "field_ref", "field": "月份"}],
      ["类型", "==", {"type": "constant", "value": ["收入"]}]
    ]
  }
}
```

| 参数 | 含义 |
|------|------|
| `from` | 源表名（精确匹配，不可猜） |
| `select` | 要聚合的字段 |
| `aggregate` | `"sum"`（小写snake_case！不是`SUM`） |
| `where[0]` | 关联月份 intersects 当前行的月份 → 确保只统计本月的记录 |
| `where[1]` | 类型 == ["收入"] → 只统计收入（select的constant用数组包选项名） |

总支出同理，将 `["收入"]` 改为 `["支出"]`。

### ⚠️ 坑点

- lookup字段的 `aggregate` 值必须是小写snake_case：`"sum"` / `"average"` / `"counta"` / `"max"` / `"min"`
- `"count"` 不存在，用 `"counta"`
- select选项的constant value用数组 `["收入"]`，不是纯字符串 `"收入"`
- 创建 `lookup` 和 `formula` 字段时，必须加 `--i-have-read-guide` 标志
- 删除被formula引用的number字段前，**必须先删formula字段**（依赖顺序）
- `+field-delete` 不支持用字段名删除；必须先用 `+field-list` 拿到 `field_id`

## L3: 仪表盘组件创建套路

### 创建顺序（必须串行）

1. 指标卡（统计数字）
2. 折线图（趋势）
3. 饼图（占比）

### 组件data_config模板

**收入指标卡**（statistics）：
```json
{
  "table_name": "费用明细",
  "series": [{"field_name": "金额", "rollup": "SUM"}],
  "filter": {
    "conjunction": "and",
    "conditions": [{"field_name": "类型", "operator": "is", "value": "收入"}]
  }
}
```

**月度收入趋势**（line）：
```json
{
  "table_name": "费用明细",
  "series": [{"field_name": "金额", "rollup": "SUM"}],
  "group_by": [{"field_name": "月份", "mode": "integrated", "sort": {"type": "group", "order": "asc"}}],
  "filter": {
    "conjunction": "and",
    "conditions": [{"field_name": "类型", "operator": "is", "value": "收入"}]
  }
}
```

**费用科目占比**（pie）：
```json
{
  "table_name": "费用明细",
  "series": [{"field_name": "金额", "rollup": "SUM"}],
  "group_by": [{"field_name": "科目", "mode": "integrated"}],
  "filter": {
    "conjunction": "and",
    "conditions": [{"field_name": "类型", "operator": "is", "value": "支出"}]
  }
}
```

### 组件创建的CLI命令

```bash
lark-cli base +dashboard-block-create \
  --base-token <token> \
  --dashboard-id <blk_xxx> \
  --name "💰 总收入" \
  --type statistics \
  --data-config '<JSON>'
```

### 布局优化

所有组件创建完后调用 `+dashboard-arrange` 自动排布：

```bash
lark-cli base +dashboard-arrange \
  --base-token <token> \
  --dashboard-id <blk_xxx>
```

### ⚠️ 坑点

- `table_name` 是表名（如"费用明细"），**不是表ID**（如`tbl_xxx`）
- `group_by` 最多2个
- 组件必须串行创建，不能并发
- dashboard-block-create不支持 `--yes`；确认参数中有 `--yes` 时会报错 `unknown flag`
- `--data-config` 的JSON中必须是**表名**，不能用表ID；字段也必须是精确的**字段名**，不是字段ID
- filter的 `value` 类型：单选用字符串，多选用字符串数组，数字用number，日期用Unix毫秒时间戳
- 仪表盘创建后，可以在Base UI中拖拽调整布局，`+dashboard-arrange` 只是初始排布

## 完整交付清单

此架构适用于以下场景的交付：

1. ✅ 已有Excel台账（收入/支出并列结构）→ 解析变更为单表
2. ✅ 用户需要日常录入 + 自动汇总 + 可视化复盘
3. ✅ 数据量5-200条/月，单人/小团队
4. ✅ 需要在飞书内完成，不依赖外部系统

**交付物**：1个Base，含3张表（明细+汇总+预填月份）+ 1个仪表盘（6组件）。
