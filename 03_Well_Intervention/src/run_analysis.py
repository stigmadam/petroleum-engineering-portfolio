"""
run_analysis.py
----------------
For each well flagged in Project 2, evaluates every candidate intervention's
economics, recommends the best option per well, and builds a fleet-wide
capital allocation ranking (across ALL wells' non-baseline options) for
prioritizing a limited workover budget.
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data"))

from economics import evaluate_intervention
from interventions import WELLS_FROM_PROJECT2, INTERVENTION_CATALOG, ECON_ASSUMPTIONS

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                      "grid.alpha": 0.3})

all_options = []       # every (well, intervention) pair - for fleet ranking
well_recommendations = []

for well in WELLS_FROM_PROJECT2:
    diag = well["diagnosis"]
    options = INTERVENTION_CATALOG[diag]
    evaluated = []
    for opt in options:
        econ = evaluate_intervention(
            lost_bopd=well["lost_bopd"], cost_usd=opt["cost_usd"],
            recovery_fraction=opt["recovery_fraction"], success_prob=opt["success_prob"],
            econ=ECON_ASSUMPTIONS,
        )
        row = dict(well=well["name"], diagnosis=diag, intervention=opt["name"],
                   cost_usd=opt["cost_usd"], **econ)
        evaluated.append(row)
        if opt["cost_usd"] > 0:  # exclude "Do Nothing" from fleet capital ranking
            all_options.append(row)

    best = max(evaluated, key=lambda r: r["npv_usd"])
    well_recommendations.append(dict(well=well["name"], diagnosis=diag,
                                      recommended_intervention=best["intervention"],
                                      npv_usd=best["npv_usd"], payout_months=best["payout_months"],
                                      roi_pct=best["roi_pct"]))

    # ---- per-well NPV comparison chart ----
    names = [e["intervention"] for e in evaluated]
    npvs = [e["npv_usd"] for e in evaluated]
    colors = ["#4c8c6b" if n == best["intervention"] else "#8a8f98" for n in names]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars = ax.barh(names, npvs, color=colors)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("NPV, USD (12-month horizon)")
    ax.set_title(f"Well {well['name']} — {diag}\nIntervention Economics")
    for b, v in zip(bars, npvs):
        ax.text(v + (2000 if v >= 0 else -2000), b.get_y() + b.get_height() / 2,
                f"${v:,.0f}", va="center", ha="left" if v >= 0 else "right", fontsize=8.5)
    plt.tight_layout()
    fname = f"well_{well['name']}_economics.png"
    plt.savefig(os.path.join(OUT, fname))
    plt.close()

# ------------------------------------------------- fleet capital allocation
all_options_sorted = sorted(all_options, key=lambda r: r["capital_efficiency"], reverse=True)

fig, ax = plt.subplots(figsize=(9, 5.5))
labels = [f"{r['well']}: {r['intervention']}" for r in all_options_sorted]
eff = [r["capital_efficiency"] for r in all_options_sorted]
colors = ["#1f6f4a" if e > 0 else "#c2542c" for e in eff]
ax.barh(labels[::-1], eff[::-1], color=colors[::-1])
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("Capital Efficiency — NPV per $1 invested")
ax.set_title("Fleet-Wide Workover Budget Ranking\n(fund top of list first if capital is limited)")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "00_fleet_capital_allocation_ranking.png"))
plt.close()

# ------------------------------------------------- payout period, recommended options
fig, ax = plt.subplots(figsize=(8, 4.5))
rec_names = [f"{r['well']}: {r['recommended_intervention']}" for r in well_recommendations]
rec_payout = [r["payout_months"] for r in well_recommendations]
ax.barh(rec_names[::-1], rec_payout[::-1], color="#2f6fa8")
ax.set_xlabel("Payout Period, months")
ax.set_title("Recommended Intervention — Payout Speed by Well")
for i, v in enumerate(rec_payout[::-1]):
    ax.text(v + 0.02, i, f"{v:.2f} mo", va="center", fontsize=8.5)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "03_payout_period_recommended.png"))
plt.close()

# ------------------------------------------------- oil price sensitivity (recommended portfolio)
price_cases = [50, 60, 70, 80, 90]
price_sensitivity = []
for price in price_cases:
    econ_case = dict(ECON_ASSUMPTIONS)
    econ_case["oil_price_usd_bbl"] = price
    total_npv = 0.0
    for well in WELLS_FROM_PROJECT2:
        diag = well["diagnosis"]
        rec_name = next(r["recommended_intervention"] for r in well_recommendations if r["well"] == well["name"])
        opt = next(o for o in INTERVENTION_CATALOG[diag] if o["name"] == rec_name)
        econ_result = evaluate_intervention(
            lost_bopd=well["lost_bopd"], cost_usd=opt["cost_usd"],
            recovery_fraction=opt["recovery_fraction"], success_prob=opt["success_prob"],
            econ=econ_case,
        )
        total_npv += econ_result["npv_usd"]
    price_sensitivity.append(round(total_npv, 0))

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(price_cases, price_sensitivity, marker="o", lw=2, color="#c2542c")
ax.axvline(70, color="gray", ls="--", lw=1, label="Base case ($70/bbl)")
ax.set_xlabel("Oil Price Assumption, $/bbl")
ax.set_ylabel("Total Portfolio NPV, USD")
ax.set_title("Oil Price Sensitivity — Recommended Intervention Portfolio")
ax.legend(fontsize=8.5)
ax.ticklabel_format(style="plain", axis="y")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "04_oil_price_sensitivity.png"))
plt.close()

# ------------------------------------------------------------- summary out
summary = dict(
    economic_assumptions=ECON_ASSUMPTIONS,
    well_recommendations=well_recommendations,
    fleet_capital_allocation_ranking=[
        dict(well=r["well"], intervention=r["intervention"], cost_usd=r["cost_usd"],
             npv_usd=r["npv_usd"], capital_efficiency=r["capital_efficiency"],
             payout_months=r["payout_months"])
        for r in all_options_sorted
    ],
    oil_price_sensitivity_usd_npv={f"${p}/bbl": v for p, v in zip(price_cases, price_sensitivity)},
)

with open(os.path.join(OUT, "results_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print("=== Recommended intervention per well ===")
for r in well_recommendations:
    print(f"  {r['well']:5s} | {r['recommended_intervention']:45s} | NPV=${r['npv_usd']:>9,.0f} "
          f"| payout={r['payout_months']} mo | ROI={r['roi_pct']}%")

print("\n=== Fleet capital allocation ranking (fund top first) ===")
for r in all_options_sorted:
    print(f"  {r['well']:5s} | {r['intervention']:45s} | cap.eff={r['capital_efficiency']:5.2f} "
          f"| NPV=${r['npv_usd']:>9,.0f} | cost=${r['cost_usd']:,.0f}")

print("\nAll plots + results_summary.json written to:", OUT)
