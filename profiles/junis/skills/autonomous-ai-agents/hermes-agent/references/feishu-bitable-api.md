# Feishu Bitable (多维表格) API 操作指南

> 场景：通过飞书 Open API 创建/读写多维表格
> 凭证来源：`~/.hermes/.env` → `FEISHU_APP_ID` + `FEISHU_APP_SECRET`

## 鉴权

```python
import requests

resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": app_id, "app_secret": app_secret},
    timeout=10
)
token = resp.json()["tenant_access_token"]  # 有效期 2小时
headers = {"Authorization": f"Bearer {token}"}
```

## 已验证的 API 端点

### 创建多维表格（获取 app_token）

```python
POST /open-apis/bitable/v1/apps
{"name": "表格名称"}

# 返回:
{
  "code": 0,
  "data": {
    "app": {
      "app_token": "Cuq4bbKjsalf9DsMYZbcSz7gnkd",
      "default_table_id": "tblk8yltq9gjUjTH",
      "url": "https://my.feishu.cn/base/{app_token}"
    }
  }
}
```

**注意：没有"列出所有表格"的 API 端点**。你需要先知道 app_token 才能操作表格。要么主动创建，要么从飞书文档 URL 中提取。

### 在一个 Base 中创建第二个数据表

```python
# 最简：仅名称，会创建只有索引字段的空表
POST /open-apis/bitable/v1/apps/{app_token}/tables
{"table": {"name": "新表名称"}}

# 带字段和默认视图 — 注意：default_view_name 和 fields 必须同时提供或同时省略
POST /open-apis/bitable/v1/apps/{app_token}/tables
{
  "table": {
    "name": "每日记录",
    "default_view_name": "日历视图",
    "fields": [
      {"field_name": "公历时间", "type": 5, "ui_type": "DateTime",
       "property": {"date_formatter": "yyyy/MM/dd", "auto_fill": false}},
      {"field_name": "标题", "type": 1, "ui_type": "Text"}
    ]
  }
}
```

**关键规则：** `default_view_name` 和 `fields` 是**绑定的**——提供一个就必须提供另一个。同时省略则创建空表。

**DateTime 可以作为主字段（索引字段，type=5）**，支持的主字段类型：1(文本)、2(数字)、5(日期)、13(电话号码)、15(超链接)、20(公式)、22(地理位置)。

### 重命名数据表

```python
PATCH /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}
{"name": "新名称"}
```

### 列出字段

```python
GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields
```

返回默认字段结构。新建表格的默认字段：

| field_name | type | type_id | 说明 |
|-----------|------|---------|------|
| 文本 | 1 (Text) | fld... | 主字段 (is_primary=true) |
| 单选 | 3 (SingleSelect) | fld... | 空选项列表 |
| 日期 | 5 (DateTime) | fld... | 格式 yyyy/MM/dd |
| 附件 | 17 (Attachment) | fld... | - |

### 字段管理

#### 重命名字段

```python
PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}
{
  "field_name": "新名称",
  "type": 1   # ⚠️ 必须传入 type，即使只是重命名！
}
```

**关键坑：** `type` 参数是**必需的**，即使只是改名称也必须传入。不传则返回 `code: 99992402` (`type is required`)。

#### 添加新字段

```python
POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields
{
  "field_name": "状态",
  "type": 3,   # 1=Text, 3=SingleSelect, 5=DateTime, 17=Attachment
  "property": {
    "options": [
      {"name": "✅ 已完成", "color": 0},
      {"name": "⏳ 待跟进", "color": 1},
      {"name": "📋 计划中", "color": 2}
    ]
  }
}
```

### 写入记录

```python
POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records
{
  "fields": {
    "文本": "内容",
    "日期": 1779361333000  # ⚠️ 毫秒级时间戳（epoch * 1000），不是秒！
  }
}
```

**关键坑 #1：** 字段名必须**完全匹配**已有字段名。不存在字段时返回 `code: 1254045` (`FieldNameNotFound`)。

**关键坑 #2（❌ 已踩过）：** DateTime 类型字段接收的是 **毫秒级** 时间戳（epoch 秒数 × 1000），不是秒。传入秒级时间戳会显示为 **1970 年**。

### 删除记录

```python
DELETE /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}
```

**适用场景：** 新建表格时默认模板会生成 10 条空记录，需要清理。识别空记录的依据是 `fields` 字典为空（`{}`）。

### 读取记录

```python
GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=10
```

返回 `items` 数组，每项包含 `record_id` 和 `fields` 字典。

### 列出云盘文件

```python
GET /open-apis/drive/v1/files?page_size=50&order_by=EditedTime
```

**详细说明及已知限制 → `references/feishu-drive-api.md`**（位于本 skill 下）。Drive API 仅返回应用 My Space 中的文件，用户个人云盘文档不可见。

## ⚠️ 关键坑：PUT 字段选项会重建内部选项 ID

> 已踩过，代价 13 条记录丢失后手动恢复

**问题：** `PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}` 会**完全替换**该字段的选项列表，且每个选项会获得**新的内部 ID**。现有记录存储的是旧 ID，PUT 后记录的单选字段值会全部变空白。

**错误示范：**
```python
# ❌ 直接 PUT 字段去重——导致所有记录的值丢失
result = api.put(f"fields/{field_id}", {
    "field_name": "状态",
    "type": 3,
    "property": {"options": [ {"name": "✅ 已完成"}, {"name": "⏳ 待跟进"} ]}
})
# 之前使用 "config_yaml" 选项的记录全部变成空白
```

**正确工作流：**

```python
# ✅ Step 1: 先迁移记录（用字段 NAME，不是 ID）
for record_id in affected_records:
    api.put(f"records/{record_id}", {"fields": {"状态": "✅ 已完成"}})

# ✅ Step 2: 再 PUT 字段移除旧选项
api.put(f"fields/{field_id}", {
    "field_name": "状态",
    "type": 3,
    "property": {
        "options": [
            {"name": "✅ 已完成", "color": 1},  # 这个选项名和原来一样，但 ID 变了
            {"name": "⏳ 待跟进", "color": 0},
        ]
    }
})
```

**发现链接已断开后的补救：** 如果已经 PUT 导致记录值为空，只能根据**其他字段的内容（标题、评分、感悟等）反向推断**并重新赋值。没有自动恢复的 API 方法。

### 完整选项清理工作流

这个流程可重复使用，用于去重、美化、统一 SingleSelect 选项：

```python
# 1. 扫描 — 获取字段定义，找出重复/脏选项
fields = api.get(f"tables/{table_id}/fields").items
for f in fields:
    if f.type == 3:  # SingleSelect
        names = [o.name for o in f.property.options]
        # 检查空格差异的重复
        normalized = {}
        for n in names:
            key = n.replace(" ", "")
            if key in normalized:
                print(f"重复: '{n}' vs '{normalized[key]}'")
            normalized[key] = n

# 2. 记录迁移 — 找出使用脏选项的记录，按选项 NAME 写入新值
records = api.get(f"tables/{table_id}/records").items
affected = [r for r in records if r.fields.get(field_name) == "脏选项名"]
for r in affected:
    api.put(f"records/{r.record_id}", {"fields": {field_name: "标准选项名"}})

# 3. PUT 字段 — 用干净的选项列表替换
api.put(f"fields/{field_id}", {
    "field_name": name,
    "type": 3,
    "property": {"options": clean_options}
})

# 4. 验证 — 重新拉取字段和记录确认
updated = api.get(f"tables/{table_id}/fields")
assert "脏选项名" not in [o.name for o in updated.items[0].property.options]
```

**关键原则：** 先用 NAME 迁移记录，再 PUT 字段。顺序不能颠倒。

## 本体映射 (Ontology) 方法

除了 CRUD 操作，飞书多维表格可以用来构建**企业本体（Ontology）**——把表、字段、记录映射为 对象/关系/动作 三元组，让 AI 能看懂数据结构。

### 核心概念

```
对象 (Object)     — 实体是什么（搭建日志 / 每日记录 / 收藏素材）
关系 (Relationship) — 实体怎么连（日期关联 / 引用关联 / 领域关联）
动作 (Action)     — 实体能做什么（自动入库 / 高分预警 / 日结汇总）
```

### 映射步骤

1. **识别对象表** — 每张表就是一个对象类型，主字段是对象标识
2. **字段角色分类** — 每个字段属于：
   - `object_key` — 对象唯一标识
   - `action_description` — 描述实体做了什么
   - `category` / `activity_category` — 分类标签
   - `lifecycle_state` — 状态流转
   - `time_property` — 时间属性
   - `source_relation` — 外部连接关系
   - `value_assessment` — 价值评估
3. **发现跨表关系** — 日期对齐、文本引用、分类映射
4. **注册动作流水线** — 啥条件触发啥操作

### 本体健康度评分

定期巡检检查：
- 字段一致性（期望的字段名是否还在）
- 选项值质量（重复、冗余、格式不统一）
- 跨表关系匹配数

健康度 < 80 需要干预。

### 现有工具

- **巡检脚本：** `~/.hermes/scripts/ontology_mapper.py` — 每天 23:00 由燕青自动执行
- **本体定义：** `~/.hermes/skills/hermes-agent/references/异虎三表本体映射.json` — 完整映射 JSON
- **输出目录：** `~/hermes-vault/ontology/ontology_snapshot_*.json` — 每日快照

巡检脚本可独立执行：`python3 ~/.hermes/scripts/ontology_mapper.py`

## 权限模型

飞书 Open API 有两种权限身份：

| 类型 | 说明 | 典型场景 |
|------|------|---------|
| **应用身份** (tenant_access_token) | 机器人自主操作 | 数据写入、自动化流程 |
| **用户身份** (user_access_token) | 模拟用户操作 | 需要用户上下文的操作 |

Bitable 读写用**应用身份**即可，不需要用户身份。

## 常见错误

| code | msg | 原因 |
|------|-----|------|
| 0 | success | 正常 |
| 1254045 | FieldNameNotFound | 写入的字段名不存在于表格中 |
| 99992402 | type is required | 更新字段时必须传 `type` 参数 |
| 99992402 | field validation failed | 参数校验失败，检查请求体各字段 |
| 99991672 | Access denied | 未开通对应权限（后台→权限管理→勾选后→**发布版本**） |
| 1254606 | DataNotChange | PUT 字段时新旧数据一样，不需要更新 |

## 权限开通流程（已验证的四阶段扩展法）

**推荐顺序：** 一次只开一两个权限，**测试通过后再开下一批**，避免一次开太多不知道哪个出问题。

| 阶段 | 权限 | 测试方法 |
|------|------|---------|
| 1️⃣ 基础 | `im:message`（收发消息） | 安装即验证 |
| 2️⃣ 多维表格 | `bitable:app:*` | 建表→写记录→读记录 |
| 3️⃣ 日历 | `calendar:calendar:readonly` + `calendar:calendar` | 列日程→创建日程→删除日程 |
| 4️⃣ 任务+云文档 | `task:task:*` + `drive:drive:*` | 列任务→列文件 |

**操作步骤：**
1. 开发者后台 → **权限管理** → 找到对应分类 → 勾选所需权限
2. 左侧 → **版本管理与发布** → 创建版本 → 发布
3. 等待 1-2 分钟生效，然后测试

**最小权限原则：** 用多少开多少。先只开通当前阶段要测的权限，测试通过后再逐步扩展。

## 模板设计模式（已验证的多表架构）

在同一个 Base 中设计多个数据表，每个表有独立的用途和字段结构。

### 模式1：搭建日志（系统追踪）

追踪系统搭建/配置过程的每一步操作。

| 字段 | 类型 | 说明 |
|------|------|------|
| ⭐ 操作内容 | Text (type=1) | 主字段，描述做了什么 |
| 领域 | SingleSelect (type=3) | 飞书权限开通 / API打通验证 / 知识库基建 / 架构决策 / 工具配置 |
| 时间 | DateTime (type=5) | 操作时间（毫秒时间戳） |
| 状态 | SingleSelect (type=3) | ✅ 已完成 / ⏳ 待跟进 / 📋 计划中 |
| 备注 | Text (type=1) | 补充说明 |

### 模式2：每日记录（带传统文化历法）

以**公历日期为第一列（主字段）**，附农历、节气、黄历。

> **用户偏好：** 表格第一列必须是公历时间

| 字段 | 类型 | 说明 |
|------|------|------|
| ⭐ **公历时间** | **DateTime (type=5, primary)** | **第一列，主字段** |
| 农历 | Text | 从 `lunar-python` 计算 |
| 节气 | Text | 当前节气 |
| 干支 | Text | 年柱+月柱+日柱 |
| 黄历宜忌 | Text | 宜/忌/冲/煞 |
| 记录内容 | Text | 今天做了什么 |
| 类型 | SingleSelect | 📚 读书 / 💼 工作 / 🤝 会议 / 💡 思考 / 🏠 生活 / 🌐 见闻 / 💻 工具 |

### 模式3：收藏随想录（通用收藏库）

通用收藏+笔记模板。

| 字段 | 类型 | 说明 |
|------|------|------|
| ⭐ **标题** | **Text (type=1, primary)** | 文章/书/电影名 |
| 来源链接 | Text | URL |
| 我的感悟 | Text | 个人思考 |
| 金句摘录 | Text | 原文金句 |
| 来源类型 | SingleSelect | 📱 微信文章 / 🌐 网页 / 📚 书籍 / 🎧 播客 / 🎬 影视 / 📰 新闻 / 🎵 歌曲 / 📨 邮件/通讯 / 💬 聊天记录 / 📄 PDF/文档 / 🗂 其他 |
| 分类 | SingleSelect | 💻 技术/AI / 🏢 商业/管理 / 🧘 个人成长 / 🎯 认知/思维 / 📖 人文/社科 / 🔮 传统文化 / 📰 资讯/见闻 / 🎨 兴趣爱好 / 🗂 其他 |
| 收藏日期 | DateTime | 收藏时间 |
| 评分 | SingleSelect | ⭐ 到 ⭐⭐⭐⭐⭐ |
| 状态 | SingleSelect | 🔖 已收藏 / 📖 在读 / ✅ 已读完 / 🔄 待重温 / ✅ 已入库 |

### 选项命名规范

**所有 SingleSelect 选项必须带 Emoji 前缀**（用户审美要求），且格式统一：

- 完成类：✅ 已完成 / ✅ 已读完 / ✅ 已入库
- 待处理类：⏳ 待跟进 / 🔖 已收藏 / 📖 在读 / 🔄 待重温
- 计划类：📋 计划中
- 分类类：💻 💼 🧘 🎯 📖 🔮 📰 🎨 🗂
- 来源类：📱 🌐 📚 🎧 🎬 📰 🎵 📨 💬 📄 🗂

**规则：** emoji + 空格 + 中文描述。禁止无 emoji 的纯文本选项。`其他`统一用 `🗂 其他`。

### 模板设计原则

1. **主字段（第一列）选择** — 日期为中心的用 DateTime，内容为中心的用 Text
2. **SingleSelect 选项命名** — 一律加 Emoji 前缀 + 空格 + 描述
3. **多个表共享一个 Base** — 按功能域分表
4. **默认空记录的清理** — 新建表格时默认约 10 条空记录，用 DELETE 逐条删除

## 经验总结

1. 没有"列出所有表格"的 API，需要用户提供 app_token
2. 建表时默认字段结构固定（文本/单选/日期/附件）
3. 字段名必须精确匹配
4. PUT 字段选项会重建内部 ID，必须先用 NAME 迁移记录再 PUT
5. PATCH 重命名数据表，PUT 更新字段——方法弄混会返回 404
6. 选项清理工作流：扫描→迁移→PUT→验证
7. 本体映射（Ontology）让 AI 能看懂表结构，不只是数据仓库
