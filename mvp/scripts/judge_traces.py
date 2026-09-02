#!/usr/bin/env python3
"""LLM-as-judge evaluation of live classify_symptom traces in LangSmith.

Instructor feedback (Round 2): evaluate the traces already being
captured (see core/tracing.py, core/pipeline.py) for correctness and
hallucination, not just capture them. This script is that evaluator.

Unlike langsmith/run_trace_sample.py (Round 1 — a fixed set of 5 worked
examples, evaluated once against a labeled dataset), this pulls *real*
classify_symptom runs already sitting in the LangSmith project — actual
installer queries and the AI's actual answers, whatever traffic the app
has generated — and scores each with a second LLM call acting as an
impartial judge:

  - correctness (0.0-1.0): does the category + guidance reasonably match
    what the manual excerpts the AI had access to (or general HVAC
    domain knowledge, if none) actually support?
  - hallucination (0.0-1.0): does the response state any specific fact
    (a part, a threshold, a procedure) not grounded in those excerpts or
    reasonable general knowledge? 0.0 = no hallucination.

Scores are posted back to LangSmith as feedback on the *original* run
(Client.create_feedback), so they appear right next to each trace in
the UI — this is meant to be read there, not just in this script's
stdout. See mvp_documentation.md, "LLM-as-judge evaluation".

Usage:
    cd mvp
    python scripts/judge_traces.py                # judges up to 20 recent runs
    python scripts/judge_traces.py --limit 50
    python scripts/judge_traces.py --project heat-pump-copilot-round2
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Set OPENAI_API_KEY (in mvp/.env) before running this script.")
if not os.environ.get("LANGSMITH_API_KEY"):
    sys.exit("Set LANGSMITH_API_KEY (in mvp/.env) before running this script — nothing to judge without it.")

from langsmith import Client  # noqa: E402
from openai import OpenAI  # noqa: E402

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gpt-4o-mini")

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


def judge_run(oai_client: OpenAI, run) -> dict | None:
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
    except Exception as exc:  # noqa: BLE001 — a bad judge call shouldn't kill the whole batch
        print(f"  [judge call failed: {exc}]")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20, help="Max number of recent runs to judge (default 20)")
    parser.add_argument(
        "--project", default=os.environ.get("LANGSMITH_PROJECT", "heat-pump-copilot-round2"),
        help="LangSmith project to pull traces from",
    )
    args = parser.parse_args()

    ls_client = Client()
    oai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    print(f"Fetching classify_symptom runs from project '{args.project}' ...")
    # LangSmith's list_runs rejects a single-page `limit` above 100 (a
    # server-side cap, hit for real with --limit 30 during development —
    # 30*4=120 400'd). Fetch a buffer (to account for runs still missing
    # outputs) capped at that ceiling rather than requesting exactly
    # what's needed and hoping it's under 100.
    fetch_limit = min(max(args.limit * 3, 20), 100)
    all_runs = list(ls_client.list_runs(project_name=args.project, limit=fetch_limit))
    runs = [r for r in all_runs if r.name == "classify_symptom" and r.outputs][: args.limit]
    print(f"  {len(runs)} judgeable runs found (of {len(all_runs)} total runs fetched).")
    if len(runs) == args.limit and fetch_limit == 100:
        print(f"  (Hit the 100-run fetch ceiling — there may be more than {args.limit} available; this is a demo-scale script, not built to paginate past that.)")

    if not runs:
        print("Nothing to judge yet — run the app (Mode 1, a free-text symptom) to generate some traces first.")
        return

    correctness_scores, hallucination_scores = [], []
    for i, run in enumerate(runs, start=1):
        symptom_preview = (run.inputs or {}).get("symptom", "")[:60]
        print(f"[{i}/{len(runs)}] {symptom_preview!r} ...")
        verdict = judge_run(oai_client, run)
        if not verdict:
            continue

        correctness = float(verdict.get("correctness", 0.0))
        hallucination = float(verdict.get("hallucination", 0.0))
        reasoning = verdict.get("reasoning", "")
        correctness_scores.append(correctness)
        hallucination_scores.append(hallucination)

        ls_client.create_feedback(
            run_id=run.id, key="llm_judge_correctness", score=correctness, comment=reasoning,
        )
        ls_client.create_feedback(
            run_id=run.id, key="llm_judge_hallucination", score=hallucination, comment=reasoning,
        )
        print(f"    correctness={correctness:.2f}  hallucination={hallucination:.2f}  — {reasoning}")

    if correctness_scores:
        avg_correctness = sum(correctness_scores) / len(correctness_scores)
        avg_hallucination = sum(hallucination_scores) / len(hallucination_scores)
        print()
        print(f"Judged {len(correctness_scores)} runs.")
        print(f"  Average correctness:   {avg_correctness:.2f}")
        print(f"  Average hallucination: {avg_hallucination:.2f}  (0 = none, 1 = severe)")
        print(f"Scores posted as feedback on each run — open the '{args.project}' project in LangSmith to review.")


if __name__ == "__main__":
    main()
