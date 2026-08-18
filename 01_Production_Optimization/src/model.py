"""
model.py
--------
IPR (composite/Vogel), VLP (multiphase homogeneous no-slip pressure traverse),
and Nodal Analysis (IPR-VLP intersection) engine for Well A-01.

VLP note: a homogeneous no-slip mixture model is used (mixture density and
viscosity from in-situ volume fractions, Moody friction). This is a
simplification of a full mechanistic/empirical correlation (e.g. Hagedorn-
Brown, Duns-Ros) which accounts for liquid holdup/slip. It captures the
correct physical trends (friction vs. gravity dominated regimes) and is
appropriate for a screening-level nodal analysis case study; a full slip
correlation would be a natural next step for higher accuracy at low rates.
"""

import numpy as np
from scipy.optimize import brentq
import pvt


# ----------------------------------------------------------------- IPR ---
def calibrate_pi(pr, pb, test_pwf, test_qo):
    """
    Calibrate the productivity index J from a single well test point using
    the standard composite (straight-line above Pb, Vogel below Pb) IPR.
    """
    if test_pwf >= pb:
        j = test_qo / (pr - test_pwf)
    else:
        pwf_r = test_pwf / pb
        term = 1.0 - 0.2 * pwf_r - 0.8 * pwf_r ** 2
        # Qtest = J*(Pr-Pb) + (J*Pb/1.8)*term  ->  solve for J
        j = test_qo / ((pr - pb) + (pb / 1.8) * term)
    return j


def ipr_rate(pwf, pr, pb, j):
    """Composite IPR: returns oil rate (STB/d) for a given Pwf."""
    if pwf >= pb:
        return j * (pr - pwf)
    qb = j * (pr - pb)
    pwf_r = pwf / pb
    term = 1.0 - 0.2 * pwf_r - 0.8 * pwf_r ** 2
    return qb + (j * pb / 1.8) * term


def ipr_curve(pr, pb, j, n=60):
    pwf_vals = np.linspace(0.0, pr, n)
    q_vals = np.array([ipr_rate(p, pr, pb, j) for p in pwf_vals])
    return pwf_vals, q_vals


# ----------------------------------------------------------------- VLP ---
def pressure_traverse(qo_stb_d, well, n_steps=110, thp_override=None):
    """
    March pressure DOWN the tubing from the wellhead to bottomhole for a
    given surface oil rate, returning flowing bottomhole pressure (Pwf, psia).

    qo_stb_d : surface oil rate (STB/d)
    well     : well data dict (see data/well_A01.py)
    """
    api = well["oil_api"]
    gg = well["gas_sg"]
    sgw = well["water_sg"]
    wc = well["water_cut"]
    gor = well["producing_gor_scf_stb"]
    pb = well["bubble_point_psi"]
    rsb = gor  # solution GOR at/above bubble point

    depth = well["depth_ft"]
    d_in = well["tubing_id_in"]
    d_ft = d_in / 12.0
    area = np.pi / 4.0 * d_ft ** 2
    eps_over_d = well["roughness_ft"] / d_ft

    t_surf = well["surface_temp_f"]
    t_res = well["reservoir_temp_f"]

    thp = well["wellhead_pressure_psi"] if thp_override is None else thp_override

    qw_stb_d = qo_stb_d * wc / (1 - wc) if wc < 1.0 else 0.0
    ql_stb_d = qo_stb_d + qw_stb_d

    dz = depth / n_steps
    p = thp

    for i in range(n_steps):
        z_mid = (i + 0.5) * dz
        t_mid = t_surf + (t_res - t_surf) * (z_mid / depth)

        # -- iterate P at this depth increment (predictor -> corrector) --
        p_est = p
        for _ in range(3):
            p_avg = 0.5 * (p + p_est)
            rs = pvt.rs_standing(p_avg, t_mid, api, gg, pb, rsb)
            bo = pvt.bo_standing(p_avg, t_mid, api, gg, pb, rsb, rs)
            z = pvt.gas_z_factor(p_avg, t_mid, gg)
            bg = pvt.gas_fvf(p_avg, t_mid, z)

            rho_o = pvt.oil_density(p_avg, t_mid, api, gg, bo, rs)
            rho_w = pvt.water_density(sgw)
            rho_g = pvt.gas_density(p_avg, t_mid, gg, z)

            mu_o = pvt.oil_viscosity(p_avg, t_mid, api, rs, pb)
            mu_w = pvt.water_viscosity(t_mid)
            mu_g = pvt.gas_viscosity(p_avg, t_mid, gg, z)

            # in-situ volumetric rates, ft3/s
            q_o = qo_stb_d * bo * 5.615 / 86400.0
            q_w = qw_stb_d * 1.01 * 5.615 / 86400.0
            gas_free_scf_d = max(gor - rs, 0.0) * qo_stb_d
            q_g = gas_free_scf_d * bg * 5.615 / 86400.0

            q_liq = q_o + q_w
            q_tot = q_liq + q_g
            lam_l = q_liq / q_tot if q_tot > 0 else 1.0

            rho_l = (rho_o * q_o + rho_w * q_w) / q_liq if q_liq > 0 else rho_o
            rho_m = rho_l * lam_l + rho_g * (1 - lam_l)

            mu_l = (mu_o * q_o + mu_w * q_w) / q_liq if q_liq > 0 else mu_o
            mu_m = mu_l * lam_l + mu_g * (1 - lam_l)

            v_m = q_tot / area  # ft/s

            re = 1488.0 * rho_m * v_m * d_ft / max(mu_m, 1e-4)
            f = moody_friction(re, eps_over_d)

            dpdz_elev = rho_m / 144.0
            dpdz_fric = f * rho_m * v_m ** 2 / (2.0 * 32.174 * d_ft * 144.0)
            dpdz = dpdz_elev + dpdz_fric

            p_est = p + dpdz * dz

        p = p_est

    return p  # Pwf, psia


def moody_friction(re, eps_over_d):
    """Chen (1979) explicit approximation to the Colebrook-White equation."""
    if re < 2300:
        return 64.0 / max(re, 1.0)
    a = (eps_over_d / 3.7065) - (5.0452 / re) * np.log10(
        (eps_over_d ** 1.1098) / 2.8257 + (7.149 / re) ** 0.8981
    )
    f = (1.0 / (-2.0 * np.log10(a))) ** 2
    return f


def vlp_curve(well, q_min=20, q_max=900, n=22, thp_override=None):
    q_vals = np.linspace(q_min, q_max, n)
    pwf_vals = np.array([pressure_traverse(q, well, thp_override=thp_override) for q in q_vals])
    return q_vals, pwf_vals


# ------------------------------------------------------------- NODAL -----
def find_operating_point(well, j, pr, pb, thp_override=None):
    """Solve for the rate where IPR(Pwf) == VLP(Pwf)."""

    def f(q):
        pwf_ipr_solve = q  # placeholder, unused
        return 0

    def diff(q):
        pwf_vlp = pressure_traverse(q, well, thp_override=thp_override)
        pwf_ipr = pwf_from_ipr(q, pr, pb, j)
        return pwf_vlp - pwf_ipr

    # bracket the root
    q_lo, q_hi = 20.0, 850.0
    try:
        q_op = brentq(diff, q_lo, q_hi, xtol=1.0, maxiter=60)
    except ValueError:
        return None, None
    pwf_op = pressure_traverse(q_op, well, thp_override=thp_override)
    return q_op, pwf_op


def pwf_from_ipr(q, pr, pb, j):
    """Invert the composite IPR (rate -> Pwf) via bisection."""
    lo, hi = 0.0, pr
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        q_mid = ipr_rate(mid, pr, pb, j)
        if q_mid > q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
