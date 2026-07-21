"""Local embeddings via sentence-transformers. No API key required."""
import numpy as np

from ..config import EMBED_MODEL, EMBED_QUERY_PREFIX

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # heavy import, do it lazily
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def embed(texts):
    """Embed documents/entities. list[str] -> np.ndarray (n, dim) float32, L2-normalized."""
    vecs = _get_model().encode(list(texts), normalize_embeddings=True)
    return np.asarray(vecs, dtype=np.float32)


def embed_query(text):
    """Embed a search query. Prepends the model's retrieval instruction so query
    and document vectors live in the same space. Returns a single (dim,) vector."""
    return embed([EMBED_QUERY_PREFIX + text])[0]


def pack(vec) -> bytes:
    return np.asarray(vec, dtype=np.float32).tobytes()


def unpack(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


def demo():
    a, b, c = embed(["a cat sat on the mat", "a feline rested on the rug", "quarterly tax filing"])
    # normalized vectors: dot product == cosine similarity
    assert a @ a == 1.0 or abs(a @ a - 1.0) < 1e-4, a @ a
    assert (a @ b) > (a @ c), (a @ b, a @ c)  # paraphrase closer than unrelated
    assert unpack(pack(a)).shape == a.shape
    print("embed demo ok")


if __name__ == "__main__":
    demo()
