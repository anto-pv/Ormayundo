"""recall(query): embed -> nearest entry nodes -> expand hops -> readable text."""
from ..config import DB_PATH, HOP_DEPTH, MIN_SIMILARITY, TOP_K
from .embed import embed, embed_query
from .store import Store


def recall(query, db_path=None, top_k=TOP_K, hop_depth=HOP_DEPTH):
    """Return connected facts relevant to `query` as readable text (empty str on no match)."""
    store = Store(db_path or DB_PATH)
    try:
        qvec = embed_query(query)
        entries = [(nid, name) for nid, name, sim in store.nearest_nodes(qvec, top_k)
                   if sim >= MIN_SIMILARITY]
        if not entries:
            return ""
        facts = {}  # dedup triples across entry nodes, preserve first-seen order
        for nid, _ in entries:
            for triple in store.neighbors(nid, depth=hop_depth):
                facts.setdefault(triple, None)
        return _format(entries, facts.keys())
    finally:
        store.close()


def _format(entries, triples):
    lines = ["Relevant memories for: " + ", ".join(name for _, name in entries)]
    for s, r, o in triples:
        lines.append(f"- {s} {r} {o}")
    return "\n".join(lines)


def demo():
    import tempfile
    from pathlib import Path
    from .store import Store

    # Seed a real temp DB (no live API), then drive recall() end-to-end against it.
    tmp = Path(tempfile.mkdtemp()) / "demo.db"
    s = Store(tmp)
    names = ["Ada Lovelace", "Analytical Engine", "Charles Babbage"]
    ids = {n: s.upsert_node(n, v) for n, v in zip(names, embed(names))}
    s.add_edge(ids["Ada Lovelace"], "wrote notes on", ids["Analytical Engine"])
    s.add_edge(ids["Charles Babbage"], "designed", ids["Analytical Engine"])
    s.close()

    out = recall("Who was Ada Lovelace?", db_path=tmp)
    assert out.startswith("Relevant memories"), out
    assert "wrote notes on" in out, out          # connected fact recovered via hop
    assert "designed" in out, out                # 2-hop reaches Babbage's edge

    # No-match query returns empty, not an error.
    assert recall("photosynthesis in ferns", db_path=tmp) == ""
    print("recall demo ok")


if __name__ == "__main__":
    demo()
