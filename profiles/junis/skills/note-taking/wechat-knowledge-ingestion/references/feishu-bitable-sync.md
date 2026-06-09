# Bitable Field Name Reference (实测验证)

在调用飞书 Bitable API 写记录时，**不要猜测字段名**——必须通过 `/fields` 端点查询真实名称。

## 查询方法

```bash
TOKEN=<your_tenant_access_token>
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields" \
  | python3 -m json.tool
```

## 已实测的字段名

### 搭建日志 (tbllV9WgN64Zwput)

| 界面显示 | API字段名 | 类型 | 说明 |
|---------|----------|------|------|
| 操作内容 | `操作内容` | Text | 必填 |
| 领域 | `领域` | SingleSelect | 选项: 工具配置/知识库基建/架构决策/API打通验证/飞书权限开通 |
| 时间 | `时间` | DateTime | ms timestamp (UTC+8当天0点) |
| 状态 | `状态` | SingleSelect | 选项: ✅已完成/⏳待跟进/📋计划中 |
| 备注 | `备注` | Text | 可选 |

### 每日记录 (tblTLllADiUdhL6e)

| 界面显示 | API字段名 | 类型 | 说明 |
|---------|----------|------|------|
| 公历时间 | `公历时间` | DateTime | ⚠️ 是"公历时间"不是"日期" |
| 农历 | `农历` | Text | 如"2026年4月9日（丙午年 癸巳月 己亥日）" |
| 节气 | `节气` | Text | 无则填"无" |
| 干支 | `干支` | Text | 如"丙午年 癸巳月 己亥日" |
| 黄历宜忌 | `黄历宜忌` | Text | 如"宜祭祀、沐浴、解除；忌开光、安葬" |
| 记录内容 | `记录内容` | Text | 当天活动记录 |
| 类型 | `类型` | SingleSelect | 选项: 📚 读书/💼 工作/🤝 会议/💡 思考/🏠 生活/🌐 见闻/💻 工具 |

### 收藏随想录 (tblydJHMALlK3stv)

| 界面显示 | API字段名 | 类型 | 说明 |
|---------|----------|------|------|
| 标题 | `标题` | Text | 必填(主字段) |
| 来源链接 | `来源链接` | Text | URL |
| 我的感悟 | `我的感悟` | Text | 个人思考 |
| 金句摘录 | `金句摘录` | Text | 原文金句 |
| 来源类型 | `来源类型` | SingleSelect | 选项: 📱 微信文章/🌐 网页/📚 书籍/🎧 播客/🎬 影视/📰 新闻/🎵 歌曲/📨 邮件/💬 聊天记录/📄 PDF/其他 |
| 分类 | `分类` | SingleSelect | 选项: 💻 技术/AI/🏢 商业/管理/🧘 个人成长/🧠 认知/思维/📖 人文/社科/🔮 传统文化/📰 资讯/见闻/🎨 兴趣爱好/其他 |
| 收藏日期 | `收藏日期` | DateTime | ⚠️ 是"收藏日期"不是"日期" |
| 评分 | `评分` | SingleSelect | 选项: ⭐/⭐⭐/⭐⭐⭐/⭐⭐⭐⭐/⭐⭐⭐⭐⭐ — 传字符串如"⭐⭐⭐⭐" |
| 状态 | `状态` | SingleSelect | 选项: 🔖 已收藏/📖 在读/✅ 已读完/🔁 待重温/已入库 |

## 规则

- DateTime 字段：传 UTC+8 当天 0 点的毫秒时间戳
- SingleSelect 字段：传选项的 **NAME 字符串**（如"📱 微信文章"），不是 option id
- 日期不留白：无活动也留空白记录（日期+农历+干支+节气）
