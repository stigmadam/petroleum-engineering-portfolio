# Production Surveillance Dashboard

**Author:** David Damanik
**Project type:** Independent portfolio tool (synthetic field data, standalone interactive dashboard)
**Tools:** Python (data generation), HTML/CSS/JavaScript, Chart.js — no server, no build step, no installation required

---

## 1. What This Is

A field-wide production surveillance dashboard for an 18-well fleet — the kind of screen a production engineer would actually use to scan a field in under a minute and decide which wells need attention today. Unlike Projects 1–4 in this portfolio, this one is not a calculation notebook: it's a standalone, interactive tool. Open `outputs/index.html` in any browser — no Python environment, no server, no installation.

## 2. Why a Dashboard, and Why Standalone HTML

Projects 1–3 established a diagnostic vocabulary (IPR/VLP, SRP card diagnostics, intervention economics) applied one well at a time. A real production engineer also needs the **fleet-wide view** — which of 18+ wells deserve attention this week, sorted by severity, without opening 18 separate reports. This project builds that view.

It's built as a single self-contained HTML file rather than a Streamlit app so that **anyone can open it immediately** — a recruiter clicking a GitHub link, or this file just double-clicked locally — with no Python installation or `pip install` step required to see it work.

## 3. Data & Methodology

### 3.1 Synthetic well fleet
18 wells across 3 fields, 52 weeks of weekly data each, generated in Python (`src/generate_data.py`) with deliberately varied "stories" so the dashboard has genuine signal to surface:

- **Field A** (7 wells, natural flow): stable/healthy wells, normal decline, water breakthrough, gas breakthrough
- **Field B** (7 wells, SRP artificial lift): ties directly to Project 2's diagnostic vocabulary — gas interference, fluid pound, worn valve, sudden mechanical failure, and a post-workover recovery case
- **Field C** (4 wells, mature mixed): stable, accelerating decline, near end of economic life, and a newly completed high-rate well

### 3.2 Rule-based attention classifier
Each well is scored **Normal / Watch / Critical** from its trailing 6-week trend against its prior 6-week baseline:

- Water cut level and rate of rise (near-economic-limit threshold, and a faster-rising-but-not-yet-critical threshold)
- Oil rate decline rate
- GOR rise relative to baseline (gas breakthrough signature)
- Pump efficiency level and trend, for SRP wells only

This mirrors the diagnostic logic from Projects 1–3 rather than introducing a new framework — the portfolio uses one consistent surveillance vocabulary throughout.

### Result on this synthetic fleet: **2 Critical, 6 Watch, 10 Normal** — a realistic attention distribution, not an evenly-split toy example.

## 4. What the Dashboard Does

- **Field-wide KPI strip**: total oil rate, active well count, wells needing attention, field-average water cut — the numbers a shift handover would open with.
- **Filterable, sortable well table**: filter by status (Critical/Watch/Normal), sort by attention priority, oil rate, or water cut.
- **Inline sparklines**: every row shows a 52-week oil-rate trend at a glance — deliberately dense, the way real SCADA/surveillance tools (e.g. PI Vision, Spotfire) present fleet data, not a decorative chart.
- **Expandable detail view**: clicking a well expands a full trend chart (oil rate, water cut, and pump efficiency where applicable) plus the specific surveillance notes that drove its status — so the tool explains *why* a well was flagged, not just that it was.

## 5. Design Notes

The visual language is deliberately built around a control-room/telemetry aesthetic (dark background, monospace numerals for all data values, status colors calibrated for quick scanning) rather than a generic report or chart-heavy layout — because the actual job of this screen is fast triage across many wells, not detailed reading of any one number.

## 6. How This Fits the Portfolio

| Project | Scope |
|---|---|
| 1 — Production Optimization | Single-well nodal analysis |
| 2 — SRP Diagnostics | Single-well dynamometer diagnosis |
| 3 — Well Intervention | Single-fleet-slice economic decision |
| 4 — CO2-EOR DOE | Reservoir-level sensitivity study |
| **5 — This dashboard** | **Fleet-wide, real-time-style surveillance — the view that ties the others together operationally** |

## 7. Limitations & Next Steps

- All well data is synthetic, generated to produce realistic *patterns* (decline curves, water breakthrough, SRP failure modes), not measured field data.
- The attention classifier is intentionally simple and rule-based (matching Projects 1–3's explainable-over-black-box philosophy) — a production deployment would likely calibrate thresholds against a field's own historical data rather than fixed values.
- No backend/database — data is generated once and embedded directly in the page. A next step toward a real internal tool would add a live data connection (e.g. to a historian or SCADA export) rather than a static snapshot.
- Chart.js is loaded from a public CDN; an offline-capable version would vendor the library locally.

---
*Data generation code is in `/src`. Run `python src/generate_data.py` to regenerate `outputs/wells_data.json`, then re-embed it into `outputs/index.html` (see README for the exact command).*
