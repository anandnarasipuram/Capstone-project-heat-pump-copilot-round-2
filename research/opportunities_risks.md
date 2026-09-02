# Opportunities & Risks

> Industry/sector: Home Energy & HVAC (Heat Pumps)
> Use case: Heat Pump Field Commissioning & API/App Connectivity Copilot
> See [[sector_research]] for the sourced market/regulatory context this builds on, and [preliminary_analysis.html](preliminary_analysis.html) for the visual opportunity/risk map and dataset-landscape comparison (EU-wide EHPA figures alongside the Germany-specific BWP figures used here).

## Opportunities

1. **Installer shortage as a capacity lever, not just a cost problem.** Germany trains ~12,000 SHK tradespeople/year against an estimated ~35,000/year need, and independently, reaching the 6M-heat-pump-by-2030 target is estimated to require a ~50% uplift in the certified installer workforce. A copilot that raises first-visit fix rate multiplies the output of installers Chleo's company already has access to, instead of requiring headcount it can't hire.
2. **A real target-vs-actual gap, not just a cost problem.** Germany's political target is 500,000 heat pumps/year from 2024; actual 2024 sales were only ~193,000 (down 46%), with BWP forecasting a recovery to ~257,000 in 2025 — still far short of target. The gap is capacity-driven, not demand-driven: if order volume ever does catch up to the target, callback rates and customer complaints would spike right when the company most needs a clean reputation with new subsidy-driven buyers.
3. **A well-documented, general technical root cause to point to.** Inverter heat pumps' reliance on proprietary, non-interoperable communication protocols (BACnet/Modbus/LonTalk) is a known industry-wide pattern, not a one-off bug — which makes "hardware vs. connectivity" classification a durable problem worth solving rather than a symptom of one bad product cycle.
4. **A real, documented gap in the market:** no public dataset or widely-known tool cleanly separates "hardware fault" from "connectivity/app/pairing issue" for heat pumps. Community reports (e.g. Octopus Energy / aroTHERM users) confirm homeowners and installers already struggle with exactly this distinction — validating the problem is real, not hypothetical, and that a small manufacturer-built dataset filling this gap is a genuine (if modest) asset.
5. **Regulation is adding connectivity surface area, not removing it.** The 2025 mandatory smart-meter-gateway connection for subsidized units means *more* pairing/network failure modes are coming. A connectivity-vs-hardware triage tool becomes more relevant over time, not less.
6. **Transparency-friendly framing for Chleo.** A dashboard that shows *where* support cost is going (hardware vs. connectivity vs. installer error) gives a non-technical CEO a plain-language lens on whether to invest in hardware QA, app/firmware fixes, or installer training — rather than an opaque "AI decided" black box.
7. **A coherent Round 2 roadmap, not just one tool.** The two non-selected candidates in [[use_cases]] sequence naturally after the flagship: the commissioning-completeness checker (confirming refrigerant charge, HEMS pairing, and firmware steps before sign-off) attacks the same root cause preventively, and the COP-drop predictive-maintenance copilot attacks it before a fault is even reported — and the latter can already lean on the real German COP baseline in [data/when2heat_DE_subset.csv](../data/when2heat_DE_subset.csv) rather than starting from zero.

## Risks

1. **Safety adjacency.** Field commissioning touches refrigerant and electrical work. Even advisory guidance that's wrong or ambiguous near this territory carries real consequences, not just a bad user experience.
2. **AI Act boundary risk.** The copilot is designed to sit in the "limited risk" tier (advisory, human-in-the-loop, transparency-only obligations). If a future version were positioned as making or gating safety decisions autonomously, it could tip into the high-risk tier and its heavier obligations (risk-management system, conformity assessment).
3. **Refrigerant transition will age the fault taxonomy.** EU F-Gas rules phase out high-GWP refrigerants in small monobloc units from 2027, with natural-refrigerant-only subsidy eligibility from 2028. The hardware/refrigerant mix in the field — and therefore fault codes and fixes — will keep shifting during exactly the window this project targets.
4. **No public dataset directly answers the core question.** Confirmed by dataset search: available public data covers general heat-pump COP/fault simulation or generic industrial predictive maintenance, not a hardware-vs-connectivity fix mapping. Round 1's classification logic will lean on a small, self-authored synthetic dataset — a real limitation to disclose, not a solved problem.
5. **GDPR exposure grows with scope.** Round 1 uses only public/synthetic data. Any Round 2 move to real installer tickets or homeowner support conversations introduces personal-data handling that isn't in scope here.
6. **Policy dependency in the market itself.** The 2025 rebound this pitch leans on on the demand side is a forecast, not a fact — it assumes continued subsidy availability and clearer municipal heat planning. The 2024 sales collapse (46% down, badly missing the 500k/year political target) shows how quickly that can go the other way; the pitch should lean on the installer-capacity story, which holds regardless of exactly how fast demand recovers, rather than on the recovery forecast itself.

## Mitigations

1. Frame the copilot explicitly as **decision-support with a human installer in the loop** — never as issuing unsupervised electrical/refrigerant instructions — in the pitch, the workflow docs, and the dashboard story.
2. Keep the AI Act framing (limited-risk, transparency-only) as an explicit, stated assumption in the docs, and flag confirming it formally (or budgeting for high-risk obligations) as Round 2 scope if the use case is kept.
3. Design the fault-code taxonomy to be **modular/data-driven** (a lookup table, not hardcoded logic) so refrigerant-transition-driven updates are a content change, not a rebuild.
4. State the synthetic-dataset limitation openly in `dashboard_documentation.md` and `n8n/workflow_documentation.md` rather than presenting Round 1 coverage as production-grade.
5. Keep GDPR/compliance depth as explicit Round 2 scope (already reflected in [cost_estimation/cost_analysis.md](../cost_estimation/cost_analysis.md) assumption #9).
6. Name the subsidy/policy dependency as a stated assumption in the pitch itself, so the ask (a scoped pilot) doesn't overreach what current market conditions actually support.
