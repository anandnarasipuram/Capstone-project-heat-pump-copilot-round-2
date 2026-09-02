# POC Documentation — Heat Pump Copilot (No-Code/Low-Code)

> Workflow file: [`poc_workflow.json`](poc_workflow.json) — import directly into n8n (Cloud or self-hosted).
> Implements the flagship use case from [../use_case_definition.md](../use_case_definition.md) / [../research/use_cases.md](../research/use_cases.md): *fault code + symptom → hardware-vs-connectivity-vs-installer-error classification → fix guidance or escalation.*
> This is the Round 1 POC, carried forward unchanged and re-documented in Round 2's required format. The Round 2 upgrade of the same capability (real embeddings-based RAG replacing the keyword match described below) is the working MVP — see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md).

## Tools used

| Component | Tool | Why |
|---|---|---|
| Automation/orchestration | **n8n** (Cloud or self-hosted) | Free-tier-friendly, visual, exports to portable JSON — matches the brief's no-code/low-code accepted tools |
| Trigger/response channel | **Telegram Bot API** | Chosen specifically so the POC is live-demoable in real time (text the bot, watch it classify and reply) rather than only testable via curl/Postman |
| Classification | **OpenAI Chat Completions API** (`gpt-4o-mini`, JSON mode) | Handles messy, free-text installer language — no fixed schema, inconsistent phrasing — where a rule engine would fail; see [../research/use_cases.md](../research/use_cases.md) for the "why an LLM, not a fixed rule engine" argument |
| Grounding | Small manual knowledge base, keyword-matched | See "AI capability shown" below |
| Monitoring (placeholder) | **LangSmith** | Marks where production tracing would attach; the real Round 1 LangSmith evidence is a separate, smaller demonstration — see [../langsmith/](../langsmith/) |

## Purpose

An installer texts a heat pump manufacturer's support bot on Telegram with a fault code or a plain-language symptom. The workflow classifies it as a **hardware fault**, a **HEMS connectivity issue**, or an **installer error**, then replies with either concrete fix guidance or an escalation instruction — always labeled as AI-suggested triage for a human to confirm, never an autonomous action.

Both the deterministic lookup and the LLM classification path are grounded in a small **manual knowledge base** ([../data/manuals/](../data/manuals/)) built from real Vaillant aroTHERM and Octopus Cosy documentation, so fix guidance reflects documented manufacturer behavior rather than the model's generic HVAC knowledge alone.

## Steps (workflow nodes)

**Trigger:** Telegram Trigger (`message` update) — fires on every message sent to the bot. Requires a Telegram Bot token from [@BotFather](https://t.me/BotFather).

| # | Node | Type | What it does |
|---|---|---|---|
| 1 | **Telegram Trigger** | Telegram Trigger | Fires on every incoming chat message. |
| 2 | **Parse Installer Message** | Code | Turns the raw chat message into a ticket shape: `chat_id`, `telegram_user`, `fault_code` (extracted via regex — synthetic codes like `E4`/`CONN-01`, or real Vaillant-style codes like `F.22`/`F22`/`F9998`, normalized to `F.NN`), and `reported_symptom`. `model`/`firmware_version`/`installer_type` default to `"not provided via chat"` — see Limits. |
| 3 | **Lookup Known Fault Code** | Code | Checks the extracted `fault_code` against a deterministic table: 5 synthetic codes plus 8 real Vaillant fault codes. A recognized code is resolved instantly — no LLM call, no cost, fully auditable — and carries a `manual_sources` citation for the real codes. |
| 4 | **Known Fault Code?** | IF | Branches on whether step 3 found a match. |
| 5 | **Retrieve Manual Context** *(false branch)* | Code | For symptoms with no recognized code, a lightweight keyword match against the manual knowledge base attaches up to 2 matching excerpts as `manual_context` plus a `manual_sources` citation list. |
| 6 | **Classify via OpenAI** | HTTP Request | Sends the symptom — plus any `manual_context` — to OpenAI (Chat Completions, JSON mode). System prompt instructs the model to treat manual excerpts as authoritative when present, and reply in whichever language the installer used. |
| 7 | **Parse OpenAI Response** | Code | Parses OpenAI's JSON reply; recovers the original ticket fields; **falls back to a safe default of escalation** if the model output can't be parsed — never silently defaults to "no action needed." |
| 8 | **Is Hardware Fault?** | IF | Both branches converge here. Routes on the resolved `category`. |
| 9 | **Build Escalation Response** *(true branch)* | Set | Formats an escalation payload ending in *"AI-suggested triage, confirm before acting."* |
| 10 | **Build Fix Guidance Response** *(false branch)* | Set | Same shape, `status: resolved_guidance`, message leads with *"Suggested fix: ..."* |
| 11 | **Log to Monitoring (LangSmith)** | NoOp (placeholder) | Marks where every triage decision would be posted to LangSmith in production. |
| 12 | **Format Telegram Reply** | Code | Formats the result into a short chat-formatted reply with a source footer. |
| 13 | **Send Telegram Reply** | Telegram | Sends the reply back to the installer's chat. |

## AI capability shown

Two AI/ML-relevant behaviors are demonstrated end-to-end in this POC:

1. **Retrieval-grounded classification of unstructured free text.** The core problem — installer symptom language with no fixed schema, inconsistent phrasing, mixed vocabulary between "the unit," "the app," and "the HEMS" — is exactly the kind of natural-language understanding an LLM handles and a rule-based classifier doesn't (see [../research/use_cases.md](../research/use_cases.md)). The manual-grounding step is a **lexical (keyword) retrieval-augmented generation pattern**: it retrieves relevant manual excerpts and forces the model to prefer documented manufacturer guidance over its own generic assumptions — the same RAG *pattern* the MVP upgrades to real embeddings.
2. **Deterministic-first, LLM-fallback routing**, so the system only pays for (and exposes itself to) an LLM call when the input doesn't resolve to a known, auditable answer — 13 fault codes bypass the model entirely.

## Language

German installers are the primary real-world user for this pilot; the manual corpus and keyword lists are English-first with a handful of hand-added German synonyms. The LLM classification step handles language natively (replies in whichever language the installer used, no separate translation call); the keyword retrieval step is the weaker mechanism — it only covers anticipated German terms, and this gap is exactly what the MVP's multilingual embeddings upgrade resolves (see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md)).

## Inputs / outputs

**Input:** whatever the installer types into the Telegram chat, e.g. `Low refrigerant pressure alarm, error code E4`

**Output (Telegram reply):**
```
🔧 *Hardware fault*

Escalation required: Escalate to hardware service technician (compressor/refrigerant circuit inspection). Not resolvable by app/firmware update. — AI-suggested triage, confirm before acting.

_Source: fault-code lookup (confidence 1)_
```

### Worked examples

| Installer message | Path taken | Reply |
|---|---|---|
| "Low refrigerant pressure alarm, error code E4" | `E4` extracted → lookup match → hardware_fault | 🔧 Hardware fault — escalate, source: fault-code lookup, confidence 1 |
| "No comms from the outdoor unit, controller not responding" | No code → keyword match → OpenAI classifies, grounded in F.9998 excerpt → installer_error | ✅ Installer/commissioning error — check eBUS wiring before escalating — *(Grounded in: Vaillant aroTHERM fault code reference (F.9998))* |
| "Fault code F532 showing, low flow rate" | `F532` normalized to `F.532` → lookup match → installer_error | ✅ Installer/commissioning error — check building circuit for blockage/air/balancing, source: fault-code lookup |
| "Wasserdurchfluss Problem, Pumpe steht" (German) | No code → keyword match on "wasserdurchfluss" → OpenAI classifies **in German**, grounded in F.532/F.788 → installer_error | ✅ (German-language fix guidance) |
| "Smart meter gateway will not pair with the control unit" | No code, no keyword match → OpenAI classifies unassisted → connectivity_issue | ✅ HEMS connectivity issue — re-pair via app, check 2.4GHz band and gateway certificate, source: AI classification |

All five rows were unit-tested directly against the actual generated node code (`Parse Installer Message` → `Lookup Known Fault Code` → `Retrieve Manual Context`) — the regex extraction, code normalization, and keyword scoring behave exactly as shown. **This does not call the real OpenAI API**, so the LLM-classified rows show the *grounding* that reaches the model, not a captured live model response — see Limits.

## Limits vs. production

- **Telegram only supplies free text** — `model`/`firmware_version`/`installer_type` default to placeholders; a production version would tag the chat with equipment context automatically (e.g. a QR scan at the unit).
- **Manual grounding is keyword-based and English-first** — resolved in the MVP via multilingual embeddings + Pinecone (see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md)).
- **Manual corpus is small and drawn from representative UK documentation, not Chleo's own product line** — see [../data/manuals/README.md](../data/manuals/README.md).
- **LangSmith is a placeholder node here** — the real Round 1 trace/eval evidence lives in [../langsmith/](../langsmith/) as a separate, smaller demonstration. **Resolved in the MVP**: Round 2's app traces every interaction live and continuously (not a one-off script) — see [../mvp/mvp_documentation.md](../mvp/mvp_documentation.md), "Monitoring — LangSmith tracing."
- **The fault-code lookup table is small** (13 codes) — production would load a full manufacturer fault-code database.
- **No retry/rate-limit handling**, and the bot is only as secure as its Telegram token — expected of a POC, not a hardened endpoint.
- **The classifier never issues autonomous repair instructions for hardware faults**, by design — a deliberate safety constraint, not a gap to close.
- **Not run against a live n8n/Telegram bot in this environment.** The JSON was hand-built to n8n's workflow schema; structural correctness (well-formed JSON, all node connections resolve, no orphans) was validated automatically, and every Code node was unit-tested against the exact generated code with the worked examples above. It has not been visually confirmed by importing into n8n and talking to a live bot — see "How to reproduce."

## How to reproduce

1. Message [@BotFather](https://t.me/BotFather) on Telegram, create a bot, copy its token.
2. In n8n: **Import from File** → [`poc_workflow.json`](poc_workflow.json).
3. Add a Telegram credential with that token; attach it to **Telegram Trigger** and **Send Telegram Reply** (already referenced by name — n8n will prompt you to reconnect it).
4. Set `OPENAI_API_KEY` in n8n's environment variables (Settings → Environment).
5. Activate the workflow.
6. Open a chat with your bot and try the worked examples above — start with `E4` (needs no API key at all, resolved by the lookup step), then a free-text example to see manual grounding, then the German example to see language handling.

## Demo recording (2–5 minutes, separate submission artifact)

Not included in this repo as a video file — record by following the reproduction steps above with a live bot, and capture:
1. The `E4` example (instant, zero-API-key lookup) — establishes the deterministic path works.
2. A free-text symptom with no fault code (e.g. the eBUS example) — shows manual-grounded LLM classification and the citation in the reply.
3. A quick screen-share of the n8n canvas showing the node graph, so the workflow structure is visible, not just the chat output.
4. One sentence stating this is Round 1's POC and pointing to the MVP (`mvp/`) as the Round 2 production-track upgrade of the same capability.
