# Heat Pump Copilot — Round 2

Ironhack AI Capstone, Round 2: the consulting package + working MVP that builds on [Round 1](https://github.com/anandnarasipuram/Capstone-Project-Heat-Pump-Copilot-Dashboard) (kept in full in this repo — see below). Sector: Home Energy & HVAC. Use case: **Field Commissioning & HEMS Connectivity Copilot** for a small-medium heat pump manufacturer entering the German market. No industry/use-case change since Round 1 — see [feedback/round1_decision.md](feedback/round1_decision.md) and the "How this evolved from Round 1" section of [use_case_definition.md](use_case_definition.md).

## Start here

| Deliverable | File |
|---|---|
| **Use case definition** | [use_case_definition.md](use_case_definition.md) |
| **No-code/low-code POC** | [poc/poc_documentation.md](poc/poc_documentation.md) + [poc/poc_workflow.json](poc/poc_workflow.json) |
| **Working MVP** | [mvp/](mvp/) — `cd mvp && streamlit run app.py` — see [mvp/mvp_documentation.md](mvp/mvp_documentation.md) |
| **ROI and risk assessment** | [roi_risk_assessment.md](roi_risk_assessment.md) |
| **EU AI Act compliance** | [compliance/eu_ai_act_compliance.md](compliance/eu_ai_act_compliance.md) |
| **GDPR documentation** | [compliance/gdpr_documentation.md](compliance/gdpr_documentation.md) |
| **Strategic deployment & commercialisation plan** | [strategic_plan.md](strategic_plan.md) |
| **Quarterly roadmap, sprint plan & Definition of Done** (IHK certification) | [roadmap_sprint_plan.md](roadmap_sprint_plan.md) |
| **Final presentation** | [presentation.pptx](presentation.pptx) (source: [presentation/build_presentation.py](presentation/build_presentation.py)) |

## Repository structure

```
.
├── README.md                       # this file
├── use_case_definition.md          # Round 2 — problem, company profile, solution, stakeholders, success criteria
├── roi_risk_assessment.md          # Round 2 — costs, value, 12/36-month ROI, 8-risk matrix
├── strategic_plan.md               # Round 2 — POC → Pilot → Full Deployment, GTM, KPIs, commercialisation
├── roadmap_sprint_plan.md          # IHK certification — Q4 2026 sprint plan, user stories + AC, Definition of Done
├── presentation.pptx               # Round 2 — final pitch deck (16 slides)
├── poc/                             # Round 2-formatted POC docs (the Round 1 n8n workflow, re-documented)
│   ├── poc_workflow.json
│   └── poc_documentation.md
├── mvp/                             # Round 2 — required working MVP (Streamlit + LangChain + Pinecone + OpenAI)
│   ├── app.py
│   ├── core/                        # RAG, LLM, fault-lookup, checklist, predictive — see mvp_documentation.md
│   ├── scripts/ingest_manuals.py
│   ├── tests/                       # 20 offline unit tests, no API keys needed
│   ├── requirements.txt · .env.example
│   └── mvp_documentation.md
├── compliance/
│   ├── eu_ai_act_compliance.md
│   └── gdpr_documentation.md
├── research/                        # Round 1 — sector research, opportunities/risks, use-case candidates
├── dashboard/                       # Round 1 — Tableau dashboard + docs
├── data/                            # Shared by POC, MVP, and dashboard — manuals, synthetic fault data, When2Heat COP baseline
├── langsmith/                       # Round 1 — LangSmith trace sample + monitoring notes
├── cost_estimation/                 # Round 1 — build cost baseline that roi_risk_assessment.md extends
├── feedback/round1_decision.md      # Round 1 — keep/change decision after staff presentation
└── presentation/                    # Round 1 deck (kept) + Round 2 deck's build script
```

## Round 1 → Round 2, in one paragraph

Round 1 built the research pack, a synthetic fault dataset, a Tableau dashboard, an n8n/Telegram POC (keyword-grounded fault triage), and a one-off LangSmith trace sample — see [feedback/round1_decision.md](feedback/round1_decision.md) for why the use case was kept unchanged. Round 2 deepens the same use case rather than starting over: the POC's keyword match becomes real embeddings-based RAG (OpenAI + Pinecone) in a working MVP that also builds out the two use-case candidates Round 1 named but didn't build (a commissioning-completeness checker and a COP-drop predictive early-warning tool), wires LangSmith into live, continuous tracing of every interaction instead of a one-off script (see [mvp/mvp_documentation.md](mvp/mvp_documentation.md), "Monitoring"), and adds the full consulting package — ROI/risk, EU AI Act + GDPR compliance, and a phased strategic deployment plan — that a real client would need before greenlighting a pilot.

## Setup (top-level)

Round 1 artifacts (dashboard, LangSmith sample) use the root `requirements.txt`... *(carried forward from Round 1 — see individual folder docs)*. **For the MVP specifically**, see [mvp/mvp_documentation.md](mvp/mvp_documentation.md) — it has its own `requirements.txt` and `.env.example` and runs independently:

```bash
cd mvp
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY + PINECONE_API_KEY for full RAG
streamlit run app.py   # runs with zero keys too — see mvp_documentation.md
```

## Submission checklist

- [x] `use_case_definition.md`
- [x] POC export + `poc/poc_documentation.md` — demo recording (2–5 min) to be captured separately per [poc/poc_documentation.md](poc/poc_documentation.md)'s "Demo recording" section
- [x] `roi_risk_assessment.md`
- [x] `compliance/eu_ai_act_compliance.md`
- [x] `compliance/gdpr_documentation.md`
- [x] `strategic_plan.md`
- [x] `presentation.pptx`
- [x] Working MVP + `mvp/mvp_documentation.md`
- [x] Round 1 materials present in this repo (`research/`, `dashboard/`, `data/`, `langsmith/`, `cost_estimation/`, `feedback/`)

## Related

- This repo: [anandnarasipuram/Capstone-project-heat-pump-copilot-round-2](https://github.com/anandnarasipuram/Capstone-project-heat-pump-copilot-round-2)
- Round 1 repo: [anandnarasipuram/Capstone-Project-Heat-Pump-Copilot-Dashboard](https://github.com/anandnarasipuram/Capstone-Project-Heat-Pump-Copilot-Dashboard)
