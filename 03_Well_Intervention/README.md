# 03 — Well Intervention Candidate Selection & Economic Decision Case

Turns Project 2's diagnoses into a funded decision: discounted cashflow economics (NPV, payout, ROI, capital efficiency) for every candidate intervention across 4 wells, a fleet-wide capital allocation ranking for a constrained workover budget, and an oil-price sensitivity check.

**➡️ [Read the full report](report.md)**

## Key result
Ranking by **capital efficiency** (NPV per $ invested) rather than diagnosis severity changes the funding order — three cheap fixes (Reduce SPM, install POC, install gas anchor, total **$27,500**) outrank a $95,000 rod-replacement workover on a per-dollar basis, even though that workover has the highest absolute NPV. Well B-04 surfaces a genuine trade-off between a **slickline valve replacement** ($28k, higher capital efficiency) and a **full workover** ($85k, higher absolute NPV) — the kind of judgment call a production engineer is expected to flag, not silently resolve.

## Structure
```
03_Well_Intervention/
├── README.md
├── report.md                              <- full write-up (start here)
├── data/
│   └── interventions.py                    <- intervention catalog + economic assumptions
├── src/
│   ├── economics.py                        <- NPV / payout / ROI / capital efficiency engine
│   └── run_analysis.py                     <- runs all wells x interventions, generates plots
└── outputs/
    ├── 00_fleet_capital_allocation_ranking.png
    ├── well_B-02_economics.png / B-03 / B-04 / B-05
    ├── 03_payout_period_recommended.png
    ├── 04_oil_price_sensitivity.png
    └── results_summary.json
```

## Run it yourself
```bash
pip install numpy matplotlib
python src/run_analysis.py
```

## Method summary
- **Input:** diagnosis + lost production per well, carried forward directly from Project 2 (no re-diagnosis).
- **Economics:** job cost incurred in full; incremental revenue is success-probability-weighted and declines monthly over a 12-month horizon; NPV/ROI use discounted cashflow, payout uses undiscounted cumulative revenue (standard field convention).
- **Two ranking lenses, both shown explicitly:** absolute NPV (best if capital is unconstrained) vs. capital efficiency / NPV-per-dollar (best for a constrained budget) — the report shows where these two lenses disagree (well B-04) rather than picking one and hiding the tension.
- **Robustness check:** oil price sensitivity from $50–90/bbl on the recommended portfolio.

## Part of a larger portfolio
This is Project 3, completing the diagnostic-to-decision chain: **Project 1** (production optimization) → **Project 2** (SRP diagnostics) → **Project 3** (this project — funding decision). Together they demonstrate reservoir/production analysis, artificial-lift surveillance, and commercial decision-making — the same combination reflected in this candidate's actual field + procurement experience.
