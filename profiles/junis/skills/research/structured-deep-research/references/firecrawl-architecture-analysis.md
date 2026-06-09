# Firecrawl 架构分析与可吸收理念

> 分析日期：2026-05-31 | 来源：firecrawl/firecrawl | Star: 28k+ | 许可证：AGPL-3.0

## 一句话定位

Web Content API for AI Agents — 搜索、抓取、清洗、结构化输出一体化，输出 LLM-ready 的 Markdown。

## 系统架构

```
用户请求
  ↓
API Gateway (Express + WebSocket)
  ↓
┌──────────────────────────────────────┐
│           Engine Selector            │
│  (buildFallbackList: 按需求+质量排序) │
└──────┬──────────────┬───────────────┘
       ↓              ↓
  ┌─────────┐   ┌──────────┐
  │ Fire    │   │Playwright │  ← 浏览器引擎
  │ Engine  │   │Service    │     (Playwright-ts)
  │ (CDP/   │   └──────────┘
  │  TLS)   │   ┌──────────┐
  └─────────┘   │   RD     │  ← 缓存层
                │ (Redis)  │
                └──────────┘
                ┌──────────┐
                │  Rabbit  │  ← 消息队列
                │   MQ     │
                └──────────┘
                ┌──────────┐
                │  Postgres│  ← 持久化
                └──────────┘
```

**服务列表（6个）：**
- `api` — 主服务 Node.js/Express，8GB
- `playwright-service` — 浏览器引擎，4GB
- `redis` — 队列+缓存
- `rabbitmq` — 消息队列（NUQ 用）
- `nuq-postgres` — 自定义 PostgreSQL（NUQ 队列后端）
- 最小自部署要求：**8GB+ RAM**

## 核心设计模式（⭐最值得吸收的部分）

### 1. 多引擎兜底链（Multi-Engine Fallback Chain）

**核心思路：** 一个 URL 进来，不是"用最好的引擎"，而是"按质量从高到低试，不行就换"。

每个引擎有三个属性：
- `quality`（质量分）— 正数是好引擎，负数是抢救引擎
- `features`（能力矩阵）— 支持哪些功能点
- `maxReasonableTime`（合理等待时间）— 不等死

**引擎排序（我们自部署场景简化版）：**

| 引擎 | 质量 | 适用场景 |
|------|------|---------|
| index（缓存） | 1000 | 缓存命中，直接输出 |
| playwight | 50 | 完整浏览器渲染 |
| fetch | 5 | 简单 HTTP GET |
| pdf | -20 | PDF 专用（抢救） |
| document | -20 | DOCX 专用（抢救） |

**关键设计决策：**
- 如果正质量引擎能覆盖需求，直接过滤掉所有负质量引擎（不降级）
- 每个引擎独立声明 feature 支持，不搞全能力一刀切
- 有重试变体（`fire-engine;cdp` 和 `fire-engine(retry);cdp`）

### 2. Feature Flag → Engine 匹配系统

请求携带功能需求（截图/actions/PDF等），系统自动计算每个引擎的"支持度分"。只有支持度 > 50% 的引擎才进入候选。

```typescript
// 简化逻辑
for (const engine of allEngines) {
  supportScore = sum(featureFlagPriority where flag requested AND engine supports it);
  if (supportScore >= totalRequestedPriority / 2) {
    candidates.push(engine);
  }
}
// 按 quality 排序后依次尝试
candidates.sort(byQuality).forEach(tryEngine);
```

**Feature Flag 优先级设计（大业务价值 > 小细节）：**

| Flag | 优先级 | 说明 |
|------|--------|------|
| pdf / document | 100 | 文档格式支持很关键 |
| screenshot | 10 | 截图需求 |
| actions | 20 | 页面交互操作 |
| waitFor | 1 | 等待时间（低优先级） |

### 3. Search → Scrape 一体化管道

不是"搜索完丢链接给你"，而是：

1. 搜索 query（多搜一倍：limit × 2）
2. 对每个 result 链接跑 scrapeURL（复用引擎链）
3. 把抓取的内容 merge 回搜索结果
4. 一次返回完整数据

**核心洞察：** 搜索和抓取是同一个问题的两面，分开是给用户添麻烦。

### 4. Markdown First 输出

所有原始内容最终统一转为 Markdown：
- HTML → 自定义转换器 → Markdown（不是 turndown，是自研）
- PDF → LlamaParse → Markdown
- DOCX → mammoth → HTML → Markdown

**理念：** 不给用户脏数据。LLM-ready 是默认要求，不是可选功能。

### 5. MCP 原生支持

`npx @firecrawl/mcp` 一行命令接入任何 MCP 客户端。

## 可吸收理念（用于我们自己的系统）

### 原则一：兜底思维

不要追求单个方案完美，建一个"试错链"——最好的方案先试，失败后自动降级。明确区分为"好方案"（正质量分）和"抢救方案"（负质量分）。

**适用：** 我们的 web_extract 可以改成多引擎链——先试浏览器渲染 → firefox headless → 简单 HTTP。当前只用一种方案，失败了就报错。

### 原则二：能力声明 vs 能力猜测

每个引擎声明自己支持什么能力（feature flags），而不是系统猜测。避免"用一个全能引擎去做所有事"。

**适用：** 我们可以给每个 web 提取方式标注能力（JS支持/截图/等待/表单提交），按需选择。

### 原则三：输出质量优先于原始数据

不要输出原始 HTML 让用户自己去洗。在 pipeline 内完成"脏数据 → 干净 Markdown"的转换，一步到位。

### 原则四：Cache 是第一引擎

质量最高（1000）的是 index（缓存层）。先看缓存有没有，有就直接返回。这不只是性能优化，是核心架构原则——**"复用就是最快"**。

### 原则五：API 即工具接口

SDK 的顶层方法（search/scrape/crawl/extract）直接对应 MCP 工具。API 设计 = UX 设计。用户的调用路径应该短到不需要看文档。

## 不可部署的原因

- 最低要求 8GB+ RAM（playwright-service 独占 4GB，api 独占 8GB）
- 当前 WSL 可用内存 1.7GB
- 需先安装 Docker（当前无）
- 替代方案：Firecrawl Cloud API，免费层 500 页/月

## 原文关联

- GitHub: https://github.com/firecrawl/firecrawl
- Cloud: https://firecrawl.dev
- Docs: https://docs.firecrawl.dev
