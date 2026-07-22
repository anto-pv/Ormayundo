# Ormayundo — Design Spec

**Date:** 2026-07-21
**Status:** Approved for planning

## Goal

Give AI agents persistent long-term memory across sessions via a self-hosted
knowledge graph. Ship it as a **Claude plugin** backed by an **MCP server**.

A minimal reimplementation of Cognee's proven approach (arXiv:2505.24478) —
not a fork, not a feature clone. Simple and optimized: only `remember` and
`recall`.

## Non-goals

- No web UI, no multi-user auth, no cloud database.
- No reimplementing Cognee's full feature set (adapters, session cache,
  auto-routing across many search strategies).
- No agent framework — we expose tools; the agent decides when to use them.

## Core decisions (locked)

| Decision | Choice | Why |
|----------|--------|-----|
| Approach | Reimplement lite engine | Own it, keep it small |
| Runtime | Python | Matches reference, best LLM/graph ecosystem |
| Graph store | SQLite, single `.db` file | Zero infra, ships in the plugin |
| Retrieval | Semantic + graph hop | Matches Cognee's hybrid; best recall |
| LLM (extraction) | Claude (default) or OpenAI, via `ORMAYUNDO_LLM` | Claude matches the plugin; OpenAI opt-in. Paper is model-agnostic. |
| Embeddings | Local `sentence-transformers` (pluggable) | Zero cost, fully offline/self-hosted, no extra API key |

## Architecture

```
ormayundo/
  core/                 the lite memory engine (no MCP knowledge)
    store.py              SQLite: nodes, edges, vectors — one .db file
    ingest.py             chunk → Claude extracts triples → embed → store
    recall.py             embed query → cosine → expand 1–2 hops → text
  mcp_server.py         MCP tools: remember(text), recall(query)
  plugin/               Claude plugin manifest registering the MCP server
```

Layering: `core` knows nothing about MCP; `mcp_server` is thin glue; `plugin`
is packaging. Each layer is testable in isolation.

### Data model (SQLite)

- `nodes(id INTEGER PK, name TEXT UNIQUE, embedding BLOB)`
- `edges(src INTEGER, relation TEXT, dst INTEGER)` — FKs to `nodes.id`

Embeddings stored as a BLOB (packed float32); cosine computed in Python over
the candidate set. `ponytail:` no vector index — linear scan is fine until the
graph is large; add sqlite-vec if scan is measurably slow.

### Data flow

**remember(text):**
1. Chunk text into tunable-size units.
2. One Claude call per chunk → `[(subject, relation, object)]` triples.
3. Embed each distinct entity (local `sentence-transformers`).
4. Upsert nodes + insert edges into SQLite.

**recall(query):**
1. Embed the query.
2. Cosine vs. node embeddings → top-k entry nodes.
3. Expand 1–2 hops along edges → connected subgraph.
4. Format subgraph as readable text for the agent.

## Build phases

Each phase ends runnable; no phase depends on a later one.

1. **Store** — SQLite schema + CRUD (upsert node, add edge, nearest-by-cosine,
   neighbors). Self-check: write triples, query them back.
2. **Ingest** — chunk → Claude triple extraction → embed → store. Self-check:
   a paragraph produces an inspectable graph.
3. **Recall** — embed query → nearest nodes → 1–2 hop expansion → text.
   Self-check: a question returns connected facts.
   *(Engine now works as a standalone Python lib.)*
4. **MCP server** — wrap `remember`/`recall` as MCP tools (Python MCP SDK).
   Done when an MCP client calls both against the .db.
5. **Claude plugin** — manifest registering the MCP server; one-command install.
   Done when installing the plugin gives Claude persistent memory tools.

## Testing

Per ponytail: each non-trivial module leaves one runnable `assert`-based
self-check (no framework). Cosine math, triple parsing, and hop expansion each
get a check. API calls (Claude, Voyage) are the only mocked/optional boundary.

## Config

- `ANTHROPIC_API_KEY` — env var (only key needed; embeddings run locally).
- Embedding model — defaults to `BAAI/bge-small-en-v1.5` (or `all-MiniLM-L6-v2`),
  downloaded once by `sentence-transformers`; overridable via constant.
- DB path — defaults to `~/.ormayundo/memory.db`, overridable.
- Chunk size, top-k, hop depth — module constants, tuned later per the paper's
  chunking/retrieval knobs.

## Open questions

None blocking. The embedding layer is behind a single `embed(texts) -> vectors`
interface, so the model (or a hosted provider) is a one-line swap if needed.
