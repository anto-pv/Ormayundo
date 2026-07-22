"""Offline stand-in used ONLY to render the demo GIF (no API key or network).
Returns the same shapes as the real ormayundo API: remember() -> int (facts
stored), recall() -> formatted text block."""


def remember(text):
    return 2


def recall(query):
    return (
        "Relevant memories for: Atlas project\n"
        "- Priya leads Atlas project\n"
        "- Arun works on Atlas project\n"
        "- Atlas project runs on PostgreSQL"
    )


print("ormayundo  ·  offline demo")
