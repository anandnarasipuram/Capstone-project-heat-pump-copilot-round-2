# Quarterly Roadmap, Sprint Plan & Definition of Done — Heat Pump Copilot

> Prepared for IHK certification presentation. This is the sprint-level operational plan for [strategic_plan.md](strategic_plan.md)'s Phase 1 → Phase 2 transition — it doesn't invent a separate timeline: same dates, same exit-gate items, same pilot already committed to there. This document exists to show *how* that gets executed, two weeks at a time, not to re-argue *what* gets built.
> Team assumed: 1 AI consultant/developer (this project's build capacity, per [roi_risk_assessment.md](roi_risk_assessment.md)'s €650/day rate) + Chleo's Service Operations Lead as product-side stakeholder + an external DPO/privacy counsel engaged for Sprint 1–2's compliance review. A solo-plus-stakeholders team, not a multi-developer squad — sprint capacity below is scoped accordingly.

## 1. Quarterly roadmap — Q4 2026 (6 × two-week sprints)

| Sprint | Dates | Sprint goal | Maps to |
|---|---|---|---|
| **Sprint 1** | Oct 1–14, 2026 | Close the two build-side items on Phase 1's exit gate: ticket persistence, DPIA review kickoff | [strategic_plan.md](strategic_plan.md) Phase 1 exit gate |
| **Sprint 2** | Oct 15–28, 2026 | Close the two people-side items: DPIA sign-off, pilot cohort recruited + trained | Phase 1 exit gate (complete) → Phase 2 entry |
| **Sprint 3** | Oct 29–Nov 11, 2026 | Pilot go-live; first two weeks of real installer traffic | Phase 2 Pilot, weeks 1–2 |
| **Sprint 4** | Nov 12–25, 2026 | Pilot iteration — override-rate review, knowledge-base coverage gaps surfaced by real usage | Phase 2 Pilot, weeks 3–4 |
| **Sprint 5** | Nov 26–Dec 9, 2026 | Adoption push + the pilot's own week-8 KPI checkpoint | Phase 2 Pilot, weeks 5–6 (checkpoint at week 8 lands early Sprint 6) |
| **Sprint 6** | Dec 10–23, 2026 | Wind down data collection, assemble the week-12 greenlight package | Phase 2 Pilot, weeks 7–8; prep for the week-12 review in Jan 2027 |

**Honest scope note:** the pilot itself is a fixed 12-week window (Oct 2026–Jan 2027, already set in `strategic_plan.md`) — it doesn't finish inside this calendar quarter. This roadmap covers the quarter's 6 sprints; the pilot's actual greenlight decision (week 12, all 5 criteria in `strategic_plan.md`) lands in early January 2027, just after Sprint 6 closes. Sprint 6's deliverable is the *package* that review runs on, not the decision itself — stated plainly rather than claiming a finished pilot inside one quarter.

## 2. Sprint-by-sprint breakdown

### Sprint 1 (Oct 1–14) — Persistence + compliance kickoff
**Goal:** the two things nothing else in the roadmap can start without.
- Build the ticket-persistence layer (`mvp/mvp_documentation.md`'s stated gap — currently `st.session_state` only)
- Engage a DPO/privacy counsel and hand off the short DPIA (`compliance/gdpr_documentation.md`, Section 4) for formal review
- **Sprint deliverable:** persisted tickets keyed to job/unit ID; DPIA under external review

### Sprint 2 (Oct 15–28) — Sign-off + cohort
**Goal:** clear every remaining item on the Phase 1 exit gate.
- Incorporate DPO feedback, obtain written DPIA sign-off
- Recruit the 10–15 pilot installers (own + partner SHK mix, per `strategic_plan.md`)
- Build and deliver installer onboarding/training (the tool, the "confirm before acting" framing, the explicit no-performance-evaluation commitment from `eu_ai_act_compliance.md`)
- Confirm Pinecone EU region (or accept the documented gap) and LangSmith EU endpoint are both set correctly for pilot traffic
- **Sprint deliverable:** Phase 1 exit gate fully closed; pilot cohort trained and ready

### Sprint 3 (Oct 29–Nov 11) — Pilot go-live
**Goal:** real installers, real tickets, week 1–2 stability.
- Go-live announcement via the stakeholder communication plan (`strategic_plan.md`, Section 3)
- Daily trace spot-checks (LangSmith) for the first week — catching integration issues before they compound
- First LLM-as-judge batch run (`mvp/scripts/judge_traces.py`) against real pilot traffic
- **Sprint deliverable:** pilot live; first judged batch of real (not synthetic-demo) traces

### Sprint 4 (Nov 12–25) — Iterate on real usage
**Goal:** fix what real installers actually hit, not what the demo anticipated.
- Review override rate (installers disagreeing with/escalating past a suggestion) — the automation-bias KPI from `strategic_plan.md`
- Log and address manual-knowledge-base coverage gaps surfaced by real free-text symptoms
- Weekly KPI snapshot #1 to Chleo (first-visit fix rate, false-hardware-fault rate trend)
- **Sprint deliverable:** first real-usage KPI trend line; knowledge-base gap backlog

### Sprint 5 (Nov 26–Dec 9) — Adoption push
**Goal:** hit the ≥60%-of-cohort adoption bar the greenlight criteria require.
- Targeted follow-up with low-adoption installers (via the named partner-SHK champions)
- Weekly KPI snapshot #2
- Week-8 checkpoint data pulled and reviewed against the pilot KPI table
- **Sprint deliverable:** adoption trend visibly moving toward the ≥60% bar, or an explicit named reason why not

### Sprint 6 (Dec 10–23) — Package the greenlight review
**Goal:** everything the week-12 decision needs, ready before the quarter closes.
- Compile all 5 greenlight criteria's actual figures against target (first-visit-fix Δ, false-hardware-fault Δ, adoption %, compliance incident count, installer sentiment survey)
- Final LLM-as-judge batch run for the quarter, summarized
- Draft the greenlight recommendation (proceed / extend-and-adjust, per `strategic_plan.md`'s stated default response)
- **Sprint deliverable:** greenlight review package, ready for the week-12 decision meeting in Jan 2027

## 3. User stories with acceptance criteria

Grouped by epic, each tagged with its sprint. Written in standard `As a / I want / so that` form with checklist-style acceptance criteria — not prose, so each is independently verifiable.

### Epic A — Compliance & governance readiness (Sprint 1–2)

**US-01 — Ticket persistence**
*As a Service Operations Lead, I want fault-triage tickets persisted beyond the browser session, so that I can actually measure first-visit fix rate and false-hardware-fault rate on real pilot data.*
- [ ] Every `fault_triage_turn` result is written to a durable store (not `st.session_state`) keyed by a job/ticket ID
- [ ] Each record includes: timestamp, model (if selected), category, source (lookup/llm), confidence — no raw homeowner PII field in the schema
- [ ] A stored ticket survives an app restart
- [ ] Retention aligns with the 12-month window recommended in `compliance/gdpr_documentation.md`, Section 2

**US-02 — DPIA review**
*As a DPO/privacy counsel, I want the short DPIA formally reviewed before real installer data flows through the system, so that the pilot doesn't launch on an unreviewed compliance assessment.*
- [ ] DPIA (`compliance/gdpr_documentation.md`, Section 4) sent to a named reviewer
- [ ] Reviewer's written feedback addressed or explicitly logged as accepted residual risk
- [ ] Sign-off recorded with date and reviewer name in the repo (not just verbal)

**US-03 — Pilot cohort recruitment & training**
*As a pilot installer, I want onboarding that explains what this tool does and doesn't do, so that I trust it enough to actually use it.*
- [ ] 10–15 installers confirmed, explicit mix of own field installers and partner SHK
- [ ] Each completes a short onboarding session covering: how to use the tool, the "AI-suggested triage, confirm before acting" framing, and the explicit commitment that usage data is never used to evaluate them individually
- [ ] Each installer has working access (URL + any credentials) before Sprint 3 starts

### Epic B — Pilot launch operations (Sprint 3)

**US-04 — Go-live communication**
*As Chleo, I want a clear go-live announcement to all stakeholders, so that everyone knows the pilot has started and what's expected of them.*
- [ ] Announcement sent per the stakeholder communication plan (`strategic_plan.md`, Section 3) — installers, support/service planning team, DPO
- [ ] Includes a feedback channel for installers to report problems

**US-05 — Early trace monitoring**
*As the developer, I want to spot-check real traces daily during week 1, so that integration issues are caught before they compound across the full pilot.*
- [ ] At least one LangSmith trace review per day, first 5 business days
- [ ] Any `ai_generated: False` fallback (a live call failure) investigated same-day
- [ ] First LLM-as-judge run against real (non-demo) traces completed by end of Sprint 3

### Epic C — Pilot iteration (Sprint 4–5)

**US-06 — Override-rate review**
*As Chleo, I want to know how often installers disagree with the AI's suggestion, so that I can tell healthy skepticism apart from a tool that isn't trustworthy yet.*
- [ ] Override signal defined and captured (e.g. installer proceeds differently than suggested, or explicitly flags a bad answer)
- [ ] Weekly override rate reported alongside the KPI snapshot
- [ ] Any override rate >40% triggers a qualitative review, not just a number

**US-07 — Knowledge-base coverage gaps**
*As a field installer, I want the copilot grounded correctly even when my symptom doesn't match the existing manual excerpts, so that I get real guidance instead of an ungrounded generic answer.*
- [ ] Every `classify_symptom` run with empty `manual_sources` logged for review
- [ ] Weekly review of that log to identify real, recurring coverage gaps (not one-off phrasing)
- [ ] At least the top 3 recurring gaps addressed (new manual entries) by end of Sprint 5

**US-08 — Weekly KPI reporting**
*As Chleo, I want a weekly snapshot of the pilot's core metrics, so that I can track progress toward the greenlight criteria without waiting until week 12.*
- [ ] Weekly snapshot: first-visit fix rate, false-hardware-fault rate, adoption %, override rate
- [ ] Delivered every Friday during the pilot, starting Sprint 4
- [ ] Trend (not just point-in-time) visible from the second snapshot onward

**US-09 — Adoption follow-up**
*As a partner-installer champion, I want to know which installers in my group haven't adopted the tool yet, so that I can follow up directly rather than relying on a generic reminder.*
- [ ] Per-installer usage visible (ticket count in the persisted store, US-01)
- [ ] Installers below 50% of eligible tickets flagged by mid-Sprint 5
- [ ] Direct follow-up logged for each flagged installer

### Epic D — Greenlight decision readiness (Sprint 6)

**US-10 — Greenlight package**
*As Chleo, I want a single package showing where the pilot stands against all 5 greenlight criteria, so that the week-12 decision is based on evidence, not impressions.*
- [ ] All 5 criteria from `strategic_plan.md` reported with actual figure vs. target: first-visit-fix Δ (≥7pp), false-hardware-fault Δ (≥3pp), adoption (≥60% sustained), compliance incidents (0), installer sentiment (net-positive survey)
- [ ] A stated recommendation: proceed to Phase 3, or extend-and-adjust — never silently defaulting to either
- [ ] Package delivered before the week-12 review meeting

**US-11 — Final LLM-as-judge summary**
*As Chleo, I want to know how accurate and hallucination-free the AI's answers have actually been over the pilot, not just how often it was used, so that "it works" is a measured claim.*
- [ ] `judge_traces.py` run against the full quarter's real traces (paginated past the 100-run cap if needed — see the script's own noted limit)
- [ ] Average correctness and hallucination scores reported alongside the KPI snapshot
- [ ] Any run scoring hallucination > 0.3 individually reviewed, not just averaged away

## 4. Definition of Done

Applies to every user story above — not aspirational, this is the same bar already applied throughout this project's Round 2 build (offline tests + live verification + visual/trace confirmation, not just "looks right"):

- [ ] **Tests**: existing offline unit test suite still passes (`pytest tests/ -v`, currently 20/20) with zero API keys required to run it
- [ ] **New logic tested**: any new pure-logic behavior has at least one new offline test
- [ ] **Live-verified, not just written**: any change touching an LLM/embedding/Pinecone call is exercised at least once against real API keys, not just believed to work from reading the code — evidence (a run's output, a trace link) noted in the commit or doc
- [ ] **Traced**: any new AI call site is wired through `core/pipeline.py`'s tracing pattern, confirmed visible in LangSmith with the correct nested structure
- [ ] **Documented**: `mvp_documentation.md` (or the relevant compliance/strategic doc) updated in the same change, not left to go stale
- [ ] **No secrets committed**: `.env`/`.env`-equivalent files remain gitignored; verified via `git status --short --ignored` before commit
- [ ] **Fails soft**: any new failure mode has a defined, non-silent fallback — never a silent "no action needed" default (the standing project-wide safety rule, see `core/llm.py`'s module docstring)
- [ ] **UI changes visually confirmed**: a real screenshot (not just "should render fine"), zero browser console errors
- [ ] **Runs clean from scratch**: `streamlit run app.py` boots with no crash in a freshly created environment (`pip install -r requirements.txt` only, no leftover local state assumed)
- [ ] **Compliance-tagged stories only**: written sign-off from the named reviewer (DPO, Chleo) recorded with date — a verbal "looks fine" doesn't close the story
