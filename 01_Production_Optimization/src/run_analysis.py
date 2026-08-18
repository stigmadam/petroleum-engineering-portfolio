"""
run_analysis.py
----------------
Main driver: builds the base-case IPR & VLP curves, solves the nodal
operating point, runs sensitivity cases (tubing size, WHP, water cut,
reservoir depletion), and saves all plots + a results summary.
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data"))

import model
from well_A01 import WELL

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                      "grid.alpha": 0.3})

results = {}

# ---------------------------------------------------------- BASE CASE ----
PR = WELL["reservoir_pressure_psi"]
PB = WELL["bubble_point_psi"]
J = model.calibrate_pi(PR, PB, WELL["test_pwf_psi"], WELL["test_qo_stb_d"])
results["productivity_index_stb_d_psi"] = round(J, 4)

pwf_ipr, q_ipr = model.ipr_curve(PR, PB, J)
q_vlp, pwf_vlp = model.vlp_curve(WELL)

q_op, pwf_op = model.find_operating_point(WELL, J, PR, PB)
results["base_case_operating_point"] = dict(
    qo_stb_d=round(q_op, 1), pwf_psi=round(pwf_op, 1)
)

print(f"Productivity Index J = {J:.4f} STB/d/psi")
print(f"Base case operating point: Qo = {q_op:.1f} STB/d @ Pwf = {pwf_op:.0f} psia")

plt.figure(figsize=(7, 5))
plt.plot(q_ipr, pwf_ipr, label="IPR (composite: linear + Vogel)", lw=2, color="#1f6f4a")
plt.plot(q_vlp, pwf_vlp, label="VLP (tubing 2-7/8\", THP=150 psi)", lw=2, color="#c2542c")
plt.scatter([q_op], [pwf_op], color="black", zorder=5, s=55,
            label=f"Operating point: {q_op:.0f} STB/d @ {pwf_op:.0f} psi")
plt.axhline(PB, color="gray", ls="--", lw=1, label=f"Bubble point ({PB:.0f} psi)")
plt.xlabel("Oil Rate, STB/d")
plt.ylabel("Flowing Bottomhole Pressure, psia")
plt.title("Well A-01 — Base Case Nodal Analysis (IPR vs. VLP)")
plt.legend(fontsize=8, loc="upper right")
plt.xlim(0, 750)
plt.ylim(0, PR * 1.05)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "01_base_case_nodal.png"))
plt.close()

# --------------------------------------------------- SENSITIVITY: TUBING -
tubing_options = {"2-3/8\" (1.995 in ID)": 1.995,
                   "2-7/8\" (2.441 in ID) - base": 2.441,
                   "3-1/2\" (2.992 in ID)": 2.992}

plt.figure(figsize=(7, 5))
plt.plot(q_ipr, pwf_ipr, label="IPR", lw=2, color="#1f6f4a")
tubing_results = {}
for label, dia in tubing_options.items():
    w = dict(WELL)
    w["tubing_id_in"] = dia
    qv, pv = model.vlp_curve(w)
    q_o, pwf_o = model.find_operating_point(w, J, PR, PB)
    tubing_results[label] = round(q_o, 1)
    plt.plot(qv, pv, lw=1.6, label=f"VLP {label}")
    plt.scatter([q_o], [pwf_o], zorder=5, s=40)
results["tubing_sensitivity_stb_d"] = tubing_results
plt.xlabel("Oil Rate, STB/d")
plt.ylabel("Flowing Bottomhole Pressure, psia")
plt.title("Sensitivity: Tubing Size")
plt.legend(fontsize=8)
plt.xlim(0, 750)
plt.ylim(0, PR * 1.05)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "02_sensitivity_tubing.png"))
plt.close()

# ------------------------------------------------------- SENSITIVITY: WHP-
whp_options = [100, 150, 200, 300]
plt.figure(figsize=(7, 5))
plt.plot(q_ipr, pwf_ipr, label="IPR", lw=2, color="#1f6f4a")
whp_results = {}
for whp in whp_options:
    qv, pv = model.vlp_curve(WELL, thp_override=whp)
    q_o, pwf_o = model.find_operating_point(WELL, J, PR, PB, thp_override=whp)
    whp_results[f"{whp} psi"] = round(q_o, 1) if q_o else None
    plt.plot(qv, pv, lw=1.6, label=f"VLP, THP={whp} psi")
    if q_o:
        plt.scatter([q_o], [pwf_o], zorder=5, s=40)
results["whp_sensitivity_stb_d"] = whp_results
plt.xlabel("Oil Rate, STB/d")
plt.ylabel("Flowing Bottomhole Pressure, psia")
plt.title("Sensitivity: Wellhead / Separator Pressure")
plt.legend(fontsize=8)
plt.xlim(0, 750)
plt.ylim(0, PR * 1.05)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "03_sensitivity_whp.png"))
plt.close()

# ------------------------------------------------- SENSITIVITY: WATER CUT-
wc_options = [0.35, 0.50, 0.65, 0.80]
plt.figure(figsize=(7, 5))
plt.plot(q_ipr, pwf_ipr, label="IPR", lw=2, color="#1f6f4a")
wc_results = {}
for wc in wc_options:
    w = dict(WELL)
    w["water_cut"] = wc
    qv, pv = model.vlp_curve(w)
    q_o, pwf_o = model.find_operating_point(w, J, PR, PB)
    wc_results[f"{int(wc*100)}%"] = round(q_o, 1) if q_o else None
    plt.plot(qv, pv, lw=1.6, label=f"VLP, WC={int(wc*100)}%")
    if q_o:
        plt.scatter([q_o], [pwf_o], zorder=5, s=40)
results["water_cut_sensitivity_stb_d"] = wc_results
plt.xlabel("Oil Rate, STB/d")
plt.ylabel("Flowing Bottomhole Pressure, psia")
plt.title("Sensitivity: Water Cut Increase (Waterflood-Driven)")
plt.legend(fontsize=8)
plt.xlim(0, 750)
plt.ylim(0, PR * 1.05)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "04_sensitivity_watercut.png"))
plt.close()

# --------------------------------------------- SENSITIVITY: RESERVOIR DEPL
pr_options = [1800, 1600, 1400, 1200]
plt.figure(figsize=(7, 5))
q_vlp_base, pwf_vlp_base = model.vlp_curve(WELL)
plt.plot(q_vlp_base, pwf_vlp_base, label="VLP (base case)", lw=2, color="#c2542c")
depletion_results = {}
for pr_i in pr_options:
    pwf_i, q_i = model.ipr_curve(pr_i, PB, J)
    q_o, pwf_o = model.find_operating_point(WELL, J, pr_i, PB)
    depletion_results[f"Pr={pr_i} psi"] = round(q_o, 1) if q_o else 0.0
    plt.plot(q_i, pwf_i, lw=1.6, ls="--", label=f"IPR, Pr={pr_i} psi")
    if q_o:
        plt.scatter([q_o], [pwf_o], zorder=5, s=40)
results["reservoir_depletion_sensitivity_stb_d"] = depletion_results
plt.xlabel("Oil Rate, STB/d")
plt.ylabel("Flowing Bottomhole Pressure, psia")
plt.title("Sensitivity: Reservoir Pressure Depletion Over Field Life")
plt.legend(fontsize=8)
plt.xlim(0, 750)
plt.ylim(0, 1900)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "05_sensitivity_depletion.png"))
plt.close()

with open(os.path.join(OUT, "results_summary.json"), "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
print("\nAll plots + results_summary.json written to:", OUT)
