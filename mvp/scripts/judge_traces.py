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
impartial judge (correctness, hallucination — see core/judge.py for the
scoring definitions and prompt).

Scores are posted back to LangSmith as feedback on the *original* run,
so they appear right next to each trace in the UI. They're also what
powers the app's "📊 Judge Reports" page (app.py) — this script and that
page share the exact same judging logic (core/judge.py), so running this
from the command line and clicking "Run judge on recent traces" in the
app do the same thing. See mvp_documentation.md, "LLM-as-judge
evaluation".

Usage:
    cd mvp
    python scripts/judge_traces.py                # judges up to 20 recent runs
    python scripts/judge_traces.py --limit 50
    python scripts/judge_traces.py --project heat-pump-copilot-round2
"""
from __future__ import annotations

import argparse
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

from core import judge  # noqa: E402


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
    runs = judge.fetch_judgeable_runs(ls_client, args.project, args.limit)
    print(f"  {len(runs)} judgeable runs found.")
    if len(runs) == args.limit:
        print(f"  (Hit the fetch ceiling — there may be more than {args.limit} available; this is a demo-scale script, not built to paginate past it.)")

    if not runs:
        print("Nothing to judge yet — run the app (Mode 1, a free-text symptom) to generate some traces first.")
        return

    correctness_scores, hallucination_scores = [], []
    for i, run in enumerate(runs, start=1):
        symptom_preview = (run.inputs or {}).get("symptom", "")[:60]
        print(f"[{i}/{len(runs)}] {symptom_preview!r} ...")
        row = judge.judge_and_record(ls_client, oai_client, run)
        if not row:
            print("  [judge call failed — skipped]")
            continue

        correctness_scores.append(row["correctness"])
        hallucination_scores.append(row["hallucination"])
        print(f"    correctness={row['correctness']:.2f}  hallucination={row['hallucination']:.2f}  — {row['reasoning']}")

    if correctness_scores:
        avg_correctness = sum(correctness_scores) / len(correctness_scores)
        avg_hallucination = sum(hallucination_scores) / len(hallucination_scores)
        print()
        print(f"Judged {len(correctness_scores)} runs.")
        print(f"  Average correctness:   {avg_correctness:.2f}")
        print(f"  Average hallucination: {avg_hallucination:.2f}  (0 = none, 1 = severe)")
        print(f"Scores posted as feedback on each run — open the '{args.project}' project in LangSmith to review,")
        print(f"or run the app and open the '📊 Judge Reports' page for charts.")


if __name__ == "__main__":
    main()
