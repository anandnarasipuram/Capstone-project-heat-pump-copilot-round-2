# Manual Knowledge Base

> Used by the n8n workflow's `Lookup Known Fault Code` and `Retrieve Manual Context` nodes — see [n8n/workflow_documentation.md](../../n8n/workflow_documentation.md) ("Manual grounding" section) for how these files are actually used in the pipeline.

## What's here

| File | Feeds | Contents |
|---|---|---|
| [fault_code_knowledge_base.json](fault_code_knowledge_base.json) | `Lookup Known Fault Code` (deterministic) | 8 real Vaillant aroTHERM fault codes (`F.22`, `F.42`, `F.514`, `F.532`, `F.718`, `F.752`, `F.788`, `F.9998`), each paraphrased into a cause summary, fix/escalation action, category, and escalation path. |
| [connectivity_status_guide.json](connectivity_status_guide.json) | `Retrieve Manual Context` (keyword retrieval) | 4 entries paraphrased from the Octopus Cosy Hub/Pod status-light guide (WiFi loss, sensor disconnection, low battery, genuine hub fault). |
| [safety_device_reference.json](safety_device_reference.json) | `Retrieve Manual Context` (keyword retrieval) | 4 entries paraphrased from the aroTHERM installation manual's safety-device/commissioning sections (eBUS wiring, flow rate, evaporator blockage, high-pressure cutout). |

## Sources

- **Vaillant aroTHERM fault codes** — paraphrased from Vaillant's published heat pump fault code documentation (see [vaillant.co.uk/service/heat-pump-fault-codes](https://www.vaillant.co.uk/service/heat-pump-fault-codes/) and the aroTHERM installation manual). Spot-checked against independent installer references during Round 1 to confirm accuracy before use — `F.22` (low system pressure), `F.42` (coding resistor fault), `F.532` (low building-circuit flow), `F.788` (pump/flow-related fault), and `F.9998` (eBUS communication fault) all matched documented behavior; `F.514`, `F.718`, and `F.752` follow the same manual's pattern but weren't independently cross-referenced beyond the primary source.
- **Octopus Cosy Hub/Pod status guide** — paraphrased from Octopus Energy's public heat pump support documentation ([octopus.energy/heat-pump-help](https://octopus.energy/heat-pump-help/)), which is what originally grounded this project's Round 1 research (see [research/sector_research.md](../../research/sector_research.md)).

## Scope and limitations — stated openly

- **This is representative UK documentation, not Chleo's own product manuals.** Chleo's company and product line are the assumed capstone scenario (see [research/opportunities_risks.md](../../research/opportunities_risks.md)); no real manufacturer supplied these documents. Real Vaillant/Octopus documentation stands in as credible, checkable content for a Round 1 demonstration of *how* manual grounding would work, not as Chleo's actual knowledge base.
- **Content is paraphrased into structured entries, not reproduced verbatim** — both to respect the source manuals' copyright and because structured (keyed/keyworded) entries are what the lookup and retrieval logic actually needs, not prose.
- **Small and hand-curated** (8 fault codes, 8 keyword-retrieval entries) — enough to demonstrate the pattern and ground the worked examples in [n8n/workflow_documentation.md](../../n8n/workflow_documentation.md), not a comprehensive fault-code database. A production build would ingest the manufacturer's full documentation set.
- **English-only keyword lists, with a handful of German synonyms bridged in by hand** — see the "Language" section in [n8n/workflow_documentation.md](../../n8n/workflow_documentation.md) for why this is a real, stated limitation and what the Round 2 fix looks like (multilingual embeddings instead of keyword matching).

## Copyright note

Vaillant and Octopus Energy trademarks, product names, and documentation belong to their respective owners. Content here is paraphrased for educational/demonstration use in a capstone project, not redistributed verbatim, and not presented as Vaillant's or Octopus's own published material.
