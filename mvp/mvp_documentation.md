# MVP Documentation — Heat Pump Copilot

> Round 2 required deliverable: *"a functional product beyond the POC... the core AI capability has to actually run."*
> Builds directly on the Round 1 n8n POC — see [../poc/poc_documentation.md](../poc/poc_documentation.md) — and on all three use-case candidates scoped in [../research/use_cases.md](../research/use_cases.md), which this MVP implements as three modes of one small app rather than three separate half-built products.

## What this is

A single Streamlit app (`app.py`) with three modes, run from one `streamlit run` command:

| Mode | Use case (from [research/use_cases.md](../research/use_cases.md)) | Lifecycle stage | Status |
|---|---|---|---|
| 🩺 **Fault Triage Copilot** | Candidate #1 — the Round 1 flagship | Reactive | Full RAG + LLM pipeline, chat UI |
| ✅ **Commissioning Checker** | Candidate #2 | Preventive | Deterministic checklist + LLM sign-off summary |
| 📉 **COP-Drop Early-Warning** | Candidate #3 | Predictive | Statistical baseline comparison + LLM alert note |

**The core AI capability that has to "actually run"** is Mode 1's pipeline: fault-code lookup → **Pinecone vector search over OpenAI embeddings of the manual knowledge base** → **OpenAI chat-completion classification, grounded in whatever the retrieval step found**. This is the concrete Round 2 upgrade the POC's own docs called for (see [poc/poc_documentation.md](../poc/poc_documentation.md), "Language" section): the POC's keyword match is replaced by real multilingual embeddings, so a German-phrased symptom retrieves the right English-language manual excerpt on semantic similarity, not exact keyword overlap.

Modes 2 and 3 reuse the same OpenAI classification layer (`core/llm.py`) to turn a deterministic result into a natural-language summary/alert — one shared AI capability, three applications of it, not three separate models.

## Architecture

```
mvp/
├── app.py                    # Streamlit UI — 3 modes, chat + forms
├── core/
│   ├── fault_lookup.py       # deterministic fault-code regex + table (ported 1:1 from the POC)
│   ├── keyword_fallback.py   # zero-dependency retrieval fallback (ported 1:1 from the POC)
│   ├── rag.py                 # Pinecone + OpenAI embeddings — the real RAG upgrade
│   ├── llm.py                  # OpenAI classification/generation, shared by all 3 modes
│   ├── checklist.py            # Mode 2 — pure evaluation logic
│   ├── predictive.py           # Mode 3 — pure COP-deviation logic
│   └── data_loader.py          # loads data/manuals/*.json + data/when2heat_DE_subset.csv
├── scripts/
│   └── ingest_manuals.py     # one-time: embeds manuals, upserts into Pinecone
├── tests/
│   └── test_core_logic.py    # 16 offline unit tests, no API keys needed
├── requirements.txt
├── .env.example
└── mvp_documentation.md      # this file
```

**Design principle:** every module that touches money or randomness (an LLM/embedding call, a Pinecone query) is isolated from the pure logic that doesn't (fault-code regex matching, checklist scoring, COP-deviation math). That's what makes 16 of the app's behaviors unit-testable with zero API keys, and it's the same separation the POC used between its deterministic lookup node and its LLM classification node.

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

### Modes 2 and 3

- **Commissioning Checker** (`core/checklist.py`): a fixed list of commissioning steps, each citing the fault code it would otherwise surface as later (e.g. unchecked eBUS wiring → F.9998). Deterministic scoring decides sign-off readiness; `core/llm.py:summarize_checklist()` turns that into a short natural-language summary for the installer.
- **COP-Drop Early-Warning** (`core/predictive.py`): aggregates the public [When2Heat Germany COP dataset](../data/dataset_documentation.md) into a monthly seasonal baseline per heat-pump profile, compares a reported reading against it, and flags `normal` / `watch` / `early_warning` by a stated percentage-deviation threshold (documented as an assumption pending real fleet data — see [../roi_risk_assessment.md](../roi_risk_assessment.md)). `core/llm.py:generate_predictive_alert()` narrates the finding.

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
Open the app, stay on 🩺 Fault Triage Copilot, and try `Low refrigerant pressure alarm, error code E4` — it resolves instantly via the deterministic lookup table, no key needed. Modes 2 and 3 also load and compute their deterministic results (checklist score, COP deviation, seasonal chart) with zero keys; only the AI-generated narrative text falls back to a clearly-labeled template (see "Error handling" below).

**Full AI capability** (what Round 2 actually asks for):
1. Fill in `OPENAI_API_KEY` in `.env`.
2. Fill in `PINECONE_API_KEY` in `.env` (free tier is sufficient for this manual corpus).
3. One-time ingestion — embeds the 16 manual entries in `data/manuals/*.json` and upserts them into a new Pinecone serverless index:
   ```bash
   python scripts/ingest_manuals.py
   ```
4. `streamlit run app.py` again. The sidebar's configuration status flips to 🟢 for both OpenAI and Pinecone. Try a free-text symptom with no fault code, e.g. `No comms from the outdoor unit, controller not responding`, to see live embeddings retrieval + grounded LLM classification.

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

16 tests cover the pure-logic modules offline: fault-code extraction/normalization against the exact worked examples in [poc/poc_documentation.md](../poc/poc_documentation.md), checklist scoring, and COP-deviation severity thresholds. They do **not** call OpenAI or Pinecone by design (no API keys needed to run them) — the live LLM/RAG path is verified separately by actually running the app/pipeline with real keys, which was done during development (see "Confirmed live" above) and should be re-run before any live demo or pilot go-live to confirm current model/vendor behavior.

`core/llm.py`'s safe-default fallback paths (missing key, and a simulated bad key) were manually verified during development to confirm they return the documented fallback shape rather than raising — see the git history for that verification run.

## Limits vs. production (stated openly)

- **Manual corpus is small and representative, not Chleo's own documentation** — same limitation as the POC (16 entries total: 8 Vaillant fault codes + 8 keyword-guide entries), see [../data/manuals/README.md](../data/manuals/README.md).
- **COP-drop thresholds (10%/20% deviation) are a stated assumption**, not calibrated against real fault outcomes — no public dataset pairs COP deviation with confirmed faults (see [../research/opportunities_risks.md](../research/opportunities_risks.md)); a real deployment would tune these against the manufacturer's own service-ticket history once available.
- **The Commissioning Checker's item list is illustrative** (7 items derived from the fault codes already in the knowledge base), not a validated installer sign-off form — a production version would be built with the manufacturer's QA team.
- **Single-session chat history** — `st.session_state` only, nothing persisted between runs or shared across installers. A pilot would need a lightweight backing store (even just a CSV/SQLite log) for the false-hardware-fault and first-visit-fix-rate metrics the Round 1 dashboard tracks.
- **No authentication** — anyone who can reach the running app can use it. Fine for an instructor demo or a single-installer trial; not fine for a multi-tenant pilot (see [../compliance/gdpr_documentation.md](../compliance/gdpr_documentation.md) for how this changes once real installer identities are involved).
- **Pinecone/OpenAI cost is per-query**, unbounded by this app — a production deployment would add basic rate limiting, matching the POC's own stated gap ("no retry/rate-limit handling on the OpenAI HTTP Request node").
