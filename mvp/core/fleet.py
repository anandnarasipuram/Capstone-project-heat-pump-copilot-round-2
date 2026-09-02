"""Installed-fleet scoring for the 🏠 Installed Fleet Overview tab — a
portfolio view of the COP-Drop Predictive Early-Warning check
(core/predictive.py) across many units at once, instead of one unit at
a time. Built specifically so a non-technical audience can see all three
severity flags (🟢/🟡/🔴) side by side in one glance — see
../../data/installed_fleet_documentation.md for the demo dataset this
runs on and why it's deliberately curated, not a real fleet sample.

Pure logic (no I/O, no LLM calls) — data_loader.py loads the CSV,
core/llm.py optionally narrates the result; this module only scores it,
same separation as core/predictive.py and core/checklist.py.
"""
from __future__ import annotations

import pandas as pd

from . import predictive

SEVERITY_ORDER = ["normal", "watch", "early_warning"]


def evaluate_fleet(fleet_df: pd.DataFrame, baseline_df: pd.DataFrame) -> pd.DataFrame:
    """Returns a copy of fleet_df with expected_cop / observed_cop /
    deviation_pct / severity columns added. Each row's observed_cop is
    computed from its stated target_deviation_pct against the live
    baseline (not stored as a raw number), so this table can never drift
    out of sync with whatever the baseline dataset currently says."""
    rows = []
    for _, row in fleet_df.iterrows():
        expected = float(baseline_df.loc[row["month"], row["profile"]])
        observed = expected * (1 - row["target_deviation_pct"] / 100)
        result = predictive.evaluate_reading(expected_cop=expected, observed_cop=observed)
        rows.append({**row.to_dict(), **result})
    return pd.DataFrame(rows)


def fleet_summary_counts(evaluated_df: pd.DataFrame) -> dict:
    """{'normal': n, 'watch': n, 'early_warning': n} — always all three
    keys present (0 if none), so callers don't need defensive .get()s."""
    counts = evaluated_df["severity"].value_counts().to_dict()
    return {sev: counts.get(sev, 0) for sev in SEVERITY_ORDER}
