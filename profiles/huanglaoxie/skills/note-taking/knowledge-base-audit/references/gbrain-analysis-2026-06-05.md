# GBrain Analysis (2026-06-05)

## What It Is

A production-grade brain layer built by Garry Tan (YC CEO) to run his
personal AI agents. 146,646 pages, 24,585 people, 5,339 companies.
Hybrid search + knowledge graph + synthesis layer in one box. Multi-user
federated with OAuth scope-gated access.

## First Principle

> Knowledge should be RETRIEVED + SYNTHESIZED into an answer with
> gap analysis, not served as raw chunks.

This is the anti-search-engine stance: the brain reads the pages for you
and writes the answer, including what it doesn't know.

## Key Design Decisions

### Synthesis Layer with Gap Analysis
`gbrain think` returns a synthesized answer with explicit citations and
an honest note on what the brain doesn't know yet. The gap analysis is
the differentiator: tells you when a page is stale, when a claim is
uncited, when two pages contradict each other.

### Typed Edges (Zero LLM Calls)
Not just [[wikilinks]] but typed edges: works_at, founded, invested_in,
attended, advises, mentions. Pure pattern matching on wikilink syntax.
Benchmarked: P@5 49.1%, R@5 97.9% on 240-page corpus, +31.4 points P@5
over vector-only RAG.

### Dream Cycle (24/7 Cron Enrichment)
Automatic overnight maintenance: dedup people pages, fix citations,
score salience, find contradictions, prep tomorrow's tasks. "I wake up
smarter than when I went to bed."

### Brain-First Lookup Protocol
Any AI agent must query the brain BEFORE calling external APIs. The
cheapest, fastest, most personal information source you have.

### Schema Packs
Declarative page types (person, company, deal, meeting, etc.) that
thread through every read + write path. 7-tier resolution chain.
Agent-authored schema evolution via 14 CLI verbs + MCP op.

### Other Notable
- PGLite (Postgres via WASM): 2-second local brain, no server, no Docker
- 30+ MCP tools, full client support (Claude Code, Codex, ChatGPT, etc.)
- MCP OAuth 2.1 with PKCE for cloud connectors
- Minions job queue: BullMQ-shaped, Postgres-native, crash-safe
- 43 curated skills in a single skillpack
- BrainBench eval framework (LongMemEval, NamedThingBench, etc.)

## What We Adapted

| Feature | Our implementation | Priority |
|---------|--------------------|----------|
| Gap Analysis | Answer template with "covered + gap + recommendation" | P1+ [done] |
| Typed Edges | Parse wiki cross-module tables -> type distribution report | P1+ [done] |
| Brain-first lookup | Context budget rules (conceptual alignment) | P1 [done] |
| Hybrid search | Future: combine tag + wikilink + semantic in one pipeline | P2 |
| Dream cycle | Future: cron-based nightly enrichment | P2 |
