# WorkBuddy Skill Standardization Reference

WorkBuddy (腾讯云 AI Agent 桌面工作台) skills are stored as SKILL.md files under:
`/mnt/c/Users/<username>/.workbuddy/skills/<skill-name>/SKILL.md`

Hermes running in WSL can access these files directly via the mounted Windows filesystem.

## ⚠️ 第一原则：先备份再修改

```bash
cp SKILL.md SKILL.md.bak.<version>
```

每次改技能前必须备份，以便回退。

## Standard Skill Structure

A standardized WB skill has three layers:

### 1. YAML Frontmatter (WB Parser Only)

WB 的 YAML 解析器只识别有限字段。标准格式如下：

```yaml
---
name: skill-slug-name
title: 中文名
display_name: 中文显示名（带类型说明）
description: 技能描述，包括触发条件、核心能力
agent_created: true
version: 1.0.0
author: Author Name
tags: [标签1, 标签2]
trigger_words: 触发词1、触发词2、触发词3    # 逗号分隔字符串，非YAML列表！
---
```

**关键注意**：
- `name` 使用短横线命名（如 `textual-alchemist`）
- `version` 升级规则：微调参数加次版本号（1.0→1.1），重大重构加大版本号（1.x→2.0）
- `trigger_words` 必须是逗号分隔字符串（参考 WB 内置 `周报生成` 技能的格式），不是 YAML 列表
- 不要在 YAML 前数据中添加 WB 未识别的自定义字段（会被忽略）

### 2. Markdown 输入输出参数表（正文开头）

WB 不识别 YAML 中的 `input_schema` / `output_schema`，所以参数定义要写在正文 Markdown 中：

```markdown
---

## 📥 标准化输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|:----:|:----:|------|
| `param1` | string | ✅ | 描述 |
| `param2` | integer | ❌ | 描述，默认值 |

### 调用示例

```json
{
  "param1": "value",
  "param2": 123
}
```

## 📤 标准化输出参数

| 参数 | 类型 | 说明 |
|------|:----:|------|
| `result_field1` | string | 描述 |
| `result_field2` | array | 描述 |

### 输出示例

```json
{
  "result_field1": "value",
  "result_field2": []
}
```
```

### 3. 技能本体（原有内容保持不变）

全部核心知识、场景、算法、示例等保留不变。只在前头加标准头。

## 技能压缩技巧（去冗余）

对于内容繁多（3000+行）的技能，可以在以下方面压缩：

### 压缩离散引用行

**Before**（7个独立标题，~21行）：
```
## 【引用D3】→ 详见「道德经讲义·无为无不为」

## 【引用D2】→ 详见「道德经讲义·执古之道」
```

**After**（紧凑列表，3行）：
```
【引用快捷索引】
- D3→道德经讲义·无为无不为 | D2→道德经讲义·执古之道
```

### 去除重复内容

**Before**（索引表 + 重复的引用规范代码块，~20行）：
```
| S1 | 概念 | 位置 | 摘要 |

引用规范：
【引用S1】→ 详见...
【引用S2】→ 详见...
...(重复索引表内容)
⚠️ 禁止重复描述
```

**After**（一句话带过，2行）：
```
引用规范：引用时使用【引用序号】→ 详见「位置」格式。禁止重复描述。
```

### 压缩原则

- ✅ 只删**明显重复**的内容（同一个数据出现两次以上）
- ✅ 只删**格式冗余**（空行、无意义分割线）
- ❌ 不删**核心知识**（算法、场景、代码、案例）
- ❌ 不合并重写**业务逻辑**（避免改错）
- 压缩后验证 YAML 头部和核心内容完成性

### 真实压缩案例：六韬易哲 V3.3 → V4.0

一个 3304 行 / 141KB 的易学智能体技能：

| 压缩项 | 变更 | 节省 |
|--------|------|------|
| 分散引用行（7个 `##` 标题） | 合并为2行列表 | **~19行** |
| 重复引用规范（16行代码块+警告） | 替换为1句话 | **~17行** |
| 知识库内容 | 全部保留 | 0损失 |
| **总计** | 3304→3274行，141KB→139KB | **0.9%** |

**注意**：大多数技能没有六韬易哲那么多冗余。六韬智脑（860行）几乎无压缩空间（0空行、紧凑格式）。标准化的核心价值是加 input/output 参数定义，而非压缩。

## 技能标准化流程

1. ✅ 读完整 SKILL.md，理解技能用途和核心能力
2. ✅ 备份原文件：`cp SKILL.md SKILL.md.bak.<version>`
3. ✅ 更新 YAML frontmatter（加 `trigger_words`、`version`、`tags` 等）
4. ✅ 在正文开头添加输入/输出参数表格 + 调用示例
5. ✅ 扫描冗余内容进行压缩
6. ✅ 验证头部和核心内容完整
7. ✅ 告知用户去 WB 刷新查看

## Input/Output Schema Design Patterns（按技能类型）

| 技能类型 | 典型输入 | 典型输出 |
|---------|---------|---------|
| **古籍数字化** | source.type, source.path, options.book_title, options.chapters, options.output_format | book_title, content_nodes[].cleaned_text, content_nodes[].annotations[], data_integrity |
| **易学占卜** | query_type, question, birth_year, birth_month, birth_hour, gender, divination_numbers | analysis_type, result_summary, key_findings, advice, references, confidence |
| **战略决策** | query_type, question, context, urgency, stakeholders, constraints, risk_tolerance | summary, core_analysis, risk_assessment, action_plan, cognitive_biases_checked |
| **周报生成** | date_range, team_name, tasks, metrics, highlights | report_content, charts, summary, next_plan |

## Key Paths

| What | Where |
|------|-------|
| User skills directory | `/mnt/c/Users/<user>/.workbuddy/skills/` |
| WB database | `/mnt/c/Users/<user>/.workbuddy/workbuddy.db` |
| WB settings | `/mnt/c/Users/<user>/.workbuddy/settings.json` |
| WB MCP config | `/mnt/c/Users/<user>/.workbuddy/.mcp.json` |
| WB executable | `C:\Users\<user>\AppData\Local\Programs\WorkBuddy\WorkBuddy.exe` |
| WB CLI | `C:\Users\<user>\AppData\Local\Programs\WorkBuddy\resources\app.asar.unpacked\cli\dist\codebuddy.js` |

## Integration with Hermes

Since Hermes runs in WSL and WB runs on Windows, they can communicate via:
- **File system**: Hermes reads/writes `/mnt/c/Users/<user>/.workbuddy/` directly
- **PowerShell CLI bridge**: Hermes calls `powershell.exe -Command "node '...codebuddy.js' --print '...' -y"`
- **MCP bridge**: WB has connector-proxy MCP at `http://127.0.0.1:9359/mcp` (Windows-only)
- **Scheduled tasks**: WB automations can be triggered via its SQLite database
