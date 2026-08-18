"""
run_analysis.py
----------------
Fleet-level SRP surveillance: generates a dynamometer card for each well,
extracts features, diagnoses the failure mode (blind to the "true" label
used to generate the card), computes theoretical vs. actual pump
displacement, and ranks wells by lost production for intervention priority.
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data"))

from dyno_card import generate_card
import diagnostics as diag
from srp_wells import WELLS

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                      "grid.alpha": 0.3})


def pump_displacement_bopd(stroke_in, spm, plunger_diam_in):
    """API-style theoretical pump displacement, bbl/day."""
    return 0.1166 * stroke_in * spm * plunger_diam_in ** 2


# --------------------------------------------------------- run the fleet -
fleet_results = []
fig, axes = plt.subplots(2, 3, figsize=(15, 9))
axes = axes.flatten()

for ax, well in zip(axes, WELLS):
    position, load = generate_card(
        well["true_condition"], pprl=well["pprl_design"], mprl=well["mprl_design"],
        stroke_in=well["stroke_in"], seed=well["seed"]
    )

    features = diag.extract_features(position, load, well["stroke_in"])
    healthy_range = well["pprl_design"] - well["mprl_design"]
    diagnosis, note, recommendation = diag.diagnose(features, healthy_load_range=healthy_range)

    pd_bopd = pump_displacement_bopd(well["stroke_in"], well["spm"], well["plunger_diam_in"])
    efficiency = well["actual_rate_bopd"] / pd_bopd if pd_bopd > 0 else 0.0
    lost_bopd = max(pd_bopd - well["actual_rate_bopd"], 0.0)

    fleet_results.append(dict(
        well=well["name"],
        diagnosis=diagnosis,
        recommendation=recommendation,
        note=note,
        features=features,
        theoretical_pd_bopd=round(pd_bopd, 1),
        actual_rate_bopd=well["actual_rate_bopd"],
        volumetric_efficiency_pct=round(efficiency * 100, 1),
        lost_production_bopd=round(lost_bopd, 1),
    ))

    ax.plot(position, load, color="#1f6f4a", lw=1.6)
    ax.fill(position, load, color="#1f6f4a", alpha=0.12)
    ax.set_title(f"{well['name']}  —  {diagnosis}", fontsize=10)
    ax.set_xlabel("Position (in)")
    ax.set_ylabel("Load (lbf)")
    ax.text(0.03, 0.05, f"Eff: {efficiency*100:.0f}%  |  Lost: {lost_bopd:.0f} bopd",
            transform=ax.transAxes, fontsize=8.5,
            bbox=dict(facecolor="white", alpha=0.75, edgecolor="none"))

plt.tight_layout()
plt.savefig(os.path.join(OUT, "01_fleet_dynamometer_cards.png"))
plt.close()

# ----------------------------------------------------- priority ranking --
ranked = sorted(fleet_results, key=lambda r: r["lost_production_bopd"], reverse=True)

fig, ax = plt.subplots(figsize=(8, 5))
names = [r["well"] for r in ranked]
lost = [r["lost_production_bopd"] for r in ranked]
colors = ["#c2542c" if r["diagnosis"] != "Normal operation" else "#4c8c6b" for r in ranked]
ax.barh(names[::-1], lost[::-1], color=colors[::-1])
ax.set_xlabel("Lost Production vs. Theoretical Pump Displacement (bbl/d)")
ax.set_title("SRP Fleet — Intervention Priority Ranking")
for i, (n, v) in enumerate(zip(names[::-1], lost[::-1])):
    ax.text(v + 1, i, f"{v:.0f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "02_intervention_priority_ranking.png"))
plt.close()

# ------------------------------------------------- classifier accuracy check
# map diagnosis strings back to condition keys for a simple accuracy check
label_map = {
    "Normal operation": "normal",
    "Gas interference": "gas_interference",
    "Fluid pound (pump-off / low fluid level)": "fluid_pound",
    "Worn / leaking traveling valve": "worn_traveling_valve",
    "Parted rod / stuck pump (mechanical failure)": "parted_rod",
}
n_correct = sum(1 for w, r in zip(WELLS, fleet_results)
                if label_map.get(r["diagnosis"]) == w["true_condition"])
accuracy = n_correct / len(WELLS)

summary = dict(
    fleet_results=fleet_results,
    ranked_priority=[r["well"] for r in ranked],
    classifier_accuracy_on_synthetic_fleet=f"{n_correct}/{len(WELLS)} ({accuracy*100:.0f}%)",
)

with open(os.path.join(OUT, "results_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print(f"Classifier accuracy on synthetic fleet: {n_correct}/{len(WELLS)}")
for r in ranked:
    print(f"  {r['well']:5s} | {r['diagnosis']:42s} | eff={r['volumetric_efficiency_pct']:5.1f}% "
          f"| lost={r['lost_production_bopd']:6.1f} bopd")
print("\nAll plots + results_summary.json written to:", OUT)
