---
name: wechat-knowledge-ingestion
description: |
  微信文章→知识库全自动管线。收到微信公众号文章链接时，自动提取正文→分类判定→注入Obsidian→更新总纲→飞书同步。
  触发词：「读这个」「处理这篇」「入库」「收藏」「转发这个」「微信文章」「mp.weixin」
  也接受普通网页链接、视频号链接（需用户提供文案）。
---

# 微信文章→知识库全自动管线

> 把你在微信上看到的每一篇好文章，自动变成知识库的永久资产。

---

## 核心工作流

```
用户转发/发送微信文章链接
  ↓
Step 1: 提取正文
  ├── 微信公众号文章 → 直接抓取（Mobile UA + js_content提取）
  ├── 普通网页 → Trafilatura / Jina Reader
  └── 视频号 → 需要用户提供文案或截图
  ↓
Step 2: 内容分析
  ├── 提取核心论点、关键数据、金句
  ├── 分类判定（归属哪个模块）
  └── 判断是否有跨模块价值
  ↓
Step 3: 知识库注入
  ├── 创建信息流入口（01-信息流/）
  ├── 创建结构化笔记
  ├── 更新模块索引
  └── 注入反链到已有笔记
  ↓
Step 3.5: 归档原始素材（`_raw_sources/`）
  ├── 文章 → `_raw_sources/articles/<文件名>.md`
  │   ├── frontmatter: source_url, ingested, sha256
  │   └── body: 原始正文（immutable，只读不改）
  ├── PDF → `_raw_sources/papers/<文件名>.md`
  └── 封面图/截图 → `_raw_sources/assets/`
  ↓
Step 4: 同步与报告
  ├── 飞书三表同步
  └── 向用户报告结果
```

---

## Step 1: 提取正文

### 微信公众号文章（已验证方案）

```python
import re, requests, html as htmlmod

url = "https://mp.weixin.qq.com/s/xxxxx"
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
}
resp = requests.get(url, headers=headers, timeout=20)
html = resp.text

# 1. 提取元数据（标题、作者、发布时间）
meta = {}
m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
if m: meta["title"] = m.group(1)
m = re.search(r'<meta property="og:article:author" content="([^"]+)"', html)
if m: meta["author"] = m.group(1)
m = re.search(r'<em id="publish_time">([^<]+)</em>', html)
if m: meta["publish_time"] = m.group(1)

# 2. 提取正文（id="js_content"）
m = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
if m:
    text = re.sub(r'<[^>]+>', '', m.group(1))
    text = htmlmod.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
```

**注意**：微信 HTML 可能 ~3MB 但 requests 下载没问题。必须用 Mobile UA 否则重定向验证页。正文提取后约 1000-5000 字。js_content 为空时降级到 Trafilatura。

### 元数据提取（必做）

每次抓取后先提取 og:title（标题）、og:article:author（公众号）、publish_time（发布时间），用于笔记 frontmatter 的 title 和 source 字段。

### 普通网页（Trafilatura）

```bash
pip install trafilatura 2>/dev/null
python3 -c "
import trafilatura
downloaded = trafilatura.fetch_url('https://example.com')
if downloaded:
    print(trafilatura.extract(downloaded))
"
```

### 备用方案（Jina Reader，零安装）

```bash
curl -sL --max-time 30 "https://r.jina.ai/https://example.com" -H "Accept: text/plain"
```

### ⚠️ 已知失败模式：access-control 限制

即使使用 Mobile UA，部分微信公众号文章仍返回「未知错误，请稍后再试」页面。常见原因：
- 文章设置了**仅限微信内访问**（最常见）
- 文章已删除/过期
- 同一 IP 短时间内大量请求触发风控

**处理流程**：

```
抓取返回"未知错误"页面
  ↓
尝试 Jina Reader 备用方案（见下方）
  ↓
Jina 也失败 → 直接向用户说明无法自动提取，请用户手动粘贴正文
  ↓
用户粘贴后 → 从 Step 2 继续（内容分析/分类/注入）
```

**不要反复重试同一 URL**。Mobile UA 失败后直接问用户要文本。

### ⚡ 可选优化：LessToken 后处理

提取到正文后，可过 LessToken 做二次优化——进一步压缩 Token、去除残留噪点：

```bash
# 方式一：Python 脚本直接抓取+优化
python3 ~/.hermes/skills/mlops/lesstoken-web-optimizer/scripts/lesstoken_optimizer.py \
  https://example.com --json -o optimized.md

# 方式二：先提取再优化（适合已有提取文本的场景）
python3 -c "
import sys; sys.path.insert(0, '~/.hermes/skills/mlops/lesstoken-web-optimizer/scripts')
from lesstoken_optimizer import optimize
result = optimize('https://example.com')
print(result['markdown'])
"
```

**效果**：在 Trafilatura/Jina 基础上再省 10-30% Token，同时清理空链接和多余空行。

**何时跳过**：短文章（<500 字）或正文已非常干净时不需要过 LessToken。

---

## Step 2: 内容分类

参照 `obsidian-ingestion-pipeline` 的模块判定矩阵：

| 内容倾向 | 主模块 | 副模块 |
|---------|-------|-------|
| 哲学/历史/文化 | 六韬史鉴 | 太极双螺旋 |
| 决策/管理/战略 | 六韬智脑 | 太极双螺旋 |
| 易学/命理/中医 | 六韬易哲 | 决断之桥 |
| 认知/思维模型 | 太极双螺旋 | 六韬智脑 |
| 法律/伦理/哲学 | 太极双螺旋 | 六韬史鉴 |
| 经济/金融/政策 | 六韬史鉴 | 六韬智脑 |
| AI/ML/技术 | 六韬智脑 | 太极双螺旋 |

**判定三问**：
1. 这篇文章的核心价值是「道」（哲学/历史）还是「法」（方法论/决策）？
2. 它和知识库中哪个现有笔记关联最紧密？
3. 它有没有跨模块对话的潜力？（如果有，同时注桥）

---

## Step 3: 知识库注入

### 信息流入口

```yaml
---
title: "文章标题"
source: "https://mp.weixin.qq.com/s/xxxxx"
status: processed
type: article
field: 见分类矩阵
tags: [文章标签]
received: 2026-05-24
processed: 2026-05-24
---
```

### 结构化笔记模板

```
# 文章标题

> 一句话摘要

## 核心论点
- 论点1（原文支撑）
- 论点2（原文支撑）

## 关键数据/事实
- [数据点]

## 与知识库的关联
- → [[现有笔记]]：对应关系说明
- → [[现有笔记]]：对应关系说明

## 金句
> 原文金句

## 我的启示
- 这个观点对我的决策/认知有什么影响？
```

### 更新索引
- 更新对应模块的 `index.md`
- 更新 `00-六韬总纲.md` 的使用场景速查表

---

## Step 3.5: 归档原始素材（_raw_sources/）

**理念**（来自 Karpathy LLM Wiki）：原始素材是**不可变层**（Immutable Layer）。处理后不删不改，只归档。未来追溯「这个框架最早出处是哪篇文章」时有锚点。

### 归档规则

| 素材类型 | 目标目录 | frontmatter 格式 |
|---------|---------|-----------------|
| 微信文章/网页 | `_raw_sources/articles/` | source_url, ingested, type, sha256 |
| PDF/论文 | `_raw_sources/papers/` | source_url, ingested, type, sha256 |
| 图片/截图 | `_raw_sources/assets/` | 原文件名保留 |

### 执行方式

信息流笔记的 frontmatter 新增 `raw_source` 字段，指向归档文件：

```yaml
---
title: "AI进入第二幕"
source: "https://mp.weixin.qq.com/s/..."
raw_source: "_raw_sources/articles/AI进入第二幕-从对话到行动.md"
status: processed
---
```

### 与知识库的关系

```
_raw_sources/
  └── articles/AI进入第二幕.md （不可变原文）
        ↑ raw_source
01-信息流/AI进入第二幕.md     （处理后的入口笔记）
        ↑ 主模块
六韬智脑/xx-AI方法论.md       （提炼后的知识库笔记）
```

**原则**：不碰 `_raw_sources/` 下的文件。更正/更新写在知识库笔记里。需要溯源时读 `raw_source` 字段找到原始出处。

---

## Step 4: 飞书同步

参照 `obsidian-ingestion-pipeline` 的飞书三表同步规矩。**详细的 API 调用模式和字段名参考见 `references/feishu-bitable-sync.md`**。

### 三表规矩

1. **搭建日志** (tbllV9WgN64Zwput) → 新增一条（内容="处理微信文章：XXX"）
   - 领域单选="知识库基建"，状态单选="✅已完成"
2. **每日记录** (tblTLllADiUdhL6e) → 追加当天记录内容
   - 日期字段名="公历时间"（非"日期"），UTC+8 当天0点毫秒时间戳
   - 类型单选：传入选项 NAME（如"💻 工具"）
3. **收藏随想录** (tblydJHMALlK3stv) → 如果文章值得收藏，新增一条
   - 日期字段名="收藏日期"（非"日期"）
   - 来源类型/分类/评分/状态：均传入选项 NAME 字符串

### ⚠️ 关键陷阱

**永远不要猜测字段名。** 字段名不一定符合直觉（"公历时间"不是"日期"）。查询 `/bitable/v1/apps/{token}/tables/{table_id}/fields` 端点验证字段名和 SingleSelect 选项名称。新建记录时 SingleSelect 字段传递选项显示的 NAME 字符串，不是 option ID。

### 异步输出模式

用户除了要求入库，有时会要求以素材为参考做二次产出（如"作为公众号构思参考"）。遇到这类需求，在 Step 3 的知识库注入后，额外创建独立的笔记文件（如 `公众号·XXX方法论.md`），并在信息流入口笔记的 frontmatter 中建立反链。

---

## 使用示例

```
用户：https://mp.weixin.qq.com/s/abc123 帮我读这篇入库
→ 我执行全流程：提取→分类→注入→报告
```

```
用户：这个视频号内容你帮我看看
→ 如果无法自动提取：告知用户需提供文案/截图
→ 如果有截图：用RapidOCR提取文字
```

---

## 安装依赖

```bash
pip install requests beautifulsoup4 lxml trafilatura
```

确保 Obsidian vault 路径可访问：
```
/mnt/c/Users/18502/Documents/Obsidian Vault/
```

---

## 触发方式

### 完整处理（默认）
Full ingestion pipeline: extract→classify→inject→sync→report.

- **微信转发**：用户转发文章到WB WeChat Bot → 我处理
- **飞书分享**：用户在飞书发链接 → 说「读一下」或「入库」→ 我处理
- **手动提交**：用户直接发URL → 自动触发本技能

### 轻量归档
用户只想「收起来」不立即加工的场景。收到内容后不做全量提取/分类/注入，仅写入 `01-信息流/`，标记 `status: raw`，留给喂料 cron 自行处理。

**触发词**：
- 「收」前缀 — 用户发内容时带「收」字（如「收 今天想到一个概念...」）
- 无明确加工指令 — 用户只发链接或文字，没说「读一下」「入库」等
- 微信文章链接 — 直接丢链接过来，不带指令

**流程**：
```
用户发链接或文字 → 直接写入01-信息流/
  → 标题格式: YYYY-MM-DD-来源-标题.md
  → frontmatter: status: raw, type, source
  → 正文保留原始内容（文章链接的抓取标题+摘要）
  → 不创建结构化笔记/索引/总纲
  → 不同步飞书三表
  → 不报告处理结果（除非用户追问）
```

### 即沉淀（三振跳过）
用户说「沉淀」时，不走轻量归档，直接完成全量提炼→分类→创建永久笔记→更新信息流状态。

**触发词**：「沉淀」「入库」「直接入库」「收好」

**流程**：
```
用户发内容 +「沉淀」
  → Step 1: 提炼核心论点、关联已有知识
  → Step 2: 判定归属模块
  → Step 3: 创建 ZN 系列永久笔记（带编号）+ 双向链接
  → Step 4: 更新信息流源文件 status: processed
  → Step 5: 记录搭建日志
  → 向用户报告归宿（哪个模块·哪条笔记）
```

**注意**：永久笔记编号需要检查当前模块最新编号（如查看 `六韬智脑/` 目录中 `ZN-` 开头的文件），从下一个顺序号开始创建。

---

## 参考示例

详细的微信文章提取实战记录见 `references/wechat-extraction-example.md`，包含实际文章的元数据提取、正文提取和分类判定全过程。
