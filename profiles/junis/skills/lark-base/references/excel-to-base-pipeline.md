# Excel→Base 多维表格导入管线

> 从原始 Excel/CSV 到完整的飞书多维表格（含关联表、自动汇总、仪表盘）的全流程技术参考。

## 适用场景

- 用户丢一个 Excel 文件过来，要求转成多维表格
- Excel 结构非标准（嵌套分类标题、左右分栏、合并行）
- 需要将报表数据转化为可长期维护的结构化+自动化系统

## 标准工作流

```
① 解析Excel结构 → ② 设计表结构 → ③ 创建Base → ④ 建表+字段 → ⑤ 转化数据 → ⑥ 灌录 → ⑦ 建关联+自动计算 → ⑧ 加仪表盘
```

## ① 解析 Excel 结构

先用 pandas 读取全貌，重点看：

```bash
python3 -c "
import pandas as pd
path = '文件路径.xlsx'
xls = pd.ExcelFile(path)
print('Sheet名称:', xls.sheet_names)
for s in xls.sheet_names:
    df = pd.read_excel(path, sheet_name=s, header=None)
    print(f'=== {s} ({df.shape}) ===')
    print(df.head(15).to_string())
"
```

### 复杂 Excel 的常见坑型

| 坑型 | 特征 | 应对策略 |
|------|------|---------|
| **嵌套分类标题** | 行中包含"收入"/"支出"等分类标题，不是纯数据 | 逐行解析，区分标题行与数据行 |
| **左右分栏** | 收入列在左半，支出列在右半（同行的两个半区是并列关系） | 用列索引分区处理，`c0/c1=左半`，`c2/c3=右半` |
| **合并行/汇总行** | 最后一行是求和汇总 | 识别最后一行或检测两端都有金额且值大的行，跳过 |
| **Excel日期序号** | 第一行显示为数字，如46023=2026-01-01 | 用 pandas 默认解析，或忽略序号行 |
| **缺少列** | 不同sheet列数不同（如经手人列在某个sheet缺失） | `len(row) > n` 兜底检查 |

### 逐行解析模板

```python
path = '文件路径.xlsx'
all_records = []

for sheet, month in month_map.items():
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    rows = [[None if pd.isna(v) else v for v in r] for r in df.values.tolist()]
    
    for i in range(数据起始行, len(rows)):
        r = rows[i]
        c0 = str(r[0]).strip("' ") if r[0] is not None else ''
        c1 = r[1] if r[1] is not None else None
        # ... 按业务逻辑解析
        
        # 跳过分类标题
        if c0 in ('收入','支出','结余'): continue
        # 跳过汇总行（最后一行+两端金额）
        if i == len(rows) - 1 and c1 and c3: continue
        # 跳过空行
        if not c0 and not c2: continue
```

## ②-③ 创建 Base+表+字段

### 创建 Base

```bash
lark-cli base +base-create --name "Base名称"
```

**注意事项：**
- Base 创建后记录 `base_token`（形如 `B8CKbR4B3aIxAYs...`）
- 默认包含一个空"数据表"，后续可删除但必须先建新表
- **权限**：Base 默认由 bot 身份创建，用户无法直接访问。必须手动授权：
  ```bash
  lark-cli drive permission.members create \
    --params '{"token":"<base_token>","type":"bitable"}' \
    --data '{"member_type":"openid","member_id":"<用户open_id>","perm":"full_access","type":"user"}' \
    --yes
  ```

### 建表+字段（一次到位）

推荐一次性建表+字段，减少 API 调用：

```bash
lark-cli base +table-create \
  --base-token <token> \
  --name "表名" \
  --fields '[
    {"name":"字段名","type":"text"},
    {"name":"金额","type":"number","style":{"type":"currency","precision":2,"currency_code":"CNY"}},
    {"name":"类型","type":"select","multiple":false,"options":[{"name":"选项A","hue":"Green","lightness":"Light"},{"name":"选项B","hue":"Red","lightness":"Light"}]},
    {"name":"日期","type":"datetime","style":{"format":"yyyy-MM-dd"}},
    {"name":"公式","type":"formula","expression":"{字段A}-{字段B}"}
  ]' \
  --view '[{"name":"默认视图","type":"grid"}]'
```

**注意：** 创建 `formula` 和 `lookup` 类型字段需 `--i-have-read-guide` 标志。

### 字段类型速查

| 用途 | type | JSON 关键配置 |
|------|------|-------------|
| 文本 | `text` | 无特殊配置 |
| 货币 | `number` | `style.type=currency`, `style.currency_code=CNY/USD`, `style.precision=2` |
| 数字（普通） | `number` | `style.type=plain`, `style.precision=n` |
| 日期 | `datetime` | `style.format=yyyy-MM-dd`（支持: yyyy-MM-dd, yyyy/MM/dd等） |
| 单选 | `select` | `multiple=false`, `options=[{name,hue,lightness}]` |
| 关联 | `link` | `link_table="目标表名"`（支持 `bidirectional` 双向关联） |
| 公式 | `formula` | `expression="{字段A}-{字段B}"`（需要 `--i-have-read-guide`） |
| 查找引用 | `lookup` | `from, select, aggregate, where`（需要 `--i-have-read-guide`） |

### 字段选项颜色参考

| hue | 适用场景 |
|-----|---------|
| `Green` | 正面（收入/成功/完成） |
| `Red/Carmine` | 负面（支出/费用/错误） |
| `Orange` | 中位/警告 |
| `Blue` | 中性/信息 |
| `Gray` | 基础/清淡 |
| `Yellow` | 活跃/高亮 |

`lightness` 可选：`Lighter`, `Light`, `Standard`, `Dark`, `Darker`

## ④ 数据转化+灌录

### CellValue 格式要点

| 字段类型 | CellValue 格式 |
|---------|---------------|
| text | `"字符串"` |
| number | `数字`（不要带单位或千分位） |
| select（单选） | `"选项名"`（或 `["选项名"]` — 两种都行） |
| datetime | `"2026-01-01 00:00:00"` |
| link | `["目标record_id"]` |
| 空值 | `null` |

### 批量创建命令

```bash
# JSON 格式：{ fields: ["字段A","字段B"], rows: [["值1","值2"]] }
lark-cli base +record-batch-create \
  --base-token <token> \
  --table-id <table_id> \
  --json @<相对路径>.json
```

**坑点**：`--json @` 只接受**相对路径**（当前目录下的文件），绝对路径报错。

### 批量更新（batched update — 同值应用到多条记录）

```bash
# JSON 格式：{ record_id_list: ["rec_id1","rec_id2"], patch: { "字段名": 值 } }
lark-cli base +record-batch-update \
  --base-token <token> \
  --table-id <table_id> \
  --json '{"record_id_list":["rec_xxx"],"patch":{"关联字段":["目标record_id"]}}'
```

**使用场景**：批量设置关联字段（同一月所有记录→同一条月度汇总记录）

## ⑤ 跨表自动汇总（link + lookup + formula）

核心架构：**明细表（可写）→ 关联 → 汇总表（只读自动计算）**

### 步骤

1. **明细表加 link 字段**指向汇总表

```bash
lark-cli base +field-create --base-token <token> --table-id <明细表ID> \
  --json '{"name":"关联月份","type":"link","link_table":"汇总表名"}'
```

2. **汇总表预填维度数据**（如月份行）

3. **明细记录关联到汇总维度**（用 batch-update）

4. **汇总表创建 lookup 字段**聚合明细数据

```bash
lark-cli base +field-create --base-token <token> --table-id <汇总表ID> \
  --json '{"type":"lookup","name":"总收入","from":"明细表名","select":"金额","aggregate":"sum","where":{"logic":"and","conditions":[["关联月份","intersects",{"type":"field_ref","field":"月份"}],["类型","==",{"type":"constant","value":["收入"]}]]}}' \
  --i-have-read-guide
```

5. **汇总表创建 formula 字段**做差值计算

```bash
lark-cli base +field-create --base-token <token> --table-id <汇总表ID> \
  --json '{"type":"formula","name":"本月结余","expression":"{总收入}-{总支出}"}' \
  --i-have-read-guide
```

### lookup 字段四要素

| 要素 | 说明 | 示例 |
|------|------|------|
| `from` | 源表名（精确匹配） | `"费用明细"` |
| `select` | 源字段名 | `"金额"` |
| `aggregate` | 聚合方式 | `sum` / `counta` / `average` / `max` / `min` / `unique` |
| `where` | 筛选条件（必需！） | `{"logic":"and","conditions":[[字段,操作符,值]]}` |

### where 条件常见模式

| 场景 | 条件写法 |
|------|---------|
| 通过 link 字段匹配 | `["关联字段","intersects",{"type":"field_ref","field":"目标字段"}]` |
| 固定值筛选 | `["类型","==",{"type":"constant","value":["收入"]}]` |
| 组合条件 | `logic:"and"` + 多个条件 |

**聚合值必须用 snake_case lowercase**：`sum` 不是 `SUM`，`counta` 不是 `count`。

## ⑥ 仪表盘（Dashboard）搭建

### 创建仪表盘

```bash
lark-cli base +dashboard-create --base-token <token> --name "仪表盘名称"
```

### 组件类型选择

| 用途 | type | data_config 模式 |
|------|------|-----------------|
| 单一指标 | `statistics` | `{table_name, series:[{field_name:"金额",rollup:"SUM"}], filter:{...}}` |
| 趋势/时序 | `line` | `{table_name, series:[...], group_by:[{field_name:"月份",mode:"integrated",sort:{type:"group",order:"asc"}}], filter:{...}}` |
| 分类对比 | `column`/`bar` | `{table_name, series:[...], group_by:[{field_name:"分类",mode:"integrated"}], filter:{...}}` |
| 占比分布 | `pie` | `{table_name, series:[...], group_by:[{field_name:"科目",mode:"integrated"}], filter:{...}}` |
| 富文本 | `text` | `{text:"# 标题\\n内容"}`（无 table_name/series） |

### data_config 结构速查

```json
{
  "table_name": "表名",                    // 必填（chart类）
  "series": [                              // 必填（与count_all二选一）
    { "field_name": "金额", "rollup": "SUM" }
  ],
  "group_by": [                            // 选填（需分组时）
    { "field_name": "月份", "mode": "integrated", "sort": {"type": "group", "order": "asc"} }
  ],
  "filter": {                              // 选填（需筛选时）
    "conjunction": "and",
    "conditions": [
      { "field_name": "类型", "operator": "is", "value": "收入" }
    ]
  }
}
```

### filter 条件速查

| 字段类型 | operator | value 格式 |
|---------|----------|-----------|
| text | is, isNot, contains | `"字符串"` |
| number | is, isGreater, isLess, etc. | `数字` |
| select（单选） | is, isNot | `"选项名"` |
| datetime | is, isGreater, etc. | `时间戳(毫秒)` |

### 创建组件

```bash
lark-cli base +dashboard-block-create \
  --base-token <token> \
  --dashboard-id <dashboard_id> \
  --name "组件名" \
  --type line \
  --data-config '{...}'
```

**重要规则：**
- 组件创建**必须串行执行**，不能并发
- `type` 创建后不可修改（要改只能删除重建）
- `data-config` 的 `@` 文件同样只接受**相对路径**

### 排版优化

```bash
lark-cli base +dashboard-arrange \
  --base-token <token> \
  --dashboard-id <dashboard_id>
```

自动智能重排所有组件布局。

## 常见完整管线示例

### 费用台账管线（实战验证）

```
输入：5sheet嵌套Excel（收支左右分栏）
→ 解析：40条记录，6字段（月份/类型/科目/项目/金额/经手人）
→ 建表：费用明细表 + 月度汇总表（link关联）
→ 自动计算：lookup SUM(收入) + lookup SUM(支出) + formula(结余=收入-支出)
→ 仪表盘：总收入/总支出指标卡 + 月度收入/支出折线图 + 费用占比饼图 + 结余趋势线
```

### 产品知识库管线（实战验证）

```
输入：产品系列文档5档 + iPhone型号表.xlsx + 报价表.xlsx
→ 建表：产品系列表(5记录) + 设备型号表(24记录) + 产品报价表(5记录)
→ 关联：按需求跨表link（编号/品类匹配）
→ 仪表盘：（按需搭建）
```
