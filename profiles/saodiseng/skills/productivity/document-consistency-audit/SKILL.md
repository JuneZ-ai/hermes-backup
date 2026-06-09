---
name: document-consistency-audit
category: productivity
description: Audit structured documents for logical consistency, cross-module coherence, terminology alignment, and data integrity. Includes a three-tier issue categorization framework and systematic fix workflow.
---

# Document Consistency Audit (文档逻辑闭环校验)

## When to Load

The user asks you to "审核" (audit/review), "检查一致性" (check consistency), "逻辑闭环" (logical closure), "帮我看一下这份文档" (review this document), or similar. Load this skill **before** reading the document — the four-pass methodology guides how you read.

## Core Principle: Diagnose First, Fix Second

Read the full document once before touching any edit. Resist the temptation to fix as you spot problems — you'll miss cascading issues. Finish all four diagnostic passes, then plan and execute fixes.

---

## The Four Diagnostic Passes

### Pass 1: Cross-Module Consistency

Verify that concepts defined in one section are used identically everywhere else:

| What to Check | What to Look For |
|---------------|-----------------|
| **Metric/equation definition** | If a formula has variables (e.g. `健康度 = A × B × C`), does every section reference the same variable names and units? |
| **Structural mapping** | If you show a diagram (3-layer tree) and a model (5-layer architecture), does every layer in one have a clear counterpart in the other? **Incompatible layer counts** are the most common trap. |
| **Data flow integrity** | If section A defines an ingress format (e.g. 7-field JSON), and section B defines the storage layer, does the ingress format actually map to what storage accepts? **Domain value lists must match.** |
| **Role vs infrastructure** | If a component is defined as an architectural layer (e.g. "包打听" sits below L1), is it also listed as an agent/role elsewhere? That's a drift signal — pick one identity. |
| **Architectural completeness** | Are there obvious enterprise concerns (information security hierarchy, compliance, access control, data sovereignty) that the document's target audience will expect but the document completely fails to address? **This is the most valuable kind of find** — not a mistake in what's written, but a hole the reader will spot. When the user corrected you on a missing concern, record it as a future checklist item. |

### Pass 2: Terminology Drift

Watch for the same concept wearing different names in different sections:

- `suggested_domain` values in the data schema vs actual storage categories in the architecture section
- Package names vs applicable team-size ranges vs listed delivery timelines
- "个人版" mentioned in one table but absent from pricing page
- Layer names that shift between sections (e.g. "沉淀层" vs "存储层" used interchangeably)

### Pass 3: Data Boundary Integrity

Numbers that must add up:

- **Team sizes** — do the recommended ranges in the "purchase guide" table exactly match the package definitions? No gaps or overlaps between tiers.
- **Pricing scopes** — when comparing against competitors, does the baseline team size actually match the cheapest package shown? Using an undersized package to win a price comparison is a credibility landmine.
- **Dates and versions** — last-updated timestamps, version numbers, reference links.

### Pass 4: Structural Integrity

- Does the Table of Contents match the actual section headers and numbering?
- Are all sections referenced in the text actually present?
- Are section numbers sequential with no gaps?

---

## Issue Categorization (Three Tiers)

| Tier | Label | Criteria | Fix Priority |
|------|-------|----------|-------------|
| 🔴 | **硬伤级** | Customer sees it → loses trust. Pricing fudged, architecture mismatch, data path broken. | Fix before presenting. |
| 🟡 | **表层裂缝** | Doesn't break the deal but makes you look sloppy. Poetic metrics you can't compute, layers you can't explain, processes you claim are critical but never detail. | Fix for v1.1 or before client delivery. |
| 🟢 | **小处疏漏** | Cosmetic. Date stamps, missing caveats, formatting. | Fix when you touch the file. |

---

## Fix Execution

1. Use `todo()` to plan all fixes — one todo item per change. This prevents losing track.
2. Use `patch()` with `mode='replace'` for each fix. Ensure `old_string` is unique by including surrounding context lines.
3. After each patch, verify the fix didn't introduce new inconsistencies in other sections (cross-section ripple check).
4. When done, re-read the affected sections to confirm logical closure. Don't assume a green diff means correct semantics.

---

## Pitfalls

- **ASCII art is fragile.** Modifying a multi-line diagram with `patch()` is error-prone and the diff is almost invisible on review. Prefer adding a **mapping table or note below the diagram** rather than redrawing the art itself.
- **One fix can break another.** Fixing the domain mapping (edit A) may make the confirmation example (edit B) inconsistent. After every edit, check all cross-references to the changed value.
- **Don't fix while diagnosing.** The temptation is to "just fix that one obvious thing" mid-read. You'll miss cascading issues. Finish all 4 passes first.
- **Preserve the marketing soul.** When a slogan is ambiguous (e.g. "采集不思考"), rephrase to clarify instead of killing the slogan. The face value is often a feature, not a bug.
- **Pick the right baseline for comparisons.** If you reposition a pricing table (e.g. from 20-person to 15-person baseline), every competitor price that scales per-seat must be recalculated. Platform-level prices (扣子, Dify) may not scale linearly — note this explicitly.

---

## Reference Files

- `references/fde-audit-example.md` — worked example from the FDE 第二大脑企业交付框架 audit, showing the four passes applied in practice, with before/after detail per tier.
