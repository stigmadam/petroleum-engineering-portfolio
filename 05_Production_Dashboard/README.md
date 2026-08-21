# 05 — Production Surveillance Dashboard

An interactive fleet-surveillance dashboard covering 18 wells. The dashboard runs directly in any web browser, with no installation, server, or Python environment required.

**➡️ [Read the full report](report.md)** · **➡️ [Open the live dashboard](https://htmlpreview.github.io/?https://github.com/stigmadam/petroleum-engineering-portfolio/blob/main/05_Production_Dashboard/outputs/index.html)**

## Key result
Rule-based attention classifier (consistent with Projects 1–3's diagnostic vocabulary) surfaces **2 Critical and 6 Watch wells out of 18** from 52 weeks of synthetic weekly production data — a realistic triage distribution, with inline sparklines and click-to-expand trend charts explaining *why* each well was flagged, not just that it was.

## Structure
```
05_Production_Dashboard/
├── README.md
├── report.md                  <- full write-up
├── src/
│   └── generate_data.py        <- generates the 18-well synthetic fleet + attention scoring
└── outputs/
    ├── index.html               <- the dashboard itself
    ├── dashboard.js              <- rendering, filtering, sparklines, detail charts
    └── wells_data.json           <- generated dataset (also embedded inline in index.html)
```

## Method summary
- **Data**: Python-generated, 18 wells × 52 weeks, with deliberate "stories" (water breakthrough, gas breakthrough, SRP failure modes, post-workover recovery) rather than random noise.
- **Classifier**: rule-based Normal/Watch/Critical scoring on trailing 6-week trends — explainable by design, matching the rest of this portfolio's approach.
- **Frontend**: vanilla JS + Chart.js (CDN), no framework, no build step — the dashboard is a single static file, viewable by anyone with zero setup.

*To regenerate the dataset: `python src/generate_data.py` (requires numpy). The output JSON is embedded directly into `outputs/index.html` — see the script's docstring for the re-embed step.*

## Part of a larger portfolio
This is Project 5, the final piece: where Projects 1–4 go deep on one well or one field at a time, this dashboard is the fleet-wide view that ties the portfolio's diagnostic vocabulary (nodal analysis, SRP diagnostics, intervention economics) together operationally.
