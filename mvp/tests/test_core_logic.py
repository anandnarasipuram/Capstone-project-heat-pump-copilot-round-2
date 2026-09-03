"""Offline unit tests for the pure-logic core modules — no API keys, no
network calls needed. Mirrors Round 1's testing philosophy for the n8n
Code nodes (see poc/poc_documentation.md's "Worked examples" section):
verify the deterministic parsing/scoring logic directly, and state
plainly that the LLM/RAG path (core/llm.py, core/rag.py) needs live
OpenAI + Pinecone keys to verify end-to-end — that part is confirmed by
running the app itself, not by this file.

Run with: python -m pytest mvp/tests/ -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import checklist, fault_lookup, fleet, predictive  # noqa: E402


# ---------------------------------------------------------------------------
# fault_lookup
# ---------------------------------------------------------------------------

def test_extract_fault_code_synthetic():
    assert fault_lookup.extract_fault_code("Low refrigerant pressure alarm, error code E4") == "E4"


def test_extract_fault_code_vaillant_variants_normalize():
    assert fault_lookup.extract_fault_code("Fault code F532 showing, low flow rate") == "F.532"
    assert fault_lookup.extract_fault_code("controller shows F.532") == "F.532"
    assert fault_lookup.extract_fault_code("display reads F9998") == "F.9998"


def test_extract_fault_code_none_found():
    assert fault_lookup.extract_fault_code("Smart meter gateway will not pair with the control unit") == ""


def test_lookup_known_hardware_code():
    result = fault_lookup.lookup_fault_code("E4")
    assert result["category"] == "hardware_fault"


def test_lookup_unknown_code_returns_none():
    assert fault_lookup.lookup_fault_code("Z999") is None


def test_try_deterministic_classify_matches_poc_worked_example():
    # Same input as poc/poc_documentation.md's first worked example.
    out = fault_lookup.try_deterministic_classify("Low refrigerant pressure alarm, error code E4")
    assert out is not None
    assert out["category"] == "hardware_fault"
    assert out["source"] == "lookup"
    assert out["confidence"] == 1.0
    assert "E4" in out["reasoning"]
    assert out["manual_excerpts"] == []


def test_try_deterministic_classify_installer_error_f532():
    out = fault_lookup.try_deterministic_classify("Fault code F532 showing, low flow rate")
    assert out["category"] == "installer_error"
    assert "Vaillant" in out["manual_sources"][0]


def test_try_deterministic_classify_falls_through_on_no_code():
    assert fault_lookup.try_deterministic_classify("Smart meter gateway will not pair") is None


# ---------------------------------------------------------------------------
# checklist
# ---------------------------------------------------------------------------

def test_checklist_all_confirmed_is_sign_off_ready():
    responses = {item["key"]: True for item in checklist.CHECKLIST_ITEMS}
    result = checklist.evaluate_checklist(responses)
    assert result["completeness_pct"] == 100.0
    assert result["sign_off_ready"] is True
    assert result["missing_required"] == []


def test_checklist_missing_required_blocks_sign_off():
    responses = {item["key"]: True for item in checklist.CHECKLIST_ITEMS}
    responses["ebus_wiring_checked"] = False
    result = checklist.evaluate_checklist(responses)
    assert result["sign_off_ready"] is False
    assert len(result["missing_required"]) == 1
    assert result["missing_required"][0]["key"] == "ebus_wiring_checked"


def test_checklist_missing_optional_only_still_sign_off_ready():
    responses = {item["key"]: True for item in checklist.CHECKLIST_ITEMS}
    responses["firmware_up_to_date"] = False
    result = checklist.evaluate_checklist(responses)
    assert result["sign_off_ready"] is True
    assert len(result["missing_optional"]) == 1


def test_checklist_empty_responses_treated_as_unconfirmed():
    result = checklist.evaluate_checklist({})
    assert result["completeness_pct"] == 0.0
    assert result["sign_off_ready"] is False


# ---------------------------------------------------------------------------
# predictive
# ---------------------------------------------------------------------------

def test_predictive_normal_reading():
    result = predictive.evaluate_reading(expected_cop=3.0, observed_cop=2.9)
    assert result["severity"] == "normal"


def test_predictive_watch_reading():
    result = predictive.evaluate_reading(expected_cop=3.0, observed_cop=2.6)  # -13.3%
    assert result["severity"] == "watch"


def test_predictive_early_warning_reading():
    result = predictive.evaluate_reading(expected_cop=3.0, observed_cop=2.2)  # -26.7%
    assert result["severity"] == "early_warning"


def test_predictive_rejects_nonpositive_baseline():
    import pytest

    with pytest.raises(ValueError):
        predictive.evaluate_reading(expected_cop=0, observed_cop=1.0)


# ---------------------------------------------------------------------------
# fleet (offline — a tiny fixture baseline, no CSV needed)
# ---------------------------------------------------------------------------

def _fixture_baseline():
    import pandas as pd

    df = pd.DataFrame({"DE_COP_ASHP_floor": [3.0]}, index=[1])
    df.index.name = "month"
    return df


def _fixture_fleet(deviations):
    import pandas as pd

    return pd.DataFrame(
        [
            {
                "unit_id": f"U{i}",
                "model": "TF-12",
                "profile": "DE_COP_ASHP_floor",
                "region": "Bayern",
                "month": 1,
                "install_date": "2023-01-01",
                "target_deviation_pct": dev,
                "notes": "test",
            }
            for i, dev in enumerate(deviations)
        ]
    )


def test_evaluate_fleet_computes_severity_from_target_deviation():
    result = fleet.evaluate_fleet(_fixture_fleet([5, 15, 25]), _fixture_baseline())
    assert list(result["severity"]) == ["normal", "watch", "early_warning"]


def test_evaluate_fleet_expected_cop_matches_baseline():
    result = fleet.evaluate_fleet(_fixture_fleet([0]), _fixture_baseline())
    assert result.iloc[0]["expected_cop"] == 3.0
    assert result.iloc[0]["observed_cop"] == 3.0


def test_fleet_summary_counts_all_keys_present_even_if_zero():
    result = fleet.evaluate_fleet(_fixture_fleet([5, 5, 5]), _fixture_baseline())
    counts = fleet.fleet_summary_counts(result)
    assert counts == {"normal": 3, "watch": 0, "early_warning": 0}


def test_fleet_summary_counts_mixed():
    result = fleet.evaluate_fleet(_fixture_fleet([5, 15, 25, 30, 8]), _fixture_baseline())
    counts = fleet.fleet_summary_counts(result)
    assert counts == {"normal": 2, "watch": 1, "early_warning": 2}
