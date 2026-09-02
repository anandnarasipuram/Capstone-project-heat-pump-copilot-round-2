# MVP Documentation — Heat Pump Copilot

> Round 2 required deliverable: *"a functional product beyond the POC... the core AI capability has to actually run."*
> Builds directly on the Round 1 n8n POC — see [../poc/poc_documentation.md](../poc/poc_documentation.md) — and on all three use-case candidates scoped in [../research/use_cases.md](../research/use_cases.md), which this MVP implements as four tabs of one small app rather than three separate half-built products (the 4th, Installed Fleet Overview, is a portfolio view of the 3rd — see below).

## What this is

A single Streamlit app (`app.py`) with four tabs, run from one `streamlit run` command:

| Mode | Use case (from [research/use_cases.md](../research/use_cases.md)) | Lifecycle stage | Status |
|---|---|---|---|
| 🩺 **Fault Triage Copilot** | Candidate #1 — the Round 1 flagship | Reactive | Full RAG + LLM pipeline, chat UI |
| ✅ **Commissioning Checker** | Candidate #2 | Preventive | Deterministic checklist + LLM sign-off summary |
| 📉 **COP-Drop Early-Warning** | Candidate #3 | Predictive | Statistical baseline comparison + LLM alert note, single unit |
| 🏠 **Installed Fleet Overview** | Candidate #3, portfolio view | Predictive | Same mechanism as above, run across a demo fleet at once — see below |

**The core AI capability that has to "actually run"** is Mode 1's pipeline: fault-code lookup → **Pinecone vector search over OpenAI embeddings of the manual knowledge base** → **OpenAI chat-completion classification, grounded in whatever the retrieval step found**. This is the concrete Round 2 upgrade the POC's own docs called for (see [poc/poc_documentation.md](../poc/poc_documentation.md), "Language" section): the POC's keyword match is replaced by real multilingual embeddings, so a German-phrased symptom retrieves the right English-language manual excerpt on semantic similarity, not exact keyword overlap.

Modes 2–4 reuse the same OpenAI classification layer (`core/llm.py`) to turn a deterministic result into a natural-language summary/alert — one shared AI capability, four applications of it, not four separate models.

**Why a 4th tab, not just 3 modes:** the single-unit 📉 tab is the honest, technical demonstration of the predictive mechanism; the 🏠 tab exists purely to make that mechanism *legible to a non-technical audience* — a business decision-maker grasps "3 of 18 units need attention now" in one glance far faster than watching one slider move. Same underlying logic (`core/predictive.py` via `core/fleet.py`), presented as a portfolio instead of a single reading.

## Architecture

```
mvp/
├── app.py                    # Streamlit UI — 4 tabs, chat + forms; calls only core/pipeline.py
├── core/
│   ├── pipeline.py            # orchestration + tracing boundary — one function per mode, see below
│   ├── fault_lookup.py       # deterministic fault-code regex + table (ported 1:1 from the POC)
│   ├── keyword_fallback.py   # zero-dependency retrieval fallback (ported 1:1 from the POC)
│   ├── rag.py                 # Pinecone + OpenAI embeddings — the real RAG upgrade
│   ├── llm.py                  # OpenAI classification/generation, shared by all 3 modes
│   ├── checklist.py            # Mode 2 — pure evaluation logic
│   ├── predictive.py           # Mode 3 — pure COP-deviation logic (single unit)
│   ├── fleet.py                 # Mode 4 — pure fleet-wide scoring, reuses predictive.py
│   ├── data_loader.py          # loads data/manuals/*.json + data/when2heat_DE_subset.csv
│   └── tracing.py              # LangSmith setup — see "Monitoring" below
├── scripts/
│   └── ingest_manuals.py     # one-time: embeds manuals, upserts into Pinecone
├── tests/
│   └── test_core_logic.py    # 20 offline unit tests, no API keys needed
├── requirements.txt
├── .env.example
└── mvp_documentation.md      # this file
```

**Design principle:** every module that touches money or randomness (an LLM/embedding call, a Pinecone query) is isolated from the pure logic that doesn't (fault-code regex matching, checklist scoring, COP-deviation math, fleet scoring). That's what makes 20 of the app's behaviors unit-testable with zero API keys, and it's the same separation the POC used between its deterministic lookup node and its LLM classification node.

### Mode 1 — Fault Triage Copilot, in detail

```
installer message
      │
      ▼
core/fault_lookup.py — regex-extract a fault code (E4, F532, F.9998, ...)
      │
      ├─ known code? ──► instant answer, no API call, confidence 1.0, source "lookup"
      │
      └─ no code / unknown code
              │
              ▼
      core/rag.py — embed the query (OpenAI text-embedding-3-small),
      similarity search against the Pinecone index built by
      scripts/ingest_manuals.py from data/manuals/*.json
              │
              ├─ Pinecone/OpenAI not configured, or the call fails
              │        │
              │        ▼
              │   core/keyword_fallback.py — POC's original lexical match,
              │   as a zero-dependency safety net (never crashes the demo)
              │
              ▼
      core/llm.py:classify_symptom() — OpenAI chat completion, JSON mode,
      system prompt instructs the model to treat manual excerpts as
      authoritative and reply in the installer's own language
              │
              ▼
      structured result: {category, message, confidence, source, manual_sources}
      rendered as a chat card with the "AI-suggested triage, confirm
      before acting" disclaimer — never an autonomous instruction
```

### Modes 2, 3, and 4

- **Commissioning Checker** (`core/checklist.py`): a fixed list of commissioning steps, each citing the fault code it would otherwise surface as later (e.g. unchecked eBUS wiring → F.9998). Deterministic scoring decides sign-off readiness; `core/llm.py:summarize_checklist()` turns that into a short natural-language summary for the installer.
- **COP-Drop Early-Warning** (`core/predictive.py`): aggregates the public [When2Heat Germany COP dataset](../data/dataset_documentation.md) into a monthly seasonal baseline per heat-pump profile, compares a reported reading against it, and flags `normal` / `watch` / `early_warning` by a stated percentage-deviation threshold (documented as an assumption pending real fleet data — see [../roi_risk_assessment.md](../roi_risk_assessment.md)). `core/llm.py:generate_predictive_alert()` narrates the finding.
- **Installed Fleet Overview** (`core/fleet.py`): runs the exact same `predictive.evaluate_reading()` check across a small, hand-curated demo fleet of 18 units (see [../data/installed_fleet_documentation.md](../data/installed_fleet_documentation.md)) instead of one reading at a time — `evaluate_fleet()` computes each unit's `observed_cop` from a stored `target_deviation_pct` against the *live* baseline (never a stored raw number, so it can't drift out of sync), and `fleet_summary_counts()` rolls that up into 🟢/🟡/🔴 counts for the metrics row. `core/llm.py:generate_fleet_summary()` optionally narrates the whole fleet in one call (only when the "Generate fleet summary" button is clicked — not on every page load, to keep it cheap).

## Monitoring — LangSmith tracing (every interaction, not a placeholder)

The POC's n8n workflow has a `Log to Monitoring (LangSmith)` node that's explicitly a **placeholder** (a NoOp — see [../poc/poc_documentation.md](../poc/poc_documentation.md)), and Round 1 shipped LangSmith evidence as a separate, small [trace-sample script](../langsmith/run_trace_sample.py) run by hand. The MVP wires real, continuous tracing into the app itself instead — every fault-triage, checklist, and predictive-alert interaction produces a live LangSmith trace, so the exact prompt sent, the raw model output, latency, and token usage are all inspectable later, not just during a demo. This is what makes it possible to pull up real usage data for a discussion with Chleo (or any pilot customer) after the fact, rather than only being able to describe what the system does.

**Architecture — `core/pipeline.py` is the single tracing boundary.** `app.py` never calls `core/llm.py` or `core/rag.py` directly; it calls one of three `@traceable`-decorated orchestration functions (`fault_triage_turn`, `commissioning_turn`, `predictive_turn`), each covering one whole user interaction as a single parent trace, with the steps inside it (deterministic lookup, retrieval, classification, the underlying OpenAI call) nested as child spans — not three unrelated traces a reviewer has to manually stitch back together. `core/tracing.py` centralizes the setup (`langsmith`'s `traceable` decorator + `wrap_openai`) so every module imports it from one place.

**Fails soft, same as everywhere else in this app:** with no `LANGSMITH_API_KEY`, `traceable` is a normal passthrough decorator and `wrap_openai` returns the client unwrapped — tracing is simply off, nothing else in the app changes behavior, and no error is raised. The sidebar shows a 🟢/🟡 status indicator for it, same pattern as the OpenAI/Pinecone indicators.

**Confirmed live** (this was actually run, not just written): with `LANGSMITH_API_KEY` set, all three modes were exercised and verified in the LangSmith UI/API to produce exactly the nested structure designed above —

```
fault_triage_turn                         (root — one per chat message)
├── deterministic_lookup                  (checked first, always)
├── retrieve_manual_context               (only reached if no fault code matched)
└── classify_symptom
    └── ChatOpenAI                        (the actual OpenAI call — wrap_openai's span)

commissioning_turn                        (root — one per checklist submission)
└── summarize_checklist
    └── ChatOpenAI

predictive_turn                           (root — one per COP-reading evaluation)
└── generate_predictive_alert
    └── ChatOpenAI
```

A message resolved entirely by the deterministic fault-code lookup (e.g. `E4`) produces a root trace with **only** the `deterministic_lookup` child — no retrieval, no classification, no LLM call — confirming the free/instant path stays free and instant, and that "everything traced" doesn't mean "everything calls an LLM."

**One real setup gotcha worth knowing** (the exact one Round 1's trace sample already hit — see [../langsmith/monitoring_notes.md](../langsmith/monitoring_notes.md)): a LangSmith workspace on the **EU region** returns `403 Forbidden` on every trace unless `LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com` is set explicitly in `.env` — the classification/summary/alert itself still succeeds either way (tracing failure never breaks the underlying feature), but no traces reach the LangSmith UI until this is set. Check this first if traces aren't showing up.

**How to view traces:** open [smith.langchain.com](https://smith.langchain.com) (or the EU equivalent), select the project named by `LANGSMITH_PROJECT` (defaults to `heat-pump-copilot-round2`), and every interaction since `LANGSMITH_API_KEY` was set will be listed there, filterable by the `mode:*` tags each root trace carries.

## How to run it

```bash
cd mvp
python -m venv venv && source venv/bin/activate   # or your preferred env manager
pip install -r requirements.txt
cp .env.example .env
```

**Zero-config smoke test** (no API keys at all — proves the app runs before wiring anything):
```bash
streamlit run app.py
```
Open the app, stay on 🩺 Fault Triage Copilot, and try `Low refrigerant pressure alarm, error code E4` — it resolves instantly via the deterministic lookup table, no key needed. Modes 2–4 also load and compute their deterministic results (checklist score, COP deviation, seasonal chart, the full fleet table + counts) with zero keys; only the AI-generated narrative text falls back to a clearly-labeled template (see "Error handling" below).

**Full AI capability** (what Round 2 actually asks for):
1. Fill in `OPENAI_API_KEY` in `.env`.
2. Fill in `PINECONE_API_KEY` in `.env` (free tier is sufficient for this manual corpus).
3. One-time ingestion — embeds the 16 manual entries in `data/manuals/*.json` and upserts them into a new Pinecone serverless index:
   ```bash
   python scripts/ingest_manuals.py
   ```
4. `streamlit run app.py` again. The sidebar's configuration status flips to 🟢 for both OpenAI and Pinecone. Try a free-text symptom with no fault code, e.g. `No comms from the outdoor unit, controller not responding`, to see live embeddings retrieval + grounded LLM classification.
5. Optional: fill in `LANGSMITH_API_KEY` in `.env` to trace every interaction — see "Monitoring — LangSmith tracing" below for what gets captured and a real setup gotcha to check first.

### Confirmed live (this is not a theoretical pipeline)

The full RAG + classification pipeline was run end-to-end against real OpenAI + Pinecone during development, not just unit-tested offline:

- `scripts/ingest_manuals.py` created the `heat-pump-copilot-manuals` Pinecone index and embedded all 16 manual entries.
- `core.rag.retrieve_manual_context("No comms from the outdoor unit, controller not responding")` returned the F.9998 eBUS-fault excerpt as its top semantic match — the same grounding the POC's keyword matcher found, now via real embeddings similarity instead of substring matching.
- `core.llm.classify_symptom(...)` on that same symptom returned `category: installer_error`, correct eBUS wiring guidance, `confidence: 0.9`, `ai_generated: True`.
- The same call on the German symptom `"Wasserdurchfluss Problem, Pumpe steht"` retrieved the right English-language manual excerpt (`F.532`/`F.788` flow-related entries) on semantic similarity — no German keywords hand-coded anywhere — and the model replied **in German** with correct fix guidance. This is the concrete resolution of the POC's stated language limitation (see [../poc/poc_documentation.md](../poc/poc_documentation.md), "Language" section: *"a differently-phrased German symptom simply won't match [the keyword list]"*) — it no longer needs to match a hand-picked keyword at all.
- `core.llm.summarize_checklist(...)` and `core.llm.generate_predictive_alert(...)` were both exercised live too, each returning `ai_generated: True` with correct, on-topic natural-language output (the checklist summary correctly cited the F.9998 fault code for an unchecked eBUS item).

## Error handling (what "basic error handling" means here)

- **Every LLM/embedding/Pinecone call is wrapped and fails soft**, never crashes the app: `core/llm.py`'s three public functions always return a dict with an `ai_generated: bool` flag — `False` means the deterministic fallback text is showing, and the UI says so explicitly (`⚠️ Deterministic ... — add OPENAI_API_KEY ...`). This mirrors the POC's own safe-default principle in its "Parse OpenAI Response" node: *"if the model output can't be parsed, escalate rather than guess — never silently default to 'no action needed'."*
- **Retrieval degrades in two steps, not one**: Pinecone RAG → keyword fallback → (worst case) no manual grounding at all, with the LLM classifying from the symptom text alone — exactly the POC's own documented worst case.
- **A top-level `try/except` around each mode's main action** catches anything unanticipated (a malformed API response shape, a network timeout) and shows `st.error(...)` instead of an unhandled traceback.
- **Config presence (not validity) is checked upfront** and shown in the sidebar as 🟢/🔴/🟡, so a missing key reads as an obvious status indicator rather than a mid-conversation crash.

## Testing

```bash
python -m pytest tests/ -v
```

20 tests cover the pure-logic modules offline: fault-code extraction/normalization against the exact worked examples in [poc/poc_documentation.md](../poc/poc_documentation.md), checklist scoring, and COP-deviation severity thresholds. They do **not** call OpenAI or Pinecone by design (no API keys needed to run them) — the live LLM/RAG path is verified separately by actually running the app/pipeline with real keys, which was done during development (see "Confirmed live" above) and should be re-run before any live demo or pilot go-live to confirm current model/vendor behavior.

`core/llm.py`'s safe-default fallback paths (missing key, and a simulated bad key) were manually verified during development to confirm they return the documented fallback shape rather than raising — see the git history for that verification run.

## Limits vs. production (stated openly)

- **Manual corpus is small and representative, not Chleo's own documentation** — same limitation as the POC (16 entries total: 8 Vaillant fault codes + 8 keyword-guide entries), see [../data/manuals/README.md](../data/manuals/README.md).
- **COP-drop thresholds (10%/20% deviation) are a stated assumption**, not calibrated against real fault outcomes — no public dataset pairs COP deviation with confirmed faults (see [../research/opportunities_risks.md](../research/opportunities_risks.md)); a real deployment would tune these against the manufacturer's own service-ticket history once available.
- **The Commissioning Checker's item list is illustrative** (7 items derived from the fault codes already in the knowledge base), not a validated installer sign-off form — a production version would be built with the manufacturer's QA team.
- **The Installed Fleet Overview tab is a demo table, not live telemetry** — 18 hand-curated units, deliberately spanning all 3 flags so the mechanism is visible in one glance (see [../data/installed_fleet_documentation.md](../data/installed_fleet_documentation.md)). A production version replaces `data/synthetic_installed_fleet.csv` with a real feed keyed to actual installed units, once that telemetry exists.
- **Single-session chat history** — `st.session_state` only, nothing persisted between runs or shared across installers. A pilot would need a lightweight backing store (even just a CSV/SQLite log) for the false-hardware-fault and first-visit-fix-rate metrics the Round 1 dashboard tracks.
- **No authentication** — anyone who can reach the running app can use it. Fine for an instructor demo or a single-installer trial; not fine for a multi-tenant pilot (see [../compliance/gdpr_documentation.md](../compliance/gdpr_documentation.md) for how this changes once real installer identities are involved).
- **Pinecone/OpenAI cost is per-query**, unbounded by this app — a production deployment would add basic rate limiting, matching the POC's own stated gap ("no retry/rate-limit handling on the OpenAI HTTP Request node").
