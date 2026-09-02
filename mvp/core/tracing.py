"""Central LangSmith tracing setup — Round 2's answer to the POC's
"Log to Monitoring (LangSmith)" placeholder node (see
../../poc/poc_documentation.md). Round 1 shipped a separate, small trace
sample ([../../langsmith/](../../langsmith/)); this module wires real,
continuous tracing into the MVP itself, so every fault-triage, checklist,
and predictive-alert interaction is inspectable in LangSmith — not just a
handful of one-off script runs.

Fails soft by design: with no LANGSMITH_API_KEY, tracing is simply off —
`traceable` becomes a normal passthrough decorator, `wrap_openai` returns
the client unwrapped, and nothing else in the app changes behavior or
errors. Import this module (not `langsmith` directly) everywhere tracing
is used, so the env defaults below are always applied first.
"""
from __future__ import annotations

import os

DEFAULT_PROJECT = "heat-pump-copilot-round2"

if os.environ.get("LANGSMITH_API_KEY", "").strip():
    # Mirrors langsmith/run_trace_sample.py's Round 1 pattern exactly —
    # setdefault so an explicit .env value is never overridden.
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGSMITH_PROJECT", DEFAULT_PROJECT)

from langsmith import traceable  # noqa: E402 — import after the env defaults above are set
from langsmith.wrappers import wrap_openai  # noqa: E402

__all__ = ["traceable", "wrap_openai", "is_configured"]


def is_configured() -> bool:
    """Cheap presence check for the sidebar status indicator — is a
    LANGSMITH_API_KEY set at all (not a live connectivity check)."""
    return bool(os.environ.get("LANGSMITH_API_KEY", "").strip())
