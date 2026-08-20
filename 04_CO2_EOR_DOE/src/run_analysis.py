"""
run_analysis.py
----------------
Runs the full DOE reproduction + residual diagnostics + log-transform
remedy for all 3 fields (X, Y, Z) from the raw thesis data, generates all
plots, and writes results_summary.json.
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))

import doe_engine as doe
import plots as pl
import transform_remedy as remedy

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
OUT = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True, "grid.alpha": 0.3})

FIELDS = ["X", "Y", "Z"]
field_results = {}
summary = {"fields": {}}

for field in FIELDS:
    df = doe.load_field(os.path.join(DATA, f"field_{field}.csv"))
    res = doe.fit_and_rank_effects(df)
    field_results[field] = res

    pl.pareto_chart(res["effects_table"], res["t_crit"], field,
                     os.path.join(OUT, f"pareto_{field}.png"))
    pl.residual_diagnostics(res["resid_std"], res["fitted"], field,
                             os.path.join(OUT, f"residuals_{field}.png"))

    # --- log-transform remedy ---
    res_log = remedy.log_transform_and_refit(df, doe)
    pl.residual_diagnostics(res_log["resid_std"], res_log["fitted"], f"{field} (log-transformed Np)",
                             os.path.join(OUT, f"residuals_{field}_logtransform.png"))

    var_check_raw = remedy.variance_ratio_check(res["resid_std"], res["fitted"])
    var_check_log = remedy.variance_ratio_check(res_log["resid_std"], res_log["fitted"])
    shapiro_raw = remedy.shapiro_test(res["resid_std"])
    shapiro_log = remedy.shapiro_test(res_log["resid_std"])

    top5 = res["effects_table"][:5]
    summary["fields"][field] = dict(
        levels=res["levels"],
        top5_effects=[dict(term=r["term"], standardized_effect=r["standardized_effect"]) for r in top5],
        t_crit=res["t_crit"],
        n_significant_terms=sum(1 for r in res["effects_table"] if r["significant"]),
        raw_model=dict(shapiro=shapiro_raw, variance_check=var_check_raw),
        log_transformed_model=dict(shapiro=shapiro_log, variance_check=var_check_log),
    )

# comparison chart
pl.comparison_bar(field_results, os.path.join(OUT, "comparison_top5_effects.png"))

with open(os.path.join(OUT, "results_summary.json"), "w") as f:
    json.dump(summary, f, indent=2, default=str)

print(json.dumps(summary, indent=2, default=str))
print("\nAll plots + results_summary.json written to:", OUT)
