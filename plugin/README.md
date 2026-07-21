# Ormayundo plugin

Registers the Ormayundo MCP server so Claude gains `remember` / `recall` tools.

## Setup

1. Install the engine so the `ormayundo-mcp` command is on PATH:
   ```
   pip install ormayundo
   ```
2. Set the one required credential (embeddings run locally — no second key):
   ```
   export OPENAI_API_KEY=sk-...
   ```
   Or put `OPENAI_API_KEY=sk-...` in a `.env` file — it's loaded automatically.
3. Optional — override where the graph lives (default `~/.ormayundo/memory.db`):
   ```
   export ORMAYUNDO_DB=/path/to/memory.db
   ```

The MCP server is declared in `.mcp.json`; installing this plugin makes the
`remember` and `recall` tools available to the agent.
