---
name: feishu-ontology
description: "从飞书多维表格数据构建企业本体（Ontology）——将Bitable字段映射为对象/关系/动作三元组，受Palantir Ontology方法论启发。包含巡检脚本、自动化流水线和动作编排。"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [feishu, ontology, bitable, palantir, fde, data-twin, data-science]
    related_skills: [hermes-agent]
platforms: [linux, macos, wsl]
---

# 飞书 Ontology 映射

> 让AI看懂你的数据世界——从飞书多维表格到企业本体的完整方法论

## 触发词

「本体巡检」「构建本体」「ontoloty映射」「数据孪生」「FDE」

## 核心概念

受Palantir AIP平台Ontology方法论启发，将飞书Bitable数据建模为三层：

```
对象 (OBJECT)    ── 实体是什么         (客户、订单、商品)
关系 (RELATION)  ── 实体怎么连         (谁买了什么)
动作 (ACTION)    ── 实体能做什么       (投诉、退款、调拨)
```

## 工作流程

### 步骤1：拉取Bitable元数据

```python
# 获取 tenant_access_token
curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id": "$FEISHU_APP_ID", "app_secret": "$FEISHU_APP_SECRET"}'

# 获取表字段元数据
curl -s 'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields' \
  -H 'Authorization: Bearer {TOKEN}'
```

### 步骤2：分析字段角色

对于每个字段，判断其在本体中的角色：

| 角色 | 说明 | 示例字段 |
|------|------|---------|
| `object_key` | 对象唯一标识 | 标题、公历时间、ID |
| `action_description` | 发生了什么操作 | 操作内容、记录内容 |
| `action_record` | 认知处理动作 | 我的感悟 |
| `category` | 分类标签 | 领域、类型、分类 |
| `lifecycle_state` | 生命周期状态 | 状态 |
| `time_property` | 时间属性 | 时间、收藏日期 |
| `source_relation` | 指向外部的关系 | 来源链接 |
| `value_assessment` | 价值评分 | 评分 |

### 步骤3：发现跨表关系

常见的关系类型：

| 关系类型 | 匹配方式 | 说明 |
|---------|---------|------|
| 日期关联 | 时间戳精确到天 | 表A日期 = 表B日期 |
| 文本引用 | 关键词/标题匹配 | 表A内容中包含表B的标题 |
| 领域映射 | 分类/标签对应 | 表A的领域 → 表B的分类 |

**时间戳陷阱**：飞书Bitable中DateTime字段用毫秒、Calendar epoch用秒。比较时需统一单位：
```python
f_day = int(f_val) // 86400000   # 毫秒
t_day = int(t_val) // 86400000   # 毫秒
```

### 步骤4：定义动作流水线

每个动作包含：触发条件、输入对象、输出对象、自然语言描述

```json
{
  "id": "action_favorite_to_obsidian",
  "name": "素材自动入库",
  "trigger": "收藏素材状态变更时（已收藏→已读完→待重温）",
  "from_object": "favorite_item",
  "to_object": "daily_record",
  "nl_description": "收藏了一篇文章，读完标记后，自动生成Obsidian笔记"
}
```

### 步骤5：选项值清理（修复重复选项）

当巡检发现重复选项（如「✅已完成」vs「✅ 已完成」），按以下流程修复：

**Step 1 — 获取字段完整定义，确认重复选项的ID**
```bash
curl -s "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields" \
  -H "Authorization: Bearer {TOKEN}"
```

**Step 2 — 查询使用脏选项的记录**
```bash
curl -s "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=100" \
  -H "Authorization: Bearer {TOKEN}"
```
筛选字段值 == 脏选项名称的记录，获取其 `record_id`。

**Step 3 — 迁移记录到标准选项**
```bash
curl -s -X PUT "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{RECORD_ID}" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"fields": {"状态": "✅ 已完成"}}'
```
⚠️ SingleSelect字段传选项**名称字符串**，不是选项ID。

**Step 4 — 从字段定义中移除脏选项**
```bash
curl -s -X PUT "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{FIELD_ID}" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"field_name":"状态","type":3,"ui_type":"SingleSelect","property":{"options":[
    {"color":1,"name":"✅ 已完成"},
    {"color":0,"name":"⏳ 待跟进"},
    {"color":2,"name":"📋 计划中"}
  ]}}'
```
⚠️ 使用 **PUT** 方法（PATCH返回404），需提供完整字段定义：`field_name`、`type`、`ui_type`（如果原字段有）、`property.options`。

**Step 5 — 验证**
重新运行巡检脚本确认健康度提升。

### 步骤6：定期巡检（可选）

使用 `ontology_mapper.py` 脚本自动巡检：

```bash
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
python3 ~/.hermes/scripts/ontology_mapper.py
```

巡检内容包括：
- 字段一致性检查（字段是否被重命名或删除）
- 选项值重复检测（如「已完成」vs「✅已完成」）
- 跨表关系匹配数统计
- 本体健康度评分

## 参考

- 完整本体定义示例：`~/.hermes/skills/hermes-agent/references/异虎三表本体映射.json`
- 巡检脚本：`~/.hermes/scripts/ontology_mapper.py`
- 巡检快照目录：`~/hermes-vault/ontology/`
- 飞书Bitable API参考：`skill_view('hermes-agent', 'references/feishu-bitable-api.md')`

## 常见坑

1. **选项值重复**：手打时空格不一致会导致同一个概念被识别为两个实体（如「✅已完成」vs「✅ 已完成」）。严重降低本体健康度。
2. **时间戳单位不一致**：同一张表的不同字段可能用DateTime(毫秒)和Calendar(秒)。必须统一。
3. **Pure text选项混入**：部分选项有emoji前缀，部分没有，导致分类稀疏化。
4. **字段重命名**：Bitable字段名修改后，脚本中的硬编码field_name会失效。用field_id替代更可靠。
5. **跨表关系过度匹配**：日期匹配按天取整可能产生大量误匹配。对样本量大的场景建议加置信度过滤。
