"""
generate_data.py
-----------------
Generates a synthetic 18-well production surveillance dataset: weekly time
series (52 weeks) of oil rate, water cut, GOR, and pump efficiency, with
distinct "stories" per well (normal decline, water breakthrough, gas
breakthrough, artificial lift degradation, workover recovery, stable/healthy)
so the dashboard has genuine variety to surface.

A rule-based attention classifier (Normal / Watch / Critical) is computed
from the trailing trend of each well - mirroring the kind of surveillance
logic a real production engineer applies, and consistent with the
diagnostic framing used in Projects 1-3 of this portfolio.
"""

import numpy as np
import json
import os

rng = np.random.default_rng(42)
N_WEEKS = 52

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUT, exist_ok=True)


def base_decline(q0, decline_annual, weeks, noise=0.02):
    t = np.arange(weeks) / 52.0
    q = q0 * np.exp(-decline_annual * t)
    q = q * (1 + rng.normal(0, noise, weeks))
    return np.clip(q, 0, None)


def ramp(start, end, weeks, start_week=0, curve="linear"):
    prof = np.full(weeks, start, dtype=float)
    active = weeks - start_week
    if curve == "linear":
        prof[start_week:] = np.linspace(start, end, active)
    elif curve == "sigmoid":
        x = np.linspace(-6, 6, active)
        prof[start_week:] = start + (end - start) / (1 + np.exp(-x))
    return prof


WELLS = []

def add_well(name, story, q0, decline, wc_profile, gor_profile, pump_eff_profile=None, artificial_lift=False):
    oil = base_decline(q0, decline, N_WEEKS)
    wc = np.clip(wc_profile, 0, 0.97)
    gor = gor_profile
    pump_eff = pump_eff_profile if pump_eff_profile is not None else np.full(N_WEEKS, np.nan)
    WELLS.append(dict(name=name, story=story, artificial_lift=artificial_lift,
                       oil_bopd=oil, water_cut=wc, gor_scf_stb=gor, pump_eff_pct=pump_eff))


# --- Field A: naturally flowing wells (some healthy, some declining) ---
add_well("A-01", "Stable, healthy natural flow", 410, 0.10,
          wc_profile=np.clip(0.30 + rng.normal(0, 0.01, N_WEEKS), 0, 1),
          gor_profile=520 + rng.normal(0, 8, N_WEEKS))

add_well("A-02", "Normal mature decline", 260, 0.35,
          wc_profile=np.clip(ramp(0.45, 0.52, N_WEEKS) + rng.normal(0, 0.012, N_WEEKS), 0, 1),
          gor_profile=610 + rng.normal(0, 10, N_WEEKS))

add_well("A-03", "Water breakthrough — rising water cut", 340, 0.18,
          wc_profile=np.clip(ramp(0.35, 0.78, N_WEEKS, start_week=8, curve="sigmoid") + rng.normal(0, 0.01, N_WEEKS), 0, 1),
          gor_profile=470 + rng.normal(0, 9, N_WEEKS))

add_well("A-04", "Gas breakthrough — rising GOR", 300, 0.20,
          wc_profile=np.clip(0.28 + rng.normal(0, 0.012, N_WEEKS), 0, 1),
          gor_profile=ramp(480, 1650, N_WEEKS, start_week=14, curve="sigmoid") + rng.normal(0, 15, N_WEEKS))

add_well("A-05", "Stable, moderate decline", 195, 0.22,
          wc_profile=np.clip(0.40 + rng.normal(0, 0.015, N_WEEKS), 0, 1),
          gor_profile=550 + rng.normal(0, 10, N_WEEKS))

add_well("A-06", "Severe water breakthrough — near economic limit", 220, 0.15,
          wc_profile=np.clip(ramp(0.50, 0.91, N_WEEKS, start_week=4, curve="linear") + rng.normal(0, 0.01, N_WEEKS), 0, 1),
          gor_profile=430 + rng.normal(0, 8, N_WEEKS))

add_well("A-07", "Healthy, low decline", 155, 0.08,
          wc_profile=np.clip(0.22 + rng.normal(0, 0.01, N_WEEKS), 0, 1),
          gor_profile=505 + rng.normal(0, 7, N_WEEKS))

# --- Field B: SRP artificial-lift wells (ties to Project 2) ---
add_well("B-01", "SRP — stable, well-maintained", 118, 0.12,
          wc_profile=np.clip(0.38 + rng.normal(0, 0.012, N_WEEKS), 0, 1),
          gor_profile=390 + rng.normal(0, 7, N_WEEKS),
          pump_eff_profile=np.clip(94 + rng.normal(0, 1.5, N_WEEKS), 0, 100), artificial_lift=True)

add_well("B-02", "SRP — gas interference, declining efficiency", 95, 0.10,
          wc_profile=np.clip(0.33 + rng.normal(0, 0.012, N_WEEKS), 0, 1),
          gor_profile=610 + rng.normal(0, 10, N_WEEKS),
          pump_eff_profile=np.clip(ramp(88, 39, N_WEEKS, start_week=10, curve="sigmoid") + rng.normal(0, 1.5, N_WEEKS), 0, 100),
          artificial_lift=True)

add_well("B-03", "SRP — fluid pound, worsening", 88, 0.14,
          wc_profile=np.clip(0.41 + rng.normal(0, 0.012, N_WEEKS), 0, 1),
          gor_profile=455 + rng.normal(0, 8, N_WEEKS),
          pump_eff_profile=np.clip(ramp(82, 37, N_WEEKS, start_week=18, curve="linear") + rng.normal(0, 1.5, N_WEEKS), 0, 100),
          artificial_lift=True)

add_well("B-04", "SRP — mechanical failure (sudden)", 132, 0.10,
          wc_profile=np.clip(0.36 + rng.normal(0, 0.01, N_WEEKS), 0, 1),
          gor_profile=400 + rng.normal(0, 7, N_WEEKS),
          pump_eff_profile=np.concatenate([np.clip(95 + rng.normal(0, 1.5, 38), 0, 100),
                                             np.clip(6 + rng.normal(0, 1.5, N_WEEKS - 38), 0, 100)]),
          artificial_lift=True)

add_well("B-05", "SRP — worn traveling valve, gradual efficiency loss", 101, 0.12,
          wc_profile=np.clip(0.39 + rng.normal(0, 0.012, N_WEEKS), 0, 1),
          gor_profile=470 + rng.normal(0, 8, N_WEEKS),
          pump_eff_profile=np.clip(ramp(90, 41, N_WEEKS, start_week=6, curve="linear") + rng.normal(0, 1.5, N_WEEKS), 0, 100),
          artificial_lift=True)

add_well("B-06", "SRP — recently worked over, recovering", 145, 0.10,
          wc_profile=np.clip(0.34 + rng.normal(0, 0.012, N_WEEKS), 0, 1),
          gor_profile=420 + rng.normal(0, 7, N_WEEKS),
          pump_eff_profile=np.clip(ramp(35, 92, N_WEEKS, start_week=2, curve="sigmoid") + rng.normal(0, 1.5, N_WEEKS), 0, 100),
          artificial_lift=True)

add_well("B-07", "SRP — stable", 76, 0.09,
          wc_profile=np.clip(0.44 + rng.normal(0, 0.012, N_WEEKS), 0, 1),
          gor_profile=380 + rng.normal(0, 6, N_WEEKS),
          pump_eff_profile=np.clip(91 + rng.normal(0, 1.5, N_WEEKS), 0, 100), artificial_lift=True)

# --- Field C: mixed mature wells ---
add_well("C-01", "Mature, stable", 168, 0.16,
          wc_profile=np.clip(0.48 + rng.normal(0, 0.013, N_WEEKS), 0, 1),
          gor_profile=505 + rng.normal(0, 9, N_WEEKS))

add_well("C-02", "Mature, accelerating decline", 142, 0.42,
          wc_profile=np.clip(ramp(0.50, 0.61, N_WEEKS) + rng.normal(0, 0.014, N_WEEKS), 0, 1),
          gor_profile=540 + rng.normal(0, 10, N_WEEKS))

add_well("C-03", "Mature, near end of economic life", 58, 0.30,
          wc_profile=np.clip(ramp(0.68, 0.85, N_WEEKS) + rng.normal(0, 0.014, N_WEEKS), 0, 1),
          gor_profile=495 + rng.normal(0, 9, N_WEEKS))

add_well("C-04", "Recently completed, high rate", 480, 0.15,
          wc_profile=np.clip(0.18 + rng.normal(0, 0.01, N_WEEKS), 0, 1),
          gor_profile=560 + rng.normal(0, 10, N_WEEKS))


# ------------------------------------------------------- attention scoring
def classify_well(well):
    oil = well["oil_bopd"]
    wc = well["water_cut"]
    gor = well["gor_scf_stb"]
    pump_eff = well["pump_eff_pct"]

    oil_trend = (oil[-6:].mean() - oil[-18:-12].mean()) / max(oil[-18:-12].mean(), 1e-6)
    wc_trend = wc[-6:].mean() - wc[-18:-12].mean()
    wc_level = wc[-4:].mean()
    gor_ratio = gor[-4:].mean() / max(gor[:8].mean(), 1e-6)

    reasons = []
    score = 0

    if wc_level > 0.82:
        score += 3
        reasons.append(f"Water cut critically high ({wc_level*100:.0f}%) — near economic limit")
    elif wc_level > 0.65:
        score += 2
        reasons.append(f"Water cut high ({wc_level*100:.0f}%)")
    elif wc_trend > 0.12:
        score += 1
        reasons.append(f"Water cut rising fast (+{wc_trend*100:.0f} pts/qtr)")

    if oil_trend < -0.30:
        score += 2
        reasons.append(f"Oil rate dropped {oil_trend*100:.0f}% recently")
    elif oil_trend < -0.15:
        score += 1
        reasons.append(f"Oil rate declining ({oil_trend*100:.0f}% recently)")

    if gor_ratio > 2.5:
        score += 2
        reasons.append(f"GOR risen sharply ({gor_ratio:.1f}x baseline) — possible gas breakthrough")
    elif gor_ratio > 1.5:
        score += 1
        reasons.append(f"GOR trending up ({gor_ratio:.1f}x baseline)")

    if well["artificial_lift"] and not np.isnan(pump_eff).all():
        eff_level = pump_eff[-4:].mean()
        eff_trend = pump_eff[-6:].mean() - pump_eff[-18:-12].mean()
        if eff_level < 20:
            score += 3
            reasons.append(f"Pump efficiency critical ({eff_level:.0f}%) — possible mechanical failure")
        elif eff_level < 50:
            score += 2
            reasons.append(f"Pump efficiency low ({eff_level:.0f}%)")
        elif eff_trend < -15:
            score += 1
            reasons.append(f"Pump efficiency declining ({eff_trend:.0f} pts/qtr)")

    if score >= 3:
        status = "Critical"
    elif score >= 1:
        status = "Watch"
    else:
        status = "Normal"
        if not reasons:
            reasons.append("No significant anomalies detected")

    return status, reasons


records = []
for w in WELLS:
    status, reasons = classify_well(w)
    records.append(dict(
        name=w["name"], story=w["story"], artificial_lift=w["artificial_lift"],
        status=status, reasons=reasons,
        oil_bopd=[round(x, 1) for x in w["oil_bopd"]],
        water_cut=[round(x, 4) for x in w["water_cut"]],
        gor_scf_stb=[round(x, 1) for x in w["gor_scf_stb"]],
        pump_eff_pct=[None if np.isnan(x) else round(x, 1) for x in w["pump_eff_pct"]],
        current_oil_bopd=round(w["oil_bopd"][-1], 1),
        current_water_cut=round(w["water_cut"][-1], 3),
        current_gor=round(w["gor_scf_stb"][-1], 0),
        current_pump_eff=None if np.isnan(w["pump_eff_pct"][-1]) else round(w["pump_eff_pct"][-1], 1),
    ))

with open(os.path.join(OUT, "wells_data.json"), "w") as f:
    json.dump(records, f, indent=2)

print(f"Generated {len(records)} wells, {N_WEEKS} weeks each.")
for r in records:
    print(f"  {r['name']:5s} | {r['status']:8s} | oil={r['current_oil_bopd']:6.1f} bopd | "
          f"wc={r['current_water_cut']*100:4.0f}% | {r['story']}")
