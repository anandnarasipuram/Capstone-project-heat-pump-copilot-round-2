"""Zero-dependency keyword retrieval — ported 1:1 from the n8n POC's
"Retrieve Manual Context" node (see poc/poc_documentation.md's "Manual
grounding" section). Used only as a fallback when Pinecone/OpenAI
embeddings aren't configured (missing API keys), so the MVP still
demos end-to-end with no cloud setup at all — same zero-key smoke-test
story as the POC's fault-code lookup path.

This is deliberately lexical, English-first, and small — the real
upgrade is core/rag.py's multilingual embeddings + Pinecone retrieval,
which is what actually resolves the POC's stated language limitation
(see poc/poc_documentation.md, "Language" section). Prefer that path
whenever keys are available; this module exists purely as a safety net.
"""
from __future__ import annotations

from . import data_loader
from .tracing import traceable


@traceable(name="keyword_fallback_retrieve", tags=["heat-pump-copilot", "retrieval:keyword_fallback"])
def retrieve(text: str, k: int = 2) -> tuple[list[str], list[str]]:
    """Returns (excerpts, sources) for the top-k keyword-matching manual
    entries, or ([], []) if nothing matched."""
    entries = data_loader.load_keyword_entries()
    text_lower = (text or "").lower()

    scored = []
    for entry in entries:
        score = sum(1 for kw in entry["keywords"] if kw.lower() in text_lower)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = [entry for _, entry in scored[:k]]

    excerpts = [f"{entry['summary']} (Source: {entry['source']})" for entry in top]
    sources = [entry["source"] for entry in top]
    return excerpts, sources
