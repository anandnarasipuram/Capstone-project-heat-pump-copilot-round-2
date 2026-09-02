"""Loads the shared data/ assets (manual knowledge base, synthetic fault
dataset, When2Heat COP baseline) that the MVP's three modes run on.

Kept separate from rag.py / predictive.py so the loading + shaping logic
is testable without pandas-heavy fixtures duplicating the real files, and
so Streamlit's @st.cache_data can wrap these functions directly.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

# data/ lives two levels up from mvp/core/
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MANUALS_DIR = DATA_DIR / "manuals"


class ManualDoc(TypedDict):
    id: str
    category: str
    source: str
    text: str  # concatenated content used as the embedding input


def load_manual_documents() -> list[ManualDoc]:
    """Flattens all three manual JSON files into a single list of
    (id, category, source, text) documents ready for embedding + upsert
    into Pinecone. See scripts/ingest_manuals.py for the ingestion step
    and data/manuals/README.md for source/copyright notes."""
    docs: list[ManualDoc] = []

    fault_codes = json.loads((MANUALS_DIR / "fault_code_knowledge_base.json").read_text())
    for entry in fault_codes["entries"]:
        docs.append(
            {
                "id": f"faultcode-{entry['code']}",
                "category": entry["category"],
                "source": entry["source"],
                "text": (
                    f"Fault code {entry['code']}. Cause: {entry['cause_summary']} "
                    f"Action: {entry['fix_or_escalation_action']} "
                    f"Category: {entry['category']}."
                ),
            }
        )

    for fname in ("connectivity_status_guide.json", "safety_device_reference.json"):
        data = json.loads((MANUALS_DIR / fname).read_text())
        for entry in data["entries"]:
            docs.append(
                {
                    "id": entry["id"],
                    "category": entry["category"],
                    "source": entry["source"],
                    "text": f"{entry['summary']} Category: {entry['category']}.",
                }
            )

    return docs


def load_cop_baseline():
    """Loads the When2Heat Germany COP subset and returns a DataFrame
    indexed by month (1-12) with the mean COP per profile column —
    the seasonal baseline the predictive module compares readings
    against. Cached at the Streamlit layer since the source CSV is
    ~130k rows; this function itself does the one-time aggregation.
    """
    import pandas as pd  # local import: keeps this module importable without pandas for callers that don't need it

    csv_path = DATA_DIR / "when2heat_DE_subset.csv"
    df = pd.read_csv(csv_path, usecols=[
        "cet_cest_timestamp",
        "DE_COP_ASHP_floor",
        "DE_COP_ASHP_radiator",
        "DE_COP_ASHP_water",
    ])
    df["month"] = pd.to_datetime(df["cet_cest_timestamp"], utc=True, errors="coerce").dt.month
    monthly = df.groupby("month")[
        ["DE_COP_ASHP_floor", "DE_COP_ASHP_radiator", "DE_COP_ASHP_water"]
    ].mean()
    return monthly


def load_installed_fleet():
    """Loads the small, hand-curated synthetic installed-fleet demo table
    used by the Installed Fleet Overview tab — see
    data/installed_fleet_documentation.md for what it is (and isn't).
    Deliberately spans all 3 severity flags for demo purposes."""
    import pandas as pd  # local import, same rationale as load_cop_baseline()

    return pd.read_csv(DATA_DIR / "synthetic_installed_fleet.csv")


def load_keyword_entries() -> list[dict]:
    """Loads the two keyword-tagged manual files (connectivity + safety)
    with their `keywords` lists intact, for core/keyword_fallback.py — the
    zero-dependency retrieval path ported from the n8n POC's "Retrieve
    Manual Context" node, used when Pinecone/OpenAI embeddings aren't
    configured. See core/rag.py for the real embeddings-based upgrade."""
    entries: list[dict] = []
    for fname in ("connectivity_status_guide.json", "safety_device_reference.json"):
        data = json.loads((MANUALS_DIR / fname).read_text())
        entries.extend(data["entries"])
    return entries


PROFILE_LABELS = {
    "DE_COP_ASHP_floor": "Air-source heat pump — underfloor heating",
    "DE_COP_ASHP_radiator": "Air-source heat pump — radiators",
    "DE_COP_ASHP_water": "Air-source heat pump — hot water",
}
