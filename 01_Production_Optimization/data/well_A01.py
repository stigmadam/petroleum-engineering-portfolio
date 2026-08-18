"""
Synthetic well and reservoir dataset for Well A-01.

This well is a hypothetical mature, undersaturated-to-saturated oil well,
built with realistic field parameters to demonstrate a full IPR-VLP-Nodal
Analysis workflow. It is NOT real field data - it is used to showcase the
engineering methodology.
"""

WELL = dict(
    name="A-01",
    depth_ft=5500.0,          # mid-perforation TVD
    tubing_id_in=2.441,       # 2-7/8" EUE 6.5 lb/ft tubing (base case)
    roughness_ft=0.0006,      # commercial steel tubing roughness

    reservoir_pressure_psi=1800.0,
    bubble_point_psi=1500.0,
    reservoir_temp_f=180.0,
    surface_temp_f=100.0,     # wellhead / flowline temperature

    oil_api=32.0,
    gas_sg=0.75,
    water_sg=1.05,
    water_cut=0.35,           # fraction
    producing_gor_scf_stb=450.0,   # solution GOR at/above bubble point

    # well test point used to calibrate the IPR (Vogel/composite model)
    test_pwf_psi=1200.0,
    test_qo_stb_d=350.0,

    wellhead_pressure_psi=150.0,   # flowing THP / separator pressure
)
