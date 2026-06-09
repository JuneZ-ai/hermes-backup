# Three-Way Comparison: 六韬 x LLM Wiki x GBrain (2026-06-05)

## Philosophical Divergences

### Knowledge as Files vs Knowledge as Database Rows
- LLM Wiki + 六韬: markdown files are the system of record. Obsidian-compatible by design.
- GBrain: Postgres is the system of record. Markdown files are export/cache copies.

Not a contradiction -- different priorities. File-first = human-curation friendly.
DB-first = agent-friendly. Our 六韬 stance is file-first, which is right for our
Obsidian-based workflow.

### Graphs as Relevance Scores vs Graphs as Facts
- LLM Wiki: four-signal model tells you "these pages are related" (recommendation)
- GBrain: typed edges tell you "this person founded this company" (fact database)
- Our 六韬: untyped [[wikilinks]] only

Complementary, not conflicting. LLM Wiki's model finds hidden connections; GBrain's
model describes known ones. 六韬 can use both: LLM Wiki's signal detection first,
then GBrain's type classification after.

### Human-in-Loop vs Agent Autonomous
- LLM Wiki: async audit queue, human reviews before changes take effect
- GBrain: dream cycle runs autonomously, human is loop-out
- Our 六韬: human-driven with AI assistance

This is a maturity gradient, not a binary choice. LLM Wiki's audit queue can feed
into a dream-cycle-like nightly enrichment.

## Derived Design Principle (for 六韬)

"集思广益，博采众长，积众长以成个性"
- Gather design decisions from multiple systems
- Adapt each to our existing data model
- Never copy wholesale, always transform

## Applied Divergences

| Dimension | LLM Wiki | GBrain | Our Take |
|-----------|----------|--------|----------|
| Knowledge shape | Wiki pages (human-readable) | DB rows (agent-queryable) | Pages are primary, DB is sync target |
| Graph model | 4-signal relevance | Typed edges | Typed edges + relevance = both |
| Ingestion | Two-step (Analyze -> Generate) | Signal -> capture -> enrich | Two-step + dream cycle hybrid |
| Search | Token + graph + optional vector | Hybrid + synthesis + gap | Synthesis layer on top of existing search |
| Schema | purpose.md + schema.md | Schema packs (7-tier) | SCHEMA.md + templates |
| Maintenance | User-triggered ingestion | 24/7 cron enrichment | Scheduled lint + manual ingestion |
