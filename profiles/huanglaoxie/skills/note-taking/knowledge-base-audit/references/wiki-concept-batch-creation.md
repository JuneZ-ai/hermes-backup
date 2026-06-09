# Wiki Concept Batch Creation

## When to Use This

After a knowledge base audit reveals a thin concept layer (< 10% of total files, or < 20 concept pages for a 200+ file vault).

## Methodology

### Step 1: Identify Candidate Concepts

Scan the knowledge base for concepts that appear across 3+ modules. Sources:

1. **MOC/index files**: Top-level themes listed in module index files
2. **Cross-module connection tables**: If the architecture documents cross-module links, the concepts in those tables are prime candidates
3. **High-frequency tags**: Tags that appear in notes from different modules
4. **Bridge terms**: Terms that naturally span domains (e.g., "周期" spans economics, history, and cognition)

Good candidates have:
- A precise definition that doesn't change across modules (the *core meaning* is stable)
- Different *applications* in each module (how it's used differs)
- At least 3 notes across different modules that rely on this concept

### Step 2: Batch Create with Consistent Format

Each concept page follows this structure:

```
---
title: Concept Name (Chinese preferred)
tags:
  - wiki
  - cross-module
  - concept
aliases:
  - English alternative
  - Synonym
created: YYYY-MM-DD
type: concept
---

# Concept Name

> One-sentence definition — this is the permanent core meaning.

## Cross-Module Mapping

| Module | Linked Note | Role in That Module |
|--------|-------------|---------------------|

---

*Concept node — bridges knowledge modules*
```

### Step 3: Cross-Module Mapping Conventions

| Binding Type | Example | Notes |
|-------------|---------|-------|
| Direct quote from source | "善战者，求之于势，不责于人" | Use for philosophical concepts from classical texts |
| Framework name | 灰度治理中的"熵减+备胎" | Use for modern management concepts |
| Conceptual variant | 易哲:阴阳 vs 智脑:灰度 | Same root, different branches |

Target: each concept page links to 2-4 module-level notes.

### Step 4: Categorize in Index

Group concepts in wiki/index.md by domain:

| Category | Example Concepts |
|----------|-----------------|
| Philosophical | 灰度, 势, 阴阳, 周期, 无为, 知行合一, 矛盾论 |
| Cognitive/Methodological | 元认知, 系统思维, 闭环, 第一性原理, 逆向思维, 慢即是快 |
| Strategic/Decision | 时机, 取舍, 博弈, 信息不对称, 信号与信任, 安全边际 |
| Business/Wealth | 杠杆, 复利, 护城河, 定位, 熵 |

### Step 5: Wire Up

After creation, update existing high-value notes to include `[[wiki/concept]]` links. Priority:
1. Module index/MOC files (each should link to relevant concept pages)
2. Deep-dive / framework notes (those most likely to be cross-referenced)
3. Fusion notes (they already cross modules, so concepts are natural fits)

### Target Sizing

| Vault Size | Min Concepts | Recommended |
|-----------|-------------|-------------|
| < 100 files | 5 | 10-15 |
| 100-300 files | 15 | 25-35 |
| 300-500 files | 25 | 40-60 |
| 500+ files | 40 | 60-100 |
