# 飞书文档 API 读取（DM 上下文）

> 当用户通过 DM 或群聊发送 feishu.cn/docx/ 链接时，`feishu_doc_read` 工具不可用（需飞书评论上下文）。走 API 读取。

## doc_token 提取

从 URL 中提取：

```
https://www.feishu.cn/docx/PBcXdJTbUoWtgcx54ExcIz9snAP
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^ doc_token (30+ chars)
```

## 读取流程

### 1. 获取 token

```bash
# 使用 timeout 防止挂起
AUTH=$(timeout 10 curl -s -m 8 -X POST \
  'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"cli_aa869b8d6b3c5cc3","app_secret":"qSk4tz1A15aWo5K4eFw2lbhibgMAVaHN"}')

# 提取 token
TOKEN=$(echo "$AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")
```

### 2. 读取文档

```bash
# 保存到临时文件（避免管道超时）
timeout 12 curl -s -m 10 \
  -H "Authorization: Bearer $TOKEN" \
  'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/raw_content' \
  -o /tmp/feishu_doc.json
```

### 3. 提取内容

用 `execute_code` 或 read_file 提取 JSON 中的 `data.content` 字段：

```python
import json
with open('/tmp/feishu_doc.json') as f:
    data = json.load(f)
content = data['data']['content']
# content 是纯文本（含 \n 换行符）
```

### 4. 保存为可读文本

```python
with open('/tmp/feishu_text.txt', 'w', encoding='utf-8') as f:
    f.write(content)
# 然后用 read_file 逐段阅读
```

## 已知故障

| 故障 | 原因 | 解决 |
|:----|:-----|:-----|
| Python `requests` 超时 | WSL 网络环境对 feishu.cn 的 Python HTTPS 请求不稳定 | 改用 `curl`（workaround：`timeout + curl -s -m`） |
| 管道超时 | `curl | python3 -c` 链式管道在大文档时超时 | 分两步：先 `-o /tmp/file.json` 保存，再读取 |
| `feishu_doc_read` 报 "not in a Feishu comment context" | 该工具仅在飞书评论对话中可用 | 走 API 流程 |
| 内容过长被截断 | read_file 的显示限制 | 分页：`offset/limit` 参数 |

## Post-Processing：raw_content → Obsidian Markdown

Feishu `raw_content` API 返回纯文本，需要手动转换为 Obsidian 格式。处理方法取决于内容类型：

### 类型 A：结构化笔记/读书笔记（带 emoji 标记、类表格文本）

**识别信号：**
- 内容以书名/标题开头，而非纯论述
- 包含 emoji 标记（📖 📌 🔑 💡 ⚠️ 等）
- 有类表格结构（竖线 `|` 或空格对齐的列）
- 有章节/部分划分（第一章 / 第二部分 / 核心内容 等）

**转换步骤：**
1. **添加 YAML frontmatter**：tags, aliases, author, rating, created
2. **emoji → markdown 标题**：
   - `🔑 核心框架` → `## 🔑 核心框架`
   - `📖 第一章` → `## 📖 第一章`
   - `核心内容`（无 emoji 但紧跟标题） → `### 核心内容`
3. **类表格 → markdown 表格**：用 `|` 分隔列，加表头分隔行 `|---|`
4. **单行点评/高亮 → Obsidian callout**：
   - `> 💡 点评：...` → `> 💡 **点评**：...`
   - `> 📌 ...` → `> ...`
5. **保留原文结构**：不重新组织内容，只格式化呈现

### 类型 B：速记/文章/分析（无结构标记，纯段落）

**转换步骤：**
1. 添加 frontmatter
2. 按段落拆分 → 适当的 `##` / `###` 标题
3. 关键结论用 `> **重要**：...` 高亮
4. 列表项用 `- ` 转为无序列表

### 类型 C：表格密集的文档（如 KPI 表、数据表、配置表）

**转换步骤：**
1. 识别类表格行（空格对齐的多列文本）
2. 用 Python 解析间隙模式 → 转为 `|` 分隔的 markdown 表格
3. 行数过多（>20行）的表格考虑片段化或只提取关键行

### 通用注意事项

- ❌ 不要直接 dump raw_content 到 .md（纯文本不可读）
- ❌ 不要手动重写每段内容 — 保留原文，只做格式转换
- ✅ 始终提供 frontmatter（tags/aliases 帮助 vault 内的反向链接和 Dataview 查询）
- ✅ 善用 Obsidian 特有语法：`[[wikilink]]`、`> [!note]` callout、YAML frontmatter
