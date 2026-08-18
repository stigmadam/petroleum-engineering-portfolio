# Petroleum Engineering Portfolio — David Damanik

Petroleum Engineering graduate (Institut Teknologi Bandung) focused on **production engineering, artificial lift, and well performance**, with hands-on field exposure in well surveillance (Pertamina Hulu Rokan) and well intervention/slickline operations (PT Petrol Pratama Energi).

This repository contains independent case studies built to demonstrate the analytical and commercial thinking expected of a junior production/reservoir engineer — full methodology, working code, and honestly-stated assumptions and limitations in every report. Well and reservoir data are synthetic (built to realistic field ranges); the engineering methods, correlations, and decision frameworks are real.

📧 daviddamanik67@gmail.com | 🔗 [linkedin.com/in/david-damanik](http://linkedin.com/in/david-damanik)

---

## The story across these three projects

They follow one well through its production life, which is deliberate — it shows how production, artificial lift, and commercial decision-making connect rather than treating them as separate skills:

**Well A-01 flows naturally →** as reservoir pressure depletes, natural flow becomes uneconomic (quantified in Project 1) **→ converts to sucker-rod-pump artificial lift**, which is then surveilled and diagnosed (Project 2) **→ that diagnosis becomes a funded capital decision** across a wider well fleet, including a genuine slickline-vs-workover trade-off (Project 3).

## Projects

### [01 — Production Optimization (IPR–VLP Nodal Analysis)](01_Production_Optimization/report.md)
Full black-oil PVT correlations, a composite IPR calibrated from a well test, and a multiphase VLP pressure-traverse solver built from scratch in Python. Identifies wellhead backpressure — not tubing size — as the highest-leverage production variable, and quantifies exactly when the well can no longer flow naturally.

### [02 — SRP Diagnostics (Dynamometer Card Analysis)](02_SRP_Optimization/report.md)
A rule-based diagnostic tool that classifies sucker-rod-pump dynamometer cards (gas interference, fluid pound, worn valve, mechanical failure) and converts every diagnosis into a ranked production-loss number. 100% classification accuracy on the synthetic test fleet. Directly extends real SRP well monitoring experience from PHR.

### [03 — Well Intervention Decision Case (Economics)](03_Well_Intervention/report.md)
Turns Project 2's diagnoses into a funded decision: NPV, payout, ROI, and capital-efficiency ranking across candidate interventions, including a genuine slickline-vs-full-workover trade-off that connects directly to real slickline field experience.

---

## Skills demonstrated
`Python` (NumPy, SciPy, Matplotlib) · Black-oil PVT correlations (Standing, Vasquez-Beggs, Beggs-Robinson, Lee) · Nodal analysis (IPR/VLP) · Artificial lift diagnostics · Discounted cashflow economics · Technical writing

## Coming next
- **04 — CO2-EOR Optimization via Design of Experiments** (built from undergraduate thesis research)
- **05 — Production Surveillance Dashboard**

---
*Each project folder contains its own `report.md` (full write-up), `src/` (working code), and `outputs/` (generated figures + results). Run instructions are in each project's README.*
