## Context

New project. The repo currently holds only a logo, README, and the design spec at
`docs/superpowers/specs/2026-07-21-ormayundo-design.md`. Ormayundo is a lite
reimplementation of Cognee's KG-LLM memory approach (arXiv:2505.24478), scoped to
persistent agent memory with just two operations: `remember` and `recall`. The end
goal is a Claude plugin backed by an MCP server; the memory engine underneath must
be usable standalone.

## Goals / Non-Goals

**Goals:**
- A minimal Python engine that ingests text into a self-hosted knowledge graph and
  recalls connected facts by natural-language query.
- Zero-infra storage: one SQLite file holding nodes, edges, and vectors.
- One required credential only (`ANTHROPIC_API_KEY`); embeddings run locally.
- Expose the engine as MCP tools, then package as an installable Claude plugin.
- Each layer (engine / MCP / plugin) testable in isolation.

**Non-Goals:**
- No web UI, multi-user auth, or cloud database.
- No reimplementing Cognee's full surface (adapters, session cache, auto-routing).
- No vector index or query optimizer at MVP — linear cosine scan is acceptable.
- No agent framework; the agent decides when to call the tools.

## Decisions

**Reimplement lite, not fork/wrap Cognee.** We own a small, readable engine instead
of tracking a large upstream. Alternative (wrap Cognee) was rejected: heavier
dependency and less control for a two-operation tool.

**Python.** Matches the reference and has the best LLM/graph/embedding ecosystem;
the MCP Python SDK is solid. Alternative (TypeScript) would rebuild glue Python
gives for free.

**Single SQLite file for graph + vectors.** `nodes(id, name, embedding BLOB)` and
`edges(src, relation, dst)`. Zero infra, ships inside the plugin, trivially
portable. Alternatives (Kùzu, Neo4j) add a dependency or a server for scale we
don't need at MVP. Cosine similarity computed in Python over candidate rows.
`ponytail:` no vector index — linear scan until measurably slow, then add sqlite-vec.

**Semantic + graph-hop retrieval.** Embed query → top-k nearest entity nodes →
expand 1–2 hops along edges → return the subgraph as text. Mirrors Cognee's hybrid;
the graph hop recovers connected facts even when the entry embedding is imperfect.

**Local `sentence-transformers` embeddings** (default `BAAI/bge-small-en-v1.5`).
No second API key, no per-query cost, fully offline. Behind a single
`embed(texts) -> vectors` interface so the model or a hosted provider is a one-line
swap. Alternative (Voyage AI) was rejected to avoid a second credential and metering.

**Claude API for triple extraction.** One call per chunk returns
`(subject, relation, object)` triples. Model configurable; defaults to a current
Claude model.

**Three layered capabilities.** `knowledge-graph-memory` (engine) knows nothing
about MCP; `mcp-server` is thin glue; `claude-plugin` is packaging. Clean seams keep
each independently testable and swappable.

## Risks / Trade-offs

- [Local embedding model is slightly weaker than top hosted models] → The graph hop
  compensates; model is a one-line swap if recall is weak.
- [`sentence-transformers` pulls in `torch` (~hundreds of MB)] → Acceptable for a
  self-hosted tool; documented as the cost of zero API keys.
- [Linear cosine scan is O(n) per query] → Fine at personal-memory scale; upgrade
  path to sqlite-vec noted in code with a `ponytail:` comment.
- [LLM triple extraction can be noisy/duplicated] → Upsert nodes by unique name;
  accept some noise at MVP rather than building a resolver.
- [Claude API cost/latency per ingest] → Chunk size is a tunable constant; batching
  can be added later if needed.

## Open Questions

None blocking. Chunk size, top-k, and hop depth start as module constants and get
tuned per the paper's chunking/retrieval knobs after the engine runs end-to-end.
