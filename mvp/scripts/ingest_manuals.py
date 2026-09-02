#!/usr/bin/env python3
"""One-time ingestion: embeds every manual knowledge-base entry
(data/manuals/*.json) and upserts it into the Pinecone index used by
core/rag.py. Run this once before using the app's RAG path (or again
after editing the manual JSON files).

Usage:
    cd mvp
    cp .env.example .env   # fill in OPENAI_API_KEY + PINECONE_API_KEY
    python scripts/ingest_manuals.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from core import data_loader, rag  # noqa: E402


def main() -> None:
    index_name = os.environ.get("PINECONE_INDEX_NAME", rag.DEFAULT_INDEX_NAME)

    print(f"Loading manual documents from data/manuals/ ...")
    docs = data_loader.load_manual_documents()
    print(f"  {len(docs)} documents loaded.")

    print(f"Connecting to Pinecone, ensuring index '{index_name}' exists ...")
    pc = rag.get_pinecone_client()
    rag.ensure_index(pc, index_name)

    from langchain_core.documents import Document
    from langchain_pinecone import PineconeVectorStore

    lc_docs = [
        Document(
            page_content=doc["text"],
            metadata={"id": doc["id"], "category": doc["category"], "source": doc["source"]},
        )
        for doc in docs
    ]
    ids = [doc["id"] for doc in docs]

    print(f"Embedding + upserting {len(lc_docs)} documents into '{index_name}' ...")
    vectorstore = PineconeVectorStore(index=pc.Index(index_name), embedding=rag.get_embeddings())
    vectorstore.add_documents(lc_docs, ids=ids)

    print("Done. Try a query:")
    print("  python -c \"from core import rag; print(rag.retrieve_manual_context('controller not responding'))\"")


if __name__ == "__main__":
    main()
