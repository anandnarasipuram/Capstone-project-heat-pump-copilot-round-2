# Sector Research

> Industry/sector: Home Energy & HVAC (Heat Pumps)
> Scenario: Chleo runs a small–medium heat pump manufacturer entering/competing in the German market
> Use case: Heat Pump Field Commissioning & API/App Connectivity Copilot

## Market overview

- Germany's political target is **500,000 heat pumps installed per year from 2024**, en route to **6 million cumulative by 2030**. [[7]](https://www.eceee.org/all-news/news/germany-to-miss-2024-heat-pump-target-by-half) Actual 2024 sales landed at only **~193,000 units — down 46% from 2023** and badly missing that target — largely due to uncertainty around municipal heat-planning rules and low public awareness of the subsidy programs available. The industry association (BWP) forecasts a rebound of **~33% to ~257,000 units in 2025**, which would still fall well short of the 500k/year target. [[1]](https://www.cleanenergywire.org/news/heat-pump-sales-halved-germany-2024-industry-confident-better-times-ahead) **This target-vs-actual gap is the core "why now" for the pitch**: Germany isn't short on ambition or subsidy money, it's short on the field capacity to convert orders into working, correctly-commissioned installations.
- Reaching the 6M-by-2030 target is independently estimated to require a **~50% uplift in the certified installer/HVAC-technician workforce**. [[8]](https://www.aldersgategroup.org.uk/content/uploads/2025/11/Heat-Pump-Workforce-report-1.pdf) The EU-wide version of the same constraint: **500,000+ new heat pump installers are needed by 2030**. [[9]](https://ehpa.org/news-and-resources/news/training-for-tomorrow-building-europes-clean-heating-workforce/)
- The German heat pump market crossed **USD 1.5B in 2024** and is projected to grow at roughly **28% CAGR through 2034**, i.e. the underlying long-term demand curve is strongly up even though 2024 was a trough year. [[2]](https://www.gminsights.com/industry-analysis/germany-heat-pump-market)
- Net takeaway for the pitch: this is a **volatile-but-recovering, policy-driven market with a structural labor ceiling**. A manufacturer's near-term challenge isn't demand generation, it's converting subsidy-driven order growth into installed, working, low-callback units without proportionally growing service headcount it can't hire fast enough regardless.

## Why this problem, why now — the technical root cause

Two field problems recur for a small-medium manufacturer selling a smart heat pump bundled with an app-based **HEMS (Home Energy Management System)** layer: (1) installers hit fault codes they can't resolve on-site without escalating to senior technicians, and (2) the heat pump controller's connection to the HEMS app is unreliable, so customers report "broken" units that are actually just connectivity issues.

The technical cause is well-documented in the wider HVAC industry, not specific to any one vendor:
- **Inverter heat pumps rely on proprietary manufacturer communication protocols** to continuously modulate capacity — the three most common families are BACnet, Modbus, and the proprietary LonTalk, and they are not easily interoperable with each other. [[10]](https://insights.globalspec.com/article/18742/12-common-hvac-communication-protocols) A communicating thermostat/HEMS controller has to be matched to the specific outdoor unit and controls; non-matching combinations run in a degraded, limited-stage mode rather than failing cleanly. [[11]](https://www.acdirect.com/blog/thermostats-controls-inverter-units/) This is exactly the ambiguity an installer faces in the field: is a "not responding correctly" unit a hardware fault, or a protocol/pairing mismatch?
- **Improper installation and commissioning is the norm, not the exception, across the HVAC industry**: US DOE-funded research found **70–90% of air conditioner and heat pump systems have at least one performance-compromising fault from improper installation**, rising to 90–100% once duct leakage is included. [[12]](https://www.osti.gov/servlets/purl/1660191) NIST's related field studies attribute roughly **20–30% higher energy use** to improperly installed HVAC equipment. [[13]](https://www.nist.gov/news-events/news/2014/11/underperforming-energy-efficiency-hvac-equipment-suffers-due-poor-installation) These figures are general HVAC/US-sourced (not Germany- or heat-pump-specific), but they're the best-evidenced version of the claim and the direction — rushed commissioning misses critical settings — applies directly to the German ramp-up given the installer shortage above.

## Key players / competitors

Stiebel Eltron, Vaillant Group, Bosch Thermotechnik, Viessmann Climate Solutions, NIBE Energy Systems, Mitsubishi Electric, Daikin Europe, Glen Dimplex Deutschland, Alpha-InnoTec, and Wolf GmbH are the established manufacturers competing in the German market. [[1]](https://www.cleanenergywire.org/news/heat-pump-sales-halved-germany-2024-industry-confident-better-times-ahead) Chleo's company is framed as a smaller challenger among these — it cannot out-spend the majors on service headcount, so field-support efficiency (getting more first-visit fixes out of the installers it already has access to) is a more realistic lever than out-scaling them.

## Relevant regulations & incentives

- **GEG ("Heizungsgesetz")** — Germany's building energy act requires new/replacement heating systems to run substantially on renewable energy; heat pumps are the default compliant technology, phased in via municipal heat planning.
- **BEG/KfW subsidy** — since Feb 2024, heat pump subsidies run through KfW (BAFA handles building-network cases); homeowners can recover **up to 70% of investment cost**, capped at **€30,000** for the heating-system portion. This subsidy is the main demand driver behind the 2025 rebound forecast. [[3]](https://accentro.de/en/knowledge/home-and-living/bafa-subsidy-for-heat-pumps-2025-everything-you-need-to-know-now)
- **Smart meter gateway mandate** — from 2025, subsidized heat pumps must connect to a certified smart meter gateway for consumption monitoring/smart-grid readiness. This *adds* a new class of network/pairing failure mode on top of existing app-connectivity issues. [[3]](https://accentro.de/en/knowledge/home-and-living/bafa-subsidy-for-heat-pumps-2025-everything-you-need-to-know-now)
- **EU F-Gas Regulation** — from **January 2027**, monobloc heat pumps ≤12 kW must use refrigerants with GWP ≤150; full phase-out of high-GWP refrigerants in that segment by 2032. From **January 2028**, only natural-refrigerant heat pumps remain subsidy-eligible. [[4]](https://www.ehpa.org/wp-content/uploads/2024/11/F-Gas-regulation-guidelines_European-Heat-Pump-Association_November-2024.pdf) This means the hardware/refrigerant mix in the field — and therefore fault codes and fix guidance — will keep shifting over the next few years.
- **EU AI Act** — a copilot that classifies faults and suggests fixes is best understood as **limited-risk** (chatbot/decision-support), which only carries a transparency obligation (disclose that the user is interacting with AI), *provided* it stays advisory and isn't positioned as a safety component of the heating system itself. If it were ever positioned that way, it could be pulled into the high-risk tier (risk-management system, conformity assessment). [[5]](https://www.trail-ml.com/blog/eu-ai-act-how-risk-is-classified) — see [[opportunities_risks]] for how this shapes scope.

## Target users / customer segments

1. **The manufacturer's own field service installers** — primary user of the copilot; needs fast, on-site triage (hardware fault vs. HEMS connectivity/app/pairing issue) to avoid a second truck roll.
2. **Independent SHK (Sanitär-Heizung-Klima) partner installers** — third-party trades who install/service the manufacturer's units but aren't direct employees; same triage need, but weaker access to internal engineering support.
3. **Homeowners** — indirect beneficiary; faster, more accurate first visits mean less downtime and fewer confused calls to Chleo's support line, but they are **not** a direct user of any of the three candidate use cases in [[use_cases]] (all three are installer- or support-team-facing by design, which also keeps Round 1 clear of customer-facing data-privacy scope).

## The structural constraint behind the opportunity

Germany's skilled-trades pipeline produces only **~12,000 new SHK (heating/plumbing/AC) tradespeople per year against an estimated need of ~35,000/year** — a gap made worse by simultaneous demand from the EU heat pump mandate, building-retrofit rules (EPBD), and data-center electrical work competing for the same electricians. [[6]](https://tajhrservices.com/resources/hvac-mechanical-trades-recruitment-europe) This sits alongside, and reinforces, the ~50% installer-workforce uplift needed for Germany's 2030 target noted above. This is the core "why now": a manufacturer cannot hire its way out of a support bottleneck, so a tool that helps **existing** installers fix more units correctly on the first visit is a capacity multiplier, not just a convenience.

## Sources

1. [Heat pump sales halved in Germany in 2024 but industry confident of better times ahead — Clean Energy Wire](https://www.cleanenergywire.org/news/heat-pump-sales-halved-germany-2024-industry-confident-better-times-ahead)
2. [Germany Heat Pump Market Size, Growth Analysis 2025–2034 — GMI Insights](https://www.gminsights.com/industry-analysis/germany-heat-pump-market)
3. [BAFA Subsidy for Heat Pumps 2025 — Accentro](https://accentro.de/en/knowledge/home-and-living/bafa-subsidy-for-heat-pumps-2025-everything-you-need-to-know-now)
4. [The new F-gas Regulation: detailed guidelines — European Heat Pump Association](https://www.ehpa.org/wp-content/uploads/2024/11/F-Gas-regulation-guidelines_European-Heat-Pump-Association_November-2024.pdf)
5. [EU AI Act: Risk-Classifications of the AI Regulation — Trail ML](https://www.trail-ml.com/blog/eu-ai-act-how-risk-is-classified)
6. [HVAC Technician Recruitment for Europe 2026 — Taj HR Services](https://tajhrservices.com/resources/hvac-mechanical-trades-recruitment-europe)
7. [Germany to miss 2024 heat pump target by half — eceee](https://www.eceee.org/all-news/news/germany-to-miss-2024-heat-pump-target-by-half/)
8. [Workforce planning for clean heat: Where will the heat pump workforce come from? — Aldersgate Group](https://www.aldersgategroup.org.uk/content/uploads/2025/11/Heat-Pump-Workforce-report-1.pdf)
9. [Training for tomorrow: building Europe's clean heating workforce — European Heat Pump Association](https://ehpa.org/news-and-resources/news/training-for-tomorrow-building-europes-clean-heating-workforce/)
10. [12 common HVAC communication protocols — GlobalSpec](https://insights.globalspec.com/article/18742/12-common-hvac-communication-protocols)
11. [Thermostats and Controls for Inverter Units: Compatibility Guide — AC Direct](https://www.acdirect.com/blog/thermostats-controls-inverter-units/)
12. [Impact of installation faults in air conditioners and heat pumps in single-family homes on U.S. energy usage — OSTI/DOE](https://www.osti.gov/servlets/purl/1660191)
13. [Underperforming? Energy Efficiency of HVAC Equipment Suffers Due to Poor Installation — NIST](https://www.nist.gov/news-events/news/2014/11/underperforming-energy-efficiency-hvac-equipment-suffers-due-poor-installation)
14. [Get to know your Cosy heat pump / heat pump support — Octopus Energy](https://octopus.energy/heat-pump-help/) (context for the connectivity-vs-hardware confusion referenced in [[opportunities_risks]] and [[use_cases]])
