# GDPR Documentation — Heat Pump Copilot

> Round 1 used only public/synthetic data and explicitly deferred GDPR depth to Round 2 (see [../research/opportunities_risks.md](../research/opportunities_risks.md), risk #5, and [../feedback/round1_decision.md](../feedback/round1_decision.md)). This document brings that into scope now that a real pilot (see [../strategic_plan.md](../strategic_plan.md)) would process installer-identifiable data. **No real personal data is processed by the Round 1 POC or Round 2 MVP as built and demoed** — both run on public and self-authored synthetic data only. This document describes what changes, and what governance needs to be in place, the moment a pilot uses real installers.

## 1. Data flow map

```
                              ┌─────────────────────────────┐
  Installer (data subject) ──►  Chat interface               │
  types symptom text, may     │  • POC: Telegram bot          │
  incidentally include a      │  • MVP: Streamlit app          │
  homeowner's name/address    └───────────┬───────────────────┘
  in free text                            │
                                           ▼
                              ┌─────────────────────────────┐
                              │  App backend                 │
                              │  • POC: n8n workflow          │
                              │  • MVP: Python/core modules    │
                              └───┬──────────────┬────────────┘
                                  │              │
                    (uncoded      │              │ (manual KB
                     symptoms      │              │  content only,
                     only)         ▼              │  no personal data)
                     ┌──────────────────┐         ▼
                     │  OpenAI API       │  ┌──────────────────┐
                     │  (embeddings +    │  │  Pinecone          │
                     │  classification)  │  │  (vector search,   │
                     │  — US-based       │  │  MVP only)         │
                     │  processor        │  │  — region-         │
                     └────────┬──────────┘  │  configurable      │
                              │              └──────────────────┘
                              ▼
                     ┌──────────────────┐
                     │  LangSmith         │  Live in the MVP (every
                     │  (trace logging)   │  interaction, when
                     │  — US or EU        │  LANGSMITH_API_KEY is set)
                     │  endpoint          │  — optional, off by default
                     └────────┬──────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  Dashboard         │  Aggregated/pseudonymized
                     │  (Tableau/PowerBI) │  metrics only — no raw
                     │  — internal        │  symptom text, no names
                     │  reporting         │
                     └──────────────────┘

  POC-only extra hop: Telegram itself (message relay) is a third-party
  processor the installer's device talks to before n8n ever sees the
  message — see Section 6.
```

**Key point for the pilot design:** the MVP's current build does not persist chat history beyond the browser session (`st.session_state`, cleared on refresh) — see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md). A pilot that wants the dashboard metrics (first-visit fix rate, false-hardware-fault rate) working on real tickets needs to add a persistence layer, which is exactly the point at which most of this document's obligations become operative rather than forward-looking.

## 2. Processing activities register

| Activity | Purpose | Data categories | Legal basis | Retention (recommended for pilot) | Recipients / processors |
|---|---|---|---|---|---|
| Fault-triage chat interaction (POC, Telegram) | Real-time fault classification/escalation for field installers | Telegram user ID, username/first name, message text, timestamp | Legitimate interest (Art. 6(1)(f)) — providing an internal support tool to the manufacturer's own and partner installers; for partner SHK installers, may instead rest on performance of the service contract between the manufacturer and the partner's firm | Session-only today; recommend a fixed 12-month window for ticket-quality analytics, then anonymize | OpenAI (processor, classification), Telegram (processor, message relay), LangSmith (processor, if activated) |
| Fault-triage chat interaction (MVP, Streamlit) | Same purpose, RAG-based | Free-text symptom (may incidentally include a homeowner's name/address), model/firmware metadata, session-only chat history | Legitimate interest | Not persisted beyond the browser session in the current build | OpenAI (embeddings + classification), Pinecone (vector similarity query), **LangSmith (trace logging, when `LANGSMITH_API_KEY` is set — see the dedicated row below)** |
| Commissioning checklist submission | Confirm commissioning completeness before sign-off | Model, firmware, checklist responses; a pilot would add an installer ID for accountability (not present in the current build) | Legitimate interest / contractual necessity (installation quality-assurance obligation) | Per job record, aligned to warranty + statutory limitation period (Germany: typically 2 years statutory warranty on goods) | OpenAI (summary generation), LangSmith (trace logging, same condition as above) |
| COP-drop predictive reading | Early-warning fleet monitoring | Unit reading (COP value, model, date), keyed to a device/unit ID — no personal data if kept device-keyed rather than homeowner-keyed | Legitimate interest | Rolling 24-month service-planning window, then aggregate | OpenAI (alert generation) — no personal data leaves for the baseline computation itself (public dataset); LangSmith (trace logging, same condition as above) |
| Dashboard analytics | Business reporting: first-visit fix rate, false-hardware-fault rate, connectivity-failure rate by model/firmware | Aggregated/pseudonymized statistics only — no raw symptom text, no installer names at the visualization layer | Legitimate interest | Indefinite for genuinely aggregated/anonymized statistics (GDPR retention limits apply to personal, not anonymized, data) | Internal (Chleo's company); Tableau/PowerBI as processor if cloud-hosted |
| LangSmith trace logging | AI system quality monitoring/evaluation — **live in the MVP as of Round 2** (`core/tracing.py` + `core/pipeline.py`, not the POC-era placeholder — see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md), "Monitoring") | Full prompt/response content for every traced interaction across all 3 modes — may carry the same incidental personal data as the chat interaction | Legitimate interest (algorithmic accountability / quality assurance) | Recommend 90 days for raw traces, longer only for anonymized eval sets | LangSmith (processor) — **use the EU endpoint** (`LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com` in [../mvp/.env.example](../mvp/.env.example)) if the workspace is EU-region, confirmed necessary during this project's own live testing (the default US endpoint 403s otherwise) |

## 3. Dashboard user profile and GDPR treatment

The processing register above names the dashboard's recipient only as "Internal (Chleo's company)" — too vague to actually apply GDPR to. This section names who that is and what specifically constrains their access.

**Primary profile — Service Operations Lead** (the "Support/service planning team" stakeholder from [../use_case_definition.md](../use_case_definition.md))

| | |
|---|---|
| **Views** | All 7 sheets of the "Copilot Operations Metrics" dashboard ([../dashboard/dashboard_documentation.md](../dashboard/dashboard_documentation.md)) — first-visit fix rate, false-hardware-fault rate, avg. commissioning time, connectivity-failure rate by model, fault category mix over time, ticket volume by installer type, first-visit fix rate by installer type |
| **Purpose** | Operational decision-making — where to invest (hardware QA / firmware fixes / installer training), which product line needs attention |
| **Data actually visible** | Aggregated rates and counts only, grouped by model/firmware/installer type (`own_field_installer` vs `partner_SHK`) — never a raw ticket, never an installer's name, never symptom free text. This is a property of the dashboard's own data pipeline (built from an aggregated CSV extract — see [../dashboard/dashboard_documentation.md](../dashboard/dashboard_documentation.md)), not just a policy promise: there is no path from this profile's view back to an individual installer's or homeowner's identity |
| **Legal basis** | Legitimate interest (Art. 6(1)(f)) — the same basis as the underlying ticket processing (Section 2), since this is downstream reporting on data already lawfully collected for support purposes; aggregate internal reporting needs no separate consent |
| **Explicit boundary** | This profile may **not** use sheet #7 ("First-Visit Fix Rate by Installer Type") to evaluate or discipline a *named* individual installer — that sheet's grouping is a category (own vs. partner), not an identity, by design. Extending it to per-installer-name breakdowns would be a new processing activity requiring its own legal-basis review and Annex III(4) reassessment (see [eu_ai_act_compliance.md](eu_ai_act_compliance.md)) — this is the same governance commitment already made for the chat interaction, applied consistently to the dashboard |

**Secondary profile — Chleo (CEO/Sponsor)**: views the same dashboard periodically (see [../strategic_plan.md](../strategic_plan.md)'s monthly steering review) plus the "Preliminary Analysis" dashboard (market context, no personal data at all). Same legal basis, same aggregate-only visibility — no elevated access to raw tickets for this or any profile.

**Access control — a stated gap, not yet solved**: `dashboard.twbx` today is a local packaged workbook with no access control of its own; anyone holding the file can open it. Fine for a capstone demo on synthetic data, **but must change before a pilot**: publish to Tableau Server/Cloud (or Power BI Service) with named-user or role-based access restricted to the two profiles above, plus audit logging of who opened it and when. Named here in the same spirit as the PII-scrubber gap in the DPIA below — a concrete pre-pilot task, not a design flaw to redesign around.

**Retention**: the dashboard carries no retention obligation beyond its source data's (Section 2's "Dashboard analytics" row) — once the underlying ticket data is anonymized/aggregated per that row's schedule, the dashboard reflects only anonymized history and falls outside GDPR's personal-data retention rules entirely (anonymized data isn't personal data under GDPR Recital 26).

## 4. Short DPIA — highest-risk processing

**Processing assessed:** the Fault Triage Copilot's free-text chat interaction (POC and MVP), because it is the only processing activity where a data subject (the installer, and potentially an incidentally-named homeowner) has the least control over what's captured — free text can carry more than the form fields around it anticipate.

| DPIA element | Assessment |
|---|---|
| **Necessity & proportionality** | Free-text input is necessary — the core business problem is that installer symptom language has no fixed schema (see [../use_case_definition.md](../use_case_definition.md)); a structured-only form would defeat the tool's purpose. Proportionality is maintained by *not* collecting more than the message itself: no location tracking, no device fingerprinting, no persistent user profile in the current build. |
| **Risk to data subjects** | (a) An installer's free text may incidentally include a homeowner's name or address, sending third-party personal data to OpenAI/Pinecone (and, when tracing is enabled, LangSmith too — see the trace-logging row above) without that homeowner's knowledge. (b) A pilot's ticket log, once persisted, could be used to evaluate individual installers' performance if repurposed — a use this project explicitly rules out (see [eu_ai_act_compliance.md](eu_ai_act_compliance.md), Annex III(4) reasoning) but which remains a governance risk if not enforced. (c) Chat content transiting a US-based LLM/monitoring processor raises a cross-border-transfer question (Section 6). |
| **Likelihood** | Medium — installers describing a job naturally sometimes reference the site/homeowner, but the symptom vocabulary is technical (fault codes, error messages) more often than personal. |
| **Severity** | Low–medium — the data category at risk (a name/address incidentally in a support ticket) is not special-category data, but homeowners have not consented to or been informed of this specific processing. |
| **Mitigations** | (1) Pilot onboarding instructs installers to describe the *unit's* symptom, not the customer's details — a training/prompt-design fix, not a technical block, stated as a limitation, not solved by policy alone. (2) A production version should add a lightweight PII scrubber before the symptom reaches OpenAI/Pinecone — named here as a pilot-readiness gap, not yet built. (3) Ticket records, once persisted, are keyed to job/unit ID, not homeowner identity, by design — no homeowner-identifiable field is in the pilot's planned schema. (4) The Annex III(4) exclusion (no use in installer performance evaluation) is a governance commitment that should be written into the pilot's data-use policy, not left implicit. |
| **Residual risk after mitigation** | Low. **Recommendation: consult a DPO or external privacy counsel before pilot go-live**, specifically to review the PII-scrubbing gap in (2) above and confirm the legitimate-interest balancing test for partner SHK installers who aren't direct employees. This DPIA is a Round 2 capstone-level short-form, not a substitute for that review. |

## 5. Data subject rights support

- **Right to access, rectification, erasure, restriction, portability, objection** (Arts. 15–21) all apply once real installer data is persisted. In the current build (no persistence beyond a browser session), most requests are trivially satisfiable — there is nothing stored to access or erase. A pilot's persistence layer should key every record to a job/ticket ID linked to an installer ID, so an access/erasure request can be fulfilled by a targeted query rather than a manual search.
- **Right to object** (Art. 21) — since the legal basis is legitimate interest, not consent, installers (or partner-firm data protection contacts, on their behalf) can object, triggering a documented balancing test rather than automatic compliance or automatic refusal.
- **Right not to be subject to a decision based solely on automated processing with legal/significant effect** (Art. 22) — **does not apply here**, by the same reasoning pattern used in [eu_ai_act_compliance.md](eu_ai_act_compliance.md): the system's outputs classify *equipment symptoms*, not the installer as a person, and produce no legal or similarly significant effect on the installer's rights, status, or entitlements. This is stated explicitly, not left to be assumed, because it's the GDPR question most often asked about AI classification tools.
- **Erasure exceptions** — checklist/commissioning records may be retained beyond an erasure request where necessary for warranty/liability record-keeping (a recognized GDPR exception, Art. 17(3)(b)); this exception should be stated to installers up front, not discovered at request time.

## 6. Third-party and cross-border transfers

| Processor | Role | Location / transfer mechanism | Notes |
|---|---|---|---|
| **OpenAI** | Classification (chat completion) + embeddings | US-based by default; relies on Standard Contractual Clauses / EU-US Data Privacy Framework participation as the transfer mechanism | **Action before pilot:** execute OpenAI's Data Processing Addendum and confirm current transfer-mechanism status directly — vendor privacy terms change, and this document should not be treated as a substitute for checking OpenAI's current DPA at pilot go-live. |
| **Pinecone** | Vector similarity search (MVP RAG) | Region-configurable (`PINECONE_REGION` in [../mvp/.env.example](../mvp/.env.example), defaults to AWS `us-east-1`) | **Recommendation:** confirm current EU region availability with Pinecone and switch to an EU region for the pilot if available, to minimize cross-border transfer scope — this is a one-line config change (`PINECONE_REGION`), not a code change, so it costs nothing to adopt once confirmed. |
| **LangSmith** | Monitoring/trace logging | US by default, EU endpoint available | Already scaffolded as an optional `.env` variable from Round 1; use it for the pilot. |
| **Telegram** (POC channel only) | Message relay | Non-EU entity (Telegram FZ-LLC) | Additional third-party surface specific to the POC's Telegram channel, not present in the MVP's own Streamlit interface. **This is a concrete, practical reason to route a real pilot through the MVP rather than the POC's Telegram bot** — one fewer third-party data processor in the chain, on top of the RAG-quality upgrade already documented in [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md). |
| **Tableau / PowerBI** | Dashboard hosting (if cloud) | Vendor-dependent; both Salesforce (Tableau) and Microsoft (PowerBI) offer EU-region hosting | Use EU-region hosting for the pilot; the dashboard layer only receives aggregated/pseudonymized metrics regardless (Section 2), which further limits transfer exposure at this layer. |

**Overall transfer posture:** every processor above is a well-known vendor with an existing GDPR transfer mechanism in principle (SCCs, adequacy frameworks, or EU-region hosting options); none of this is exotic. The concrete pre-pilot task is administrative — execute DPAs, confirm current transfer mechanisms, and prefer EU regions/endpoints where a config flag already makes that free — not a redesign of the system.
