---
name: structured-deep-research
description: >-
  对课题进行深度研究与调研，输出结构化报告。吸收自 AutoGLM DeepResearch 方法论，
  核心哲学是「够用即可」——用有限搜索+有限深读，先展示中间发现，再综合成报告，
  避免信息过量和无效调用。适用于行业调研、专题研究、竞品分析、知识探索等场景。
category: research
trigger_keywords: [深度研究, 调研, 行业分析, 竞品分析, 专题研究, deep research, API调研, 接入工具, 外部API, 工具集成]
related_skills: [arxiv, blogwatcher, task-driven-model-routing, knowledge-synthesis]
references:
  - firecrawl-architecture-analysis.md: Firecrawl 源码级架构分析（多引擎兜底链/Feature Flag匹配/Markdown First），作为开源工具架构分析的完整案例
  - agnes-ai-api-discovery.md: Agnes AI API 侦察实战记录——从视频描述出发，通过域名变体扫描/多语言搜索/子域名探针/端点验证/媒体交叉验证五步法，确认免费全模态 API 的存在
---

# Structured Deep Research（结构化深度研究）

> 吸收自 AutoGLM DeepResearch 工作流。不是搜索越多越好，是**够用即可**。
> 与韬定律元操作原则一致：**做对的事 > 做更多的事**。

## 核心哲学

**信息过量比信息不足更常见。** 限制调用数量本身就倒逼思考质量——如果你只能搜2次、读3页，你就会在动手之前先想清楚真正需要什么。

六条铁律：

| # | 原则 | 说明 |
|:-|:----|:-----|
| ① | **先搜1次，够用就停** | 精准搜索，不够再加第2次。上限≤2次搜索 |
| ② | **展示中间结果** | 每轮搜索后先摆结果，再决定是否继续 |
| ③ | **默认只读1页，≤3页** | 先读最相关那1页，不够再加，上限3页 |
| ④ | **"中间发现"先行** | 出报告前先列"已确认／待核实／缺口" |
| ⑤ | **固定报告结构** | 统一输出格式，不每次临时拼凑 |
| ⑥ | **写完后自查调用数** | 确保搜索≤2次、读页≤3次，超出说明方法有问题 |

## 深度研究流程

### Step 1：拆解子问题

将课题拆解为 **1～2 个最关键的搜索方向**，不要扩散成过多子问题。

优先选择最能直接回答问题的维度，例如：
- 背景与定义
- 最新现状 / 关键数据
- 代表性案例（仅在确有必要时）

> 如果用户的问题已经很具体，直接进入搜索，不必额外拆解。

### Step 2：多轮搜索（≤2次）

使用 `web_search`（或 `arxiv`、`blogwatcher` 等适用工具）进行**有限搜索**：

- **默认先做1次**精准搜索
- **只有当**第一次搜索结果明显不够、结果质量差、或缺少关键维度时，才进行第2次
- 不要为了"完整性"机械扩展搜索轮次

**每次搜索后**，整理并向用户展示中间结果：
- 本次搜索使用的查询词
- 2～5 条最相关结果的标题/来源/摘要
- 对当前信息是否足够的简短判断

### Step 3：深度阅读（≤3页）

从搜索结果中筛选 **1～3 个最相关的页面**，使用 `web_fetch` 或其他读取工具获取全文。

**筛选标准：**
- 摘要信息量丰富、与课题高度相关
- 来源权威（官方网站、知名媒体、学术机构）
- 避免重复来源

**控制规则：**
- 默认只打开 **1 个**页面
- 仅当第1页信息不足、存在明显缺口、或需要交叉验证时，再增加到2或3个
- 不要批量打开多个相似来源

**每次打开后**，展示中间提炼结果：
- 页面标题或 URL
- 3～6 条关键信息点
- 与用户问题的相关性说明

> 如果前1～2个页面已足够回答问题，**立即停止**，进入综合分析。

### Step 4：综合分析 → 结构化报告

在完成有限搜索和有限深读后，先输出**"中间发现"**小节，再给出完整报告。

#### 中间发现
列出搜索和阅读阶段已经确认的关键事实、主要来源、仍不确定的点。格式示例：
```
### 中间发现
✅ 已确认：事实A（来源1）、事实B（来源2）
❓ 待核实：说法C（仅单来源）
🔲 未覆盖：维度D（未找到权威信息）
```

#### 完整报告结构

```
# [课题名称] 深度调研报告

## 概述
（2～3 句话概括核心结论）

## 背景
（课题基本定义、背景信息、为什么重要）

## 现状分析
（关键数据、行业状态、主要玩家/流派）

## 典型案例 / 代表性观点
（具体案例或多方观点，避免同质化来源）

## 发展趋势
（未来走向、可预见的变数）

## 总结
（综合结论与可操作的见解）

## 参考来源
1. [标题](URL)
2. [标题](URL)
...
```

> **元操作检查**：写完报告后自查——搜索≤2次？读页≤3次？如果超了，说明方法有问题。

## ⚠️ 常见陷阱

| 陷阱 | 后果 | 纠正 |
|:----|:----|:-----|
| 一上来就多关键词地毯搜索 | 信息过载，反而找不到重点 | 先精准搜1次，不够再加 |
| 批量打开所有搜索结果 | token 浪费，上下文被噪音填满 | 一次只读1页，读完评估再决定 |
| 追求"穷尽式"检索 | 研究永远做不完 | 够用即可，用户要的是洞察不是数据量 |
| 跳过中间结果直接出报告 | 用户无法干预方向，可能白做 | 每轮展示中间发现，给用户调整方向的机会 |

## 专项 A：开源工具架构深度分析

当需要**理解一个开源工具的设计哲学、核心架构和可吸收的理念**时（而非仅仅是接入 API），走源码优先路线。此流程适用于：评估能否吸纳其设计模式、学习架构思路、判断自部署可行性。

### 分析流程（五层递进）

```
README         → 理解价值主张和功能边界
Docker Compose → 理解系统架构（服务/组件/依赖关系）
核心源码       → 理解引擎/算法设计（不要通读，只读骨架）
SDK            → 理解 API 设计哲学（Python/TS SDK 看接口）
官方 Blog/Docs → 理解设计原则和性能基准
```

#### Layer 1：README 快速扫描

- 项目星数、主要语言、许可证
- 核心功能列表（Feature Overview）
- Quick Start：看最简使用路径
- 问自己：它的核心价值主张是什么？一句话能说清吗？

#### Layer 2：Docker Compose 看架构骨架

不要通读，只看这几行：

```
grep -E "^  [a-z][a-z-]+:" docker-compose.yaml
```

**关键信号：**
- 是否需要外部存储（PostgreSQL/Redis）→ 状态持久化程度
- 是否有独立 worker 服务 → 异步/队列架构
- 是否依赖专有引擎（CDP/TLS 服务）→ 核心技术栈
- 每个服务的 mem_limit → 资源需求

**架构分类：** 单服务 | 微服务 | 有队列的微服务 | 有 worker pool 的

#### Layer 3：源码骨架分析

只读关键文件，不通读：

| 文件模式 | 读什么 |
|---------|--------|
| `src/index.ts` / `main.py` | 路由注册、中间件链、启动流程 |
| `src/routes/` | API 端点列表（看功能边界） |
| `src/controllers/` | 核心业务逻辑入口 |
| 核心引擎目录（scraper/crawler/engine） | **最值钱的部分** |
| 引擎内部的 engines/ 或 strategies/ | 多策略/多引擎设计 |

**读引擎代码时的关键信号：**

```
□ 有没有"引擎列表"或"策略列表"（enum/const array）→ 看有多少种技术方案
□ 每个引擎有没有 quality/priority/score 属性 → 看如何排序
□ 有没有 fallback/builder 模式 → 看如何处理失败
□ 有没有 feature flag 匹配机制 → 看如何按需选引擎
□ 有没有 maxReasonableTime 或类似超时机制 → 看如何控制延迟
```

#### Layer 4：SDK 看接口设计哲学

Python SDK 或 JS SDK 的 client 入口：

- 用户调用的顶层接口（search / scrape / crawl / extract）
- 参数设计（少而合理的必填参数，丰富的可选参数）
- 返回结构（是否标准化的 markdown-first 输出）
- MCP/CLI 支持

#### Layer 5：Blog/Docs 看设计原则

搜官方技术博客的关键字：

```
architecture | design decisions | benchmark | reliability
why we built | lessons learned | our approach
```

### 输出结构

完成五层分析后，输出结构化笔记（可作为技能参考文件存入）：

```
# [工具名] 架构分析与可吸收理念

## 一句话定位
（它的核心价值主张）

## 系统架构
（服务组件图、数据流简述）

## 核心设计模式（最值得吸收的部分）
1. [模式名] — 简述，适用场景
2. ...

## 技术亮点
（具体实现中的精巧设计）

## 可吸收理念（用于我们自己的系统）
- 原则 A：...
- 原则 B：...

## 部署可行性判断
- 自部署：可行/不可行（原因：资源要求/依赖链）
- 云服务替代：有/无（免费额度）
```

### ⚠️ 常见陷阱

| 陷阱 | 纠正 |
|:----|:-----|
| 试图通读全部源码 | 只读骨架，不通读。一读具体实现就陷进去 |
| 只读 README 就下结论 | README 是 marketing，源码才是真实设计 |
| 忽略 docker-compose | 这是最快了解系统架构的地方 |
| SDK 和 API 文档混为一谈 | SDK 看用户视角，服务端源码看实现视角 |
| 只关注功能不关注设计哲学 | "为什么这么设计"比"能做什么"值钱一百倍 |

## 专项 B：外部工具 API 调研

当需要调研一个第三方工具的 API 能力时，常规搜索可能不够——很多 API 文档在登录墙后或藏在 SPA 中。此专项流程适用于：评估新工具能否接入、发现 API 端点、确认认证方式和付费门槛。

### API 调研流程

```
Step 1: 确认工具身份+URL → Step 2: 探测API端点 → Step 3: 发现认证方式 → Step 4: 验证付费门槛
```

#### Step 1：基础发现

先确认工具的名称、类型（Notion-like / 协作平台 / 存储服务等）、官网。尝试以下 URL 模式：

| 探测目标 | URL 模式 |
|---------|---------|
| 开发者文档 | `developer.<domain>` / `docs.<domain>` / `<domain>/developer` |
| 开放平台 | `open.<domain>` / `<domain>/openapi` |
| API 参考 | `<domain>/api` / `<domain>/api/v1` / `<domain>/docs` |
| OpenAPI Spec | `<domain>/openapi.json` / `<domain>/swagger.json` / `<domain>/v3/api-docs` |
| 帮助中心 | `help.<domain>` / `<domain>/help` |

**注意**：中国 SaaS 工具通常使用 `open.<domain>.cn` 或 `<domain>.cn/openapi` 作为开发者入口。

#### Step 2：端点探测

使用 `curl -sIL` 检查 HTTP 状态码来区分存在性与权限：

| 状态码 | 含义 | 下一步 |
|--------|------|--------|
| `200` | 页面存在 | 尝试检查是否为 SPA（查看返回是否含 `<div id="root">`） |
| `401` | 端点存在，需认证 | **这是好信号**——API 路径正确 |
| `404` | 路径不存在 | 换其他路径模式 |
| `405` | 方法不支持 | 端点存在，换 HTTP 方法重试 |

> **SPA 检测**：如果返回 HTML 含 `<div id="root">` 或类似 JS 应用标记，说明是客户端渲染，curl 抓不到实际内容。此时从 JS bundle 中搜与 开发者 相关的关键词（`developer` / `token` / `apiKey` / `oauth`）定位配置。

#### Step 3：认证方式发现

尝试不同的 OAuth2 grant type 来确定工具支持的认证方式：

```bash
# 尝试 client_credentials（最理想，服务器直调）
curl -X POST "<domain>/api/oauth/token" -H "Content-Type: application/json" \
  -d '{"grant_type":"client_credentials","client_id":"...","client_secret":"..."}'

# 尝试 password grant
curl -X POST "<domain>/oauth/token" \
  -d 'grant_type=password&client_id=...&client_secret=...&username=...&password=...'
```

| 返回错误 | 含义 | 对策 |
|---------|------|------|
| `unsupported_grant_type` | 不支持直连 | 需授权码模式(authorization_code)，需要用户浏览器授权 |
| `invalid_client` | client_id/secret 格式不对 | 确认创建应用时的字段名 |
| `400 Bad Request` | 端点存在但参数不对 | 调整参数格式尝试 |

#### Step 4：验证付费门槛

API 功能经常被 gated 在付费计划后：

```bash
# 检查定价页面
curl -sL "<domain>/pricing" | grep -oP '[\x{4e00}-\x{9fff}]+' | sort -u | grep -E '免费|专业|企业|版'

# 直接用 App ID 尝试 OAuth 授权（返回的实际错误会暴露权限问题）
# "当前不支持免费版空间" = 需要付费
# "应用未审核/未上线" = 可能需要提审
```

付费计划中通常标注的 feature：`API访问` / `Open API` / `开发者接口` / `集成能力`。

#### 常见工具 API 特征速查

| 工具类型 | 典型 OAuth 端点 | Token 前缀 | 备注 |
|---------|----------------|-----------|------|
| 飞书系 | `/open-apis/auth/v3/tenant_access_token` | `Bearer` | App ID + App Secret 直换 token |
| Notion 系 | `/v1/oauth/token` | `Bearer` | 需授权码模式 |
| FlowUs/息流 | `api.flowus.cn/oauth/authorize` | `Bearer` | 仅支持 authorization_code，免费版不可用 |

### 调通后的验证清单

```
□ 枚举 API 版本: /api/v1 和 /api/v2 都要试
□ 确认 Token 可用: 请求一个简单端点验证连通性
□ 确认权限范围: 测试 read / write / update 各端点
□ 确认 Rate Limit: 返回头有无 X-RateLimit-* 
□ 确认 Webhook: 检查是否有事件通知能力
□ 确认 SDK: 检查 npm / PyPI 有无官方或社区 SDK
```

### 验证后的工具映射表
|:--------|:-----------|
| 通用搜索 | `web_search` |
| 学术论文 | `arxiv` |
| 博客/RSS | `blogwatcher` |
| 深度阅读页面 | `web_fetch` 或 `vision_analyze` |
| 代码搜索 | `mcp_github_search_code` |
| 模型路由决策 | `task-driven-model-routing`（如何选工具/模型） |

### 专项 C：AI 产品侦察（从视频/描述/文章出发）

当用户说"我看了个视频/文章/tweet，说XX模型/API免费/很强，研究一下"时，不要直接查已知域名——产品可能刚发布，官网域名与名称不一定匹配。此流程用于**从零到一验证一个 AI 产品是否真实存在**。

> 实战案例见参考文件 `references/agnes-ai-api-discovery.md`

#### 侦察流程

```
Step 1: 域名变体扫描 → Step 2: 多语言搜索 → Step 3: 子域名探针 → Step 4: 端点验证 → Step 5: 媒体交叉验证
```

#### Step 1：域名变体扫描

尝试所有常见的域名组合模式：

```bash
# 模式 1: <name>.ai（AI 产品标配）
# 模式 2: <name>.com（商业版）
# 模式 3: <name>ai.com / ai-<name>.com
# 模式 4: <name>-ai.com（带连字符的完整名称）

# 用一个循环批量探测
for domain in "agnes.ai" "agnese.ai" "agnese-ai.com" "agnesai.com" "agnes-ai.com"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://${domain}" --connect-timeout 10)
  echo "${domain} → ${code}"
done
```

**注意：** 404 也可能是真实域名但未配置完成。看网页标题 / 返回内容判断是未配置空页还是明确不相关。

#### Step 2：多语言搜索

中国/东南亚 AI 产品在中文搜索引擎上的曝光度远高于英文：

```bash
# 搜索产品完整名称 + 中文关键词
curl -sL "https://www.bing.com/search?q=<Product+Name>+AI+%E5%85%8D%E8%B4%B9+API" ...
curl -sL "https://www.bing.com/search?q=<Product+Name>+AI+%E5%85%A8%E6%A8%A1%E6%80%81" ...
```

**关键信号 & 来源可信度分级：**

| 来源 | 可信度 | 说明 |
|------|--------|------|
| 量子位 / 机器之心 / 36氪 | ⭐⭐⭐ | 行业头部媒体，报道有事实核查 |
| 知乎专栏 | ⭐⭐ | 可能有官方入驻或深度分析 |
| 新浪财经 / 投资界 | ⭐⭐ | 偏投资视角，确认公司存在 |
| 个人博客 / B站视频 | ⭐ | 需交叉验证 |
| GitHub Trending | ⭐⭐⭐ | 代码已开源 |

#### Step 3：子域名探针

找到官网后，探测常用子域名定位 API 入口和管理后台：

```bash
for sub in "api" "console" "docs" "platform" "dashboard" "developer" "app"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://${sub}.${mainDomain}" --connect-timeout 10)
  echo "${sub}.${mainDomain} → ${code}"
done
```

**子域名到功能的映射：**

| 子域名 | 大概率是什么 | 应对 |
|--------|-------------|------|
| `api.` | API 入口 | 尝试 OpenAI 兼容端点 |
| `console.` / `dashboard.` / `admin.` | 管理后台（API Key 管理） | 通常需登录 |
| `docs.` | 文档站 | 最理想——直接看接入方式 |
| `platform.` | 消费者产品 | 可能有免费试用 |
| `developer.` / `dev.` | 开发者门户 | 注册 API Key 的入口 |

#### Step 4：端点验证

找到 `api.*` 子域名后，尝试 OpenAI 兼容的端点路径：

```bash
paths=("/api/v1/chat/completions" "/v1/chat/completions" "/api/chat/completions"
       "/api/v1/models" "/v1/models"
       "/api/v1/images/generations" "/v1/images/generations"
       "/api/v1/video/generations")

for path in "${paths[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://api.example.com${path}")
  echo "${path} → ${code}"
done
```

**HTTP 状态码判读：**

| 状态码 | 含义 | 行动 |
|--------|------|------|
| `401` | ✅ 端点存在且路径正确——需要 API Key | 确认端点和认证方式无误 |
| `405` | ✅ 端点存在——方法不对（POST 写成 GET） | 换方法重试 |
| `400` | ✅ 端点存在——参数格式不对 | 好信号，继续 |
| `404` | ❌ 路径不存在 | 换其他路径模式 |
| `000`/超时 | 可能无 DNS 或无服务 | 跳过 |

> **核心原则：401 = 好信号。** 只有 API 端点才会返回 401，静态页面返回 404。

#### Step 5：媒体交叉验证

收集至少 2 个独立来源确认产品真实性：
- **技术博客**（量子位/机器之心）：看功能描述和实测
- **投资媒体**（投资界/36氪）：看公司背景和融资
- **知乎/讨论区**：看社区反馈和真实使用体验
- **GitHub**：如开源，检查仓库活跃度和 issue

#### 输出格式

```markdown
## [产品名] API 侦察报告

### 基础信息
| 维度 | 结果 |
|------|------|
| **是否真实** | ✅ / ❌ / ⚠️ 待核实 |
| **母公司** | |
| **API 是否免费** | |
| **认证方式** | |
| **兼容性** | |

### 已验证的端点
| 端点 | 状态 | 用途 |
|------|------|------|
| `/api/v1/chat/completions` | 401（需Key） | 文本 |
| `/api/v1/models` | 401（需Key） | 模型列表 |

### 来源
1. 媒体报道 [标题](url)
2. 官网 [url]
3. 其他

### 待办
- [ ] 注册获取 API Key
- [ ] 实测各模型
- [ ] 性价比对比
```

## 关联技能

- `task-driven-model-routing` — 判断研究任务需要什么模型/工具
- `knowledge-synthesis` — 将研究成果注入知识库
- `arxiv` — 学术论文专项搜索
- `blogwatcher` — 博客文章监控
