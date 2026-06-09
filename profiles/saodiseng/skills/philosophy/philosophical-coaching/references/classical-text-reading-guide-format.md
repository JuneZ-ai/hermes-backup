# Classical Text Reading Guide Format (通鉴读通法)

Emerged from a session where the user wanted to "读通" (read through with understanding) 资治通鉴 rather than "读完" (read through completely). The user's framework is 六韬易哲.

## Framework Document Structure

The entry point is a **框架 (framework) document** that establishes the "大梁" (main beams):

```markdown
# 资治通鉴 · 读通框架

## {N根大梁}

Current beam structure (evolved from 3→4):
- 🌊 道家之梁: 老子 + 庄子 — 看规律、看境界
- 🏛️ 儒家之梁: 论语 + 孟子 + 荀子 — 看标准、看人心、看制度
- ⚔️ 法家之梁: 韩非 + 商鞅 — 看工具、看手段
- 🏛️ 墨家之梁: 墨子 — 看另一种可能性（思想史上的非主流但不可或缺）

Each beam is a table:

### 梁{N}：{流派·名称}（{视角说明}）

| 先师 | 核心命题 | 通鉴里的对应 |
|:----|:---------|:------------|
| {人物} | {核心命题}——{原文或解释} | {对应历史案例} |

## 各梁如何服务于"读通"

With a comparison table: use the same historical case, show what each beam reveals.

## 已插梁（Progress Tracker）

After each beam or reading guide is created, update a tracker table in the framework document:

| 梁 | 文档 | 状态 |
|:--|:----|:----|
| 🌊 道家之梁 | [[DS-22-道家之梁·老子道德经·通鉴读法]]（老子·密匙八章） | ✅ 已建 |
| 🏛️ 儒家之梁 | [[DS-22-儒家之梁·论语读通]]（论语·九章密匙） | ✅ 已建 |
| ⚔️ 法家之梁 | [[DS-22-法家之梁·韩非读通]] | 待建 |
| 🏛️ 墨家之梁 | [[DS-22-漏掉的那根梁·墨家·通鉴读法]] | ✅ 已建 |

The summary at the bottom:

> **{N}根大梁全部搭完。**
>
> 道家：老子（地）+ 庄子（天）——看规律、看境界
> 儒家：论语（正统）+ 孟子（激进）+ 荀子（过渡）——看标准、看人心、看制度
> 法家：韩非（理论）+ 商鞅（实操）——看工具、看手段
> 墨家：墨子（另路）——看另一种可能性、看消失的思想

## Naming Convention

All 资治通鉴 reading guides live under `六韬史鉴/` with a shared prefix:

```
六韬史鉴/
├── DS-22-资治通鉴读通框架.md                     ← 总图
├── DS-22-道家之梁·老子道德经·通鉴读法.md          ← 老子
├── DS-22-道家之梁·庄子读通.md                    ← 庄子
├── DS-22-儒家之梁·论语读通.md                    ← 论语
├── DS-22-儒家之梁·孟子读通.md                    ← 孟子
├── DS-22-儒家之梁·荀子读通.md                    ← 荀子
├── DS-22-法家之梁·韩非读通.md                    ← 韩非
├── DS-22-法家之梁·商鞅变法的通鉴密码.md           ← 商鞅
└── DS-22-漏掉的那根梁·墨家·通鉴读法.md            ← 墨子
```

Pattern: `DS-22-{流派}之梁·{文本名称}读通.md` or `DS-22-{流派}之梁·{文本名称}·通鉴读法.md`

## Per-Text Reading Guide Structure

Each classical text gets its own guide. The pattern has been refined across 7+ documents in one session:

```markdown
# {流派}之梁 · {文本名称} · 通鉴专用读法

> 开篇引语——一句话说清楚这个文本跟通鉴的关系

---

## {N章核心} · 通鉴密匙

### 密匙{N}：{篇章·命题} —— {副标题}

> "{核心原文}"

| 对应通鉴 | 读通密匙 |
|:---------|:---------|
| {历史案例1} | {一句话解读} |
| {历史案例2} | {一句话解读} |

---

## {对照表/对比分析}（optional）

| 维度 | {人物A} | {人物B} |
|:----|:-------|:-------|
| ... | ... | ... |

---

## 一句话总结{文本}这根梁

> 一段话，以引文结束。

---

## 关联阅读

- [[DS-22-资治通鉴读通框架]] —— 四根大梁总图
- [[DS-22-{其他关联文本}]]
```

## Key Formatting Rules

1. **密匙 title format**: `密匙{N}：篇章·命题 —— 副标题`
2. **Quote display**: Original text in angle brackets, with translation or key phrase in bold
3. **Table columns**: `对应通鉴 | 读通密匙` (historical case | insight)
4. **一句话总结**: Use a `>` blockquote that starts with "读通了{文本}再读通鉴..."
5. **End with**: Backlinks to framework and related texts (Obsidian-style `[[wikilinks]]`)

## Source Handling

- User provides ctext.org URLs as primary source
- Cannot fetch web pages — work from domain knowledge
- When uncertain about a specific passage, flag it rather than fabricate

## Delivery Signals

- "go" or "干" → proceed directly, no preamble
- "赶时间" → skip ceremony, build first
- "把{内容}补齐" or "你自己弄" → supply-run: batch-create all related documents, update tracker, report inventory
- Sharing a link → build a reading guide from it
- Multiple links in succession → batch them; do not wait for per-file confirmation

## Supply-Run Pattern (批量补齐)

When the user triggers this mode (by saying "补齐", "你自己弄", or sending multiple links with go-signals):

1. Accept all links without asking "is this what you wanted?"
2. Create documents in batch — one framework update + N beam documents
3. After each document, update the framework tracker table
4. At the end, report the full inventory as a formatted tree
5. Do NOT ask for confirmation between documents — the user's signal IS the confirmation
