"""
build_dashboard_data.py
------------------------
Analysis layer: computes field-level aggregates, well ranking/status
classification, and rule-based anomaly detection from the raw time series -
the same output a real surveillance system would produce, consumed by the
dashboard as a single embedded JSON payload.
"""

import json
import os
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "wells_timeseries.json")) as f:
    series = json.load(f)

N_MONTHS = len(next(iter(series.values()))["month"])
well_names = sorted(series.keys())

# ---------------------------------------------------------------- anomaly detection
def detect_anomalies(name, s):
    events = []
    oil = np.array(s["oil_bopd"])
    wc = np.array(s["water_cut"])
    gor = np.array(s["gor_scf_stb"])
    eff = s["pump_efficiency"]

    for m in range(1, N_MONTHS):
        # sudden oil rate drop month-over-month beyond expected decline noise
        pct_change = (oil[m] - oil[m - 1]) / oil[m - 1] if oil[m - 1] > 0 else 0
        if pct_change < -0.25:
            events.append(dict(well=name, month=m, type="Rate Drop",
                                severity="Critical", detail=f"Oil rate fell {abs(pct_change)*100:.0f}% month-over-month"))
        # water cut jump
        wc_change = wc[m] - wc[m - 1]
        if wc_change > 0.08:
            events.append(dict(well=name, month=m, type="Water Cut Spike",
                                severity="Warning", detail=f"Water cut jumped {wc_change*100:.1f} pts"))
        # GOR jump (gas breakout)
        gor_change = gor[m] - gor[m - 1]
        if gor_change > 150:
            events.append(dict(well=name, month=m, type="GOR Increase",
                                severity="Warning", detail=f"GOR increased {gor_change:.0f} scf/stb"))
        # pump efficiency collapse
        if eff[m] is not None and eff[m - 1] is not None:
            eff_change = eff[m] - eff[m - 1]
            if eff_change < -0.15:
                events.append(dict(well=name, month=m, type="Pump Efficiency Drop",
                                    severity="Critical", detail=f"Pump efficiency fell {abs(eff_change)*100:.0f} pts"))
    return events

all_anomalies = []
for name in well_names:
    all_anomalies.extend(detect_anomalies(name, series[name]))
all_anomalies.sort(key=lambda e: e["month"], reverse=True)

# ---------------------------------------------------------------- well ranking / status
wells_summary = []
for name in well_names:
    s = series[name]
    oil = np.array(s["oil_bopd"])
    current = oil[-1]
    three_mo_ago = oil[-4] if len(oil) >= 4 else oil[0]
    pct_3mo = (current - three_mo_ago) / three_mo_ago * 100 if three_mo_ago > 0 else 0
    wc_current = s["water_cut"][-1]
    n_events = sum(1 for e in all_anomalies if e["well"] == name)
    last_event_month = max([e["month"] for e in all_anomalies if e["well"] == name], default=None)

    if n_events > 0 and last_event_month is not None and last_event_month >= N_MONTHS - 6:
        status = "Critical" if any(e["severity"] == "Critical" for e in all_anomalies
                                     if e["well"] == name and e["month"] == last_event_month) else "Watch"
    elif pct_3mo < -15:
        status = "Watch"
    else:
        status = "Normal"

    wells_summary.append(dict(
        name=name, lift_type=s["lift_type"], current_oil_bopd=round(current, 1),
        pct_change_3mo=round(pct_3mo, 1), water_cut_pct=round(wc_current * 100, 1),
        status=status, n_anomalies=n_events,
    ))

wells_summary.sort(key=lambda w: w["current_oil_bopd"], reverse=True)

# ---------------------------------------------------------------- field aggregates
field_monthly = []
for m in range(N_MONTHS):
    total_oil = sum(series[n]["oil_bopd"][m] for n in well_names)
    total_water = sum(series[n]["water_bwpd"][m] for n in well_names)
    total_gas = sum(series[n]["gas_mscfd"][m] for n in well_names)
    avg_wc = sum(series[n]["water_cut"][m] for n in well_names) / len(well_names)
    field_monthly.append(dict(month=m, total_oil_bopd=round(total_oil, 1),
                               total_water_bwpd=round(total_water, 1),
                               total_gas_mscfd=round(total_gas, 1),
                               avg_water_cut_pct=round(avg_wc * 100, 1)))

kpis = dict(
    total_wells=len(well_names),
    field_oil_now=round(field_monthly[-1]["total_oil_bopd"], 0),
    field_oil_change_pct=round((field_monthly[-1]["total_oil_bopd"] - field_monthly[-7]["total_oil_bopd"])
                                 / field_monthly[-7]["total_oil_bopd"] * 100, 1),
    avg_water_cut=field_monthly[-1]["avg_water_cut_pct"],
    n_normal=sum(1 for w in wells_summary if w["status"] == "Normal"),
    n_watch=sum(1 for w in wells_summary if w["status"] == "Watch"),
    n_critical=sum(1 for w in wells_summary if w["status"] == "Critical"),
    n_anomalies_total=len(all_anomalies),
)

dashboard_data = dict(
    kpis=kpis,
    field_monthly=field_monthly,
    wells_summary=wells_summary,
    anomalies=all_anomalies,
    well_series=series,
    n_months=N_MONTHS,
)

OUT = os.path.join(DATA_DIR, "dashboard_data.json")
with open(OUT, "w") as f:
    json.dump(dashboard_data, f)

print("KPIs:", json.dumps(kpis, indent=2))
print(f"\nTotal anomaly events detected: {len(all_anomalies)}")
print(f"Wrote consolidated dashboard data -> {OUT}")
