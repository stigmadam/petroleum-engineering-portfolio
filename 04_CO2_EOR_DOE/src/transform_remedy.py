"""
transform_remedy.py
--------------------
The thesis identified non-normal, heteroscedastic residuals (a classic
"funnel" pattern - variance growing with fitted value) and recommended
Response Surface Methodology (RSM) as future work to fix this.

A TRUE quadratic RSM (e.g. Central Composite Design) cannot be fit with the
existing dataset: a 2-level design has no center/axial points, so curvature
(x^2 terms) is mathematically inestimable from this data - fitting a "fake"
RSM would misrepresent what a 2-level factorial can support.

What CAN be legitimately done with only the existing 64-run dataset is a
variance-stabilizing transformation. A funnel-shaped residual pattern
(variance increasing with the response magnitude) is the textbook signature
for applying a Box-Cox transform - most simply, a log transform - BEFORE
refitting the same linear model. This is tested here as a lightweight,
honest first step, with the report explicitly stating what a full RSM
would additionally require (new simulation runs at center/axial points).
"""

import numpy as np
from scipy import stats


def log_transform_and_refit(df, doe_engine_module):
    """Refit the same main+2-way model on log(Np) and return diagnostics for comparison."""
    df_log = df.copy()
    df_log["Np"] = np.log(df["Np"])
    res_log = doe_engine_module.fit_and_rank_effects(df_log)
    return res_log


def variance_ratio_check(resid_std, fitted, n_bins=4):
    """
    Quantifies the heteroscedasticity funnel: splits fitted values into bins
    and compares residual variance across bins (max/min ratio - closer to 1
    is better / more constant variance).
    """
    order = np.argsort(fitted)
    fitted_sorted = np.array(fitted)[order]
    resid_sorted = np.array(resid_std)[order]
    bin_edges = np.array_split(np.arange(len(fitted_sorted)), n_bins)
    variances = [resid_sorted[idx].var() for idx in bin_edges]
    ratio = max(variances) / min(variances) if min(variances) > 0 else np.inf
    return dict(bin_variances=[round(v, 3) for v in variances], variance_ratio=round(ratio, 2))


def shapiro_test(resid_std):
    stat, p = stats.shapiro(resid_std)
    return dict(shapiro_stat=round(stat, 4), p_value=round(p, 5), normal_at_5pct=p > 0.05)
