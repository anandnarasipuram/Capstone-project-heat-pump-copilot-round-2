"""LLM-as-judge over real LangSmith traces — the correctness/hallucination
evaluator instructor feedback (Round 2) asked for. Shared by two callers so
neither can silently drift from the other:

  - scripts/judge_traces.py — CLI entry point, judges a batch, prints to
    stdout, exits.
  - app.py's "📊 Judge Reports" page — same judging logic behind a "Run
    judge on recent traces" button, plus a read-only view of whatever's
    already been judged (existing LangSmith feedback — no new judge-model
    calls to just look at a chart).

Why this lives in core/ and not just scripts/: the app's Reports page has
to use the *exact* same prompt, model and scoring definition as the CLI
script, or the numbers on screen would quietly mean something different
from the numbers the script prints — two competing implementations of
"what counts as correct" is worse than one. See mvp_documentation.md,
"LLM-as-judge evaluation" and "Judge Reports page".

What this is not: a general-purpose AI-governance audit tool. It scores
exactly two dimensions (correctness against retrieved evidence,
hallucination beyond it) for one call site (classify_symptom) — chosen
because those are the two things a second LLM call can actually assess
from a trace's own inputs/outputs, not because they're a complete audit.
"""
from __future__ import annotations

import json
import os
from typing import Optional

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gpt-4o-mini")
JUDGED_RUN_NAME = "classify_symptom"

JUDGE_SYSTEM_PROMPT = """You are an impartial technical auditor reviewing a heat pump fault-triage AI's response, for a manufacturer's quality-assurance process. You are NOT the same system that produced the response — judge it independently and skeptically.

Given the installer's reported symptom, the manual excerpts the AI had access to (if any), and the AI's classification + response, score:

1. "correctness" (0.0-1.0): does the category (hardware_fault / connectivity_issue / installer_error) and the guidance reasonably match what the manual excerpts support — or, if no excerpts were provided, standard HVAC domain knowledge? 1.0 = fully correct and well-supported, 0.0 = wrong category or guidance that contradicts the excerpts.
2. "hallucination" (0.0-1.0): does the response state any specific fact — a part name, a numeric threshold, a specific procedure — that is NOT actually present in the manual excerpts and goes beyond reasonable general HVAC knowledge? 0.0 = nothing fabricated, 1.0 = significant invented specifics presented as fact.

Respond ONLY as JSON: {"correctness": 0.0-1.0, "hallucination": 0.0-1.0, "reasoning": "1-2 sentence explanation citing what supported or undermined the score"}"""


def build_user_prompt(run) -> str:
    inputs = run.inputs or {}
    outputs = run.outputs or {}
    symptom = inputs.get("symptom", "(not captured)")
    excerpts = inputs.get("manual_excerpts") or []
    excerpts_block = "\n".join(f"- {e}" for e in excerpts) if excerpts else "(none provided)"
    category = outputs.get("category", "(none)")
    message = outputs.get("message", "(none)")
    return (
        f"Installer's reported symptom:\n{symptom}\n\n"
        f"Manual excerpts available to the AI:\n{excerpts_block}\n\n"
        f"AI's classification: {category}\n"
        f"AI's response: {message}"
    )


def judge_run(oai_client, run) -> Optional[dict]:
    try:
        response = oai_client.chat.completions.create(
            model=JUDGE_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(run)},
            ],
        )
        return json.loads(response.choices[0].message.content)
    except Exception:  # noqa: BLE001 — a bad judge call shouldn't kill the whole batch
        return None


def fetch_judgeable_runs(ls_client, project: str, limit: int) -> list:
    """Recent classify_symptom runs that have outputs, most-recent-first.
    LangSmith's list_runs rejects a single-page `limit` above 100 (hit for
    real during development), so this fetches a buffer — to account for
    runs still missing outputs or of the wrong name — capped at that
    ceiling rather than requesting exactly what's needed and hoping it's
    under 100."""
    fetch_limit = min(max(limit * 3, 20), 100)
    all_runs = list(ls_client.list_runs(project_name=project, limit=fetch_limit))
    return [r for r in all_runs if r.name == JUDGED_RUN_NAME and r.outputs][:limit]


def _row_from_run(run, correctness: Optional[float], hallucination: Optional[float], reasoning: str) -> dict:
    inputs = run.inputs or {}
    outputs = run.outputs or {}
    started_at = getattr(run, "start_time", None)
    return {
        "run_id": str(run.id),
        "started_at": started_at.isoformat() if started_at else None,
        "symptom": inputs.get("symptom", "(not captured)"),
        "category": outputs.get("category", "(none)"),
        "message": outputs.get("message", ""),
        "correctness": correctness,
        "hallucination": hallucination,
        "reasoning": reasoning,
    }


def judge_and_record(ls_client, oai_client, run) -> Optional[dict]:
    """Judges one run and posts both scores back to LangSmith as feedback
    on that run (Client.create_feedback) — so they show up next to the
    trace in LangSmith's own UI, not just in this app. Returns None (skip,
    don't count it) if the judge call itself failed to return usable
    JSON — same behavior the CLI script always had."""
    verdict = judge_run(oai_client, run)
    if not verdict:
        return None
    correctness = float(verdict.get("correctness", 0.0))
    hallucination = float(verdict.get("hallucination", 0.0))
    reasoning = verdict.get("reasoning", "")
    ls_client.create_feedback(run_id=run.id, key="llm_judge_correctness", score=correctness, comment=reasoning)
    ls_client.create_feedback(run_id=run.id, key="llm_judge_hallucination", score=hallucination, comment=reasoning)
    return _row_from_run(run, correctness, hallucination, reasoning)


def run_judge_batch(ls_client, oai_client, project: str, limit: int) -> list[dict]:
    """High-level batch entry point — both scripts/judge_traces.py and the
    app's 'Run judge on recent traces' button call this and nothing lower
    level, so the two callers can never diverge on which runs get fetched
    or how a failed judge call is handled."""
    runs = fetch_judgeable_runs(ls_client, project, limit)
    results = []
    for run in runs:
        row = judge_and_record(ls_client, oai_client, run)
        if row:
            results.append(row)
    return results


def fetch_judged_results(ls_client, project: str, run_limit: int = 30) -> list[dict]:
    """Read-only: pulls recent classify_symptom runs and, for each,
    whatever llm_judge_* feedback already exists on it (posted by an
    earlier run_judge_batch call — this session's button, a previous
    session's, or the CLI script) — makes no new judge-model calls. Runs
    with no judge feedback yet are silently skipped; use 'Run judge on
    recent traces' to generate scores for them.

    One list_feedback call per run — LangSmith has no bulk "feedback for
    these N runs" endpoint — so this is fine at demo scale (run_limit
    defaults to 30) and deliberately not built to paginate past it."""
    runs = fetch_judgeable_runs(ls_client, project, run_limit)
    results = []
    for run in runs:
        feedback = list(ls_client.list_feedback(run_ids=[run.id]))
        correctness = next((f.score for f in feedback if f.key == "llm_judge_correctness"), None)
        hallucination = next((f.score for f in feedback if f.key == "llm_judge_hallucination"), None)
        reasoning = next((f.comment for f in feedback if f.key == "llm_judge_correctness" and f.comment), "") or ""
        if correctness is None and hallucination is None:
            continue
        results.append(_row_from_run(run, correctness, hallucination, reasoning))
    return results
