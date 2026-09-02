# Installed Fleet Demo Dataset

> File: [`synthetic_installed_fleet.csv`](synthetic_installed_fleet.csv) (18 rows) — feeds the MVP's **🏠 Installed Fleet Overview** tab, see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md).

## What this is — and isn't

This is a **small, hand-curated demo table**, not a statistical sample of a real installed base. It exists for one purpose: making the [COP-Drop Predictive Early-Warning](../research/use_cases.md) mechanism legible to a non-technical audience in one glance — a portfolio view across many units, instead of dragging one slider on one unit at a time. It is **not** real telemetry (Chleo's company has none yet — see [../research/use_cases.md](../research/use_cases.md)'s note on why the predictive candidate wasn't selected as the Round 1 flagship), not a statistically representative fleet, and not a forecast of what a real installed base's health distribution looks like.

## Columns

| Column | Meaning |
|---|---|
| `unit_id` | Synthetic unit identifier |
| `model` | Fictional Chleo model code, reused from [synthetic_fault_dataset.csv](synthetic_fault_dataset.csv) (`TF-08`, `TF-12`, `AS-10`, `AS-16`) for consistency across the demo |
| `profile` | Which [When2Heat](dataset_documentation.md) COP profile this unit's end-use matches (`DE_COP_ASHP_floor` / `_radiator` / `_water`) |
| `region` | Fictional German state, for realism only — not used in any calculation |
| `month` | Which month's seasonal baseline this unit's reading is compared against |
| `install_date` | Fictional install date, for realism only — not used in any calculation |
| `target_deviation_pct` | **The only column that drives the flag.** How far below the live baseline this unit's simulated reading sits. The app computes `observed_cop = expected_cop × (1 − target_deviation_pct/100)` **at runtime** against the real baseline (`core/fleet.py:evaluate_fleet`), rather than storing a raw COP number here — so the table can never drift out of sync with the baseline dataset it's compared against. |
| `notes` | Short human-readable flavor text for the demo table — not used in any calculation |

## Why these specific 18 rows

Deliberately constructed, not randomly sampled, to guarantee the demo shows all three severity flags every time — the whole point of this tab is letting someone see 🟢/🟡/🔴 side by side:

- **11 units at 0–8% deviation** → 🟢 `normal` (below `WATCH_THRESHOLD_PCT` in [../mvp/core/predictive.py](../mvp/core/predictive.py))
- **4 units at 12–17% deviation** → 🟡 `watch`
- **3 units at 24–32% deviation** → 🔴 `early_warning`

This ~61% / 22% / 17% split is a deliberately realistic-*looking* proportion for a demo (mostly healthy fleet, a genuine minority flagged) — not a claim about what Chleo's real fleet's distribution would be. The 10%/20% thresholds themselves are a stated assumption pending real fleet-outcome data — see [../roi_risk_assessment.md](../roi_risk_assessment.md) and [../mvp/core/predictive.py](../mvp/core/predictive.py)'s module docstring.

## Regenerating / extending it

There's no generator script for this one — 18 hand-picked rows with a documented rationale (above) is more transparent than a seeded random generator would be for a table whose whole purpose is a curated demo, not a statistical sample. To add more rows: pick a `model`/`profile`/`region`/`month` freely (`notes` and `install_date` are cosmetic), and choose `target_deviation_pct` to land in whichever bucket you want to demonstrate.
