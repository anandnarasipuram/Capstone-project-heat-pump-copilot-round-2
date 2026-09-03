# MVP Documentation — Heat Pump Copilot

> Round 2 required deliverable: *"a functional product beyond the POC... the core AI capability has to actually run."*
> Builds directly on the Round 1 n8n POC — see [../poc/poc_documentation.md](../poc/poc_documentation.md) — and on all three use-case candidates scoped in [../research/use_cases.md](../research/use_cases.md), which this MVP implements as one small app with a real 4-page menu rather than three separate half-built products (Installed Fleet Overview is a portfolio view of the predictive candidate — see below).

## What this is

A single Streamlit app (`app.py`), run from one `streamlit run` command. Layout:

- **Header** — title, and two matching icon-only buttons side by side: 🔔 (opens a dropdown of the Installed Fleet Overview page's current High/Medium/Low alert counts and which units they are — computed once and shared with that page, not recomputed) and 👤 (opens a small "Chleo · demo profile" popover). There's no real authentication in this MVP (stated plainly, not implied) — the profile icon is a UI placeholder for where a real user identity would sit once the app has one.
- **Collapsible sidebar menu** — collapsed by default (Streamlit's native hamburger-style `«`/`»` toggle at the top-left opens/closes it; `initial_sidebar_state="collapsed"` in `st.set_page_config`). A real page router (`st.session_state.active_page`), not decorative labels — 4 selectable buttons, the current page shown filled (`type="primary"`):
  - **🏠 Dashboard** (default) — the 3 operational tools, as browser-style tabs
  - **🏘️ Installed Fleet Overview** — its own full page, not nested in the tab bar
  - **📊 Judge Reports** — its own full page, LLM-as-judge correctness/hallucination scores over live traces — see "Judge Reports page" below
  - **⚙️ System status** — its own full page (label left / indicator right per row, no nested expander)
- **Human-in-the-loop notice** — pinned to the bottom of the browser window via CSS (`position: fixed`), visible on every page at all times regardless of menu state, rather than tucked inside a menu someone might never open. Same Art. 50 EU AI Act transparency disclosure as before (see [../compliance/eu_ai_act_compliance.md](../compliance/eu_ai_act_compliance.md)) — moved for visibility, not reworded.

The Dashboard page's 3 tabs, plus the Installed Fleet Overview page:

| Mode | Use case (from [research/use_cases.md](../research/use_cases.md)) | Lifecycle stage | Where | Status |
|---|---|---|---|---|
| 🩺 **Fault Triage Copilot** | Candidate #1 — the Round 1 flagship | Reactive | Dashboard, tab 1 | Full RAG + LLM pipeline, chat UI |
| ✅ **Commissioning Checker** | Candidate #2 | Preventive | Dashboard, tab 2 | Deterministic checklist + LLM sign-off summary |
| 📉 **COP-Drop Early-Warning** | Candidate #3 | Predictive | Dashboard, tab 3 | Statistical baseline comparison + LLM alert note, single unit |
| 🏘️ **Installed Fleet Overview** | Candidate #3, portfolio view | Predictive | Its own menu page | Same mechanism as above, run across a demo fleet at once — see below |

**The core AI capability that has to "actually run"** is Mode 1's pipeline: fault-code lookup → **Pinecone vector search over OpenAI embeddings of the manual knowledge base** → **OpenAI chat-completion classification, grounded in whatever the retrieval step found**. This is the concrete Round 2 upgrade the POC's own docs called for (see [poc/poc_documentation.md](../poc/poc_documentation.md), "Language" section): the POC's keyword match is replaced by real multilingual embeddings, so a German-phrased symptom retrieves the right English-language manual excerpt on semantic similarity, not exact keyword overlap.

Modes 2–4 reuse the same OpenAI classification layer (`core/llm.py`) to turn a deterministic result into a natural-language summary/alert — one shared AI capability, four applications of it, not four separate models.

**Why a separate menu page, not a 4th tab:** the single-unit 📉 tab is the honest, technical demonstration of the predictive mechanism; the 🏘️ Installed Fleet Overview page exists purely to make that mechanism *legible to a non-technical audience* — a business decision-maker grasps "3 of 18 units need attention now" in one glance far faster than watching one slider move. Same underlying logic (`core/predictive.py` via `core/fleet.py`), presented as a portfolio instead of a single reading. It's a full page rather than a 4th tab specifically so it can also be reached directly from the sidebar menu, without first landing on the Dashboard.

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

**Model selector ("Which unit is this?"):** an installer can optionally pick which of Chleo's models (`TF-08`/`TF-12`/`AS-10`/`AS-16`) they're working on, threaded through both paths above as `model` and shown on the result card. Two honest things this does today, and one it doesn't:

- ✅ Passed to the LLM as context (`core/llm.py:classify_symptom`), so the model prompt is instructed to make its answer read as specific to that unit.
- ✅ Recorded on every result and trace, so `model` becomes a real filterable field once tickets are persisted — directly feeds the "connectivity-failure rate by model/firmware" metric already scoped in [../dashboard/dashboard_documentation.md](../dashboard/dashboard_documentation.md), not a new metric invented for this feature.
- ❌ It does **not** filter which fault codes are recognized or which manual excerpts are retrieved — the current 13-code lookup table and 16-entry manual corpus aren't actually split per Chleo model (the real Vaillant codes are explicitly representative reference documentation, not tied to any specific Chleo model — see [../data/manuals/README.md](../data/manuals/README.md)). Building genuine per-model filtering is a natural next step once Chleo's own model-specific documentation is ingested, not something to fake with today's shared corpus.

### Modes 2, 3, and 4

- **Commissioning Checker** (`core/checklist.py`): a fixed list of commissioning steps, each citing the fault code it would otherwise surface as later (e.g. unchecked eBUS wiring → F.9998). Deterministic scoring decides sign-off readiness; `core/llm.py:summarize_checklist()` turns that into a short natural-language summary for the installer.
- **COP-Drop Early-Warning** (`core/predictive.py`): aggregates the public [When2Heat Germany COP dataset](../data/dataset_documentation.md) into a monthly seasonal baseline per heat-pump profile, compares a reported reading against it, and flags `normal` / `watch` / `early_warning` by a stated percentage-deviation threshold (documented as an assumption pending real fleet data — see [../roi_risk_assessment.md](../roi_risk_assessment.md)). `core/llm.py:generate_predictive_alert()` narrates the finding.
- **Installed Fleet Overview** (`core/fleet.py`): runs the exact same `predictive.evaluate_reading()` check across a small, hand-curated demo fleet of 18 units (see [../data/installed_fleet_documentation.md](../data/installed_fleet_documentation.md)) instead of one reading at a time — `evaluate_fleet()` computes each unit's `observed_cop` from a stored `target_deviation_pct` against the *live* baseline (never a stored raw number, so it can't drift out of sync), and `fleet_summary_counts()` rolls that up into 🟢/🟡/🔴 counts for the metrics row. `core/llm.py:generate_fleet_summary()` optionally narrates the whole fleet in one call (only when the "Generate fleet summary" button is clicked — not on every page load, to keep it cheap).

## Transparency UI — Reasoning & Evidence, session activity, KPI tiles

Three additions to the Fault Triage tab that make the transparency story something you can actually see, not just a footer claim:

- **🔍 Reasoning & Evidence** (on every response) — an expander showing the AI's own `reasoning` field (a real field the LLM returns, requested explicitly in `core/llm.py`'s JSON schema — not derived from the message text after the fact), a visual confidence bar, and the *actual* retrieved manual excerpt text with its source citation (not just the source name, the real passage that grounded the answer). The deterministic lookup path gets an honest equivalent: "Exact match on fault code 'X' — resolved deterministically, no AI call needed."
- **📋 Recent Triage Activity** — a compact table of this session's own tickets (time, fault code, classification, confidence, status), built from `st.session_state.messages` via `build_activity_rows()`. Real interaction history for this browser session, not fabricated sample rows — same session-only limitation as the rest of the app (see "Limits vs. production" below).
- **KPI tiles** — 4 stat cards mirroring the Tableau dashboard's own metrics, split honestly: **Tickets this session**, **Escalation rate (session)**, and **Avg. response time (session)** are computed live from `compute_session_kpis()` — real, small numbers, because it's a demo session, not a fleet. **False hardware-fault rate** is the Round 1 dataset baseline (10.9%, from `data/synthetic_fault_dataset.csv`, the same figure the dashboard and `roi_risk_assessment.md` use) — deliberately *not* computed from this session, which has no way to know whether a live classification was actually wrong. The two are never blended into one number, and the tile row's own caption says so explicitly.

**A rerun ordering bug worth naming**, because it's the second time this exact class of bug showed up in this app: the KPI row and the activity-feed/empty-state switch are both computed near the *top* of the script, but a newly-processed message is appended lower down in that same run — so without an explicit `st.rerun()` after the append, they'd render with one-turn-stale data. Same fix as the sidebar nav buttons' active-state highlighting earlier: force a fresh run so everything that reads `st.session_state.messages` sees the update from the top of the script, not mid-run.

## Design system

A defined brand palette, not ad-hoc colors. Implemented in two layers, native theming doing as much of the work as possible so the app stays correct across Streamlit upgrades:

- **`.streamlit/config.toml`** — Streamlit's own theming (`[theme]` + the separately-themeable `[theme.sidebar]` section this Streamlit version supports). Covers: page/sidebar backgrounds, primary color (drives active tab underlines, primary buttons, checkboxes, and focus rings all at once), text/border/link colors, and the semantic `red`/`green`/`yellow`/`blue` families that `st.error`/`st.success`/`st.warning`/`st.info` render with.
- **CSS in `app.py`** — only for the handful of things config.toml can't reach: primary-button hover state, and the two-tone "Heat Pump / Copilot" header title (`st.title()` can't color part of its own text, so this is a hand-built `<h1>` matched to `st.title()`'s exact measured computed style — 44px/700/line-height 52.8px — so it doesn't visibly jump size against the rest of the app).

| Token | Hex | Where it's used |
|---|---|---|
| Primary Navy | `#172554` | Sidebar background |
| Primary Blue | `#2563EB` | Primary color — active tabs/buttons/focus rings, "Copilot" in the header, sidebar active menu item |
| AI Cyan | `#06B6D4` | Sidebar link color (a light accent, not a dominant color) |
| Success Green | `#16A34A` | `st.success()` — sign-off ready, healthy states |
| Warning Amber | `#F59E0B` | `st.warning()` — fallback/degraded-mode notices |
| Error Red | `#DC2626` | `st.error()` — actual faults/missing steps only, never "selected" |
| Page Background | `#F8FAFC` | Main content area |
| AI Card Background | `#EFF6FF` | `st.info()` — every AI-generated summary/note in the app renders in this "AI card" styling automatically |
| Primary/Secondary Text | `#0F172A` / `#475569` | Body text / captions |
| Border | `#E2E8F0` | Dividers, footer border |

**One correction this fixed:** Streamlit's *default* theme uses a red-ish `primaryColor` (`#FF4B4B`) for active-tab underlines and `type="primary"` buttons — which meant the "Fault Triage Copilot" active tab and the sidebar's active menu button were both rendering in red before this palette was applied, easy to misread as an error/fault state rather than "currently selected." Setting `primaryColor = "#2563EB"` fixes this at the theme level for every native component at once, not just the two places it was visibly wrong.

**One real bug this caught:** the pinned human-in-the-loop footer's background was set via `background: var(--secondary-background-color)`, which resolves to fully transparent in this Streamlit version — invisible before only because everything nearby happened to be similarly light; the moment the sidebar went navy, the transparency showed through as unreadable dark-on-dark text. Fixed by using an explicit hex value instead of a CSS custom property that turned out not to be reliably set.

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

## LLM-as-judge evaluation (`scripts/judge_traces.py`)

Tracing captures *what* the copilot said; it doesn't say whether that was any good. `scripts/judge_traces.py` closes that gap — an instructor-requested addition — by pulling real `classify_symptom` runs already sitting in the LangSmith project (actual installer queries and the AI's actual answers, whatever traffic the app has generated, not a fixed set of worked examples) and scoring each with a second, independent LLM call:

- **correctness** (0.0–1.0): does the category and guidance actually match what the manual excerpts the AI had access to support (or general HVAC knowledge, if none were retrieved)?
- **hallucination** (0.0–1.0): does the response state a specific fact — a part, a threshold, a procedure — not actually grounded in those excerpts?

```bash
cd mvp
python scripts/judge_traces.py            # judges up to 20 recent runs
python scripts/judge_traces.py --limit 50
```

Scores are posted back to the *original* trace via `Client.create_feedback` — they show up as `llm_judge_correctness` / `llm_judge_hallucination` feedback right next to each run in the LangSmith UI, not in a separate report disconnected from the traces themselves. **Confirmed live**: run against this project's own real traces (including free-text German-language symptoms), it correctly scored 5/5 runs, all with `hallucination = 0.0` and `correctness` between 0.80–1.00, with per-run reasoning explaining each score (e.g. flagging one response as slightly incomplete rather than wrong, rather than either rubber-stamping or over-penalizing it).

This is a judge, not a gate — nothing in the app currently blocks on these scores. A pilot would set a review threshold (e.g. flag any run scoring `hallucination > 0.3` for manual review) and run this on a schedule rather than by hand; that's named here as the natural next step, not built into this script.

### Judge Reports page (`app.py`, menu → 📊 Judge Reports)

The judging logic above moved into `core/judge.py` so it has two callers instead of one: the CLI script (`scripts/judge_traces.py`, now a thin wrapper) and a 4th sidebar page in the app itself — a **▶️ Run judge on recent traces** button plus two charts, so scores are visible without leaving the app or reading LangSmith's UI.

This came from a direct comparison: a colleague's AI-audit tool renders a radar ("Pattern Scan") across six invented governance dimensions — Strategy, Accuracy, UX Timing, Workflow, and so on — each PASS/RISK/FAIL. That's a different tool for a different domain (a legal-classification-agent audit), and reproducing its exact dimensions here would mean fabricating scores this app has no way to actually compute. What's reused instead is the *shape* of the idea — a reports view with a real findings chart — built on the two dimensions this app's own judge can honestly assess:

- **Correctness per trace** and **Hallucination per trace** — bar charts, one bar per judged `classify_symptom` run, oldest→newest, colored by QA status (🟢 Good / 🟡 Caution / 🔴 Concern — the same Success Green / Warning Amber / Error Red tokens used everywhere else in the app, not a new palette). Hovering a bar shows the symptom, the AI's category, the exact score, and the judge's own one-line reasoning.
- Summary tiles (traces judged, average correctness, average hallucination) and a **Full report** expander — the underlying table plus a CSV download — the closest honest equivalent to the colleague's tool's "Full report" link.
- A **🔄 Refresh** button re-reads existing LangSmith feedback (no new judge-model calls, free); **▶️ Run judge on recent traces** judges up to N (default 10, capped at 30) un-scored recent traces live, posting feedback to LangSmith exactly like the CLI script, then reloads the report.

**Confirmed live**: ran end-to-end through the actual UI (not just the CLI) — judged 3 real recent traces (including the German `"Die Vorlauftemperatur ist niedrig"` symptom), got `avg. correctness = 83%`, `avg. hallucination = 0%`, both charts and the CSV-exportable table populated with the real per-trace scores and reasoning, and a fresh page load afterwards picked the same 3 scored traces straight back up from LangSmith (this page has no local storage of its own — every score shown is either just-computed or freshly re-read from LangSmith's feedback API). One chart-rendering issue was caught and fixed during that same live check: a true `hallucination = 0.0` (the *good* outcome) rendered as a zero-height bar, indistinguishable from no data — fixed with a floored display height (the tooltip still reports the real `0.00`).

What this page deliberately does **not** claim to be: a general AI-governance audit tool. It scores exactly the two dimensions a second LLM call can actually assess from a trace's own inputs and outputs — nothing about "strategy fit" or "validated user need," which would need a different kind of evaluation (product/business judgment, not a QA read of one response) that this app has no data to back.

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
Open the app, stay on the Dashboard's 🩺 Fault Triage Copilot tab, and try `Low refrigerant pressure alarm, error code E4` — it resolves instantly via the deterministic lookup table, no key needed. The other 2 tabs and the Installed Fleet Overview page also load and compute their deterministic results (checklist score, COP deviation, seasonal chart, the full fleet table + counts) with zero keys; only the AI-generated narrative text falls back to a clearly-labeled template (see "Error handling" below).

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

### A real bug found during live use: duplicate language instructions broke language-matching

Reported from an actual live-testing session: a German symptom (`"vorlauf temperatur ist nedrig"`) got an **English** reply. Root-caused by isolating the exact API call (raw OpenAI client, no wrapper, no tracing) with the real 3-excerpt RAG context — reproducible outside the app entirely, which ruled out `wrap_openai`/tracing/temperature as causes one at a time before finding it: the JSON schema's `message` field description had picked up a second, redundant language instruction (*"...in the installer's own language per the rule above"*) alongside the system prompt's own `"Reply in the same language the installer used."` — added when the `reasoning` field was introduced (see "Reasoning & Evidence" above). Two instructions saying the same thing in different places made the model's language selection unreliable — not just for the reported German case, but for **most English inputs too** (several came back in Spanish or Italian, confirmed by systematic testing across 5+ symptoms before the fix and after). Removing the duplicate — one language instruction, stated once — fixed all of them.

Also set `temperature=0.2` on this call while debugging (was previously unset, defaulting to OpenAI's `1.0`) — not the actual cause (the bug reproduced identically at `temperature=0`, `0.2`, and `1.0`), but a reasonable general improvement for a classification task, kept after the real fix.

**One honest residual case, not a bug**: a *very* short, telegraphic German phrase with no article or verb conjugation (`"vorlauf temperatur ist niedrig"`, even correctly spelled) is occasionally still classified as English — "vorlauf" and "temperatur" read as ambiguous/cognate-like to the model without a stronger grammar marker. Adding a definite article resolves it (`"Die Vorlauftemperatur ist niedrig"` → correctly German, confirmed live) — a real, narrow limitation of automatic language detection on minimal input, not something further prompt engineering should chase, given how directly the *last* round of prompt tweaking caused the much bigger regression above.

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
- **The Installed Fleet Overview page is a demo table, not live telemetry** — 18 hand-curated units, deliberately spanning all 3 flags so the mechanism is visible in one glance (see [../data/installed_fleet_documentation.md](../data/installed_fleet_documentation.md)). A production version replaces `data/synthetic_installed_fleet.csv` with a real feed keyed to actual installed units, once that telemetry exists.
- **Single-session chat history** — `st.session_state` only, nothing persisted between runs or shared across installers. A pilot would need a lightweight backing store (even just a CSV/SQLite log) for the false-hardware-fault and first-visit-fix-rate metrics the Round 1 dashboard tracks.
- **No authentication** — anyone who can reach the running app can use it. Fine for an instructor demo or a single-installer trial; not fine for a multi-tenant pilot (see [../compliance/gdpr_documentation.md](../compliance/gdpr_documentation.md) for how this changes once real installer identities are involved).
- **Pinecone/OpenAI cost is per-query**, unbounded by this app — a production deployment would add basic rate limiting, matching the POC's own stated gap ("no retry/rate-limit handling on the OpenAI HTTP Request node").
