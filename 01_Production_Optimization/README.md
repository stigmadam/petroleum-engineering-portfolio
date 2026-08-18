# 01 — Production Optimization (IPR–VLP Nodal Analysis)

Production optimization case study for a mature, undersaturated oil well, built from scratch in Python: full black-oil PVT correlations, a composite (linear + Vogel) IPR calibrated from a single well test, a multiphase VLP pressure traverse, and a nodal-analysis solver — plus sensitivity analysis on tubing size, wellhead pressure, water cut, and reservoir depletion.

**➡️ [Read the full report](report.md)**

## Key result
Base case operating point: **368 STB/d @ 1,164 psia**, against a theoretical AOF of ~690 STB/d. Sensitivity analysis identifies **wellhead/separator backpressure** — not tubing size — as the highest-leverage variable, and quantifies the water-cut and reservoir-depletion thresholds at which the well stops flowing naturally and needs artificial lift.

## Structure
```
01_Production_Optimization/
├── README.md
├── report.md                  <- full write-up (start here)
├── data/
│   └── well_A01.py             <- synthetic well/reservoir dataset
├── src/
│   ├── pvt.py                  <- Standing / Vasquez-Beggs / Beggs-Robinson / Lee PVT correlations
│   ├── model.py                <- IPR, VLP pressure traverse, nodal solver
│   └── run_analysis.py         <- generates all plots + results_summary.json
└── outputs/
    ├── 01_base_case_nodal.png
    ├── 02_sensitivity_tubing.png
    ├── 03_sensitivity_whp.png
    ├── 04_sensitivity_watercut.png
    ├── 05_sensitivity_depletion.png
    └── results_summary.json
```

## Run it yourself
```bash
pip install numpy scipy matplotlib
python src/run_analysis.py
```

## Method summary
- **IPR:** composite linear/Vogel model, productivity index calibrated from a single well test (standard practice for undersaturated reservoirs producing below bubble point).
- **VLP:** multi-segment pressure traverse using a homogeneous no-slip multiphase model, driven by Standing/Vasquez-Beggs/Beggs-Robinson/Lee PVT correlations, Moody/Chen friction factor.
- **Nodal point:** root-finding (Brent's method) on the difference between IPR and VLP bottomhole pressure as a function of rate.
- **Limitation, stated explicitly in the report:** a no-slip model is a simplification vs. a full slip correlation (Hagedorn-Brown/Duns-Ros) — appropriate for screening-level analysis, noted as a next-step refinement.

## Part of a larger portfolio
This is Project 1 of a Petroleum Engineering portfolio focused on **production / well performance / artificial lift**, with reservoir engineering as a secondary strength. Project 2 (SRP diagnostics) picks up directly where this well's natural-flow runway ends.
