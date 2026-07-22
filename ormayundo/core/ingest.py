"""remember(text): chunk -> LLM extracts triples -> embed entities -> store."""
import json

from ..config import (
    ANTHROPIC_API_KEY,
    CHUNK_CHARS,
    DB_PATH,
    EXTRACT_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
)
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


def _client():
    """Build the client for the configured provider (imported lazily so only the
    provider actually in use needs its SDK installed)."""
    if LLM_PROVIDER == "anthropic":
        from anthropic import Anthropic
        return Anthropic(api_key=ANTHROPIC_API_KEY)
    if LLM_PROVIDER == "openai":
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY)
    raise ValueError(f"LLM_PROVIDER={LLM_PROVIDER!r}; expected 'anthropic' or 'openai'.")


def _extract_triples(chunk, client):
    prompt = _PROMPT.format(chunk=chunk)
    if LLM_PROVIDER == "anthropic":
        # Force structured output via a single required tool call.
        msg = client.messages.create(
            model=EXTRACT_MODEL,
            max_tokens=4096,
            tools=[{"name": "emit_triples", "description": "Emit extracted triples.",
                    "input_schema": _TRIPLE_SCHEMA}],
            tool_choice={"type": "tool", "name": "emit_triples"},
            messages=[{"role": "user", "content": prompt}],
        )
        for block in msg.content:
            if block.type == "tool_use":
                return parse_triples(block.input)
        return []
    resp = client.chat.completions.create(
        model=EXTRACT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "triples", "strict": True, "schema": _TRIPLE_SCHEMA},
        },
    )
    return parse_triples(resp.choices[0].message.content or "{}")


def parse_triples(raw):
    """Defensive parse: drop anything that isn't a complete (s, r, o) triple.
    Accepts a JSON string (OpenAI) or an already-parsed dict (Anthropic tool_use)."""
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            return []
    else:
        data = raw
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
    client = _client()
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
    # dict input (Anthropic tool_use path) parses the same as its JSON-string form
    assert parse_triples({"triples": [{"subject": "Ada", "relation": "designed",
                                       "object": "the Engine"}]}) == [("Ada", "designed", "the Engine")]
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
