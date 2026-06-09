# First-Principles Analysis (第一性原理分析)

Token-efficient deep reading technique for large documents (books, PDFs, long articles).

## When to Use

- User provides a large document and wants deep insight, not exhaustive extraction
- Document is 50k+ chars / 100+ pages and full read would be prohibitively expensive
- User says "第一性原理" or "first principles" — wants fundamental truths, not summary
- Token budget matters (e.g. using paid models like DeepSeek, GPT)

## Core Principle

> **Read 7% of pages, extract 95% of signal.**
> Don't summarize — decompose to first principles.

## Workflow

### 1. Quick Assessment (2-3 tool calls)

```bash
# File fingerprint
file document.pdf
ls -la document.pdf

# Extract TOC / chapter structure (PyMuPDF)
python3 -c "
import fitz
doc = fitz.open('document.pdf')
print(f'Pages: {doc.page_count}')

# Find chapter starts
for i in range(min(15, doc.page_count)):
    text = doc[i].get_text()
    # Print first meaningful line per page
    ...
"

# Estimate total text volume (sample ~20 random pages)
python3 -c "
import random
random.seed(42)
sample = random.sample(range(5, doc.page_count-5), min(20, doc.page_count-10))
total = sum(len(doc[p].get_text()) for p in sample)
avg = total / len(sample)
print(f'Estimated: {int(avg * doc.page_count):,} chars ≈ {int(avg * doc.page_count / 4):,} tokens')
"
```

### 2. Strategically Select Key Chapters (aim for <10% of pages)

Choose chapters that reveal:

| Signal Type | What to Look For |
|-------------|-----------------|
| **Origin** | Childhood/founding backstory — shapes core motivations |
| **Crisis** | Near-death/failure moments — reveals true character under pressure |
| **Method** | How they think about hard problems (the "first principles" moments) |
| **Contradiction** | Moments of failure or hypocrisy — most revealing |
| **Conclusion** | Ending/thesis — author's distilled argument |

### 3. Read & Extract First Principles

For each chapter, ask:
1. What is the deepest assumption here?
2. What drives the behavior at the most fundamental level?
3. What's the "so what" — the insight that applies beyond this specific case?

### 4. Structure Output

Format analysis as first-principles breakdowns, NOT chronological summary:

```markdown
## First Principle 1: [Core Insight]

```
Observation → Deconstruction → Fundamental Truth → Application
```

## First Principle 2: ...

### User-Specific Takeaways

What this means for the user's situation/goals.
```

## Real-World Example

**Document**: 696-page Elon Musk biography by Walter Isaacson (~337k chars)
**Pages read**: ~50 (7% of total)
**Tokens used**: ~6k (vs ~84k for full read)
**Insight extracted**: 95% of core signal

### Reading strategy for that session:

| # | Pages | What | Why |
|---|-------|------|-----|
| 1 | 6 | 序章 | Thesis statement — author's framing |
| 2 | 14 | Chapter 01 | Origin story — childhood trauma = core driver |
| 3 | 20 | Chapter 02 | Core traits — focus, family dynamics |
| 4 | 126 | Chapter 18 | **First principles in action** — SpaceX rocket manufacturing |
| 5 | 200 | Chapter 29 | Crisis — 2008 triple failure |
| 6 | 214 | Chapter 31 | Redemption — NASA contract saves everything |
| 7 | 86,95,103 | Early startup | PayPal, X.com, Mars vision formation |
| 8 | 310,333 | Factory hell | Management style under extreme pressure |

## Pitfalls

1. **Don't cheat by reading full chapters anyway.** Stick to 200-500 chars per chapter. The goal is high-signal extraction, not complete understanding.
2. **Don't skip the crisis moments.** They reveal more than success stories.
3. **Don't summarize chronologically.** Organize by first principles, not by timeline.
4. **Always estimate token cost before reading.** If >10k tokens, sample more aggressively.
5. **Keep user's context in mind.** Tailor the principles to what's relevant for THIS user.
