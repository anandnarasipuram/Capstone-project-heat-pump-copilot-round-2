# ROI and Risk Assessment — Heat Pump Copilot

> Extends [cost_estimation/cost_analysis.md](cost_estimation/cost_analysis.md) (Round 1 build cost only) into a full Round 2 ROI and risk package. Ties directly to the two measurable success criteria in [use_case_definition.md](use_case_definition.md) and the pilot design in [strategic_plan.md](strategic_plan.md).
> **Headline framing:** all business-value figures below are **gross operational cost avoidance from a documented Round 1 synthetic-data baseline** (see [data/dataset_documentation.md](data/dataset_documentation.md)), not audited client financials or guaranteed net profit — they become real profit only if the avoided technician/truck-roll cost is actually reallocated or reduced, not automatically. Treat every number here as a pilot-validation target, not a committed forecast.

## 1. Upfront (build) costs

| Phase | Work item | Effort | Cost (€650/day) |
|---|---|---|---|
| **Round 1** (already spent — see [cost_estimation/cost_analysis.md](cost_estimation/cost_analysis.md)) | Research, use-case scoping, dataset authoring, n8n POC, LangSmith sample, PowerBI/Tableau dashboard, QA/docs | ~19 days | €12,350 |
| **Round 2** | MVP build — Pinecone/OpenAI RAG upgrade, 3-mode Streamlit app (fault triage + checklist + predictive), offline test suite | 6 days | €3,900 |
| **Round 2** | ROI/risk assessment, EU AI Act + GDPR compliance package, strategic deployment plan | 4 days | €2,600 |
| **Round 2** | Final presentation build + QA/integration pass across both rounds' deliverables | 2 days | €1,300 |
| **Round 2 subtotal** | | **12 days** | **€7,800** |
| **Combined Round 1 + 2 build** | | **~31 days** | **≈ €20,150** |

## 2. Ongoing (run) costs — pilot scale, per month

Pilot scale assumption carried from Round 1 (see Assumptions table below): ~15–30 installers, ~750–1,500 queries/month across all three modes.

| Item | Basis | Cost/month |
|---|---|---|
| OpenAI API (chat completions + embeddings, 3 modes) | ~1,000 queries/mo × ~3–4K tokens avg, plus embedding calls for uncoded symptoms | €70–150 |
| Pinecone (serverless, free tier likely sufficient at this corpus size — 16 manual entries) | Contingency if pilot volume outgrows free tier | €0–25 |
| App hosting (Streamlit Community Cloud free tier, or a small VM) | Reliability upgrade from free tier once pilot is customer-facing | €0–25 |
| LangSmith | Free/dev tier at pilot volume; lowest paid tier once tracing volume grows | €0–40 |
| n8n (legacy Telegram channel, if kept running alongside the MVP) | Optional — Cloud Starter or small self-hosted VM | €0–50 |
| **Subtotal, no retainer** | | **≈ €150–300/month (≈ €1,800–3,600/year)** |
| Optional maintenance & support retainer | 0.5 day/month × €650 | +€325/month |

## 3. Quantified business value

Grounded in the Round 1 synthetic-dataset baseline (n=220 tickets — see [data/dataset_documentation.md](data/dataset_documentation.md)) and the two measurable success criteria in [use_case_definition.md](use_case_definition.md).

### Assumptions table

| # | Assumption | Value | Rationale |
|---|---|---|---|
| 1 | Pilot query volume | 9,000–18,000 tickets/year (750–1,500/month) | Round 1 cost_analysis.md assumption #3, unchanged |
| 2 | False-hardware-fault baseline rate | 10.9% | Round 1 synthetic dataset — the costliest misdiagnosis (triggers an unneeded parts/technician visit) |
| 3 | Target false-hardware-fault reduction | 5 percentage points → ~5.9% | Use case success criterion #2 |
| 4 | Cost per avoided false-hardware-fault dispatch | €150 | Blended technician + travel + parts-logistics cost for an unnecessary hardware visit; a stated planning estimate, not an audited client figure |
| 5 | First-visit-fix baseline rate | 69.1% | Round 1 synthetic dataset |
| 6 | Target first-visit-fix improvement | 10 percentage points → ~79.1% | Use case success criterion #1 |
| 7 | Cost per avoided second visit | €90 | Installer time + travel for a return visit a correct first-visit fix would have prevented |
| 8 | Realization factor | 70% | Conservative discount for pilot-phase reality — partial installer adoption, some tickets outside the tool's coverage, imperfect behavior change |
| 9 | Value ramp across the 3 phases | Year 1 (pilot): 50% of steady-state value · Year 2: 85% · Year 3 (full deployment): 100% | Matches the POC→Pilot→Full phasing in [strategic_plan.md](strategic_plan.md) — value doesn't appear on day one |

### Steady-state annual value (before ramp)

| Value stream | Low (9,000 tickets/yr) | High (18,000 tickets/yr) |
|---|---|---|
| False-hardware-fault dispatches avoided (5pp × tickets × €150 × 70%) | €47,250 | €94,500 |
| Second visits avoided (10pp × tickets × €90 × 70%) | €56,700 | €113,400 |
| **Total steady-state value/year** | **≈ €104,000** | **≈ €208,000** |

Central case used below: midpoint **≈ €156,000/year** steady-state, ≈ €13,000/month.

## 4. ROI — 12 and 36 months

`ROI = (Net Benefit / Total Cost) × 100`

| | Year 1 (pilot, 50% ramp) | Years 1–3 cumulative (36 months) |
|---|---|---|
| Value realized | €78,000 | €78,000 + €132,600 (Yr2 @85%) + €156,000 (Yr3 @100%) = **€366,600** |
| Total cost | Build €20,150 (one-time) + ongoing €2,700/yr (midpoint of €150–300/mo) = **€22,850** | Build €20,150 (one-time) + ongoing €2,700/yr × 3 = **€28,250** |
| Net benefit | €78,000 − €22,850 = **€55,150** | €366,600 − €28,250 = **€338,350** |
| **ROI** | **(55,150 / 22,850) × 100 ≈ 241%** | **(338,350 / 28,250) × 100 ≈ 1,198%** |

**Sensitivity (low/high value scenarios, same cost base):**

| Scenario | Year 1 ROI | 36-month ROI |
|---|---|---|
| Conservative (low value band) | ≈ 140% | ≈ 750% |
| Optimistic (high value band) | ≈ 342% | ≈ 1,650% |

### Break-even note

At the central-case Year 1 value run-rate (~€6,500/month realized during the 50%-ramp pilot), the €22,850 Year 1 total cost is recovered in roughly **3.5–4 months** into the pilot — i.e. break-even is expected within the pilot phase itself, not deferred to full deployment. This is highly sensitive to assumption #8 (realization factor) and #9 (ramp) — see [strategic_plan.md](strategic_plan.md) for the pilot KPIs that would confirm or revise it before greenlighting full deployment.

## 5. Risk matrix

Likelihood and impact scored 1 (low) – 5 (high). At least six risks spanning regulatory, technical, ethical, and operational categories, per the Round 2 checklist.

| # | Category | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|---|
| 1 | Regulatory | **EU AI Act boundary risk** — repositioning the copilot as gating a safety decision autonomously (rather than advisory) would tip it into the high-risk tier and its heavier obligations | 2 | 5 | Keep advisory-only, human-in-the-loop positioning explicit in product UI, contracts, and marketing; legal review gate before any scope change that touches autonomous action — see [compliance/eu_ai_act_compliance.md](compliance/eu_ai_act_compliance.md) |
| 2 | Regulatory | **GDPR exposure grows** as a real pilot introduces installer-identifiable data (chat handles, employment/installer-type fields) not present in Round 1/2's public/synthetic data | 4 | 3 | Short DPIA completed before pilot go-live, data minimization (no homeowner PII collected), defined retention limits, installer consent/notice — see [compliance/gdpr_documentation.md](compliance/gdpr_documentation.md) |
| 3 | Technical | **LLM misclassification / hallucination** leads to an incorrect escalation route (e.g. a genuine hardware fault classified as installer error) | 3 | 4 | Deterministic lookup-first routing (13 known codes bypass the LLM entirely), JSON-mode structured output with a documented safe-default-to-escalation fallback (never silently "no action needed"), mandatory human confirmation before any physical work, periodic trace review via LangSmith |
| 4 | Technical | **Third-party API dependency** — OpenAI/Pinecone outage, breaking API change, or pricing increase disrupts the live capability | 3 | 3 | Graceful degradation already built into the MVP (keyword-match fallback for retrieval, deterministic checklist/COP math work with zero API keys — see [mvp/mvp_documentation.md](mvp/mvp_documentation.md)); monitor vendor status pages; ROI model already budgets a cost range, not a point estimate, to absorb pricing drift |
| 5 | Ethical | **Automation bias / over-reliance** — installers stop independently verifying AI suggestions, eroding the human-in-the-loop safety design the whole compliance posture depends on | 3 | 4 | Persistent on-screen disclaimer on every response ("AI-suggested triage — confirm before acting"), installer training at pilot kickoff, override-rate tracked as an explicit pilot KPI (how often installers disagree with or escalate past the suggestion) |
| 6 | Ethical | **Unequal service quality** between own field installers and partner SHK installers (partners have weaker access to internal engineering context/history), risking inequitable escalation outcomes | 2 | 2 | Same tool and knowledge base for both groups by design (no tiered access); false-hardware-fault and first-visit-fix rates monitored split by `installer_type` in the dashboard to catch drift early |
| 7 | Operational | **Low installer adoption** — installers revert to phone calls to senior technicians rather than trusting/using a new tool | 3 | 4 | Pilot communication plan with named champions among partner SHK installers, adoption rate tracked as an explicit go/no-go KPI for pilot→full deployment, low-friction chat-based interaction (no new app to install for the flagship mode) |
| 8 | Operational | **Manual knowledge base staleness** as the EU F-Gas refrigerant phase-out (2027–2028) shifts the hardware/refrigerant mix in the field, aging the fault taxonomy faster than content gets updated | 3 | 3 | Knowledge base is modular/data-driven JSON, not hardcoded logic, in both the POC and the MVP (a content change, not a rebuild); a named content-owner role reviews the knowledge base quarterly, flagged explicitly in [strategic_plan.md](strategic_plan.md) |

**Overall risk posture:** no single risk scores above 4×5=20 (max: risk #1 at 2×5=10, risk #3/#5/#7 at 3×4=12) — the highest-severity risk (EU AI Act boundary) is low-likelihood specifically *because* the product is deliberately scoped to stay advisory. The mitigations that matter most operationally are #3, #5, and #7 (technical accuracy, human-in-the-loop discipline, and adoption) — all three are named as explicit pilot-phase KPIs in [strategic_plan.md](strategic_plan.md), not left as slide-only commitments.
