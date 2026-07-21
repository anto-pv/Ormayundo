"""MCP server exposing the Ormayundo memory engine as `remember` and `recall` tools.

Run:  ormayundo-mcp        (stdio transport, for Claude / any MCP client)
The graph persists at ORMAYUNDO_DB (default ~/.ormayundo/memory.db), so memories
survive across server restarts.
"""
from mcp.server.fastmcp import FastMCP

from .core.ingest import remember as _remember
from .core.recall import recall as _recall

mcp = FastMCP("ormayundo")


@mcp.tool()
def remember(text: str) -> str:
    """Store text into long-term memory. Extracts entities and relationships
    into the self-hosted knowledge graph for later recall."""
    n = _remember(text)
    return f"Stored {n} fact(s) to memory."


@mcp.tool()
def recall(query: str) -> str:
    """Recall relevant long-term memories for a natural-language query.
    Returns connected facts, or a note if nothing relevant is found."""
    result = _recall(query)
    return result or "No relevant memories found."


def main():
    mcp.run()


if __name__ == "__main__":
    main()
