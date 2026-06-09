# Agent Memory System (Absorption Case Study: TencentDB-Agent-Memory)

> **Consolidated reference.** Formerly a standalone skill (`fde/agent-memory-system`). Now a reference case study under the FDE External Absorption umbrella.

## Origin

Absorbed from [TencentDB-Agent-Memory](https://github.com/Tencent/TencentDB-Agent-Memory) (2026-06-08).
Design philosophy: **人主动驾驭知识，而非系统自动捕获。** 博采众长，不失六韬根基。

## Architecture Overview

Five components that form the 六韬 FDE memory system:

```
                         ┌────────────────────────────────┐
                         │  Progressive Context Injection  │
                         │  (L3 profile → L2 scenes →     │
                         │   L1 facts → L0 logs)          │
                         └──────────┬─────────────────────┘
                                    │ on-demand load
     ┌──────────────────────────────┼─────────────────────────────┐
     │                              │                             │
     ▼                              ▼                             ▼
┌────────────┐           ┌──────────────────┐          ┌──────────────────┐
│ Symbolic   │           │ Hybrid Search    │          │ Task Checkpoint  │
│ STM        │◄─────────►│ (BM25+Vector+RRF)│◄────────►│ (save/resume)    │
└──────┬─────┘           └────────┬─────────┘          └────────┬─────────┘
       │                          │                             │
       ▼                          ▼                             ▼
   refs.md + canvas.md     hybrid-memory MCP             state.json + summary.md
```

## The 5 Components

### 1. Symbolic Context Compression (Symbolic STM)

**Problem:** Tool logs explode to hundreds of thousands of tokens in long tasks.

**Solution:** Auto-summarize tool output into Mermaid state diagrams; dump full text to refs files.

```
Verbose Logs → ① Offload to refs.md
             → ② Extract key state → Mermaid canvas (hundreds of tokens)
             → ③ node_id backtracking: grep 'node_id:xxx' refs.md
```

**Trigger:** context >50% / single step >5K tokens / 3+ consecutive tool calls

**Script:** `~/.hermes/profiles/yanqing/scripts/mermaid-offload/mermaid_offload.py`

### 2. BM25 + Vector Hybrid Search (Hybrid Memory MCP)

**Problem:** Pure vector search has weak Chinese keyword matching.

**Solution:** jieba segmentation → BM25 FTS5 + vector semantics → RRF(k=60) fusion ranking

```
MCP: hybrid-memory (registered, 5 tools)
├── memory_hybrid_search    — mixed search
├── memory_bm25_search      — BM25 keyword
├── memory_vector_search    — vector semantic
├── memory_index_add        — add index
└── memory_index_stats      — index stats
```

**Verification:** 42/42 tests passed.
**Config:** `hermes mcp test hybrid-memory`
**REST port:** 8421 (for downstream products like 包打听)

### 3. Semi-Auto User Profile (Auto-Profile)

**Problem:** Agent starts every conversation as if meeting the user for the first time.

**Solution:** Agent generates draft → human reviews & confirms → injected into memory (not fully automatic — keeps human in control)

```
/profile generate   → Agent reads conversation history → structured profile draft
/profile review     → User views full Markdown draft
/profile confirm    → Injected into ~/.hermes/memories/USER.md (auto-loaded next session)
```

**Dimensions:** 6 aspects (preferences, decision mode, habits, pitfalls, knowledge gaps, automation preferences). Each entry tagged with confidence + source session.

**Script:** `~/.hermes/profiles/yanqing/scripts/auto-profile/`

### 4. Progressive Context Injection Protocol

**Problem:** Agent pulls in entire conversation history every time instead of loading only what's needed.

**Solution:** Surface-to-core layered injection:

| Layer | Content | Strategy |
|:------|:--------|:---------|
| L3 | User profile + current goal | **Always loaded** |
| L2 | Relevant scene blocks / SOPs | **On-demand** (when encountering a specific issue) |
| L1 | Key facts / past decisions | **On-demand** (when factual basis needed) |
| L0 | Raw logs / tool output | **Not injected** (backtrack via node_id) |

### 5. Task-Level Checkpoint/Resume

**Problem:** Long tasks (30+ rounds) lose state on interruption.

**Solution:** Save task state at key milestones; load to resume after interruption.

```python
save_checkpoint(task_id, goal, completed_steps, partial_outputs, next_plan)
state = load_checkpoint(task_id)  # {goal, completed_steps, partial_outputs, next_plan}
force_delete_checkpoint(task_id)  # cleanup on completion
```

**Format:** Pure JSON + Markdown, human-readable and editable.
**Relationship:** Hermes /rollback & /snapshot are config-level snapshots; this is task-level.

**Script:** `~/.hermes/profiles/yanqing/scripts/task-checkpoint/checkpoint.py`

## Design Principles

1. **人为知识负责** — all memory writes must be human-confirmed (Profile)
2. **白盒可调试** — every layer is readable Markdown (Canvas / Profile / Checkpoint)
3. **渐进展开** — start with overview, drill down on demand (L3→L0)
4. **轻量不侵入** — pure skill + Python scripts, no Hermes core modifications
5. **博采众长** — engineering from TencentDB-Agent-Memory, philosophy kept 六韬

## File Locations

| Resource | Path |
|:---------|:-----|
| Mermaid offload script | `~/.hermes/profiles/yanqing/scripts/mermaid-offload/` |
| Hybrid memory MCP + REST | `~/.hermes/profiles/yanqing/scripts/hybrid-memory/` |
| Auto-profile scripts | `~/.hermes/profiles/yanqing/scripts/auto-profile/` |
| Task checkpoint scripts | `~/.hermes/profiles/yanqing/scripts/task-checkpoint/` |
| Active user profile | `~/.hermes/memories/USER.md` |
| Context offload storage | `~/.hermes/tmp/context-offload/` |
| Checkpoint storage | `~/.hermes/tmp/checkpoints/` |
| Hybrid Memory MCP | Registered via config (port 8421) |

## Product Integration

The memory system is integrated into **包打听（企业经验引擎）**:

| Component | Product Use | Integration |
|:----------|:------------|:------------|
| hybrid-memory | Retrieval layer | REST (port 8421), HTTP calls |
| Mermaid compression | Deep analysis reports | Agent-triggered |
| Progressive injection | Answer generation strategy | Behavioral guidance |
| User profile | Enterprise client profiling | Semi-auto + human confirmation |

See `Delivery/企业交付/Toolkits/包打听-技术架构-v0.1.md` for full architecture.

## Notes for Future Absorption

- The 5-component split maps well to the absorption's "可吸收 → 可改造 → 不吸收" framework
- The scripts directory structure (`scripts/{功能名}/`) is the standard pattern for absorption output
- The hybrid-memory REST service (port 8421) is a good model for future MCP + HTTP dual-mode services
