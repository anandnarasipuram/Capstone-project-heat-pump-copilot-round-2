"""Commissioning-Completeness Checker — the preventive use case from
research/use_cases.md ("Candidate #2, not selected as the Round 1
flagship but sequenced as a Round 2 companion"). Confirms the
commissioning steps most likely to later surface as a fault-code
misdiagnosis (see poc/poc_documentation.md's worked examples: F.22
low pressure, F.532/F.788 low flow, F.9998 eBUS wiring, F.752 electrical
supply) were actually completed before an installer signs a job off.

Pure logic, no network calls — unit-tested in tests/test_core_logic.py.
The natural-language sign-off summary (core/llm.py:summarize_checklist)
is the LLM layer on top of this deterministic evaluation.
"""
from __future__ import annotations

from typing import TypedDict

# Each item's `manual_ref` cites the fault code it would otherwise surface
# as later (ties the checker back to the flagship copilot's own knowledge base).
CHECKLIST_ITEMS = [
    {
        "key": "refrigerant_charge_confirmed",
        "label": "Refrigerant charge verified against nameplate spec",
        "manual_ref": None,
        "required": True,
    },
    {
        "key": "system_pressure_in_range",
        "label": "System water pressure filled to 1–1.5 bar",
        "manual_ref": "F.22 — low system pressure",
        "required": True,
    },
    {
        "key": "flow_rate_balanced",
        "label": "Building circuit flow rate checked for blockage/air/balancing",
        "manual_ref": "F.532 / F.788 — low building-circuit flow",
        "required": True,
    },
    {
        "key": "ebus_wiring_checked",
        "label": "eBUS wiring verified (cable type, polarity, clearance from power lines)",
        "manual_ref": "F.9998 — eBUS communication fault",
        "required": True,
    },
    {
        "key": "electrical_supply_checked",
        "label": "Incoming mains voltage, phase order, and earthing checked",
        "manual_ref": "F.752 — inverter/electrical-supply fault",
        "required": True,
    },
    {
        "key": "hems_gateway_paired",
        "label": "Smart-meter-gateway / HEMS pairing completed and confirmed online",
        "manual_ref": "connectivity_issue — HEMS pairing",
        "required": True,
    },
    {
        "key": "firmware_up_to_date",
        "label": "Firmware version confirmed current for this model",
        "manual_ref": None,
        "required": False,
    },
]


class ChecklistResult(TypedDict):
    completeness_pct: float
    missing_required: list[dict]
    missing_optional: list[dict]
    sign_off_ready: bool


def evaluate_checklist(responses: dict[str, bool]) -> ChecklistResult:
    """responses: {item_key: True/False} — items not present are treated
    as unconfirmed (False), never assumed complete."""
    required_items = [i for i in CHECKLIST_ITEMS if i["required"]]
    optional_items = [i for i in CHECKLIST_ITEMS if not i["required"]]

    missing_required = [i for i in required_items if not responses.get(i["key"], False)]
    missing_optional = [i for i in optional_items if not responses.get(i["key"], False)]

    total = len(CHECKLIST_ITEMS)
    confirmed = sum(1 for i in CHECKLIST_ITEMS if responses.get(i["key"], False))
    completeness_pct = round(100 * confirmed / total, 1) if total else 0.0

    return {
        "completeness_pct": completeness_pct,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "sign_off_ready": len(missing_required) == 0,
    }
