# Cost Analysis

**Project:** Heat Pump Field Commissioning & API Connectivity Copilot
**Scope of this estimate:** Round 1 deliverables only (research, dashboard, n8n POC, LangSmith monitoring sample). Round 2 (working MVP, compliance package, pilot rollout) is estimated separately once the use case is confirmed after the staff presentation.

## Assumptions

| # | Assumption | Rationale |
|---|---|---|
| 1 | Client (Chleo's company) is a small–medium heat pump manufacturer entering the German market. | Stated in the scenario brief. |
| 2 | Delivery team: 1 AI consultant (this project), blended day rate **€650/day**. | Typical freelance/boutique AI-consulting rate in the DACH region for a solo builder covering research + no-code + light dev. |
| 3 | Pilot scale: ~15–30 field installers, ~5–8 support agents, ~500–1,500 fault/connectivity queries per month. | Small-medium manufacturer, single-market (Germany) pilot rather than full fleet rollout. |
| 4 | LLM provider: OpenAI API (gpt-4o-mini class model), pay-as-you-go, no fine-tuning. | Matches the "grounded reasoning over your own documents" (RAG) approach described for the copilot; avoids upfront training cost. |
| 5 | Automation layer: n8n Cloud "Starter" tier (or self-hosted on a small VM) is sufficient for POC/pilot volume. | Query volume in assumption 3 is well under n8n Cloud execution limits; self-hosting is a fallback if IT prefers on-prem. |
| 6 | LangSmith: free/developer tier during Round 1 (monitoring sample only), reassessed for a paid tier once tracing volume grows in Round 2/pilot. | Round 1 only needs a small dataset + a handful of traced runs, not production-scale observability. |
| 7 | PowerBI: Pro licenses only for report viewers who need to interact live (assume 3 seats: Chleo + 2 stakeholders); everyone else views exported/shared snapshots. | Keeps licensing cost proportional to a pilot, not an org-wide rollout. |
| 8 | No real customer, installer, or telemetry data is used — only public datasets (Kaggle heat pump COP / predictive maintenance) plus a self-authored synthetic fault-code → cause → fix dataset. | Stated constraint in the one-pager and in the capstone brief (public/synthetic data only). |
| 9 | Excludes: EU AI Act / GDPR compliance documentation, full MVP engineering (FastAPI/Streamlit build), and multi-market localization. | Those are explicitly Round 2 scope per the capstone brief. |
| 10 | Currency: EUR, reflecting the German target market. LLM/API vendor pricing (USD-denominated) converted at an approximate €1 ≈ $1.05 rate and rounded. | Vendor list pricing is USD; client-facing estimate is presented in EUR for consistency. |

## Cost breakdown (build) — one-time, Round 1

| Work item | Effort | Rate | Cost |
|---|---|---|---|
| Sector research + opportunity/risk mapping | 3 days | €650/day | €1,950 |
| Use case scoping & justification (2–3 candidates → 1 selected) | 2 days | €650/day | €1,300 |
| Fault-code → cause → fix-category dataset authoring (sourcing public data + synthesizing the connectivity-vs-hardware gap dataset) | 3 days | €650/day | €1,950 |
| n8n POC build (symptom intake → hardware-vs-connectivity classification → fix guidance/escalation routing) | 4 days | €650/day | €2,600 |
| LangSmith monitoring setup (trace sample, small eval dataset, documentation of what's observed) | 1.5 days | €650/day | €975 |
| PowerBI dashboard build (5–7 metrics: first-visit fix rate, commissioning time, connectivity-failure rate by model/firmware, false-hardware-fault rate) + documentation | 3 days | €650/day | €1,950 |
| QA, integration pass, README/docs, staff presentation prep | 2.5 days | €650/day | €1,625 |
| **Subtotal — Round 1 build** | **~19 days** | | **≈ €12,350** |

## Cost breakdown (run / ongoing) — pilot scale, per month

| Item | Basis | Estimated cost/month |
|---|---|---|
| LLM API usage (OpenAI) | ~1,000 queries/month × ~3K tokens avg (in+out) | €50–90 |
| n8n hosting | Cloud Starter plan, or self-hosted small VM | €20–50 |
| LangSmith | Free/developer tier at Round 1 volume; budget for lowest paid tier once pilot traffic grows | €0–40 |
| PowerBI Pro licenses | 3 seats × €9.40/user | ≈ €28 |
| Manual/RAG storage (embeddings + vector store, e.g. pgvector or a starter managed vector DB) | Small document corpus (product manuals) | €10–20 |
| **Subtotal — run cost, no retainer** | | **≈ €110–230/month** |
| Optional light maintenance & support retainer | 0.5 day/month × €650 | +€325/month |

Note: these run costs assume Round 1 POC-level traffic. They will step up materially once a real MVP (Round 2) is handling live installer traffic at fleet scale — see the Round 2 estimate once scope is confirmed.

## Total estimate

| Scenario | Amount |
|---|---|
| Round 1 build (one-time) | **≈ €12,350** |
| + First 12 months run, no retainer (€110–230/mo × 12) | + €1,300–2,750 |
| **Year 1 total, no retainer** | **≈ €13,650–15,100** |
| + Optional maintenance retainer (€325/mo × 12) | + €3,900 |
| **Year 1 total, with retainer** | **≈ €17,550–19,000** |

**Headline for the pitch:** a Round 1 proof of concept costs roughly **€12k to build** and **€1–2k over the first year to run at pilot scale**, before any paid support retainer. Round 2 (working MVP + compliance package + pilot deployment) will be quoted separately once the use case survives the staff presentation, since its scope — and therefore its cost — depends on that decision.
