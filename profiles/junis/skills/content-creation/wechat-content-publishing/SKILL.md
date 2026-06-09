---
name: wechat-content-publishing
description: |-
  Write and deliver WeChat public account articles for the user's brand (蛮不错).
  TWO entry points: (A) pre-format WB-generated daily fables for quick publish,
  (B) draft original articles from vault research. Covers the full workflow:
  draft/optimize → format → image prompts → publish checklist → file delivery.
  The user wants a frictionless "一键发送" experience — minimize the steps they need to take.
version: 1.2.0
author: Hermes Agent
license: MIT
tags: [content, publishing, wechat, social-media, series]
trigger_keywords: [公众号, 发文章, 写一篇, 蛮不错, 六韬, 发布, 每日寓言, 寓言, 概念穿故事, 排版, 即梦]
---

# WeChat Content Publishing · 公众号文章发布工作流

## User Preferences (embed these in every article)

| Preference | Value |
|-----------|-------|
| **Account** | 蛮不错 (the user's only public account) |
| **Author name** | 六韬 |
| **Max length** | ≤800 Chinese characters (strict) |
| **Structure** | Series format — split long content into numbered posts |
| **Primary series** | 每日寓言·概念穿故事 (daily fable — weave a management/biz concept into a story, 800-1200 chars) |
| **Images** | User uses 即梦 (Jimeng) for cover images. I provide Chinese prompt text only (user pastes into 即梦 directly). 16:9 cover, match fable tone. NO FAL_KEY needed — just prompt text. |
| **Delivery** | Save files to a Windows-accessible path for easy copy-paste |
| **Tone** | Personal, practical, not salesy — "记录一下" not "卖课" |
| **Call to action** | Light: "转发给一个朋友就是最好的支持" |

## Entry Point Detection

| If user says... | Use Entry... |
|----------------|-------------|
| "帮我排版/处理一下这个寓言" (pastes content) | A — pre-format WB source |
| "写一篇关于X的文章" or no source provided | B — draft from scratch |

## Entry A: Pre-format from WB Source (每日寓言·概念穿故事)

**Trigger**: User pastes WB-generated fable content in chat. WB outputs its daily fable at ~10:00 AM via its own automation (not Hermes cron). User manually copies from WB dialog and sends to me.

### Workflow

1. **Receive source text** — User pastes the WB-generated fable. Read it fully.
2. **Determine next sequence number** — Check `Claw/公众号文章/` for existing files. Format is `NNN-标题.md` where NNN = 001, 002, 003... Increment from highest existing.
3. **Optimize for WeChat** — Keep the core concept→story arc. Tighten to ≤800 Chinese chars. Rewrite opening hook for social media capture rate. PRESERVE the user's original voice — only tighten, don't rewrite their style. The user is 六韬 (six-syllable author persona).
4. **Generate 即梦 cover prompt** — Chinese only (user uses 即梦, a Chinese AI image tool). 16:9 aspect ratio. Visualize the fable's core concept, not literal scene description. Match fable tone (warm/philosophical for management concepts).
5. **Package single file** — Save one self-contained `.md` file to standardized path (see below). Embed image prompts inline at the bottom. The user copies the article body from the "正文" section.
6. **Deliver** — Tell user the Windows path: `C:\Users\18502\WorkBuddy\Claw\公众号文章\NNN-标题.md`. Say: "文件已存到路径：`C:\Users\18502\WorkBuddy\Claw\公众号文章\NNN-标题.md`，正文可直接复制粘贴到公众号后台，封面提示词在文件底部。"

### File Format for Entry A (NNN-标题.md)

```markdown
# 📦 每日寓言·[标题]

## 基本信息

- **标题**：[文章标题]
- **署名**：六韬
- **公众号**：蛮不错
- **字数**：[实际字数]字

---

## 正文（可直接复制到公众号后台）

[文章标题]

[正文段落，≤800字]

*我是六韬，[一句话身份定位]。*
*觉得有用的话，转发给一个朋友就是最好的支持。*

---

## 🎨 封面图提示词（即梦）

> **风格建议**：匹配寓言调性。管理概念类用「暖色调插画」或「水墨意境」；科技概念类用「蓝金配色科技感」

### 封面图（16:9）

```
[纯中文描述，用户直接粘贴到即梦]
```

---

## ✅ 发布前清单

- [ ] 标题复制到公众号
- [ ] 署名改为「六韬」
- [ ] 正文贴入编辑器（注意段间距）
- [ ] 用即梦生成封面图 → 下载保存 → 上传到公众号
- [ ] 预览检查排版
- [ ] 设定时发布
```

## Entry B: Draft from Scratch (original articles)

For when no source exists — write an original piece from vault/research.

### Step 1: Draft
Read relevant vault content, write ≤800 Chinese character article with hook in first paragraph, concrete example (cross-module analysis preferred), series teaser.

### Step 2: Package
Save to standardized path (same directory as Entry A). Same file format but without the 📦 prefix.

### Step 3-5: Same as Entry A steps 5-6

## Sequence Management

- **Next number**: List files in `Claw/公众号文章/`, find highest `NNN-` prefix, add 1.
- **Track published articles**: If user asks, list files in the directory and describe what each covers.
- **Standalone articles**: Each article should make sense for new readers.

## Delivery Path

The user accesses files from Windows. Always save to the WSL mount path, but communicate the Windows path.

- **Save to (WSL)**: `/mnt/c/Users/18502/WorkBuddy/Claw/公众号文章/`
- **Tell user (Windows)**: `C:\Users\18502\WorkBuddy\Claw\公众号文章\`

```
├── NNN-标题.md                ← single self-contained deliverable
```

**NNN format**: 001, 002, 003... always 3-digit zero-padded.

## Article Structure Templates

### Template A: Fable (概念穿故事) — for Entry A
```
Title: <concept-name>的<animal/person>版本 (e.g. 二八法则的狐狸版)

Paragraph 1: Situation — a relatable scenario that introduces a tension/problem
Paragraph 2: Action — a character (animal, historical figure, or ordinary person) faces the problem
Paragraph 3-4: Twist — the concept reveals itself through the story's resolution
Paragraph 5: Reflection — what this means for the reader today
Sign-off: 我是六韬，[一句话身份定位]。
CTA: 转发给一个朋友就是最好的支持。
```

### Template B: Original Article — for Entry B

```
Title: <hook-driven, under 20 chars>

Paragraph 1: Problem/context (the user's real situation)
Paragraph 2-3: What they did (the solution)
Paragraph 4-5: Concrete example (show, don't tell)
Paragraph 6: The realization/insight
Paragraph 7: What's next (series teaser)
Sign-off: Author + CTA
```

## Series Management

- Keep a running list of published articles in `C:\Users\18502\WorkBuddy\Claw\公众号文章\` (WSL: `/mnt/c/Users/18502/WorkBuddy/Claw/公众号文章/`)
- Track which topics are covered to avoid repetition
- Each article should stand alone (new readers can start anywhere)
- Series teaser at the end of each article lists upcoming topics

## Formatting Done vs. Manual User Steps

When delivering the article file, be explicit about what formatting is already applied vs. what the user needs to do manually in the WeChat editor.

| Already in file | User does manually in WeChat editor |
|----------------|--------------------------------------|
| Natural paragraph breaks | Select title text → set to large bold heading |
| `>` for quotes (paste keeps format) | Bold or highlight key sentences (金句) with color |
| `---` for section dividers | Adjust paragraph spacing (paste sometimes collapses gaps) |
| `「」` around concept names | Add any inline images (user uses 即梦 separately) |

Always tell the user: "正文可直接复制粘贴，标题和金句建议在编辑器里加粗改色。"

## Pitfalls

1. **Overwriting the user's voice** — The user has their own style.
2. **Exceeding 800 chars** — This is a hard constraint. Count Chinese characters specifically (not total bytes).
3. **Forgetting images** — Every article needs at least one cover image prompt (Chinese, 即梦-compatible, 16:9). Inline images for key visuals are a nice bonus.
4. **Not communicating the Windows path** — Save to `/mnt/c/Users/18502/...` (WSL path), but ALWAYS tell the user the `C:\Users\18502\...` (Windows path). If you only tell them the WSL path, they won't find the file in Windows Explorer.
5. **Assuming I can publish directly** — I cannot log into WeChat backend. The workflow ends at file delivery.
6. **Fable vs. article confusion** — When user says "帮我排版/处理寓言", use Entry A (pre-format WB source). When they say "写一篇关于X的文章", use Entry B (write from scratch). Don't rewrite a completed fable from scratch — the user already has the content.
7. **即梦 prompt in English** — User uses 即梦 (Chinese AI image tool). Prompts MUST be in Chinese only, not bilingual. Just the concept visualization in natural Chinese.
8. **No automatic publish** — User must manually: copy from file → paste into WeChat editor → add cover image via 即梦 → schedule publish time. The workflow ends at file delivery. Don't assume any publishing automation.
