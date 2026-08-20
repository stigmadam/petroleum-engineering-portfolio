# 04 — CO2-EOR Sensitivity Analysis via Design of Experiments

An independent Python reproduction of undergraduate thesis research (ITB Petroleum Engineering, 2025), rebuilt from raw experimental data — not from the thesis's Minitab output — plus an honest, data-only extension addressing the model-validity problem the thesis identified.

**➡️ [Read the full report](report.md)**

## Key result
Independently reproduced the thesis's DOE analysis in Python from the raw 64-run-per-field simulation matrices (192 runs total across 3 fields), matching the original Minitab-reported standardized effects almost exactly (e.g. Field X: B=57.58 vs. thesis's ≈57). Confirmed the central finding — **Pattern Area, Porosity, and Thickness dominate CO2-EOR recovery regardless of depositional environment** — and extended the thesis's "future work" recommendation (RSM) with a data-only log-transform test: it **fixes the residual/heteroscedasticity problem for Fields X and Z but not Field Y**, a genuinely useful negative result that sharpens where a full RSM study is actually needed.

## Structure
```
04_CO2_EOR_DOE/
├── README.md
├── report.md                          <- full write-up (start here)
├── data/
│   ├── field_X.csv                     <- raw 64-run DOE matrix, transcribed from thesis Table 7
│   ├── field_Y.csv                     <- Table 8
│   └── field_Z.csv                     <- Table 9
├── src/
│   ├── doe_engine.py                   <- orthogonal factorial design, effect estimation, error pooling
│   ├── transform_remedy.py             <- log-transform variance-stabilization test
│   ├── plots.py                        <- Pareto chart + residual diagnostic plotting
│   └── run_analysis.py                 <- runs all 3 fields, generates plots + results_summary.json
└── outputs/
    ├── pareto_X.png / Y / Z
    ├── residuals_X.png / Y / Z (+ _logtransform versions)
    ├── comparison_top5_effects.png
    └── results_summary.json
```

## Run it yourself
```bash
pip install pandas numpy scipy matplotlib
python src/run_analysis.py
```

## Method summary
- **Design:** 2⁶ full factorial, 64 runs/field, no replicates — factor levels verified empirically from raw data rather than assumed from the thesis's narrative tables.
- **Effect estimation:** exact orthogonal-design solution; 3-way+ interactions (42 terms) pooled as pure error, giving the same 42 error d.f. / t=2.018 threshold the thesis reports.
- **Validation:** reproduced standardized effects checked directly against the thesis's reported Pareto chart values before drawing any further conclusions.
- **Extension:** log-transform tested as a legitimate, data-only remedy for the heteroscedasticity the thesis found — explicitly does NOT claim to be a full RSM, since a 2-level design can't estimate curvature; the report states exactly what a true RSM would additionally require.

## Part of a larger portfolio
This is Project 4, rounding out the reservoir-engineering side of the portfolio (Projects 1-3 focus on production/artificial lift/economics). Unlike Projects 1-3, this one uses **real thesis data** rather than synthetic data, and demonstrates independent statistical reproduction as a skill in its own right.
