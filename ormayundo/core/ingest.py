"""remember(text): chunk -> Claude extracts triples -> embed entities -> store."""
import json

from ..config import CHUNK_CHARS, DB_PATH, EXTRACT_MODEL, OPENAI_API_KEY
from .embed import embed
from .store import Store

_TRIPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "triples": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "relation": {"type": "string"},
                    "object": {"type": "string"},
                },
                "required": ["subject", "relation", "object"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["triples"],
    "additionalProperties": False,
}

_PROMPT = (
    "Extract factual (subject, relation, object) triples from the text below. "
    "Use concise canonical entity names so the same entity is named identically "
    "across triples. Only include facts stated in the text.\n\n{chunk}"
)


def _chunk(text, size=CHUNK_CHARS):
    text = text.strip()
    return [text[i:i + size] for i in range(0, len(text), size)] or []


def _extract_triples(chunk, client):
    resp = client.chat.completions.create(
        model=EXTRACT_MODEL,
        messages=[{"role": "user", "content": _PROMPT.format(chunk=chunk)}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "triples", "strict": True, "schema": _TRIPLE_SCHEMA},
        },
    )
    return parse_triples(resp.choices[0].message.content or "{}")


def parse_triples(raw):
    """Defensive parse: drop anything that isn't a complete (s, r, o) triple."""
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return []
    out = []
    for t in data.get("triples", []) if isinstance(data, dict) else []:
        if not isinstance(t, dict):
            continue
        s, r, o = t.get("subject"), t.get("relation"), t.get("object")
        if all(isinstance(x, str) and x.strip() for x in (s, r, o)):
            out.append((s.strip(), r.strip(), o.strip()))
    return out


def remember(text, db_path=None):
    """Ingest text into the knowledge graph. Returns the number of triples stored."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    store = Store(db_path or DB_PATH)

    all_triples = []
    for chunk in _chunk(text):
        all_triples.extend(_extract_triples(chunk, client))

    if not all_triples:
        store.close()
        return 0

    # Embed every distinct entity once, then wire up nodes + edges.
    entities = sorted({e for s, _, o in all_triples for e in (s, o)})
    id_by_name = {}
    for name, vec in zip(entities, embed(entities)):
        id_by_name[name] = store.upsert_node(name, vec)
    for s, r, o in all_triples:
        store.add_edge(id_by_name[s], r, id_by_name[o])

    store.close()
    return len(all_triples)


def demo():
    # No live API: exercise the defensive parser only.
    good = '{"triples": [{"subject": "Ada", "relation": "designed", "object": "the Engine"}]}'
    assert parse_triples(good) == [("Ada", "designed", "the Engine")]
    # malformed / incomplete rows dropped, valid kept
    mixed = ('{"triples": ['
             '{"subject": "A", "relation": "r", "object": "B"},'
             '{"subject": "", "relation": "r", "object": "B"},'   # empty subject
             '{"subject": "C", "object": "D"},'                    # missing relation
             '"not-an-object"]}')
    assert parse_triples(mixed) == [("A", "r", "B")]
    assert parse_triples("not json") == []
    assert _chunk("x" * (CHUNK_CHARS + 5)) == ["x" * CHUNK_CHARS, "xxxxx"]
    print("ingest demo ok")


if __name__ == "__main__":
    demo()
