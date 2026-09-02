"""
LangSmith monitoring sample — Heat Pump Field Commissioning & API/HEMS
Connectivity Copilot (Round 1).

Runs the *same* classification prompt used in the n8n workflow's
"Classify via OpenAI" node (see ../n8n/workflow.json and
../n8n/workflow_documentation.md) against a handful of worked examples,
traced end-to-end in LangSmith so every classification decision is
auditable: the exact prompt sent, the raw model output, latency, and
token usage.

It also creates a small LangSmith Dataset from those examples and runs a
LangSmith Experiment (evaluate()) scoring predicted vs. expected category —
this is the "dataset and/or experiment" evidence for the Round 1 deliverable.

Note: every example here is sent through the LLM directly, bypassing the
n8n workflow's deterministic fault-code lookup shortcut. The point of this
script is to observe the LLM's own reasoning across all three categories —
including ones (like the E4 example) that production would resolve for
free via the lookup table. Seeing the LLM independently agree with the
deterministic rule is itself a useful validation signal.

Usage:
    pip install -r ../requirements.txt

    # Either put these in ../.env (repo root — this script loads it
    # automatically) or export them in your shell:
    #   OPENAI_API_KEY=...
    #   LANGSMITH_API_KEY=...
    #   LANGSMITH_PROJECT=heat-pump-copilot-round1   # optional, see default below

    python run_trace_sample.py
"""

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    from openai import OpenAI
    from langsmith import Client, traceable
    from langsmith.wrappers import wrap_openai
    from langsmith.evaluation import evaluate
except ImportError:
    sys.exit(
        "Missing dependencies. Run: pip install -r ../requirements.txt\n"
        "(needs the `openai`, `langsmith`, and `python-dotenv` packages)"
    )

# Load ../.env (the repo root's .env, relative to this script — works
# regardless of the directory you run this from) before reading any keys.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Set OPENAI_API_KEY (in your environment or ../.env) before running this script.")
if not os.environ.get("LANGSMITH_API_KEY"):
    sys.exit("Set LANGSMITH_API_KEY (in your environment or ../.env) before running this script.")

os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGSMITH_PROJECT", "heat-pump-copilot-round1")

# Same system prompt as the n8n "Classify via OpenAI" HTTP Request node —
# kept in sync by hand; see CLASSIFY_SYSTEM_PROMPT in the workflow build.
SYSTEM_PROMPT = """You are a triage assistant for a heat pump manufacturer's field installers in Germany. An installer has reported a symptom that has no recognized structured fault code, so you must classify it from free text.

Classify the report into exactly one category: hardware_fault, connectivity_issue, or installer_error.
- hardware_fault: the physical unit (compressor, refrigerant circuit, electrical component) is likely broken and needs a technician visit.
- connectivity_issue: the unit itself is likely fine; the HEMS app/pairing/network connection is the problem.
- installer_error: a commissioning step (wiring, pressure fill, sensor orientation, valve position) was likely done incorrectly and can be corrected without escalation.

Then provide fix_or_escalation_action: for hardware_fault, an escalation instruction (never step-by-step repair instructions for refrigerant/electrical work — always escalate to a certified technician); for the other two categories, concrete fix guidance the installer can act on immediately.

Respond with ONLY minified JSON, no other text: {"category":"...","fix_or_escalation_action":"...","confidence":0.0}
confidence is your own estimate (0 to 1) of how certain this classification is from the text alone."""

# The first three mirror the worked examples in n8n/workflow_documentation.md
# and real rows in data/synthetic_fault_dataset.csv, so the same tickets can
# be cross-referenced across the n8n docs, this trace sample, and the
# dashboard's fault-category breakdown.
EXAMPLES = [
    {
        "inputs": {
            "model": "AS-16",
            "firmware_version": "2.4.2",
            "installer_type": "own_field_installer",
            "fault_code": "E4",
            "reported_symptom": "Low refrigerant pressure alarm, error code E4",
        },
        "expected_category": "hardware_fault",
    },
    {
        "inputs": {
            "model": "TF-12",
            "firmware_version": "3.0.0",
            "installer_type": "partner_SHK",
            "fault_code": "",
            "reported_symptom": "Smart meter gateway will not pair with the control unit",
        },
        "expected_category": "connectivity_issue",
    },
    {
        "inputs": {
            "model": "TF-08",
            "firmware_version": "2.4.0",
            "installer_type": "own_field_installer",
            "fault_code": "",
            "reported_symptom": "Unit trips on startup, wiring terminal check shows a loose connection",
        },
        "expected_category": "installer_error",
    },
    {
        "inputs": {
            "model": "AS-10",
            "firmware_version": "2.3.1",
            "installer_type": "partner_SHK",
            "fault_code": "",
            "reported_symptom": "App shows unit offline, unit itself is heating normally",
        },
        "expected_category": "connectivity_issue",
    },
    {
        "inputs": {
            "model": "TF-12",
            "firmware_version": "3.0.0",
            "installer_type": "own_field_installer",
            "fault_code": "",
            "reported_symptom": "Compressor short-cycling, no fault code shown, unit feels warm to the touch",
        },
        "expected_category": "hardware_fault",
    },
]

oai_client = wrap_openai(OpenAI())
ls_client = Client()

DATASET_NAME = "heat-pump-fault-triage-eval-round1"


@traceable(name="classify_fault_report")
def classify(inputs: dict) -> dict:
    """Send one ticket to the model and return its parsed classification.
    Mirrors the n8n 'Classify via OpenAI' node's request shape exactly."""
    user_content = (
        f"Model: {inputs['model']}\n"
        f"Firmware: {inputs['firmware_version']}\n"
        f"Installer type: {inputs['installer_type']}\n"
        f"Fault code: {inputs['fault_code'] or 'none'}\n"
        f"Reported symptom: {inputs['reported_symptom']}"
    )
    response = oai_client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    return json.loads(response.choices[0].message.content)


def run_manual_trace_pass():
    """Step 1: run each example once, printed live, traced individually."""
    print(f"--- Manual trace pass ({len(EXAMPLES)} examples) ---\n")
    correct = 0
    for i, ex in enumerate(EXAMPLES, start=1):
        symptom = ex["inputs"]["reported_symptom"]
        try:
            result = classify(ex["inputs"])
        except Exception as err:  # noqa: BLE001 — deliberately broad for a demo script
            print(f"[{i}] ERROR classifying {symptom!r}: {err}\n")
            continue
        is_correct = result.get("category") == ex["expected_category"]
        correct += int(is_correct)
        print(f'[{i}] "{symptom[:65]}"')
        print(
            f"    expected={ex['expected_category']!r}  got={result.get('category')!r}  "
            f"{'OK' if is_correct else 'MISMATCH'}"
        )
        print(f"    fix_or_escalation_action: {result.get('fix_or_escalation_action')}")
        print(f"    confidence: {result.get('confidence')}\n")
    print(f"{correct}/{len(EXAMPLES)} matched the expected category.\n")


def create_or_reuse_dataset():
    """Step 2: create a LangSmith Dataset from the same examples (or reuse
    it if this script has already been run once)."""
    existing = list(ls_client.list_datasets(dataset_name=DATASET_NAME))
    if existing:
        print(f"Reusing existing dataset '{DATASET_NAME}' ({existing[0].id})\n")
        return existing[0]

    dataset = ls_client.create_dataset(
        dataset_name=DATASET_NAME,
        description=(
            "Round 1 capstone eval set for the Heat Pump Field Commissioning "
            "& API/HEMS Connectivity Copilot's fault classification step. "
            "Mirrors data/synthetic_fault_dataset.csv archetypes."
        ),
    )
    ls_client.create_examples(
        inputs=[ex["inputs"] for ex in EXAMPLES],
        outputs=[{"category": ex["expected_category"]} for ex in EXAMPLES],
        dataset_id=dataset.id,
    )
    print(f"Created dataset '{DATASET_NAME}' ({dataset.id}) with {len(EXAMPLES)} examples.\n")
    return dataset


def category_correct(run, example) -> dict:
    """Evaluator: does the predicted category match the expected one?"""
    predicted = (run.outputs or {}).get("category")
    expected = (example.outputs or {}).get("category")
    return {"key": "category_correct", "score": int(predicted == expected)}


def run_experiment():
    """Step 3: run a LangSmith Experiment (evaluate()) against the dataset —
    this is the 'experiment' half of the Round 1 deliverable."""
    print(f"--- Running LangSmith experiment against '{DATASET_NAME}' ---\n")
    results = evaluate(
        classify,
        data=DATASET_NAME,
        evaluators=[category_correct],
        experiment_prefix="heat-pump-fault-triage",
        metadata={"use_case": "field_commissioning_connectivity_copilot", "round": "1"},
    )
    print("\nExperiment complete. Open the LangSmith UI to view the run:")
    print(f"  Project: {os.environ['LANGSMITH_PROJECT']}")
    print(f"  Dataset: {DATASET_NAME}")
    return results


if __name__ == "__main__":
    # OPENAI_API_KEY / LANGSMITH_API_KEY are already validated above, right
    # after load_dotenv() — see the top of this file.
    run_manual_trace_pass()
    create_or_reuse_dataset()
    run_experiment()
