# Use Cases

> Industry/sector: Home Energy & HVAC (Heat Pumps + HEMS app layer)
> Company size: Small–medium heat pump manufacturer, German market
> See [[sector_research]] and [[opportunities_risks]] for the research this is built on.

## Candidate use cases considered

Three candidates were compared, deliberately spanning **three different points in the service lifecycle** — reactive (after a fault is reported), preventive (before sign-off), and predictive (before anyone reports anything) — rather than three variations on the same idea:

### 1. Field Commissioning & API/HEMS Connectivity Copilot — **selected** (reactive)
An installer enters a fault code or symptom after something has already gone wrong. The copilot classifies it as a **hardware fault**, a **HEMS connectivity/pairing/app issue**, or an **installer/commissioning error**, and returns fix guidance or an escalation route.
- **Target user:** the manufacturer's own and partner SHK field installers.
- **Expected value:** fewer senior-technician escalations, fewer misdiagnosed "false hardware faults" (the costliest error — an unneeded parts dispatch), faster first-visit resolution.

### 2. Commissioning-Completeness Checker (preventive)
Confirms that required commissioning steps (refrigerant charge, HEMS pairing, firmware version) were actually completed before an installer signs off a job — catching the problem before it ever becomes a fault ticket.
- **Target user:** installers, at the point of job completion.
- **Why not selected for Round 1:** it attacks the same root cause as the flagship (rushed commissioning — see [[sector_research]]) but at a different, earlier moment in the workflow, and would need its own checklist data model and n8n flow to demo credibly. Flagged as a strong, cheap-to-scope **Round 2 companion** once the flagship's fault taxonomy exists.

### 3. COP-Drop Predictive Maintenance Early-Warning Copilot (predictive)
Uses heat pump performance data (coefficient-of-performance trends) to flag a unit that's likely to fail *before* anyone calls it in — the earliest possible intervention point.
- **Target user:** the support/service planning team, not the installer or homeowner directly.
- **Why not selected for Round 1:** needs a live or streaming telemetry feed from installed units to be a credible dashboard/POC story, which Round 1's public/synthetic-data constraint can't realistically support — Chleo's company has no real installed-base telemetry yet. That said, the German COP baseline already sitting in [data/when2heat_DE_subset.csv](../data/when2heat_DE_subset.csv) (see [data/dataset_documentation.md](../data/dataset_documentation.md)) is exactly the kind of seasonal-COP ground truth this use case would need to define "abnormal" drop thresholds — making it a natural, partly-de-risked **Round 2 extension** once the flagship is live and generating its own ticket data.

*(An earlier draft also considered a homeowner-facing B2C connectivity chatbot. It was dropped rather than kept as a third candidate: it re-uses the flagship's classification logic without adding a new capability, and a customer-facing conversational tool is the hardest of all the options to responsibly demo under Round 1's public/synthetic-data-only constraint — it would need real complaint transcripts to be credible.)*

## Selected use case

**Heat Pump Field Commissioning & API/HEMS Connectivity Copilot** — matching the single Round 1 POC scoped in [cost_estimation/cost_analysis.md](../cost_estimation/cost_analysis.md) and [cost_estimation/timeline_estimate.md](../cost_estimation/timeline_estimate.md): *fault code + symptom → hardware-vs-connectivity classification → fix guidance or escalation*.

An installer at a job site enters a fault code or short symptom description. The copilot classifies whether the underlying issue is most likely a **hardware fault**, a **HEMS connectivity/pairing/app issue**, or an **installer/commissioning error**, and returns either concrete next-step fix guidance or a clear escalation route — always as advisory support for the installer, not an autonomous instruction to act.

## Why this use case was chosen

- **Wins the lifecycle comparison for Round 1 specifically**: of the three postures (reactive/preventive/predictive), reactive is the only one buildable end-to-end on public + self-authored synthetic data alone — the preventive checker needs a checklist data model not yet built, and the predictive candidate needs real installed-base telemetry Chleo's company doesn't have yet. It's the most de-risked starting point, not just the most obvious one.
- **Matches the sharpest structural constraint in the sector research** — the installer shortage (~50% workforce uplift needed by Germany's 2030 target, ~12k trained/yr vs ~35k/yr needed overall). A tool that improves first-visit fix rate and reduces senior-technician escalations multiplies the value of installers the company already has, rather than depending on hiring more of them.
- **Grounded in a documented real-world pain point**, not a hypothetical one: community reports around Octopus Energy / Vaillant aroTHERM installs show homeowners and installers already struggling to tell "is this the unit or the HEMS connectivity" apart, and the wider HVAC literature confirms proprietary inverter communication protocols as a real, general cause of exactly this ambiguity (see [[sector_research]]).
- **Stays in the EU AI Act's limited-risk tier** by design — advisory, human-in-the-loop, transparency obligation only — which keeps Round 1 scope honest about what it is and isn't (see [[opportunities_risks]] for the boundary risk if that changes).
- **Why an LLM, not a fixed rule engine:** the input side of this problem is messy, free-text field language — installer complaints and fault descriptions with no fixed schema, inconsistent phrasing, and mixed vocabulary between "the unit," "the app," and "the HEMS." That's precisely the kind of unstructured natural-language understanding where an LLM outperforms a rule-based classifier.
- **Already the backbone of the cost/timeline work**: the 4 dashboard metrics and n8n workflow scoped in [cost_estimation/cost_analysis.md](../cost_estimation/cost_analysis.md) and [cost_estimation/timeline_estimate.md](../cost_estimation/timeline_estimate.md) — first-visit fix rate, commissioning time, connectivity-failure rate by model/firmware, false-hardware-fault rate — are written for exactly this use case, so research, dashboard, and POC tell one coherent story instead of three disconnected pieces.
- **The other two candidates aren't discarded, they're sequenced**: the checker (preventive) and COP-drop copilot (predictive) are natural, named Round 2 extensions that build on data the flagship itself generates — a coherent product roadmap, not three unrelated ideas.
