"""SQLite-backed knowledge graph: nodes (name + embedding) and edges (triples).

ponytail: linear cosine scan, no vector index. Fine at personal-memory scale;
swap in sqlite-vec if nearest_nodes() gets measurably slow on a large graph.
"""
import sqlite3

import numpy as np

from .embed import pack, unpack

SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id        INTEGER PRIMARY KEY,
    name      TEXT UNIQUE NOT NULL,
    embedding BLOB NOT NULL
);
CREATE TABLE IF NOT EXISTS edges (
    src      INTEGER NOT NULL REFERENCES nodes(id),
    relation TEXT NOT NULL,
    dst      INTEGER NOT NULL REFERENCES nodes(id),
    UNIQUE(src, relation, dst)
);
"""


class Store:
    def __init__(self, db_path):
        self.db_path = db_path
        db_path = str(db_path)
        if db_path != ":memory:":
            from pathlib import Path
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.executescript(SCHEMA)

    def upsert_node(self, name: str, embedding) -> int:
        """Idempotent by name; returns the node id."""
        cur = self.conn.execute("SELECT id FROM nodes WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur = self.conn.execute(
            "INSERT INTO nodes(name, embedding) VALUES (?, ?)", (name, pack(embedding))
        )
        self.conn.commit()
        return cur.lastrowid

    def add_edge(self, src_id: int, relation: str, dst_id: int) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO edges(src, relation, dst) VALUES (?, ?, ?)",
            (src_id, relation, dst_id),
        )
        self.conn.commit()

    def nearest_nodes(self, vector, k: int):
        """Top-k (node_id, name, similarity) by cosine, highest first."""
        rows = self.conn.execute("SELECT id, name, embedding FROM nodes").fetchall()
        if not rows:
            return []
        q = np.asarray(vector, dtype=np.float32)
        scored = []
        for node_id, name, blob in rows:
            v = unpack(blob)
            sim = float(q @ v / ((np.linalg.norm(q) * np.linalg.norm(v)) or 1.0))
            scored.append((node_id, name, sim))
        scored.sort(key=lambda t: t[2], reverse=True)
        return scored[:k]

    def neighbors(self, node_id: int, depth: int = 1):
        """Edges reachable within `depth` hops (either direction).

        Returns list of (src_name, relation, dst_name)."""
        seen_nodes = {node_id}
        frontier = {node_id}
        collected = {}  # (src, rel, dst) -> names, dedup
        for _ in range(depth):
            if not frontier:
                break
            placeholders = ",".join("?" * len(frontier))
            rows = self.conn.execute(
                f"""SELECT s.id, s.name, e.relation, d.id, d.name
                    FROM edges e
                    JOIN nodes s ON s.id = e.src
                    JOIN nodes d ON d.id = e.dst
                    WHERE e.src IN ({placeholders}) OR e.dst IN ({placeholders})""",
                (*frontier, *frontier),
            ).fetchall()
            next_frontier = set()
            for sid, sname, rel, did, dname in rows:
                collected[(sid, rel, did)] = (sname, rel, dname)
                for nid in (sid, did):
                    if nid not in seen_nodes:
                        seen_nodes.add(nid)
                        next_frontier.add(nid)
            frontier = next_frontier
        return list(collected.values())

    def close(self):
        self.conn.close()


def demo():
    from .embed import embed
    s = Store(":memory:")
    names = ["Ada", "Analytical Engine", "London"]
    vecs = embed(names)
    ids = {n: s.upsert_node(n, v) for n, v in zip(names, vecs)}
    # idempotent
    assert s.upsert_node("Ada", vecs[0]) == ids["Ada"]
    s.add_edge(ids["Ada"], "designed", ids["Analytical Engine"])
    s.add_edge(ids["Ada"], "lived in", ids["London"])
    s.add_edge(ids["Ada"], "lived in", ids["London"])  # duplicate ignored

    # round-trip: edges come back
    hood = s.neighbors(ids["Ada"], depth=1)
    assert ("Ada", "designed", "Analytical Engine") in hood, hood
    assert len([e for e in hood if e[1] == "lived in"]) == 1  # dedup held

    # ranking: querying "Ada" returns Ada as the top node
    top = s.nearest_nodes(embed(["Ada"])[0], k=3)
    assert top[0][1] == "Ada", top
    assert top[0][2] >= top[-1][2]  # descending similarity
    print("store demo ok")


if __name__ == "__main__":
    demo()
