# 飞书 Base 同步配置参考

## 连接信息

- **Base Token**: `NzuPbMtMFa0wUusVQKwc69lenib`
- **Feishu App ID**: `cli_aa869b8d6b3c5cc3`
- **Feishu App Secret**: `qSk4tz1A15aWo5K4eFw2lbhibgMAVaHN`（硬编码在 sync-all-to-feishu.py 中）

## 三表结构

| 表名 | Table ID | 去重方式 |
|:----|:---------|:---------|
| 搭建日志 | `tbllV9WgN64Zwput` | 「操作内容」字段精确匹配 |
| 每日记录 | `tblTLllADiUdhL6e` | 「公历时间」当天已存在则跳过 |
| 收藏随想录 | `tblydJHMALlK3stv` | 「收藏日期」当天已存在则跳过 |

## 权限要求

飞书应用需要开通权限：
- `bitable:app` — 多维表格读写

## API 端点

| 操作 | 端点 |
|------|------|
| 获取 token | `POST /open-apis/auth/v3/tenant_access_token/internal` |
| 列出字段 | `GET /open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/fields` |
| 列出记录 | `GET /open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records` |
| 新增记录 | `POST /open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records` |

## 同步脚本

路径：`~/.hermes/profiles/yanqing/scripts/sync-all-to-feishu.py`

逻辑（三表各自独立）：

### 搭建日志
1. 获取 tenant_access_token
2. 读取 OB vault 搭建日志 → 解析日期区块 → 提取表格任务行
3. 读取飞书 Base 已有记录的「操作内容」作为去重依据
4. 新增不重复的记录
5. 按关键词自动推断「领域」字段

### 每日记录（自动留痕）
1. 检查今天是否已有记录（按「公历时间」去重）
2. 如果没有：自动生成一条，含农历/干支/节气 + 当日搭建日志摘要 或「今日无重大动作」
3. 如果有：跳过

### 收藏随想录（自动留痕）
1. 检查今天是否已有记录（按「收藏日期」去重）
2. 如果没有：自动生成一条留痕标记「日期 · 无新增收藏」
3. 如果有：跳过

## 领域映射规则（搭建日志）

| 关键词 | 映射领域 |
|--------|---------|
| 飞书、权限、API、bitable、token | 飞书权限开通 |
| 工具、配置、OCR、Tesseract、脚本、定时 | 工具配置 |
| 架构、设计、决策、规划 | 架构决策 |
| 其他（默认） | 知识库基建 |

## 留痕纪律

- **每日记录**：即使没有新内容，也写入一条留痕记录（含日期/农历/干支等）。不留白白天。
- **收藏随想录**：**不留空壳。** 只有真实收藏（喂料入库的内容）才写入。无内容的日子不写留痕条目。补录/留痕类条目应被清理。

## 排序限制

当前 app 无法通过 API 设置视图排序。PATCH view 返回成功但 property 始终 null。
- **程序化排序**：使用 `POST records/search` 的 `sort: [{"field_name": "收藏日期", "desc": true}]` 参数
- **用户侧排序**：在飞书 UI 点击列头排序，会保存到视图

## 定时任务

- 频率：每天 21:00（北京时间）
- 命令：`hermes cron list` 查看状态
- **留痕纪律**：即使没有新内容，每日记录和收藏随想录也会写入一条空留痕。不留空白天。
- **⚠️ 时序陷阱**：21:00 之后更新的搭建日志不会自动同步，必须手动触发。见 SKILL.md Step 5 规则。
- 手动触发：`python3 /home/hermes/.hermes/profiles/yanqing/scripts/sync-all-to-feishu.py`
- 去重方式：搭建日志按「操作内容」精确匹配；每日记录和收藏随想录按当天日期
