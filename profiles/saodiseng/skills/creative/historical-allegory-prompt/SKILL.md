---
name: historical-allegory-prompt
title: Historical Allegory Prompt Writing (借古讽今)
description: Write effective AI prompts for Chinese social media storytelling content that uses historical allegories to comment on modern issues (借古讽今). Covers persona design, narrative structure, style absorption, and calibration.
tags: [prompt-engineering, content-creation, chinese-writing, storytelling, wechat-public-account]
---

# Historical Allegory Prompt Writing (借古讽今)

Use when the user asks you to design, review, or optimize a prompt for AI-generated narrative content in Chinese — especially content that uses ancient/historical stories to reveal modern social rules.

## Core Pattern: 六段叙事结构

The fundamental architecture for 借古讽今 storytelling prompts:

| # | Section | Function | Constraints |
|---|---------|----------|-------------|
| 1 | **现实钩子** (Reality Hook) | Present a modern problem/dilemma the reader faces | ≤100 words, one concrete scene, no theory. Reader's first reaction: "That's me." |
| 2 | **过渡桥** (Transition Bridge) | One sentence to transport the reader from modern story to ancient setting | No explanation, no preamble. E.g. "同样的事，一千年前就发生过。" |
| 3 | **借古** (Historical Story) | Relive the same dilemma in an ancient setting | Use real dynasties/people. Characters speak modern language (时空错位 humor). Dialogue-driven. |
| 4 | **转折** (The Turn) | Reveal the modern name of this phenomenon | Phrase: "这事儿，其实有个名字。" Then give the concept name. One sentence only. |
| 5 | **讽今** (Rule Reveal) | Explain the unchanging mechanism | Three sub-questions: (1) What rule runs this? (2) Why does it still exist? (3) Why can't ordinary people see it? All vernacular. |
| 6 | **破局** (Solution) | Give actionable paths forward | 3 items: mindset / action / strategy. No despair, no cynicism. |

## Persona Design (老爷子)

The "老爷子" (old grandpa) narrator needs a concrete backstory — not just a function. Key ingredients:

```
Background: 70+, worked in government writing documents for 30 years (县委大院/宣传部).
Saw how things really work underneath the official documents.
Occupation history lends him credibility — he's been inside the system.
Current life: tea house in the afternoon, an old book, a pack of cigarettes.
He never says "when I was young" — but you know he's seen it.
```

The user's real-life prototype for this character: **郑佳明** — 1949年生, 北大历史系, 曾任省委宣传部副部长→省社科联主席→《雍正王朝》总监制→历史学教授. "既在红墙里待过，又能站在墙外讲清楚墙里头是怎么回事的人".

### Pitfalls
- **致命的**：给角色一个功能（"认知观察者"）但不给出身（"从哪来的"）。读者不认识这个人，不会信他。
- **不要** 把角色写成年轻人/互联网从业者/成功学讲师 — 老爷子的说服力来自"经历过但不炫耀"。

## Style Absorption (Not Mimicry)

When your prompt wants to absorb multiple writers' styles, **do NOT give the AI their signature catchphrases**. Doing so produces patchwork imitation:

| Writer | Absorb this capability | BAN these patterns |
|--------|----------------------|-------------------|
| 刘震云 | Everyday details carrying large structures; small characters revealing big systems | "话说回来……" "事情往往不是事情本身……" |
| 易中天 | Rhythmic pacing, strong rhetorical questions, 评书感 | "这就有意思了" "问题出在哪儿呢" |
| 王朔 | One sentence to puncture pretense; say "破" the complex | Copying his Beijing accent or 痞气 |
| 罗翔 | Explain theory through life scenes first | Definition openings, academic terms |
| 余华 | Restrained narration generating force; quiet language for shocking reality | Sloganeering, emotional manipulation |
| 冯唐 | Ultra-short lines as cognitive conclusions, screenshot-worthy | Oily/lecturing tone |

### Special additions for 借古讽今:
- **黑色幽默** (Black Humor): Comes from the gap between "体制的荒谬" (systemic absurdity) and "个人的清醒" (individual clarity). Not jokes — things that make you laugh, then realize you're laughing at yourself.
- **借古讽今** (Historical Allegory): Strip dynasty names and official titles — the skeleton is identical to today. Don't say "暗讽", just place the story in a real dynasty. Readers connect the dots themselves.

## 金句 System (Forced)

- **Body quotes**: 3-5 sentences, ≤20 chars each, screenshot-worthy. Best when pulled from the historical story (古今互文).
- **Ending quote**: 1 sentence, ≤15 chars. Makes the reader put down the phone and stare for two seconds.

## Title Directions (Pick One)

1. **借古讽今型**: 《北宋的"公务员"也在卷考课》
2. **荒诞反差型**: 《恭喜你，终于忙成了可替代的人》
3. **规则揭示型**: 《真正决定命运的，从来不是能力》

## Calibration Mechanism

After first output, user says "可以" or "不够". If "不够", adjust exactly once in the specified direction:

- **不够锋利** → peel another layer of satire
- **不够幽默** → find more contrast between ancient and modern
- **不够具体** → write the "rule" as something tangible
- **太啰嗦** → delete all adjectives, keep only nouns and verbs

## Output Constraint

Output ONLY the final article. **Do not output**: structure analysis, drafting process, title options, multiple versions.

## Cover Image Prompt Rule

Output only the prompt text (English). **Do not generate images**. Must include: 1 core character, 1 scene showing ancient-modern conflict, 1 symbolic metaphor, Chinese ink-wash style, 16:9, ample white space, calligraphy title centered.

## Trigger

Load this skill when the user:
- Asks you to write/optimize a prompt for Chinese storytelling content
- Mentions 借古讽今, 老爷子讲故事, or historical allegory content
- Asks about WeChat public account (公众号) content generation
- Wants to create a narrative persona for content generation
- Asks about prompt engineering for Chinese social media
