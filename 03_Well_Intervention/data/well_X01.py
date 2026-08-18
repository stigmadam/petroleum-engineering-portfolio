"""
Synthetic well dataset for Well X-01 - a producer showing a sustained
production decline with an ambiguous root cause (two plausible mechanisms
score closely), which is deliberately the point of this case study: it
demonstrates when a low-cost diagnostic run is worth more than jumping
straight to an expensive fix.
"""

import numpy as np

# 24 months of monthly production history (synthetic, built to show a
# realistic decline pattern: oil rate falling, water cut climbing, GOR flat,
# wellhead pressure drifting down)
MONTHS = np.arange(24)

OIL_RATE_BOPD = np.round(420 * np.exp(-0.028 * MONTHS) + np.random.default_rng(7).normal(0, 4, 24), 1)
OIL_RATE_BOPD = np.clip(OIL_RATE_BOPD, 240, None)
OIL_RATE_BOPD[-1] = 250.0  # anchor current rate to the case narrative

WATER_CUT_PCT = np.round(35 + (60 - 35) * (MONTHS / 23) ** 1.3 +
                          np.random.default_rng(8).normal(0, 0.6, 24), 1)
WATER_CUT_PCT = np.clip(WATER_CUT_PCT, 30, 65)
WATER_CUT_PCT[-1] = 60.0

GOR_SCF_STB = np.round(430 + np.random.default_rng(9).normal(0, 8, 24), 0)  # flat / stable

WHP_PSI = np.round(650 - (650 - 500) * (MONTHS / 23) +
                    np.random.default_rng(10).normal(0, 5, 24), 0)
WHP_PSI[-1] = 500.0

WELL = dict(
    name="X-01",
    reservoir_pressure_psi=1500.0,
    current_oil_rate_bopd=250.0,
    current_water_cut_pct=60.0,
    current_whp_psi=500.0,
    decline_12mo_pct=round(100 * (1 - OIL_RATE_BOPD[-1] / OIL_RATE_BOPD[-13]), 1),

    # symptom flags used by the diagnostic scoring engine (src/diagnosis.py)
    water_cut_trend="increasing",     # 35% -> 60% over the last 12 months
    gor_trend="stable",
    whp_trend="declining",            # 650 -> 500 psi over the last 12 months
    pi_trend="declining_moderate",    # productivity index down ~25% vs. last test
    sand_production=False,
    months_since_last_intervention=18,
)
