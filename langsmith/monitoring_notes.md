# LangSmith Monitoring Sample

> Script: [`run_trace_sample.py`](run_trace_sample.py) — run it yourself with your own `OPENAI_API_KEY` and `LANGSMITH_API_KEY` to generate real traces; see **How to run** below.
> **Round 2 extends this.** The MVP wires live, continuous tracing into every real interaction (not just this Round 1 sample script) — see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md), "Monitoring — LangSmith tracing." An LLM-as-judge evaluator ([../mvp/scripts/judge_traces.py](../mvp/scripts/judge_traces.py)) scores those real traces for correctness and hallucination and posts the scores back as LangSmith feedback — see that same doc, "LLM-as-judge evaluation." This file's own dataset/experiment below remains the Round 1 evidence and hasn't been re-run.

## What this monitors

The script runs the **exact same classification prompt** used in the n8n workflow's `Classify via OpenAI` node (see [n8n/workflow.json](../n8n/workflow.json) and [n8n/workflow_documentation.md](../n8n/workflow_documentation.md)) against 5 worked examples — the same fault-code/symptom pairs documented in the n8n docs and drawn from [data/synthetic_fault_dataset.csv](../data/synthetic_fault_dataset.csv). Each call is traced via LangSmith's `@traceable` decorator and `wrap_openai`, so every classification decision produces a full trace: the exact system + user prompt sent, the raw model completion, latency, and token usage.

It then does two more things a single trace can't show on its own:
1. **Creates a LangSmith Dataset** (`heat-pump-fault-triage-eval-round1`) from the same 5 examples, with the expected category as the labeled output.
2. **Runs a LangSmith Experiment** (`evaluate()`) that re-runs the classifier against that dataset and scores each prediction against the expected category with a custom evaluator (`category_correct`) — producing an aggregate accuracy view in the LangSmith UI, not just five isolated traces.

**Note on scope:** every example here goes through the LLM directly, bypassing the n8n workflow's deterministic fault-code lookup shortcut (which resolves known codes like `E4` for free, with no LLM call). That's deliberate — the point of this sample is to observe the LLM's own reasoning across all three categories, including on a case (the `E4` example) that production would normally shortcut. Seeing the LLM independently agree with the deterministic rule is itself a small validation signal, not a redundant step.

## What it shows about transparency / observability

This is the concrete answer to "how would anyone know *why* the copilot said what it said" — the transparency question the whole use case is framed around (see [research/opportunities_risks.md](../research/opportunities_risks.md) and the EU AI Act limited-risk argument in [research/sector_research.md](../research/sector_research.md)):

- **Every decision is inspectable, not just its output.** A reviewer (or Chleo) can open any trace and see the exact prompt the model received and the exact text it returned — not a black-box "the AI decided X."
- **Failures are visible, not silent.** If the model returns malformed JSON, the trace itself records the error rather than the process quietly falling back to a default outcome, which surfaces a related but distinct question: whether the fallback logic in the *n8n* workflow (which escalates safely on parse failure) is doing the right thing.
- **Accuracy is measurable, not assumed.** The experiment's `category_correct` score against a labeled dataset turns "does the classifier work" from an anecdote into a number that can be tracked over time as the dataset grows — the same pattern a Round 2 evaluation pipeline would scale up.

## Dataset / experiment link

Run — 5/5 examples classified correctly (all three categories covered):

- LangSmith project: `Heatpump copilot` (EU region workspace)
- Dataset: `heat-pump-fault-triage-eval-round1` (5 examples)
- Experiment: `heat-pump-fault-triage-41b38381`
- Link: https://eu.smith.langchain.com/o/06377b1d-767e-4e90-86c0-b75420269aef/datasets/3d9a2f7b-fd8b-489f-8ca3-574966b99f4e/compare?selectedSessions=a4455df1-cff4-4ef9-ab9d-96fa6bac675d

If link sharing is restricted for instructor access, export the run/dataset from the LangSmith UI (Project → Export, or screenshot the trace and experiment views) and drop the export/screenshots into this folder as a backup.

## How to run

```bash
pip install -r ../requirements.txt
python run_trace_sample.py
```

The script loads `../.env` automatically (via `python-dotenv`), so set `OPENAI_API_KEY` and `LANGSMITH_API_KEY` there (and optionally `LANGSMITH_PROJECT`, which defaults to `heat-pump-copilot-round1`) rather than exporting them by hand — see [.env.example](../.env.example).

If `python3` on your machine resolves to a broken/old interpreter (symptom: `Killed: 9` on even `python3 --version`, common on Apple Silicon Macs with a stale Intel-only Python still first on `PATH`), point at a working interpreter explicitly, e.g. `/opt/anaconda3/bin/python3 run_trace_sample.py`.

The script prints each classification result as it runs, then a link to the LangSmith project. Open [smith.langchain.com](https://smith.langchain.com), find the project/dataset/experiment named above, and paste the link into this file.

## Limits — stated honestly

- **Authored in an environment with no Python runtime or credentials** (same constraint noted for the Tableau and n8n builds), then **run and verified end-to-end** afterward with real `OPENAI_API_KEY` / `LANGSMITH_API_KEY` credentials — see the real dataset/experiment link above. Two real setup snags worth knowing if this is re-run elsewhere: (1) some Macs have a broken `python3` first on `PATH` (symptom: `Killed: 9` on even `python3 --version`) — point at a working interpreter explicitly if that happens; (2) LangSmith workspaces created in the **EU region** need `LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com` set explicitly, or every API call 403s even with a valid key (LangSmith's dashboard shows the right endpoint under the language/framework quickstart panel).
- **n=5 examples**, not the full 220-ticket synthetic dataset — enough to demonstrate the pattern and cover all three categories, not a statistically meaningful accuracy benchmark.
- **Only the LLM half of the pipeline is traced.** The deterministic fault-code lookup path (which would handle the majority of real hardware_fault tickets cheaply, per [n8n/workflow_documentation.md](../n8n/workflow_documentation.md)) isn't an LLM call, so there's nothing for LangSmith to trace there — that path's "transparency" is just reading the lookup table directly.
- **No real customer/installer data** — same public/synthetic-data constraint as the rest of Round 1 (see [data/dataset_documentation.md](../data/dataset_documentation.md)).
