# LLM Wiki Analysis (2026-06-05)

## What It Is

An open-source desktop app (Tauri v2 + React 19) that converts personal
documents into an interlinked, self-building Wiki. Based on Karpathy's
abstract methodology, with significant extensions.

## First Principle

> Knowledge should be COMPILED into human-readable Wiki pages, not
> re-derived on every query.

This is the anti-RAG stance: compile once, update incrementally.

## Key Design Decisions

### Two-Step Chain-of-Thought Ingestion
Split material processing into two sequential LLM calls:
1. Analyze -> structured analysis (entities, concepts, contradictions)
2. Generate -> Wiki pages from the analysis, not from raw material
SHA256 incremental cache skips unchanged files.

### Four-Signal Relevance Model
Source overlap (x4.0) gets the highest weight, followed by direct links
(x3.0), Adamic-Adar (x1.5), and type affinity (x1.0). Source overlap
is the key insight: pages sharing the same source document are
strongly related.

### Graph Insights Engine
- Surprising connections: cross-community/cross-type edges
- Knowledge gaps: isolated pages (deg <= 1), sparse communities
- Auto Deep Research: generate search topics from gaps

### Other Notable
- Purpose.md as direction anchor (separate from Schema.md's structural rules)
- Asynchronous audit queue (human-in-loop, non-blocking)
- Context budget: 60/20/5/15 allocation for retrieval
- Chrome extension with Mozilla Readability.js extraction
- Obsidian-compatible markdown output

## What We Adapted

| Feature | Our implementation | Priority |
|---------|--------------------|----------|
| Source overlap | source_note + 01-infofile wikilinks -> add [[wikilinks]] | P0 [done] |
| Two-step ingestion | Pre-analysis -> Review -> Generation workflow | P0 [done] |
| Graph insights | Degree/density/bridge/potential-link scan | P1 [done] |
| Context budget | 60/20/5/15 retrieval prompt template | P1 [done] |
