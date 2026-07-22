<p align="center">
  <img src="https://raw.githubusercontent.com/anto-pv/Ormayundo/main/assets/Logo.jpg" alt="Ormayundo" width="420">
</p>

<h1 align="center">Ormayundo</h1>

<p align="center">
  <em>Persistent long-term memory for AI agents, backed by a self-hosted knowledge graph.</em>
</p>

<p align="center">
  <a href="https://anto-pv.github.io/Ormayundo"><strong>🌐 anto-pv.github.io/Ormayundo</strong></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/anto-pv/Ormayundo/main/assets/ormayundo-demo.gif" alt="Ormayundo remember/recall demo" width="680">
</p>

---

## What is this?

**Ormayundo** (Malayalam: *"Do you remember?"*) gives your AI agents memory that
survives across sessions. Instead of stuffing everything back into the context
window on every run, agents write to and read from a **self-hosted knowledge
graph** — so what an agent learned yesterday is still there today.

Under the hood it turns raw text, documents, and conversations into a structured
graph of entities and relationships, then serves that graph back to agents as
retrievable long-term memory.

## Why a knowledge graph?

Flat vector search finds *similar* chunks. A knowledge graph finds *connected*
facts — which is what multi-hop reasoning actually needs ("who did X work with
on the project that shipped in Y?"). Ormayundo builds that graph automatically
and lets agents traverse it.

The approach follows the KG + LLM interface studied in
[**Optimizing the Interface Between Knowledge Graphs and LLMs for Complex
Reasoning** (arXiv:2505.24478)](https://arxiv.org/abs/2505.24478): performance
comes not from a new architecture but from tuning the pipeline —
**chunking → graph construction → retrieval → prompting**.

## How it works

```
ingest  →  chunk  →  extract entities & relations  →  knowledge graph  →  retrieve  →  agent
```

1. **Ingest** documents, notes, or conversation transcripts.
2. **Chunk** them into tunable units.
3. **Extract** entities and relationships with an LLM.
4. **Store** them in a self-hosted graph (your infra, your data).
5. **Retrieve** connected context on demand — multi-hop, not just nearest-neighbor.

## Install

```bash
pip install ormayundo          # or: pip install -e .  (from a clone)
export OPENAI_API_KEY=sk-...    # default provider; only the LLM key is needed
```

Extraction runs on OpenAI by default. To use Claude instead, set
`LLM_PROVIDER=anthropic` and provide `ANTHROPIC_API_KEY`. Either key can live in a
`.env` file at your project root — it's loaded automatically. First use downloads the
local embedding model (`BAAI/bge-small-en-v1.5`) once (embeddings never need an API key).

## Use it as a library

```python
from ormayundo import remember, recall

remember("Ada Lovelace wrote the first algorithm for Charles Babbage's Analytical Engine.")
print(recall("Who worked on the Analytical Engine?"))
# Relevant memories for: Ada Lovelace, Analytical Engine
# - Ada Lovelace wrote first algorithm for Analytical Engine
# - Charles Babbage designed Analytical Engine
```

## Use it from Claude (MCP)

Run the MCP server (stdio):

```bash
ormayundo-mcp
```

It exposes two tools — `remember(text)` and `recall(query)` — backed by one SQLite
file at `~/.ormayundo/memory.db` (override with `ORMAYUNDO_DB`). Because the graph is
on disk, memories persist across restarts and sessions.

To register it with Claude Code, add to your `.mcp.json`:

```json
{ "mcpServers": { "ormayundo": { "command": "ormayundo-mcp" } } }
```

Or install the bundled plugin in [`plugin/`](plugin/).

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `LLM_PROVIDER` | `openai` | Extraction provider: `openai` or `anthropic` |
| `OPENAI_API_KEY` | — | Required when provider is `openai` (the default) |
| `ANTHROPIC_API_KEY` | — | Required when provider is `anthropic` |
| `ORMAYUNDO_MODEL` | `gpt-5.5` / `claude-sonnet-5` | Extraction model (per-provider default) |
| `ORMAYUNDO_DB` | `~/.ormayundo/memory.db` | Graph storage location |
| `ORMAYUNDO_EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | Local embedding model |

Config is read from the environment or a `.env` file (loaded automatically).

## Status

Early stage. Interfaces and layout will change.

## Contributing

Issues and focused PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) © anto-pv
