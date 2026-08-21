# 05 — Production Surveillance Dashboard

An interactive fleet-surveillance dashboard covering 18 wells. The dashboard runs directly in any web browser, with no installation, server, or Python environment required.

**➡️ [Read the full report](report.md)** · **➡️ [Open the live dashboard](https://htmlpreview.github.io/?https://github.com/stigmadam/petroleum-engineering-portfolio/blob/main/05_Production_Dashboard/outputs/index.html )**

## Key result
Rule-based attention classifier (consistent with Projects 1–3's diagnostic vocabulary) surfaces **2 Critical and 6 Watch wells out of 18** from 52 weeks of synthetic weekly production data — a realistic triage distribution, with inline sparklines and click-to-expand trend charts explaining *why* each well was flagged, not just that it was.

## Structure
```
05_Production_Dashboard/
├── README.md
├── report.md                  <- full write-up (start here)
├── src/
│   └── generate_data.py        <- generates the 18-well synthetic fleet + attention scoring
└── outputs/
    ├── index.html               <- the dashboard itself (open this)
    ├── dashboard.js              <- rendering, filtering, sparklines, detail charts
    └── wells_data.json           <- generated dataset (also embedded inline in index.html)
```

## Run it yourself
```bash
# regenerate the dataset
pip install numpy
python src/generate_data.py

# re-embed the fresh data into the dashboard (data is inlined for a fully standalone file)
python3 -c "
import json
data = json.load(open('outputs/wells_data.json'))
html = open('outputs/index.html').read()
import re
html = re.sub(r'const WELLS = \[.*?\];', 'const WELLS = ' + json.dumps(data) + ';', html, flags=re.S)
open('outputs/index.html', 'w').write(html)
"
```
Then just open `outputs/index.html` in a browser.

## Method summary
- **Data**: Python-generated, 18 wells × 52 weeks, with deliberate "stories" (water breakthrough, gas breakthrough, SRP failure modes, post-workover recovery) rather than random noise.
- **Classifier**: rule-based Normal/Watch/Critical scoring on trailing 6-week trends — explainable by design, matching the rest of this portfolio's approach.
- **Frontend**: vanilla JS + Chart.js (CDN), no framework, no build step — chosen specifically so the dashboard is viewable by anyone with zero setup, including directly on GitHub Pages.

## Part of a larger portfolio
This is Project 5, the final piece: where Projects 1–4 go deep on one well or one field at a time, this dashboard is the fleet-wide view that ties the portfolio's diagnostic vocabulary (nodal analysis, SRP diagnostics, intervention economics) together operationally.
