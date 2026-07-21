import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # read a local .env (walks up from cwd) into the environment

# Only credential needed — embeddings run locally.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OpenAI model used for entity/relation extraction.
EXTRACT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.5")

# Local embedding model (downloaded once by sentence-transformers).
EMBED_MODEL = os.environ.get("ORMAYUNDO_EMBED_MODEL", "BAAI/bge-small-en-v1.5")

# Single self-hosted graph file.
DB_PATH = Path(os.environ.get("ORMAYUNDO_DB", Path.home() / ".ormayundo" / "memory.db"))

# bge models want a retrieval instruction prepended to the QUERY (not documents).
# Blank this if you swap in a model that doesn't use a query prefix.
EMBED_QUERY_PREFIX = os.environ.get(
    "ORMAYUNDO_QUERY_PREFIX", "Represent this sentence for searching relevant passages: "
)

# Tunables (the paper's chunking/retrieval knobs). ponytail: constants until tuned.
CHUNK_CHARS = 2000    # chunk size for ingestion
TOP_K = 5             # entry nodes per recall query
HOP_DEPTH = 2         # graph expansion depth
# Cosine gate for an entry node to count. bge's unrelated-text floor is ~0.47 with
# the query prefix, and relevant hits land ~0.9, so 0.5 separates cleanly.
MIN_SIMILARITY = 0.5
