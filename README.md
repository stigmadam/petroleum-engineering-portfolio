# Petroleum Engineering Portfolio — David Damanik

Petroleum Engineering graduate (Institut Teknologi Bandung) focused on **production engineering, artificial lift, and well performance**, with hands-on field exposure in well surveillance (Pertamina Hulu Rokan) and well intervention/slickline operations (PT Petrol Pratama Energi).

This repository contains independent case studies built to demonstrate the analytical and commercial thinking expected of a junior production/reservoir engineer — full methodology, working code, and honestly-stated assumptions and limitations in every report. Well and reservoir data are synthetic (built to realistic field ranges) except Project 4, which uses real thesis data; the engineering methods, correlations, and decision frameworks throughout are real.

📧 daviddamanik67@gmail.com | 🔗 [linkedin.com/in/david-damanik](http://linkedin.com/in/david-damanik)

---

## The story across these five projects

They follow one well through its production life, then widen out to the fleet and reservoir level — deliberate, since it shows how production, artificial lift, reservoir engineering, and commercial decision-making connect rather than treating them as separate skills:

**Well A-01 flows naturally →** as reservoir pressure depletes, natural flow becomes uneconomic (quantified in Project 1) **→ converts to sucker-rod-pump artificial lift**, which is then surveilled and diagnosed (Project 2) **→ that diagnosis becomes a funded capital decision** across a wider well fleet, including a genuine slickline-vs-workover trade-off (Project 3). Project 4 goes deep on the reservoir side with real thesis data, and Project 5 zooms back out to a fleet-wide surveillance view tying the whole portfolio's diagnostic vocabulary together.

## Projects

### [01 — Production Optimization (IPR–VLP Nodal Analysis)](01_Production_Optimization/report.md)
Full black-oil PVT correlations, a composite IPR calibrated from a well test, and a multiphase VLP pressure-traverse solver built from scratch in Python. Identifies wellhead backpressure — not tubing size — as the highest-leverage production variable, and quantifies exactly when the well can no longer flow naturally.

### [02 — SRP Diagnostics (Dynamometer Card Analysis)](02_SRP_Optimization/report.md)
A rule-based diagnostic tool that classifies sucker-rod-pump dynamometer cards (gas interference, fluid pound, worn valve, mechanical failure) and converts every diagnosis into a ranked production-loss number. 100% classification accuracy on the synthetic test fleet. Directly extends real SRP well monitoring experience from PHR.

### [03 — Well Intervention Decision Case (Economics)](03_Well_Intervention/report.md)
Turns Project 2's diagnoses into a funded decision: NPV, payout, ROI, and capital-efficiency ranking across candidate interventions, including a genuine slickline-vs-full-workover trade-off that connects directly to real slickline field experience.

### [04 — CO2-EOR Sensitivity Analysis via Design of Experiments](04_CO2_EOR_DOE/report.md)
Independent Python reproduction of undergraduate thesis research, rebuilt from raw experimental data (not the original Minitab output), matching the thesis's reported standardized effects almost exactly. Extends the thesis's own "future work" recommendation with a log-transform remedy for model heteroscedasticity — fixing it for two of three fields and pinpointing exactly which field still needs full RSM study.

### [05 — Production Surveillance Dashboard](05_Production_Dashboard/report.md)
A standalone, interactive fleet-surveillance dashboard for an 18-well field — no installation, no server, opens directly in any browser. Rule-based attention classifier (consistent with Projects 1–3's diagnostic vocabulary) surfaces which wells need attention today, with inline sparklines and click-to-expand trend charts. **[Open the live dashboard →](https://stigmadam.github.io/petroleum-engineering-portfolio/05_Production_Dashboard/outputs/index.html)**

---

## Skills demonstrated
`Python` (NumPy, SciPy, Pandas, Matplotlib) · Black-oil PVT correlations (Standing, Vasquez-Beggs, Beggs-Robinson, Lee) · Nodal analysis (IPR/VLP) · Artificial lift diagnostics · Discounted cashflow economics · Design of Experiments & statistical modeling · HTML/CSS/JavaScript dashboard development · Technical writing

---
*Each project folder contains its own `report.md` (full write-up), `src/` (working code), and `outputs/` (generated figures + results). Run instructions are in each project's README.*
