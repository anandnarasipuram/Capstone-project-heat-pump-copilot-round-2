"""Heat Pump Copilot — Round 2 MVP.

Single Streamlit app covering all three use-case candidates from
research/use_cases.md, sequenced in Round 1 as flagship + two Round 2
companions, plus a portfolio view of the third. Navigation is a 3-item
menu in the sidebar (Dashboard / Installed Fleet Overview / System
status — a real page router via st.session_state.active_page, not
decorative labels); Dashboard itself holds 3 tabs:

  Dashboard (default page)
    1. 🩺 Fault Triage Copilot      — reactive, the flagship, chat-style RAG
    2. ✅ Commissioning Checker     — preventive
    3. 📉 COP-Drop Early-Warning    — predictive, single unit
  🏘️ Installed Fleet Overview       — predictive, portfolio view, its own page
  ⚙️ System status                  — technical config status, its own page

The Dashboard's Tab 1 is the core, end-to-end AI capability this MVP
exists to prove: fault-code lookup (deterministic, zero cost) →
Pinecone RAG over the manual knowledge base (real embeddings, the
Round 2 upgrade from the POC's keyword match) → OpenAI classification,
grounded in whatever the retrieval step found. See mvp_documentation.md
for the full architecture, what "runs" means with vs. without API keys,
and how to reproduce.

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

st.set_page_config(
    page_title="Heat Pump Copilot", page_icon="🔧", layout="wide", initial_sidebar_state="collapsed"
)

CATEGORY_LABELS = {
    "hardware_fault": "Hardware fault",
    "connectivity_issue": "HEMS connectivity issue",
    "installer_error": "Installer/commissioning error",
}

# Chleo's fictional model lineup, reused from data/synthetic_fault_dataset.csv
# for consistency across the whole demo. See Tab 1's selector below and
# core/llm.py's module docstring for what this does (and doesn't) do.
MODEL_OPTIONS = ["Not specified", "TF-08", "TF-12", "AS-10", "AS-16"]

FLEET_FLAG_EMOJI = {"normal": "🟢", "watch": "🟡", "early_warning": "🔴"}
FLEET_SEVERITY_TO_ALERT_LEVEL = {"early_warning": "High", "watch": "Medium", "normal": "Low"}


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
# Fleet status — computed once, shared by the header notification bell and
# the Installed Fleet Overview page, so both always agree and neither
# recomputes it separately.
# ---------------------------------------------------------------------------

try:
    fleet_df = cached_installed_fleet()
    baseline_df = cached_cop_baseline()
    fleet_evaluated = fleet.evaluate_fleet(fleet_df, baseline_df)
    fleet_counts = fleet.fleet_summary_counts(fleet_evaluated)
except Exception:  # noqa: BLE001 — a bad fleet load shouldn't take down the whole app
    fleet_evaluated, fleet_counts = None, {"normal": 0, "watch": 0, "early_warning": 0}


# ---------------------------------------------------------------------------
# Navigation state — which of the 3 menu pages is showing. The sidebar
# menu's buttons are the only writer of this; everything else just reads
# it. Single source of truth for what the main content area renders.
# ---------------------------------------------------------------------------

if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"


# ---------------------------------------------------------------------------
# Header — title, plus a notification bell and a profile icon, side by
# side, matching size — icon-only triggers, details live in their popovers.
# ---------------------------------------------------------------------------

header_left, header_bell, header_profile = st.columns([6, 0.8, 0.8])
with header_left:
    st.title("🔧 Heat Pump Copilot")
    st.caption("Field Commissioning & HEMS Connectivity Copilot")

with header_bell:
    alert_total = fleet_counts["early_warning"] + fleet_counts["watch"]
    bell_label = f"🔔 {alert_total}" if alert_total else "🔔"
    with st.popover(bell_label, use_container_width=True):
        st.markdown("**Fleet alerts**")
        st.caption("From the Installed Fleet Overview page (menu, top-left) — synthetic demo fleet, not real telemetry.")
        st.markdown(f"🔴 High — {fleet_counts['early_warning']} unit(s) need inspection now")
        st.markdown(f"🟡 Medium — {fleet_counts['watch']} unit(s) to monitor")
        st.markdown(f"🟢 Low — {fleet_counts['normal']} unit(s) normal")
        if fleet_evaluated is not None and alert_total:
            st.divider()
            flagged = (
                fleet_evaluated[fleet_evaluated["severity"] != "normal"][["unit_id", "model", "severity"]]
                .assign(Alert=lambda d: d["severity"].map(FLEET_SEVERITY_TO_ALERT_LEVEL))
                .rename(columns={"unit_id": "Unit", "model": "Model"})[["Unit", "Model", "Alert"]]
            )
            st.dataframe(flagged, hide_index=True, use_container_width=True)

with header_profile:
    with st.popover("👤", use_container_width=True):
        st.markdown("**Chleo**")
        st.caption("Demo profile — this MVP has no real authentication; see mvp_documentation.md.")

st.divider()


# ---------------------------------------------------------------------------
# Sidebar menu — collapsed by default (Streamlit's native hamburger-style
# toggle at the top-left handles open/close, no custom widget needed).
# Three real, selectable navigation buttons — clicking one changes what
# the main content area renders (st.session_state.active_page), the
# currently-selected one shown filled (type="primary") so it's obvious
# which page you're on.
# ---------------------------------------------------------------------------

st.sidebar.markdown("### Menu")
for page_name, icon in [
    ("Dashboard", "🏠"),
    ("Installed Fleet Overview", "🏘️"),
    ("System status", "⚙️"),
]:
    is_active = st.session_state.active_page == page_name
    if st.sidebar.button(
        f"{icon} {page_name}",
        key=f"nav_{page_name}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
        st.session_state.active_page = page_name
        st.rerun()


# ---------------------------------------------------------------------------
# Human-in-the-loop notice — the Art. 50 EU AI Act transparency disclosure
# (see compliance/eu_ai_act_compliance.md). Pinned to the bottom of the
# viewport via CSS so it's visible at all times on every page, independent
# of the (now collapsed-by-default) sidebar menu — it shouldn't be
# possible to miss this by simply not opening the menu.
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .block-container { padding-bottom: 5rem; }
    #hitl-footer {
        position: fixed; left: 0; right: 0; bottom: 0; z-index: 999999;
        background: var(--secondary-background-color);
        border-top: 1px solid rgba(128, 128, 128, 0.35);
        padding: 0.5rem 1.5rem;
        font-size: 0.85rem;
        color: var(--text-color);
        text-align: center;
    }
    </style>
    <div id="hitl-footer">
        🤝 <b>Human-in-the-loop, by design</b> — every response here is AI-suggested triage;
        a human installer always confirms before acting on electrical or refrigerant work.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Page: Dashboard — browser-style tabs for the 3 operational tools
# ---------------------------------------------------------------------------

if st.session_state.active_page == "Dashboard":
    tab_triage, tab_checklist, tab_predictive = st.tabs(
        [
            "🩺 Fault Triage Copilot",
            "✅ Commissioning Checker",
            "📉 COP-Drop Early-Warning",
        ]
    )

    # -------------------------------------------------------------------
    # Tab 1 — Fault Triage Copilot (flagship, chat-style RAG)
    # -------------------------------------------------------------------

    with tab_triage:
        st.caption(
            "An installer enters a fault code or symptom. The copilot classifies it as a "
            "hardware fault, a HEMS connectivity/pairing issue, or an installer/commissioning "
            "error, and returns fix guidance or an escalation route."
        )

        selected_model = st.selectbox(
            "Select a heat pump",
            MODEL_OPTIONS,
            help=(
                "Optional. Sharpens the AI's answer and lets Chleo's team see fault trends "
                "by model over time — it doesn't currently filter which fault codes are "
                "recognized, since today's manual knowledge base isn't split per model."
            ),
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "pending_prompt" not in st.session_state:
            st.session_state.pending_prompt = None

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "user":
                    st.write(msg["content"])
                else:
                    render_assistant_card(msg)

        # Read the incoming prompt (typed, or from an example-button click
        # below) and process it *before* deciding whether to show the empty
        # state — so a clicked example's answer never renders on the same
        # pass as the "get started" buttons above it. See the button loop's
        # comment below for why the buttons are defined after this block.
        prompt = st.chat_input("Describe the fault or paste a fault code, e.g. 'F532 low flow rate'…")
        if st.session_state.pending_prompt:
            prompt = st.session_state.pending_prompt
            st.session_state.pending_prompt = None
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

        # Empty-state guidance: the chat box above is pinned to the bottom of
        # the screen by Streamlit regardless of where st.chat_input() is called
        # in the script (that's not something this app can move), so on first
        # load the page looked like empty dead space between here and the
        # input. Clickable example prompts fill that space and double as
        # onboarding — click one, or type your own below. Same pattern
        # ChatGPT/Claude use on a blank chat. Checked *after* processing above,
        # so a just-clicked example's result (now in session_state.messages)
        # correctly hides these buttons on this same render pass, not just
        # the next one — clicking still triggers an immediate rerun via
        # st.rerun() so the result shows right away rather than needing a
        # second interaction to flush the pending click.
        if not st.session_state.messages:
            st.markdown("#### 💬 Ask about a fault code or symptom to get started")
            st.caption("Tap an example below, or type your own question in the box at the bottom of the screen.")
            example_prompts = [
                "Low refrigerant pressure alarm, error code E4",
                "Fault code F532 showing, low flow rate",
                "No comms from the outdoor unit, controller not responding",
                "Smart meter gateway will not pair with the control unit",
            ]
            ex_col1, ex_col2 = st.columns(2)
            for i, example in enumerate(example_prompts):
                target_col = ex_col1 if i % 2 == 0 else ex_col2
                if target_col.button(example, use_container_width=True, key=f"example_{i}"):
                    st.session_state.pending_prompt = example
                    st.rerun()

    # -------------------------------------------------------------------
    # Tab 2 — Commissioning-Completeness Checker (preventive)
    # -------------------------------------------------------------------

    with tab_checklist:
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
                    st.caption(
                        "⚠️ Deterministic summary (no live model response) — add OPENAI_API_KEY for an AI-generated one."
                    )

    # -------------------------------------------------------------------
    # Tab 3 — COP-Drop Predictive Early-Warning (single unit)
    # -------------------------------------------------------------------

    with tab_predictive:
        st.caption(
            "Compares a reported coefficient-of-performance (COP) reading against the "
            "When2Heat Germany seasonal baseline to flag a unit likely to need attention "
            "before anyone reports a fault. See mvp_documentation.md for the threshold "
            "assumptions this uses."
        )

        if baseline_df is None:
            st.error("Could not load the COP baseline dataset.")
        else:
            col1, col2, col3 = st.columns(3)
            profile = col1.selectbox(
                "Profile",
                options=list(data_loader.PROFILE_LABELS.keys()),
                format_func=lambda k: data_loader.PROFILE_LABELS[k],
            )
            month = col2.selectbox("Month", options=list(range(1, 13)), format_func=lambda m: calendar.month_name[m])
            observed = col3.number_input("Observed COP reading", min_value=0.1, max_value=10.0, value=2.5, step=0.1)

            st.line_chart(baseline_df[profile], height=220)
            st.caption(f"Seasonal baseline for {data_loader.PROFILE_LABELS[profile]} — When2Heat Germany subset.")

            if st.button("Evaluate reading"):
                expected = float(baseline_df.loc[month, profile])
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
                    rcol1, rcol2, rcol3 = st.columns(3)
                    rcol1.metric("Expected COP", result["expected_cop"])
                    rcol2.metric("Observed COP", result["observed_cop"])
                    rcol3.metric("Deviation", f"{result['deviation_pct']}%")
                    st.markdown(f"### {predictive.SEVERITY_LABELS[result['severity']]}")

                if alert:
                    st.info(alert["note"])
                    if not alert["ai_generated"]:
                        st.caption(
                            "⚠️ Deterministic note (no live model response) — add OPENAI_API_KEY for an AI-generated one."
                        )


# ---------------------------------------------------------------------------
# Page: Installed Fleet Overview (demo: all 3 predictive flags at once)
# ---------------------------------------------------------------------------

elif st.session_state.active_page == "Installed Fleet Overview":
    st.header("🏘️ Installed Fleet Overview")
    st.caption(
        "The same COP-Drop Early-Warning check from the Dashboard's predictive tab, run across an entire "
        "installed fleet at once — a portfolio view built for demo purposes so it's obvious at a glance "
        "what this use case catches. This is a small, hand-curated synthetic table, not real telemetry — "
        "see data/installed_fleet_documentation.md."
    )

    if fleet_evaluated is None:
        st.error("Could not load/evaluate the installed fleet.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 Normal", fleet_counts["normal"])
        col2.metric("🟡 Watch", fleet_counts["watch"])
        col3.metric("🔴 Early warning", fleet_counts["early_warning"])

        display_df = fleet_evaluated.copy()
        display_df["Flag"] = display_df["severity"].map(FLEET_FLAG_EMOJI) + " " + display_df[
            "severity"
        ].str.replace("_", " ").str.title()
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
        st.caption(f"{len(fleet_evaluated)} units shown — synthetic demo fleet, deliberately spans all 3 flags.")

        if st.button("Generate fleet summary"):
            flagged_units = fleet_evaluated[fleet_evaluated["severity"] != "normal"].to_dict("records")
            try:
                with st.spinner("Generating summary…"):
                    summary = pipeline.fleet_overview_turn(fleet_counts, flagged_units)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not generate a fleet summary: {exc}")
                summary = None

            if summary:
                st.info(summary["summary"])
                if not summary["ai_generated"]:
                    st.caption(
                        "⚠️ Deterministic summary (no live model response) — add OPENAI_API_KEY for an AI-generated one."
                    )


# ---------------------------------------------------------------------------
# Page: System status — technical configuration status, its own page now
# (was inline sidebar content; pulled out so the sidebar menu is just
# navigation, and this is read like any other page).
# ---------------------------------------------------------------------------

else:
    st.header("⚙️ System status")
    st.caption("Technical configuration status for the AI capabilities behind this app.")

    for label, ok, ok_icon, bad_icon in [
        ("AI classification", llm.is_configured(), "🟢", "🔴"),
        ("Knowledge-base search", rag.is_configured(), "🟢", "🟡"),
        ("Interaction monitoring", tracing.is_configured(), "🟢", "🟡"),
    ]:
        status_label_col, status_icon_col = st.columns([4, 1])
        status_label_col.write(label)
        status_icon_col.write(ok_icon if ok else bad_icon)

    st.divider()
    if not llm.is_configured():
        st.caption("Add OPENAI_API_KEY in .env for live AI responses.")
    if not rag.is_configured():
        st.caption("Add PINECONE_API_KEY in .env for semantic search (falls back to keyword match otherwise).")
    if not tracing.is_configured():
        st.caption("Add LANGSMITH_API_KEY in .env to trace every interaction.")
    if llm.is_configured() and rag.is_configured() and tracing.is_configured():
        st.success("All AI capabilities are fully configured.")
