"""
Well intervention candidate catalog.

Input data (diagnosis + lost production) is carried forward directly from
Project 2 (SRP Diagnostics) results_summary.json - this project does not
re-diagnose the wells, it turns an already-made diagnosis into a funded
decision: which intervention (if any) should be executed on each well,
and in what order given a limited workover budget.

Cost, duration, expected recovery fraction, and success probability are
engineering planning-level assumptions (typical ranges for Indonesian /
SE Asia onshore workover and slickline pricing), stated explicitly as
assumptions - not vendor quotes.
"""

# carried forward from Project 2 (02_SRP_Optimization/outputs/results_summary.json)
WELLS_FROM_PROJECT2 = [
    dict(name="B-05", diagnosis="Parted rod / stuck pump (mechanical failure)", lost_bopd=178.8),
    dict(name="B-02", diagnosis="Gas interference", lost_bopd=99.0),
    dict(name="B-03", diagnosis="Fluid pound (pump-off / low fluid level)", lost_bopd=93.1),
    dict(name="B-04", diagnosis="Worn / leaking traveling valve", lost_bopd=58.1),
]

# candidate interventions per diagnosis
# cost_usd, duration_days : planning-level estimate
# recovery_fraction       : fraction of "lost production" this intervention is expected to restore
# success_prob            : probability the job achieves that recovery (mechanical/technical risk)
INTERVENTION_CATALOG = {
    "Parted rod / stuck pump (mechanical failure)": [
        dict(name="Workover — Pull & Replace Rod String", cost_usd=95000, duration_days=7,
             recovery_fraction=0.98, success_prob=0.93),
        dict(name="Do Nothing (remain shut-in)", cost_usd=0, duration_days=0,
             recovery_fraction=0.0, success_prob=1.0),
    ],
    "Gas interference": [
        dict(name="Install Gas Anchor", cost_usd=15000, duration_days=2,
             recovery_fraction=0.55, success_prob=0.85),
        dict(name="Lower Pump Setting Depth (Workover)", cost_usd=65000, duration_days=5,
             recovery_fraction=0.80, success_prob=0.90),
        dict(name="Do Nothing", cost_usd=0, duration_days=0,
             recovery_fraction=0.0, success_prob=1.0),
    ],
    "Fluid pound (pump-off / low fluid level)": [
        dict(name="Install Pump-Off Controller (POC)", cost_usd=12000, duration_days=1,
             recovery_fraction=0.60, success_prob=0.90),
        dict(name="Reduce SPM (operational adjustment only)", cost_usd=500, duration_days=0.5,
             recovery_fraction=0.35, success_prob=0.95),
        dict(name="Do Nothing", cost_usd=0, duration_days=0,
             recovery_fraction=0.0, success_prob=1.0),
    ],
    "Worn / leaking traveling valve": [
        dict(name="Slickline Traveling/Standing Valve Replacement", cost_usd=28000, duration_days=1.5,
             recovery_fraction=0.75, success_prob=0.80),
        dict(name="Full Workover (Rig, pull tubing + rods)", cost_usd=85000, duration_days=6,
             recovery_fraction=0.95, success_prob=0.92),
        dict(name="Do Nothing", cost_usd=0, duration_days=0,
             recovery_fraction=0.0, success_prob=1.0),
    ],
}

# economic assumptions
ECON_ASSUMPTIONS = dict(
    oil_price_usd_bbl=70.0,
    variable_opex_usd_bbl=15.0,     # lifting cost netted off incremental barrels
    discount_rate_annual=0.10,
    decline_rate_monthly=0.02,      # decline applied to the INCREMENTAL rate over the eval horizon
    eval_months=12,
)
