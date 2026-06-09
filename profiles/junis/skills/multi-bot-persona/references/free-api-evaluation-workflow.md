# Free AI API Evaluation Workflow

> 2026-06-06 首次实践（Agnes AI AGNese-2.0 评估）。适用于用户发现新免费AI工具后要求"研究看看"的场景。

## 流水线

```
① 用户体验/视频/帖子 → ② Junis初筛 → ③ 黄老邪深度调研 → ④ 燕青技术验证 → ⑤ 鲁班内容产出 → ⑥ 扫地僧校验 → 交付
```

## 各工序详解

### ① Junis初筛（5-10min）

用户丢来链接/视频/截图，先做第一轮快速判断：

- **域名存活检查**：`curl -sL <域名> -o /dev/null -w "%{http_code}"`
- **搜索验证**：Bing/DuckDuckGo 搜"公司名+API+免费"，看有没有媒体报道
- **是否有官网**：确认公司真实存在，排除纯营销号/山寨项目

**交付物**：一句话结论（"这是真的" / "可能是假的，因为..."）+ 基础的 URL 清单

### ② 黄老邪深度调研（交给 delegate_task，web+terminal 工具集）

当初筛确认"值得追"时，派黄老邪做深度调研：

- 找到官网/API文档/控制台入口
- 确认模型名称、端点格式、认证方式
- 找到媒体/社区评价（知乎、量子位、新浪等）
- 评估：和同类产品比有没有真优势？免费是 Feature 还是 Marketing？
- 摸清潜在风险：Rate Limit、隐藏收费（超出后）、服务稳定性

**常见端点路径探测顺序**：
```
/v1/chat/completions, /api/v1/chat/completions, /api/chat/completions
/v1/models, /api/v1/models
company.com/api, api.company.com, console.company.com, platform.company.com
```

**域名探测技巧**（Agnes AI 实战经验）：
- 视频/文章里提到的域名（`agnes.ai` / `agnese.ai`）可能是已失效或不准确的
- 用 Bing 中文搜索（`公司名+免费+全模态`）比英文搜索更有效——中文科技媒体（量子位/知乎/博客园/新浪）是第一批覆盖的
- Bing 搜索结果从原始 HTML 中提取：`curl -sL "https://www.bing.com/search?q=关键词" -H "User-Agent: ..." | sed 's/<[^>]*>//g'`
- 找到正确域名后，子域名探测：`api.`, `console.`, `platform.`, `docs.`
- **ChatGPT已验证的端点不做数**——如果 AI 说某个域名存在，必须亲自 curl 验证。AI 会编造不存在的域名（幻觉）

**认证方式探测顺序**：
1. `Authorization: Bearer <key>`（OpenAI 兼容标准 — 最常用）
2. `x-api-key: <key>`（AWS API Gateway 风格）
3. URL query param：`?key=<key>` 或 `?api_key=<key>`
4. 响应码语义：`401` = 需要认证，`invalid or expired token` = 格式对但 key 无效，`missing or invalid authorization header` = header 格式不对

**控制台登录方式探测**：
- 检查 HTML 中的 `GoogleOAuthProvider` / google 相关 JS 判断是否支持 Google 登录
- 检查后端 API 路径：`/api/auth/github` `/api/oauth/github` 返回 200 则表示后端支持 GitHub OAuth
- 如果是 Vue.js/Next.js SPA，无法通过 curl 完成 OAuth 流程——需要浏览器或 headless automation

**交付物**：结构化调研报告（表格 + 结论）

### ③ 燕青技术验证

拿到 API Key 后：

1. **认证测试**：试着三种模式（Bearer Token / 无前缀 / api-key header）
2. **模型列表**：`/api/v1/models` 看返回了哪些模型
3. **文本测试**：`/api/v1/chat/completions` 简单对话
4. **图像/视频测试**：对应端点按需测试
5. **质量评估**：生成结果是否满足"可发布"标准

**交付物**：实测结果 + 截屏/输出样例

### ④ 鲁班内容产出

把调研+实测结果转化成可交付的内容：

- 公众号文章（署名六韬，800字内）
- 知识库笔记（结构化归档）
- 教程/测评

**交付物**：最终成品

### ⑤ 扫地僧校验（可选）

涉及开放性判断/哲学争议时启用。

## Key 无效时的应对流程

如果用户提供的 API Key 被拒（`invalid or expired token`）：

1. **先排查问题范围**：是 Key 格式不对、端点不对、还是 Key 根本没激活？
2. **定位到控制台**：告知用户需要去 console/dashboard 页面用 OAuth 登录后手动创建 Key
3. **如果用户不想/无法注册**：尊重决定，切换到内容产出模式（鲁班）——把调研结果直接写成文章/笔记
4. **如果用户坚持让某 Bot 处理**：服从指派。如指派对象不适合该任务，先执行，干不了再如实汇报

> **2026-06-06 教训**：用户两次提供 Key 都无效→用户放弃注册→转鲁班出内容。避免在这个阶段反复劝说用户注册，尊重放弃决策。

## 注意事项

- **Key无效常见原因**：还没在控制台激活、格式不对、API端点猜错了、该服务还没正式上线
- **"无限期免费"的红旗**：和常规免费API一样——"无限期"取决于公司资金能烧多久。历史教训：不少AI公司开始免费，后来收费或关停
- **用户偏好**：用户喜欢先给结论再给细节，不说"我觉得"，说数据
- **Bot指派**：如果用户明确说"让XX接入"（如"让鲁班接入"），尊重指派不质疑
- **放弃也是结果**：技术接入遇到障碍且用户选择放弃时，把已有调研/内容成果归档，不白做
