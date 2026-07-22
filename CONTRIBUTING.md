# Contributing to Ormayundo

Thanks for your interest! Ormayundo is a small, deliberately minimal memory
engine. Contributions are welcome — bug reports, docs, and focused PRs.

## Philosophy

Keep it lite. Ormayundo is a minimal reimplementation of the KG + LLM approach
from [arXiv:2505.24478](https://arxiv.org/abs/2505.24478) — not a feature clone.
Before adding code, prefer the standard library, an already-installed dependency,
or a few lines over a new abstraction. The shortest change that works wins.

## Dev setup

```bash
git clone https://github.com/anto-pv/Ormayundo
cd Ormayundo
pip install -e .
```

Set the LLM key for the provider you're testing (`OPENAI_API_KEY`, or
`LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY`). Embeddings run locally — the
model downloads once on first use, no key needed.

## Running the checks

Each core module ships a runnable self-check (no test framework). Run them
before opening a PR — they exercise the graph store, embeddings, triple parsing,
and recall without hitting any API:

```bash
python -m ormayundo.core.store
python -m ormayundo.core.embed
python -m ormayundo.core.ingest
python -m ormayundo.core.recall
```

Each prints `... demo ok` on success. If you change logic in a module, update or
add an assertion to its `demo()` so the check still fails when the logic breaks.

## Project layout

- `ormayundo/core/` — the memory engine (knows nothing about MCP)
  - `store.py` — SQLite nodes/edges + cosine search + hop expansion
  - `embed.py` — local sentence-transformers embeddings
  - `ingest.py` — chunk → LLM triple extraction → embed → store
  - `recall.py` — embed query → nearest nodes → expand → text
- `ormayundo/mcp_server.py` — thin MCP glue (`remember`, `recall`)
- `plugin/` — Claude plugin packaging

## Submitting a PR

1. Fork and branch off `main`.
2. Keep the diff focused — one concern per PR.
3. Run the self-checks above.
4. Open the PR with a short description of what and why.

## Reporting bugs

Open an issue with what you ran, what you expected, and what happened. A minimal
reproduction (the `remember`/`recall` calls or config) helps a lot.
