# FDE Adaptation of Karpathy LLM Wiki

> **FDE (Full-Stack Digital Expert)** — a practitioner who builds AI-augmented knowledge systems
> both for themselves and as a deliverable to enterprise clients.
>
> This is a third role alongside Karpathy's researcher and Robbin's content creator,
> requiring a distinct adaptation of the LLM Wiki pattern.
>
> *Based on: 六韬·认知操作系统 practice, 2026-06-05*

## Role Comparison

| Dimension | Karpathy (Researcher) | Robbin (Content Creator) | FDE (Practitioner) |
|-----------|----------------------|------------------------|-------------------|
| Primary need | Knowledge storage + retrieval | Knowledge → content products | Knowledge → solutions + delivery |
| Output type | Papers, research | Videos, articles, courses | Case studies, frameworks, toolkits, playbooks |
| Output audience | Academic peers | Public audience | Enterprise clients |
| AI autonomy | Full autonomy | Suggest + confirm | Trust + report (routine) / Suggest + confirm (new path) |
| Layer count | 3 | 5 | 5 |
| Output layer name | None | Writing/ | Delivery/ |
| Conversation archive | None | Notes/Conversation (for content) | Conversation Archive (for insight recovery) |
| Vault isolation | Single wiki | Multi-vault by domain | Single vault with layered structure |

## 5-Layer Architecture (FDE Specific)

```
🍂 L1: 01-信息流/ (Input)       ← All incoming material, no classification needed
🌳 L2: 知识模块 (Knowledge)     ← Domain modules with prefix-based classification
🛠️    _工具/ (Tools)           ← SOPs, templates, scripts, agent configs
🌿      生活管理 (LifeOS)       ← Investment, health, contacts (prefix-based)
🎯 L3: Delivery/ (Output)      ← Two tracks: public + enterprise
    ├── 公众号/                 ← Public content (articles, columns)
    └── 企业交付/               ← Enterprise deliverables
        ├── Case-Studies/      ← Client project archives
        ├── Frameworks/        ← Repeatable methodologies
        ├── Toolkits/          ← Reusable deliverable assets
        └── Playbooks/         ← Standard operating procedures
```

**Core principle:** Knowledge is ammunition, not inventory. Every piece of knowledge in the vault must answer "what output does this serve?" — decisions internally, deliverables externally.

## AI Agent Role in FDE Mode

```yaml
AI role: Cognitive co-pilot + method library steward

Routine operations (known pipeline, repeated path):
  → Execute directly, report in one sentence on completion

New path / cross-module / high-impact operations:
  → Present plan + estimated effort → await confirmation → execute → report

Conversation archive (new for FDE):
  → When user says "归档" / "收" / "存" or when valuable cross-module insight emerges
  → Auto-extract key insights → file to 01-信息流/ with status:conversation
  → Update backlinks on related permanent notes
  → One-line report on completion
```

## Multi-Bot Team Structure

The FDE model works best with a multi-agent team rather than a single bot:

| Bot | Role | Owes |
|-----|------|------|
| **Junis** (Orchestrator) | Receive → triage → dispatch → integrate | All complex tasks |
| **燕青** (Executor) | Run scripts, cron, git, file ops | Mechanical work |
| **黄老邪** (Analyst) | Framework analysis, competitive review, research | Thinking work |
| **鲁班** (Craftsman) | Polish, layout, cover design, vault maintenance | Finished output |
| **扫地僧** (Philosopher) | Deep thinking, cross-module bridging, arbitration | Edge cases |

## Dual-Track Output Layer

The FDE's Delivery/ layer has two output tracks that share the same knowledge base:

### Track 1: Public Content (公众号)
- **Purpose:** Build personal brand, share insights, drive OPC
- **Format:** Articles, columns, courses
- **Pipeline:** Knowledge extraction → Draft in Delivery/公众号/草稿/ → Publish → Archive to Delivery/公众号/已发布/
- **Monetization:** Knowledge product (OPC)

### Track 2: Enterprise Delivery (企业交付)
- **Purpose:** Client deliverables, professional services
- **Format:** Case studies, frameworks, toolkits, playbooks
- **Pipeline:** Client engagement → Case-Study in Delivery/企业交付/Case-Studies/ → Framework extraction → Toolkit packaging
- **Monetization:** Service fees
- **Reuse principle:** Each client engagement adds a Case-Study, iterates a Framework, and makes the next client smoother

## Key Differences from Robbin's Adaptation

| Aspect | Robbin (Content Creator) | FDE |
|--------|------------------------|-----|
| Output layer | Writing/ (single track) | Delivery/ (dual track: public + enterprise) |
| Conversation use | Content raw material | Insight recovery + method refinement |
| AI confirmation | Mandatory every time | Only for new paths (routine ops auto-execute) |
| Tool stack | OpenClaw + Claude Code | Multi-bot team (Junis/燕青/黄老邪/鲁班/扫地僧) |
| Knowledge reuse | → Articles/videos | → Case studies → Frameworks → Toolkits → Next client |
| Vault metaphor | Pipeline | Tree + pipeline (dual perspective) |

## When to Use This Adaptation

- User identifies as a practitioner/consultant/FDE rather than researcher or pure content creator
- User serves multiple audiences (public + enterprise)
- User needs repeatable deliverable assets (frameworks, toolkits)
- User is building knowledge systems for both self-use and as a client service
- The "in the process of building, learning" (干中学) pattern applies

*Written: 2026-06-05*
*Source: 六韬·认知操作系统 practice, derived from session on Robbin(FanKai) vs Karpathy vs FDE adaptation*
