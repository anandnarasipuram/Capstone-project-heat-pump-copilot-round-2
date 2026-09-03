"""Deterministic fault-code extraction + lookup.

Ported 1:1 from the Round 1 n8n POC's "Parse Installer Message" and
"Lookup Known Fault Code" Code nodes (see ../../poc/poc_workflow.json and
../../poc/poc_documentation.md) so the MVP and the POC agree on every
fault code that skips the LLM entirely — fast, free, and fully auditable.

Two sources feed KNOWN_CODES:
  1. The 5 synthetic codes mirroring data/synthetic_fault_dataset.csv
  2. 8 real Vaillant aroTHERM fault codes, paraphrased from
     data/manuals/fault_code_knowledge_base.json (see that file for
     sources/copyright notes).
"""
from __future__ import annotations

import re
from typing import Optional, TypedDict

from .tracing import traceable

FAULT_CODE_PATTERN = re.compile(r"\b(E\d{1,2}|CONN-\d{2}|F\.?\d{2,4})\b", re.IGNORECASE)


class FaultLookupResult(TypedDict):
    category: str
    fix_or_escalation_action: str
    source: str


KNOWN_CODES: dict[str, FaultLookupResult] = {
    "E4": {
        "category": "hardware_fault",
        "fix_or_escalation_action": "Escalate to hardware service technician (compressor/refrigerant circuit inspection). Not resolvable by app/firmware update.",
        "source": "synthetic fault dataset",
    },
    "E7": {
        "category": "hardware_fault",
        "fix_or_escalation_action": "Escalate to hardware service technician (compressor/refrigerant circuit inspection). Not resolvable by app/firmware update.",
        "source": "synthetic fault dataset",
    },
    "E12": {
        "category": "hardware_fault",
        "fix_or_escalation_action": "Escalate to hardware service technician (compressor/refrigerant circuit inspection). Not resolvable by app/firmware update.",
        "source": "synthetic fault dataset",
    },
    "E2": {
        "category": "installer_error",
        "fix_or_escalation_action": "Correct commissioning step per install checklist (wiring, pressure fill, sensor orientation, or valve position); no manufacturer escalation needed.",
        "source": "synthetic fault dataset",
    },
    "CONN-01": {
        "category": "connectivity_issue",
        "fix_or_escalation_action": "Re-pair the control unit via the installer app, confirm router 2.4GHz band is enabled, and check smart-meter-gateway certificate status. No hardware visit required.",
        "source": "synthetic fault dataset",
    },
    # Real manufacturer fault codes — see data/manuals/fault_code_knowledge_base.json
    "F.22": {
        "category": "installer_error",
        "fix_or_escalation_action": "Check system water pressure at the filling loop; if below roughly 1 bar, top up to 1-1.5 bar. If pressure is already normal and the fault persists, escalate — likely a sensor fault.",
        "source": "Vaillant aroTHERM fault code reference",
    },
    "F.42": {
        "category": "hardware_fault",
        "fix_or_escalation_action": "Escalate to a certified technician — documented as a component-level fault inside the unit, not installer- or app-side.",
        "source": "Vaillant aroTHERM fault code reference",
    },
    "F.514": {
        "category": "hardware_fault",
        "fix_or_escalation_action": "Escalate to a certified technician — documented as a compressor inlet temperature sensor fault requiring internal inspection.",
        "source": "Vaillant aroTHERM fault code reference",
    },
    "F.532": {
        "category": "installer_error",
        "fix_or_escalation_action": "Check the building circuit for blockage, trapped air, or incorrect balancing before escalating — documented as usually an installation/flow issue, not a broken unit.",
        "source": "Vaillant aroTHERM fault code reference",
    },
    "F.718": {
        "category": "hardware_fault",
        "fix_or_escalation_action": "Escalate to a certified technician — documented as a blocked or faulty fan requiring hardware inspection.",
        "source": "Vaillant aroTHERM fault code reference",
    },
    "F.752": {
        "category": "installer_error",
        "fix_or_escalation_action": "Check incoming mains voltage, phase order, and earthing before escalating — documented as usually an electrical-supply issue at the installation, not a broken inverter.",
        "source": "Vaillant aroTHERM fault code reference",
    },
    "F.788": {
        "category": "installer_error",
        "fix_or_escalation_action": "Check the building circuit for air or restricted flow before escalating — documented as usually an installation-side pump/flow issue.",
        "source": "Vaillant aroTHERM fault code reference",
    },
    "F.9998": {
        "category": "installer_error",
        "fix_or_escalation_action": "Check eBUS wiring: correct cable type and polarity, no shielded/twisted cable, minimum clearance from power lines — documented as usually a wiring issue, not a broken controller.",
        "source": "Vaillant aroTHERM fault code reference",
    },
}


def extract_fault_code(text: str) -> str:
    """Pull a known-style fault code out of free text, normalized to the
    table's key form (F22 / F.22 / F9998 all normalize to 'F.NN')."""
    match = FAULT_CODE_PATTERN.search(text or "")
    if not match:
        return ""
    raw = match.group(1).upper()
    if re.match(r"^F\.?\d+$", raw):
        raw = "F." + re.sub(r"^F\.?", "", raw)
    return raw


def lookup_fault_code(code: str) -> Optional[FaultLookupResult]:
    """Exact-match lookup against the known-code table. Returns None for
    unrecognized/blank codes — the caller should fall through to RAG."""
    return KNOWN_CODES.get((code or "").strip().upper())


@traceable(name="deterministic_lookup", tags=["heat-pump-copilot", "path:lookup"])
def try_deterministic_classify(text: str) -> Optional[dict]:
    """Convenience: extract + lookup in one call. Returns a result dict
    shaped like the LLM path's output (category, message, confidence,
    source, manual_sources) so callers can treat both paths uniformly, or
    None if no known code was found."""
    code = extract_fault_code(text)
    if not code:
        return None
    result = lookup_fault_code(code)
    if not result:
        return None
    return {
        "category": result["category"],
        "message": result["fix_or_escalation_action"],
        "confidence": 1.0,
        "reasoning": f"Exact match on fault code '{code}' in the manufacturer fault-code table — resolved deterministically, no AI call needed.",
        "source": "lookup",
        "fault_code": code,
        "manual_sources": [result["source"]],
        "manual_excerpts": [],
    }
