# 02 — SRP Diagnostics (Dynamometer Card Analysis & Fleet Surveillance)

A fully explainable artificial-lift diagnostic tool built from scratch in Python: generates characteristic dynamometer card shapes for 5 classic SRP failure modes, extracts quantitative features (area ratio, notch depth, top-edge tilt), classifies each card with a rule-based decision tree, and converts every diagnosis into a **ranked production-loss number** for intervention prioritization.

**➡️ [Read the full report](report.md)**

## Key result
Classifier scored **6/6 (100%)** on the synthetic test fleet. More importantly, ranking wells by **lost production** (not diagnosis category alone) reordered intervention priority versus a naive "worst-looking card first" approach — B-05's mechanical failure (179 bopd deferred, 2.2% efficiency) is the clear top priority, ahead of gas interference and fluid-pound cases that look visually dramatic but cost less.

## Structure
```
02_SRP_Optimization/
├── README.md
├── report.md                          <- full write-up (start here)
├── data/
│   └── srp_wells.py                    <- synthetic 6-well fleet (pump design + true condition)
├── src/
│   ├── dyno_card.py                    <- parametric dynamometer card generator (5 failure modes)
│   ├── diagnostics.py                  <- feature extraction + rule-based classifier
│   └── run_analysis.py                 <- runs the fleet, generates plots + results_summary.json
└── outputs/
    ├── 01_fleet_dynamometer_cards.png
    ├── 02_intervention_priority_ranking.png
    └── results_summary.json
```

## Run it yourself
```bash
pip install numpy matplotlib
python src/run_analysis.py
```

## Method summary
- **Card generation:** parametric shapes reproducing recognized SRP failure signatures (rounded/compressed = gas interference, sharp downstroke notch = fluid pound, tilted top edge = worn traveling valve, collapsed card = mechanical failure).
- **Classification:** rule-based decision tree on 4 interpretable features — deliberately not a black-box model, so every diagnosis is explainable to a supervisor before it drives a workover decision.
- **Business layer:** theoretical pump displacement (`PD = 0.1166 × S × SPM × D²`) vs. actual rate → volumetric efficiency → lost bbl/d → intervention ranking.
- **Limitation, stated explicitly in the report:** cards are synthetic/stylized, not from a rod-string wave-equation simulation or real SCADA data; thresholds would need re-calibration against labeled field data before deployment.

## Part of a larger portfolio
This is Project 2, picking up directly where **Project 1 (Production Optimization)** left off — Well A-01 appears in both, transitioning from natural flow to SRP artificial lift once reservoir depletion made natural flow uneconomic. Project 3 (Well Intervention Decision Case) will turn this project's diagnosis + lost-production numbers into a full cost/benefit case.
