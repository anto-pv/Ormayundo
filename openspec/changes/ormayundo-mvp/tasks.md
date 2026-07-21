## 1. Project setup

- [x] 1.1 Create `ormayundo/` package with `core/` subpackage and `pyproject.toml`
- [x] 1.2 Add dependencies: `anthropic`, `sentence-transformers` (sqlite3 is stdlib)
- [x] 1.3 Add config: read `ANTHROPIC_API_KEY`; DB path default `~/.ormayundo/memory.db`

## 2. Store (`core/store.py`)

- [x] 2.1 Create schema: `nodes(id, name UNIQUE, embedding BLOB)`, `edges(src, relation, dst)`
- [x] 2.2 Implement `upsert_node(name, embedding) -> id` (idempotent by name)
- [x] 2.3 Implement `add_edge(src_id, relation, dst_id)`
- [x] 2.4 Implement `nearest_nodes(vector, k)` via Python cosine over rows (`ponytail:` linear scan)
- [x] 2.5 Implement `neighbors(node_id, depth)` for 1–2 hop expansion
- [x] 2.6 Self-check: write triples, query them back, assert round-trip + ranking — PASSES

## 3. Embeddings (`core/embed.py`)

- [x] 3.1 Implement `embed(texts) -> vectors` wrapping `sentence-transformers` (default `BAAI/bge-small-en-v1.5`)
- [x] 3.2 Add float32 pack/unpack helpers for the BLOB column
- [x] 3.3 Self-check: assert cosine of a text with itself ≈ 1, with an unrelated text is lower — PASSES
- [x] 3.4 Add `embed_query()` with bge retrieval prefix (query/document space alignment)

## 4. Ingest (`core/ingest.py`)

- [x] 4.1 Implement chunking with a tunable size constant
- [x] 4.2 Implement Claude call returning `(subject, relation, object)` triples per chunk (structured output)
- [x] 4.3 Parse triples defensively; skip malformed/incomplete ones
- [x] 4.4 Embed distinct entities and write nodes + edges via `store`
- [x] 4.5 Self-check: assert triple parser drops bad rows and keeps valid ones (no live API) — PASSES

## 5. Recall (`core/recall.py`)

- [x] 5.1 Embed query → `nearest_nodes` (top-k, threshold) → entry nodes
- [x] 5.2 Expand 1–2 hops and collect the connected subgraph
- [x] 5.3 Format subgraph as readable text; return empty result on no match
- [x] 5.4 Self-check: hop expansion returns connected facts + no-match returns empty — PASSES

## 6. MCP server (`mcp_server.py`)

- [x] 6.1 Wire the Python MCP SDK server (FastMCP) with configurable DB path (via `ORMAYUNDO_DB`)
- [x] 6.2 Register `remember(text)` tool calling `ingest`
- [x] 6.3 Register `recall(query)` tool calling `recall`
- [ ] 6.4 Verify with an MCP client that both tools work and persist across restart — NOT RUN (needs `pip install`, live client)

## 7. Claude plugin (`plugin/`)

- [x] 7.1 Write plugin manifest (`.claude-plugin/plugin.json` + `.mcp.json`) registering the MCP server
- [x] 7.2 Document `ANTHROPIC_API_KEY` and DB path config in plugin setup
- [ ] 7.3 Verify installing the plugin exposes `remember`/`recall` to the agent — NOT RUN (needs live Claude Code install)

## 8. Docs

- [x] 8.1 Update README with install + usage (single API key, local embeddings)
