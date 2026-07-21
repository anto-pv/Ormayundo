## Why

AI agents lose everything they learn when a session ends, forcing users to
re-supply context every run. Ormayundo gives agents persistent long-term memory
backed by a self-hosted knowledge graph — so what an agent learned before stays
available, retrievable as connected facts rather than a flat blob.

## What Changes

- Introduce a minimal Python memory engine: `remember(text)` ingests text into a
  knowledge graph; `recall(query)` returns connected facts via semantic + graph-hop
  retrieval.
- Store the graph (nodes, edges, vectors) in a single self-hosted SQLite file — no
  external database, no cloud service.
- Extract entities/relations with the Claude API; embed entities locally with
  `sentence-transformers` (only `ANTHROPIC_API_KEY` required, no second API key).
- Expose the engine as an MCP server (`remember`, `recall` tools).
- Package the MCP server as an installable Claude plugin.

Scope is deliberately narrow: a lite reimplementation of Cognee's proven approach
(arXiv:2505.24478), not a feature clone. Only `remember` and `recall`.

## Capabilities

### New Capabilities
- `knowledge-graph-memory`: the core engine — SQLite-backed graph store, LLM-based
  triple ingestion, and semantic + graph-hop recall. Usable as a standalone Python
  library.
- `mcp-server`: exposes the engine's `remember`/`recall` as MCP tools over the
  Python MCP SDK, backed by a configurable `.db` path.
- `claude-plugin`: a Claude plugin manifest that registers the MCP server so agents
  gain memory tools with a one-command install.

### Modified Capabilities
<!-- None — new project, no existing specs. -->

## Impact

- New Python package `ormayundo/` (`core/`, `mcp_server.py`, `plugin/`).
- New dependencies: `anthropic`, `sentence-transformers`. Graph/vector storage uses
  stdlib `sqlite3`.
- Config via `ANTHROPIC_API_KEY` env var and a DB path (default `~/.ormayundo/memory.db`).
- No changes to existing code (repo is currently docs + logo only).
