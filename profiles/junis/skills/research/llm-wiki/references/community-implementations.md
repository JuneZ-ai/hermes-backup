# Community LLM Wiki Implementations

> Karpathy's LLM Wiki pattern has several community implementations. This reference
> compares the most prominent ones, evaluated through Karpathy's own cognitive framework
> and real-world adaptation cases.

## Repo Overview

| Dimension | Astro-Han/karpathy-llm-wiki | balukosuri/llm-wiki-karpathy |
|-----------|----------------------------|------------------------------|
| Author | Yuhan Lei | Balu Kosuri (JFrog) |
| Target tool | Agent Skills (Claude Code, Codex) | Cursor |
| Schema file | SKILL.md | CLAUDE.md |
| Install | `npx add-skill` | `git clone` |
| Obsidian setup | Manual | Pre-configured `.obsidian/` ✅ |
| Page types | 2 (entities, concepts) | 7 (source/feature/product/persona/concept/style/analysis) |
| Stars | 2,100+ | — |
| First commit | 2026-04 | 2026-04 |

## Karpathy Framework Evaluation

### Astro-Han/karpathy-llm-wiki

| Model | Score | Evidence |
|-------|:-----:|----------|
| Software 3.0 | ✅ | Agent Skills standard — natural language as programming |
| Build to Understand | ⚠️ | LLM writes wiki, human reads. Missing: human should also write |
| Summoned Ghost | ✅ | Uses LLM's summarization/cross-reference abilities appropriately |
| March of Nines | ✅ | Lint system, cascade updates, immutable raw/, conventions |
| Jagged Intelligence | ❌ | Assumes equal LLM competence across all knowledge domains |
| Iron Man Suit | ⚠️ | Depends on usage pattern: questioning+rewriting = suit; dumping only = robot |

### balukosuri/llm-wiki-karpathy

| Model | Score | Evidence |
|-------|:-----:|----------|
| Software 3.0 | ✅+ | Core philosophy is "AI handles everything" — pure Software 3.0 |
| Build to Understand | ❌ | README explicitly says "Don't write wiki pages yourself" |
| Summoned Ghost | ✅+ | 7 page types show nuanced LLM capability mapping |
| March of Nines | ✅ | CLAUDE.md schema, lint, glossary, pre-configured Obsidian |
| Jagged Intelligence | ❌ | Same blind spot: no distinction between LLM-strong and LLM-weak domains |
| Iron Man Suit | ❌ | Default usage pattern leans toward Iron Man Robot (replace, not augment) |

## Which One to Use

| Your situation | Better pick | Why |
|---------------|-------------|-----|
| Using Cursor, want Obsidian out of box | balukosuri | 5-min setup, pre-configured |
| Using Claude Code / Codex CLI | Astro-Han | Agent Skills native |
| Building product/competitor knowledge base | balukosuri | 7 page types fit product work |
| Building personal research/wiki | Astro-Han | Cleaner, more general architecture |
| Want human in the loop (recommended) | Either + modify | Don't blindly automate — rewrite AI drafts |

## Key Caveat (from Karpathy himself)

Imo, the best knowledge base is the one you **write yourself**. LLM can do first-draft processing, but if you never write, you never learn. The "Iron Man Suit" pattern means: AI does rough processing, human does the finishing rewrite. Both repos work great with this pattern — just don't skip the rewrite step.

*Last updated: 2026-05-21*

---

## 实践案例三：Robbin（范凯）5层改造 — 内容创作者适配版

> 与以上两种 GitHub 仓库实现不同，Robbin/FanKai 的改造来自真实使用场景——他发现 Karpathy 原方案对内容创作者「不够用」，于是动手改了三个地方，管理 900+ 篇笔记。

### 角色定位

| 维度 | 说明 |
|------|------|
| 设计者 | 范凯（Robbin），「范凯说AI」公众号/视频创作者 |
| 角色 | 内容创作者 + 软件开发 |
| 工具栈 | Obsidian + OpenClaw + Claude Code |
| 核心痛點 | 知识存下来不产出就是浪费 |

### 三个改造点

#### 改造1：3层 → 5层架构

```
Karpathy 原案：        Robbin 改案：
Raw Sources            Notes/（所有输入的入口）
Wiki                   Knowledge/ + LifeOS/ + Software/
Schema                 Writing/（**新增输出层**）
```

核心洞察：Karpathy 是科研者，知识存下来能查询就够用了。Robbin 是内容创作者，知识必须变成视频/文章才算完整闭环。**加的一个 Writing/ 层是输出层**。

#### 改造2：AI 全权 → 建议+确认

Karpathy 让 AI 全自动读写归档。Robbin 试后遇到问题：AI 把写作方法论塞到 Knowledge（应该放 Writing），把 Chrome DevTools 教程新建文件（已有相关笔记应该合并）。

改法：**AI 先出方案 → 用户十秒确认 → AI 再执行**。规则写进 AGENTS.md。

#### 改造3：单 Wiki → 多目录隔离

投资笔记和育儿心得不应该放一个 wiki。Robbin 按应用领域拆成多个 Obsidian 知识库，各自独立逻辑、互不干扰。

#### 暗线创新：对话存档

Karpathy 没提过的东西——跟 AI 的对话本身也是知识。Robbin 在 Notes/Conversation 目录下保存有价值对话，本视频的底稿就是从跟 Claude 讨论 Karpathy 方案的对话中长出来的。

### 这个案例的价值

| 对比项目 | Karpathy 原案 | Astro-Han 实现 | Robbin 改造 |
|----------|--------------|---------------|-------------|
| 角色 | 科研者 | 通用 | 内容创作者 |
| 层数 | 3 | 3 | 5 |
| 输出层 | 无 | 无 | Writing/ |
| AI 角色 | 全自动 | 全自动 | 建议+确认 |
| 对话存档 | 无 | 无 | Notes/Conversation |
| 是否开箱 | Gist 需自行实现 | 安装即用 | 需自行配置 |

### 对本 wiki 使用者的启示

1. **先确定你的角色**（科研者/内容创作者/工程师/FDE），同一个方案在不同角色手中应该长成不同形态
2. **输出层是关键差异**。如果你的知识最终要变成产品（文章、视频、方案），一定要加输出层
3. **AI 角色取决于你的容错率**。科研场景全自动没问题，内容产出场景需要确认环节
4. **对话是隐形的知识来源**。有价值的对话不存档就是浪费

*Added: 2026-06-05*