# 飞书多维表格「🧠 第二大脑搭建日志」Schema

> Base Token: `NzuPbMtMFa0wUusVQKwc69lenib`
> API Base: `https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}`
> Auth: POST to `https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal` with `{"app_id": ..., "app_secret": ...}`

## 表1：搭建日志 (tbllV9WgN64Zwput)

| 字段名 | 字段ID | 类型 | 说明 |
|:------|:------|:----|:----|
| 操作内容 | fldJImtmIr | Text (primary) | 操作简述 |
| 领域 | flddmM5UDL | SingleSelect | 可选：工具配置、知识库基建、架构决策、API打通验证、飞书权限开通 |
| 时间 | fldXWij8m0 | DateTime(yyyy/MM/dd) | UTC+8 当天00:00毫秒 |
| 附件 | fldvryjDim | Attachment | — |
| 状态 | fld0bOEl8u | SingleSelect | 可选：✅ 已完成、⏳ 待跟进、📋 计划中 |
| 备注 | fldgHsYXuU | Text | 关联笔记名/备注信息 |

## 表2：每日记录 (tblTLllADiUdhL6e)

| 字段名 | 字段ID | 类型 | 说明 |
|:------|:------|:----|:----|
| 公历时间 | fldzEXgEz7 | DateTime(yyyy/MM/dd, primary) | UTC+8 当天00:00毫秒 |
| 农历 | fldr9WPIQf | Text | 如"四月初七" |
| 节气 | fldheJEN6x | Text | 如"小满后"或空 |
| 干支 | fldJRQcwJ1 | Text | 如"丙午年 癸巳月 丁酉日" |
| 黄历宜忌 | fldJIRpbB0 | Text | 宜/忌/冲 三行 |
| 记录内容 | fldB3bNGW0 | Text | 当天做了什么 |
| 类型 | fld6Dzu6U9 | SingleSelect | 可选：📚读书、💼工作、🤝会议、💡思考、🏠生活、🌐见闻、💻工具 |

## 表3：收藏随想录 (tblydJHMALlK3stv)

| 字段名 | 字段ID | 类型 | 说明 |
|:------|:------|:----|:----|
| 标题 | fldG9B6QMd | Text (primary) | 收藏内容的标题 |
| 来源链接 | fldbQ293j8 | Text | URL |
| 我的感悟 | fldRSYtYaQ | Text | 用户原创感悟 |
| 金句摘录 | fld982hPKJ | Text | 原文金句 |
| 来源类型 | fldPhhTCrK | SingleSelect | 可选：📱微信文章、🌐网页、📚书籍、🎧播客、🎬影视、📰新闻、🎵歌曲、📨邮件/通讯、💬聊天记录、📄PDF/文档、其他 |
| 分类 | fldyJReGgs | SingleSelect | 可选：💻技术/AI、🏢商业/管理、🧘个人成长、🎯认知/思维、📖人文/社科、🔮传统文化、📰资讯/见闻、🎨兴趣爱好、其他 |
| 收藏日期 | fldYEqYVW7 | DateTime(yyyy/MM/dd) | UTC+8 当天00:00毫秒 |
| 评分 | fldWRnwxo4 | SingleSelect | 可选：⭐、⭐⭐、⭐⭐⭐、⭐⭐⭐⭐、⭐⭐⭐⭐⭐ |
| 状态 | fldru2VWwg | SingleSelect | 可选：🔖已收藏、📖在读、✅已读完、🔄待重温 |

## API 模式速查

### 获取 token
```python
import requests
resp = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET})
token = resp.json()["tenant_access_token"]
```

### 查记录（查重）
```python
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
resp = requests.get(f"{base_url}/tables/{TABLE_ID}/records?page_size=50", headers=headers)
items = resp.json()["data"]["items"]
has = any(r["fields"].get("公历时间") == today_ms for r in items)  # DateTime字段匹配毫秒
```

### 创建记录
```python
resp = requests.post(f"{base_url}/tables/{TABLE_ID}/records", headers=headers, json={
    "fields": {
        "操作内容": "xxx",
        "领域": "知识库基建",  # 传选项名，不是ID
        "时间": today_ms,
        "状态": "✅ 已完成"
    }
})
```

### ⚠️ 关键陷阱
1. **DateTime 必须是毫秒级**：`int(today.timestamp() * 1000)`，不是秒
2. **SingleSelect 传选项名**：传"知识库基建"而不是"optgWp5oQH"
3. **field name 是中文名**：传"操作内容"而不是"fldJImtmIr"
4. **code: 1254045 = FieldNameNotFound**：说明传入的字段名在表中不存在
   - 常见错误："操作时间" → 应是"时间"（字段叫"时间"不叫"操作时间"）
   - "所属领域" → 应是"领域"（字段叫"领域"不叫"所属领域"）
   - "完成状态" → 应是"状态"（字段叫"状态"不叫"完成状态"）
   - "关联笔记" → 应是"备注"（字段叫"备注"，用来存关联笔记名）
   - 诊断方法：先 GET /fields 查出实际字段名，再用那些名字 POST，不要猜
