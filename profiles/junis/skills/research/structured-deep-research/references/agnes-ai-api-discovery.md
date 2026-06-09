# Agnes AI API 侦察记录

> 2026-06-06 从用户提供的视频描述出发，验证并定位 Agnes AI 全模态免费 API。

## 触发来源

用户分享了一段视频内容，描述 Agnes AI 公司推出了 AGNese-2.0 全模态模型（文本/图像/视频）且 API 无限期免费。

## 侦察流程

### Step 1：域名探测

尝试了域名变体以定位真实官网：

| 域名 | 结果 | 说明 |
|------|------|------|
| agnes.ai | 404 | 命名空间占用 |
| agnese.ai | -> atom.com | 域名交易市场 |
| agnesai.com | 空页 | 未配置 |
| agnes-ai.com | ✅ 200 | **真实官网**（Next.js） |

### Step 2：中文搜索（Bing）

搜索 "Agnes AI 免费 全模态" 发现大量中文媒体报道：
- 量子位（QbitAI）— 5天前报道
- 知乎专栏 — 全球AI Lab前十分析
- 新浪财经 — 全模态API免费发布
- 博客园 — 东南亚AI赛道分析
- 投资界（pedaily.cn）— 行业分析

**关键信息**：母公司是新加坡 Sapiens AI。

### Step 3：子域名探测

```
console.agnes-ai.com → ✅ 200（"Agnes后台系统"，Vue.js SPA）
platform.agnes-ai.com → ✅ 200（"Agnes" 消费者应用，Next.js）
api.agnes-ai.com → ✅ 200（API 入口）
docs.agnes-ai.com → 000（无 DNS）
```

### Step 4：API 端点验证

测试 OpenAI 兼容端点：

```bash
# 无认证 → 明确错误："missing or invalid authorization header"
curl https://api.agnes-ai.com/api/v1/models
# 返回: {"code":"000501","message":"missing or invalid authorization header"}

# 假 Token → 明确错误："invalid or expired token"  
curl https://api.agnes-ai.com/api/v1/chat/completions \
  -H "Authorization: Bearer test-key"
# 返回: {"code":"000501","message":"invalid or expired token","data":{"trace_id":"..."}}
```

**结论**：端点在 OpenAPI 规范路径上，需要 Bearer Token 认证。

### 验证的 API 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/v1/chat/completions` | POST | 文本生成（Agnes-2.0-Flash） |
| `/api/v1/models` | GET | 模型列表 |
| `/api/v1/images/generations` | 推测 | 图像生成（Agnes-Image-2.0-Flash） |
| `/api/v1/video/generations` | 推测 | 视频生成（Agnes-Video-2.0） |

## 关键结论

| 维度 | 结果 |
|------|------|
| **是否真实** | ✅ 确认真实 |
| **母公司** | Sapiens AI（新加坡） |
| **API 免费** | ✅ 已宣布无限期免费 |
| **认证方式** | Bearer Token（console.agnes-ai.com 生成） |
| **兼容性** | OpenAI API 格式 |
| **质量评估** | 待实测算（需 API Key） |

## 待办

- [ ] 在 console.agnes-ai.com 注册账号（Google 登录）
- [ ] 生成 API Key
- [ ] 实测三种模型的接口和质量
- [ ] 与 DeepSeek 等已有模型进行性价比对比
