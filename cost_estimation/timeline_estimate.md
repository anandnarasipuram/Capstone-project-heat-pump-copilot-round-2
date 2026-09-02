# Timeline Estimate

**Project:** Heat Pump Field Commissioning & API Connectivity Copilot
**Scope of this estimate:** Round 1 deliverables only — research through POC/dashboard/monitoring, ending at the staff presentation. Figures use the same 1-consultant, part-time-equivalent assumption as [cost_analysis.md](cost_analysis.md).

## Milestones

- [x] Sector + company-size scenario locked (Home Energy/HVAC, small–medium manufacturer, German market)
- [x] Sector research, opportunity/risk mapping, and use case shortlist complete
- [x] Fault-code → cause → fix dataset drafted (public sources + synthetic gap-filling)
- [x] n8n POC workflow built (structurally validated; end-to-end run against a live n8n instance still pending — see n8n/workflow_documentation.md)
- [x] LangSmith monitoring sample complete and verified — 5/5 classifications correct, real dataset + experiment link in langsmith/monitoring_notes.md
- [x] Dashboard built with 5–7 stakeholder metrics + documentation (Tableau, agreed alternative to PowerBI)
- [x] Cost/timeline estimate finalized
- [ ] Round 1 presentation delivered to teaching staff; feedback captured; keep/change decision recorded

## Estimated schedule

| Phase | Duration | Notes |
|---|---|---|
| 1. Discovery & scenario lock | 1 day | Sector + company size chosen; scenario grounded in the Octopus Energy/aroTHERM connectivity discussion. |
| 2. Research pack (sector research, opportunities/risks, use case shortlist) | 2–3 days | Public data gathering (Kaggle heat pump COP / predictive maintenance sets); document the "no public dataset maps hardware-vs-connectivity directly" gap explicitly. |
| 3. Dataset authoring | 2–3 days | Self-authored fault-code → cause → fix-category dataset; can run partly in parallel with Phase 2. |
| 4. n8n POC build | 3–4 days | Symptom/fault-code intake → hardware-vs-connectivity classification → fix guidance or escalation. Depends on Phase 3 dataset being usable. |
| 5. LangSmith monitoring setup | 1–2 days | Trace a handful of POC runs; write up what's observable (why a classification/fix was chosen). Depends on Phase 4. |
| 6. PowerBI dashboard build | 2–3 days | Metrics: first-visit fix rate, commissioning time, connectivity-failure rate by model/firmware, false-hardware-fault rate. Can start once research pack metrics are known (Phase 2). |
| 7. Cost/timeline estimate + docs pass | 1–2 days | This document + cost_analysis.md, README, workflow docs. |
| 8. Presentation prep & staff presentation | 1–2 days | Slides, rehearsal, live presentation, feedback capture. |
| **Total (sequential-equivalent effort)** | **~13–20 consultant-days** | Matches the ~19-day build estimate in cost_analysis.md; elapsed calendar time is shorter where phases run in parallel (see below). |

## Suggested calendar mapping (Week 8 Day 3 → Week 9, per the capstone brief)

| Week | Focus |
|---|---|
| Week 8, Day 3–5 | Phases 1–3: scenario lock, research pack, dataset authoring |
| Week 9, Day 1–2 | Phases 4–5: n8n POC + LangSmith monitoring |
| Week 9, Day 3 | Phase 6: PowerBI dashboard |
| Week 9, Day 4 | Phase 7: cost/timeline + documentation pass |
| Week 9, Day 5 | Phase 8: presentation to teaching staff, feedback, keep/change decision |

## Dependencies / risks to schedule

| Risk | Impact | Mitigation |
|---|---|---|
| No public dataset directly maps "hardware fault vs. connectivity issue" | Dataset authoring (Phase 3) could run long if done rigorously | Time-box to a small, clearly-labeled synthetic dataset and document the gap as a stated assumption/limitation, rather than trying to source it publicly. |
| PowerBI dashboard depends on research-pack metrics being defined first | Slippage in Phase 2 delays Phase 6 | Draft the 5–7 target metrics early (even before research is 100% done) so dashboard build can start in parallel. |
| n8n POC and LangSmith setup are sequential (monitoring traces the POC's runs) | A delayed POC pushes out monitoring setup | Keep POC scope to one workflow (intake → classify → route) so Phase 4 doesn't expand into a multi-workflow build. |
| Guidance touches near-safety-critical territory (refrigerant/electrical commissioning steps) | Scope creep if reviewers push for stronger safety guardrails during Round 1 | Explicitly frame the copilot as human-in-the-loop decision support in the presentation, and defer deeper safety/compliance work to Round 2 (EU AI Act / GDPR docs). |
| Solo-consultant delivery model | Any single-phase delay pushes the whole chain (no parallel headcount) | Built-in buffer of ~1 day already reflected in the day ranges above; presentation date is fixed, so cut dashboard polish before cutting the POC if time runs short. |
