# Strategic Deployment and Commercialisation Plan — Heat Pump Copilot

> Ties together [use_case_definition.md](use_case_definition.md) (success criteria), [roi_risk_assessment.md](roi_risk_assessment.md) (ROI model, break-even, risk matrix), and [compliance/](compliance/) (the gates a pilot must clear) into a phased rollout plan with named milestones, KPIs, and a concrete pilot→full-deployment greenlight.

## 1. Phases

```
Phase 0: POC          Phase 1: MVP /              Phase 2: Pilot              Phase 3: Full            Phase 4: Scale
(Round 1 — done)       Internal Validation          (external, real            Deployment                (optional)
n8n + Telegram,        (Round 2 — done)              installers, real           (all installers,
keyword grounding      Streamlit + Pinecone RAG,      data, 12 weeks)            company-wide)
                        3 modes, offline-tested
─────────────────►    ─────────────────────►       ─────────────────────►     ─────────────────►      ─────────────────►
Sep 2025 – present     Sep 2026 (this package)       Oct 2026 – Jan 2027        Mar – Aug 2027            2028+
```

### Phase 0 — POC (Round 1, complete)
n8n/Telegram workflow, keyword-based manual grounding, LangSmith trace sample, PowerBI/Tableau dashboard spec. See [poc/poc_documentation.md](poc/poc_documentation.md). No further action needed here — carried forward, not re-built.

### Phase 1 — MVP / Internal Validation (Round 2, complete)
The Streamlit application in [mvp/](mvp/): real RAG (OpenAI embeddings + Pinecone), all three use-case modes functional, 16 offline unit tests passing, graceful degradation with zero API keys. **This phase's job is to prove the capability works before any real installer sees it** — it is deliberately internal-only (Chleo's own team, synthetic/public data), not yet a pilot.

**Exit gate to Phase 2 (all required):**
- [ ] Internal team reproduces all 5 POC worked examples live against real OpenAI + Pinecone keys (not just the offline unit tests) — confirms the RAG pipeline, not just the deterministic fallback
- [ ] `scripts/ingest_manuals.py` run successfully against a production-intended Pinecone index
- [ ] Short DPIA (see [compliance/gdpr_documentation.md](compliance/gdpr_documentation.md)) reviewed by a DPO or privacy counsel
- [ ] Ticket-persistence layer added (current build is session-only — see [mvp/mvp_documentation.md](mvp/mvp_documentation.md), Limits) so pilot metrics can actually be measured
- [ ] Pilot cohort recruited: 10–15 installers, a deliberate mix of the manufacturer's own field installers and partner SHK installers (both target user groups from [use_case_definition.md](use_case_definition.md))

### Phase 2 — Pilot (external, real data, 12 weeks)
Real installers, real tickets, the compliance posture in [compliance/](compliance/) fully operative (not just documented). Runs Oct 2026 – Jan 2027 (12 weeks + 2 weeks review buffer).

**Pilot KPIs** (measured weekly, reviewed monthly):

| KPI | Target | Source |
|---|---|---|
| First-visit fix rate improvement | ≥10 percentage points vs. 69.1% baseline | [use_case_definition.md](use_case_definition.md) success criterion #1 |
| False-hardware-fault rate reduction | ≥5 percentage points vs. 10.9% baseline | [use_case_definition.md](use_case_definition.md) success criterion #2 |
| Median time-to-classification | <30 seconds | [use_case_definition.md](use_case_definition.md) supporting criterion |
| Installer adoption | ≥60% of pilot cohort using the tool for ≥50% of eligible tickets by week 8 | New for this phase — operational viability check |
| Override rate (automation-bias signal) | Tracked, reviewed qualitatively — no installer should feel pressured to accept a suggestion they disagree with | [roi_risk_assessment.md](roi_risk_assessment.md) risk #5 |
| Compliance incidents | Zero — no autonomous action taken, no data-subject complaint, no AI Act/GDPR gate breached | [compliance/](compliance/) |
| Cost recovery trend | Consistent with the ~3.5–4 month break-even modeled in [roi_risk_assessment.md](roi_risk_assessment.md) | ROI model validation |

**Greenlight criteria — Pilot → Full Deployment (all required, reviewed at week 12):**
1. First-visit-fix improvement ≥7pp (a meaningfully-trending-right bar, not requiring the full 10pp target to be hit exactly in 12 weeks)
2. False-hardware-fault reduction ≥3pp
3. Adoption ≥60% sustained through week 8–12 (not just an initial spike)
4. Zero unresolved compliance incidents
5. Installer feedback survey: net-positive sentiment on "this tool made my job easier this week"

**If not met:** the default response is to extend and adjust the pilot (revisit knowledge-base coverage, retrain on override-rate feedback, re-run installer onboarding), not to kill the project outright or proceed regardless — a pilot existing specifically to catch this before a company-wide rollout is the point of having one.

### Phase 3 — Full Deployment
Company-wide rollout to all own field installers and the full partner SHK network, phased by region over ~6 months (Mar–Aug 2027) rather than a single cutover, so the support/service planning team's escalation queue isn't disrupted all at once. The Commissioning Checker and COP-Drop Early-Warning modes move from "functional demo" to "used in the field alongside the flagship" during this phase, since pilot data now exists to validate their thresholds (see [mvp/mvp_documentation.md](mvp/mvp_documentation.md), Limits).

**KPIs:** sustained pilot-level metrics at full scale; cost-per-ticket trending down as fixed Pinecone/index costs amortize across higher volume; dashboard (see [dashboard/dashboard_documentation.md](dashboard/dashboard_documentation.md)) live company-wide as the standing reporting layer for Chleo.

### Phase 4 — Scale (optional)
Two independent scale vectors, evaluated separately rather than bundled:
1. **Product depth:** the COP-Drop module moves from a public-baseline mechanism to a real, per-unit-telemetry-calibrated predictive model once the installed base is generating its own fault-outcome data (see [research/use_cases.md](research/use_cases.md) — this was always the named Round 3+ extension).
2. **Market breadth:** the installer-shortage structural problem this product addresses is EU-wide, not Germany-specific (500,000+ new installers needed EU-wide by 2030 — see [research/sector_research.md](research/sector_research.md)) — a candidate second-market expansion (e.g. Austria, Netherlands) reuses the same architecture with a localized manual corpus.

## 2. Go-to-market

| | |
|---|---|
| **Primary buyer/sponsor** | Chleo, as the business decision-maker funding the field-operations budget this tool's opex sits in |
| **Users (not external customers)** | Own field installers (direct), partner SHK installers (via the manufacturer's existing partner program), support/service planning team (dashboard consumer) |
| **Channel** | Direct internal rollout for own installers; existing partner-installer communication channels (partner onboarding, training, newsletters) for SHK partners — no new sales channel needed for Phases 1–3, since this is an internal capability, not an external product, until Phase 4 |
| **Differentiator vs. a generic HVAC chatbot** | (1) Grounded in the manufacturer's own manual knowledge base, not generic internet HVAC knowledge — see the RAG architecture in [mvp/mvp_documentation.md](mvp/mvp_documentation.md); (2) deterministic-first routing keeps 13+ known fault codes free and instant, not an LLM call every time; (3) advisory-only design deliberately keeps the EU AI Act compliance burden light (limited-risk tier — see [compliance/eu_ai_act_compliance.md](compliance/eu_ai_act_compliance.md)) rather than building something that needs a conformity assessment before it can ship |

## 3. Stakeholder communication plan

| Stakeholder | Cadence | Content |
|---|---|---|
| Chleo (sponsor) | Monthly steering update; decision-gate meeting at each phase transition | KPI dashboard snapshot, ROI-model actuals vs. [roi_risk_assessment.md](roi_risk_assessment.md) projections, greenlight recommendation |
| Own field installers | Pre-pilot training session; weekly performance digest during the pilot | How to use the tool, the "AI-suggested triage, confirm before acting" framing, a feedback channel |
| Partner SHK installers | Comms via the existing partner program; opt-in pilot invitation | Same training/feedback loop as own installers, **plus an explicit statement that tool usage is never used to evaluate individual installer performance** — this trust point is the practical difference between adoption and rejection for a workforce that isn't directly employed, and it's a compliance commitment already made in [compliance/eu_ai_act_compliance.md](compliance/eu_ai_act_compliance.md), not just a talking point |
| Support/service planning team | Weekly ops review during pilot; standing dashboard access from Phase 3 | Escalation-queue impact, direct feedback loop into quarterly knowledge-base content review (see [roi_risk_assessment.md](roi_risk_assessment.md) risk #8) |
| Compliance/legal (DPO) | Gate review before pilot go-live; quarterly check-in during pilot and full deployment | DPIA sign-off, transfer-mechanism confirmation (see [compliance/gdpr_documentation.md](compliance/gdpr_documentation.md)), any scope-change re-classification triggers |
| Homeowners (indirect) | No direct tool-related communication — not a data subject interacting with the system directly | Customer support scripts updated to reflect faster resolution times as a passive value message only |

## 4. Commercialisation model

**Phases 1–3 are an internal cost-avoidance tool**, not a resold product — funded from the field-service operations budget, with return measured against the ROI model in [roi_risk_assessment.md](roi_risk_assessment.md) (Year 1 ROI ≈ 241% central case, 36-month ≈ 1,198%). No pricing/licensing is needed for this scope.

**Phase 4 opens an optional productization path**, since the underlying problem (installer shortage, hardware-vs-connectivity ambiguity) is structural to the whole HVAC/heat-pump sector, not unique to Chleo's company (see [research/sector_research.md](research/sector_research.md)). If pursued:

- **Model:** white-label licensing to other small-medium heat pump manufacturers facing the same installer-capacity constraint — not a horizontal multi-industry SaaS play, a narrow, defensible one.
- **Pricing shape:** a flat onboarding/integration fee (covers ingesting the licensee's own manual corpus into their own Pinecone index — the architecture is already built to take a swapped-in `data/manuals/` corpus, see [mvp/mvp_documentation.md](mvp/mvp_documentation.md)) plus a per-installer/month subscription, priced well below the per-installer value each licensee's own ROI model would show (roughly €100–200+/installer/month of avoided cost per the ROI model here) — a €15–25/installer/month subscription price still leaves substantial margin for the licensee while being a credible SaaS price point.
- **Why this is a Phase 4 decision, not a Phase 1 one:** commercializing before Chleo's own pilot has validated the KPIs above would mean selling an unproven claim to a third party — the internal deployment is both the product and the reference case a future licensing pitch would need.
