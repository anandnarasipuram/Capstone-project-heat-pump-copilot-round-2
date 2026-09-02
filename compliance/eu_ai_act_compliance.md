# EU AI Act Compliance — Heat Pump Copilot

> Regulation (EU) 2024/1689 (the "AI Act"). Formalizes the "limited risk" framing that Round 1 treated as a stated assumption (see [../research/opportunities_risks.md](../research/opportunities_risks.md), risk #2, and [../research/sector_research.md](../research/sector_research.md)) into a documented classification with reasoning, as Round 2 requires.

## 1. Risk classification — step-by-step reasoning

The Act's classification is a screening funnel: prohibited → high-risk (two independent routes) → limited-risk (transparency only) → minimal-risk. Each step is walked below against the actual system described in [../use_case_definition.md](../use_case_definition.md).

### Step 1 — Prohibited practices (Article 5)

The eight prohibited practices (subliminal manipulation, exploitation of vulnerabilities, social scoring, real-time remote biometric identification in public for law enforcement, biometric categorization inferring sensitive attributes, workplace/education emotion recognition, predictive policing from profiling alone, untargeted facial-image scraping) all concern manipulation of people or biometric/behavioral inference. This system classifies **equipment fault symptoms**, not people — no biometric data, no emotion inference, no behavioral profiling of installers or homeowners.

**Result: not prohibited.**

### Step 2 — High-risk, Annex I route (AI as a safety component of a regulated product)

Annex I high-risk status attaches to an AI system that is a **safety component** of a product already subject to third-party conformity assessment under EU product-safety legislation (e.g. the Machinery Regulation, gas appliances, radio equipment) — defined in Art. 3(14) as a component whose failure or malfunction endangers health/safety, or which is required for the safe functioning of the product.

The copilot is a **separate, advisory chat/web application** the installer consults — it is not embedded in the heat pump's control firmware, does not read live sensor data from the unit, and cannot trigger, block, or alter any physical function of the appliance (compressor, valves, safety cutouts). Its output is text guidance a human reads and acts on independently. It is therefore not a component of the heat pump at all, let alone a safety component.

**Result: not high-risk under Annex I** — with an explicit, stated boundary condition: this determination reverses immediately if a future version is wired to auto-trigger a shutdown/lockout, bypass a technician's manual confirmation, or otherwise gate the appliance's own operation. See [../roi_risk_assessment.md](../roi_risk_assessment.md), risk #1.

### Step 3 — High-risk, Annex III route (specific high-stakes use-case areas)

Walking each of the eight listed areas against this system, including the two closest calls in detail:

| Annex III area | Applies? | Reasoning |
|---|---|---|
| 1. Biometrics | No | No biometric identification or categorization of any kind |
| **2. Critical infrastructure** (incl. safety components managing the *supply* of water, gas, heating, or electricity) | **No — closest call, reasoned explicitly** | "Heating" is named in this category, which is why it gets a full paragraph below rather than a one-line dismissal |
| 3. Education/vocational training | No | Not used for admission, assessment, or educational access decisions |
| **4. Employment, workers' management, self-employment access** | **No — second closest call** | See reasoning below |
| 5. Essential private/public services (credit, insurance, emergency-service dispatch, benefits eligibility) | No | Not used for credit/insurance/benefits eligibility; not emergency-service dispatch (see below) |
| 6. Law enforcement | No | No involvement |
| 7. Migration, asylum, border control | No | No involvement |
| 8. Administration of justice, democratic processes | No | No involvement |

**On Annex III(2) — critical infrastructure/heating supply:** this category targets AI safety components that manage or operate infrastructure-level supply networks — e.g. grid balancing, district-heating network control, gas-network safety systems — where failure disrupts service to many users at once. This copilot operates at the level of a single household appliance's after-sales fault diagnosis; it does not manage, operate, or control any heating, gas, or electricity *supply network* or *infrastructure*, and a failure of the copilot (a wrong triage suggestion) affects one installer's next action on one unit, not a supply network. It falls outside this category.

**On Annex III(4) — employment/workers' management:** this category targets AI used to make or materially influence decisions about workers — recruitment, task allocation, performance evaluation, promotion, or termination. The copilot's outputs are diagnostic classifications of *equipment symptoms*, not evaluations of *installer performance*. This is a deliberate, stated exclusion (see [../use_case_definition.md](../use_case_definition.md), Out-of-scope) — the "override rate" metric named as a pilot KPI in [../strategic_plan.md](../strategic_plan.md) monitors *tool accuracy*, and using it to evaluate individual installers would cross into this Annex III category. That reuse is explicitly ruled out, not just unaddressed.

**On Annex III(5) — emergency-service dispatch, as the nearest analogy to "escalation routing":** this category targets dispatch of life/property emergency services (police, fire, ambulance). Routing a support ticket to a hardware technician is commercial after-sales service prioritization, not an emergency-service function — no plausible reading places it in this category.

**Result: not high-risk under Annex III.**

### Step 4 — Limited risk: transparency obligations (Article 50)

The system interacts directly with natural persons (installers, via chat) and is not "obvious from context" that it's AI-driven by default — so **Article 50(1)'s transparency obligation applies**: users must be informed they are interacting with an AI system, clearly and at the latest at the time of first interaction.

**Result: LIMITED RISK.** The system's only mandatory AI Act obligation is the Article 50 transparency disclosure — already implemented (see Section 2).

### Step 5 — Minimal-risk residual

Not applicable — the system clears Step 4, so it sits in the limited-risk tier, not minimal-risk. Voluntary codes of conduct (Art. 95) are available but not adopted as formal commitments in this Round 2 package; the "voluntarily adopted good practices" in Section 3 cover the substance of what such a code would ask for.

## 2. Mandatory requirements summary — Limited risk (Article 50)

| Requirement | Status | Evidence |
|---|---|---|
| Disclose to the user that they are interacting with an AI system | ✅ Implemented | POC: every Telegram reply is framed as "AI-suggested triage, confirm before acting" (see [../poc/poc_documentation.md](../poc/poc_documentation.md)). MVP: persistent sidebar disclosure + inline caption on every chat response (see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md)) |
| Disclosure is clear, distinguishable, and provided no later than first interaction | ✅ Implemented | Disclosure is on-screen before and with every response, not buried in terms of service |
| Exemption for "obvious from context" | Not relied on | Explicit disclosure is kept even though a support chatbot might arguably qualify for the exemption — safer and clearer for field installers under time pressure |
| Third-party conformity assessment, CE marking, EU database registration, Annex IV technical documentation | ❌ Not legally required at this tier | See Section 3 for what's voluntarily documented anyway |

**If a future version were reclassified High-risk** (per the boundary conditions in Steps 2–3), the mandatory obligations would expand substantially: a risk-management system (Art. 9), data governance requirements (Art. 10), Annex-IV-standard technical documentation (Art. 11), automatic logging (Art. 12), instructions for deployers (Art. 13), human-oversight-by-design (Art. 14), accuracy/robustness/cybersecurity requirements (Art. 15), and conformity assessment + CE marking + EU database registration before market placement. None of these are triggered today; they are listed here so a future scope change (e.g. autonomous shutdown control) is evaluated against a known bar, not discovered late.

## 3. Conformity Assessment Summary

*(No formal third-party conformity assessment is legally required at limited-risk. This is a self-assessment summary — good consulting practice for a client who may face investor or partner due diligence, and forward-compatible if the system is later reclassified.)*

**Intended purpose:** Advisory decision-support for field installers and support staff triaging heat pump fault reports and commissioning completeness. Not intended, marketed, or authorized for autonomous control of any heat pump function, and not intended for evaluating individual installer performance.

**Classification outcome:** Limited risk (Article 50 transparency obligation only) — see Section 1 for full reasoning. Re-assessed whenever the product scope changes (named explicitly as a strategic-plan gate — see [../strategic_plan.md](../strategic_plan.md)).

**Transparency measure implemented:** Persistent, on-screen AI-interaction disclosure across both the POC (Telegram) and MVP (Streamlit) surfaces, present on every single AI-generated response, not just a one-time onboarding notice.

**Human oversight design:** Every classification is explicitly labeled advisory ("confirm before acting"); the system's own architecture routes to a documented safe-default (escalate to a senior technician) whenever the model's output can't be parsed or a call fails, rather than silently proceeding — see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md), "Error handling." No workflow in either the POC or the MVP allows a classification to trigger a physical action without a human installer's independent judgment in between.

**Data governance (voluntarily documented, not mandated at this tier):** Grounding data is a small, sourced, versioned manual knowledge base with documented provenance and copyright notes (see [../data/manuals/README.md](../data/manuals/README.md)); no personal data is used in the manual corpus. See [gdpr_documentation.md](gdpr_documentation.md) for the separate, mandatory GDPR treatment of any installer-identifiable data introduced once a pilot uses real chat identities.

**Monitoring approach:** LangSmith trace sampling (Round 1 evidence: [../langsmith/monitoring_notes.md](../langsmith/monitoring_notes.md)) plus the dashboard metrics already scoped in [../dashboard/dashboard_documentation.md](../dashboard/dashboard_documentation.md) — first-visit fix rate, false-hardware-fault rate, connectivity-failure rate by model/firmware — give an operational accuracy signal even though formal accuracy/robustness requirements (Art. 15) aren't mandatory here.

**Accountability:** Chleo's company is the deployer or record for this system. OpenAI (foundation model) and Pinecone (vector database infrastructure) are upstream providers with their own separate obligations as GPAI/infrastructure providers under the Act — out of scope for this deployer-side document, referenced only where their behavior affects this system's own classification (e.g. Art. 50 disclosure obligations apply to the deployer regardless of which model is used underneath).

**Change-control commitment:** This classification is re-run (not assumed to still hold) before: (a) any move toward autonomous appliance control, (b) any use of copilot output in installer performance evaluation, or (c) market expansion into a jurisdiction with different AI regulation. Named explicitly so it isn't a one-time exercise that goes stale.

## 4. Technical Documentation Outline (ToC / skeleton)

Not mandatory at limited-risk (Annex IV applies to high-risk systems), but sketched here as a forward-compatible skeleton — both good practice for investor/partner due diligence and ready to fill in immediately if a future reclassification requires it:

1. **General description** — intended purpose, deployment context (field installers, support staff), the three modes (see [../use_case_definition.md](../use_case_definition.md))
2. **System architecture** — retrieval-augmented generation pipeline, module map (see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md) architecture diagram)
3. **Data used** — manual knowledge base provenance and limitations ([../data/manuals/README.md](../data/manuals/README.md)), synthetic fault dataset and public COP baseline ([../data/dataset_documentation.md](../data/dataset_documentation.md))
4. **Model description** — OpenAI `gpt-4o-mini` (classification) and `text-embedding-3-small` (retrieval) via API, no fine-tuning; foundation-model-provider documentation referenced, not reproduced
5. **Human oversight measures** — advisory-only framing, mandatory disclosure, safe-default-to-escalation fallback design
6. **Known limitations and risk treatment** — cross-referenced to [../poc/poc_documentation.md](../poc/poc_documentation.md) "Limits vs. production," [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md) "Limits vs. production," and the full risk matrix in [../roi_risk_assessment.md](../roi_risk_assessment.md)
7. **Performance/evaluation approach** — offline unit tests (16 tests, [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md)), LangSmith trace sample and experiment ([../langsmith/monitoring_notes.md](../langsmith/monitoring_notes.md)), dashboard operational metrics
8. **Change log / version history** — Round 1 POC → Round 2 MVP upgrade path, tracked in this repository's git history
9. **Post-market monitoring plan** — phase-gated KPIs for pilot → full deployment (see [../strategic_plan.md](../strategic_plan.md))
