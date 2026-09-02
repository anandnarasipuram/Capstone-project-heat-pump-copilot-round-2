"""Core logic for the Heat Pump Copilot MVP.

Split deliberately into pure-logic modules (fault_lookup, checklist,
predictive — no network calls, fully unit-testable offline) and
integration modules (rag, llm — call Pinecone/OpenAI, require API keys).
See mvp_documentation.md for the module map.
"""
