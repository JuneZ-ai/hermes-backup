---
name: firecrawl-patterns
description: Firecrawl 爬取架构与设计模式——多引擎兜底链、质量分排序、Markdown First 输出管线。可复用设计哲学 + Firecrawl Cloud API 接入方案
category: web
trigger_keywords: [firecrawl, 爬虫, 网页抓取, 引擎兜底, fallback, 网页清洗, web-scraping]
---

# Firecrawl 设计模式

> 知识来源：[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) 源码逆向分析（MIT 协议）。20.4k stars，Node.js/Typescript 全栈。

## 核心架构图

```
请求进来
  ↓
buildFallbackList() — 根据 feature flags + quality 选引擎
  ↓
┌──────────────────────────────────────────┐
│         引擎兜底链 (按质量分试)             │
│                                          │
│  index(1000) → 命中即返回，不往下走         │
│    ↓ (未命中/失败)                         │
│  x-twitter(1500) / wikipedia(500)         │
│    ↓                                      │
│  fire-engine:cdp(50) → 主力引擎            │
│    ↓                                      │
│  fire-engine:cdp;retry(45) → 重试一次      │
│    ↓                                      │
│  playwright(20) → 回退到 Playwright        │
│    ↓                                      │
│  fire-engine:tls(10) → TLS 级轻量爬取      │
│    ↓                                      │
│  fetch(5) → 纯 HTTP GET                   │
│    ↓                                      │
│  [抢救引擎 - 负质量分]                      │
│  cdp;stealth(-2) / tls;stealth(-15)       │
│  pdf(-20) / document(-20)                 │
└──────────────────────────────────────────┘
  ↓ (成功)
统一输出管线
  ↓
Markdown / JSON / Screenshot / PDF...
```

## 精髓设计：Feature Flag + Quality

### 1. 每个引擎声明能力

```typescript
type Engine = {
  quality: number;        // 质量分：>0 = 好引擎, <0 = 抢救引擎
  features: {
    actions: boolean;     // 支持点击/交互
    screenshot: boolean;  // 支持截图
    pdf: boolean;         // 支持 PDF
    // ...
  };
  maxReasonableTime: number; // 最久等多久，超时就跳过
};
```

### 2. 选引擎逻辑

```
① 遍历所有引擎 → 计算 feature support score
② 只保留支持度 > 50% 的引擎
③ 如果列表中有 quality > 0 的引擎 → 过滤掉所有 quality < 0 的
④ 按 (supportScore desc, quality desc) 排序
⑤ 从第一名依次尝试，成功则停止，失败则下一个
```

**关键决策点**：`selectedEngines.some(x => x.quality > 0)` 时排除负质量引擎——好引擎能干活就不走抢救路线。

### 3. 每个维度的优先级

feature flag 也有优先级权重（截图=10, actions=20, PDF=100），支持度分数是满足的功能权重之和。这个权重系统决定了：如果请求需要截图+actions（总权重30），某个引擎只支持截图（权重10），分数=10 < 阈值15，就不选这个引擎。

## 输出管线（Markdown First）

```
原始内容 → 按类型分流：

HTML → 自定义 markdown 转换器 → 干净 Markdown
PDF  → LlamaParse API          → Markdown
DOCX → mammoth(HTML)           → Markdown
视频  → YouTube Transcript API  → 文本

统一输出格式：
  { url, title, markdown, screenshot?, metadata? }
```

不给用户原始 HTML，直接出 LLM-ready 内容。这是和 lesstoken 互补的地方：
- **lesstoken**：本地简单的 HTML → Markdown
- **Firecrawl**：多引擎兜底 + 专业文档解析 + 截图 + 结构化提取

## Search+Scrape 一体化

```
query → 搜索引擎(limit*2) → 对每个结果跑 scrapeURL → 合并返回

好处：
- 用户一次请求，拿到完整内容
- 复用同一套引擎链，保证输出质量一致
- 计费清晰：search credits + scrape credits
```

## 可吸纳的设计原则

| 原则 | 描述 | 对我们当前 web_extract 的启发 |
|------|------|------------------------------|
| **多引擎兜底** | 不追求单个引擎完美，按质量排序试错 | 我们的 web_extract 只有单通道，失败就是失败 |
| **质量分正负分离** | >0 是正常引擎，<0 是抢救引擎 | 可以给不同方案打质量分，分阶段降级 |
| **Feature Flag 匹配** | 按需求选引擎，不用大炮打蚊子 | 简单取文本用 fetch，要交互用浏览器 |
| **Markdown First** | 输出直接喂 LLM，不二次清洗 | 和 lesstoken 理念一致，但质量更高 |
| **Cache 优先** | 缓存质量分最高（1000），命中不往下走 | 我们的 web 抓取没有缓存层 |
| **MCP 原生** | `npx @firecrawl/mcp` 一行接入 | 我们也可以通过 MCP server 挂载 |

## 接入方案：Firecrawl Cloud API

由于自部署需 8GB+ 内存，推荐用 Cloud API（免费层 500 页/月）。

### 方式一：MCP Server（推荐）

⚠️ npm 包名是 `firecrawl-mcp`（v3.20.1），不是 `@firecrawl/mcp`

```bash
# Firecrawl 官方 MCP server
# 1. 获取 API key：https://firecrawl.dev
# 2. 在 config.yaml 的 mcp_servers 添加：

# mcp_servers:
#   firecrawl:
#     command: npx
#     args: ["-y", "firecrawl-mcp"]
#     env:
#       FIRECRAWL_API_KEY: "fc-xxx"

# 3. 重启 Hermes，自动加载 firecrawl_scrape / firecrawl_search / firecrawl_crawl 等工具
```

### 方式二：Python SDK 直接调用

```python
from firecrawl import Firecrawl

client = Firecrawl(api_key="fc-xxx")

# 单页抓取
result = client.scrape("https://example.com")
print(result["markdown"])

# 搜索+抓取一体
results = client.search("deepseek API tutorial")
for r in results:
    print(r["markdown"][:200])

# 整站爬取
crawl = client.crawl("https://docs.example.com", limit=100)
```

### 方式三：REST API（无 SDK 时）

```bash
curl -X POST 'https://api.firecrawl.dev/v2/scrape' \
  -H 'Authorization: Bearer fc-xxx' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'
```

## Herramienta（工具化启发）

Firecrawl 启示我们：当前的 `web_extract` + `web_search` 可以做三层升级：

1. **浅层（无需部署）**：所有抓取先走 fetch，fetch 失败降级到 playwright/浏览器
2. **中层（加 MCP）**：挂载 Firecrawl Cloud MCP server，接管搜索和抓取
3. **深层（自部署）**：待内存充足（8GB+），Docker 部署 Firecrawl 全栈

当前建议走**中层**——注册 Cloud API 挂 MCP，15 分钟，0 运维。

## 参考链接

- GitHub: https://github.com/firecrawl/firecrawl
- Cloud API: https://firecrawl.dev
- Docs: https://docs.firecrawl.dev
- MCP: `npx @firecrawl/mcp`
