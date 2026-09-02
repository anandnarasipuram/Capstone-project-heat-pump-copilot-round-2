# Dataset Documentation

> Use case: Heat Pump Field Commissioning & API/App Connectivity Copilot (see [[../research/use_cases.md]])

Two datasets live in `data/`, matching the two things the use case needs: a **real, public** baseline for what "normal" heat pump performance looks like in Germany, and a **self-authored synthetic** dataset for the hardware-vs-connectivity-vs-installer-error fault classification that no public dataset covers (the gap documented in [research/opportunities_risks.md](../research/opportunities_risks.md)).

## 1. Public dataset — When2Heat Heating Profiles (Germany subset)

| | |
|---|---|
| **File** | `when2heat_DE_subset.csv` (11 MB, 131,484 hourly rows) |
| **Source** | Open Power System Data — [When2Heat Heating Profiles](https://data.open-power-system-data.org/when2heat/), package `2023-07-27` |
| **Original coverage** | Simulated hourly heat demand and heat pump COP for 28 European countries, 2008–2022 |
| **This subset** | Germany (`DE_*`) columns only, extracted from the 328 MB full package |
| **License** | Data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution required (see below). |
| **Citation** | Ruhnau, O., Hirth, L., Praktiknjo, A. (2019). *Time series of heat demand and heat pump efficiency for energy system modeling.* Scientific Data, 6, 189. https://doi.org/10.1038/s41597-019-0199-y — and Ruhnau, O., Muessel, J. (2023). *When2Heat Heating Profiles.* Open Power System Data. https://doi.org/10.25832/when2heat/2023-07-27 |

**Columns:** `utc_timestamp`, `cet_cest_timestamp`, `DE_COP_ASHP_floor`, `DE_COP_ASHP_radiator`, `DE_COP_ASHP_water`, `DE_COP_GSHP_floor`, `DE_COP_GSHP_radiator`, `DE_COP_GSHP_water`, `DE_heat_demand_space`, `DE_heat_demand_total`, `DE_heat_demand_water`. (ASHP = air-source heat pump, GSHP = ground-source; decimal separators normalized from the source's comma format to standard dots.)

**Why this dataset:** it is the only well-documented, openly-licensed, hourly, Germany-specific heat pump COP series we found (see the dataset search recorded in [research/sector_research.md](../research/sector_research.md)). It doesn't contain fault or connectivity data — no public dataset does — but it gives a **credible real-world baseline for seasonal COP behavior**, which grounds what counts as an "abnormal" COP drop when the synthetic fault dataset below defines hardware-fault scenarios, and can seed a "typical seasonal performance" chart on the dashboard for context.

**Note on the originally-planned dataset:** earlier project notes named **Kaggle "Heat Pump COP Drop – Synthetic Faults"** (`mathieuvallee/ai-dhc-heatpump-cop`) as the intended public dataset — a real, citable dataset from a peer-reviewed synthetic district-heating fault-generation study (Vallée et al., *Energy*, 2023). It could not be fetched in this environment: Kaggle's download API returns 404/requires an authenticated session even for public datasets, and no Kaggle credentials are configured here. When2Heat was used instead as a real, no-login, equally-relevant substitute (same domain — heat pump COP — just without the fault-injection angle). **If you have Kaggle access**, downloading `ai-dhc-heatpump-cop` and swapping/adding it here would better match the original plan and add genuine (simulated) fault-injection data alongside When2Heat's clean baseline.

**Limitation:** it's a national simulation, not per-unit telemetry from any real installed base (Chleo's or otherwise) — it's background/context data, not a substitute for the fault-classification dataset.

## 2. Self-authored synthetic dataset — field fault classification

| | |
|---|---|
| **File** | `synthetic_fault_dataset.csv` (220 rows) |
| **Source** | Self-authored for this project — no real customer, installer, or telemetry data was used, per the capstone brief's public/synthetic-data constraint (see assumption #8 in [cost_estimation/cost_analysis.md](../cost_estimation/cost_analysis.md)) |
| **Generator** | Deterministic, seeded script (Node.js, `mulberry32` PRNG, seed `42`) — fully reproducible, not hand-typed row by row |

**Columns:**

| Column | Meaning |
|---|---|
| `fault_id` | Synthetic ticket ID |
| `date` | Synthetic report date, spread over a 180-day window (2025-03-01 → 2025-08-28) |
| `model` | Fictional Chleo model code (`TF-08`, `TF-12`, `AS-10`, `AS-16`) |
| `firmware_version` | Fictional firmware version (`2.3.1` → `3.0.0`) |
| `installer_type` | `own_field_installer` or `partner_SHK` |
| `reported_symptom` | Free-text symptom as an installer would phrase it |
| `fault_code` | Structured fault code if one exists (connectivity issues typically show none) |
| `true_category` | Ground-truth label: `hardware_fault`, `connectivity_issue`, or `installer_error` |
| `predicted_category` | What a first-pass classifier would guess (used to simulate realistic misclassification, not a perfect oracle) |
| `correct_prediction` | Whether `predicted_category` matches `true_category` |
| `false_hardware_fault` | True when the fault was wrongly predicted as hardware (drives an unnecessary parts dispatch — the costliest error type) |
| `fix_or_escalation_action` | The guidance/escalation text for that fault archetype |
| `first_visit_fixed` | Whether the installer's first visit resolved the issue |
| `commissioning_time_minutes` | Simulated time on site |

**Built-in narrative (intentional, not noise):** the generator simulates a firmware rollout — model `TF-12` moving to firmware `3.0.0` partway through the window — that coincides with a spike in connectivity issues. This mirrors a realistic risk named in [research/opportunities_risks.md](../research/opportunities_risks.md) (the 2025 mandatory smart-meter-gateway connection adding new pairing failure modes) and gives the dashboard a concrete, investigable pattern instead of flat, uninformative distributions.

**Summary statistics (this run, n=220):**

| Metric | Value |
|---|---|
| Category split | hardware_fault 78 · connectivity_issue 72 · installer_error 70 |
| First-visit fix rate (overall) | 69.1% |
| False-hardware-fault rate (overall) | 10.9% |
| Avg. commissioning time | 82.0 minutes |
| Connectivity-failure rate — TF-12 | **55.9%** |
| Connectivity-failure rate — AS-10 | 27.7% |
| Connectivity-failure rate — TF-08 | 24.1% |
| Connectivity-failure rate — AS-16 | 15.7% |

These four rate/count metrics (first-visit fix rate, false-hardware-fault rate, commissioning time, connectivity-failure rate by model) are the ones scoped for the PowerBI dashboard in [dashboard/dashboard_documentation.md](../dashboard/dashboard_documentation.md) and feed the classification step of the n8n workflow in [n8n/workflow_documentation.md](../n8n/workflow_documentation.md).

**A stronger real-data option surfaced for Round 2:** [research/preliminary_analysis.html](../research/preliminary_analysis.html)'s dataset-landscape comparison flags the **NIST/Purdue Residential Heat Pump Fault Detection and Diagnosis Research Data** (public, [data.gov](https://catalog.data.gov/dataset/residential-heat-pump-fault-detection-and-diagnosis-research-data-10acc)) — real fault-injection measurements on two physical heat pump units, not synthetic. It covers hardware faults only (no connectivity telemetry, no field/behavioral data), so it can't replace this dataset on its own, but it's a credible candidate to blend in if the use case is kept into Round 2, replacing the synthetic `hardware_fault` rows with real measured ones while keeping the connectivity/installer-error categories self-authored.

**Limitations (stated openly, not glossed over):**
- This is synthetic data authored to be *plausible*, not measured from real field tickets — it demonstrates the shape of the use case, not validated real-world rates.
- The "true" vs. "predicted" category split is generated by the same script, i.e. the misclassification noise is designed-in, not learned from a real model — in Round 2, `predicted_category` would come from an actual classifier (rule-based or LLM-based) run against `reported_symptom`, and this dataset would instead serve as its evaluation/eval set.
- Model codes, firmware versions, and the rollout narrative are fictional, illustrative stand-ins for Chleo's product line, not real SKUs.

## Regenerating the synthetic dataset

`generate_synthetic_fault_dataset.js` in this folder is the generator — a ~100-line seeded Node.js script (no dependencies) that builds rows from a small set of fault "archetypes" (hardware / connectivity / installer-error), each with its own symptom phrasing pool, fix/escalation text, and first-visit-fix probability, plus the firmware-rollout bias described above. It's included so the dataset is fully reproducible and auditable, not a black box:

```bash
node data/generate_synthetic_fault_dataset.js > data/synthetic_fault_dataset.csv
```

The seed (`42`) is fixed in the script, so re-running it regenerates an identical CSV. Edit `N` (row count) or the `archetypes` array to extend it.
