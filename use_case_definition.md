# Use Case Definition — Heat Pump Copilot

> Round 2 core deliverable. Builds on [research/use_cases.md](research/use_cases.md), [research/sector_research.md](research/sector_research.md), [research/opportunities_risks.md](research/opportunities_risks.md), and [feedback/round1_decision.md](feedback/round1_decision.md) from Round 1 — this document restates and sharpens that work into the consulting-package format Round 2 requires, it doesn't re-derive it from scratch.

## Business problem statement

Chleo's company sells smart, app-connected heat pump systems into the German residential market, where the manufacturer competes against established players (Vaillant, Bosch, Stiebel Eltron, Viessmann, NIBE, and others) without their service-headcount budgets. Two field problems recur and are hard to tell apart in the moment:

1. **Genuine hardware faults** the installer cannot resolve on-site and must escalate.
2. **HEMS (Home Energy Management System) connectivity/pairing/app issues** that look like a broken unit but need no hardware visit at all.

The technical root cause is industry-wide, not vendor-specific: inverter heat pumps rely on proprietary communication protocols that fail in a degraded, ambiguous way rather than cleanly, so installers cannot reliably tell "hardware fault" from "connectivity mismatch" from the symptoms alone (see [research/sector_research.md](research/sector_research.md)). Layered on top of this, Germany's certified-installer pipeline trains roughly 12,000 SHK tradespeople per year against an estimated 35,000/year need, and reaching the government's 6-million-heat-pump-by-2030 target independently requires a ~50% uplift in the certified installer workforce. **The business cannot hire its way out of this** — a tool that raises the first-visit fix rate multiplies the value of installers the company already has, instead of requiring headcount growth that the labor market cannot supply on any realistic timeline.

The costliest failure mode specifically is the **false hardware-fault**: misdiagnosing a connectivity issue as a hardware fault dispatches an unneeded parts/technician visit, wasting scarce senior-technician time and delaying the customer's actual fix.

## Company profile

| | |
|---|---|
| **Industry** | Home Energy & HVAC — smart heat pumps with an app-based HEMS layer |
| **Company size** | Small–medium manufacturer (per the capstone scenario brief) |
| **Market** | Entering/competing in Germany, a policy-driven market: 2024 target was 500,000 units/year, actual sales were ~193,000 (down 46%), BWP forecasts ~257,000 in 2025 — a volatile-but-recovering market with a structural labor ceiling, not a demand problem |
| **Current state** | Installers and support staff triage faults manually today, by phone/experience, with no tool cleanly separating "hardware" from "connectivity" from "installer/commissioning error" — a documented market gap (see [research/opportunities_risks.md](research/opportunities_risks.md)) |
| **Regulatory context** | GEG heating-system rules, BEG/KfW subsidy (up to 70% of cost, capped at €30k), a 2025 smart-meter-gateway mandate that adds *new* pairing failure modes, and the EU F-Gas phase-out reshaping refrigerants/hardware from 2027–2028 |

## Proposed AI solution and system type

**A decision-support copilot for field installers and support staff** — advisory only, always with a human installer in the loop, never issuing autonomous electrical/refrigerant instructions. Concretely, three related capabilities, built and demoed as one system rather than three disconnected tools (see [research/use_cases.md](research/use_cases.md) for why all three were scoped together):

1. **Fault Triage Copilot (reactive, the flagship)** — installer enters a fault code or free-text symptom → the system classifies it as `hardware_fault`, `connectivity_issue`, or `installer_error` and returns fix guidance or an escalation route. Round 1 proved this as an n8n + Telegram POC with keyword-based manual grounding (see [poc/poc_documentation.md](poc/poc_documentation.md)); Round 2's MVP upgrades the grounding to real RAG (OpenAI embeddings + Pinecone vector search over the manual knowledge base — see [mvp/mvp_documentation.md](mvp/mvp_documentation.md)).
2. **Commissioning-Completeness Checker (preventive)** — confirms commissioning steps (refrigerant charge, HEMS pairing, eBUS wiring, flow balancing, electrical supply) were actually completed before an installer signs a job off, catching the same root causes before they become a fault ticket.
3. **COP-Drop Predictive Early-Warning (predictive)** — compares a unit's reported coefficient-of-performance against a public seasonal baseline (When2Heat Germany) to flag likely-failing units before anyone reports a fault.

**System type:** a retrieval-augmented generation (RAG) system grounded in the manufacturer's own manual/fault-code documentation, using a general-purpose LLM (OpenAI) for natural-language understanding of free-text installer symptoms — not a fine-tuned model, not an autonomous agent that takes actions in the world. Classified under the EU AI Act as **limited risk** (transparency-obligation tier) by design — see [compliance/eu_ai_act_compliance.md](compliance/eu_ai_act_compliance.md) for the full reasoning and the boundary condition that would change this.

## Key stakeholders and interests

| Stakeholder | Interest |
|---|---|
| **Chleo (decision-maker / CEO-level sponsor)** | Wants field-support cost under control and installer capacity multiplied without proportional headcount growth; needs a plain-language view of *where* support cost concentrates (hardware vs. connectivity vs. installer error) to decide where to invest — hardware QA, app/firmware fixes, or installer training |
| **Own field installers** | Fewer unresolved on-site visits, faster access to fix guidance, fewer unnecessary escalations to senior technicians |
| **Partner SHK installers** (third-party trades) | Same triage need as own installers, but weaker access to internal engineering support — the copilot is often their *only* fast escalation path |
| **Support/service planning team** | Owns the escalation queue and (for the predictive module) service scheduling; wants fewer false hardware-fault dispatches and earlier visibility into likely-failing units |
| **Homeowners** (indirect) | Faster, more accurate first visits mean less downtime — not a direct user of any of the three modes, kept out of direct-data scope deliberately (see Out-of-scope) |
| **Compliance/legal function** | Needs the system to stay inside the EU AI Act's limited-risk tier and GDPR-compliant as real installer data is introduced in a pilot (see [compliance/](compliance/)) |

## Success criteria

At least two measurable outcomes, both traceable to metrics already scoped in Round 1's dashboard (see [dashboard/dashboard_documentation.md](dashboard/dashboard_documentation.md)) so the pilot can be evaluated against a baseline that already exists:

1. **First-visit fix rate improves by at least 10 percentage points** against the Round 1 synthetic baseline (69.1%) within the first 90 days of pilot use — i.e. fewer second truck rolls per fault ticket.
2. **False hardware-fault rate drops by at least 5 percentage points** against the Round 1 synthetic baseline (10.9%) within the same window — directly targeting the costliest misdiagnosis category named in the business problem above.
3. *(Supporting, not primary)* **Median time-to-classification under 30 seconds** for the Fault Triage Copilot's chat interaction, so the tool is faster than a phone call to a senior technician, not just more accurate.

These are pilot-phase targets against synthetic-data baselines, not production guarantees — see [strategic_plan.md](strategic_plan.md) for the concrete pilot design (real ticket volume, real measurement window) that would validate or revise them, and [roi_risk_assessment.md](roi_risk_assessment.md) for how they translate into ROI.

## Out-of-scope boundaries

- **No real customer, installer, or telemetry data** — Round 1 and Round 2 both use only public datasets (When2Heat) and a self-authored synthetic fault dataset, per the capstone brief's constraint. A pilot moving to real data is explicitly Round 2→pilot scope, not covered by this MVP (see [compliance/gdpr_documentation.md](compliance/gdpr_documentation.md)).
- **No autonomous action** — the system never issues unsupervised electrical or refrigerant-handling instructions, and never gates a safety decision without a human installer confirming it. This boundary is what keeps the system in the EU AI Act's limited-risk tier (see [compliance/eu_ai_act_compliance.md](compliance/eu_ai_act_compliance.md)); crossing it is explicitly out of scope for this product.
- **No homeowner-facing chatbot.** All three modes are installer- or support-team-facing by design (see [research/use_cases.md](research/use_cases.md)'s note on the dropped B2C candidate) — partly a product-focus decision, partly because a customer-facing conversational tool would need real complaint transcripts to be credible, which the data constraint above rules out.
- **No fine-tuning / custom model training.** The system uses general-purpose LLM APIs with retrieval grounding, not a trained classifier — keeping build cost and compliance surface area small enough for a small-medium manufacturer's budget.
- **No multi-market localization beyond German/English.** The MVP's language handling (LLM replies in whichever language the installer used, per [mvp/mvp_documentation.md](mvp/mvp_documentation.md)) is not tested against markets outside Germany.
- **The COP-drop predictive module uses a national public baseline, not per-unit installed-base telemetry** — Chleo's company has no real fleet telemetry yet, so this module demonstrates the *mechanism* (baseline comparison → deviation → alert), not a validated fault-prediction model. Calibrating real thresholds against confirmed field faults is named as pilot-phase follow-up work, not delivered here.

## How this evolved from Round 1

**No industry or use case change.** Per [feedback/round1_decision.md](feedback/round1_decision.md), no teaching-staff feedback called for a pivot after the Round 1 presentation — the reactive fault-triage use case remained the most de-risked of the three lifecycle candidates and the underlying business case (installer shortage, target-vs-actual demand gap, documented hardware-vs-connectivity ambiguity) held up. Round 2 **deepens** the same use case rather than restarting:

- **POC → MVP**: the n8n/Telegram keyword-grounded POC becomes a Python/Streamlit RAG application with real OpenAI embeddings + Pinecone vector search, exactly the upgrade path the POC's own documentation named as Round 2 scope.
- **One flagship → three integrated modes**: the two use-case candidates sequenced but not built in Round 1 (the Commissioning-Completeness Checker and the COP-Drop predictive copilot) are now built as genuinely functional companion modes in the same MVP, not left as roadmap slides.
- **Compliance moves from stated assumption to documented package**: Round 1 treated "limited risk" and "no GDPR scope" as assumptions to revisit; Round 2 formalizes both (see [compliance/](compliance/)) now that a pilot touching installer-identifiable data is in view.
- **Cost estimate moves from Round 1 build cost only to a full ROI/risk assessment** covering pilot-scale run costs and 12/36-month return (see [roi_risk_assessment.md](roi_risk_assessment.md)).
