"""Heat Pump Copilot — Round 2 MVP.

Single Streamlit app covering all three use-case candidates from
research/use_cases.md, sequenced in Round 1 as flagship + two Round 2
companions:

  1. 🩺 Fault Triage Copilot     — reactive, the flagship, chat-style RAG
  2. ✅ Commissioning Checker    — preventive
  3. 📉 COP-Drop Early-Warning   — predictive

Mode 1 is the core, end-to-end AI capability this MVP exists to prove:
fault-code lookup (deterministic, zero cost) → Pinecone RAG over the
manual knowledge base (real embeddings, the Round 2 upgrade from the
POC's keyword match) → OpenAI classification, grounded in whatever the
retrieval step found. See mvp_documentation.md for the full architecture,
what "runs" means with vs. without API keys, and how to reproduce.

Run: streamlit run app.py
"""
from __future__ import annotations

import calendar
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
load_dotenv()

from core import checklist, data_loader, fleet, llm, pipeline, predictive, rag, tracing  # noqa: E402

st.set_page_config(page_title="Heat Pump Copilot", page_icon="🔧", layout="wide")

CATEGORY_LABELS = {
    "hardware_fault": "Hardware fault",
    "connectivity_issue": "HEMS connectivity issue",
    "installer_error": "Installer/commissioning error",
}

# Chleo's fictional model lineup, reused from data/synthetic_fault_dataset.csv
# for consistency across the whole demo. See Mode 1's selector below and
# core/llm.py's module docstring for what this does (and doesn't) do.
MODEL_OPTIONS = ["Not specified", "TF-08", "TF-12", "AS-10", "AS-16"]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def cached_cop_baseline():
    return data_loader.load_cop_baseline()


@st.cache_data(show_spinner=False)
def cached_installed_fleet():
    return data_loader.load_installed_fleet()


def render_assistant_card(result: dict) -> None:
    category_label = CATEGORY_LABELS.get(result["category"], result["category"])
    emoji = "🔧" if result["category"] == "hardware_fault" else "✅"
    st.markdown(f"**{emoji} {category_label}**")
    st.write(result["message"])

    source_label = "fault-code lookup" if result["source"] == "lookup" else "AI classification"
    if result.get("manual_sources"):
        source_label += ", grounded in manufacturer manual"
    if result.get("retrieval_mode"):
        source_label += f" ({result['retrieval_mode']})"
    confidence = result.get("confidence")
    conf_str = f" · confidence {confidence}" if confidence is not None else ""
    st.caption(f"Source: {source_label}{conf_str}")
    if result.get("model") and result["model"] != "Not specified":
        st.caption(f"Model: {result['model']}")

    if result.get("manual_sources"):
        with st.expander("Manual citations"):
            for source in result["manual_sources"]:
                st.write("-", source)

    if result["source"] == "llm" and not result.get("ai_generated", True):
        st.warning(
            "⚠️ Live model call unavailable — showing a safe-default escalation instead of "
            "a real classification. Check OPENAI_API_KEY in mvp/.env."
        )

    st.caption("_AI-suggested triage — confirm before acting._")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("🔧 Heat Pump Copilot")
st.sidebar.caption("Field Commissioning & HEMS Connectivity Copilot")
mode = st.sidebar.radio(
    "Mode",
    [
        "🩺 Fault Triage Copilot",
        "✅ Commissioning Checker",
        "📉 COP-Drop Early-Warning",
        "🏠 Installed Fleet Overview",
    ],
)

st.sidebar.divider()
st.sidebar.caption(
    "⚠️ Advisory decision support only. Every response is AI-suggested triage for a "
    "human installer to confirm — never an autonomous instruction to act on electrical "
    "or refrigerant work."
)

# Technical status — collapsed by default so a client demo shows the
# product, not the vendor plumbing. Check this before a demo starts, not
# during it: expand once to confirm all 3 are green, then leave collapsed.
with st.sidebar.expander("⚙️ System status", expanded=False):
    st.markdown(f"{'🟢' if llm.is_configured() else '🔴'} AI classification")
    st.markdown(f"{'🟢' if rag.is_configured() else '🟡'} Knowledge-base search")
    st.markdown(f"{'🟢' if tracing.is_configured() else '🟡'} Interaction monitoring")
    if not llm.is_configured():
        st.caption("Add OPENAI_API_KEY in .env for live AI responses.")
    if not rag.is_configured():
        st.caption("Add PINECONE_API_KEY in .env for semantic search (falls back to keyword match otherwise).")
    if not tracing.is_configured():
        st.caption("Add LANGSMITH_API_KEY in .env to trace every interaction.")


# ---------------------------------------------------------------------------
# Mode 1 — Fault Triage Copilot (flagship, chat-style RAG)
# ---------------------------------------------------------------------------

if mode.startswith("🩺"):
    st.title("🩺 Fault Triage Copilot")
    st.caption(
        "An installer enters a fault code or symptom. The copilot classifies it as a "
        "hardware fault, a HEMS connectivity/pairing issue, or an installer/commissioning "
        "error, and returns fix guidance or an escalation route."
    )

    selected_model = st.selectbox(
        "Which unit is this?",
        MODEL_OPTIONS,
        help=(
            "Optional. Sharpens the AI's answer and lets Chleo's team see fault trends "
            "by model over time — it doesn't currently filter which fault codes are "
            "recognized, since today's manual knowledge base isn't split per model."
        ),
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                render_assistant_card(msg)

    prompt = st.chat_input("Describe the fault or paste a fault code, e.g. 'F532 low flow rate'…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Classifying…"):
                    result = pipeline.fault_triage_turn(prompt, model=selected_model)
            except Exception as exc:  # noqa: BLE001 — last-resort guard so the chat never hard-crashes
                st.error(f"Something went wrong processing that message: {exc}")
                result = {
                    "role": "assistant",
                    "category": "hardware_fault",
                    "message": "An internal error occurred — escalating to a senior technician as a safe default.",
                    "source": "llm",
                    "confidence": 0.0,
                    "manual_sources": [],
                    "ai_generated": False,
                    "model": selected_model,
                }
            result["role"] = "assistant"
            render_assistant_card(result)
        st.session_state.messages.append(result)

    with st.expander("Try a worked example"):
        st.markdown(
            "- `Low refrigerant pressure alarm, error code E4` — instant lookup, no API key needed\n"
            "- `Fault code F532 showing, low flow rate` — instant lookup, real Vaillant code\n"
            "- `No comms from the outdoor unit, controller not responding` — RAG/keyword-grounded LLM classification\n"
            "- `Smart meter gateway will not pair with the control unit` — LLM classification, no manual grounding"
        )


# ---------------------------------------------------------------------------
# Mode 2 — Commissioning-Completeness Checker (preventive)
# ---------------------------------------------------------------------------

elif mode.startswith("✅"):
    st.title("✅ Commissioning-Completeness Checker")
    st.caption(
        "Confirms required commissioning steps were actually completed before an installer "
        "signs off a job — catching the problem before it becomes a fault ticket. Each item "
        "cites the fault code it would otherwise surface as later."
    )

    with st.form("checklist_form"):
        col1, col2 = st.columns(2)
        model = col1.text_input("Model", value="TF-12")
        firmware = col2.text_input("Firmware version", value="3.0.0")

        responses = {}
        for item in checklist.CHECKLIST_ITEMS:
            help_text = f"Unconfirmed → risks surfacing as {item['manual_ref']}" if item["manual_ref"] else None
            label = item["label"] + ("" if item["required"] else " (optional)")
            responses[item["key"]] = st.checkbox(label, help=help_text)

        submitted = st.form_submit_button("Evaluate")

    if submitted:
        try:
            with st.spinner("Evaluating…"):
                turn = pipeline.commissioning_turn(model, firmware, responses)
            result, summary = turn["checklist"], turn["summary"]
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not evaluate this checklist: {exc}")
            result, summary = None, None

        if result:
            col1, col2 = st.columns(2)
            col1.metric("Completeness", f"{result['completeness_pct']}%")
            col2.metric("Sign-off ready", "Yes" if result["sign_off_ready"] else "No")

            if result["sign_off_ready"]:
                st.success("All required steps confirmed. Ready to sign off.")
            else:
                st.error(f"{len(result['missing_required'])} required step(s) outstanding:")
                for item in result["missing_required"]:
                    ref = f" — risks surfacing as **{item['manual_ref']}**" if item["manual_ref"] else ""
                    st.write(f"- {item['label']}{ref}")

        if summary:
            st.info(summary["summary"])
            if not summary["ai_generated"]:
                st.caption("⚠️ Deterministic summary (no live model response) — add OPENAI_API_KEY for an AI-generated one.")


# ---------------------------------------------------------------------------
# Mode 3 — COP-Drop Predictive Early-Warning
# ---------------------------------------------------------------------------

elif mode.startswith("📉"):
    st.title("📉 COP-Drop Predictive Early-Warning")
    st.caption(
        "Compares a reported coefficient-of-performance (COP) reading against the "
        "When2Heat Germany seasonal baseline to flag a unit likely to need attention "
        "before anyone reports a fault. See mvp_documentation.md for the threshold "
        "assumptions this uses."
    )

    try:
        baseline = cached_cop_baseline()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not load the COP baseline dataset: {exc}")
        st.stop()

    col1, col2, col3 = st.columns(3)
    profile = col1.selectbox(
        "Profile",
        options=list(data_loader.PROFILE_LABELS.keys()),
        format_func=lambda k: data_loader.PROFILE_LABELS[k],
    )
    month = col2.selectbox("Month", options=list(range(1, 13)), format_func=lambda m: calendar.month_name[m])
    observed = col3.number_input("Observed COP reading", min_value=0.1, max_value=10.0, value=2.5, step=0.1)

    st.line_chart(baseline[profile], height=220)
    st.caption(f"Seasonal baseline for {data_loader.PROFILE_LABELS[profile]} — When2Heat Germany subset.")

    if st.button("Evaluate reading"):
        expected = float(baseline.loc[month, profile])
        try:
            with st.spinner("Evaluating…"):
                turn = pipeline.predictive_turn(
                    data_loader.PROFILE_LABELS[profile], calendar.month_name[month], expected, observed
                )
            result, alert = turn["prediction"], turn["alert"]
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not evaluate this reading: {exc}")
            result, alert = None, None

        if result:
            col1, col2, col3 = st.columns(3)
            col1.metric("Expected COP", result["expected_cop"])
            col2.metric("Observed COP", result["observed_cop"])
            col3.metric("Deviation", f"{result['deviation_pct']}%")
            st.markdown(f"### {predictive.SEVERITY_LABELS[result['severity']]}")

        if alert:
            st.info(alert["note"])
            if not alert["ai_generated"]:
                st.caption("⚠️ Deterministic note (no live model response) — add OPENAI_API_KEY for an AI-generated one.")


# ---------------------------------------------------------------------------
# Mode 4 — Installed Fleet Overview (demo: all 3 predictive flags at once)
# ---------------------------------------------------------------------------

else:
    st.title("🏠 Installed Fleet Overview")
    st.caption(
        "The same COP-Drop Early-Warning check from the previous tab, run across an entire installed "
        "fleet at once — a portfolio view built for demo purposes so it's obvious at a glance what this "
        "use case catches. This is a small, hand-curated synthetic table, not real telemetry — see "
        "data/installed_fleet_documentation.md."
    )

    try:
        fleet_df = cached_installed_fleet()
        baseline = cached_cop_baseline()
        evaluated = fleet.evaluate_fleet(fleet_df, baseline)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not load/evaluate the installed fleet: {exc}")
        st.stop()

    counts = fleet.fleet_summary_counts(evaluated)
    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Normal", counts["normal"])
    col2.metric("🟡 Watch", counts["watch"])
    col3.metric("🔴 Early warning", counts["early_warning"])

    FLAG_EMOJI = {"normal": "🟢", "watch": "🟡", "early_warning": "🔴"}
    display_df = evaluated.copy()
    display_df["Flag"] = display_df["severity"].map(FLAG_EMOJI) + " " + display_df["severity"].str.replace(
        "_", " "
    ).str.title()
    display_df["Profile"] = display_df["profile"].map(data_loader.PROFILE_LABELS)
    display_df = display_df.rename(
        columns={
            "unit_id": "Unit",
            "model": "Model",
            "region": "Region",
            "expected_cop": "Expected COP",
            "observed_cop": "Observed COP",
            "deviation_pct": "Deviation %",
            "notes": "Notes",
        }
    )
    st.dataframe(
        display_df[
            ["Unit", "Model", "Profile", "Region", "Expected COP", "Observed COP", "Deviation %", "Flag", "Notes"]
        ].sort_values("Deviation %", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"{len(evaluated)} units shown — synthetic demo fleet, deliberately spans all 3 flags.")

    if st.button("Generate fleet summary"):
        flagged_units = evaluated[evaluated["severity"] != "normal"].to_dict("records")
        try:
            with st.spinner("Generating summary…"):
                summary = pipeline.fleet_overview_turn(counts, flagged_units)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not generate a fleet summary: {exc}")
            summary = None

        if summary:
            st.info(summary["summary"])
            if not summary["ai_generated"]:
                st.caption("⚠️ Deterministic summary (no live model response) — add OPENAI_API_KEY for an AI-generated one.")
