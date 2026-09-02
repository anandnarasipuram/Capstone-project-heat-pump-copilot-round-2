"""OpenAI classification/generation layer — the "core AI capability" the
Round 2 brief requires to actually run. Three call sites, one shared
JSON-mode helper:

  1. classify_symptom      — Mode 1 (Fault Triage Copilot), the flagship
  2. summarize_checklist    — Mode 2 (Commissioning-Completeness Checker)
  3. generate_predictive_alert — Mode 3 (COP-Drop Early-Warning)

Every function fails soft with a documented, non-silent safe default —
same principle as the POC's "Parse OpenAI Response" node ("if the model
output can't be parsed, escalate rather than guess — never silently
default to 'no action needed'"). The returned dict always carries
`ai_generated: bool` so app.py can show the user which mode produced
the text on screen — a fallback is labeled as a fallback, never
presented as if it were a real model response.

Every call site is traced to LangSmith via core/tracing.py — each public
function here is one inspectable trace (exact prompt sent, raw model
output, latency, token usage), the Round 2 replacement for the POC's
"Log to Monitoring (LangSmith)" placeholder node. See
../mvp_documentation.md, "Monitoring / LangSmith tracing".
"""
from __future__ import annotations

import json
import os
from typing import Optional

from .tracing import traceable, wrap_openai

DEFAULT_CHAT_MODEL = "gpt-4o-mini"

CLASSIFICATION_SYSTEM_PROMPT = """You are a triage assistant for a heat pump manufacturer's field installers.
Classify the installer's reported symptom into exactly one category:
- "hardware_fault": a physical unit/component fault requiring a certified technician
- "connectivity_issue": HEMS/app/pairing/network problem, no hardware visit needed
- "installer_error": a commissioning/installation step (wiring, pressure, flow, electrical supply) needs correcting on site

If manual excerpts are provided, treat them as authoritative over your own general knowledge, and cite them in your reasoning.
The installer may specify which heat pump model they're working on — use it to make your guidance read as specific to their situation (e.g. referencing the model in your reply), but never invent model-specific fault codes, thresholds, or behavior that isn't actually present in the manual excerpts provided. If the model is "Not specified" or no excerpts are provided, answer from the symptom text and your general HVAC knowledge as usual.
Reply in the same language the installer used.
Respond ONLY as JSON: {"category": "...", "message": "concrete next-step guidance or escalation instruction, 1-3 sentences", "confidence": 0.0-1.0}
Never issue autonomous repair instructions for hardware faults beyond "escalate to a certified technician" — this is advisory support for a human installer, not an autonomous action."""

CHECKLIST_SYSTEM_PROMPT = """You are a commissioning sign-off assistant for a heat pump manufacturer.
Given a completed/incomplete checklist for a field installation, write a short (2-4 sentence) plain-language summary for the installer: whether the job is ready to sign off, and if not, exactly what to fix first and why it matters (cite the fault code it would otherwise surface as, if given).
Respond ONLY as JSON: {"summary": "..."}"""

PREDICTIVE_SYSTEM_PROMPT = """You are a predictive-maintenance assistant for a heat pump manufacturer's support/service planning team.
Given a unit's observed coefficient-of-performance (COP) reading versus the expected seasonal baseline, write a short (2-3 sentence) plain-language early-warning note: what the deviation means, and the recommended next step (no action / monitor next reading / schedule an inspection).
Respond ONLY as JSON: {"note": "..."}"""

FLEET_SUMMARY_SYSTEM_PROMPT = """You are a service-planning assistant summarizing the health of an installed heat pump fleet for a non-technical business owner.
Given counts of units by status (normal / watch / early_warning) and details of the units needing attention, write a short (2-4 sentence) plain-language executive summary: overall fleet health, how many units need attention now vs. soon, and the recommended next action. Be concrete about which units/models are most urgent if any are early_warning.
Respond ONLY as JSON: {"summary": "..."}"""


class LlmError(Exception):
    """Raised for a genuine configuration problem (no API key). Callers
    catch it to show a setup banner rather than crash."""


def _get_client():
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise LlmError("OPENAI_API_KEY is not set — see mvp/.env.example.")
    # wrap_openai only actually traces when LangSmith tracing is enabled
    # (see core/tracing.py) — with no LANGSMITH_API_KEY it wraps the
    # client but makes no LangSmith network calls, so this is always safe.
    return wrap_openai(OpenAI(api_key=api_key))


def _chat_json(system_prompt: str, user_prompt: str) -> Optional[dict]:
    """Returns the parsed JSON dict, or None if the call/parse failed —
    including a missing API key. Every public function in this module
    therefore always returns a dict with `ai_generated` set; callers
    never need to catch LlmError themselves. is_configured() below is
    how app.py shows a setup banner instead of silently degrading."""
    model = os.environ.get("OPENAI_CHAT_MODEL", DEFAULT_CHAT_MODEL)
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return json.loads(response.choices[0].message.content)
    except Exception:  # noqa: BLE001 — any config/API/parse failure, handled by each call site's safe default
        return None


def is_configured() -> bool:
    """Cheap presence check (not a live API call) for the sidebar status
    indicator — does OPENAI_API_KEY look set at all."""
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


@traceable(name="classify_symptom", tags=["heat-pump-copilot", "mode:fault_triage"])
def classify_symptom(
    symptom: str, manual_excerpts: list[str], manual_sources: list[str], model: str = "Not specified"
) -> dict:
    context_block = (
        "\n".join(f"- {excerpt}" for excerpt in manual_excerpts)
        if manual_excerpts
        else "(no matching manual excerpt found — classify from the symptom alone)"
    )
    user_prompt = (
        f"Heat pump model: {model}\n\n"
        f"Installer's reported symptom:\n{symptom}\n\nManual excerpts:\n{context_block}"
    )

    parsed = _chat_json(CLASSIFICATION_SYSTEM_PROMPT, user_prompt)
    if parsed and "category" in parsed and "message" in parsed:
        return {
            "category": parsed["category"],
            "message": parsed["message"],
            "confidence": parsed.get("confidence"),
            "source": "llm",
            "manual_sources": manual_sources,
            "ai_generated": True,
            "model": model,
        }

    # Safe default — mirrors the POC's "Parse OpenAI Response" fallback:
    # escalate rather than guess, never silently "no action needed".
    return {
        "category": "hardware_fault",
        "message": "Could not get a reliable model response — escalating to a senior technician as a safe default.",
        "confidence": 0.0,
        "source": "llm",
        "manual_sources": manual_sources,
        "ai_generated": False,
        "model": model,
    }


@traceable(name="summarize_checklist", tags=["heat-pump-copilot", "mode:commissioning_checker"])
def summarize_checklist(model: str, firmware: str, checklist_result: dict) -> dict:
    missing = ", ".join(
        f"{item['label']} (would otherwise surface as {item['manual_ref']})" if item["manual_ref"] else item["label"]
        for item in checklist_result["missing_required"]
    ) or "none"
    user_prompt = (
        f"Unit: {model}, firmware {firmware}\n"
        f"Completeness: {checklist_result['completeness_pct']}%\n"
        f"Missing required steps: {missing}\n"
        f"Sign-off ready: {checklist_result['sign_off_ready']}"
    )
    parsed = _chat_json(CHECKLIST_SYSTEM_PROMPT, user_prompt)
    if parsed and "summary" in parsed:
        return {"summary": parsed["summary"], "ai_generated": True}

    # Deterministic fallback — still useful, clearly labeled as non-AI in app.py.
    if checklist_result["sign_off_ready"]:
        summary = f"All required commissioning steps confirmed ({checklist_result['completeness_pct']}% complete). Ready to sign off."
    else:
        items = "; ".join(item["label"] for item in checklist_result["missing_required"])
        summary = f"Not ready to sign off — {len(checklist_result['missing_required'])} required step(s) outstanding: {items}."
    return {"summary": summary, "ai_generated": False}


@traceable(name="generate_predictive_alert", tags=["heat-pump-copilot", "mode:predictive_early_warning"])
def generate_predictive_alert(profile_label: str, month_label: str, predictive_result: dict) -> dict:
    user_prompt = (
        f"Unit profile: {profile_label}\n"
        f"Month: {month_label}\n"
        f"Expected seasonal COP: {predictive_result['expected_cop']}\n"
        f"Observed COP: {predictive_result['observed_cop']}\n"
        f"Deviation: {predictive_result['deviation_pct']}% below baseline\n"
        f"Severity: {predictive_result['severity']}"
    )
    parsed = _chat_json(PREDICTIVE_SYSTEM_PROMPT, user_prompt)
    if parsed and "note" in parsed:
        return {"note": parsed["note"], "ai_generated": True}

    from .predictive import SEVERITY_LABELS

    note = (
        f"{SEVERITY_LABELS[predictive_result['severity']]} — observed COP is "
        f"{predictive_result['deviation_pct']}% below the {month_label} baseline "
        f"for {profile_label} ({predictive_result['expected_cop']} expected vs. "
        f"{predictive_result['observed_cop']} observed)."
    )
    return {"note": note, "ai_generated": False}


@traceable(name="generate_fleet_summary", tags=["heat-pump-copilot", "mode:predictive_early_warning"])
def generate_fleet_summary(counts: dict, flagged_units: list[dict]) -> dict:
    units_desc = (
        "\n".join(
            f"- {u['unit_id']} ({u['model']}, {u['region']}): {u['deviation_pct']}% below baseline — {u['notes']}"
            for u in flagged_units
        )
        or "none"
    )
    user_prompt = (
        f"Fleet status counts: {counts['normal']} normal, {counts['watch']} watch, "
        f"{counts['early_warning']} early warning.\n"
        f"Units needing attention:\n{units_desc}"
    )
    parsed = _chat_json(FLEET_SUMMARY_SYSTEM_PROMPT, user_prompt)
    if parsed and "summary" in parsed:
        return {"summary": parsed["summary"], "ai_generated": True}

    total = sum(counts.values())
    needs_attention = counts["watch"] + counts["early_warning"]
    summary = (
        f"{counts['normal']} of {total} units are operating normally. {needs_attention} unit(s) show reduced "
        f"efficiency ({counts['early_warning']} urgent, {counts['watch']} to monitor) — schedule inspections "
        f"for the urgent units first."
    )
    return {"summary": summary, "ai_generated": False}
