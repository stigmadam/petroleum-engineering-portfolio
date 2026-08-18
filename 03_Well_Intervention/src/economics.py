"""
economics.py
------------
Simple, transparent intervention economics: probability-weighted incremental
revenue against a declining production profile, discounted monthly, versus
an upfront job cost.

Convention used:
  - Job cost is incurred in full regardless of outcome (rig/slickline time
    is spent whether or not the job achieves its target recovery).
  - Incremental revenue is the EXPECTED VALUE (success_prob-weighted) of the
    production uplift, declining monthly over the evaluation horizon.
  - Payout period is computed on UNDISCOUNTED cumulative revenue (standard
    field practice) while NPV/ROI use the discounted cashflow.
"""

import numpy as np


def evaluate_intervention(lost_bopd, cost_usd, recovery_fraction, success_prob, econ):
    oil_price = econ["oil_price_usd_bbl"]
    opex = econ["variable_opex_usd_bbl"]
    margin = oil_price - opex
    disc_annual = econ["discount_rate_annual"]
    disc_monthly = (1 + disc_annual) ** (1 / 12) - 1
    decline_m = econ["decline_rate_monthly"]
    n_months = econ["eval_months"]

    incremental_rate_0 = lost_bopd * recovery_fraction  # bopd, if successful

    months = np.arange(1, n_months + 1)
    rate_profile = incremental_rate_0 * (1 - decline_m) ** (months - 1)
    monthly_revenue_gross = rate_profile * 30.4 * margin           # if successful
    monthly_revenue_expected = monthly_revenue_gross * success_prob  # probability-weighted

    discounted = monthly_revenue_expected / (1 + disc_monthly) ** months
    npv = -cost_usd + discounted.sum()

    cum_undiscounted = np.cumsum(monthly_revenue_expected)
    if cost_usd == 0:
        payout_months = 0.0
    elif cum_undiscounted[-1] < cost_usd:
        payout_months = None  # does not pay out within horizon
    else:
        idx = np.searchsorted(cum_undiscounted, cost_usd)
        if idx == 0:
            payout_months = cost_usd / monthly_revenue_expected[0]
        else:
            prev_cum = cum_undiscounted[idx - 1]
            frac = (cost_usd - prev_cum) / monthly_revenue_expected[idx]
            payout_months = idx + frac

    total_revenue = discounted.sum()
    roi_pct = (total_revenue - cost_usd) / cost_usd * 100 if cost_usd > 0 else 0.0

    return dict(
        incremental_rate_bopd=round(incremental_rate_0, 1),
        npv_usd=round(npv, 0),
        payout_months=round(payout_months, 2) if payout_months is not None else None,
        roi_pct=round(roi_pct, 1) if cost_usd > 0 else None,
        capital_efficiency=round(npv / cost_usd, 2) if cost_usd > 0 else None,  # NPV per $ invested
        monthly_expected_revenue=monthly_revenue_expected,
    )
