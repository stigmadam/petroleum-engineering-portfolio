"""
Synthetic SRP well fleet for surveillance and diagnostics.

Well A-01 (SRP) is the same well from Project 1 (Production Optimization),
now shown after conversion to sucker-rod-pump artificial lift once natural
flow could no longer sustain economic rates (see Project 1, Section 5.4) -
this ties the two projects together as one coherent field-life story.

Each well entry includes:
  - pump design parameters (stroke, SPM, plunger diameter) -> theoretical
    pump displacement (PD, bbl/d)
  - the field-measured (synthetic) actual oil rate -> observed volumetric efficiency
  - a "true" condition used only to generate a realistic card (the
    diagnostic tool does NOT see this - it must infer it from the card)
"""

WELLS = [
    dict(name="A-01", stroke_in=64, spm=6.5, plunger_diam_in=1.75,
         pprl_design=8200, mprl_design=3100,
         actual_rate_bopd=142, true_condition="normal", seed=11),

    dict(name="B-02", stroke_in=64, spm=7.0, plunger_diam_in=1.75,
         pprl_design=7600, mprl_design=3400,
         actual_rate_bopd=61, true_condition="gas_interference", seed=22),

    dict(name="B-03", stroke_in=54, spm=6.0, plunger_diam_in=2.00,
         pprl_design=8600, mprl_design=3200,
         actual_rate_bopd=58, true_condition="fluid_pound", seed=33),

    dict(name="B-04", stroke_in=74, spm=5.0, plunger_diam_in=1.50,
         pprl_design=7100, mprl_design=3000,
         actual_rate_bopd=39, true_condition="worn_traveling_valve", seed=44),

    dict(name="B-05", stroke_in=64, spm=8.0, plunger_diam_in=1.75,
         pprl_design=8200, mprl_design=3100,
         actual_rate_bopd=4, true_condition="parted_rod", seed=55),

    dict(name="B-06", stroke_in=48, spm=10.0, plunger_diam_in=1.25,
         pprl_design=5200, mprl_design=2200,
         actual_rate_bopd=83, true_condition="normal", seed=66),
]
