# Round 1 Decision — Keep or Change Industry/Use Case

## Decision
**KEEP** — Home Energy & HVAC (heat pumps), Field Commissioning & API/HEMS Connectivity Copilot.

## Industry/use case evaluated
Heat Pump Copilot Dashboard (Home Energy & HVAC) — see [research/use_cases.md](../research/use_cases.md) and [research/opportunities_risks.md](../research/opportunities_risks.md).

## Why
- No teaching-staff feedback called for a change of industry, use case, or company profile — this repo has no record of a required pivot, and the underlying case still holds: a documented installer-capacity shortage (Germany trains ~12k SHK tradespeople/yr against a ~35k/yr need), a real target-vs-actual demand gap (500k/yr political target vs. ~193k actual 2024 sales), and a genuine market gap (no public tool cleanly separates "hardware fault" from "connectivity/app issue" for heat pumps).
- The reactive fault-triage copilot remains the most de-risked of the three candidates considered in Round 1 (reactive/preventive/predictive) — the other two need data (a checklist model, live telemetry) Chleo's company doesn't have yet, and are already sequenced as named Round 2/3 extensions rather than discarded.
- Round 1 build (research, n8n POC, dashboard, cost/timeline estimate, LangSmith monitoring) is complete and internally consistent — keeping the use case lets Round 2 deepen it (real MVP, compliance package, ROI/risk, GTM) instead of restarting research from zero.

## Feedback received
No specific written feedback was captured in this repo after the Round 1 presentation. Nothing surfaced (formally or informally) required a change of direction, so this decision proceeds on that basis rather than on a documented staff verdict. *(If you have notes from the actual presentation, add them here and I'll fold in any adjustments.)*

## Next steps for Round 2
- Deepen the same use case: working MVP (real RAG upgrade — embeddings + local vector store, replacing Round 1's keyword match), ROI/risk assessment, EU AI Act + GDPR compliance docs, and a strategic deployment/commercialisation plan.
- Formalize the "limited risk" EU AI Act framing already assumed in [research/opportunities_risks.md](../research/opportunities_risks.md) rather than continuing to treat it as a stated assumption.
- Bring GDPR into scope now that Round 2 may touch installer-identifiable data (out of scope in Round 1 per [cost_estimation/cost_analysis.md](../cost_estimation/cost_analysis.md), assumption #9).
