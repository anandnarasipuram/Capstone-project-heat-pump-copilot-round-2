# Dashboard Documentation

> Tool: **Tableau** (agreed alternative to Power BI — Power BI Desktop is Windows-only and wasn't available on this build machine).
> File: [`dashboard.twbx`](dashboard.twbx) — a packaged Tableau workbook (data included, opens in Tableau Desktop/Public with no extra setup).

## Overview

The workbook has **two dashboards**, because it answers two different questions for two different moments in the pitch:

1. **"Preliminary Analysis"** — market/opportunity context: why this use case, why now. Built first, in Tableau, from EHPA/JRC market figures and the dataset-landscape comparison also captured in [research/preliminary_analysis.html](../research/preliminary_analysis.html).
2. **"Copilot Operations Metrics"** — the actual **stakeholder metrics dashboard** the brief asks for: what the Field Commissioning & Connectivity Copilot would show a CEO/ops lead once it's running, built from [data/synthetic_fault_dataset.csv](../data/synthetic_fault_dataset.csv).

Chleo (or any non-technical stakeholder) should read dashboard 1 as "why we're building this" and dashboard 2 as "what it would tell you day to day."

## Data sources

| Dashboard | Data source | Notes |
|---|---|---|
| Preliminary Analysis | `Data/.../copilot_dashboard_data.csv` (bundled in the workbook, embedded as a Tableau extract) | Long-format table of market stats, dataset-coverage comparison, opportunity/risk scores, and the 3-step build roadmap. Same content as `preliminary_analysis.html`. |
| Copilot Operations Metrics | `Data/.../copilot_ops_metrics.csv` (bundled, live CSV connection) | A Tableau-ready derivative of [data/synthetic_fault_dataset.csv](../data/synthetic_fault_dataset.csv): same 220 synthetic tickets, with boolean flags recoded as 0/1 and a `month` column added for time-series grouping. Regenerate via `node data/generate_synthetic_fault_dataset.js` + the Tableau-CSV conversion step noted in [data/dataset_documentation.md](../data/dataset_documentation.md) if the underlying dataset changes. |

## Pages / visuals

### Dashboard 1 — Preliminary Analysis (5 sheets)
- **Market Growth – Residential**: EU residential heat pump sales, 2024 vs 2025 (EHPA).
- **Market Growth – Air-Water**: air-water heat pump sales, 2015 vs 2024 (JRC) — the fastest-growing, most relevant category.
- **Dataset Coverage**: which public datasets cover hardware faults vs. connectivity telemetry vs. field/behavioral data — visualizing the gap this project's synthetic dataset fills.
- **Opportunity Risk Quadrant**: impact vs. containment scoring for 4 opportunities and 4 risks.
- **Roadmap Sequence**: the proposed 3-step build order (site readiness assistant → installer chatbot → fault triage copilot).

### Dashboard 2 — Copilot Operations Metrics (7 sheets — the required stakeholder metrics)

| # | Metric | What it shows | Value from the synthetic dataset |
|---|---|---|---|
| 1 | **First-Visit Fix Rate** | % of tickets resolved on the installer's first visit | 69.1% |
| 2 | **False-Hardware-Fault Rate** | % of tickets wrongly flagged as hardware (drives an unnecessary parts dispatch — the costliest error) | 10.9% |
| 3 | **Avg. Commissioning Time** | Average minutes on site per ticket | 82.0 min |
| 4 | **Connectivity-Failure Rate by Model** | Share of tickets that are connectivity issues, broken out by product model | TF-12 at 55.9% vs. 15.7–27.7% for the others — the firmware-3.0.0 rollout signal (see [data/dataset_documentation.md](../data/dataset_documentation.md)) |
| 5 | **Fault Category Mix Over Time** | Monthly ticket counts split by hardware / connectivity / installer-error, colored | Shows the connectivity-issue spike coinciding with the TF-12 firmware rollout |
| 6 | **Ticket Volume by Installer Type** | Count of tickets from the manufacturer's own installers vs. partner SHK installers | Context for #7 |
| 7 | **First-Visit Fix Rate by Installer Type** | Same fix-rate metric as #1, split by installer type | Flags whether partner installers need more support/training than in-house ones |

## Key metrics & definitions

- **First-visit fix rate** = tickets resolved without a second visit ÷ total tickets. Directly answers "is the copilot making installers more effective," the core value claim tied to the trades-shortage opportunity in [research/opportunities_risks.md](../research/opportunities_risks.md).
- **False-hardware-fault rate** = tickets the copilot (or installer) wrongly called a hardware fault ÷ total tickets. This is the costliest failure mode (an unneeded parts dispatch), so it's tracked separately from general accuracy.
- **Commissioning time** = minutes on site per ticket, a direct labor-cost proxy.
- **Connectivity-failure rate by model** = connectivity-category tickets ÷ total tickets, per product model — the metric that surfaces the TF-12/firmware-3.0.0 pattern as something worth investigating, rather than burying it in an aggregate.
- All rate metrics are computed as `AVG()` of a 0/1 indicator column in the data, displayed as a 0–100 number labeled "(%)" in each sheet title (kept as plain numbers rather than Tableau percentage-formatted fields, to keep the workbook's XML simple and robust).

## How to open / refresh

1. Open `dashboard.twbx` directly in Tableau Desktop or Tableau Public — it's a packaged workbook, so both CSVs and the market-data extract are bundled inside; no external file paths to fix.
2. The two dashboards are separate tabs at the bottom of the window: **Final Dashboard** (preliminary analysis) and **Copilot Operations Metrics**.
3. To refresh with new data, replace the CSV(s) under `Data/.../` inside the `.twbx` (or right-click the data source → **Data Source** → point it at an updated file) and hit **Refresh**.
4. To regenerate the operations-metrics CSV from scratch: `node data/generate_synthetic_fault_dataset.js > data/synthetic_fault_dataset.csv`, then re-run the Tableau-format conversion step described in [data/dataset_documentation.md](../data/dataset_documentation.md).

## A note on how this was built

The "Copilot Operations Metrics" dashboard's 7 sheets and its data connection were added by directly editing the Tableau workbook's XML (`.twb`) and repackaging it as a `.twbx`, rather than built by hand inside Tableau Desktop (not available on this machine). The XML is well-formed and mirrors the structure Tableau itself generated for the existing "Preliminary Analysis" sheets, but it hasn't been visually confirmed by opening it in real Tableau. **Please open `dashboard.twbx` in Tableau and check that all 7 new sheets render as expected** — if anything looks off, flag it and it can be adjusted from within Tableau directly (it's a normal, editable workbook at that point).
