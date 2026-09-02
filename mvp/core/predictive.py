"""COP-Drop Predictive Maintenance Early-Warning — the predictive use
case from research/use_cases.md ("Candidate #3, not selected as the
Round 1 flagship because it needs real installed-base telemetry Chleo's
company doesn't have yet — but the German COP baseline in
data/when2heat_DE_subset.csv is exactly the ground truth it needs to
define 'abnormal' thresholds").

Compares a single reported COP reading for a unit against the
When2Heat Germany seasonal baseline for the matching profile/month and
flags a deviation severity. Pure logic — the baseline itself is loaded
by core/data_loader.load_cop_baseline(); this module only compares
numbers, so it's unit-testable with a small fixture baseline instead of
the full 130k-row CSV.

Deviation thresholds are a stated, documented assumption (see
mvp_documentation.md and roi_risk_assessment.md's risk matrix — "no
public dataset gives ground-truth fault thresholds, only ground-truth
*normal* seasonal COP"), not a calibrated fault-detection model.
"""
from __future__ import annotations

from typing import TypedDict

# % below the seasonal baseline before we call it "watch" vs "early_warning".
# Chosen as a stated, round-number assumption pending real fleet data to
# calibrate against — see roi_risk_assessment.md.
WATCH_THRESHOLD_PCT = 10.0
EARLY_WARNING_THRESHOLD_PCT = 20.0


class PredictiveResult(TypedDict):
    expected_cop: float
    observed_cop: float
    deviation_pct: float
    severity: str  # "normal" | "watch" | "early_warning"


def evaluate_reading(expected_cop: float, observed_cop: float) -> PredictiveResult:
    if expected_cop <= 0:
        raise ValueError("expected_cop must be > 0 — check the baseline lookup")

    deviation_pct = round(100 * (expected_cop - observed_cop) / expected_cop, 1)

    if deviation_pct >= EARLY_WARNING_THRESHOLD_PCT:
        severity = "early_warning"
    elif deviation_pct >= WATCH_THRESHOLD_PCT:
        severity = "watch"
    else:
        severity = "normal"

    return {
        "expected_cop": round(expected_cop, 2),
        "observed_cop": round(observed_cop, 2),
        "deviation_pct": deviation_pct,
        "severity": severity,
    }


SEVERITY_LABELS = {
    "normal": "✅ Normal — within expected seasonal range",
    "watch": "🟡 Watch — below seasonal baseline, monitor next reading",
    "early_warning": "🔴 Early warning — schedule an inspection before a fault is reported",
}
