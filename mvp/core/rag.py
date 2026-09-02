"""Real embeddings-based RAG over the manual knowledge base — the Round 2
upgrade the POC's own docs flagged as next (poc/poc_documentation.md,
"Language" section: "swap the keyword match for multilingual embeddings
... a German query then retrieves the right English-language manual
excerpt on semantic similarity, not exact keyword overlap").

Uses OpenAI embeddings (text-embedding-3-small — multilingual) + Pinecone
serverless as the vector store, via LangChain. Index is built once by
scripts/ingest_manuals.py; this module only queries it.

Every public function fails soft: if Pinecone/OpenAI aren't configured or
a call errors, callers get a clear RagUnavailable with a human-readable
reason, and app.py falls back to core/keyword_fallback.retrieve(). The
core AI capability is real when keys are present — this is the
"don't crash the demo" layer around it, not a fake success path.
"""
from __future__ import annotations

import os

DEFAULT_INDEX_NAME = "heat-pump-copilot-manuals"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536  # text-embedding-3-small's fixed output size


class RagUnavailable(Exception):
    """Raised when Pinecone/OpenAI aren't configured, or the index/query
    call fails — always carries a human-readable reason for the UI."""


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RagUnavailable(f"{name} is not set — see mvp/.env.example.")
    return value


def get_embeddings():
    from langchain_openai import OpenAIEmbeddings

    api_key = _require_env("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    return OpenAIEmbeddings(model=model, api_key=api_key)


def get_pinecone_client():
    from pinecone import Pinecone

    api_key = _require_env("PINECONE_API_KEY")
    return Pinecone(api_key=api_key)


def ensure_index(pc, index_name: str) -> None:
    """Creates the serverless index if it doesn't exist yet. Called by
    scripts/ingest_manuals.py; app.py assumes the index already exists
    (querying a missing index is treated as RagUnavailable, not created
    on the fly, so a live app never silently starts a billable resource)."""
    from pinecone import ServerlessSpec

    existing = {idx["name"] for idx in pc.list_indexes()}
    if index_name in existing:
        return
    cloud = os.environ.get("PINECONE_CLOUD", "aws")
    region = os.environ.get("PINECONE_REGION", "us-east-1")
    pc.create_index(
        name=index_name,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud=cloud, region=region),
    )


def get_vectorstore():
    from langchain_pinecone import PineconeVectorStore

    index_name = os.environ.get("PINECONE_INDEX_NAME", DEFAULT_INDEX_NAME)
    pc = get_pinecone_client()
    existing = {idx["name"] for idx in pc.list_indexes()}
    if index_name not in existing:
        raise RagUnavailable(
            f"Pinecone index '{index_name}' doesn't exist yet — run "
            f"`python scripts/ingest_manuals.py` once to create and populate it."
        )
    return PineconeVectorStore(index=pc.Index(index_name), embedding=get_embeddings())


def is_configured() -> bool:
    """Cheap presence check (not a live API/Pinecone call) for the sidebar
    status indicator — do PINECONE_API_KEY and OPENAI_API_KEY look set."""
    return bool(os.environ.get("PINECONE_API_KEY", "").strip()) and bool(
        os.environ.get("OPENAI_API_KEY", "").strip()
    )


def retrieve_manual_context(query: str, k: int = 3) -> tuple[list[str], list[str]]:
    """Returns (excerpts, sources) from semantic similarity search, or
    raises RagUnavailable — callers should catch it and fall back to
    core/keyword_fallback.retrieve()."""
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search(query, k=k)
    except RagUnavailable:
        raise
    except Exception as exc:  # noqa: BLE001 — any Pinecone/OpenAI failure, surfaced not swallowed
        raise RagUnavailable(f"Pinecone/OpenAI retrieval failed: {exc}") from exc

    excerpts = [doc.page_content for doc in results]
    sources = [doc.metadata.get("source", "manual knowledge base") for doc in results]
    return excerpts, sources
