"""Orchestration layer — one function per app mode, each wrapped as a
single top-level LangSmith trace covering the whole interaction, not
just the raw LLM call inside it. This is what makes the traces useful
for the "meaningful discussions with Chleo/customers" the tracing exists
for (per project instructions): one trace per installer message shows
the full decision chain — lookup attempt → retrieval (Pinecone or
keyword fallback) → classification — nested under one parent, instead of
three unrelated spans a reviewer has to manually stitch together.

app.py calls only these three functions; it never calls core/llm.py or
core/rag.py directly, so this module is the single place tracing
boundaries are decided.
"""
from __future__ import annotations

from . import checklist, fault_lookup, keyword_fallback, llm, predictive, rag
from .tracing import traceable


@traceable(name="fault_triage_turn", tags=["heat-pump-copilot", "mode:fault_triage"])
def fault_triage_turn(symptom: str, model: str = "Not specified") -> dict:
    """One installer chat turn: deterministic lookup first (free, instant,
    traced as its own child span so coverage vs. LLM usage is visible in
    LangSmith), else RAG retrieval (Pinecone, falling back to keyword
    match) feeding a grounded classification call.

    `model` is the installer-selected heat pump model (see app.py's Mode 1
    selector). It's passed to the LLM as context and recorded on the
    trace/result either way — see core/llm.py's module docstring on why
    this narrows the AI's answer and feeds per-model analytics without
    actually filtering the fault-code table, since the current manual
    corpus isn't per-model."""
    deterministic = fault_lookup.try_deterministic_classify(symptom)
    if deterministic:
        deterministic["retrieval_mode"] = None
        deterministic["model"] = model
        return deterministic

    retrieval_mode = "keyword fallback"
    excerpts, sources = [], []
    if rag.is_configured():
        try:
            excerpts, sources = rag.retrieve_manual_context(symptom)
            retrieval_mode = "Pinecone RAG (embeddings)"
        except rag.RagUnavailable:
            excerpts, sources = keyword_fallback.retrieve(symptom)
    else:
        excerpts, sources = keyword_fallback.retrieve(symptom)

    result = llm.classify_symptom(symptom, excerpts, sources, model=model)
    result["retrieval_mode"] = retrieval_mode
    return result


@traceable(name="commissioning_turn", tags=["heat-pump-copilot", "mode:commissioning_checker"])
def commissioning_turn(model: str, firmware: str, responses: dict) -> dict:
    """One checklist submission: deterministic scoring, then an LLM
    sign-off summary grounded in the scoring result."""
    result = checklist.evaluate_checklist(responses)
    summary = llm.summarize_checklist(model, firmware, result)
    return {"checklist": result, "summary": summary}


@traceable(name="predictive_turn", tags=["heat-pump-copilot", "mode:predictive_early_warning"])
def predictive_turn(profile_label: str, month_label: str, expected_cop: float, observed_cop: float) -> dict:
    """One COP-reading evaluation: deterministic deviation scoring, then
    an LLM early-warning note grounded in the scoring result."""
    result = predictive.evaluate_reading(expected_cop=expected_cop, observed_cop=observed_cop)
    alert = llm.generate_predictive_alert(profile_label, month_label, result)
    return {"prediction": result, "alert": alert}


@traceable(name="fleet_overview_turn", tags=["heat-pump-copilot", "mode:predictive_early_warning"])
def fleet_overview_turn(counts: dict, flagged_units: list[dict]) -> dict:
    """One fleet-summary request: the fleet-wide table itself is scored
    deterministically by core/fleet.py before this is called (free,
    instant, no need to trace); this wraps only the LLM executive-summary
    call, so it's traced consistently with the other two LLM call sites."""
    return llm.generate_fleet_summary(counts, flagged_units)
