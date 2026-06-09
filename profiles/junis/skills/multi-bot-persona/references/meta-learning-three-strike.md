# Meta-Learning: Three-Strike Promotion Rule

> Absorbed from `meta-learning` (2026-05-31 consolidation). Governs what gets promoted to permanent memory or skill — complementary to the design philosophy in the main multi-bot-persona SKILL.md.

## Core Philosophy

**One-shot fix is noise. Third repeat is a pattern. Patterns get promoted.**

### Three-Strike Promotion Rule

| Strike | Condition | Action |
|:------|:----------|:-------|
| **1st** | Correction/error/recurring issue occurs | Note mentally. If significant (>2 min to resolve), save to memory immediately |
| **2nd** | Same pattern in a **different task/context** | Raise internal flag. Start watching |
| **3rd** | Same pattern within **30 days**, across **≥2 distinct tasks** | **Promote** — embed in memory or create/update a skill |

### What Gets Promoted Where

| Pattern Type | Promote To | Example |
|:------------|:-----------|:--------|
| User preference / pet peeve | `memory` (user profile) | "User hates verbose preamble" |
| Workflow correction | The relevant skill's SKILL.md | "Always convert Windows paths to /mnt/c/" |
| Tool quirk / gotcha | `memory` (notes) | "lark-cli needs both drive/drive AND space/document scopes" |
| Reusable technique | Create a new skill | Full workflow for a recurring task class |

### Weaker Signals to Watch

| Signal | What It Means |
|:-------|:-------------|
| You catch yourself about to repeat a past mistake | Pattern internalized but skill/memory not updated |
| User says "you always do X" or "last time we..." | Pattern already struck ≥2 times — promote immediately |
| Same tool produces same unexpected behavior | Environment or config issue to document |
| A question the user asks repeatedly | Blind spot worth noting as a knowledge gap |

### Session Scan at Natural Breakpoints

```
1. Scan memory for recent entries from the last 30 days
2. Check for recurrence: same topic appearing with ≥2 entries?
3. If yes → check threshold: ≥3 across ≥2 tasks?
4. If threshold met → promote (merge into user profile or skill)
5. Clean up transient memory entries now consolidated
```

## Relationship to Multi-Bot Persona

The three-strike rule is how all three bots learn and improve over time:

- **燕青** learns workflow corrections (e.g., "always run lesstoken-web-optimizer first")
- **扫地僧** learns philosophical patterns (e.g., "quote Mao poetry in X context")
- **黄老邪** learns framework evaluation patterns (e.g., "score D4 separately for Chinese tools")

The rule complements the 韬定律元操作原则 — when a pattern strikes 3 times, it's time to change the approach, not just patch the symptom.
